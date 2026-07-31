#!/usr/bin/env python3
"""Regenerate the angled book render on the landing page (docs/assets/book-3d.webp).

Pipeline:
  1. render ../kaappi-book/build/cover.pdf at 400 DPI (needs `make cover` there),
  2. crop the front-cover panel out of the KDP wrap sheet,
  3. hand that panel to gemini-3-pro-image as an image reference, so the cover
     art and typography are photographed rather than re-invented,
  4. mask the result so it dissolves into the landing page's espresso book band.

The band is #180E09 -- the cover's own background color -- and the render's
alpha falls off through a blurred capsule around the book, so no rectangular
frame shows against it. That is why the prompt insists on a plain #180E09
backdrop: any floor, wall or vignette would survive the mask as a visible box.

Usage:
    GEMINI_API_KEY=... python3 scripts/generate-book-3d.py
    python3 scripts/generate-book-3d.py --raw /tmp/render.png   # skip the API

Image generation is nondeterministic. After regenerating, open the render at
full size and check four things:

  1. Geometry. The spine and the fore-edge are opposite faces of a closed
     book, so at most one can face the camera. Only the spine (left) may
     show, plus a sliver of the page block's head along the top edge. A
     cream stack of page edges down the RIGHT side is impossible — an
     earlier render had both and shipped before anyone noticed.
  2. The title block still reads "Kaappi / A Scheme Programming Language",
     with the real letterforms rather than re-drawn ones.
  3. The spine text is present but unemphasized.
  4. No hard edge against the band — dissolve() asserts the margin it needs,
     but eyeball the result over #180E09 anyway.
"""
import argparse
import base64
import io
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

MODEL = "gemini-3-pro-image"
DPI = 400
ESPRESSO = "#180E09"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.environ.get("KAAPPI_BOOK", os.path.join(ROOT, "..", "kaappi-book"))
OUT = os.path.join(ROOT, "docs", "assets", "book-3d.webp")

PROMPT = f"""\
Photograph the EXACT book shown in the reference image as a real physical \
trade paperback, closed, standing upright and floating in mid-air with no \
surface beneath it.

GEOMETRY - get this exactly right. The book is a closed rectangular block \
rotated about 35 degrees about its vertical axis, so its LEFT edge, the \
SPINE, swings well toward the camera and reads as a broad, clearly visible \
face - wide enough to carry legible type - rather than a thin sliver. \
Exactly TWO faces of the book are visible and no others: the front cover, \
foreshortened by that rotation, and the spine running down the left side of \
it. The opposite edge - the fore-edge, where the pages open - is on \
the RIGHT, turned away from the camera and completely hidden behind the \
front cover. The spine and the fore-edge point in opposite directions, so \
they can never both be seen at once: do NOT draw any stack of page edges, \
any cream-white block of paper, any fanned or ruffled pages, and no second \
side face anywhere along the right-hand edge. The right edge of the front \
cover is simply the cover's outline against the background.

The camera sits a little ABOVE the book and tilts slightly down, so a \
shallow sliver of the book's top edge is also visible in perspective: the \
dark cover's top edge, and just inside it the cream-white head of the closed \
page block. That thin band along the top is the only paper that shows.

CRITICAL - the front cover artwork is a fixed, unchangeable reference. \
Reproduce it pixel-for-pixel, only warped by perspective: the same cream \
coffee cup on a saucer, the same cream lambda-shaped steam ribbon, the same \
amber radial glow, the same dark espresso background, and the same \
typography reading exactly "Kaappi", then "A Scheme Programming Language", \
then a coffee-bean divider, then "R7RS-small - Zig - Batteries Included", \
then "Baiju Muthukadan". Do not redraw, restyle, re-letter, re-space or \
translate any of it. Every letterform, weight and position must match the \
reference.

The book: 6 x 9 inch trade paperback, 337 pages, so the spine is a \
substantial 19 mm (3/4 inch) thick - a chunky perfect-bound volume with real \
heft, not a thin booklet. Matte soft-touch cover stock with a barely visible \
paper tooth - no gloss, no laminate sheen, no reflections. The spine is the \
same dark espresso brown as the cover background, and because it is turned \
toward the camera its type must be crisp and readable. The spine type is \
printed sideways, rotated a quarter turn clockwise so it reads top to \
bottom: a small caramel lambda near the head, then in cream sans-serif the \
word "Kaappi" in bold followed by "A Scheme Programming Language" in regular \
weight, and lower down, smaller and in tan, "Baiju Muthukadan". Spell those \
exactly, with no invented words, no publisher logo and no other spine \
markings. Slightly rounded, gently worn cover corners; the cover has the \
faint natural curl of a real perfect-bound paperback, not a rigid box.

Lighting: a single soft warm key light from the upper left, like a lamp over \
a reading desk. Gentle falloff across the front cover, a slightly darker \
spine, and a soft warm rim along the book's top edge. A soft diffuse drop \
shadow floats well below the book, blurred and low in contrast.

Background: completely plain, flat, solid dark espresso brown {ESPRESSO} \
filling the entire frame edge to edge, with no gradient, vignette, pattern, \
texture, floor line, horizon, wall, desk, props or other objects. The book \
and its shadow are the only things in the image. The four corners and all \
four edges must be exactly {ESPRESSO}.

The book is centred with generous empty space on all sides and nothing \
cropped by the frame. Sharp focus throughout, no depth-of-field blur, no \
film grain, no lens flare, no added text, captions, watermarks or logos \
anywhere outside the cover artwork itself.\
"""


def front_cover() -> bytes:
    """Render cover.pdf and crop the front panel out of the KDP wrap sheet."""
    pdf = os.path.join(BOOK, "build", "cover.pdf")
    if not os.path.exists(pdf):
        sys.exit(f"{pdf} not found -- run `make cover` in {BOOK} first")
    with tempfile.TemporaryDirectory() as tmp:
        stem = os.path.join(tmp, "sheet")
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-singlefile", pdf, stem],
                       check=True)
        sheet = Image.open(stem + ".png").convert("RGB")
    # Sheet = 12.25in (2 x 6in trim + 4 x 0.125in bleed) + spine, so the spine
    # width -- and with it the front panel's left edge -- follows from the
    # rendered width. No need to duplicate \PageCount from cover.tex.
    spine = sheet.width / DPI - 12.25
    left = round((6.125 + spine) * DPI)
    top = round(0.125 * DPI)
    front = sheet.crop((left, top, left + 6 * DPI, top + 9 * DPI))
    print(f"sheet {sheet.size}, spine {spine:.3f}in, front panel {front.size}")
    front.thumbnail((1024, 1536), Image.LANCZOS)
    buf = io.BytesIO()
    front.save(buf, "PNG")
    return buf.getvalue()


def generate(ref: bytes) -> Image.Image:
    body = {
        "contents": [{"parts": [
            {"inlineData": {"mimeType": "image/png",
                            "data": base64.b64encode(ref).decode()}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "3:4", "imageSize": "2K"},
        },
    }
    import urllib.request
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    for part in resp["candidates"][0]["content"]["parts"]:
        blob = part.get("inlineData") or part.get("inline_data")
        if blob:
            return Image.open(io.BytesIO(base64.b64decode(blob["data"]))).convert("RGB")
    sys.exit("no image in response: " + json.dumps(resp)[:800])


def dissolve(im: Image.Image) -> Image.Image:
    """Alpha-mask the render so it fades into the band with no visible frame.

    A rectangular border fade would leave the backdrop's ambient floor glow
    (~20 levels above espresso) ending on a straight line. Instead the mask is
    a rounded rectangle around the book, Gaussian-blurred: the glow survives
    close to the book and dies off smoothly in every direction.
    """
    W, H = im.size
    # The lit book, without its faint drop shadow (that lives in the falloff).
    box = im.convert("L").point(lambda v: 255 if v > 60 else 0).getbbox()
    l, t, r, b = box
    print("book bbox", box)
    # Blur radius: keep the book >= 2 sigma inside the capsule (so it stays
    # fully opaque) and the 3-sigma falloff inside the frame -- i.e. 5 sigma
    # of headroom on every side.
    sigma = int(min(l, t, W - r, H - b) / 5)
    if sigma < 20:
        sys.exit(f"only {sigma * 5}px of margin around the book; regenerate "
                 "with more empty space around it")
    print("falloff sigma", sigma)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (l - 2 * sigma, t - 2 * sigma, r + 2 * sigma, b + 2 * sigma),
        radius=3 * sigma, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(sigma))
    im = im.convert("RGBA")
    im.putalpha(mask)
    return im.crop((max(0, l - 5 * sigma), max(0, t - 5 * sigma),
                    min(W, r + 5 * sigma), min(H, b + 5 * sigma)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", help="post-process this render instead of calling the API")
    ap.add_argument("--save-raw", help="also keep the unmasked render here")
    ap.add_argument("--out", default=OUT, help=f"default {os.path.relpath(OUT, ROOT)}")
    args = ap.parse_args()

    raw = Image.open(args.raw).convert("RGB") if args.raw else generate(front_cover())
    print("render", raw.size)
    if args.save_raw:
        raw.save(args.save_raw)
    im = dissolve(raw)
    out = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
    out.save(args.out, quality=88, method=6)
    print(f"wrote {args.out} {out.size} {os.path.getsize(args.out) // 1024}KB")
    print("update the img width/height in overrides/home.html if the size changed")


if __name__ == "__main__":
    main()
