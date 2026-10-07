"""Rigenera sitemap.xml con il dominio canonico e lastmod reali (mtime file)."""
import os
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://infissiparadise.it"

PAGES = [
    ("index.html", "daily", "1.0"),
    ("finestre.html", "monthly", "0.9"),
    ("porte-blindate.html", "monthly", "0.9"),
    ("persiane.html", "monthly", "0.8"),
    ("avvolgibili.html", "monthly", "0.8"),
    ("cassonetti.html", "monthly", "0.7"),
    ("zanzariere.html", "monthly", "0.7"),
    ("grate-sicurezza.html", "monthly", "0.7"),
    ("tende-da-sole.html", "monthly", "0.7"),
    ("chi-siamo.html", "monthly", "0.6"),
    ("contatti.html", "monthly", "0.8"),
    ("privacy.html", "yearly", "0.3"),
    ("cookie-policy.html", "yearly", "0.3"),
    ("blog/bonus-sicurezza.html", "yearly", "0.6"),
    ("blog/detrazioni-fiscali-infissi.html", "yearly", "0.6"),
    ("blog/iva-agevolata-inferriate.html", "yearly", "0.6"),
    ("blog/materiali-finestre.html", "yearly", "0.6"),
]


def loc(rel):
    return SITE + "/" if rel == "index.html" else f"{SITE}/{rel}"


def lastmod(rel):
    path = os.path.join(ROOT, rel)
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, timezone.utc).date().isoformat()


def main():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for rel, freq, prio in PAGES:
        if not os.path.isfile(os.path.join(ROOT, rel)):
            print(f"  !! mancante {rel}")
            continue
        out += [
            "  <url>",
            f"    <loc>{loc(rel)}</loc>",
            f"    <lastmod>{lastmod(rel)}</lastmod>",
            f"    <changefreq>{freq}</changefreq>",
            f"    <priority>{prio}</priority>",
            "  </url>",
        ]
    out.append("</urlset>")

    dest = os.path.join(ROOT, "sitemap.xml")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"sitemap.xml: {len(PAGES)} URL, ultimo lastmod {date.today()}")


if __name__ == "__main__":
    main()
