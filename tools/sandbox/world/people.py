"""
world.people — residents, relationships, memory, intentions.

Residents are generated FROM DISTRICT DATA (name pool, occupation pool,
household sizes, canon rows) by a generic recipe. No resident has code;
June Hartley is a data row supplied by her district.

Relationship records carry event ledgers and first meetings; place memory
carries warmth, soreness and associations. Intentions target CAPABILITIES
or people — never place identities.
"""
from collections import defaultdict, deque

# the shared human model — WORLD-level defaults, overridable per world
NEEDS = ["bread", "errand", "conversation", "food", "drink", "outdoors",
         "quiet", "purpose", "play", "football", "rest", "family", "cheer",
         "repair"]
GROW = {"bread": 0.55, "errand": 0.32, "conversation": 0.5, "food": 0.4,
        "drink": 0.32, "outdoors": 0.5, "quiet": 0.4, "purpose": 0.45,
        "play": 0.9, "football": 0.0, "rest": 0.6, "family": 0.5,
        "cheer": 0.0, "repair": 0.0}


def make_population(rng, dd, ndays):
    """dd = the district data dict"""
    h, f = rng.h, rng.f
    res = []
    names = list(dd["name_pool"])
    occs = list(dd["occ_pool"])
    ni = 0
    for hi, (plot, size) in enumerate(zip(dd["plots"], dd["household_sizes"])):
        adults = min(size, 2)
        for a in range(adults):
            nm = names[ni]; ni += 1
            occ = occs.pop(h("occ", nm) % len(occs)) if occs else "retired"
            age = 28 + h("age", nm) % 45
            if occ == "retired":
                age = 60 + h("age", nm) % 20
            res.append({
                "n": nm, "age": age, "hh": hi, "home": plot, "occ": occ,
                "tr": {"soc": 0.3 + f("soc", nm) * 0.6,
                       "rout": 0.4 + f("rt", nm) * 0.55,
                       "out": 0.2 + f("ot", nm) * 0.7,
                       "foot": f("ft", nm),
                       "temper": f("tp", nm) * 0.8,
                       "duty": 0.3 + f("dt", nm) * 0.6,
                       "range": 0.7 + f("rg", nm) * 0.6},
                "poss": (["bike"] if f("bk", nm) > 0.5 else []) +
                        (["season ticket"] if f("st", nm) < 0.35 else []),
            })
        for k in range(size - adults):
            nm = names[ni]; ni += 1
            res.append({
                "n": nm, "age": 6 + h("age", nm) % 10, "hh": hi, "home": plot,
                "occ": dd.get("child_occ", "school"), "child": True,
                "tr": {"soc": 0.6 + f("soc", nm) * 0.3, "rout": 0.35,
                       "out": 0.7 + f("ot", nm) * 0.25,
                       "foot": 0.5 + f("ft", nm) * 0.5,
                       "temper": f("tp", nm) * 0.5, "duty": 0.2, "range": 0.8},
                "poss": ["ball"] if f("bl", nm) > 0.4 else [],
            })
        if ni >= dd.get("core_population", len(names)):
            break
    for nc in dd.get("newcomers", []):
        res.append(dict(nc))
    # canon rows — data overrides, zero special-case behaviour
    canon = dd.get("canon", {})
    displaced = []
    for r in res:
        c = canon.get(r["n"])
        if c:
            if "occ" in c and r["occ"] not in ("retired", c["occ"]):
                displaced.append(r["occ"])       # the job returns to the town
            for k, v in c.items():
                if k == "tr_patch":
                    r["tr"].update(v)
                else:
                    r[k] = v
            if r.get("age", 0) >= 18:
                r.pop("child", None)
    # displaced occupations are taken up by fallback retirees (deterministic)
    if displaced:
        takers = [r for r in res if r["occ"] == "retired" and not r.get("child")
                  and not r.get("arrives") and r["age"] < 70
                  and r["n"] not in canon]
        for occ in displaced:
            if takers:
                t = takers.pop()
                t["occ"] = occ
    for r in res:
        r["needs"] = {n: 0.5 for n in NEEDS}
        r["habit"] = {}
        r["rel"] = {}
        r["pmem"] = {}
        r["intents"] = []
        r["exp"] = deque(maxlen=12)
        r["log"] = []
        r["ill_until"] = -1
        r["pressure_until"] = -1
        r["bday"] = h("bd", r["n"]) % ndays
    return res


def rel(r, other):
    if other not in r["rel"]:
        r["rel"][other] = {"rec": 0, "comfort": 0.0, "affection": 0.0,
                           "irritation": 0.0, "trust": 0.0, "obligation": 0.0,
                           "last": -99, "tension": 0, "met": None, "ev": []}
    return r["rel"][other]


def pmem(r, p):
    if p not in r["pmem"]:
        r["pmem"][p] = {"uses": 0, "last": -99, "assoc": defaultdict(int),
                        "warm": 0, "sore_until": -1}
    return r["pmem"][p]


def add_intent(r, kind, target, prio, day, deadline, note=""):
    """target is a CAPABILITY (buy/repair/prep) or a person (visit/return/
    celebrate) — never a place identity."""
    for it in r["intents"]:
        if it["kind"] == kind and it["target"] == target and it["state"] == "open":
            it["prio"] = max(it["prio"], prio)
            return
    r["intents"].append({"kind": kind, "target": target, "prio": prio,
                         "born": day, "deadline": deadline, "state": "open",
                         "note": note})
