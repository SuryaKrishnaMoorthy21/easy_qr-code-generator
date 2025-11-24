#!/usr/bin/env python3
"""
qr_generator.py
Tiny, humanized QR generator that puts a caption below the QR.
Author: Surya K (humanized variable names)
Requires: qrcode, Pillow
Install: pip install qrcode pillow
"""

from typing import Optional
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import sys

OUT_FILE = "qrcode_with_caption.png"
FONT_SIZE = 16
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]

def get_font(s: int = FONT_SIZE):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, s)
            except Exception:
                pass
    return ImageFont.load_default()

def make_qr(t: str, box: int = 10, br: int = 4, fg: str = "black", bg: str = "white") -> Image.Image:
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box, border=br)
    q.add_data(t)
    q.make(fit=True)
    im = q.make_image(fill_color=fg, back_color=bg).convert("RGB")
    return im

def _measure(txt: str, fnt: ImageFont.ImageFont):
    # small helper to measure text size
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    try:
        bb = d.textbbox((0, 0), txt, font=fnt)
        return bb[2] - bb[0], bb[3] - bb[1]
    except Exception:
        return d.textsize(txt, font=fnt)

def add_caption(qr: Image.Image, cap: Optional[str], pad: int = 10, bgc: str = "white", tc: str = "black") -> Image.Image:
    if not cap:
        return qr

    f = get_font()
    tw, th = _measure(cap, f)
    w, h = qr.size

    new_w = max(w, tw + pad * 2)
    new_h = h + th + pad * 2

    out = Image.new("RGB", (new_w, new_h), color=bgc)
    x_qr = (new_w - w) // 2
    out.paste(qr, (x_qr, 0))

    d = ImageDraw.Draw(out)
    x_txt = (new_w - tw) // 2
    y_txt = h + pad
    d.text((x_txt, y_txt), cap, fill=tc, font=f)

    return out

def main():
    print("Simple QR — Surya K")
    try:
        t = input("Text or URL (example: https://github.com/SuryaKrishnaMoorthy21): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(0)

    if not t:
        print("No text. Bye.")
        sys.exit(1)

    out = input(f"Output filename (default: {OUT_FILE}): ").strip() or OUT_FILE
    cap = input("Caption (press Enter to skip): ").strip() or None

    try:
        qr = make_qr(t)
    except Exception as e:
        print("QR failed:", e)
        sys.exit(1)

    img = add_caption(qr, cap)

    try:
        img.save(out)
        print("Saved to:", out)
    except Exception as e:
        print("Save failed:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
