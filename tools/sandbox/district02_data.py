"""
district02_data — the Phase 6 proof: a second district authored ENTIRELY
as data. Not a real district yet — a deliberately small sketch (the
riverside quarter: a chandlery instead of a bakery, a boatyard instead
of an allotment, a slipway green, one pub, a chapel bench) that the
engine runs with ZERO new simulation code.

If this file simulates, Phase 6's success criterion holds.
"""

_LOC = {"Q01": (10, 10), "Q02": (18, 10), "Q03": (26, 12), "Q04": (34, 10),
        "Q05": (42, 12), "Q06": (50, 10), "Q07": (58, 12), "Q08": (66, 10)}

DISTRICT = {
    "id": "district02",
    "name": "District 02 — the Riverside (data sketch)",
    "seed": 41,
    "weeks": 8,
    "plots": list(_LOC),
    "plot_loc": _LOC,

    "places": {
        "chandlery": {"loc": (22.0, 18.0), "provides": {"bread": 2.6, "errand": 1.8,
                                                        "conversation": 0.7},
                      "open": {0, 1, 2, 3}, "days": range(6), "cover": True,
                      "closes_holidays": True, "operator": "chandlery_biz"},
        "boatyard":  {"loc": (60.0, 22.0), "provides": {"purpose": 2.5, "outdoors": 1.5,
                                                        "repair": 2.2},
                      "open": {0, 1, 2, 5}, "cover": False, "quiet": True,
                      "season_profile": "garden", "operator": "boat_club"},
        "slipway":   {"loc": (40.0, 20.0), "provides": {"outdoors": 1.6, "play": 1.8},
                      "cover": False, "season_profile": "open_air"},
        "ferry_inn": {"loc": (30.0, 14.0), "provides": {"conversation": 2.2, "drink": 2.5,
                                                        "food": 1.0, "cheer": 1.1,
                                                        "celebration": 1.4},
                      "open": {3, 4, 5, 6}, "cover": True, "adults_only": True,
                      "operator": "inn_biz"},
        "chapel_bench": {"loc": (48.0, 16.0), "provides": {"quiet": 1.8,
                                                           "conversation": 0.4},
                         "cover": False, "quiet": True, "season_profile": "open_air"},
        "jetty":     {"loc": (36.0, 24.0), "provides": {}, "cover": False},
    },

    "name_pool": ["Ada", "Frank", "Meg", "Tom", "Sula", "Bert", "Iris",
                  "Cal", "Nora", "Pip", "Edie", "Gus", "Wren", "Olly",
                  "Fern", "Hal"],
    "occ_pool": ["chandler", "keeper", "keeper2", "boatwright", "commuter",
                 "commuter", "retired"],
    "household_sizes": [2, 2, 2, 3, 2, 2, 2, 1],
    "core_population": 16,
    "child_occ": "school",
    "household_items": ["rope fender", "tar bucket", "long ladder"],
    "newcomers": [],
    "canon": {},

    "occupations": {
        "chandler":   {"institution": "chandlery_biz", "income": 85,
                       "shifts": [(range(6), (0, 1, 2), "chandlery")]},
        "keeper":     {"institution": "inn_biz", "income": 85,
                       "shifts": [(None, (3, 4, 5, 6), "ferry_inn")]},
        "keeper2":    {"institution": "inn_biz", "income": 60,
                       "shifts": [(range(7), (5, 6), "ferry_inn")]},
        "boatwright": {"institution": "boat_club", "income": 90,
                       "shifts": [(range(6), (1, 2, 3), "boatyard")]},
        "commuter":   {"institution": None, "income": 120,
                       "shifts": [(range(5), (1,), "jetty"), (range(5), (5,), "jetty")]},
        "school":     {"institution": None, "income": 0, "term_bound": True,
                       "shifts": [(range(5), (1, 2, 3), "slipway")]},
        "retired":    {"institution": None, "income": 70, "shifts": []},
    },

    "institutions": {
        "chandlery_biz": {"name": "the chandlery", "kind": "business",
                          "places": ["chandlery"]},
        "inn_biz":       {"name": "the Ferry Inn", "kind": "business",
                          "places": ["ferry_inn"]},
        "boat_club":     {"name": "the boat club", "kind": "association",
                          "places": ["boatyard"],
                          "auto_member": {"place": "boatyard", "uses": 25}},
    },

    "football": None,           # the riverside has no club — and needs no code for that

    "event_rates": {"illness": 5200, "pressure": 3000, "household": 4500,
                    "borrow": 4200, "argument": 2800, "invitation": 3600},
    "retirement_age": 60,
    "retirement_day": None,

    "ambience": {"baseline": "the same town, nearer the water"},
}
