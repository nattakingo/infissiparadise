"""Genera favicon.ico (multirisona) replicando il disegno di favicon.svg.

favicon.svg: rounded-rect #4C8A71 + "IP" bianco.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "favicon.ico")
BG = (76, 138, 113, 255)      # #4C8A71
FG = (255, 255, 255, 255)
SIZES = [16, 32, 48, 64, 128, 256]
FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
]


def load_font(px):
    for f in FONT_CANDIDATES:
        if os.path.isfile(f):
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def render(size):
    s = 4  # render iper-risoluto e poi ridotto: testo anti-alias pulito
    img = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = int(size * s * 14 / 64)
    d.rounded_rectangle([0, 0, size * s - 1, size * s - 1], radius=radius, fill=BG)

    font = load_font(int(size * s * 30 / 64))
    text = "IP"
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # il testo SVG e' centrato su y=42 per un font di 30px in una viewBox 64
    cx, cy = size * s / 2, size * s * 42 / 64
    d.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, font=font, fill=FG)
    return img.resize((size, size), Image.LANCZOS)


def main():
    base = render(256)
    base.save(OUT, format="ICO", sizes=[(n, n) for n in SIZES])
    print(f"favicon.ico scritto ({os.path.getsize(OUT) / 1024:.0f} KB, "
          f"taglie: {', '.join(str(n) for n in SIZES)})")


if __name__ == "__main__":
    main()
