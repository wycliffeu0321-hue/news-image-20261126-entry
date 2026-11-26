#!/usr/bin/env python3
"""Compose the 'One Day in One Picture' newspaper front-page poster.

Reads the five illustration panels in assets/ and writes entry.png
(1024x1024) in the repo root, next to this script.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
CREAM = "#F3EAD8"
NAVY = "#14263F"
ORANGE = "#D9622B"
WHITE = "#FFFFFF"
MAX_BYTES = 1048576

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_size(draw, text, path, size, max_width, min_size=10):
    """Largest size at or below `size` at which `text` fits `max_width`."""
    while size > min_size:
        if draw.textlength(text, font=font(path, size)) <= max_width:
            return size
        size -= 1
    return min_size


def fit_font(draw, text, path, size, max_width, min_size=10):
    """Shrink a font from `size` down until `text` fits `max_width`."""
    return font(path, fit_size(draw, text, path, size, max_width, min_size))


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap using PIL textlength."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def centre_crop(img, tw, th):
    """Resize `img` to cover (tw, th) and centre-crop the overflow."""
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return img.crop((x, y, x + tw, y + th))


def panel(name):
    return Image.open(os.path.join(ASSETS, name)).convert("RGB")


def draw_panel(draw, img, x, y, panel_img, headline, detail, hf):
    """One grid cell: 500x148 image with an 84px caption block below."""
    img.paste(centre_crop(panel_img, 500, 148), (x, y))
    draw.rectangle([x, y + 148, x + 500, y + 232], fill=CREAM)
    draw.text((x + 10, y + 152), headline, font=hf, fill=NAVY)
    df = font(FONT_REG, 20)
    lines = wrap(draw, detail, df, 480)[:2]
    ly = y + 184
    for ln in lines:
        draw.text((x + 10, ly), ln, font=df, fill=NAVY)
        ly += 24


img = Image.new("RGB", (W, H), CREAM)
draw = ImageDraw.Draw(img)

# --- Masthead band y0-76 (navy) ---
draw.rectangle([0, 0, W, 76], fill=NAVY)
mf = font(FONT_BOLD, 40)
draw.text((28, 38), "ONE DAY IN ONE PICTURE", font=mf, fill=CREAM, anchor="lm")
draw.text((996, 38), "WORLD NEWS", font=mf, fill=CREAM, anchor="rm")

# --- Date band y76-130 (orange) ---
draw.rectangle([0, 76, W, 130], fill=ORANGE)
dfont = font(FONT_BOLD, 38)
draw.text((512, 103), "THURSDAY · 26 NOVEMBER 2026", font=dfont,
          fill=WHITE, anchor="mm")

# --- Hero image y130-436 ---
img.paste(centre_crop(panel("hero.png"), 1024, 306), (0, 130))
draw.rectangle([0, 130, W - 1, 435], outline=NAVY, width=3)

# --- Hero caption band y436-502 (navy) ---
draw.rectangle([0, 436, W, 502], fill=NAVY)
h1 = "UNITED STATES — A STORM STOPS THE PARADE"
h1s = fit_size(draw, h1, FONT_BOLD, 27, 940)
h1f = font(FONT_BOLD, h1s)
h2 = ("The 100th Macy's Thanksgiving parade is postponed for the first "
      "time ever; 400,000 lose power.")
h2s = fit_size(draw, h2, FONT_REG, 22, 940)
h2f = font(FONT_REG, h2s)
# Centre the two lines as a block inside the 66px band.
block_h = h1s + 4 + h2s
hy = 436 + (66 - block_h) // 2
draw.text((28, hy), h1, font=h1f, fill=CREAM)
draw.text((28, hy + h1s + 4), h2, font=h2f, fill=CREAM)

# --- Panel grid: two rows, two columns ---
cells = [
    (12, 502, "kyiv.png", "UKRAINE — MISSILES OVER KYIV",
     "Russia strikes the capital with ballistic missiles and hits grain "
     "ships near Odesa."),
    (512, 502, "tariffs.png", "TRADE — NEW TARIFFS ON 14 NATIONS",
     "Washington targets 14 trading partners, blaming factory "
     "overcapacity."),
    (12, 734, "nkorea.png", "NORTH KOREA — A BIGGER ARSENAL",
     "Pyongyang signals it will expand its nuclear weapons programme."),
    (512, 734, "mideast.png", "MIDDLE EAST — STRIKES IN GAZA AND KUWAIT",
     "Israeli strikes kill nine in Gaza; an Iranian drone strike kills "
     "two Italians in Kuwait."),
]
# One shared headline size for all four cells: the largest size at which
# even the longest headline fits on a single line.
head_size = min(fit_size(draw, c[3], FONT_BOLD, 24, 480) for c in cells)
head_font = font(FONT_BOLD, head_size)
for x, y, fname, headline, detail in cells:
    draw_panel(draw, img, x, y, panel(fname), headline, detail, head_font)

# --- Ticker band y966-1024 (navy) ---
draw.rectangle([0, 966, W, H], fill=NAVY)
ticker = ("ALSO: ECB picks Hernández de Cos to succeed Lagarde • UK net "
          "migration falls to 77,000, a 30-year low • Cairo highway fire "
          "kills dozens • Chip shortage triples memory prices on Black "
          "Friday eve • FCC approves SpaceX plan for up to 1 million "
          "orbital data-centre satellites • EU leaders haggle over the "
          "budget and Ukraine funds in Brussels")
tsize = 19
while tsize > 10:
    tf = font(FONT_REG, tsize)
    tlines = wrap(draw, ticker, tf, 984)
    if len(tlines) <= 2:
        break
    tsize -= 1
lh = tsize + 5
ty = 966 + (58 - lh * len(tlines)) // 2
for ln in tlines[:2]:
    draw.text((512, ty), ln, font=tf, fill=CREAM, anchor="ma")
    ty += lh

img.save(OUT)
size = os.path.getsize(OUT)
if size > MAX_BYTES:
    img.quantize(colors=256, dither=Image.Dither.NONE).save(OUT)
    size = os.path.getsize(OUT)
print(f"entry.png: {img.width}x{img.height}, {size} bytes")
