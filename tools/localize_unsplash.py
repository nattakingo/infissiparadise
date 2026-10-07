"""Scarica tutte le immagini Unsplash usate dal sito e le rende locali.

- Salva in img/unsplash/<id>-<w>.jpg
- Riscrive gli URL in styles.css e negli HTML (inclusi preload/srcset/poster)
- Rimuove il preconnect a images.unsplash.com

Uso: python tools/localize_unsplash.py
"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "img", "unsplash")
TEXT_FILES = []
for name in os.listdir(ROOT):
    if name.endswith((".html", ".css")):
        TEXT_FILES.append(os.path.join(ROOT, name))
blog = os.path.join(ROOT, "blog")
if os.path.isdir(blog):
    TEXT_FILES += [os.path.join(blog, n) for n in os.listdir(blog) if n.endswith(".html")]

PATTERN = re.compile(r"https://(?:images|plus)\.unsplash\.com/[^'\"\s\)]+")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def local_name(url):
    base = url.split("?")[0]
    photo = base.rsplit("/", 1)[-1]
    m = re.search(r"[?&]w=(\d+)", url)
    w = m.group(1) if m else "orig"
    return f"{photo}-{w}.jpg"


def fetch(url):
    # forza JPEG per avere un'estensione deterministica
    dl = url + ("&" if "?" in url else "?") + "fm=jpg"
    req = urllib.request.Request(dl, headers={"User-Agent": UA, "Accept": "image/jpeg"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    urls = set()
    for path in TEXT_FILES:
        with open(path, encoding="utf-8") as f:
            urls.update(PATTERN.findall(f.read()))

    print(f"Trovati {len(urls)} URL Unsplash distinti")
    mapping = {}
    failed = []
    for url in sorted(urls):
        name = local_name(url)
        dest = os.path.join(OUT_DIR, name)
        rel = f"img/unsplash/{name}"
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            mapping[url] = rel
            print(f"  = gia presente {name}")
            continue
        try:
            data = fetch(url)
            with open(dest, "wb") as f:
                f.write(data)
            mapping[url] = rel
            print(f"  + {name}  {len(data)/1024:.0f} KB")
        except Exception as e:  # noqa: BLE001
            failed.append((url, str(e)))
            print(f"  !! ERRORE {name}: {e}")

    if failed:
        print("\nURL NON SCARICABILI (da sistemare a mano):")
        for url, err in failed:
            print(f"  {err}  {url}")

    # riscrittura riferimenti (parte piu lunga per prima: evita sostituzioni parziali)
    for path in TEXT_FILES:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        orig = src
        depth = os.path.relpath(os.path.dirname(path), ROOT)
        prefix = "" if depth == "." else "../"
        for url in sorted(mapping, key=len, reverse=True):
            src = src.replace(url, prefix + mapping[url])
        src = src.replace(
            '    <link rel="preconnect" href="https://images.unsplash.com">\n', "")
        src = src.replace(
            '<link rel="preconnect" href="https://images.unsplash.com">', "")
        if src != orig:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(src)
            print(f"  riscritto {os.path.relpath(path, ROOT)}")

    left = 0
    for path in TEXT_FILES:
        with open(path, encoding="utf-8") as f:
            left += len(PATTERN.findall(f.read()))
    print(f"\nURL Unsplash rimasti: {left}")


if __name__ == "__main__":
    main()
