from __future__ import annotations

import hashlib
import os
from pathlib import Path


def make_og(path: Path, label: str, brand: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 630
    digest = hashlib.sha256(str(path.stem).encode()).hexdigest()
    bg = tuple(int(digest[i : i + 2], 16) for i in (0, 2, 4))
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    title_font = None
    small_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            title_font = ImageFont.truetype(fp, 96)
            small_font = ImageFont.truetype(fp, 40)
            break
    if title_font is None:
        title_font = ImageFont.load_default(size=64)
        small_font = ImageFont.load_default(size=32)
    words = label.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if (
            current
            and draw.textlength(current + " " + word, font=title_font) > width - 160
        ):
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    y = height // 2 - 40 * max(1, len(lines) // 2)
    primer = (255, 255, 255)
    for line in lines[:4]:
        text_width = draw.textlength(line, font=title_font)
        draw.text(((width - text_width) / 2, y), line, font=title_font, fill=primer)
        y += 110
    brand_width = draw.textlength(brand, font=small_font)
    draw.text(
        ((width - brand_width) / 2, height - 90),
        brand,
        font=small_font,
        fill=(230, 230, 230),
    )
    img.save(path, format="PNG")
