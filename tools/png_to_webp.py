"""Converte le foto PNG (RGB, senza trasparenza) in WebP e aggiorna gli HTML.

I PNG fotografici pesano 5-10x il WebP equivalente: sui gamma_*.png di
finestre.html il risparmio e di circa 3 MB.
"""
import os
import re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = [
    "immaginifinestre/gamma_design70.png",
    "immaginifinestre/gamma_artevo.png",
    "immaginifinestre/gamma_synego.png",
    "immaginifinestre/gamma_synegoslide.png",
]


def main():
    pages = [os.path.join(ROOT, n) for n in os.listdir(ROOT) if n.endswith(".html")]
    for rel in TARGETS:
        src = os.path.join(ROOT, rel)
        if not os.path.isfile(src):
            print(f"  salvo {rel} (assente)")
            continue
        dst = os.path.splitext(src)[0] + ".webp"
        with Image.open(src) as im:
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.save(dst, "WEBP", quality=85, method=6)
        old, new = os.path.getsize(src), os.path.getsize(dst)
        print(f"  {os.path.basename(src)}  {old//1024} KB -> {new//1024} KB")

        name = os.path.basename(src)
        new_name = os.path.basename(dst)
        for p in pages:
            with open(p, encoding="utf-8") as f:
                t = f.read()
            if name not in t:
                continue
            t2 = t.replace(name, new_name)
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(t2)
            print(f"     aggiornato {os.path.relpath(p, ROOT)}")

        os.remove(src)
        print(f"     rimosso {rel}")


if __name__ == "__main__":
    main()
