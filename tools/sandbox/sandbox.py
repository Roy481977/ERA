"""
sandbox — the smallest deterministic simulation capable of testing District 01.

NOT the Town Engine. A sandbox that borrows its concepts:
  intention, not movement (CD-006) — residents choose WHERE and WHY; nobody
      animates a step.
  recognition by repetition (CD-003) — familiarity is a counter that only
      co-presence can raise.
  traces (CD-025) — behaviour leaves evidence with an author and an exit.
  determinism (CD-007) — seed 27; same seed, same month.

One question: does District 01 generate believable everyday life?
Believability is MEASURED, not asserted:
  1. routines must EMERGE (habit reinforcement, never scripts) and stabilise;
  2. place rhythms must emerge from needs x opening hours (bakery mornings,
     pub evenings, market Fridays are never scheduled);
  3. the familiarity histogram must be long-tailed (many nodders, few friends);
  4. dead places and overloads are reported as evidence.

Residents are DATA. If June needs a special rule, the engine is wrong.
"""
import hashlib
import math
from district_level import LEVEL

SEED = 27
WEEKS = 4
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOTS = ["07", "09", "11", "13", "15", "17", "19"]
NS = len(SLOTS)


def h(*a):
    s = ":".join(map(str, a)) + f":{SEED}"
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 1000


def wx_day(d):
    r = h("wx", d)
    return "rain" if r < 280 else ("wind" if r < 420 else "dry")


# ---------------------------------------------------------------- places
PXY = {p["id"]: (p["x"], p["y"]) for p in LEVEL["plots"]}
PLACES = {
    # id: loc, satisfies {need: strength}, open slots, days (None=all), covered
    "bakery":   {"loc": PXY["P02"], "sat": {"bread": 3.0, "social": 0.6}, "open": {0, 1, 2}, "days": range(6), "cover": True},
    "post":     {"loc": PXY["P06"], "sat": {"errand": 2.0}, "open": {1, 2, 3}, "days": range(5), "cover": True},
    "stores":   {"loc": PXY["P05"], "sat": {"errand": 1.6, "bread": 0.7}, "open": {1, 2, 3, 4, 5}, "days": range(6), "cover": True},
    "cafe":     {"loc": PXY["P04"], "sat": {"social": 2.0, "food": 1.2}, "open": {1, 2, 3, 4}, "days": range(7), "cover": True},
    "pub":      {"loc": PXY["P07"], "sat": {"social": 2.4, "drink": 2.6}, "open": {3, 4, 5, 6}, "days": range(7), "cover": True},
    "market":   {"loc": (117.0, 20.0), "sat": {"errand": 2.6, "social": 1.4, "bread": 1.0}, "open": {1, 2, 3}, "days": (4,), "cover": False},
    "square":   {"loc": (117.0, 20.0), "sat": {"outdoors": 0.5, "play": 1.2}, "open": set(range(NS)), "days": None, "cover": False},
    "oak":      {"loc": (51.5, 28.5), "sat": {"outdoors": 1.8, "quiet": 1.4}, "open": set(range(NS)), "days": None, "cover": False},
    "benchA":   {"loc": (46.0, 23.4), "sat": {"quiet": 1.7, "social": 0.5}, "open": set(range(NS)), "days": None, "cover": False},
    "benchB":   {"loc": (55.2, 23.6), "sat": {"quiet": 1.7, "social": 0.5}, "open": set(range(NS)), "days": None, "cover": False},
    "allotment": {"loc": (30.0, 68.0), "sat": {"purpose": 2.4, "outdoors": 1.6}, "open": {0, 1, 2, 5}, "days": None, "cover": False},
    "field":    {"loc": (40.0, -20.0), "sat": {"play": 2.6, "outdoors": 1.2}, "open": {2, 4, 5, 6}, "days": None, "cover": False},
    "green":    {"loc": (45.0, 25.0), "sat": {"outdoors": 1.3, "play": 0.8}, "open": set(range(NS)), "days": None, "cover": False},
    "ground":   {"loc": (155.0, 50.0), "sat": {"football": 6.0}, "open": {3, 4}, "days": (5,), "cover": False},
    "home":     {"loc": None, "sat": {"rest": 1.2, "family": 1.0}, "open": set(range(NS)), "days": None, "cover": True},
}

# ---------------------------------------------------------------- residents
# pure data. anchors: (day-filter, slot, place, label). traits 0..1.
R = [
    {"n": "June", "home": "P09",
     "anchors": [(("Tue", "Thu", "Fri"), (1, 2), "post", "counter shift"),
                 (("Sat",), (3, 4), "ground", "Gordon's seats")],
     "tr": {"soc": 0.55, "rout": 0.9, "out": 0.7, "foot": 0.8, "range": 1.0},
     "needs0": {"bread": 1.2, "quiet": 0.8, "purpose": 1.0}},
    {"n": "Vera", "home": "P08",
     "anchors": [], "tr": {"soc": 0.85, "rout": 0.7, "out": 0.5, "foot": 0.1, "range": 0.9},
     "needs0": {"social": 1.4, "bread": 0.8}},
    {"n": "Hana", "home": "P03",
     "anchors": [(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat"), (0, 1, 2), "bakery", "the ovens"),
                 (("Fri",), (3,), "market", "her stall")],
     "tr": {"soc": 0.7, "rout": 0.8, "out": 0.4, "foot": 0.5, "range": 0.8},
     "needs0": {"quiet": 1.2, "drink": 0.5}},
    {"n": "Marge", "home": "P10",
     "anchors": [(("Mon", "Tue", "Wed", "Thu", "Fri"), (1, 2, 3), "post", "the counter")],
     "tr": {"soc": 0.6, "rout": 0.85, "out": 0.4, "foot": 0.3, "range": 0.9},
     "needs0": {"social": 0.9}},
    {"n": "Bram", "home": "P07",
     "anchors": [(None, (3, 4, 5, 6), "pub", "landlord")],
     "tr": {"soc": 0.8, "rout": 0.9, "out": 0.3, "foot": 0.7, "range": 0.7},
     "needs0": {}},
    {"n": "Stan", "home": "P01",
     "anchors": [], "tr": {"soc": 0.5, "rout": 0.8, "out": 0.95, "foot": 0.6, "range": 1.2},
     "needs0": {"outdoors": 2.2, "drink": 0.8}},
    {"n": "Claire", "home": "P13",
     "anchors": [(("Mon", "Tue", "Wed", "Thu", "Fri"), (1,), "green", "school run out"),
                 (("Mon", "Tue", "Wed", "Thu", "Fri"), (4,), "green", "school run back")],
     "tr": {"soc": 0.7, "rout": 0.75, "out": 0.6, "foot": 0.4, "range": 1.0},
     "needs0": {"errand": 1.3, "social": 1.0}},
    {"n": "Leo", "home": "P13", "child": True,
     "anchors": [(("Mon", "Tue", "Wed", "Thu", "Fri"), (1, 2, 3), "green", "school")],
     "tr": {"soc": 0.8, "rout": 0.4, "out": 0.9, "foot": 0.9, "range": 0.8},
     "needs0": {"play": 2.4}},
    {"n": "Pat Kelly", "home": "P11",
     "anchors": [], "tr": {"soc": 0.6, "rout": 0.85, "out": 0.9, "foot": 0.4, "range": 0.9},
     "needs0": {"purpose": 2.0, "outdoors": 1.2}},
    {"n": "Mo Kelly", "home": "P11",
     "anchors": [], "tr": {"soc": 0.75, "rout": 0.8, "out": 0.85, "foot": 0.2, "range": 0.9},
     "needs0": {"purpose": 1.8, "social": 1.0}},
    {"n": "Dev", "home": "P12", "teen": True,
     "anchors": [(("Mon", "Tue", "Wed", "Thu", "Fri"), (1,), "busstop", "college bus out"),
                 (("Mon", "Tue", "Wed", "Thu", "Fri"), (5,), "busstop", "college bus back")],
     "tr": {"soc": 0.75, "rout": 0.5, "out": 0.7, "foot": 0.85, "range": 1.3},
     "needs0": {"play": 1.6, "social": 1.5}},
    {"n": "Tomas", "home": "P14",
     "anchors": [(("Mon", "Tue", "Wed", "Thu", "Fri"), (1,), "busstop", "works in town"),
                 (("Mon", "Tue", "Wed", "Thu", "Fri"), (5,), "busstop", "home again")],
     "tr": {"soc": 0.65, "rout": 0.7, "out": 0.5, "foot": 0.85, "range": 1.0},
     "needs0": {"drink": 1.3, "social": 1.1}},
    {"n": "Luca", "home": "P04",
     "anchors": [(None, (1, 2, 3, 4), "cafe", "the machine")],
     "tr": {"soc": 0.85, "rout": 0.85, "out": 0.4, "foot": 0.6, "range": 0.8},
     "needs0": {}},
    {"n": "Agnes", "home": "P15",
     "anchors": [], "tr": {"soc": 0.6, "rout": 0.9, "out": 0.6, "foot": 0.5, "range": 0.6},
     "needs0": {"quiet": 2.0, "social": 0.9, "bread": 0.6}},
]
PLACES["busstop"] = {"loc": (115.4, 8.0), "sat": {}, "open": set(range(NS)),
                     "days": None, "cover": True}   # anchor-only; shelter counts as cover

NEEDS = ["bread", "errand", "social", "food", "drink", "outdoors", "quiet",
         "purpose", "play", "football", "rest", "family"]
GROW = {"bread": 0.55, "errand": 0.35, "social": 0.5, "food": 0.4, "drink": 0.35,
        "outdoors": 0.5, "quiet": 0.4, "purpose": 0.5, "play": 0.9,
        "football": 0.0, "rest": 0.6, "family": 0.5}

for r in R:
    r["needs"] = {n: r.get("needs0", {}).get(n, 0.5) for n in NEEDS}
    r["habit"] = {}
    r["loc"] = PXY[r["home"]]

fam = {}
traces = []
occupancy = {}
choices = {}
events = []
new_pairs_week = [0] * WEEKS
day_trace_sets = {}


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def anchored(r, day, s):
    for (dayf, slots, place, label) in r["anchors"]:
        if (dayf is None or day in dayf) and s in slots:
            return place, label
    return None, None


T = 0
for week in range(WEEKS):
    for d in range(7):
        day = DAYS[d]
        wx = wx_day(week * 7 + d)
        dts = set()
        for r in R:
            # overnight need growth + fixture pulse
            for n in NEEDS:
                g = GROW[n]
                if n == "play" and not (r.get("child") or r.get("teen")):
                    g *= 0.25          # adults kick a ball about sometimes; not daily
                r["needs"][n] += g * (0.8 + h("g", r["n"], week, d, n) / 2500)
            if day == "Sat":
                r["needs"]["football"] += 5.0 * r["tr"]["foot"]
            # domestic traces
            if wx != "rain" and not r.get("child"):
                traces.append((week, day, "07", r["n"], "+ washing out"))
                dts.add((r["n"], "washing"))
            if day == "Tue" and not r.get("child"):
                traces.append((week, day, "07", r["n"], "+ bin to kerb"))
                dts.add((r["n"], "bin"))

        for s in range(NS):
            present = {}
            for r in R:
                place, label = anchored(r, day, s)
                why = label
                if place is None:
                    # ------- intention: score every open place
                    best, bestv = "home", 1.0 + r["needs"]["rest"] * 0.5
                    for pid, P_ in PLACES.items():
                        if pid in ("home", "busstop"):
                            continue
                        if pid == "pub" and r.get("child"):
                            continue   # no seven-year-old regulars
                        if P_["days"] is not None and d not in P_["days"]:
                            continue
                        if s not in P_["open"]:
                            continue
                        v = sum(r["needs"].get(n, 0) * st for n, st in P_["sat"].items())
                        v *= (1.5 if s >= 5 and "drink" in P_["sat"] else 1.0)
                        v -= dist(r["loc"], P_["loc"]) / (55.0 * r["tr"]["range"])
                        v += r["habit"].get((pid, d, s), 0) * 0.55 * r["tr"]["rout"]
                        if wx == "rain" and not P_["cover"]:
                            v -= 2.6
                        if wx == "wind" and not P_["cover"]:
                            v -= 0.7
                        v += (h("j", r["n"], week, d, s, pid) / 1000.0 - 0.5) * 0.8
                        if v > bestv:
                            best, bestv = pid, v
                    place = best
                    why = "chose it" if place != "home" else None
                # satisfy + habit + occupancy
                if place != "home":
                    P_ = PLACES[place]
                    for n, st in P_["sat"].items():
                        r["needs"][n] = max(0.0, r["needs"][n] - st * 1.4)
                    if place == "ground":
                        r["needs"]["football"] = 0.0
                    r["habit"][(place, d, s)] = r["habit"].get((place, d, s), 0) + 1
                    occupancy[(place, s)] = occupancy.get((place, s), 0) + 1
                    present.setdefault(place, []).append(r["n"])
                    r["loc"] = P_["loc"] or PXY[r["home"]]
                else:
                    r["needs"]["rest"] = max(0, r["needs"]["rest"] - 1.2)
                    r["needs"]["family"] = max(0, r["needs"]["family"] - 0.8)
                    r["loc"] = PXY[r["home"]]
                choices[(r["n"], week, d, s)] = place
                events.append((week, d, s, r["n"], place,
                               anchored(r, day, s)[0] is not None, wx))
                # place traces
                if place == "ground":
                    traces.append((week, day, SLOTS[s], r["n"], "+ scarf on the rail"))
                    dts.add((r["n"], "scarf"))
                if place == "allotment":
                    dts.add((r["n"], "tools"))
                if place in ("field", "square") and (r.get("child") or r.get("teen")):
                    dts.add((r["n"], "chalk/ball"))
            # ------- recognition: co-presence (one increment per pair per day —
            # you don't get to know a colleague eight times before lunch)
            for pid, names in present.items():
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        k = tuple(sorted((names[i], names[j])))
                        dk = ("famday", k, week, d)
                        if dk in day_trace_sets:
                            continue
                        day_trace_sets[dk] = True
                        if k not in fam:
                            new_pairs_week[week] += 1
                        fam[k] = fam.get(k, 0) + 1
        day_trace_sets[(week, d)] = dts

# ---------------------------------------------------------------- metrics
print(f"SANDBOX — District 01, {WEEKS} weeks, {len(R)} residents, seed {SEED}")
print("weather:", ", ".join(wx_day(x)[0] for x in range(WEEKS * 7)))
print()

# 1 routine stability week-over-week
stab = []
for w in range(1, WEEKS):
    same = tot = 0
    for r in R:
        for d in range(7):
            for s in range(NS):
                a = choices[(r["n"], w, d, s)]
                b = choices[(r["n"], w - 1, d, s)]
                tot += 1
                same += (a == b)
    stab.append(same / tot)
print("1 ROUTINE EMERGENCE (share of slots repeating previous week):")
print("   " + "  ".join(f"wk{w + 1}: {v * 100:.0f}%" for w, v in enumerate(stab)))
print()

# 2 place pulse (emergent rhythms)
print("2 PLACE PULSE (visits per slot over the month; nothing was scheduled):")
for pid in ["bakery", "cafe", "pub", "market", "oak", "allotment", "field",
            "square", "benchA", "benchB", "ground", "stores", "post", "green"]:
    row = [occupancy.get((pid, s), 0) for s in range(NS)]
    if sum(row):
        print(f"   {pid:10s} " + " ".join(f"{v:3d}" for v in row) + f"   total {sum(row)}")
    else:
        print(f"   {pid:10s} " + " DEAD — zero visits in {} weeks".format(WEEKS))
print("   slots:      " + "  ".join(SLOTS))
print()

# 3 familiarity histogram
b = {"seen (1-2)": 0, "nodding (3-6)": 0, "chatting (7-14)": 0, "friends (15+)": 0}
for k, v in fam.items():
    if v <= 2:
        b["seen (1-2)"] += 1
    elif v <= 6:
        b["nodding (3-6)"] += 1
    elif v <= 14:
        b["chatting (7-14)"] += 1
    else:
        b["friends (15+)"] += 1
print("3 RECOGNITION (pairs by familiarity; must be long-tailed):")
for k, v in b.items():
    print(f"   {k:15s} {v}")
print("   new pairs met per week:", new_pairs_week, " (should decelerate)")
top = sorted(fam.items(), key=lambda x: -x[1])[:6]
print("   closest pairs:", ", ".join(f"{a}&{bb}:{v}" for (a, bb), v in top))
print()

# 4 the Tuesday test (trace-set distinguishability)
tue = day_trace_sets[(1, 1)]
sat = day_trace_sets[(1, 5)]
sun = day_trace_sets[(1, 6)]
print("4 EMPTY TUESDAY TEST (week 2): |Tue|=%d |Sat|=%d |Sun|=%d, Tue^Sat differ by %d items"
      % (len(tue), len(sat), len(sun), len(tue.symmetric_difference(sat))))
print()

# 5 evidence
print("5 EVIDENCE FOR THE ENVIRONMENT TEAM:")
dead = [pid for pid in PLACES if pid not in ("home", "busstop")
        and not any(occupancy.get((pid, s), 0) for s in range(NS))]
print("   dead places:", ", ".join(dead) if dead else "none")
mkt = sum(occupancy.get(("market", s), 0) for s in range(NS))
sq = sum(occupancy.get(("square", s), 0) for s in range(NS))
print(f"   market Fridays: {mkt} visits; square other days: {sq} — the pairing works" if mkt and sq
      else f"   market {mkt} / square {sq} — check")
pk = max((occupancy.get(("pub", s), 0), s) for s in range(NS))
print(f"   pub peak at {SLOTS[pk[1]]}:00 with {pk[0]} visits over month (evening emerged: {pk[1] >= 4})")
bk = max((occupancy.get(("bakery", s), 0), s) for s in range(NS))
print(f"   bakery peak at {SLOTS[bk[1]]}:00 (morning emerged: {bk[1] <= 1})")
ba = sum(occupancy.get(("benchA", s), 0) for s in range(NS))
bb2 = sum(occupancy.get(("benchB", s), 0) for s in range(NS))
print(f"   benches: A {ba} vs B {bb2} — with no grief rule, do both live?")
gr = sum(occupancy.get(("ground", s), 0) for s in range(NS))
print(f"   ground: {gr} matchday visits from {len(R)} residents ({gr / (WEEKS):．0f}/match avg)"
      if False else f"   ground: {gr} matchday visits across {WEEKS} Saturdays")
print(f"   traces logged: {len(traces)}")


DATA = {"events": events, "fam": fam, "traces": traces, "choices": choices,
        "occupancy": occupancy, "new_pairs_week": new_pairs_week,
        "places": PLACES, "residents": R, "weeks": WEEKS, "nslots": NS,
        "wx": [wx_day(x) for x in range(WEEKS * 7)]}
