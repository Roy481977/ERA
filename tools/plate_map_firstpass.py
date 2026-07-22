#!/usr/bin/env python3
"""First-pass plate-v1 map: pin the 23 sim locations + trace main walk-paths,
in plate-v1 pixel space (1376x768). Renders an overlay for eyeball verification
and writes era-plate-map.json (importable into plate-mapper.html)."""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
BIBLE = os.path.join(HERE, "..", "design", "bible")
PLATE = os.path.join(BIBLE, "plate-v1.jpeg")

# ---- PLACES: plate-v1 pixel coords (x right, y down), 1376x768 ----
# Confidence tiers noted; off-frame ones parked at frame edges (provisional).
PLACES = {
    # distinctive landmarks (high confidence)
    "loc_stadium":        (1165, 455),   # centre of the green pitch
    "loc_main_square":    (853, 350),    # foot of the clock tower
    "loc_cafe":           (806, 380),    # terrace tables just left of tower
    "loc_north_gate":     (935, 415),    # plaza in front of the stand
    "loc_bridge":         (868, 448),    # river head, just below the square
    "loc_riverside":      (798, 520),    # riverbank walk below the bridge
    # near-landmark (medium confidence)
    "loc_museum":         (905, 332),    # right of the square, toward the ground
    "loc_pub":            (886, 348),    # The Anchor, east edge of the square
    "loc_club_offices":   (958, 372),    # ground-side offices
    "loc_club_shop":      (946, 398),    # ground-side shop
    "loc_bakery":         (720, 356),    # high street, west of square
    "loc_high_street":    (688, 346),    # high-street rooms
    "loc_corner_grocer":  (748, 366),    # corner of the high street
    # residential cluster (approximate — Roy to nudge)
    "loc_millers_row":    (240, 560),    # foreground-left terraces
    "loc_slate_house":    (318, 598),    # named home, foreground-left
    "loc_kiln_yard":      (360, 468),    # mid-left lane
    "loc_elm_row":        (560, 300),    # back-band left-centre
    "loc_oakside":        (1010, 645),   # right-foreground greenery (the old oak)
    # off-frame in plate-v1 — parked at the nearest frame edge (provisional)
    "loc_school":         (110, 232),    # far back-left (near station)
    "loc_training_ground":(30, 250),     # far back-left, off the built frame
    "loc_weavers_lane":   (34, 560),     # left edge, mid/low
    "loc_orchard_close":  (1322, 300),   # right edge, behind NE terraces
    "loc_canal_side":     (1336, 468),   # right edge, canal spur
}

# ---- PATHS: plate-v1 pixel polylines ----
PATHS = [
    {"id": "high_street", "type": "street",
     "pts": [[300, 418], [400, 402], [520, 386], [640, 372], [730, 362], [812, 358]]},
    {"id": "matchday_way", "type": "street",
     "pts": [[862, 360], [900, 382], [935, 412], [962, 432]]},
    {"id": "town_road", "type": "street",
     "pts": [[250, 432], [330, 456], [420, 470], [520, 470], [600, 452], [680, 420]]},
    {"id": "riverside_walk", "type": "path",
     "pts": [[812, 398], [788, 442], [762, 492], [720, 540], [648, 582], [560, 612]]},
    {"id": "river", "type": "river",
     "pts": [[866, 448], [848, 484], [826, 524], [802, 568], [780, 614], [766, 664], [758, 714], [752, 768]]},
    {"id": "allotment_lane", "type": "lane",
     "pts": [[560, 612], [640, 636], [720, 648], [780, 640]]},
    {"id": "ground_approach", "type": "lane",
     "pts": [[962, 432], [1010, 445], [1080, 452], [1140, 455]]},
]

def main():
    im = Image.open(PLATE).convert("RGB")
    W, H = im.size
    dr = ImageDraw.Draw(im, "RGBA")
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
        sfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = sfont = ImageFont.load_default()

    KC = {"street": (232, 185, 58), "lane": (232, 132, 58), "path": (70, 192, 110), "river": (58, 159, 232)}
    for p in PATHS:
        col = KC.get(p["type"], (255, 255, 255))
        dr.line([tuple(pt) for pt in p["pts"]], fill=col + (235,), width=5, joint="curve")
        for pt in p["pts"]:
            dr.ellipse([pt[0]-3, pt[1]-3, pt[0]+3, pt[1]+3], fill=col + (255,))

    for lid, (x, y) in PLACES.items():
        short = lid.replace("loc_", "")
        dr.ellipse([x-6, y-6, x+6, y+6], fill=(255, 60, 60, 255), outline=(255, 255, 255, 255), width=2)
        tw = dr.textlength(short, font=sfont)
        bx0, by0 = x + 8, y - 8
        dr.rectangle([bx0-2, by0-1, bx0+tw+3, by0+13], fill=(0, 0, 0, 150))
        dr.text((bx0, by0), short, fill=(255, 255, 255, 255), font=sfont)

    out = os.path.join(BIBLE, "plate-map-overlay.png")
    im.save(out)
    print("overlay ->", out)

    m = {"space": f"plate-v1 {W}x{H} px", "paths": PATHS,
         "places": {k: {"x": v[0], "y": v[1]} for k, v in PLACES.items()}}
    j = os.path.join(BIBLE, "era-plate-map.json")
    json.dump(m, open(j, "w"), indent=1)
    print("map ->", j, "places:", len(PLACES), "paths:", len(PATHS))

if __name__ == "__main__":
    main()
