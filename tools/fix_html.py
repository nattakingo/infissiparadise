"""Trasformazione SEO + accessibilita su tutte le pagine HTML.

Operazioni (idempotente):
  1. canonical + Open Graph + Twitter Card in <head>
  2. title / description riscritti nei limiti (title <=60, desc 120-160)
  3. dominio normalizzato su https://infissiparadise.it (niente /www.)
  4. rel="noopener" su ogni target="_blank"
  5. skip-link + id="main-content" su <main>
  6. aria-current="page" sul link attivo della nav
  7. voci "Chi Siamo" e "Contatti" aggiunte alla nav
  8. width/height di ogni <img> allineati alle dimensioni reali (+ srcset w)
  9. id="blog" sulla sezione blog della home
 10. ripulitura righe vuote duplicate in <head>

Uso: python tools/fix_html.py
"""
import os
import re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://infissiparadise.it"

# ---------------------------------------------------------------- contenuti
# (title, description, og:image)
PAGES = {
    "index.html": (
        "ShowRoom Infissi | Serramenti, Finestre e Porte a Roma",
        "ShowRoom Infissi: serramenti, finestre, porte blindate, persiane e avvolgibili "
        "di qualità Made in Italy. Installazione a Roma e provincia.",
        "img/unsplash/photo-1505691938895-1758d7feb511-1280.jpg",
    ),
    "finestre.html": (
        "Finestre e Portefinestre | ShowRoom Infissi",
        "Finestre e portefinestre in PVC, alluminio e legno. Serramenti certificati per "
        "risparmio energetico e isolamento acustico. Preventivo a Roma e provincia.",
        "img/unsplash/photo-1600585154340-be6161a56a0c-1920.jpg",
    ),
    "porte-blindate.html": (
        "Porte Blindate | ShowRoom Infissi",
        "Porte blindate di alta sicurezza con design esclusivo. Certificazione "
        "antieffrazione, installazione a Roma e provincia. Richiedi il preventivo gratuito.",
        "immaginiHome/portablindata.jpg",
    ),
    "persiane.html": (
        "Persiane | ShowRoom Infissi",
        "Persiane in legno, alluminio e PVC su misura. Protezione, estetica e isolamento "
        "termico per finestre e portefinestre. Installazione a Roma e dintorni.",
        "immaginiHome/persiana-muro.jpg",
    ),
    "avvolgibili.html": (
        "Avvolgibili | ShowRoom Infissi",
        "Avvolgibili in PVC, alluminio coibentato e acciaio su misura. Isolamento termico, "
        "oscuramento e sicurezza blindata. Made in Italy, installazione a Roma.",
        "immaginiAvvolgibili/avvolgibiliHero.jpg",
    ),
    "cassonetti.html": (
        "Cassonetti | ShowRoom Infissi",
        "Cassonetti coibentati per un perfetto isolamento termico e acustico del foro "
        "finestra. Installazione professionale a Roma e provincia.",
        "img/unsplash/photo-1600566753190-17f0baa2a6c3-1920.jpg",
    ),
    "zanzariere.html": (
        "Zanzariere | ShowRoom Infissi",
        "Zanzariere a rullo, plissettate, fisse e magnetiche per finestre e portefinestre. "
        "Protezione da insetti e pollini. Installazione a Roma.",
        "img/unsplash/photo-1598928506311-c55ded91a20c-1920.jpg",
    ),
    "grate-sicurezza.html": (
        "Grate di Sicurezza | ShowRoom Infissi",
        "Grate di sicurezza in acciaio e ferro battuto su misura, con soluzioni "
        "antieffrazione certificate. Vendita e installazione a Roma e provincia.",
        "img/unsplash/photo-1550989460-0adf9ea622e2-1920.jpg",
    ),
    "tende-da-sole.html": (
        "Tende da Sole | ShowRoom Infissi",
        "Tende da sole a caduta, a bracci e cassonetto per terrazze e giardini. Tessuti "
        "certificati, installazione a Roma. Protezione UV e comfort tutto l'anno.",
        "img/unsplash/photo-1616486338812-3dadae4b4ace-1920.jpg",
    ),
    "chi-siamo.html": (
        "Chi Siamo | ShowRoom Infissi",
        "Dal 1992 produciamo porte e finestre con un reparto tecnico dedicato a ricerca e "
        "progettazione su misura. Scopri la storia e i valori di ShowRoom Infissi.",
        "img/unsplash/photo-1581092160562-40aa08e78837-1200.jpg",
    ),
    "contatti.html": (
        "Contattaci | ShowRoom Infissi - Preventivo Express",
        "Contattaci per un preventivo express su infissi, porte blindate, persiane e "
        "serramenti. Rispondiamo entro 24 ore. Sede a Roma.",
        "logo.png",
    ),
    "privacy.html": (
        "Privacy Policy | ShowRoom Infissi",
        "Privacy Policy di ShowRoom Infissi / Infissi Paradise. Come trattiamo i tuoi dati "
        "personali ai sensi del Regolamento UE 2016/679 (GDPR).",
        "logo.png",
    ),
    "cookie-policy.html": (
        "Cookie Policy | ShowRoom Infissi",
        "Cookie Policy di ShowRoom Infissi / Infissi Paradise. Cookie utilizzati, finalità "
        "e come gestire le preferenze sui cookie.",
        "logo.png",
    ),
    "blog/bonus-sicurezza.html": (
        "Bonus Sicurezza 2025: Detrazione 50% | ShowRoom Infissi",
        "Guida al Bonus Sicurezza 2025-2026: detrazione 50% per inferriate, grate e porte "
        "blindate. Requisiti, documenti e come usufruirne.",
        "blog/bonussicurezza.jpg",
    ),
    "blog/detrazioni-fiscali-infissi.html": (
        "Detrazioni Fiscali Infissi 2026 | ShowRoom Infissi",
        "Tutto sulle detrazioni fiscali per infissi nel 2026. Bonus ristrutturazioni 50%, "
        "Ecobonus 50%, requisiti, documenti e scadenze.",
        "blog/ecobonus.jpg",
    ),
    "blog/iva-agevolata-inferriate.html": (
        "IVA Agevolata 10% Inferriate | ShowRoom Infissi",
        "Guida all'IVA agevolata al 10% per l'acquisto di inferriate di sicurezza. Quando "
        "si applica, chi può richiederla, acquisto con e senza installazione.",
        "immaginiGrate/IMG_0446.JPG",
    ),
    "blog/materiali-finestre.html": (
        "Quali Materiali per le Finestre? | ShowRoom Infissi",
        "Guida ai materiali per finestre e infissi a Roma: PVC, legno, alluminio e "
        "legno-alluminio. Scopri prezzi, vantaggi e quale scegliere per le tue esigenze.",
        "blog/guidainfissi.jpg",
    ),
}

NAV_EXTRA = ('{ind}<li><a href="{p}chi-siamo.html">Chi Siamo</a></li>\n'
             '{ind}<li><a href="{p}contatti.html">Contatti</a></li>')

issues = []


# ----------------------------------------------------------------- util
def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def image_size(rel, base):
    full = os.path.normpath(os.path.join(base, rel.split("?")[0]))
    if not os.path.isfile(full):
        return None
    if full.lower().endswith(".svg"):
        return None  # le dimensioni dichiarate in un SVG non servono al layout
    try:
        with Image.open(full) as im:
            return im.size
    except Exception:  # noqa: BLE001
        return None


def url_for(rel_path):
    return f"{SITE}/{rel_path}" if rel_path != "index.html" else f"{SITE}/"


# ------------------------------------------------------------ head: meta
def build_head(title, desc, og_rel, canon_rel, base):
    size = image_size(og_rel, base) or (1200, 630)
    og = url_for(og_rel)
    return (
        f'    <link rel="canonical" href="{url_for(canon_rel)}">\n'
        f'    <meta property="og:type" content="website">\n'
        f'    <meta property="og:site_name" content="ShowRoom Infissi">\n'
        f'    <meta property="og:locale" content="it_IT">\n'
        f'    <meta property="og:url" content="{url_for(canon_rel)}">\n'
        f'    <meta property="og:title" content="{title}">\n'
        f'    <meta property="og:description" content="{desc}">\n'
        f'    <meta property="og:image" content="{og}">\n'
        f'    <meta property="og:image:width" content="{size[0]}">\n'
        f'    <meta property="og:image:height" content="{size[1]}">\n'
        f'    <meta name="twitter:card" content="summary_large_image">\n'
        f'    <meta name="twitter:title" content="{title}">\n'
        f'    <meta name="twitter:description" content="{desc}">\n'
        f'    <meta name="twitter:image" content="{og}">\n'
    )


def fix_head(html, title, desc, og_rel, canon_rel, base, name):
    if len(title) > 60:
        issues.append(f"{name}: title ancora lungo ({len(title)})")
    if not 110 <= len(desc) <= 165:
        issues.append(f"{name}: description fuori range ({len(desc)})")

    if 'rel="canonical"' in html:
        html = re.sub(r'\s*<link rel="canonical"[^>]*>', "", html)
    if 'property="og:title"' in html:
        html = re.sub(r'\n\s*<meta property="og:[^>]*>', "", html)
        html = re.sub(r'\n\s*<meta name="twitter:[^>]*>', "", html)

    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, flags=re.S)
    html = re.sub(r'<meta name="description"\s*content="[^"]*"',
                  f'<meta name="description" content="{desc}"', html, flags=re.S)

    block = build_head(title, desc, og_rel, canon_rel, base)
    html, n = re.subn(r"(</title>)", r"\1\n" + block, html, count=1, flags=re.S)
    if n != 1:
        issues.append(f"{name}: impossibile inserire il blocco meta")
    return html


# ------------------------------------------------------------- body: nav
def fix_nav(html, prefix, rel):
    m = re.search(r'(<nav class="header-nav"[^>]*>\s*<ul class="nav-list"[^>]*>)'
                  r'(.*?)(</ul>)', html, re.S)
    if not m:
        issues.append(f"{rel}: nav non trovata")
        return html
    head, body, tail = m.groups()

    items = re.findall(r"[ \t]*<li>.*?</li>", body, re.S)
    if not items:
        issues.append(f"{rel}: voci di nav non trovate")
        return html
    ind = re.match(r"[ \t]*", items[0]).group(0)
    tail_ind = re.search(r"[ \t]*$", body).group(0) or ind

    if "chi-siamo.html" not in body:
        items.append(NAV_EXTRA.format(ind=ind, p=prefix))

    # link attivo della pagina corrente + aria-current
    self_ref = prefix + os.path.basename(rel)
    for i, li in enumerate(items):
        hm = re.search(r'href="([^"]+)"', li)
        if not hm:
            continue
        href = hm.group(1)
        is_active = href == self_ref
        if not is_active:
            continue
        if "aria-current" not in li:
            li = li.replace(f'href="{href}"',
                            f'href="{href}" aria-current="page"', 1)
        if 'class="active"' not in li:
            li = li.replace(f'href="{href}"',
                            f'href="{href}" class="active"', 1)
        items[i] = li

    new_body = "\n" + "\n".join(items) + "\n" + tail_ind
    return html[:m.start()] + head + new_body + tail + html[m.end():]


def fix_skip_link(html, name):
    if 'class="skip-link"' in html:
        return html
    if not re.search(r"<body[^>]*>", html):
        issues.append(f"{name}: <body> non trovato")
        return html
    html = re.sub(r"(<body[^>]*>)",
                  r'\1\n    <a class="skip-link" href="#main-content">Salta al contenuto '
                  r'principale</a>', html, count=1)
    if re.search(r"<main(\s[^>]*)?>", html):
        html = re.sub(r"<main(\s[^>]*)?>",
                      lambda m: '<main id="main-content" tabindex="-1"'
                                + (m.group(1) or "") + ">", html, count=1)
    else:
        issues.append(f"{name}: <main> non trovato per l'ancora skip-link")
    return html


def fix_images(html, base, name):
    def repl(m):
        tag = m.group(0)
        sm = re.search(r'\bsrc="([^"]+)"', tag)
        if not sm:
            return tag
        src = sm.group(1)
        if src.startswith(("http://", "https://", "data:", "//")):
            return tag
        dims = image_size(src, base)
        if not os.path.isfile(os.path.normpath(os.path.join(base, src.split("?")[0]))):
            issues.append(f"{name}: immagine non trovata {src}")
            return tag
        if not dims:
            return tag  # SVG o formato non leggibile: lasciamo com'è
        w, h = dims
        if re.search(r'\bwidth="\d+"', tag):
            tag = re.sub(r'\bwidth="\d+"', f'width="{w}"', tag)
        else:
            tag = tag.replace("<img ", f'<img width="{w}" ', 1)
        if re.search(r'\bheight="\d+"', tag):
            tag = re.sub(r'\bheight="\d+"', f'height="{h}"', tag)
        else:
            tag = tag.replace("<img ", f'<img height="{h}" ', 1)

        # allinea i descrittori di larghezza nello srcset
        if "srcset=" in tag:
            def fix_ss(item_m):
                item = item_m.group(0)
                fname = item.strip().split()[0]
                d = image_size(fname, base)
                return re.sub(r"\d+w$", f"{d[0]}w", item) if d else item

            def fix_ss_attr(ss_m):
                return 'srcset="' + re.sub(r"[^,]+", fix_ss, ss_m.group(1)) + '"'

            tag = re.sub(r'\bsrcset="([^"]*)"', fix_ss_attr, tag)
        return tag

    return re.sub(r"<img\b[^>]*>", repl, html)


def fix_blank_targets(html, name):
    def repl(m):
        tag = m.group(0)
        if "rel=" in tag:
            if 'rel="' in tag and "noopener" not in tag:
                tag = re.sub(r'rel="([^"]*)"',
                             lambda r: 'rel="' + r.group(1) + ' noopener"', tag, count=1)
            return tag
        return tag.replace('target="_blank"', 'target="_blank" rel="noopener"')
    return re.sub(r"<a\b[^>]*target=\"_blank\"[^>]*>", repl, html)


def tidy_head(html):
    head = re.search(r"<head>(.*?)</head>", html, re.S)
    if not head:
        return html
    inner = head.group(1)
    fixed = re.sub(r"\n{3,}", "\n\n", inner)
    return html[:head.start(1)] + fixed + html[head.end(1):]


# ------------------------------------------------------------------ main
def main():
    for rel, (title, desc, og) in PAGES.items():
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            issues.append(f"{rel}: FILE MANCANTE")
            continue
        base = os.path.dirname(path)
        prefix = "" if base == ROOT else "../"
        html = read(path)

        html = html.replace("https://www.infissiparadise.it", SITE)
        html = fix_head(html, title, desc, og, rel, base, rel)
        html = fix_nav(html, prefix, rel)
        html = fix_skip_link(html, rel)
        html = fix_images(html, base, rel)
        html = fix_blank_targets(html, rel)

        if rel == "index.html" and 'id="blog"' not in html:
            html = html.replace('<section class="blog-section scroll-reveal">',
                                '<section class="blog-section scroll-reveal" id="blog">')

        html = tidy_head(html)
        write(path, html)
        print(f"  ok {rel}")

    print()
    if issues:
        print("SEGNALAZIONI:")
        for i in sorted(set(issues)):
            print("  -", i)
    else:
        print("Nessuna segnalazione.")


if __name__ == "__main__":
    main()
