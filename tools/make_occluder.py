#!/usr/bin/env python3
"""Cut a foreground occluder from the plate: the front greenery arc that should
draw IN FRONT of the living layer, giving the 2.5D depth. Green vegetation in
the lower band only (keeps mid-ground house-trees and the water out of it, so
the heron on the river stays visible). Outputs web/assets/occluder.png (RGBA)."""
import numpy as np
from PIL import Image, ImageFilter
import pathlib

bible = pathlib.Path(__file__).resolve().parent.parent / "design/bible"
web = pathlib.Path(__file__).resolve().parent.parent / "web"
im = Image.open(bible / "plate-v1-graded.jpeg").convert("RGB")
W, H = im.size
a = np.asarray(im).astype(np.int16)
R, G, B = a[..., 0], a[..., 1], a[..., 2]

# vegetation: green clearly dominant, not too dark, not the tan roofs
veg = (G > R + 12) & (G > B + 6) & (G > 60)

# front-edge curve: only keep vegetation in the foreground band. The band starts
# higher on the sides (front gardens wrap around) and dips across the middle.
ys = np.arange(H)[:, None].repeat(W, axis=1)
xs = np.arange(W)[None, :].repeat(H, axis=0)
# parabola-ish front edge: lowest allowed y per column (above=excluded)
front = 470 + 70 * np.cos((xs - 700) / 700 * 1.4)   # ~470 centre, rises to sides
band = ys > front
mask = (veg & band).astype(np.uint8) * 255

m = Image.fromarray(mask, "L").filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
out = Image.new("RGBA", (W, H))
rgba = np.dstack([np.asarray(im), np.asarray(m)])
out = Image.fromarray(rgba, "RGBA")
out.save(web / "assets/occluder.png")
# debug composite
dbg = im.convert("RGBA"); dbg.alpha_composite(Image.merge("RGBA", (
    Image.new("L", (W, H), 255), Image.new("L", (W, H), 40), Image.new("L", (W, H), 120), m)))
dbg.convert("RGB").save("/tmp/occluder_dbg.png")
print("occluder ->", web / "assets/occluder.png", "coverage %.1f%%" % (100 * (mask > 0).mean()))
