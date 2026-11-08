# -*- coding: utf-8 -*-
"""
Generate a 1080x1920 Douyin selling cover for Gannan navel oranges.

Style reference: the photo attached to issue #3 (reference.png) — a lush
close-up of glossy navel oranges with a juicy cross-section hero slice,
warm golden backlight, a scalloped maroon badge top-right, and a dark
vignette at the bottom for copy. This script keeps that photographic hero
and art-directs a dedicated selling cover on top of it: a clean warm light
wash, a stronger bottom copy zone, and a styled selling-point copy block
("现摘现发 · 皮薄多汁") plus a price/selling tag.

Output: cover.png (1080x1920, RGB).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference.png")
OUT = os.path.join(HERE, "cover.png")

W, H = 1080, 1920

FONT_HEI = r"C:\Windows\Fonts\simhei.ttf"
FONT_DENG = r"C:\Windows\Fonts\Deng.ttf"
FONT_DENGB = r"C:\Windows\Fonts\Dengb.ttf"
FONT_KAI = r"C:\Windows\Fonts\simkai.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vertical_gradient(size, stops):
    """stops: list of (position 0..1, (r,g,b,a)). Returns RGBA image."""
    w, h = size
    arr = np.zeros((h, w, 4), dtype=np.float32)
    positions = [s[0] for s in stops]
    for y in range(h):
        p = y / (h - 1)
        # find surrounding stops
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= p <= p1 or i == len(stops) - 2 and p > p1:
                if p1 == p0:
                    t = 0
                else:
                    t = (p - p0) / (p1 - p0)
                t = max(0.0, min(1.0, t))
                col = [c0[k] + (c1[k] - c0[k]) * t for k in range(4)]
                arr[y, :, :] = col
                break
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def text_with_glow(base, xy, text, fnt, fill, glow_fill, glow_radius,
                   anchor="mm", stroke_width=0, stroke_fill=None):
    """Draw text onto an RGBA layer with an outer glow, paste onto base."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # glow
    if glow_radius > 0:
        g = Image.new("RGBA", base.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.text(xy, text, font=fnt, fill=glow_fill, anchor=anchor,
                stroke_width=stroke_width, stroke_fill=glow_fill)
        g = g.filter(ImageFilter.GaussianBlur(glow_radius))
        layer = Image.alpha_composite(layer, g)
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=fnt, fill=fill, anchor=anchor,
           stroke_width=stroke_width, stroke_fill=stroke_fill)
    return Image.alpha_composite(base, layer)


def rounded_rect_glow(base, box, radius, fill, glow_color, glow_radius=18):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if glow_radius > 0:
        g = Image.new("RGBA", base.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.rounded_rectangle(box, radius=radius, fill=glow_color)
        g = g.filter(ImageFilter.GaussianBlur(glow_radius))
        layer = Image.alpha_composite(layer, g)
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill)
    return Image.alpha_composite(base, layer)


def main():
    im = Image.open(REF).convert("RGB")

    # --- 1. Punch up the hero photo: saturation + contrast warmth ---
    im = ImageEnhance.Color(im).enhance(1.10)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Brightness(im).enhance(1.03)
    base = im.convert("RGBA")

    # --- 2. Warm clean light wash at top (clean background light) ---
    top_wash = vertical_gradient(
        (W, H),
        [
            (0.00, (255, 214, 128, 70)),
            (0.22, (255, 200, 110, 30)),
            (0.40, (255, 190, 100, 0)),
            (0.60, (0, 0, 0, 0)),
            (0.72, (40, 18, 0, 60)),
            (0.86, (30, 12, 0, 150)),
            (1.00, (18, 7, 0, 205)),
        ],
    )
    base = Image.alpha_composite(base, top_wash)

    # --- 3. Bottom copy zone: deepened dark panel gradient ---
    bottom_panel = vertical_gradient(
        (W, H),
        [
            (0.0, (0, 0, 0, 0)),
            (0.70, (0, 0, 0, 0)),
            (0.78, (28, 11, 2, 150)),
            (0.88, (22, 8, 1, 205)),
            (0.95, (16, 6, 0, 232)),
            (1.00, (12, 4, 0, 242)),
        ],
    )
    base = Image.alpha_composite(base, bottom_panel)

    # --- 4. Top-right badge already in photo; reinforce a clean price tag
    #        top-left to add a strong selling hook (带货 style). ---
    d = ImageDraw.Draw(base)

    # small "新鲜现摘" ribbon tag top-left
    tag_box = (60, 150, 60 + 300, 150 + 96)
    base = rounded_rect_glow(
        base, tag_box, radius=48,
        fill=(213, 32, 17, 235),
        glow_color=(255, 140, 90, 130),
        glow_radius=16,
    )
    d = ImageDraw.Draw(base)
    f_tag = font(FONT_DENGB, 52)
    d.text((tag_box[0] + 150, tag_box[1] + 48), "新鲜现摘", font=f_tag,
           fill=(255, 255, 255, 255), anchor="mm")

    # --- 5. Selling points block in bottom copy zone ---
    cx = W // 2

    # line A: main selling point
    y_pts = 1545
    f_pts = font(FONT_DENGB, 112)
    pts = "现摘现发 · 皮薄多汁"
    base = text_with_glow(
        base, (cx, y_pts), pts, f_pts,
        fill=(255, 248, 224, 255),
        glow_fill=(255, 110, 12, 130),
        glow_radius=16,
        stroke_width=5,
        stroke_fill=(120, 42, 0, 255),
    )

    # line B: secondary hook
    y_sub = 1700
    f_sub = font(FONT_DENG, 74)
    sub = "赣南产地直发  酸甜爆汁"
    base = text_with_glow(
        base, (cx, y_sub), sub, f_sub,
        fill=(255, 226, 170, 255),
        glow_fill=(120, 40, 0, 160),
        glow_radius=14,
        stroke_width=3,
        stroke_fill=(90, 30, 0, 220),
    )

    # divider line under sub
    d = ImageDraw.Draw(base)
    d.line([(cx - 300, 1770), (cx + 300, 1770)], fill=(255, 190, 90, 200), width=4)

    # bottom CTA pill
    cta_box = (cx - 250, 1810, cx + 250, 1810 + 92)
    base = rounded_rect_glow(
        base, cta_box, radius=46,
        fill=(255, 176, 32, 245),
        glow_color=(255, 120, 20, 150),
        glow_radius=20,
    )
    d = ImageDraw.Draw(base)
    f_cta = font(FONT_DENGB, 56)
    d.text((cx, 1810 + 46), "当季新果 · 点击抢购", font=f_cta,
           fill=(120, 30, 0, 255), anchor="mm")

    # --- 6. Subtle bottom dark strip to seat the CTA cleanly ---
    base.save(OUT)
    print("saved", OUT, base.size)


if __name__ == "__main__":
    main()
