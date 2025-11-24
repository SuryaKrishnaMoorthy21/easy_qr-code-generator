#!/usr/bin/env python3
"""
qr_generator.py
Tiny, humanized QR generator that puts an optional caption below the QR.
Author: Surya K

Requires:
    pip install qrcode[pil] Pillow
"""

from typing import Optional, Tuple
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# ---------- Configuration ----------
OUT_FILE = "qrcode_with_caption.png"
FONT_SIZE = 16
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux common
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",                              # macOS
    "C:\\Windows\\Fonts\\arial.ttf",                         # Windows
]

# ---------- Helpers ----------
def find_font(size: int = FONT_SIZE) -> ImageFont.ImageFont:
    """
    Try several common system font paths; fall back to PIL's default font.
    """
    for p in FONT_PATHS:
        try:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def measure_text(text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    """
    Measure text width and height. Uses textbbox if available for better accuracy.
    """
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    try:
        bbox = d.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height
    except Exception:
        return d.textsize(text, font=font)


def ensure_png_filename(name: str) -> str:
    """
    Ensure filename has a readable image extension. Default to .png.
    """
    name = (name or "").strip()
    if not name:
        return OUT_FILE
    base, ext = os.path.splitext(name)
    if ext.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"):
        return name
    return base + ".png"


# ---------- QR + image functions ----------
def generate_qr(text: str, box_size: int = 10, border: int = 4,
                fill_color: str = "black", back_color: str = "white") -> Image.Image:
    """
    Create a QR PIL Image from `text`.
    """
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    return img


def add_caption_below(img: Image.Image, caption: Optional[str], padding: int = 10,
                      bg_color: str = "white", text_color: str = "black") -> Image.Image:
    """
    Return a new image with caption text below the QR image.
    If caption is None or empty, returns the original image unchanged.
    """
    if not caption:
        return img

    font = find_font()
    txt_w, txt_h = measure_text(caption, font)
    img_w, img_h = img.size

    # Ensure new image width can contain caption with padding
    new_w = max(img_w, txt_w + padding * 2)
    new_h = img_h + txt_h + padding * 2

    out = Image.new("RGB", (new_w, new_h), color=bg_color)
    # center QR horizontally
    x_qr = (new_w - img_w) // 2
    out.paste(img, (x_qr, 0))

    draw = ImageDraw.Draw(out)
    x_txt = (new_w - txt_w) // 2
    y_txt = img_h + padding
    draw.text((x_txt, y_txt), caption, fill=text_color, font=font)

    return out


def open_file_platform(abspath: str) -> None:
    """
    Try to open the file using platform-appropriate command.
    Non-fatal if it fails.
    """
    try:
        if sys.platform.startswith("win"):
            os.startfile(abspath)                 # Windows
        elif sys.platform == "darwin":
            os.system(f'open "{abspath}"')        # macOS
        else:
            # Linux / other - try xdg-open
            os.system(f'xdg-open "{abspath}" &')
    except Exception:
        pass


# ---------- Main ----------
def main() -> None:
    print("Simple QR Code Generator — Surya K")
    try:
        text = input("Enter text or URL to encode (example: https://github.com/SuryaKrishnaMoorthy21): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(0)

    if not text:
        print("No text entered. Exiting.")
        sys.exit(1)

    filename = input(f"Output filename (default: {OUT_FILE}): ").strip() or OUT_FILE
    filename = ensure_png_filename(filename)
    caption = input("Optional small caption to appear below the QR (press Enter to skip): ").strip() or None

    # Generate QR
    try:
        qr_img = generate_qr(text)
    except Exception as e:
        print("Failed to generate QR code:", e)
        sys.exit(1)

    final_img = add_caption_below(qr_img, caption)

    # Save (try normal save, fallback to explicit PNG)
    try:
        final_img.save(filename)
    except Exception as e:
        # Try again with explicit format
        try:
            final_img.save(filename, format="PNG")
        except Exception as e2:
            print("Save failed:", e2)
            sys.exit(1)

    abspath = os.path.abspath(filename)
    print(f"Saved QR image to: {abspath}")

    # Try to open automatically
    open_file_platform(abspath)
    print("Done. You can open the file from the path above.")

if __name__ == "__main__":
    main()
