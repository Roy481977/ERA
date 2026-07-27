"""
district01_data — DISTRICT 01 as pure data. No behaviour lives here.

Everything the world engine needs to simulate this district: physical
layout (reused from district_level.LEVEL — the Build v1 level data),
places as capability bundles, households, occupations, institutions,
the football club's world, ambience, and the canon residents.

The test of Phase 6: district02_data.py is authored the same way, and
the engine cannot tell the difference.
"""
from district_level import LEVEL

_PXY = {p["id"]: (p["x"], p["y"]) for p in LEVEL["plots"]}

DISTRICT = {
    "id": "district01",
    "name": "District 01 — the Heart",
    "seed": 27,
    "weeks": 52,
    "level": LEVEL,                       # physical layout: Build v1 data
    "plots": [p["id"] for p in LEVEL["plots"]],
    "plot_loc": _PXY,

    # ---------------------------------------------------------- places
    # capabilities only; identity is what the historian finds afterwards
    "places": {
        "bakery":   {"loc": _PXY["P02"], "provides": {"bread": 3.0, "conversation": 0.6},
                     "open": {0, 1, 2}, "days": range(6), "cover": True,
                     "closes_holidays": True, "operator": "bakery_biz"},
        "post":     {"loc": _PXY["P06"], "provides": {"errand": 2.0},
                     "open": {1, 2, 3}, "days": range(5), "cover": True,
                     "closes_holidays": True, "operator": "post_office"},
        "stores":   {"loc": _PXY["P05"], "provides": {"errand": 1.7, "bread": 0.7, "repair": 3.0},
                     "open": {1, 2, 3, 4, 5}, "days": range(6), "cover": True,
                     "closes_holidays": True, "operator": "stores_shop"},
        "cafe":     {"loc": _PXY["P04"], "provides": {"conversation": 2.0, "food": 1.2},
                     "open": {1, 2, 3, 4}, "days": range(7), "cover": True,
                     "closes_holidays": True, "operator": "cafe_biz"},
        "pub":      {"loc": _PXY["P07"], "provides": {"conversation": 2.3, "drink": 2.6,
                                                      "cheer": 1.2, "celebration": 1.5},
                     "open": {3, 4, 5, 6}, "days": range(7), "cover": True,
                     "adults_only": True, "operator": "pub_biz"},
        "market":   {"loc": (117.0, 20.0), "provides": {"errand": 2.6, "conversation": 1.4, "bread": 1.0},
                     "open": {1, 2, 3}, "days": (4,), "cover": False,
                     "closes_holidays": True},
        "square":   {"loc": (117.0, 20.0), "provides": {"outdoors": 0.5, "play": 1.1},
                     "cover": False, "season_profile": "open_air"},
        "oak":      {"loc": (51.5, 28.5), "provides": {"outdoors": 1.7, "quiet": 1.5},
                     "cover": False, "quiet": True, "season_profile": "open_air",
                     "operator": "council"},
        "benchA":   {"loc": (46.0, 23.4), "provides": {"quiet": 1.7, "conversation": 0.5},
                     "cover": False, "quiet": True, "season_profile": "open_air",
                     "operator": "council"},
        "benchB":   {"loc": (55.2, 23.6), "provides": {"quiet": 1.7, "conversation": 0.5},
                     "cover": False, "quiet": True, "season_profile": "open_air",
                     "operator": "council"},
        "allotment": {"loc": (30.0, 68.0), "provides": {"purpose": 2.4, "outdoors": 1.6},
                      "open": {0, 1, 2, 5}, "cover": False, "quiet": True,
                      "season_profile": "garden", "operator": "allot_soc"},
        "field":    {"loc": (40.0, -20.0), "provides": {"play": 2.6, "outdoors": 1.2},
                     "open": {2, 4, 5, 6}, "cover": False, "season_profile": "open_air"},
        "green":    {"loc": (45.0, 25.0), "provides": {"outdoors": 1.3, "play": 0.8},
                     "cover": False, "operator": "council"},
        "ground":   {"loc": (155.0, 50.0), "provides": {"football": 6.0},
                     "open": {3, 4}, "days": (5,), "cover": False,
                     "matchday_only": True, "operator": "afc"},
        "ground_work": {"loc": (155.0, 50.0), "provides": {}, "cover": False,
                        "quiet": True, "public": False, "operator": "afc"},
        "busstop":  {"loc": (115.4, 8.0), "provides": {}, "cover": True},
    },

    # ---------------------------------------------------------- people
    "name_pool": ["June", "Vera", "Hana", "Marge", "Bram", "Stan", "Claire",
                  "Leo", "Pat", "Mo", "Dev", "Tomas", "Luca", "Agnes", "Bill",
                  "Rosa", "Colin", "Priya", "Ted", "Nell", "Sam", "Iris",
                  "Gwen", "Arthur", "Faye", "Ron", "Dot", "Ken", "Lily",
                  "Owen", "Beth", "Carl", "Enid", "Vik", "Mabel", "Joe",
                  "Wyn", "Sal", "Reg"],
    "occ_pool": ["baker", "baker2", "post", "post2", "cafe", "cafe2", "pub",
                 "pub2", "stores", "stores2", "commuter", "commuter",
                 "commuter", "commuter", "commuter", "commuter", "groundsman",
                 "teacher", "teacher", "retired"],
    "household_sizes": [3, 3, 2, 2, 4, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2],
    "core_population": 39,
    "child_occ": "school",
    "household_items": ["ladder", "big pan", "hedge shears"],

    "newcomers": [
        {"n": "Petra", "age": 34, "hh": 99, "home": "P10", "occ": "commuter",
         "arrives": 35,
         "tr": {"soc": 0.7, "rout": 0.6, "out": 0.6, "foot": 0.3,
                "temper": 0.3, "duty": 0.6, "range": 1.1},
         "poss": ["bike"]},
        {"n": "Jack", "age": 58, "hh": 98, "home": "P15", "occ": "retired",
         "arrives": 190,
         "tr": {"soc": 0.55, "rout": 0.7, "out": 0.5, "foot": 0.65,
                "temper": 0.25, "duty": 0.5, "range": 0.9},
         "poss": []},
        # the player's body — one more resident; the engine cannot tell.
        # human input, when present, replaces only this row's free choices.
        {"n": "Roy", "age": 47, "hh": 97, "home": "P12", "occ": "newcomer",
         "arrives": 7,
         "tr": {"soc": 0.6, "rout": 0.5, "out": 0.6, "foot": 0.7,
                "temper": 0.2, "duty": 0.5, "range": 1.0},
         "poss": []},
    ],

    # canon residents — data rows, zero special-case behaviour
    "canon": {
        "June": {"age": 61, "hh": 90, "occ": "post2", "home": "P09",
                 "commitments": [((5,), (3, 4), "ground")],
                 "tr_patch": {"foot": 0.8, "rout": 0.9, "temper": 0.14},
                 "poss": ["season ticket"]},
        "Hana": {"age": 44, "occ": "baker", "tr_patch": {}, "poss": []},
    },

    # ------------------------------------------------------- occupations
    # shifts: (day filter or None, slots, place). Institutions employ.
    "occupations": {
        "baker":     {"institution": "bakery_biz", "income": 90,
                      "shifts": [(range(6), (0, 1, 2), "bakery")]},
        "baker2":    {"institution": "bakery_biz", "income": 70,
                      "shifts": [(range(6), (1, 2), "bakery")]},
        "post":      {"institution": "post_office", "income": 90,
                      "shifts": [(range(5), (1, 2, 3), "post")]},
        "post2":     {"institution": "post_office", "income": 60,
                      "shifts": [((1, 3, 4), (1, 2), "post")]},
        "cafe":      {"institution": "cafe_biz", "income": 85,
                      "shifts": [(None, (1, 2, 3, 4), "cafe")]},
        "cafe2":     {"institution": "cafe_biz", "income": 60,
                      "shifts": [(range(7), (2, 3), "cafe")]},
        "pub":       {"institution": "pub_biz", "income": 90,
                      "shifts": [(None, (3, 4, 5, 6), "pub")]},
        "pub2":      {"institution": "pub_biz", "income": 60,
                      "shifts": [(range(7), (5, 6), "pub")]},
        "stores":    {"institution": "stores_shop", "income": 85,
                      "shifts": [(range(6), (1, 2, 3, 4), "stores")]},
        "stores2":   {"institution": "stores_shop", "income": 60,
                      "shifts": [(range(6), (3, 4, 5), "stores")]},
        "commuter":  {"institution": None, "income": 130,
                      "shifts": [(range(5), (1,), "busstop"), (range(5), (5,), "busstop")]},
        "groundsman": {"institution": "afc", "income": 75,
                       "shifts": [(range(5), (1, 2), "ground_work")]},
        "teacher":   {"institution": "school", "income": 100, "term_bound": True,
                      "shifts": [(range(5), (1, 2, 3), "green")]},
        "school":    {"institution": "school", "income": 0, "term_bound": True,
                      "pupil": True,
                      "shifts": [(range(5), (1, 2, 3), "green")]},
        "retired":   {"institution": None, "income": 70, "shifts": []},
        "newcomer":  {"institution": None, "income": 80, "shifts": []},
    },

    # ------------------------------------------------------ institutions
    "institutions": {
        "afc":         {"name": "the football club", "kind": "football_club",
                        "places": ["ground", "ground_work"]},
        "school":      {"name": "the school", "kind": "school", "places": ["green"]},
        "bakery_biz":  {"name": "the bakery", "kind": "business", "places": ["bakery"]},
        "post_office": {"name": "the post office", "kind": "business", "places": ["post"]},
        "stores_shop": {"name": "the stores", "kind": "business", "places": ["stores"]},
        "cafe_biz":    {"name": "the café", "kind": "business", "places": ["cafe"]},
        "pub_biz":     {"name": "the pub", "kind": "business", "places": ["pub"]},
        "allot_soc":   {"name": "the allotment society", "kind": "association",
                        "places": ["allotment"],
                        "auto_member": {"place": "allotment", "uses": 190}},
        "council":     {"name": "the parish council", "kind": "civic",
                        "places": ["oak", "green", "benchA", "benchB", "square"]},
    },

    # --------------------------------------------------------- football
    "football": {
        "club": "Athletic",
        "league": ["Harborough", "Millbrook", "Netherton", "Kings Weald",
                   "Ashcombe", "Dunmore", "Ravensfield", "St Edmunds",
                   "Oxcroft", "Longbridge", "Fenwick", "Marsh End", "Weyford"],
        "squad": ["Doyle", "Okafor", "Prentice", "Small", "Kaminski",
                  "Batty", "Hughes", "O'Rourke", "Sisay", "Mercer",
                  "Trent", "Nowak", "Gill", "Bakewell"],
        "fixture_dow": 5,
    },

    # life-event weekly rates (of 10000) — the district's temperament
    "event_rates": {"illness": 5200, "pressure": 3300, "household": 4500,
                    "borrow": 4000, "argument": 3000, "invitation": 3800},
    "retirement_age": 58,
    "retirement_day": 217,

    "ambience": {"baseline": "modern English village, 1970s–80s",
                 "canon": ["CD-024", "CD-025", "CD-026", "CD-027"]},
}

# ------------------------------------------------------------------
# PHASE 12 — SPATIAL REVISION (ADJ-6..12, PROPOSED, pending Roy).
# Meaning is canon; coordinates are not. Two south-row households move
# to face Market Street as a short terrace (ADJ-7) — the street gains
# its second side, the Loop keeps three outer homes. BenchB moves under
# the oak (the quiet seat; benchA keeps watching the street).
REV = {
    "plots": {"P14": (72.0, 9.0), "P15": (88.0, 9.0)},
    "benchB": (56.5, 27.6),
}
for _pid, _xy in REV["plots"].items():
    DISTRICT["plot_loc"][_pid] = list(_xy)
DISTRICT["places"]["benchB"]["loc"] = tuple(REV["benchB"])
DISTRICT["rev"] = REV

# ------------------------------------------------------------------
# REV2 — THE VILLAGE PLAN (Continuous Creative Direction, PROPOSED).
# The prototype plan is replaced, not optimised. Language untouched;
# composition redrawn: a continuous shop-and-terrace wall on the south
# side of Market Street, the green opened into a three-sided room with
# homes facing it (June's window looks down the green to the oak), the
# square walled by the pub, the post office clock as the vertical accent.
REV2 = {
    "plots": {
        # the south street wall: shops and terrace, fronts on the pavement
        "P02": (34.0, 11.6),   # bakery at the school corner (zebra beside it)
        "P05": (46.0, 11.6),   # stores
        "P04": (56.0, 11.6),   # cafe, facing the green across the street
        "P06": (68.0, 11.6),   # post office — carries the clock
        "P14": (80.0, 11.4),   # terrace
        "P13": (90.0, 11.4),   # terrace
        "P15": (100.0, 11.4),  # terrace end — Jack stays 30 m from the pub
        # the green's shoulders on the north side
        "P01": (26.0, 25.4),   # Hana's cottage at the green's west shoulder
        "P03": (70.0, 25.4),   # the east shoulder cottage
        # North Lane homes face south into the green
        "P08": (38.0, 49.5),
        "P09": (48.0, 50.3),   # June — her window looks down the green
        "P10": (58.0, 49.5),
        # the pub walls the square
        "P07": (114.0, 26.5),
        # P11, P12 keep the quiet School Lane fringe
    },
    "places": {
        "green":  (48.0, 31.0),
        "oak":    (48.0, 32.5),
        "benchA": (42.0, 24.6),   # the watching seat, at the green's mouth
        "benchB": (50.5, 33.8),   # the quiet seat, under the oak
    },
    "oak_lm": (48.0, 32.0),
    "roads": {
        "high-street": (64.0, 15.0, 112.0, 21.5),   # reaches the square
        "north-lane":  (26.0, 42.5, 66.0, 46.5),    # fronts the green
    },
    "new_roads": [
        {"id": "green-west", "x0": 30.0, "y0": 21.5, "x1": 34.0, "y1": 42.5},
    ],
    "paths": {
        "bakery-sq":  (10.0, 21.5, 30.0, 24.5),
        "pave-w-s":   (-20.0, 11.0, 112.0, 15.0),
        "hs-walk":    (64.0, 21.5, 112.0, 25.5),
        "north-path": (26.0, 46.5, 66.0, 48.5),
    },
    "worn": {
        "worn-sq-oak":    [(42.0, 22.0), (48.0, 31.0)],
        "worn-oak-hs":    [(52.0, 33.0), (62.0, 23.0)],
        "worn-oak-north": [(48.0, 34.0), (48.0, 46.5)],
    },
}
for _pid, _xy in REV2["plots"].items():
    DISTRICT["plot_loc"][_pid] = list(_xy)
for _pl, _xy in REV2["places"].items():
    DISTRICT["places"][_pl]["loc"] = tuple(_xy)
for _shop, _plot in (("bakery", "P02"), ("stores", "P05"), ("cafe", "P04"),
                     ("post", "P06"), ("pub", "P07")):
    DISTRICT["places"][_shop]["loc"] = tuple(DISTRICT["plot_loc"][_plot])
_LV = DISTRICT["level"]
_LV["landmarks"]["oak"]["x"], _LV["landmarks"]["oak"]["y"] = REV2["oak_lm"]
for _r in _LV["roads"]:
    if _r["id"] in REV2["roads"]:
        _r["x0"], _r["y0"], _r["x1"], _r["y1"] = REV2["roads"][_r["id"]]
for _nr in REV2["new_roads"]:
    if not any(r["id"] == _nr["id"] for r in _LV["roads"]):
        _LV["roads"].append(dict(_nr))
for _p in _LV["paths"]:
    if _p["id"] in REV2["paths"]:
        _p["x0"], _p["y0"], _p["x1"], _p["y1"] = REV2["paths"][_p["id"]]
    if _p["id"] in REV2["worn"]:
        _p["pts"] = [tuple(q) for q in REV2["worn"][_p["id"]]]
for _f in _LV["furniture"]:
    if _f["m"] == "ST-04 bench" and abs(_f["x"] - 46.0) < 1:
        _f["x"], _f["y"] = 42.0, 24.6
    elif _f["m"] == "ST-04 bench" and abs(_f["x"] - 55.2) < 1:
        _f["x"], _f["y"] = 50.5, 33.8
DISTRICT["rev2"] = REV2
