"""
story_metrics — the researcher above the simulator.

The sandbox generates behaviour; this layer asks whether any of it became a
LIFE. Occupancy is a vanity metric here. Every construct is operationalised
so it can be defended, disputed, and recomputed:

  RITUAL     a CHOSEN visit recurring at the same (day, slot) for >=3
             consecutive weeks. Anchored visits never count — a shift is a
             job, not a ritual.
  LOOM       a place that repeatedly brings the same pair together on
             different days. "Chosen looms" (at least one of the pair chose
             to be there) outrank colleague looms.
  ADOPTION   chosen devotion: share of a resident's free slots given to a
             place, persistence across weeks, and at least one visit in bad
             weather to an uncovered place (devotion beyond comfort).
  INTERSECTION  a pair that meets in >=2 DIFFERENT places (>=2 meetings in
             each). Colleagues meet at work; intersecting lives meet
             everywhere.
  FORGOTTEN  alive in weeks 1-2, abandoned in weeks 3-4 (chosen visits
             late/early < 0.4), or never chosen at all.
  ATTACHMENT DRIVERS  place attributes (cover, affordance breadth, hours
             breadth) compared by mean adoption — which design elements
             create attachment.

Town verdicts: MEMORABLE (share of places hosting rituals), LOVABLE (share
of residents with an adopted place), SOCIALLY RICH (multi-place ties and
chosen encounters).
"""
import sandbox
from collections import defaultdict

D = sandbox.DATA
EV = D["events"]                    # (week, d, s, name, place, anchored, wx)
WEEKS = D["weeks"]
PLACES = D["places"]
RESIDENTS = [r["n"] for r in D["residents"]]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOTS = ["07", "09", "11", "13", "15", "17", "19"]

chosen = [e for e in EV if not e[5] and e[4] != "home"]
anchoredv = [e for e in EV if e[5]]

# ---------------------------------------------------------------- rituals
rituals = []
by_rps = defaultdict(set)
for (w, d, s, n, p, a, wx) in chosen:
    by_rps[(n, p, d, s)].add(w)
for (n, p, d, s), ws in by_rps.items():
    streak = best = 0
    for w in range(WEEKS):
        streak = streak + 1 if w in ws else 0
        best = max(best, streak)
    if best >= 3:
        rituals.append((n, p, DAYS[d], SLOTS[s], best))

# ---------------------------------------------------------------- looms
pair_place_days = defaultdict(set)
pair_place_chosen = defaultdict(bool)
loc_at = defaultdict(dict)
for (w, d, s, n, p, a, wx) in EV:
    if p != "home":
        loc_at[(w, d, s)][n] = (p, a)
for key, folks in loc_at.items():
    names = sorted(folks)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_, b_ = names[i], names[j]
            pa, aa = folks[a_]
            pb, ab = folks[b_]
            if pa == pb:
                pair_place_days[(a_, b_, pa)].add((key[0], key[1]))
                if not (aa and ab):
                    pair_place_chosen[(a_, b_, pa)] = True

looms = defaultdict(lambda: [0, 0])
for (a_, b_, p), days in pair_place_days.items():
    if len(days) >= 3:
        looms[p][0] += 1
        if pair_place_chosen[(a_, b_, p)]:
            looms[p][1] += 1

# ---------------------------------------------------------------- adoption
free_slots = defaultdict(int)
chosen_pn = defaultdict(int)
weeks_pn = defaultdict(set)
badwx_pn = defaultdict(int)
for (w, d, s, n, p, a, wx) in EV:
    if not a:
        free_slots[n] += 1
for (w, d, s, n, p, a, wx) in chosen:
    chosen_pn[(n, p)] += 1
    weeks_pn[(n, p)].add(w)
    if wx in ("rain", "wind") and not PLACES[p]["cover"]:
        badwx_pn[(n, p)] += 1

adoption = {}
for (n, p), c in chosen_pn.items():
    share = c / max(1, free_slots[n])
    persist = len(weeks_pn[(n, p)]) / WEEKS
    devotion = min(1.0, badwx_pn[(n, p)] / 2.0)
    score = 0.5 * min(1.0, share * 4) + 0.35 * persist + 0.15 * devotion
    adoption[(n, p)] = score
adopted = [(n, p, sc) for (n, p), sc in adoption.items() if sc >= 0.62]
adopted.sort(key=lambda x: -x[2])

# ---------------------------------------------------------------- intersections
pair_places = defaultdict(set)
for (a_, b_, p), days in pair_place_days.items():
    if len(days) >= 2:
        pair_places[(a_, b_)].add(p)
inter = [(a_, b_, ps) for (a_, b_), ps in pair_places.items() if len(ps) >= 2]
inter.sort(key=lambda x: -len(x[2]))

# ---------------------------------------------------------------- forgotten
early = defaultdict(int)
late = defaultdict(int)
for (w, d, s, n, p, a, wx) in chosen:
    (early if w < 2 else late)[p] += 1
forgotten = []
for p in PLACES:
    if p in ("home", "busstop"):
        continue
    e_, l_ = early[p], late[p]
    if e_ + l_ == 0:
        forgotten.append((p, "never chosen at all (anchor/transit only)"))
    elif e_ >= 4 and l_ / max(1, e_) < 0.4:
        forgotten.append((p, f"abandoned: {e_} early chosen visits, {l_} late"))

# ---------------------------------------------------------------- drivers
def mean_adopt(pids):
    vals = [sc for (n, p), sc in adoption.items() if p in pids]
    return sum(vals) / len(vals) if vals else 0.0

cov = [p for p in PLACES if PLACES[p]["cover"] and p != "home"]
unc = [p for p in PLACES if not PLACES[p]["cover"]]
multi = [p for p in PLACES if len(PLACES[p]["sat"]) >= 2 and p != "home"]
single = [p for p in PLACES if len(PLACES[p]["sat"]) == 1]
allday = [p for p in PLACES if len(PLACES[p]["open"]) >= 6 and p != "home"]
narrow = [p for p in PLACES if 0 < len(PLACES[p]["open"]) <= 3]

# ---------------------------------------------------------------- verdicts
placeset = [p for p in PLACES if p not in ("home", "busstop")]
ritual_places = {p for (_, p, _, _, _) in rituals}
lovers = {n for (n, p, sc) in adopted}
chosen_pair_share = (sum(1 for k in pair_place_chosen if pair_place_chosen[k])
                     / max(1, len(pair_place_days)))

print("STORY METRICS — District 01, %d weeks, seed %d" % (WEEKS, sandbox.SEED))
print("=" * 64)
print()
print("RITUALS (chosen, same day+slot, 3+ consecutive weeks):")
for (n, p, dy, sl, st) in sorted(rituals, key=lambda x: (x[1], x[0])):
    print(f"   {n:10s} {p:10s} {dy} {sl}:00  ({st} weeks running)")
print(f"   -> {len(rituals)} rituals across {len(ritual_places)} places: "
      + ", ".join(sorted(ritual_places)))
print()
print("LOOMS (places weaving the same pairs together, 3+ different days):")
for p, (tot, ch) in sorted(looms.items(), key=lambda x: -x[1][0]):
    print(f"   {p:10s} {tot} recurring pairs ({ch} with at least one side there by choice)")
print()
print("EMOTIONAL ADOPTION (score >= 0.62: share of free life + persistence + bad-weather devotion):")
for (n, p, sc) in adopted:
    marks = []
    if badwx_pn[(n, p)]:
        marks.append("went in bad weather")
    if len(weeks_pn[(n, p)]) == WEEKS:
        marks.append("every week")
    print(f"   {n:10s} adopted {p:10s} ({sc:.2f}" + ((" — " + ", ".join(marks)) if marks else "") + ")")
print()
print("LIVES THAT INTERSECT (same pair, 2+ places, 2+ meetings each):")
for (a_, b_, ps) in inter[:10]:
    print(f"   {a_} & {b_}: " + ", ".join(sorted(ps)))
print(f"   -> {len(inter)} multi-context ties of {len(pair_places)} recurring pairs")
print()
print("FORGOTTEN:")
for (p, why) in forgotten:
    print(f"   {p:10s} {why}")
if not forgotten:
    print("   none")
print()
print("ATTACHMENT DRIVERS (mean adoption score by design attribute):")
print(f"   covered {mean_adopt(cov):.2f}  vs  uncovered {mean_adopt(unc):.2f}")
print(f"   multi-need {mean_adopt(multi):.2f}  vs  single-need {mean_adopt(single):.2f}")
print(f"   all-day hours {mean_adopt(allday):.2f}  vs  narrow hours {mean_adopt(narrow):.2f}")
print()
print("TOWN VERDICTS")
print(f"   MEMORABLE: {len(ritual_places)}/{len(placeset)} places host at least one ritual "
      f"({100 * len(ritual_places) // len(placeset)}%)")
print(f"   LOVABLE:   {len(lovers)}/{len(RESIDENTS)} residents have adopted a place "
      f"({100 * len(lovers) // len(RESIDENTS)}%) — missing: "
      + (", ".join(sorted(set(RESIDENTS) - lovers)) or "nobody"))
print(f"   SOCIALLY RICH: {len(inter)} multi-place ties; "
      f"{100 * chosen_pair_share:.0f}% of recurring pair-meetings involve choice, not duty")
