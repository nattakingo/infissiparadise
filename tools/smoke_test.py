"""Smoke test: avvia un server statico locale e verifica che ogni pagina,
ogni asset referenziato e ogni ancora rispondano correttamente.

Uso: python tools/smoke_test.py   (exit code != 0 se ci sono problemi)
"""
import os
import re
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8099
SITE = "http://127.0.0.1:%d/" % PORT
ABS = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:)")

_cache = {}
_problems = []


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def fetch(path):
    """Ritorna (status, body). body = None per i binari."""
    if path in _cache:
        return _cache[path]
    url = SITE + quote(path, safe="/")
    try:
        with urlopen(url) as r:
            body = r.read()
            status = r.status
            ctype = r.headers.get("Content-Type", "")
    except HTTPError as e:
        body, status, ctype = None, e.code, ""
    except Exception as e:
        body, status, ctype = None, str(e), ""
    TEXTY = ("text", "html", "css", "javascript", "xml", "json")
    if any(k in ctype for k in TEXTY):
        try:
            body = body.decode("utf-8")
        except Exception:
            pass
    _cache[path] = (status, body)
    return status, body


def pages():
    out = [n for n in sorted(os.listdir(ROOT)) if n.endswith(".html")]
    blog = os.path.join(ROOT, "blog")
    return out + ["blog/" + n for n in sorted(os.listdir(blog)) if n.endswith(".html")]


def norm(base, ref):
    ref = unquote(urlparse(ref).path)
    if ref.startswith("/"):
        return ref.lstrip("/")
    return os.path.normpath(os.path.join(base, ref)).replace("\\", "/")


def check_page(rel, html, visited=None):
    visited = visited if visited is not None else set()
    base = os.path.dirname(rel)
    refs = re.findall(r'(?:href|src)="([^"]+)"', html)
    for m in re.finditer(r'srcset="([^"]+)"', html):
        refs += [e.strip().split()[0] for e in m.group(1).split(",") if e.strip()]

    for ref in refs:
        if ABS.match(ref):
            continue
        path, _, frag = ref.partition("#")
        if path:
            target = norm(base, path)
            if target not in visited:
                visited.add(target)
                status, body = fetch(target)
                if status != 200:
                    _problems.append("%s -> HTTP %s (da %s)" % (target, status, rel))
                elif frag and isinstance(body, str):
                    if not re.search(r'id="%s"' % re.escape(unquote(frag)), body):
                        _problems.append("%s#%s -> ancora inesistente (da %s)"
                                         % (target, frag, rel))
                    else:
                        check_page(target, body, visited)
        elif frag:
            if not re.search(r'id="%s"' % re.escape(unquote(frag)), html):
                _problems.append("%s -> ancora interna inesistente #%s" % (rel, frag))


def check_css():
    for css in ("styles.css", "fonts/inter.css", "fonts/phosphor.css"):
        status, text = fetch(css)
        if status != 200:
            _problems.append("%s -> HTTP %s" % (css, status))
            continue
        cdir = os.path.dirname(css)
        for url in re.findall(r"url\(['\"]?([^'\")]+)", text):
            if url.startswith(("data:", "#", "http")):
                continue
            target = os.path.normpath(os.path.join(cdir, url.split("?")[0])).replace("\\", "/")
            if fetch(target)[0] != 200:
                _problems.append("%s -> HTTP %s (da %s)" % (target, fetch(target)[0], css))


def main():
    handler = partial(Quiet, directory=ROOT)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    visited = set()
    for rel in pages():
        status, html = fetch(rel)
        if status != 200:
            _problems.append("%s -> HTTP %s" % (rel, status))
            continue
        visited.add(rel)
        check_page(rel, html, visited)

    check_css()
    for extra in ("robots.txt", "sitemap.xml", "favicon.ico", "favicon.svg",
                  "logo.png", "main.js", "404.html"):
        if fetch(extra)[0] != 200:
            _problems.append("%s -> HTTP %s" % (extra, fetch(extra)[0]))

    # una inesistente deve davvero dare 404
    if fetch("pagina-inesistente.html")[0] != 404:
        _problems.append("il server non restituisce 404 per un path inesistente")

    srv.shutdown()
    print("pagine verificate : %d" % len(pages()))
    print("risorse verificate: %d" % len(_cache))
    for p in _problems:
        print("  ERRORE %s" % p)
    print("\n%d problemi" % len(_problems))
    return 1 if _problems else 0


if __name__ == "__main__":
    sys.exit(main())
