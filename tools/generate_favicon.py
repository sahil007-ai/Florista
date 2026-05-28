"""
Generate favicon.ico and apple-touch-icon.png from the brand flower mark.

Renders the same 5-petal organza flower as `images/favicon.svg`, but pixel-
perfect at multiple sizes via Pillow (no SVG renderer needed).

Run from repo root:
    python3 tools/generate_favicon.py

Outputs:
    images/favicon.ico            (multi-res 16, 32, 48)
    images/apple-touch-icon.png   (180x180)

The supersample-then-downscale technique gives anti-aliased edges that
read well at every browser-tab size.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

# Brand palette
BG_TOP        = (168,  85, 122, 255)  # #a8557a — plum top
BG_BOTTOM     = (125,  58,  85, 255)  # #7d3a55 — plum bottom
PETAL_HI      = (255, 248, 251, 255)  # #fff8fb — cream highlight
PETAL_MID     = (253, 218, 232, 255)  # #fddae8 — soft pink
PETAL_LOW     = (245, 184, 208, 255)  # #f5b8d0 — deeper pink at base
STAMEN_OUTER  = (125,  58,  85, 255)  # #7d3a55 — plum stamen ring
STAMEN_INNER  = (201, 126, 160, 255)  # #c97ea0 — pink stamen
STAMEN_HI     = (255, 248, 251, 230)  # cream highlight dot
STROKE        = (125,  58,  85,  90)  # subtle plum stroke around petals


def _vertical_gradient(size: int, top: tuple, bottom: tuple) -> Image.Image:
    """Build a vertical RGBA gradient from top to bottom colors."""
    grad = Image.new("RGBA", (1, size))
    for y in range(size):
        t = y / max(size - 1, 1)
        r = round(top[0] + (bottom[0] - top[0]) * t)
        g = round(top[1] + (bottom[1] - top[1]) * t)
        b = round(top[2] + (bottom[2] - top[2]) * t)
        a = round(top[3] + (bottom[3] - top[3]) * t)
        grad.putpixel((0, y), (r, g, b, a))
    return grad.resize((size, size))


def _radial_gradient(size: int, center: tuple, inner: tuple, outer: tuple) -> Image.Image:
    """Soft radial gradient, used for petal shading."""
    img = Image.new("RGBA", (size, size))
    cx, cy = center
    max_r = math.hypot(max(cx, size - cx), max(cy, size - cy))
    px = img.load()
    for y in range(size):
        for x in range(size):
            r = math.hypot(x - cx, y - cy) / max_r
            r = min(max(r, 0.0), 1.0)
            # ease-out so the highlight reads softly
            t = r * r
            cr = round(inner[0] + (outer[0] - inner[0]) * t)
            cg = round(inner[1] + (outer[1] - inner[1]) * t)
            cb = round(inner[2] + (outer[2] - inner[2]) * t)
            ca = round(inner[3] + (outer[3] - inner[3]) * t)
            px[x, y] = (cr, cg, cb, ca)
    return img


def _petal(size: int) -> Image.Image:
    """
    Draw one teardrop petal pointing UP, centered horizontally, with the
    pointy tip near the top edge. Returns an RGBA image of side `size`.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Geometry for the petal in viewBox coords (matches favicon.svg petal-shape)
    #   M 0 -22 C 8 -19, 9 -8, 0 -3 C -9 -8, -8 -19, 0 -22 Z
    # Translate so center=(32,32) of a 64-unit canvas. Scale to image size.
    s = size / 64.0
    cx, cy = size / 2, size / 2

    def pt(x, y):
        return (cx + x * s, cy + y * s)

    # Sample the cubic bezier to a polygon (Pillow has no native bezier fill).
    def cubic(p0, p1, p2, p3, n=32):
        pts = []
        for i in range(n + 1):
            t = i / n
            mt = 1 - t
            x = (mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0]
                 + 3 * mt * t ** 2 * p2[0] + t ** 3 * p3[0])
            y = (mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1]
                 + 3 * mt * t ** 2 * p2[1] + t ** 3 * p3[1])
            pts.append((x, y))
        return pts

    p0 = pt(0, -22)
    p1 = pt(8, -19)
    p2 = pt(9, -8)
    p3 = pt(0, -3)
    p4 = pt(-9, -8)
    p5 = pt(-8, -19)

    polygon = cubic(p0, p1, p2, p3) + cubic(p3, p4, p5, p0)

    # Fill: radial-ish gradient applied inside a mask of the polygon
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)

    grad = _radial_gradient(
        size,
        center=(size * 0.5, size * 0.25),  # highlight near the tip
        inner=PETAL_HI,
        outer=PETAL_LOW,
    )
    # Blend in the mid pink at mid-radius for warmer base
    mid = Image.new("RGBA", (size, size), PETAL_MID)
    grad = Image.blend(grad, mid, 0.25)

    img.paste(grad, (0, 0), mask)

    # Subtle stroke
    draw.polygon(polygon, outline=STROKE)
    return img


def _rounded_bg(size: int, radius_ratio: float = 14 / 64) -> Image.Image:
    """Plum rounded-square background with a soft top-to-bottom gradient."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = _vertical_gradient(size, BG_TOP, BG_BOTTOM)
    mask = Image.new("L", (size, size), 0)
    radius = round(size * radius_ratio)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=radius, fill=255
    )
    img.paste(grad, (0, 0), mask)
    return img


def render(size: int) -> Image.Image:
    """Render the full favicon at the requested pixel size."""
    # Supersample 4x for clean anti-aliasing on small targets
    super_factor = 4 if size < 256 else 2
    big = size * super_factor

    canvas = _rounded_bg(big)

    # Build a single petal pointing up, then rotate 5 copies and paste.
    petal_img = _petal(big)
    cx = cy = big / 2

    for i in range(5):
        angle = -i * 72  # PIL rotates counter-clockwise; we want clockwise from top
        rotated = petal_img.rotate(angle, resample=Image.BICUBIC, center=(cx, cy))
        canvas.alpha_composite(rotated)

    # Center stamen
    draw = ImageDraw.Draw(canvas)
    r_outer = big * (5 / 64)
    r_inner = big * (3 / 64)
    r_hi    = big * (1.6 / 64)

    draw.ellipse(
        (cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer),
        fill=STAMEN_OUTER,
    )
    draw.ellipse(
        (cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner),
        fill=STAMEN_INNER,
    )
    # Cream highlight slightly off-center for life
    hx, hy = cx - big * (1.5 / 64), cy - big * (1.5 / 64)
    draw.ellipse(
        (hx - r_hi, hy - r_hi, hx + r_hi, hy + r_hi),
        fill=STAMEN_HI,
    )

    # Downscale to the target with high-quality filtering
    return canvas.resize((size, size), Image.LANCZOS)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    images = repo_root / "images"
    images.mkdir(exist_ok=True)

    # Render once at the largest needed size, then resize down for the rest.
    # Rendering each size independently gives marginally better edges, so we
    # do that for the small icons and the apple-touch separately.
    sizes_for_ico = (16, 32, 48)
    rendered_for_ico = [render(s) for s in sizes_for_ico]

    ico_path = images / "favicon.ico"
    rendered_for_ico[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes_for_ico],
        append_images=rendered_for_ico[1:],
    )
    print(f"wrote {ico_path}  ({sum(s*s for s in sizes_for_ico)} px²)")

    apple = render(180)
    apple_path = images / "apple-touch-icon.png"
    # iOS expects RGB (no alpha) on apple-touch — flatten onto plum.
    bg = Image.new("RGBA", apple.size, BG_TOP)
    bg.alpha_composite(apple)
    bg.convert("RGB").save(apple_path, format="PNG", optimize=True)
    print(f"wrote {apple_path}  ({apple_path.stat().st_size} bytes)")

    # Bonus: a high-res PNG that can be referenced as <link rel="icon" sizes="512x512">
    big = render(512)
    big_path = images / "favicon-512.png"
    big.save(big_path, format="PNG", optimize=True)
    print(f"wrote {big_path}  ({big_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
