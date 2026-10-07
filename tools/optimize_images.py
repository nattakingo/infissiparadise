"""Ottimizza tutte le immagini del sito in place.

- Ridimensiona a MAX_DIM px di lato maggiore (mai ingrandisce)
- Applica l'orientamento EXIF e ne rimette i metadati (privacy + correzione rotazione)
- Ricompresse: JPEG q=82 progressivo, PNG ottimizzato, WebP q=82
- Non scrive MAI un file piu grande dell'originale

Uso:  python tools/optimize_images.py [--dry-run]
"""
import os
import sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_DIM = 1600
DRY = "--dry-run" in sys.argv

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
# Cartelle escluse
SKIP_DIRS = {".git", "tools"}
# I loghi vengono mostrati piccoli (box 80-120px): bastano 512px
FOLDER_MAX = {"loghi": 512}

Image.MAX_IMAGE_PIXELS = 200_000_000


def max_dim_for(path):
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    head = rel.split("/")[0]
    return FOLDER_MAX.get(head, MAX_DIM)


def save_image(im, path, ext):
    """Salva nel formato di origine. Restituisce i byte scritti o None se non conviene."""
    tmp = path + ".tmp"
    try:
        if ext in (".jpg", ".jpeg"):
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            im.save(tmp, "JPEG", quality=82, optimize=True, progressive=True)
        elif ext == ".png":
            if im.mode == "P":
                im = im.convert("RGBA" if "transparency" in im.info else "RGB")
            im.save(tmp, "PNG", optimize=True, compress_level=9)
        elif ext == ".webp":
            if im.mode not in ("RGB", "RGBA", "L"):
                im = im.convert("RGB")
            im.save(tmp, "WEBP", quality=82, method=6)
        else:
            return None
    except Exception as e:  # noqa: BLE001
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"  !! errore salvataggio {path}: {e}")
        return None

    new = os.path.getsize(tmp)
    old = os.path.getsize(path)
    if new >= old:
        os.remove(tmp)
        return None
    if not DRY:
        os.replace(tmp, path)
    else:
        os.remove(tmp)
    return new


def process(path):
    rel = os.path.relpath(path, ROOT)
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMG_EXT:
        return 0, 0

    old = os.path.getsize(path)
    limit = max_dim_for(path)
    try:
        with Image.open(path) as src:
            im = ImageOps.exif_transpose(src)
            w, h = im.size
            resized = False
            if max(w, h) > limit:
                scale = limit / max(w, h)
                im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
                resized = True
            new = save_image(im, path, ext)
    except Exception as e:  # noqa: BLE001
        print(f"  !! errore apertura {rel}: {e}")
        return 0, 0

    if new:
        tag = "  [ridim]" if resized else ""
        print(f"{old/1024:9.0f} KB -> {new/1024:7.0f} KB  {rel}{tag}")
        return old, new
    return 0, 0


def main():
    total_old = total_new = 0
    n = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if ".git" in dirpath:
            continue
        for fn in sorted(filenames):
            if os.path.splitext(fn)[1].lower() not in IMG_EXT:
                continue
            o, nw = process(os.path.join(dirpath, fn))
            if o:
                n += 1
                total_old += o
                total_new += nw

    print("\n" + "=" * 60)
    print(f"File ottimizzati: {n}")
    print(f"Prima : {total_old/1048576:8.1f} MB")
    print(f"Dopo  : {total_new/1048576:8.1f} MB")
    print(f"Risparmio: {(total_old-total_new)/1048576:8.1f} MB "
          f"({100*(total_old-total_new)/max(total_old,1):.1f}%)")


if __name__ == "__main__":
    main()
