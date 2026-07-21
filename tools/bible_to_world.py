#!/usr/bin/env python3
"""ERA blockout step 1 — map bible-pixel coords -> plate WORLD units.

LOCKED transform (retune constants here). The plate is 1800x1000 world units
(1 wu = 0.25 m => 450 x 250 m). The composition bible (1024x1024 px) is the
RIGHT HALF of the plate width; off-frame places live in the LEFT extension.
Single uniform linear scale so drawn curves are preserved (the bible is AI
concept art with no known camera; true perspective is re-established later by
the NEW locked plate camera, per CD-008 — see the interpretation flag in the
session status doc).

  world_x_wu = 900 + px * (900/1024)     # px 0..1024  -> x 900..1800 wu
  world_y_wu = 100 + py * (900/1024)     # py 0..1024  -> y 100..1000 wu
  (equivalently  x_m = 225 + px*225/1024 ,  y_m = 25 + py*225/1024 ; wu = m*4)
"""
import json

M_PER_WU = 0.25
PLATE_WU = [1800, 1000]
SX = SY = 900/1024                 # wu per px (uniform)
OX, OY = 900, 100                  # bible top-left -> world (right half)

def wu(px, py):
    return [round(OX + px*SX, 2), round(OY + py*SY, 2)]
def wupath(pts):
    return [wu(x, y) for x, y in pts]

nav = json.load(open('design/bible/nav-graph.json'))
ann = json.load(open('design/bible/annotations.json'))

out = {
  "space": "plate world units (wu); 1 wu = 0.25 m; plate 1800x1000 wu = 450x250 m",
  "transform": {"m_per_wu": M_PER_WU, "wu_per_px": round(SX, 6),
                "origin_wu": [OX, OY], "note": "bible = right half of plate; uniform linear map"},
  "nav_paths": [{"id": p["id"], "type": p["type"], "pts": wupath(p["pts"])} for p in nav["paths"]],
  "connectors": [{"id": c["id"], "type": "door", "place": c.get("place"), "pts": wupath(c["pts"])}
                 for c in nav.get("connectors", [])],
  "dressing_paths": [{"id": p["id"], "type": p["type"],
                      "pts": wupath(p["pts"]) if "pts" in p else None,
                      "circle": (lambda c: {"c": wu(c["cx"], c["cy"]),
                                            "rx": round(c["rx"]*SX,2), "ry": round(c["ry"]*SY,2)})(p["circle"])
                                 if "circle" in p else None} for p in ann["paths"]],
  "crossings": [{"id": x["id"], "on": x["on"], "world": wu(*x["px"])} for x in ann["crossings"]],
  "places": [{"n": pl["n"], "name": pl["name"], "role": pl.get("role"),
              "world": wu(*pl["px"])} for pl in ann["places"]],
}

# off-frame (LEFT extension, x < 900 wu) — PROVISIONAL, retune in step 3
OFF = {
  "loc_training_ground": {"world": [180, 300], "note": "far-left & back, behind the station (pitch+pavilion)"},
  "loc_school":          {"world": [430, 240], "note": "left extension, back band"},
  "loc_weavers_lane":    {"world": [470, 720], "note": "left extension, mid/low"},
  "loc_orchard_close":   {"world": [1660, 260], "note": "behind NE terraces (right side)"},
  "loc_canal_side":      {"world": [1650, 520], "note": "canal spur off the river (right side)"},
}
out["off_frame"] = OFF

# sim_bindings: 22 sim loc ids -> a world coord (direct input to the Rust sim)
by_n = {pl["n"]: wu(*pl["px"]) for pl in ann["places"]}
ring = next(p for p in ann["paths"] if p["id"] == "square_ring")["circle"]
hs = next(p for p in ann["paths"] if p["id"] == "high_street")["pts"]
out["sim_bindings"] = {
  "loc_stadium":       by_n[19], "loc_museum":     by_n[5],  "loc_bakery":   by_n[4],
  "loc_main_square":   wu(ring["cx"], ring["cy"]),           "loc_cafe":     by_n[2],
  "loc_pub":           by_n[3],  "loc_bridge":     by_n[18], "loc_riverside":by_n[17],
  "loc_millers_row":   by_n[14], "loc_high_street":wu(*hs[len(hs)//2]),
  "loc_oakside":       by_n[12], "loc_elm_row":    by_n[16], "loc_kiln_yard":by_n[15],
  "loc_north_gate":    by_n[11], "loc_club_offices":by_n[6], "loc_club_shop":by_n[7],
  "loc_corner_grocer": by_n[10],
  "loc_school":        OFF["loc_school"]["world"],
  "loc_weavers_lane":  OFF["loc_weavers_lane"]["world"],
  "loc_orchard_close": OFF["loc_orchard_close"]["world"],
  "loc_canal_side":    OFF["loc_canal_side"]["world"],
  "loc_training_ground": OFF["loc_training_ground"]["world"],
}
# reconciliation flags for step 2
out["reconcile"] = [
  "bible #11 North Gate = the GROUND PLAZA, but sim loc_north_gate is currently a residential HOME.",
  "bible #3 pub = 'The Turnstile Arms', but current sim name is 'The Anchor'.",
  "off_frame + loc_main_square/high_street coords are PROVISIONAL — retune when the plate camera is locked (step 3)."
]
json.dump(out, open('design/bible/world-coords.json', 'w'), indent=1)
print("wrote design/bible/world-coords.json")
print("  nav_paths:", len(out["nav_paths"]), "connectors:", len(out["connectors"]),
      "places:", len(out["places"]), "sim_bindings:", len(out["sim_bindings"]))
# sanity: every bible place inside plate bounds
bad = [pl["name"] for pl in out["places"] if not (900<=pl["world"][0]<=1800 and 100<=pl["world"][1]<=1000)]
print("  out-of-bounds places:", bad or "none")
