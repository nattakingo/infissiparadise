"""Sincronizza announcement-bar, header e footer su tutte le pagine.

Fonte di verita: index.html. Ogni altra pagina riceve gli stessi blocchi con:
  - il prefisso di percorso corretto ("../" per blog/)
  - il link di nav attivo sulla pagina corrente (class="active" + aria-current)

404.html e escluso: usa percorsi assoluti per essere servito a qualsiasi profondita.

Uso: python tools/sync_layout.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "index.html")
EXCLUDE = {"404.html"}

ABSOLUTE = re.compile(r"^(https?:|/|#|mailto:|tel:|data:|javascript:)")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def extract(html, pattern, label, name):
    m = re.search(pattern, html, re.S)
    if not m:
        raise SystemExit(f"{name}: blocco {label} non trovato")
    return m.group(0)


def add_prefix(block, prefix):
    if not prefix:
        return block

    def repl(m):
        attr, val = m.group(1), m.group(2)
        if ABSOLUTE.match(val):
            return m.group(0)
        return f'{attr}="{prefix}{val}"'

    block = re.sub(r'\b(href|src)="([^"]+)"', repl, block)

    def repl_srcset(m):
        out = []
        for entry in [e.strip() for e in m.group(1).split(",") if e.strip()]:
            parts = entry.split()
            if parts and not ABSOLUTE.match(parts[0]):
                parts[0] = prefix + parts[0]
            out.append(" ".join(parts))
        return 'srcset="%s"' % ", ".join(out)

    return re.sub(r'\bsrcset="([^"]+)"', repl_srcset, block)


def set_active(header, self_ref):
    # azzera lo stato attivo su tutte le voci
    header = re.sub(r'\s+aria-current="page"', "", header)
    header = re.sub(r'(\s+class="active")+', "", header)
    if not self_ref:
        return header

    pat = re.compile(r'<a href="' + re.escape(self_ref) + r'"')
    if not pat.search(header):
        return header  # la pagina non e' nella nav (es. pagine blog)
    return pat.sub('<a href="%s" aria-current="page" class="active"' % self_ref,
                   header, count=1)


def main():
    src = read(SOURCE)
    # l'announcement-bar contiene annidamenti: estrazione con il commento come perno
    ann = extract(src, r'<!-- 1\. Announcement Bar -->\s*<div class="announcement-bar">'
                       r'.*?</div>\s*</div>', "announcement-bar", "index.html")
    head = extract(src, r"<header\b.*?</header>", "header", "index.html")
    foot = extract(src, r"<footer\b.*?</footer>", "footer", "index.html")

    pages = [os.path.join(ROOT, n) for n in sorted(os.listdir(ROOT))
             if n.endswith(".html") and n not in EXCLUDE and n != "index.html"]
    blog = os.path.join(ROOT, "blog")
    pages += [os.path.join(blog, n) for n in sorted(os.listdir(blog))
              if n.endswith(".html")]

    for path in pages:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        prefix = "" if "/" not in rel else "../"
        self_ref = prefix + rel

        html = read(path)
        n_before = html

        # 1. announcement bar
        html, k1 = re.subn(
            r'<!-- 1\. Announcement Bar -->\s*<div class="announcement-bar">.*?</div>\s*</div>'
            r'|<div class="announcement-bar">.*?</div>\s*</div>',
            add_prefix(ann, prefix), html, count=1, flags=re.S)

        # 2. header
        new_head = set_active(add_prefix(head, prefix), self_ref)
        html, k2 = re.subn(r"<header\b.*?</header>", lambda _: new_head,
                           html, count=1, flags=re.S)

        # 3. footer
        html, k3 = re.subn(r"<footer\b.*?</footer>",
                           lambda _: add_prefix(foot, prefix),
                           html, count=1, flags=re.S)

        if k1 != 1 or k2 != 1 or k3 != 1:
            print(f"  !! {rel}: announcement={k1} header={k2} footer={k3}")
            continue
        if html == n_before:
            print(f"  = {rel} (già sincronizzato)")
            continue
        write(path, html)
        print(f"  ok {rel}")

    print("\nVerifica: header/footer identici alla fonte (a parte prefisso e attivo)")


if __name__ == "__main__":
    main()
