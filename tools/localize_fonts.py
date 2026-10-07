"""Scarica Inter (Google Fonts) e Phosphor Icons e li installa in locale.

Risultato:
  fonts/inter.css + 4 woff2 (latin / latin-ext, regular + italic)
  fonts/phosphor.css + Phosphor.woff2

Poi riscrive le <head> di tutte le pagine: rimuove i riferimenti a
fonts.googleapis.com / fonts.gstatic.com / unpkg.com e inserisce i link locali.

Uso: python tools/localize_fonts.py
"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

INTER_URL = ("https://fonts.googleapis.com/css2?"
             "family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900"
             "&display=swap")
PHOSPHOR_CSS = "https://unpkg.com/@phosphor-icons/web@2.1.2/src/regular/style.css"
PHOSPHOR_WOFF2 = "https://unpkg.com/@phosphor-icons/web@2.1.2/src/regular/Phosphor.woff2"

KEEP_SUBSETS = {"latin", "latin-ext"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  = gia presente {os.path.basename(dest)}")
        return
    data = get(url, binary=True)
    with open(dest, "wb") as f:
        f.write(data)
    print(f"  + {os.path.basename(dest)}  {len(data)/1024:.0f} KB")


def build_inter():
    css = get(INTER_URL)
    blocks = re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    out = ["/* Inter - self hosted (sottoinsiemi latin/latin-ext) */\n"]
    n = 0
    for subset, block in blocks:
        if subset not in KEEP_SUBSETS:
            continue
        m = re.search(r"url\((\S+?)\)", block)
        src = m.group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        name = f"inter-{style}-{subset}.woff2"
        download(src, os.path.join(FONTS, name))
        out.append(block.replace(src, name).strip() + "\n")
        n += 1
    with open(os.path.join(FONTS, "inter.css"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"  + inter.css ({n} @font-face)")


def build_phosphor():
    css = get(PHOSPHOR_CSS)
    download(PHOSPHOR_WOFF2, os.path.join(FONTS, "Phosphor.woff2"))

    # teniamo solo il woff2: tutti i browser moderni lo supportano
    css = re.sub(r",\s*url\([^)]*\.ttf\)\s*format\('truetype'\)", "", css)
    css = css.replace("./Phosphor.woff2", "Phosphor.woff2")
    header = "/* Phosphor Icons v2.1.2 (regular) - self hosted */\n"
    with open(os.path.join(FONTS, "phosphor.css"), "w", encoding="utf-8") as f:
        f.write(header + css)
    print(f"  + phosphor.css  ({len(css)/1024:.0f} KB)")


def rewrite_heads():
    """Sostituisce i link a CDN con i CSS locali, in tutte le pagine."""
    pages = [os.path.join(ROOT, n) for n in os.listdir(ROOT) if n.endswith(".html")]
    blog = os.path.join(ROOT, "blog")
    pages += [os.path.join(blog, n) for n in os.listdir(blog) if n.endswith(".html")]

    DROP = re.compile(r"fonts\.googleapis\.com|fonts\.gstatic\.com|unpkg\.com/@phosphor-icons")
    DROP_COMMENT = re.compile(r"<!--\s*(Google Fonts|Phosphor Icons)")

    for path in sorted(pages):
        rel_dir = os.path.relpath(os.path.dirname(path), ROOT)
        p = "" if rel_dir == "." else "../"
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        out = []
        inserted = False
        for line in lines:
            if DROP.search(line) or DROP_COMMENT.search(line):
                continue
            if not inserted and re.search(r'<link rel="stylesheet" href="[^"]*styles\.css">',
                                          line):
                indent = line[:len(line) - len(line.lstrip())]
                out.append(f'{indent}<link rel="stylesheet" href="{p}fonts/inter.css">\n')
                out.append(f'{indent}<link rel="stylesheet" href="{p}fonts/phosphor.css">\n')
                inserted = True
            out.append(line)

        if not inserted:
            print(f"  !! {os.path.basename(path)}: anchor styles.css non trovato")
            continue

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.writelines(out)
        print(f"  riscritto {os.path.relpath(path, ROOT)}")


def main():
    os.makedirs(FONTS, exist_ok=True)
    print("Inter:")
    build_inter()
    print("Phosphor:")
    build_phosphor()
    print("Pagine:")
    rewrite_heads()


if __name__ == "__main__":
    main()
