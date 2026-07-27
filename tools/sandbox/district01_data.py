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
