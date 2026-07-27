"""
district_level — DISTRICT 01, Build v1. THE LEVEL DATA.

This file is the layout. The plan drawing is derived from it, never the
other way round. Coordinates in metres; x east, y north; one worldspace,
continuous with `district01.py`. Canon: CD-024..027. No creative decisions
are made here — only construction.

Camera-validation adjustments baked in and flagged:
  ADJ-1  bridge moved 2.0 m south — parapet now visible from the pub corner
         (restores the S2-family sightline on the matchday route).
  ADJ-2  bus shelter shifted 1.5 m west — no longer blocks S3
         (bus stop -> pub sign, the visitor's first orientation).
  ADJ-3  market bollard line aligned with the stall bay edge — the road's
         end now reads as a threshold, not an accident.
  ADJ-4  green's north path connected through to the backdrop lane — every
         worn path now has a destination (no dead desire lines).
"""

LEVEL = {
    "meta": {
        "id": "district01",
        "version": "build-v1",
        "canon": ["CD-024", "CD-025", "CD-026", "CD-027"],
        "composition": "The Weave — daily line W-E, weekly line S-NE, crossing at the Oak",
        "extent": (-20.0, -34.0, 192.0, 84.0),      # x0, y0, x1, y1
    },

    # ------------------------------------------------------------- terrain
    "terrain": {
        "base": "grass",
        "playing_field": (-16.0, -32.0, 96.0, -14.0),
        "allotments": (2.0, 58.0, 78.0, 80.0),
        "ground_apron": (132.0, 42.0, 192.0, 84.0),  # towards the stadium
    },

    # water: centreline polyline + width
    "water": {"pts": [(141.5, -10.0), (139.5, 4.0), (142.0, 30.0),
                      (140.0, 56.0), (142.5, 84.0)], "w": 4.4},

    # ------------------------------------------------------------- roads
    # axis-aligned carriageway segments (module RD-01/02), 5.8 m wide
    "roads": [
        {"id": "west-lane",   "x0": -20.0, "y0": 15.0, "x1": 36.0,  "y1": 21.5},
        {"id": "high-street", "x0": 64.0,  "y0": 15.0, "x1": 108.0, "y1": 21.5},
        {"id": "green-south", "x0": 36.0,  "y0": 15.0, "x1": 64.0,  "y1": 21.5},
        {"id": "south-link-w", "x0": -14.0, "y0": -12.0, "x1": -8.0, "y1": 15.0},
        {"id": "south-loop",  "x0": -14.0, "y0": -18.0, "x1": 122.0, "y1": -12.0},
        {"id": "south-link-e", "x0": 116.0, "y0": -12.0, "x1": 122.0, "y1": 15.0},
        {"id": "north-lane",  "x0": -6.0,  "y0": 40.5,  "x1": 40.0,  "y1": 44.5},
    ],
    "zebra": [{"id": "school-crossing", "x": 30.0, "roadseg": "west-lane",
               "beacons": [(27.6, 14.2), (32.4, 22.3)]}],

    # ------------------------------------------------------------- paths
    "paths": [
        {"id": "pave-w-n",  "kind": "flags", "x0": -20.0, "y0": 21.5, "x1": 10.0, "y1": 26.0},
        {"id": "bakery-sq", "kind": "flags", "x0": 10.0,  "y0": 21.5, "x1": 36.0, "y1": 30.0},
        {"id": "pave-w-s",  "kind": "flags", "x0": -20.0, "y0": 11.0, "x1": 108.0, "y1": 15.0},
        {"id": "hs-walk",   "kind": "brick", "x0": 64.0,  "y0": 21.5, "x1": 102.0, "y1": 30.0},
        {"id": "market-sq", "kind": "brick", "x0": 108.0, "y0": 11.0, "x1": 131.0, "y1": 30.0},
        {"id": "north-path", "kind": "flags", "x0": -6.0, "y0": 44.5, "x1": 40.0, "y1": 46.5},
        {"id": "worn-sq-oak",   "kind": "worn", "pts": [(40.0, 21.5), (50.0, 28.0)]},
        {"id": "worn-oak-hs",   "kind": "worn", "pts": [(53.5, 29.0), (64.0, 24.0)]},
        {"id": "worn-oak-north", "kind": "worn", "pts": [(51.5, 31.5), (52.0, 44.5)]},  # ADJ-4
        {"id": "worn-stadium-1", "kind": "worn", "pts": [(128.0, 26.0), (138.0, 30.0)]},
        {"id": "worn-stadium-2", "kind": "worn", "pts": [(142.5, 32.0), (152.0, 46.0)]},
        {"id": "worn-field",    "kind": "worn", "pts": [(30.0, 11.0), (34.0, -14.0)]},
    ],

    # ------------------------------------------------------------- plots
    # every building is BLD-A (hero core + annex) + a kit; rot always 0
    # (fronts face south — camera law); accents from the accent set
    "plots": [
        {"id": "P01", "kit": "home",   "accent": "GRN", "x": 2.0,   "y": 30.0, "traces": 6},
        {"id": "P02", "kit": "bakery", "accent": "MUS", "x": 16.0,  "y": 30.0, "traces": 5},
        {"id": "P03", "kit": "home",   "accent": "RED", "x": 27.5,  "y": 30.6, "traces": 6},
        {"id": "P04", "kit": "cafe",   "accent": "ORG", "x": 66.0,  "y": 30.0, "traces": 5},
        {"id": "P05", "kit": "stores", "accent": "NVY", "x": 78.0,  "y": 30.5, "traces": 4},
        {"id": "P06", "kit": "post",   "accent": "RED", "x": 90.5,  "y": 30.0, "traces": 4},
        {"id": "P07", "kit": "pub",    "accent": "GRN", "x": 119.0, "y": 30.0, "traces": 6},
        {"id": "P08", "kit": "home",   "accent": "OLV", "x": 2.0,   "y": 46.5, "traces": 6},
        {"id": "P09", "kit": "home",   "accent": "TEAL", "x": 15.0, "y": 47.3, "traces": 6},
        {"id": "P10", "kit": "home",   "accent": "PNK", "x": 27.5,  "y": 46.5, "traces": 6},
        {"id": "P11", "kit": "home",   "accent": "NVY", "x": 8.0,   "y": -1.5, "traces": 6},
        {"id": "P12", "kit": "home",   "accent": "TEAL", "x": 22.0, "y": -2.3, "traces": 6},
        {"id": "P13", "kit": "home",   "accent": "OLV", "x": 52.0,  "y": -1.5, "traces": 6},
        {"id": "P14", "kit": "home",   "accent": "MUS", "x": 66.0,  "y": -2.3, "traces": 6},
        {"id": "P15", "kit": "home",   "accent": "GRN", "x": 96.0,  "y": -1.5, "traces": 6},
    ],

    # ------------------------------------------------------------- landmarks
    "landmarks": {
        "oak":       {"x": 51.5, "y": 28.5, "s": 1.35, "unique": True},
        "board":     {"x": 37.5, "y": 20.0},
        "bridge":    {"x": 137.4, "y": 27.2, "w": 5.8, "note": "ADJ-1 (was y 29.2)"},
        "stand":     {"x0": 142.0, "y": 50.0, "w": 26.0, "h": 5.6},
        "turnstiles": [(146.0, 47.6), (159.0, 47.6)],
        "floodlights": [(152.0, 55.5), (164.0, 55.5), (146.0, 76.0), (170.0, 74.0)],
    },

    # ------------------------------------------------------------- furniture
    "furniture": [
        {"m": "ST-01 shelter", "x": 107.5, "y": 8.2, "note": "ADJ-2 (was 109.0)"},
        {"m": "ST-01 flag",    "x": 115.4, "y": 8.0},
        {"m": "ST-04 bench",   "x": 46.0,  "y": 23.4},
        {"m": "ST-04 bench",   "x": 55.2,  "y": 23.6},
        {"m": "ST-04 bench",   "x": 109.6, "y": 8.6},
        {"m": "ST-07 pillar",  "x": 104.5, "y": 13.2},
        {"m": "ST-05 bollard", "x": 108.5, "y": 16.5, "note": "ADJ-3"},
        {"m": "ST-05 bollard", "x": 108.5, "y": 20.5, "note": "ADJ-3"},
        {"m": "ST-02 lamp",    "x": 40.0,  "y": 13.6},
        {"m": "ST-02 lamp",    "x": 88.0,  "y": 13.6},
        {"m": "ST-02 lamp",    "x": 128.5, "y": 12.4},
        {"m": "ST-02 lamp",    "x": 8.0,   "y": 13.6},
        {"m": "ST-06 bin",     "x": 12.5,  "y": 22.6},
        {"m": "ST-06 bin",     "x": 118.0, "y": 8.4},
        {"m": "ST-08 planter", "x": 66.5,  "y": 22.6},
        {"m": "ST-08 planter", "x": 97.0,  "y": 22.6},
        {"m": "ST-11 rail x3", "x": 131.0, "y": 28.6},
        {"m": "ST-10 hedge",   "x": 128.0, "y": 23.2},
    ],

    "veg": [
        {"m": "VEG-01 tree", "x": 70.0, "y": 7.0}, {"m": "VEG-01 tree", "x": 94.0, "y": 6.2},
        {"m": "VEG-01 tree", "x": 45.0, "y": 41.0}, {"m": "VEG-01 tree", "x": 136.0, "y": 13.0},
        {"m": "VEG-01 tree", "x": -12.0, "y": 24.0}, {"m": "VEG-01 tree", "x": 40.0, "y": -10.0},
        {"m": "VEG-02 shrub", "x": 24.0, "y": 8.2}, {"m": "VEG-02 shrub", "x": 148.5, "y": 12.0},
    ],

    # market stalls are SIM state, not layout: bay marked only
    "stall_bay": (109.0, 16.0, 126.0, 26.0),
}


# quick structural checks (run at import; a level that lies is worse than none)
def _validate():
    x0, y0, x1, y1 = LEVEL["meta"]["extent"]
    for p in LEVEL["plots"]:
        assert x0 <= p["x"] <= x1 - 10.5 and y0 <= p["y"] <= y1, p["id"]
    ids = [p["id"] for p in LEVEL["plots"]]
    assert len(ids) == len(set(ids)), "duplicate plot ids"
    assert sum(p["traces"] for p in LEVEL["plots"]) >= 60, "trace anchor budget"


_validate()
