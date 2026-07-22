#!/usr/bin/env python3
"""Build tools/plate-mapper.html from the template: embed the plate (base64),
the 23 location ids/names, and the current era-plate-map.json as the starting
state so the tool opens ready to edit."""
import base64, json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
tpl = (root / "tools/plate-mapper-template.html").read_text()
img_b64 = base64.b64encode((root / "design/bible/plate-v1.jpeg").read_bytes()).decode()
init = json.loads((root / "design/bible/era-plate-map.json").read_text())

LOCS = [
    ("loc_stadium", "Stadium"), ("loc_main_square", "Main Square"), ("loc_bakery", "Bakery"),
    ("loc_cafe", "Café"), ("loc_riverside", "Riverside"), ("loc_school", "The School"),
    ("loc_museum", "The Museum"), ("loc_pub", "The Anchor (pub)"), ("loc_bridge", "The Old Bridge"),
    ("loc_millers_row", "Miller's Row"), ("loc_high_street", "High Street Rooms"),
    ("loc_oakside", "Oakside Cottages"), ("loc_elm_row", "Elm Row"), ("loc_kiln_yard", "Kiln Yard"),
    ("loc_canal_side", "Canalside"), ("loc_orchard_close", "Orchard Close"),
    ("loc_weavers_lane", "Weavers' Lane"), ("loc_north_gate", "North Gate (the Ground plaza)"),
    ("loc_slate_house", "The Slate House"), ("loc_club_offices", "Club Offices — ERA FC"),
    ("loc_club_shop", "The Club Shop"), ("loc_corner_grocer", "The Corner Grocer"),
    ("loc_training_ground", "The Training Ground"),
]
locs_json = json.dumps([{"id": i, "name": n} for i, n in LOCS])

out = (tpl.replace("__IMG__", img_b64)
          .replace("__LOCS__", locs_json)
          .replace("__INIT__", json.dumps(init)))
dst = root / "tools/plate-mapper.html"
dst.write_text(out)
print("built", dst, f"{dst.stat().st_size/1e6:.2f} MB")
