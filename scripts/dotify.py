#!/usr/bin/env python3
"""Turn a raster image into a dot-matrix SVG portrait.

Each source pixel (after downscaling to --cols columns) becomes a circle whose
radius tracks luminance and whose fill is the pixel's own colour, so a single
colour SVG serves both GitHub themes.

Usage:
    python scripts/dotify.py assets/avatar.png -o assets/portrait \
        --cols 90 --detail 0.55 --color
"""
import argparse
from PIL import Image, ImageOps


def build(src, out, cols, detail, color, gap, bg_cutoff):
    img = Image.open(src).convert("RGB")
    w, h = img.size
    rows = max(1, round(cols * h / w))
    small = img.resize((cols, rows), Image.LANCZOS)
    gray = small.convert("L")

    step = 10.0                     # grid spacing in SVG user units
    r_max = step / 2 * (1 + gap)    # max dot radius
    px = small.load()
    gx = gray.load()

    width = cols * step
    height = rows * step
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" '
        f'height="{height:.0f}" role="img" aria-label="dot-matrix portrait">'
    ]
    for y in range(rows):
        for x in range(cols):
            lum = gx[x, y] / 255.0
            # drop the light studio background
            if lum >= bg_cutoff:
                continue
            # darker pixels -> larger dots
            r = r_max * ((1 - lum) ** detail)
            if r < 0.35:
                continue
            cx = x * step + step / 2
            cy = y * step + step / 2
            if color:
                cr, cg, cb = px[x, y]
                fill = f"#{cr:02x}{cg:02x}{cb:02x}"
            else:
                fill = "#39d353"
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{fill}"/>'
            )
    parts.append("</svg>")
    svg = "".join(parts)
    with open(f"{out}.svg", "w") as fh:
        fh.write(svg)
    print(f"wrote {out}.svg  ({cols}x{rows} grid, {len(parts)-2} dots)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out", default="assets/portrait")
    ap.add_argument("--cols", type=int, default=90)
    ap.add_argument("--detail", type=float, default=0.55,
                    help="contrast curve; lower = punchier")
    ap.add_argument("--color", action="store_true")
    ap.add_argument("--gap", type=float, default=0.08)
    ap.add_argument("--bg-cutoff", type=float, default=1.0, dest="bg_cutoff",
                    help="skip pixels brighter than this (0-1) to drop a light background")
    a = ap.parse_args()
    build(a.src, a.out, a.cols, a.detail, a.color, a.gap, a.bg_cutoff)
