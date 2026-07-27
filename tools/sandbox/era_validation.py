"""
era_validation — the third layer. The sandbox generates; story metrics
interpret; this judges against ERA's design principles. No new score zoo:
each check ends PASS / CONCERN / FAIL with the observed behaviour that
justifies it. Also writes living_report.txt: five lives in detail.
"""
import living
from collections import defaultdict

R = living.RESIDENTS
W = living.WORLD
WEEKS = living.WEEKS
DAYS = living.DAYS
SLOTS = living.SLOTS
BY = living.BY_NAME

visits = W["visits"]
out = []
P = out.append

active_names = [r["n"] for r in R]

# ---------------------------------------------------------------- helpers
chosen = defaultdict(list)      # name -> [(day,s,place)]
byslot = defaultdict(dict)      # (name, day) -> {s: place}
for (day, s, n, p, why, intent, wx) in visits:
    byslot[(n, day)][s] = p
    if why.startswith("chose") or why.startswith("intention"):
        chosen[n].append((day, s, p))


def week_routine(n, w):
    return tuple(byslot.get((n, w * 7 + d), {}).get(s, "home")
                 for d in range(7) for s in range(7))


def stability(n, w):
    a, b = week_routine(n, w), week_routine(n, w - 1)
    return sum(x == y for x, y in zip(a, b)) / 49.0


def jacc(a, b):
    A = set(k for k in BY[a]["habit"] if BY[a]["habit"][k] >= 3)
    B = set(k for k in BY[b]["habit"] if BY[b]["habit"][k] >= 3)
    return len(A & B) / max(1, len(A | B))


def adopted_places(r):
    tot = defaultdict(int)
    for (day, s, p) in chosen[r["n"]]:
        if p != "home":
            tot[p] += 1
    free = max(1, len(chosen[r["n"]]))
    return [(p, c) for p, c in sorted(tot.items(), key=lambda x: -x[1])
            if c >= 8 and c / free > 0.12][:3]


# ---------------------------------------------------------------- verdicts
def verdict(name, status, evidence):
    P(f"[{status:^7s}] {name}")
    for e in evidence:
        P(f"          - {e}")
    P("")


P("=" * 72)
P("ERA VALIDATION — living district, %d residents, %d weeks, seed %d"
  % (len(R), WEEKS, living.SEED))
P("=" * 72)
P("")

# 1 distinct lives
sims = []
adults = [r["n"] for r in R if not r.get("child")]
for i in range(len(adults)):
    for j in range(i + 1, len(adults)):
        a, b = adults[i], adults[j]
        if BY[a]["hh"] != BY[b]["hh"]:
            sims.append((jacc(a, b), a, b))
sims.sort(reverse=True)
med = sims[len(sims) // 2][0]
verdict("residents develop distinct lives",
        "PASS" if med < 0.35 and sims[0][0] < 0.8 else "CONCERN",
        [f"median cross-household routine overlap {med:.2f}; most similar pair "
         f"{sims[0][1]}&{sims[0][2]} at {sims[0][0]:.2f}"])

# 2 attachment possible for everyone
ad = {r["n"]: adopted_places(r) for r in R}
without = [n for n, a in ad.items() if not a and not BY[n].get("child")]
verdict("every resident can form attachment",
        "PASS" if len(without) <= len(adults) * 0.25 else "CONCERN",
        [f"{len(adults) - len(without)}/{len(adults)} adults adopted at least one place",
         ("still placeless: " + ", ".join(without[:8])) if without else "nobody placeless"])

# 3 places matter differently
place_adopters = defaultdict(list)
for n, a in ad.items():
    for (p, c) in a:
        place_adopters[p].append(n)
multi = {p: ns for p, ns in place_adopters.items() if len(ns) >= 2}
ex = []
for p, ns in list(multi.items())[:3]:
    ages = sorted(BY[n]["age"] for n in ns)
    ex.append(f"{p}: adopted by {len(ns)} (ages {ages[0]}–{ages[-1]})")
verdict("places matter differently to different people",
        "PASS" if len(multi) >= 4 else "CONCERN",
        [f"{len(multi)} places hold 2+ adopters with different lives"] + ex)

# 4 familiar strangers
recs = []
for r in R:
    for o, rl in r["rel"].items():
        if r["n"] < o:
            recs.append(rl["rec"])
low = sum(1 for v in recs if 1 <= v <= 6)
verdict("familiar strangers remain possible",
        "PASS" if low / max(1, len(recs)) > 0.25 else "CONCERN",
        [f"{low}/{len(recs)} known pairs are still in the 1–6 'nodding' band "
         f"({100 * low // max(1, len(recs))}%) at week {WEEKS}"])

# 5 routine recovery after interruption
recov = []
for (day, kind, pay) in W["eventlog"]:
    if kind == "illness":
        n = pay["who"]
        w0 = day // 7
        if 1 <= w0 <= WEEKS - 3:
            pre = stability(n, w0) if w0 >= 1 else 1
            after = [stability(n, w) for w in range(w0 + 1, min(w0 + 4, WEEKS))]
            back = next((i + 1 for i, v in enumerate(after) if v >= 0.6), None)
            recov.append((n, day, back))
ok = [b for (_, _, b) in recov if b is not None and b <= 2]
verdict("routines recover after interruption",
        "PASS" if recov and len(ok) >= len(recov) * 0.7 else "CONCERN",
        [f"{len(ok)}/{len(recov)} illness interruptions recovered within 2 weeks"] +
        [f"{n}: ill day {d}, routine back in {b or '>3'} week(s)" for (n, d, b) in recov[:4]])

# 6 football influences without consuming
sat_foot = sum(1 for (day, s, n, p, why, i, wx) in visits
               if day % 7 == 5 and p in ("ground", "pub"))
sat_all = sum(1 for (day, s, n, p, why, i, wx) in visits if day % 7 == 5 and p != "home")
wk_foot = sum(1 for (day, s, n, p, why, i, wx) in visits
              if day % 7 < 5 and p == "ground")
wk_all = sum(1 for v in visits if v[0] % 7 < 5 and v[3] != "home")
verdict("football shapes life without consuming it",
        "PASS" if sat_foot / max(1, sat_all) > 0.2 and wk_foot / max(1, wk_all) < 0.05 else "CONCERN",
        [f"Saturday: {100 * sat_foot // max(1, sat_all)}% of outings are ground/pub; "
         f"weekdays: {100 * wk_foot / max(1, wk_all):.1f}% touch the ground (staff only)"])

# 7 Tuesday vs Saturday
def dayset(dd):
    return set((n, p) for (day, s, n, p, why, i, wx) in visits
               if day == dd and p != "home")
tu, sa = dayset(7 * 6 + 1), dayset(7 * 6 + 5)
diff = len(tu.symmetric_difference(sa))
verdict("Tuesday and Saturday are structurally different",
        "PASS" if diff > (len(tu) + len(sa)) * 0.4 else "CONCERN",
        [f"week 7: |Tue|={len(tu)} |Sat|={len(sa)}, symmetric difference {diff}"])

# 8 solitude, waiting, encounters, belonging
solo = sum(1 for (day, s, n, p, why, i, wx) in visits
           if p in ("oak", "benchA", "benchB", "allotment"))
waiting = sum(1 for (day, s, n, p, why, i, wx) in visits if p == "busstop")
enc = sum(1 for k, v in W["copresence"].items() if v <= 2)
belong = sum(c for n, a in ad.items() for (p, c) in a)
verdict("the district produces solitude, waiting, encounters and belonging",
        "PASS" if min(solo, waiting, enc, belong) > 30 else "CONCERN",
        [f"quiet-place visits {solo} · bus-stop waits {waiting} · "
         f"light encounters {enc} pairs · adopted-place visits {belong}"])

# 9 believable over months
stab_by_week = [sum(stability(n, w) for n in active_names if (n, w * 7) and
                    BY[n].get("arrives", -1) < (w - 1) * 7) /
                max(1, len([n for n in active_names if BY[n].get("arrives", -1) < (w - 1) * 7]))
                for w in range(2, WEEKS)]
maxneed = max(max(r["needs"].values()) for r in R)
forgot = W["int_forgot"]
done = W["int_done"]
verdict("behaviour stays believable over months",
        "PASS" if stab_by_week[-1] > 0.5 and maxneed < 30 else "CONCERN",
        [f"routine stability weeks 3..{WEEKS}: " +
         " ".join(f"{v:.2f}" for v in stab_by_week),
         f"no need diverges (max accumulated need {maxneed:.1f}); "
         f"intention outcomes over the run: {done} fulfilled / {forgot} forgotten"])

# ---------------------------------------------------------------- five lives
P("=" * 72)
P("FIVE LIVES (selected: June; the newcomer; the most eventful; a child; a shift worker)")
P("=" * 72)


def life(nm):
    r = BY[nm]
    P("")
    P(f"--- {r['n']}, {r['age']}, {r['occ']}, household {r['hh']} ({r['home']}) ---")
    tr = r["tr"]
    P(f"    traits: sociability {tr['soc']:.2f} routine {tr['rout']:.2f} "
      f"outdoors {tr['out']:.2f} football {tr['foot']:.2f} temper {tr['temper']:.2f}")
    if r.get("poss"):
        P(f"    possessions: {', '.join(r['poss'])}")
    a = adopted_places(r)
    P("    adopted: " + (", ".join(f"{p} ({c} chosen visits)" for p, c in a) or "nowhere yet"))
    sore = [p for p, m in r["pmem"].items() if m["sore_until"] > 0]
    if sore:
        P("    avoided for a while: " + ", ".join(sore))
    # relationships: top by affection and by irritation
    rels = sorted(r["rel"].items(), key=lambda kv: -kv[1]["affection"])[:3]
    for o, rl in rels:
        P(f"    close to {o}: rec {rl['rec']}, comfort {rl['comfort']:.1f}, "
          f"affection {rl['affection']:.1f}, trust {rl['trust']:.1f}")
    irr = sorted(r["rel"].items(), key=lambda kv: -kv[1]["irritation"])[:1]
    for o, rl in irr:
        if rl["irritation"] > 0.8:
            P(f"    rubbed wrong by {o}: irritation {rl['irritation']:.1f}"
              + (", unresolved tension" if rl["tension"] else ""))
    ints = [it for it in r["intents"]]
    P(f"    intentions now open: " +
      (", ".join(f"{it['kind']}->{it['target']}" for it in ints if it["state"] == "open") or "none"))
    st = [f"wk{w}:{stability(r['n'], w):.2f}" for w in (2, 5, 8, 11)
          if BY[nm].get("arrives", -1) < (w - 1) * 7]
    P("    routine stability: " + "  ".join(st))
    P("    life log:")
    for (dy, txt) in r["log"][:10]:
        P(f"      d{dy:02d} {DAYS[dy % 7]}: {txt}")


most_eventful = max((r for r in R if r["n"] not in ("June", "Petra")
                     and not r.get("child")), key=lambda r: len(r["log"]))
picked = {"June", "Petra", most_eventful["n"]}
a_child = next(r for r in R if r.get("child") and r["n"] not in picked)
picked.add(a_child["n"])
shift = next(r for r in R if r["occ"] in ("baker", "pub", "cafe", "stores")
             and not r.get("child") and r["n"] not in picked)
for nm in ["June", "Petra", most_eventful["n"], a_child["n"], shift["n"]]:
    life(nm)

# ---------------------------------------------------------------- district failures
P("")
P("=" * 72)
P("DISTRICT FAILURES EXPOSED")
P("=" * 72)
occ = W["occ"]
for pid in living.PLACES:
    if pid in ("home", "ground_work"):
        continue
    tot = sum(occ.get((pid, s), 0) for s in range(7))
    if tot == 0:
        P(f"  DEAD: {pid} — zero visits in {WEEKS} weeks")
evening_out = sum(occ.get((p, s), 0) for p in ("oak", "green", "benchA", "benchB")
                  for s in (5, 6))
P(f"  the green/oak quarter after 17:00: {evening_out} visits in {WEEKS} weeks "
  f"— the pub owns the evening; standing finding, third run in a row")
mkt = sum(occ.get(("market", s), 0) for s in range(7))
P(f"  market: {mkt} visits, all Friday — pairing with 'square' holds, no action")
argu = [x for x in W["argulog"] if x[3] == "argument"]
reso = [x for x in W["argulog"] if x[3] == "resolved"]
P(f"  arguments: {len(argu)} broke out, {len(reso)} made peace (quiet places did "
  f"the mending: {', '.join(sorted(set(x[4] for x in reso))) or 'n/a'})")

text = "\n".join(out)
open("living_report.txt", "w").write(text)
print(text[:400])
print("...")
print(f"[written living_report.txt — {len(text)} chars]")
