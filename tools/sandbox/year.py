"""
year — PHASE 5: the First Living Town.

One in-game year on the Phase 4 stack. No new frameworks: the additions are
persistence, and every one of them makes tomorrow different because today
happened.

New over living.py:
  calendar        Aug -> Jul. Seasons drive weather, daylight and the
                  allotment. School terms and half-terms. Public holidays
                  close the shops and fill the homes. ERA's competition is
                  a fantasy calendar: a fixture EVERY weekend, all year —
                  home and away alternating. The weekly heartbeat never
                  stops; the seasons change around it.
  first meetings  every pair remembers where and when it began.
  event ledgers   relationships carry their history (borrowed, argued,
                  made peace, matches watched together) as events, not
                  only as numbers.
  social pull     residents drift toward places where the people they
                  like will probably be — friendships bend routines.
  retirement      one working life ends mid-year; the routine that grows
                  into the gap is the simulation's answer, not ours.
  two newcomers   Petra (Sep, commuter) and Jack (Feb, retired) — the
                  district integrates them at its own two speeds.

Residents remain data. June and Hana are canon rows, not code.
Determinism: seed 27 end to end. Run: 42 residents, 52 weeks.
"""
import hashlib
import math
from collections import defaultdict, deque
from district_level import LEVEL

SEED = 27
WEEKS = 52
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOTS = ["07", "09", "11", "13", "15", "17", "19"]
NS = len(SLOTS)
NDAYS = WEEKS * 7                      # 364 days, Mon 1 Aug .. Sun 30 Jul


def h(*a):
    s = ":".join(map(str, a)) + f":{SEED}"
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10000


def hf(*a):
    return h(*a) / 10000.0


# ---------------------------------------------------------------- calendar
MNAME = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan",
         "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
MLEN = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31]
MSTART = []
_acc = 0
for _l in MLEN:
    MSTART.append(_acc)
    _acc += _l


def month_of(day):
    for i in range(11, -1, -1):
        if day >= MSTART[i]:
            return i
    return 0


def date_str(day):
    mi = month_of(day)
    return f"{DAYS[day % 7]} {day - MSTART[mi] + 1} {MNAME[mi]}"


def season_of(day):
    mi = month_of(day)
    if mi in (0, 10, 11):
        return "summer"
    if mi in (1, 2, 3):
        return "autumn"
    if mi in (4, 5, 6):
        return "winter"
    return "spring"


# public holidays (day % 7 == 0 is a Monday)
def _last_monday(mi):
    end = MSTART[mi] + MLEN[mi] - 1
    return end - (end % 7)


HOLIDAYS = {
    _last_monday(0),                    # summer bank holiday (Aug)
    MSTART[4] + 24, MSTART[4] + 25,     # Christmas Day, Boxing Day
    MSTART[5], MSTART[5] + 1,           # New Year's Day + the Monday
    MSTART[8] + 6, MSTART[8] + 9,       # Good Friday, Easter Monday
    MSTART[9],                          # May Day (1 May is a Monday)
    _last_monday(9),                    # spring bank holiday
}
CHRISTMAS = MSTART[4] + 24

_TERM_BREAKS = [
    (0, 34),                            # summer holidays until Sep term
    (84, 90),                           # autumn half-term (late Oct)
    (MSTART[4] + 17, MSTART[5] + 1),    # Christmas break
    (196, 202),                         # spring half-term (mid Feb)
    (245, 258),                         # Easter fortnight
    (_last_monday(9), _last_monday(9) + 6),   # summer half-term
    (355, NDAYS),                       # summer holidays again
]


def school_holiday(day):
    return any(a <= day <= b for a, b in _TERM_BREAKS)


def wx_day(day):
    sn = season_of(day)
    r = h("wx", day)
    rain = {"summer": 1700, "autumn": 3100, "winter": 3400, "spring": 2600}[sn]
    wind = rain + {"summer": 900, "autumn": 1700, "winter": 2000, "spring": 1500}[sn]
    return "rain" if r < rain else ("wind" if r < wind else "dry")


# ---------------------------------------------------------------- places
PXY = {p["id"]: (p["x"], p["y"]) for p in LEVEL["plots"]}
PLACES = {
    "bakery":   {"loc": PXY["P02"], "sat": {"bread": 3.0, "social": 0.6}, "open": {0, 1, 2}, "days": range(6), "cover": True, "quiet": False},
    "post":     {"loc": PXY["P06"], "sat": {"errand": 2.0}, "open": {1, 2, 3}, "days": range(5), "cover": True, "quiet": False},
    "stores":   {"loc": PXY["P05"], "sat": {"errand": 1.7, "bread": 0.7, "repair": 3.0}, "open": {1, 2, 3, 4, 5}, "days": range(6), "cover": True, "quiet": False},
    "cafe":     {"loc": PXY["P04"], "sat": {"social": 2.0, "food": 1.2}, "open": {1, 2, 3, 4}, "days": range(7), "cover": True, "quiet": False},
    "pub":      {"loc": PXY["P07"], "sat": {"social": 2.3, "drink": 2.6, "cheer": 1.2}, "open": {3, 4, 5, 6}, "days": range(7), "cover": True, "quiet": False},
    "market":   {"loc": (117.0, 20.0), "sat": {"errand": 2.6, "social": 1.4, "bread": 1.0}, "open": {1, 2, 3}, "days": (4,), "cover": False, "quiet": False},
    "square":   {"loc": (117.0, 20.0), "sat": {"outdoors": 0.5, "play": 1.1}, "open": set(range(NS)), "days": None, "cover": False, "quiet": False},
    "oak":      {"loc": (51.5, 28.5), "sat": {"outdoors": 1.7, "quiet": 1.5}, "open": set(range(NS)), "days": None, "cover": False, "quiet": True},
    "benchA":   {"loc": (46.0, 23.4), "sat": {"quiet": 1.7, "social": 0.5}, "open": set(range(NS)), "days": None, "cover": False, "quiet": True},
    "benchB":   {"loc": (55.2, 23.6), "sat": {"quiet": 1.7, "social": 0.5}, "open": set(range(NS)), "days": None, "cover": False, "quiet": True},
    "allotment": {"loc": (30.0, 68.0), "sat": {"purpose": 2.4, "outdoors": 1.6}, "open": {0, 1, 2, 5}, "days": None, "cover": False, "quiet": True},
    "field":    {"loc": (40.0, -20.0), "sat": {"play": 2.6, "outdoors": 1.2}, "open": {2, 4, 5, 6}, "days": None, "cover": False, "quiet": False},
    "green":    {"loc": (45.0, 25.0), "sat": {"outdoors": 1.3, "play": 0.8}, "open": set(range(NS)), "days": None, "cover": False, "quiet": False},
    "ground":   {"loc": (155.0, 50.0), "sat": {"football": 6.0}, "open": {3, 4}, "days": (5,), "cover": False, "quiet": False},
    "busstop":  {"loc": (115.4, 8.0), "sat": {}, "open": set(range(NS)), "days": None, "cover": True, "quiet": False},
    "home":     {"loc": None, "sat": {"rest": 1.2, "family": 1.0}, "open": set(range(NS)), "days": None, "cover": True, "quiet": True},
}
SHOPS = ("bakery", "post", "stores", "market", "cafe")


def smul(pid, day):
    """the seasons reach the places themselves"""
    sn = season_of(day)
    if pid == "allotment":
        return {"spring": 1.35, "summer": 1.15, "autumn": 0.8, "winter": 0.25}[sn]
    if pid in ("field", "green", "square", "oak", "benchA", "benchB"):
        return 0.65 if sn == "winter" else 1.0
    return 1.0


NEEDS = ["bread", "errand", "social", "food", "drink", "outdoors", "quiet",
         "purpose", "play", "football", "rest", "family", "cheer", "repair"]
GROW = {"bread": 0.55, "errand": 0.32, "social": 0.5, "food": 0.4, "drink": 0.32,
        "outdoors": 0.5, "quiet": 0.4, "purpose": 0.45, "play": 0.9,
        "football": 0.0, "rest": 0.6, "family": 0.5, "cheer": 0.0, "repair": 0.0}

# ---------------------------------------------------------------- population
FIRST = ["June", "Vera", "Hana", "Marge", "Bram", "Stan", "Claire", "Leo",
         "Pat", "Mo", "Dev", "Tomas", "Luca", "Agnes", "Bill", "Rosa",
         "Colin", "Priya", "Ted", "Nell", "Sam", "Iris", "Gwen", "Arthur",
         "Faye", "Ron", "Dot", "Ken", "Lily", "Owen", "Beth", "Carl",
         "Enid", "Vik", "Mabel", "Joe", "Wyn", "Sal", "Reg", "Petra"]
OCCS = ["baker", "baker2", "post", "post2", "cafe", "cafe2", "pub", "pub2",
        "stores", "stores2", "commuter", "commuter", "commuter", "commuter",
        "commuter", "commuter", "groundsman", "teacher", "teacher", "retired"]
ANCH = {
    "baker":     [(range(6), (0, 1, 2), "bakery")],
    "baker2":    [(range(6), (1, 2), "bakery")],
    "post":      [(range(5), (1, 2, 3), "post")],
    "post2":     [((1, 3, 4), (1, 2), "post")],
    "cafe":      [(None, (1, 2, 3, 4), "cafe")],
    "cafe2":     [(range(7), (2, 3), "cafe")],
    "pub":       [(None, (3, 4, 5, 6), "pub")],
    "pub2":      [(range(7), (5, 6), "pub")],
    "stores":    [(range(6), (1, 2, 3, 4), "stores")],
    "stores2":   [(range(6), (3, 4, 5), "stores")],
    "commuter":  [(range(5), (1,), "busstop"), (range(5), (5,), "busstop")],
    "groundsman": [(range(5), (1, 2), "ground_work")],
    "teacher":   [(range(5), (1, 2, 3), "green")],
    "retired":   [],
    "school":    [(range(5), (1, 2, 3), "green")],
}
PLACES["ground_work"] = {"loc": (155.0, 50.0), "sat": {}, "open": set(range(NS)),
                         "days": None, "cover": False, "quiet": True}


def make_population():
    res = []
    plots = [p["id"] for p in LEVEL["plots"]]
    ni = 0
    occs = list(OCCS)
    for hi, plot in enumerate(plots):
        size = [3, 3, 2, 2, 4, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2][hi]
        adults = min(size, 2)
        kids = size - adults
        for a in range(adults):
            nm = FIRST[ni]; ni += 1
            occ = occs.pop(h("occ", nm) % len(occs)) if occs else "retired"
            age = 28 + h("age", nm) % 45
            if occ == "retired":
                age = 60 + h("age", nm) % 20
            res.append({
                "n": nm, "age": age, "hh": hi, "home": plot, "occ": occ,
                "anchors": ANCH[occ],
                "tr": {"soc": 0.3 + hf("soc", nm) * 0.6,
                       "rout": 0.4 + hf("rt", nm) * 0.55,
                       "out": 0.2 + hf("ot", nm) * 0.7,
                       "foot": hf("ft", nm),
                       "temper": hf("tp", nm) * 0.8,
                       "duty": 0.3 + hf("dt", nm) * 0.6,
                       "range": 0.7 + hf("rg", nm) * 0.6},
                "poss": (["bike"] if hf("bk", nm) > 0.5 else []) +
                        (["season ticket"] if hf("st", nm) < 0.35 else []) +
                        (["ladder"] if hf("ld", nm) > 0.8 else []),
            })
        for k in range(kids):
            nm = FIRST[ni]; ni += 1
            res.append({
                "n": nm, "age": 6 + h("age", nm) % 10, "hh": hi, "home": plot,
                "occ": "school", "anchors": ANCH["school"], "child": True,
                "tr": {"soc": 0.6 + hf("soc", nm) * 0.3, "rout": 0.35,
                       "out": 0.7 + hf("ot", nm) * 0.25, "foot": 0.5 + hf("ft", nm) * 0.5,
                       "temper": hf("tp", nm) * 0.5, "duty": 0.2, "range": 0.8},
                "poss": ["ball"] if hf("bl", nm) > 0.4 else [],
            })
        if ni >= 39:
            break
    # two newcomers — data like anyone else, a year apart in season
    res.append({"n": "Petra", "age": 34, "hh": 99, "home": "P10", "occ": "commuter",
                "anchors": ANCH["commuter"], "arrives": 35,
                "tr": {"soc": 0.7, "rout": 0.6, "out": 0.6, "foot": 0.3,
                       "temper": 0.3, "duty": 0.6, "range": 1.1},
                "poss": ["bike"]})
    res.append({"n": "Jack", "age": 58, "hh": 98, "home": "P15", "occ": "retired",
                "anchors": ANCH["retired"], "arrives": 190,
                "tr": {"soc": 0.55, "rout": 0.7, "out": 0.5, "foot": 0.65,
                       "temper": 0.25, "duty": 0.5, "range": 0.9},
                "poss": []})
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
        r["bday"] = h("bd", r["n"]) % NDAYS
    return res


R = make_population()
# canon overrides — still data rows, zero special-case behaviour
_CANON = {
    "June": {"age": 61, "hh": 90, "occ": "post2", "home": "P09",
             "anchors": ANCH["post2"] + [((5,), (3, 4), "ground")],
             "tr_patch": {"foot": 0.8, "rout": 0.9, "temper": 0.14},
             "poss": ["season ticket"]},
    "Hana": {"age": 44, "occ": "baker", "anchors": ANCH["baker"],
             "tr_patch": {}, "poss": []},
}
for r in R:
    c = _CANON.get(r["n"])
    if c:
        for k, v in c.items():
            if k == "tr_patch":
                r["tr"].update(v)
            else:
                r[k] = v
        if r.get("age", 0) >= 18:
            r.pop("child", None)
            r.pop("teen", None)
BY_NAME = {r["n"]: r for r in R}


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
    for it in r["intents"]:
        if it["kind"] == kind and it["target"] == target and it["state"] == "open":
            it["prio"] = max(it["prio"], prio)
            return
    r["intents"].append({"kind": kind, "target": target, "prio": prio,
                         "born": day, "deadline": deadline, "state": "open",
                         "note": note})


# ---------------------------------------------------------------- events
def match_calendar():
    """ERA's competition: a fixture every Saturday, all 52 weeks.
    Home and away alternate — the town's fortnight heartbeat."""
    cal = {}
    for w in range(WEEKS):
        home = (w % 2 == 0)
        roll = h("match", w)
        result = "win" if roll < 4500 else ("draw" if roll < 7500 else "loss")
        cal[w] = ("home" if home else "away", result)
    return cal


MATCH = match_calendar()
EVENTS = []


def gen_events():
    adults = [r for r in R if not r.get("child") and not r.get("arrives")]
    for w in range(WEEKS):
        base = w * 7
        if h("ill", w) < 5200:
            v = adults[h("illwho", w) % len(adults)]
            EVENTS.append((base + h("illd", w) % 5, "illness",
                           {"who": v["n"], "days": 2 + h("illn", w) % 3}))
        if h("wp", w) < 3300:
            work = [a for a in adults if a["occ"] != "retired"]
            v = work[h("wpw", w) % len(work)]
            EVENTS.append((base + 0, "pressure", {"who": v["n"], "days": 5}))
        if h("hp", w) < 4500:
            v = adults[h("hpw", w) % len(adults)]
            EVENTS.append((base + h("hpd", w) % 6, "household",
                           {"who": v["n"], "what": ["leaking gutter", "stuck gate",
                                                    "broken pane", "wobbly shelf"][h("hpx", w) % 4]}))
        if h("bor", w) < 4000:
            a = adults[h("borA", w) % len(adults)]
            b = adults[h("borB", w) % len(adults)]
            if a["n"] != b["n"]:
                EVENTS.append((base + h("bord", w) % 6, "borrow",
                               {"who": a["n"], "lender": b["n"],
                                "item": ["ladder", "big pan", "hedge shears"][h("bori", w) % 3]}))
        if h("arg", w) < 3000:
            EVENTS.append((base + h("argd", w) % 6, "argument", {"seed": w}))
        if h("inv", w) < 3800:
            a = adults[h("invA", w) % len(adults)]
            EVENTS.append((base + h("invd", w) % 5, "invitation", {"who": a["n"]}))
    EVENTS.append((35, "arrival", {"who": "Petra"}))
    EVENTS.append((190, "arrival", {"who": "Jack"}))
    # one working life ends this year — the oldest non-canon worker
    olds = [a for a in adults if a["occ"] != "retired" and a["age"] >= 58
            and a["n"] not in _CANON]
    if olds:
        v = max(olds, key=lambda r: r["age"])
        EVENTS.append((217, "retirement", {"who": v["n"], "was": v["occ"]}))
    EVENTS.sort()


gen_events()

# ---------------------------------------------------------------- run
world = {"visits": [], "traces": [], "copresence": defaultdict(int),
         "argulog": [], "eventlog": [], "occ": defaultdict(int),
         "int_done": 0, "int_forgot": 0, "famday": set()}


def active(r, day):
    return day >= r.get("arrives", -1)


def anchored(r, d, s, day):
    if r["ill_until"] >= day:
        return None, None
    if day in HOLIDAYS:
        return None, None
    if r["occ"] in ("school", "teacher") and school_holiday(day):
        return None, None
    for (dayf, slots, place) in r["anchors"]:
        if (dayf is None or d in dayf) and s in slots:
            if place == "ground":
                _mt = MATCH.get(day // 7)
                if _mt is None or _mt[0] != "home":
                    continue                # away week: gates shut
            return place, "work/school"
    if r["pressure_until"] >= day and s == 4 and r["occ"] not in ("retired", "school"):
        for (dayf, slots, place) in r["anchors"]:
            return place, "staying late (pressure)"
    return None, None


def dist(a, b):
    if a is None or b is None:
        return 0.0
    return math.hypot(a[0] - b[0], a[1] - b[1])


for day in range(NDAYS):
    w, d = divmod(day, 7)
    wx = wx_day(day)
    sn = season_of(day)
    mt = MATCH.get(w)
    # ---- events fire
    while EVENTS and EVENTS[0][0] == day:
        _, kind, pay = EVENTS.pop(0)
        world["eventlog"].append((day, kind, dict(pay)))
        if kind == "illness":
            v = BY_NAME[pay["who"]]
            v["ill_until"] = day + pay["days"]
            v["log"].append((day, f"ill for {pay['days']} days"))
        elif kind == "pressure":
            v = BY_NAME[pay["who"]]
            v["pressure_until"] = day + pay["days"]
            v["log"].append((day, "a hard week at work"))
        elif kind == "household":
            v = BY_NAME[pay["who"]]
            add_intent(v, "repair", "stores", 3.2, day, day + 6, pay["what"])
            v["log"].append((day, f"household problem: {pay['what']}"))
        elif kind == "borrow":
            a, b = BY_NAME[pay["who"]], BY_NAME[pay["lender"]]
            if active(a, day) and active(b, day):
                add_intent(a, "return", pay["lender"], 2.4, day, day + 7, pay["item"])
                rel(a, b["n"])["obligation"] += 1.0
                rel(a, b["n"])["ev"].append((day, "borrowed " + pay["item"]))
                rel(b, a["n"])["ev"].append((day, "lent " + pay["item"]))
                a["log"].append((day, f"borrowed the {pay['item']} from {b['n']}"))
        elif kind == "invitation":
            a = BY_NAME[pay["who"]]
            best = sorted(((rl["affection"], o) for o, rl in a["rel"].items()
                           if rl["rec"] >= 4), reverse=True)[:1]
            if best:
                o = best[0][1]
                add_intent(a, "visit", o, 2.2, day, day + 5)
                a["log"].append((day, f"means to call on {o}"))
        elif kind == "arrival":
            v = BY_NAME[pay["who"]]
            v["log"].append((day, f"moved into {v['home']} — knows nobody"))
        elif kind == "retirement":
            v = BY_NAME[pay["who"]]
            v["occ"] = "retired"
            v["anchors"] = ANCH["retired"]
            v["log"].append((day, f"retired — last shift as {pay['was']}"))
    # birthdays
    for r in R:
        if active(r, day) and r["bday"] == day and not r.get("child"):
            r["log"].append((day, "birthday"))
            invited = sorted(((rl["affection"], o) for o, rl in r["rel"].items()
                              if rl["rec"] >= 5), reverse=True)[:3]
            for _, o in invited:
                add_intent(BY_NAME[o], "celebrate", r["n"], 3.0, day, day + 1)
    # matchday mood (only in season)
    if d == 5 and mt:
        venue, result = mt
        world["eventlog"].append((day, "match", {"venue": venue, "result": result}))
        for r in R:
            if active(r, day):
                r["needs"]["football"] += 5.5 * r["tr"]["foot"] * (1.0 if venue == "home" else 0.45)
    # holidays fill the houses
    if day in HOLIDAYS:
        for r in R:
            if active(r, day):
                r["needs"]["family"] += 4.0 if day in (CHRISTMAS, CHRISTMAS + 1) else 1.2
    # ---- needs grow, intents form
    for r in R:
        if not active(r, day):
            continue
        for n in NEEDS:
            g = GROW[n]
            if n == "play" and not r.get("child"):
                g *= 0.25
            if n == "play" and r.get("child") and school_holiday(day):
                g *= 1.5
            r["needs"][n] += g * (0.8 + hf("g", r["n"], day, n) / 2.5)
        if r["needs"]["bread"] > 2.6:
            add_intent(r, "buy", "bakery", 2.0 + r["needs"]["bread"] * 0.2, day, day + 2)
        if not r.get("child") and r["tr"]["soc"] > 0.55:
            lonely = [o for o, rl in r["rel"].items()
                      if rl["affection"] >= 2.5 and day - rl["last"] > 9]
            if lonely and hf("visit", r["n"], day) > 0.6:
                add_intent(r, "visit", lonely[h("vw", r["n"], day) % len(lonely)],
                           1.8, day, day + 6)
        if d == 4 and r["tr"]["foot"] > 0.6 and mt and mt[0] == "home":
            add_intent(r, "prep", "stores", 1.6, day, day + 1, "matchday shop")
        if wx != "rain" and not r.get("child") and hf("wash", r["n"], day) > 0.45:
            world["traces"].append((day, r["n"], "washing out/in"))
        if d == 1:
            world["traces"].append((day, r["n"], "bin out"))

    # ---- whereabouts guesses + social shortlist (computed once per day)
    guess = {}
    for r in R:
        g = {}
        for (pl, dd, ss), c in r["habit"].items():
            if dd == d and (ss not in g or c > g[ss][0]):
                g[ss] = (c, pl)
        guess[r["n"]] = {ss: pl for ss, (c, pl) in g.items()}
    for r in R:
        top = sorted(((rl["affection"], o, rl) for o, rl in r["rel"].items()
                      if rl["tension"] or rl["affection"] >= 4.0), reverse=True)[:6]
        r["_top"] = [(o, rl) for _, o, rl in top]

    for s in range(NS):
        present = defaultdict(list)
        for r in R:
            if not active(r, day):
                continue
            place, why = anchored(r, d, s, day)
            intent_used = None
            if place is None:
                if r["ill_until"] >= day:
                    place, why = "home", "ill"
                else:
                    best, bestv = "home", 1.0 + r["needs"]["rest"] * 0.5
                    open_now = {}
                    for pid, P_ in PLACES.items():
                        if pid in ("home", "busstop", "ground_work"):
                            continue
                        if pid == "pub" and r.get("child"):
                            continue
                        if day in HOLIDAYS and pid in SHOPS:
                            continue
                        if pid == "ground" and (mt is None or mt[0] != "home"):
                            continue        # away week: gates shut
                        if P_["days"] is not None and d not in P_["days"]:
                            continue
                        if s not in P_["open"]:
                            continue
                        open_now[pid] = P_
                    for it in sorted(r["intents"], key=lambda i: -i["prio"]):
                        if it["state"] != "open":
                            continue
                        tgt = it["target"]
                        if it["kind"] in ("buy", "repair", "prep") and tgt in open_now:
                            place, why, intent_used = tgt, f"intention: {it['kind']} ({it['note'] or tgt})", it
                            break
                        if it["kind"] in ("visit", "return", "celebrate"):
                            o = BY_NAME.get(tgt)
                            if o and active(o, day):
                                gp = guess.get(tgt, {}).get(s)
                                if it["kind"] == "celebrate":
                                    gp = "pub" if "pub" in open_now else gp
                                if gp and gp in open_now:
                                    place, why, intent_used = gp, f"intention: {it['kind']} {tgt}", it
                                    break
                    if place is None:
                        for pid, P_ in open_now.items():
                            v = sum(r["needs"].get(n, 0) * st for n, st in P_["sat"].items())
                            v *= smul(pid, day)
                            v *= (1.5 if s >= 5 and "drink" in P_["sat"] else 1.0)
                            v -= dist(PXY[r["home"]], P_["loc"]) / (55.0 * r["tr"]["range"])
                            v += min(r["habit"].get((pid, d, s), 0), 8) * 0.5 * r["tr"]["rout"]
                            if wx == "rain" and not P_["cover"]:
                                v -= 2.6
                            if wx == "wind" and not P_["cover"]:
                                v -= 0.7
                            if sn == "winter" and s >= 5 and not P_["cover"]:
                                v -= 1.6              # dark by five o'clock
                            m = pmem(r, pid)
                            if m["sore_until"] >= day:
                                v -= 2.0
                            v += min(m["warm"], 3) * 0.25
                            # the people you like bend your path; tension bends it away
                            pull = 0.0
                            for o, rl in r["_top"]:
                                if guess.get(o, {}).get(s) == pid:
                                    if rl["tension"]:
                                        pull -= 1.8
                                    else:
                                        pull += 0.5 * r["tr"]["soc"]
                            v += max(-3.6, min(pull, 1.2))
                            v += (hf("j", r["n"], day, s, pid) - 0.5) * 0.8
                            if v > bestv:
                                best, bestv = pid, v
                        place, why = best, ("chose it" if best != "home" else None)
            # ---- commit
            r["cur"] = place
            if place not in ("home",):
                P_ = PLACES[place]
                for n, st in P_.get("sat", {}).items():
                    r["needs"][n] = max(0.0, r["needs"][n] - st * 1.4)
                if place == "ground":
                    r["needs"]["football"] = 0.0
                    if "season ticket" in r.get("poss", []) or r["tr"]["foot"] > 0.55:
                        world["traces"].append((day, r["n"], "scarf on the rail"))
                r["habit"][(place, d, s)] = r["habit"].get((place, d, s), 0) + 1
                world["occ"][(place, s)] += 1
                m = pmem(r, place)
                m["uses"] += 1
                m["last"] = day
                present[place].append(r["n"])
            else:
                r["needs"]["rest"] = max(0, r["needs"]["rest"] - 1.2)
                r["needs"]["family"] = max(0, r["needs"]["family"] - 0.8)
            world["visits"].append((day, s, r["n"], place,
                                    why or "", intent_used is not None, wx))
            if intent_used is not None:
                intent_used["state"] = "done"
                intent_used["done"] = day
                world["int_done"] += 1
                if intent_used["kind"] == "return":
                    o = BY_NAME[intent_used["target"]]
                    rel(r, o["n"])["obligation"] = 0.0
                    rel(o, r["n"])["trust"] += 1.0
                    rel(r, o["n"])["trust"] += 0.5
                    rel(r, o["n"])["ev"].append((day, "returned " + intent_used["note"]))
                    r["log"].append((day, f"returned the {intent_used['note']} to {o['n']}"))
        # ---- co-presence -> relationships
        for pid, names in present.items():
            quiet = PLACES[pid].get("quiet")
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = BY_NAME[names[i]], BY_NAME[names[j]]
                    key = (names[i], names[j], day)
                    if key in world["famday"]:
                        continue
                    world["famday"].add(key)
                    ra, rb = rel(a, b["n"]), rel(b, a["n"])
                    if ra["met"] is None:
                        ra["met"] = (day, pid)
                        rb["met"] = (day, pid)
                    if pid == "ground":
                        ra["ev"].append((day, "match together"))
                        rb["ev"].append((day, "match together"))
                    for rr in (ra, rb):
                        rr["rec"] += 1
                        rr["last"] = day
                        rr["comfort"] += 0.25 if quiet else 0.15
                    if ra["rec"] > 3:
                        ra["affection"] += 0.2 * a["tr"]["soc"]
                        rb["affection"] += 0.2 * b["tr"]["soc"]
                    if len(names) > 6:
                        ra["irritation"] += 0.15 * a["tr"]["temper"]
                        rb["irritation"] += 0.15 * b["tr"]["temper"]
                    if ra["tension"] and day - ra["tension"] >= 3 and quiet:
                        ra["tension"] = 0
                        rb["tension"] = 0
                        ra["comfort"] += 1.0
                        rb["comfort"] += 1.0
                        ra["ev"].append((day, "made peace at the " + pid))
                        rb["ev"].append((day, "made peace at the " + pid))
                        a["log"].append((day, f"made peace with {b['n']} at the {pid}"))
                        world["argulog"].append((day, a["n"], b["n"], "resolved", pid))
                    world["copresence"][(names[i], names[j], pid)] += 1
            for nm in names:
                m = pmem(BY_NAME[nm], pid)
                for other in names:
                    if other != nm:
                        m["assoc"][other] += 1
    # ---- arguments pick their pair at day end
    for (dy, kind, pay) in list(world["eventlog"]):
        if kind == "argument" and dy == day and "done" not in pay:
            pay["done"] = True
            cands = [(k, v) for k, v in world["copresence"].items() if v >= 4]
            if cands:
                (a, b, pl), _ = cands[h("argpick", pay["seed"]) % len(cands)]
                ra, rb = rel(BY_NAME[a], b), rel(BY_NAME[b], a)
                ra["tension"] = day
                rb["tension"] = day
                ra["irritation"] += 1.2
                rb["irritation"] += 1.2
                ra["ev"].append((day, "argued at the " + pl))
                rb["ev"].append((day, "argued at the " + pl))
                pmem(BY_NAME[a], pl)["sore_until"] = day + 6
                pmem(BY_NAME[b], pl)["sore_until"] = day + 6
                BY_NAME[a]["log"].append((day, f"words with {b} at the {pl}"))
                BY_NAME[b]["log"].append((day, f"words with {a} at the {pl}"))
                world["argulog"].append((day, a, b, "argument", pl))
    # post-match cheer
    if d == 5 and mt:
        venue, result = mt
        for r in R:
            if active(r, day) and r["tr"]["foot"] > 0.3:
                r["needs"]["cheer"] += {"win": 2.2, "draw": 0.6, "loss": -1.0}[result] * r["tr"]["foot"]
                r["needs"]["cheer"] = max(0.0, r["needs"]["cheer"])
    # moods fade at day's end; unfed relationships cool
    for r in R:
        r["needs"]["football"] *= 0.55
        r["needs"]["cheer"] *= 0.75
        for rl in r["rel"].values():
            if day - rl["last"] > 14:
                rl["affection"] *= 0.985
                rl["comfort"] *= 0.99
            rl["irritation"] *= 0.995
    # intention lifecycle
    for r in R:
        for it in r["intents"]:
            if it["state"] == "open" and day > it["deadline"]:
                it["state"] = "forgotten"
                world["int_forgot"] += 1
                if it["kind"] == "return":
                    o = BY_NAME.get(it["target"])
                    if o:
                        rel(o, r["n"])["irritation"] += 0.8
                        rel(o, r["n"])["trust"] -= 0.5
                        rel(o, r["n"])["ev"].append((day, "never got the " + it["note"] + " back"))
                        o["log"].append((day, f"still hasn't got the {it['note']} back from {r['n']}"))
        r["intents"] = [it for it in r["intents"] if it["state"] == "open" or
                        day - it.get("done", it["deadline"]) < 30]

WORLD = world
RESIDENTS = R

if __name__ == "__main__":
    print(f"the first living town: {len(R)} residents, {WEEKS} weeks, "
          f"{len(world['visits'])} visit records, {len(world['eventlog'])} events, "
          f"intentions {world['int_done']} done / {world['int_forgot']} forgotten")
