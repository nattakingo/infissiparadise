"""Verifica completa del sito statico.

Controlla:
  1. link e asset locali risolvono su disco (href/src/srcset/url())
  2. ancore interne (#id) esistono nella stessa pagina
  3. meta SEO (canonical, OG, Twitter, description, viewport, charset) e lunghezze
  4. attributi immagine (alt, width, height, loading/decoding)
  5. layout sincronizzato (announcement-bar, header, footer, link attivo, prefissi)
  6. presenza di skip-link, main#main-content, favicon.svg + favicon.ico
  7. robots.txt / sitemap.xml coerenti
  8. nessun riferimento a www., http:// interno o Unsplash

Uso: python tools/verify_site.py   (exit code != 0 se ci sono errori)
"""
import os
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://infissiparadise.it"
SKIP_NAV = {"404.html", "privacy.html", "cookie-policy.html"}
ABSOLUTE = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:|#|/)")
TITLE_OK = (25, 60)
DESC_OK = (110, 160)

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def html_pages():
    out = [n for n in sorted(os.listdir(ROOT)) if n.endswith(".html")]
    blog = os.path.join(ROOT, "blog")
    return [(n, os.path.join(ROOT, n)) for n in out] + \
           [("blog/" + n, os.path.join(blog, n))
            for n in sorted(os.listdir(blog)) if n.endswith(".html")]


def resolve(base_dir, ref):
    ref = unquote(urlparse(ref).path)
    if not ref:
        return None
    p = os.path.normpath(os.path.join(base_dir, ref))
    return p


def check_targets(rel, html, base_dir):
    refs = re.findall(r'(?:href|src)="([^"]+)"', html)
    for m in re.finditer(r'srcset="([^"]+)"', html):
        refs += [e.strip().split()[0] for e in m.group(1).split(",") if e.strip()]
    for ref in refs:
        if ref.startswith(("mailto:", "tel:", "http")):
            host = (urlparse(ref).hostname or "").lower()
            if host.endswith("infissiparadise.it") and host.startswith("www."):
                err("%s: dominio www. nel link -> %s" % (rel, ref))
            for cdn in ("fonts.googleapis", "fonts.gstatic", "unpkg.com",
                        "jsdelivr", "cdnjs", "images.unsplash",
                        "google-analytics", "googletagmanager", "cdn."):
                if cdn in host:
                    err("%s: risorsa da CDN/tracker di terzi -> %s" % (rel, ref))
            continue
        if ref.startswith(("#", "data:", "javascript:")):
            continue
        if ref.startswith("/"):          # root-relative (404.html)
            p = os.path.normpath(os.path.join(ROOT, ref.lstrip("/")))
        else:
            p = resolve(base_dir, ref)
        if p and not os.path.exists(p):
            err("%s: asset/link mancante -> %s" % (rel, ref))

    # ancore interne
    for anchor in re.findall(r'href="#([^"]+)"', html):
        if anchor and not re.search(r'id="%s"' % re.escape(anchor), html):
            err("%s: ancora senza target -> #%s" % (rel, anchor))


def check_css():
    for css in ("styles.css", "fonts/inter.css", "fonts/phosphor.css"):
        path = os.path.join(ROOT, css)
        if not os.path.isfile(path):
            err("css mancante: %s" % css)
            continue
        css_dir = os.path.dirname(path)
        text = read(path)
        for url in re.findall(r"url\(['\"]?([^'\")]+)", text):
            if url.startswith("data:") or url.startswith("#"):
                continue
            if url.startswith("http"):
                if "unsplash" in url:
                    err("%s: URL Unsplash residuo -> %s" % (css, url))
                continue
            target = os.path.normpath(os.path.join(css_dir, url.split("?")[0]))
            if not os.path.exists(target):
                err("%s: url() mancante -> %s" % (css, url))


def check_meta(rel, html, base_dir):
    def one(pattern, label, required=True):
        m = re.search(pattern, html, re.S)
        if not m:
            if required:
                err("%s: manca %s" % (rel, label))
            return ""
        return (m.group(1) if m.lastindex else m.group(0)).strip()

    title = one(r"<title>(.*?)</title>", "<title>")
    desc = one(r'<meta name="description" content="(.*?)">', "meta description")
    one(r'<meta name="viewport" content="[^"]*">', "meta viewport")
    one(r'<meta charset="[^"]*">', "meta charset", required=False)

    if title and not TITLE_OK[0] <= len(title) <= TITLE_OK[1]:
        warn("%s: title %d char (consigliato %d-%d)" % (rel, len(title), *TITLE_OK))
    if desc and not DESC_OK[0] <= len(desc) <= DESC_OK[1]:
        warn("%s: description %d char (consigliato %d-%d)" % (rel, len(desc), *DESC_OK))

    if rel != "404.html":
        can = one(r'<link rel="canonical" href="([^"]+)">', "canonical")
        if can != SITE + "/" + ("" if rel == "index.html" else rel):
            err("%s: canonical errato -> %s" % (rel, can))
        for tag, label in ((r'<meta property="og:title" content="[^"]*">', "og:title"),
                           (r'<meta property="og:description" content="[^"]*">', "og:description"),
                           (r'<meta property="og:image" content="[^"]*">', "og:image"),
                           (r'<meta property="og:url" content="[^"]*">', "og:url"),
                           (r'<meta name="twitter:card" content="[^"]*">', "twitter:card")):
            if not re.search(tag, html):
                err("%s: manca %s" % (rel, label))
        if not re.search(r'rel="(shortcut icon|icon)"', html) or "favicon.ico" not in html:
            err("%s: manca il fallback favicon.ico" % rel)
        if not re.search(r'class="skip-link"', html):
            err("%s: manca lo skip-link" % rel)
        if not re.search(r'<main[^>]*id="main-content"', html):
            err("%s: manca <main id=main-content>" % rel)


def check_images(rel, html):
    for m in re.finditer(r"<img\b[^>]*>", html):
        tag = m.group(0)
        if 'alt=' not in tag:
            err("%s: <img> senza alt -> %s" % (rel, tag[:90]))
        if 'width=' not in tag or 'height=' not in tag:
            err("%s: <img> senza width/height -> %s" % (rel, tag[:90]))
        if 'loading=' not in tag and 'fetchpriority=' not in tag:
            warn("%s: <img> senza loading -> %s" % (rel, tag[:90]))


def check_layout(rel, html, base_dir):
    if not all(re.search(p, html, re.S)
               for p in (r"<header\b.*?</header>", r"<footer\b.*?</footer>",
                         r'<div class="announcement-bar">.*?</div>\s*</div>')):
        err("%s: blocchi header/footer/announcement incompleti" % rel)
        return
    pre = "" if "/" not in rel else "../"
    if pre and not re.search(r'href="\.\./index\.html"', html):
        err("%s: prefisso ../ mancante nel layout" % rel)

    hdr = re.search(r"<header\b.*?</header>", html, re.S).group(0)
    act = re.findall(r'<a href="([^"]+)"\s+aria-current="page"\s+class="active"', hdr)
    expect = [] if (rel.startswith("blog/") or rel in SKIP_NAV) else [pre + rel]
    if act != expect:
        err("%s: link attivo=%s atteso=%s" % (rel, act, expect))


def check_robots_sitemap():
    robots = os.path.join(ROOT, "robots.txt")
    if not os.path.isfile(robots):
        err("manca robots.txt")
    else:
        t = read(robots)
        if "Sitemap: %s/sitemap.xml" % SITE not in t:
            err("robots.txt: manca la riga Sitemap con il dominio apex")
        if "www." in t:
            err("robots.txt: riferimento www. residuo")

    sm = os.path.join(ROOT, "sitemap.xml")
    if not os.path.isfile(sm):
        err("manca sitemap.xml")
        return
    t = read(sm)
    urls = re.findall(r"<loc>(.*?)</loc>", t)
    expected = sorted(
        SITE + "/" + ("" if n == "index.html" else n) for n in os.listdir(ROOT)
        if n.endswith(".html") and n not in ("404.html",))
    expected += sorted(SITE + "/blog/" + n for n in os.listdir(os.path.join(ROOT, "blog"))
                       if n.endswith(".html"))
    if sorted(urls) != sorted(expected):
        missing = set(expected) - set(urls)
        extra = set(urls) - set(expected)
        if missing:
            err("sitemap.xml: URL mancanti -> %s" % sorted(missing))
        if extra:
            err("sitemap.xml: URL extra -> %s" % sorted(extra))
    if "404" in t:
        err("sitemap.xml: contiene 404.html")

    if not os.path.isfile(os.path.join(ROOT, "favicon.svg")):
        err("manca favicon.svg")
    if not os.path.isfile(os.path.join(ROOT, "favicon.ico")):
        err("manca favicon.ico")


def main():
    for rel, path in html_pages():
        html = read(path)
        base = os.path.dirname(path)
        check_targets(rel, html, base)
        check_meta(rel, html, base)
        check_images(rel, html)
        check_layout(rel, html, base)
        if re.search(r'(?:content|href)="(?:https?:)?//?[^"]*www\.infissiparadise', html):
            err("%s: riferimento www. residuo" % rel)

    check_css()
    check_robots_sitemap()

    for w in warnings:
        print("  warn  %s" % w)
    for e in errors:
        print("  ERRORE %s" % e)
    print("\n%d errori, %d avvisi" % (len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
