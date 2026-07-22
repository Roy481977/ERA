#!/usr/bin/env python3
"""Render a plate-map JSON (plate-v1 pixel space) as an overlay for review.
Usage: render_map.py <map.json> <out.png>"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
PLATE = os.path.join(HERE, "..", "design", "bible", "plate-v1.jpeg")
KC = {"street": (232, 185, 58), "lane": (232, 132, 58), "path": (70, 192, 110), "river": (58, 159, 232)}

def main(mp, out):
    m = json.load(open(mp))
    im = Image.open(PLATE).convert("RGB")
    W, H = im.size
    # widen canvas so off-frame pins (negative / >W) are visible
    pad = 140
    canvas = Image.new("RGB", (W + 2 * pad, H + 90), (30, 30, 34))
    canvas.paste(im, (pad, 0))
    dr = ImageDraw.Draw(canvas, "RGBA")
    try:
        sfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        sfont = ImageFont.load_default()

    def X(x): return x + pad

    # frame edges
    dr.rectangle([pad, 0, pad + W, H], outline=(255, 255, 255, 120), width=2)

    for p in m.get("paths", []):
        col = KC.get(p.get("type"), (255, 255, 255))
        pts = [(X(a), b) for a, b in p["pts"]]
        if len(pts) >= 2:
            dr.line(pts, fill=col + (230,), width=4, joint="curve")

    for lid, pt in m.get("places", {}).items():
        x, y = X(pt["x"]), pt["y"]
        short = lid.replace("loc_", "")
        off = pt["x"] < 0 or pt["x"] > W or pt["y"] < 0 or pt["y"] > H
        fill = (90, 190, 255, 255) if off else (255, 60, 60, 255)
        dr.ellipse([x-6, y-6, x+6, y+6], fill=fill, outline=(255, 255, 255, 255), width=2)
        tw = dr.textlength(short, font=sfont)
        dr.rectangle([x+7, y-9, x+11+tw, y+4], fill=(0, 0, 0, 160))
        dr.text((x+9, y-8), short, fill=(255, 255, 255, 255), font=sfont)

    canvas.save(out)
    print("->", out, canvas.size)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
