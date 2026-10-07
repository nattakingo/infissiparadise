import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEXT_EXT = {'.html', '.css', '.js'}
IMG_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.ico', '.heic', '.avif'}

blob = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if '.git' in dirpath:
        continue
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext in TEXT_EXT:
            with open(os.path.join(dirpath, fn), encoding='utf-8', errors='ignore') as f:
                blob.append(f.read())

blob = "\n".join(blob)

used, unused = [], []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if '.git' in dirpath:
        continue
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in IMG_EXT:
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        if fn in blob:
            used.append((rel, os.path.getsize(full)))
        else:
            unused.append((rel, os.path.getsize(full)))

used.sort(key=lambda x: -x[1])
unused.sort(key=lambda x: -x[1])

print(f"USATE: {len(used)} file, {sum(s for _, s in used)/1048576:.1f} MB")
print(f"NON USATE: {len(unused)} file, {sum(s for _, s in unused)/1048576:.1f} MB")
print("\n--- NON USATE ---")
for rel, s in unused:
    print(f"{s/1024:9.0f} KB  {rel}")
