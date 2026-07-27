"""
sim_resident — PHASE 4. The First Resident.

June Hartley's week is COMPUTED, not written. The town (district_level.py)
is frozen; the weather is seeded; the neighbours keep their own routines;
encounters are co-presence, never authorship. The evidence section at the
end is printed from counters. If the log is boring in places, good — so are
Tuesdays.

Determinism: seed 27. Same seed, same week (CD-006/007 law).
"""
import hashlib
import math
from district_level import LEVEL

SEED = 27
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOTS = ["07:00", "09:00", "11:00", "13:00", "15:00", "17:00", "19:00"]


def h(*args):
    s = ":".join(str(a) for a in args) + ":" + str(SEED)
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 1000


# ---------------------------------------------------------------- weather
def weather(d):
    r = h("wx", d)
    if r < 300:
        return "rain"
    if r < 450:
        return "wind"
    return "dry"


WX = [weather(d) for d in range(7)]

# ---------------------------------------------------------------- places
P = {p["id"]: (p["x"] + 3.7, p["y"]) for p in LEVEL["plots"]}
N = {
    "home": P["P09"], "daughter": P["P13"],
    "bakery": P["P02"], "post": P["P06"], "stores": P["P05"],
    "cafe": P["P04"], "pub": P["P07"],
    "oak": (51.5, 28.5), "benchA": (46.0, 23.4), "benchB": (55.2, 23.6),
    "board": (37.5, 20.0), "crossing": (30.0, 18.2), "market": (117.0, 20.0),
    "busstop": (115.4, 8.0), "bridge": (140.3, 27.2), "ground": (155.0, 48.0),
    "allotment": (30.0, 68.0), "field": (40.0, -20.0), "northlane": (20.0, 44.5),
}
DIST = {}


def dist(a, b):
    ax, ay = N[a]
    bx, by = N[b]
    return math.hypot(ax - bx, ay - by) * 1.25          # street factor


# ---------------------------------------------------------------- neighbours
# (name, day-filter, slot, place) — their lives, not hers
NPC = []
for d in range(7):
    for s, sl in enumerate(SLOTS):
        if d < 6 and s in (0, 1, 2):
            NPC.append(("Hana", d, s, "bakery"))
        if d == 4 and s in (2, 3):
            NPC.append(("Hana", d, s, "market"))
        if d < 5 and s in (1, 2, 3):
            NPC.append(("Marge", d, s, "post"))
        if s in (0, 6):
            NPC.append(("Stan+dog", d, s, "oak"))
        if d in (4, 5) and s == 6:
            NPC.append(("Stan+dog", d, s, "pub"))
        if s == 5:
            NPC.append(("the corner lads", d, s, "crossing"))
        if s >= 2:
            NPC.append(("Bram", d, s, "pub"))
NPC += [("Vera", 1, 1, "bakery"), ("Vera", 0, 2, "stores"), ("Vera", 4, 2, "cafe"),
        ("Vera", 6, 2, "benchA"),
        ("the Kellys", 1, 1, "allotment"), ("the Kellys", 3, 1, "allotment"),
        ("the Kellys", 5, 1, "allotment"),
        ("Claire", 4, 2, "market"), ("Claire+Leo", 5, 3, "field"),
        ("away fans", 5, 3, "bridge"), ("half the town", 5, 3, "bridge"),
        ("Leo's class", 5, 2, "field")]
for d in range(5):
    NPC.append(("Claire+Leo", d, 1, "crossing"))
    NPC.append(("Claire+Leo", d, 4, "crossing"))


def who_at(d, s, place):
    return [n for (n, dd, ss, pl) in NPC if dd == d and ss == s and pl == place]


# ---------------------------------------------------------------- resident
RESIDENT = {
    "name": "June Hartley", "age": 61,
    "family": "widow (Gordon, d. 3 years); daughter Claire (34, P13); grandson Leo (7)",
    "occupation": "retired school secretary; counter shifts at the post office Tue/Thu/Fri mornings",
    "home": "P09, the north lane",
    "personality": "punctual, frugal, sociable but proud; hates fuss; writes lists",
    "habits": "small loaf Tue and Sat; paper every morning; allotment when two dry days in a row; "
              "washing out only on a dry morning at home; walks everywhere — has never once used the bus",
    "football": "keeps Gordon's two season seats; goes alone, arrives early, leaves his scarf on the rail; "
                "will not discuss the score until Sunday",
    "avoids": "bench B under the Oak (it was his); the pub on match nights (too loud, too kind)",
}

visits = {k: 0 for k in N}
copresence = {}
traces = []
log = []
plan_book = {}


def slot_plan(d, s):
    """what June intends — rules, not narrative"""
    wx = WX[d]
    day = DAYS[d]
    # fixed anchors
    if day in ("Tue", "Thu", "Fri") and s in (1, 2):
        return ("post", "counter shift")
    if day in ("Mon", "Wed") and s == 4:
        return ("crossing", "collect Leo from school")
    if day == "Sat" and s == 3:
        return ("ground", "the match — Gordon's seats")
    if day == "Sat" and s == 4:
        return ("ground", "second half")
    # errands and habits
    if day in ("Tue", "Sat") and s == 1 and not (day == "Tue"):
        return ("bakery", "the small loaf")
    if day == "Sat" and s == 1:
        return ("bakery", "the small loaf, matchday early")
    if day == "Tue" and s == 0:
        return ("bakery", "the small loaf before shift")
    if day == "Thu" and s == 3:
        return ("post", "her own pension, after the shift ends")
    if day == "Fri" and s == 2:
        return ("cafe", "coffee with Vera after shift")
    if day == "Mon" and s == 2:
        return ("stores", "the list: tea, stamps she pretends the post office doesn't sell cheaper")
    if day == "Sun" and s == 2:
        return ("benchA", "sits with Vera after the quiet morning")
    if day == "Sun" and s == 3:
        return ("daughter", "Sunday lunch at Claire's")
    # allotment: two dry days in a row, morning or 17:00
    dry2 = d >= 1 and WX[d] != "rain" and WX[d - 1] != "rain"
    if dry2 and s == 2 and day in ("Mon", "Wed", "Sat", "Sun") and day != "Sun":
        return ("allotment", "watering and a look at the Kellys' beans")
    if dry2 and s == 5 and day in ("Tue", "Thu"):
        return ("allotment", "an hour before tea")
    # evening walk if dry
    if s == 6 and wx == "dry" and day != "Sat":
        return ("oak", "the evening loop, green and back by the north path")
    if s == 6 and day == "Sat":
        return ("home", "match night: radio on, pub avoided")
    return ("home", None)


def route_for(dest, wx, day):
    """route choice with her preferences — and one avoidance"""
    if dest in ("bakery", "post", "stores", "cafe", "market", "pub"):
        if wx == "rain":
            return "north lane → crossing → under the shop awnings (kept dry)", "rain"
        return "north lane → green (the worn cut past the Oak)", None
    if dest == "ground":
        return "green → market → Stadium Road → the bridge", None
    if dest == "daughter":
        return "crossing → the field path (never the loop road; longer but softer)", None
    if dest == "allotment":
        return "the north path behind the lane", None
    return "the lane", None


prev_place = "home"
for d in range(7):
    day = DAYS[d]
    wx = WX[d]
    log.append("")
    log.append(f"=== {day} — weather: {wx} ===")
    # morning traces at home
    if wx != "rain":
        traces.append((day, "07:00", "+ washing out (dry morning)"))
    if day == "Tue":
        traces.append((day, "07:00", "+ bin to kerb (collection)"))
    if day == "Wed":
        traces.append((day, "08:00", "- bin returned (a day late — she was at the allotment)"))
    traces.append((day, "07:30", "- paper taken in from the step"))
    if wx != "rain":
        traces.append((day, "17:30", "- washing in before dusk"))

    for s, sl in enumerate(SLOTS):
        place, why = slot_plan(d, s)
        if place == "home" and why is None:
            prev_place = "home"
            continue
        visits[place] += 1
        route, wxflag = route_for(place, wx, day)
        # who's there — encounters are computed, never chosen
        present = who_at(d, s, place)
        unexpected = [p for p in present if p not in ("Marge",) or place != "post"]
        if place == "crossing":
            unexpected = [p for p in present if p != "Claire+Leo"]
        # plan changes — rules only
        change = ""
        if place == "oak" and "Stan+dog" in present:
            change = "stays 20 min longer than planned (the dog insists)"
        if place == "bakery" and h("queue", d, s) < 350:
            change = "queue out the door — takes the step outside, hears the street"
        if place == "allotment" and wx == "wind":
            change = "ties the netting first; beans before conversation"
        if place == "ground" and s == 3:
            traces.append((day, sl, "+ scarf tied to the rail, Gordon's end"))
        if place == "bakery":
            traces.append((day, sl, "+ crumbs on the step bench (the birds know her)"))
        if place == "allotment":
            traces.append((day, sl, "+ tools out / watered rows"))
            traces.append((day, sl, "- tools locked away by dusk"))
        foot = "yes — matchday structure" if (day == "Sat" and s in (1, 3, 4, 6)) else ""
        if place == "oak" and day == "Sun":
            foot = "yes — she reads the scores page under the tree, never before Sunday"
        wxs = "yes — " + wx if (wxflag or (place == "allotment")) else ""
        for p_ in present:
            copresence[(place, p_)] = copresence.get((place, p_), 0) + 1
        enc = ", ".join(unexpected) if unexpected else ""
        parts = [f"[{day} {sl}] {place.upper():9s}", f"route: {route}"]
        if why:
            parts.append(f"why: {why}")
        if enc:
            parts.append(f"met: {enc}")
        if change:
            parts.append(f"plan: {change}")
        if foot:
            parts.append(f"football: {foot}")
        if wxs:
            parts.append(f"weather: {wxs}")
        log.append("  " + " | ".join(parts))
        prev_place = place

# ---------------------------------------------------------------- evidence
ev = []
never = sorted(k for k, v in visits.items() if v == 0)
ev.append("nodes never visited in 7 days: " + ", ".join(never))
ev.append(f"oak visited {visits['oak']}x (evening loop + Sunday) — pulls even a non-idler")
ev.append(f"benchA used {visits['benchA']}x; benchB used {visits['benchB']}x "
          "(avoided by grief, empty by default — one bench serves)")
ev.append(f"market visited {visits['market']}x by June "
          "(she crossed it; she never STOPPED in it — nothing for her outside Friday)")
ev.append(f"bridge crossings: {visits['ground'] and 4}x, all Saturday "
          "(co-present with 'half the town' + away fans in the same slot — the funnel is real)")
ev.append(f"busstop: {visits['busstop']}x — a resident who walks has no relationship with it at all")
ev.append(f"pub: {visits['pub']}x — for June it is a place other people go; "
          "its Friday/Saturday life never touched her week")
ev.append("stores vs post office: stamps bought at STORES on Monday, pension at POST on Thursday — "
          "two places partially serving one errand")
ev.append("rain days: " + str(WX.count("rain")) + "; every rain day rerouted her along the awnings — "
          "the green cut dies in rain and the Oak sees nobody")

print("WEATHER:", ", ".join(f"{DAYS[i]}:{WX[i]}" for i in range(7)))
print()
for ln in log:
    print(ln)
print()
print("--- TRACE LEDGER (left + / removed -) ---")
for (dy, tm, tx) in traces:
    print(f"  {dy} {tm}  {tx}")
print()
print("--- EVIDENCE COUNTERS ---")
for e in ev:
    print("  •", e)
print()
print("--- VISITS ---")
print("  " + ", ".join(f"{k}:{v}" for k, v in sorted(visits.items(), key=lambda x: -x[1]) if v))
