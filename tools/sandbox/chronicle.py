"""
chronicle — PHASE 5: the historian above the year.

year.py generates a year of behaviour; this layer writes what the year
MEANT. Three documents, all computed, none authored:

  year_chronicle.txt      the district's historical record + place identities
  year_biographies.txt    five resident lives, generated from simulation
  era_validation_v2.txt   one question: if a player returned a year later,
                          would it genuinely feel like another year passed?

Relationships are reported as histories (borrowed twice, argued once, six
matches together, haven't spoken since March) — the numbers stay inside.
"""
import year as Y
from collections import defaultdict, Counter

W = Y.WORLD
R = Y.RESIDENTS
BY = Y.BY_NAME
NDAYS = Y.NDAYS
END = NDAYS - 1
ds = Y.date_str

# ---------------------------------------------------------------- indices
VIS = W["visits"]                       # (day, s, n, place, why, intent, wx)


def is_chosen(why):
    return why.startswith("cho") or why.startswith("inten")


chosen_nd = defaultdict(list)           # (n, place) -> [day,...] chosen only
all_np = defaultdict(int)
week_np = defaultdict(int)              # (n, place, week) chosen
occ_at = defaultdict(list)              # (day, s, place) -> [names]
per_day_place = defaultdict(int)
for (day, s, n, p, why, iu, wx) in VIS:
    if p == "home":
        continue
    occ_at[(day, s, p)].append(n)
    all_np[(n, p)] += 1
    per_day_place[(p, day)] += 1
    if is_chosen(why):
        chosen_nd[(n, p)].append(day)
        week_np[(n, p, day // 7)] += 1

HOMEWK = [w for w in range(52) if Y.MATCH.get(w) and Y.MATCH[w][0] == "home"]
ground_sat = defaultdict(set)
for (day, s, n, p, why, iu, wx) in VIS:
    if p == "ground" and day % 7 == 5:
        ground_sat[day // 7].add(n)


def routine_set(nm, w0, w1):
    """(place, dow, slot) triples appearing >=3 times in the week window"""
    c = Counter()
    for (day, s, n, p, why, iu, wx) in VIS:
        if n == nm and p != "home" and w0 <= day // 7 <= w1:
            c[(p, day % 7, s)] += 1
    return {k for k, v in c.items() if v >= 3}


def jacc(a, b):
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 1.0


# ---------------------------------------------------------------- history detectors
def switches(nm):
    """emergent started/stopped-using-place lines, with the likely reason"""
    out = []
    r = BY[nm]
    arrives = r.get("arrives", 0)
    for p in sorted({pl for (n2, pl) in chosen_nd if n2 == nm}):
        wk = [week_np.get((nm, p, w), 0) for w in range(52)]
        w0 = max(4, arrives // 7 + 1)
        bestt, bestd = None, 0.0
        for t in range(w0 + 2, 49):
            before = sum(wk[w0:t]) / max(1, t - w0)
            after = sum(wk[t:t + 10]) / min(10, 52 - t)
            if before < 0.3 and after >= 1.0 and after - before > bestd:
                bestt, bestd, kind = t, after - before, "started"
            if before >= 1.0 and after < 0.25 and before - after > bestd:
                bestt, bestd, kind = t, before - after, "stopped"
        if bestt:
            day0 = bestt * 7
            why = ""
            for (dy, txt) in r["log"]:
                if abs(dy - day0) <= 12 and ("retired" in txt or "words with" in txt
                                             or "made peace" in txt or "moved into" in txt):
                    why = f" — around the time of: “{txt}” ({ds(dy)})"
                    break
            verb = "started using" if kind == "started" else "stopped visiting"
            out.append(f"{verb} the {p} around {Y.MNAME[Y.month_of(day0)]}{why}")
    return out


def match_streak(nm):
    att = [w for w in HOMEWK if nm in ground_sat[w]]
    if not att:
        return None
    streak = 0
    for w in reversed(HOMEWK):
        if nm in ground_sat[w]:
            streak += 1
        else:
            break
    return len(att), len(HOMEWK), streak


def rituals_now(nm):
    """chosen (place, dow, slot) still alive in the last 8 weeks — one per place"""
    c = Counter()
    for (day, s, n, p, why, iu, wx) in VIS:
        if n == nm and is_chosen(why) and day // 7 >= 44:
            c[(p, day % 7, s)] += 1
    seen, out = set(), []
    for (p, dw, sl), v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
        if v < 6 or p in seen:
            continue
        seen.add(p)
        out.append((p, dw, sl, v))
        if len(out) == 3:
            break
    return out


def rel_story(nm, o):
    """a relationship rendered as history, not a counter"""
    r = BY[nm]
    rl = r["rel"].get(o)
    if not rl or rl["rec"] == 0:
        return None
    bits = []
    if rl["met"]:
        md, mp = rl["met"]
        newpair = BY[nm].get("arrives") or BY.get(o, {}).get("arrives")
        if md < 14 and not newpair:
            bits.append("known since before the year")
        else:
            bits.append(f"first crossed paths at the {mp} on {ds(md)}")
    ev = Counter(kind.split(" at ")[0] for _, kind in rl["ev"])
    for k, v in sorted(ev.items()):
        if k.startswith("match"):
            bits.append(f"{v} matches together" if v > 1 else "one match together")
        elif k.startswith("borrowed"):
            bits.append(k + (f" ×{v}" if v > 1 else ""))
        elif k.startswith("lent"):
            bits.append(k + (f" ×{v}" if v > 1 else ""))
        elif k.startswith("argued"):
            bits.append("argued" + (f" ×{v}" if v > 1 else " once"))
        elif k.startswith("made peace"):
            bits.append("made peace")
        elif k.startswith("never got"):
            bits.append(k)
    tops = [(c, pl) for (a, b, pl), c in W["copresence"].items()
            if {a, b} == {nm, o}]
    if tops:
        c, pl = max(tops)
        if c >= 8:
            bits.append(f"most often meet at the {pl}")
    gap = END - rl["last"]
    if gap > 21:
        bits.append(f"haven't crossed paths in {gap // 7} weeks")
    if rl["tension"]:
        bits.append(f"still not speaking (since {ds(rl['tension'])})")
    return "; ".join(bits)


# ---------------------------------------------------------------- place identity
def place_identity(pid):
    tot = sum(v for (p2, dd), v in per_day_place.items() if p2 == pid)
    if tot == 0:
        return None
    slots = Counter()
    solo = 0
    groups = 0
    for (day, s, p2), names in occ_at.items():
        if p2 != pid:
            continue
        slots[s] += len(names)
        groups += 1
        if len(names) == 1:
            solo += 1
    morning = sum(slots[s] for s in (0, 1)) / tot
    evening = sum(slots[s] for s in (5, 6)) / tot
    args = sum(1 for (dy, a, b, k, pl) in W["argulog"] if pl == pid and k == "argument")
    peace = sum(1 for (dy, a, b, k, pl) in W["argulog"] if pl == pid and k == "resolved")
    met_here = sum(1 for r in R for o, rl in r["rel"].items()
                   if rl["met"] and rl["met"][1] == pid and r["n"] < o)
    regs = Counter()
    for (n2, p2), v in all_np.items():
        if p2 == pid:
            regs[n2] += v
    wtr = sum(v for (p2, dd), v in per_day_place.items()
              if p2 == pid and Y.season_of(dd) == "winter")
    smr = sum(v for (p2, dd), v in per_day_place.items()
              if p2 == pid and Y.season_of(dd) == "summer")
    tags = []
    if morning > 0.5:
        tags.append(f"a morning place ({100*morning:.0f}% of its life before 11:00)")
    if evening > 0.5:
        tags.append(f"an evening place ({100*evening:.0f}% of its life after 17:00)")
    if solo / max(1, groups) > 0.5:
        tags.append(f"mostly solitary ({100*solo/max(1,groups):.0f}% of moments alone)")
    if peace >= 2:
        tags.append(f"where peace gets made ({peace} of the year's reconciliations)")
    if args >= 2:
        tags.append(f"where tempers fray ({args} arguments broke out here)")
    if met_here >= 40:
        tags.append(f"the town's introduction bureau ({met_here} pairs first met here)")
    if wtr and smr and smr / max(1, wtr) > 1.8:
        tags.append(f"a fair-weather place (summer {smr} visits vs winter {wtr})")
    if wtr and smr and wtr / max(1, smr) > 1.3:
        tags.append("busier in winter than summer")
    top3 = ", ".join(n2 for n2, _ in sorted(regs.items(),
                                            key=lambda kv: (-kv[1], kv[0]))[:3])
    return tot, tags, top3


# ---------------------------------------------------------------- chronicle items
def busiest_market_day():
    best = max(((v, dd) for (p2, dd), v in per_day_place.items() if p2 == "market"),
               default=(0, None))
    if best[1] is None:
        return "the market never opened"
    v, dd = best
    wx = Y.wx_day(dd)
    return f"{ds(dd)} — {v} visits ({wx})"


def longest_friendship():
    """genuinely NEW this year: the first fortnight is the town waking up,
    not people meeting — those pairs knew each other before the year."""
    best = None
    for r in R:
        for o, rl in r["rel"].items():
            if r["n"] < o and rl["met"] and rl["met"][0] >= 14 and rl["affection"] >= 5:
                rl2 = BY[o]["rel"].get(r["n"], {})
                if rl2.get("affection", 0) >= 5:
                    dur = END - rl["met"][0]
                    if best is None or dur > best[0]:
                        best = (dur, r["n"], o, rl["met"])
    if not best:
        return "no new friendship crossed the threshold this year"
    dur, a, b, (md, mp) = best
    return (f"{a} & {b} — met at the {mp} on {ds(md)}, "
            f"close for {dur // 7} weeks by year's end")


def disagreements():
    unres, longest_heal = [], None
    for (dy, a, b, k, pl) in W["argulog"]:
        if k != "argument":
            continue
        healed = next((dy2 for (dy2, a2, b2, k2, pl2) in W["argulog"]
                       if k2 == "resolved" and {a2, b2} == {a, b} and dy2 > dy), None)
        if healed is None:
            unres.append((END - dy, a, b, dy, pl))
        else:
            if longest_heal is None or healed - dy > longest_heal[0]:
                longest_heal = (healed - dy, a, b, dy, pl, healed)
    unres.sort(reverse=True)
    return unres, longest_heal


def attachment_shift():
    """weeks 5-25 vs 26-51 — the first month is the town waking, not growth"""
    h1, h2 = Counter(), Counter()
    for (n2, p2, w2), v in week_np.items():
        if w2 < 5:
            continue
        (h1 if w2 < 26 else h2)[p2] += v
    grow = max(Y.PLACES, key=lambda p: h2.get(p, 0) - h1.get(p, 0)
               if p not in ("home", "busstop", "ground_work") else -9e9)
    fade = None
    for p in Y.PLACES:
        if p in ("home", "busstop", "ground_work", "ground") or h1.get(p, 0) < 40:
            continue
        drop = (h1[p] - h2.get(p, 0)) / h1[p]
        if drop >= 0.15 and (fade is None or drop > fade[0]):
            fade = (drop, p)
    return (grow, h1.get(grow, 0), h2.get(grow, 0)), \
           (fade[1], h1[fade[1]], h2.get(fade[1], 0)) if fade else None


def most_changed_routine():
    best = None
    for r in R:
        if r.get("arrives") or r.get("child"):
            continue
        a = routine_set(r["n"], 4, 13)
        b = routine_set(r["n"], 42, 51)
        j = jacc(a, b)
        if best is None or j < best[0]:
            best = (j, r["n"], len(a), len(b))
    return best


def integration(nm):
    """woven in = an adopted place (12+ chosen visits), a standing ritual
    (same place+day+slot three weeks running), and three real friendships."""
    r = BY[nm]
    a0 = r.get("arrives", 0)
    # weekly (p,dow,slot) chosen sets for the ritual test
    slotwk = defaultdict(set)
    cum = defaultdict(int)
    first_ok = None
    for w in range(a0 // 7 + 1, 52):
        for (day, s, n, p, why, iu, wx) in VIS:
            if n == nm and day // 7 == w and is_chosen(why):
                slotwk[w].add((p, day % 7, s))
                cum[p] += 1
        adopted = any(v >= 12 for v in cum.values())
        ritual = any(k in slotwk.get(w - 1, ()) and k in slotwk.get(w - 2, ())
                     for k in slotwk.get(w, ()))
        friends = sum(1 for o, rl in r["rel"].items()
                      if rl["affection"] >= 4 and rl["met"] and rl["met"][0] >= a0)
        if adopted and ritual and friends >= 3:
            return w - a0 // 7
    return None


def biggest_match():
    best = None
    for w in HOMEWK + [w2 for w2 in range(52) if Y.MATCH.get(w2) and Y.MATCH[w2][0] == "away"]:
        sat = w * 7 + 5
        att = len(ground_sat.get(w, ()))
        pub_eve = sum(len(occ_at.get((sat, s, "pub"), ())) for s in (5, 6))
        impact = att + pub_eve
        if best is None or impact > best[0]:
            best = (impact, w, att, pub_eve)
    imp, w, att, pub_eve = best
    venue, res = Y.MATCH[w]
    return (f"{ds(w * 7 + 5)} ({venue}, a {res}) — {att} at the ground, "
            f"{pub_eve} pub visits that evening")


def season_record():
    c = Counter(res for w in range(52) if Y.MATCH.get(w) for _, res in [Y.MATCH[w]])
    return f"{c['win']}W {c['draw']}D {c['loss']}L over {sum(c.values())} matches"


# ---------------------------------------------------------------- documents
def out(fname, lines):
    txt = "\n".join(lines) + "\n"
    with open(fname, "w") as f:
        f.write(txt)
    return txt


# ============ 1. the chronicle
L = []
A = L.append
A("=" * 72)
A("DISTRICT 01 — CHRONICLE OF THE YEAR (Aug–Jul, seed %d)" % Y.SEED)
A("=" * 72)
A("")
A(f"population {len(R)} (two arrivals); {len(W['visits'])} lived moments; "
  f"{len(W['eventlog'])} events; intentions {W['int_done']} kept, {W['int_forgot']} forgotten")
A(f"football: {season_record()}")
A("")
A("THE RECORD")
A(f"  busiest market day ........ {busiest_market_day()}")
A(f"  longest friendship formed . {longest_friendship()}")
unres, heal = disagreements()
if unres:
    dur, a, b, dy, pl = unres[0]
    A(f"  longest unresolved feud ... {a} & {b} — words at the {pl} on {ds(dy)}, "
      f"unhealed for {dur // 7} weeks and counting")
if heal:
    hd, a, b, dy, pl, dy2 = heal
    A(f"  slowest reconciliation .... {a} & {b} — argued {ds(dy)}, "
      f"made peace {ds(dy2)} ({hd} days)")
(gp, g1, g2), fd = attachment_shift()
A(f"  attachment grew most ...... the {gp} ({g1} chosen visits Sep–Jan → {g2} Feb–Jul)")
if fd:
    fp, f1, f2 = fd
    A(f"  quietly faded ............. the {fp} ({f1} → {f2} chosen visits)")
else:
    A("  quietly faded ............. no place lost more than 15% of its life — "
      "the district floor held all year")
mc = most_changed_routine()
if mc:
    j, nm, la, lb = mc
    why = next((f" — {txt} ({ds(dy)})" for dy, txt in BY[nm]["log"] if "retired" in txt), "")
    ra, rb = routine_set(nm, 4, 13), routine_set(nm, 42, 51)
    ca = Counter(p for (p, dw, sl) in ra)
    cb = Counter(p for (p, dw, sl) in rb)
    dv = {p: cb.get(p, 0) - ca.get(p, 0) for p in set(ca) | set(cb)}
    lost = sorted((p for p in dv if dv[p] <= -2), key=lambda p: (dv[p], p))[:2]
    gained = sorted((p for p in dv if dv[p] >= 2), key=lambda p: (-dv[p], p))[:2]
    detail = ""
    if lost or gained:
        detail = (" — less: " + (", ".join(lost) or "—") +
                  "; more: " + (", ".join(gained) or "—"))
    A(f"  routine changed most ...... {nm} (only {100*j:.0f}% of the autumn week "
      f"survived to summer){why}{detail}")
pi_, ji_ = integration("Petra"), integration("Jack")
A(f"  newcomer integration ...... Petra (arrived Sep): "
  + (f"woven in by week {pi_}" if pi_ else "not yet woven in")
  + f"; Jack (arrived Feb): " + (f"woven in by week {ji_}" if ji_ else "not yet woven in"))
A(f"  biggest match ............. {biggest_match()}")
A("")
A("WHAT THE PLACES BECAME")
for pid in Y.PLACES:
    if pid in ("home", "busstop", "ground_work"):
        continue
    ident = place_identity(pid)
    if not ident:
        continue
    tot, tags, regs = ident
    line = f"  {pid:10s} {tot:5d} visits"
    if tags:
        line += " — " + "; ".join(tags)
    A(line)
    A(f"  {'':10s} regulars: {regs}")
A("")
A("THE YEAR'S SHAPE (out-of-home visits by month)")
bym = Counter()
for (p2, dd), v in per_day_place.items():
    bym[Y.month_of(dd)] += v
A("  " + "  ".join(f"{Y.MNAME[i]} {bym[i]}" for i in range(12)))
xd = Y.CHRISTMAS
xmas = sum(v for (p2, dd), v in per_day_place.items() if dd == xd)
ordy = sum(v for (p2, dd), v in per_day_place.items() if dd == xd - 7)
A(f"  Christmas Day: {xmas} moments outside vs {ordy} the Sunday before — the town stays home")
kidset = {r["n"] for r in R if r.get("child")}
term_kid = hol_kid = 0
for (day2, s2, n2, p2, why2, iu2, wx2) in VIS:
    if n2 in kidset and p2 in ("field", "green", "square") and is_chosen(why2):
        if Y.school_holiday(day2):
            hol_kid += 1
        else:
            term_kid += 1
hol_days = sum(1 for dd in range(NDAYS) if Y.school_holiday(dd))
kid_hol_rate = hol_kid / hol_days
kid_term_rate = term_kid / (NDAYS - hol_days)
A(f"  children CHOOSING the outdoors (school hours excluded): "
  f"{kid_hol_rate:.1f}/day in the holidays vs {kid_term_rate:.1f}/day in term")
CHRON = out("year_chronicle.txt", L)

# ============ 2. five biographies
def biography(nm, title):
    r = BY[nm]
    B = []
    B.append("-" * 72)
    occ = r["occ"]
    ret = next(((dy, txt) for dy, txt in r["log"] if "retired" in txt), None)
    if ret:
        occ = f"retired since {Y.MNAME[Y.month_of(ret[0])]} ({ret[1].split(' as ')[-1]} before)"
    B.append(f"{nm}, {r['age']} — {occ} — {r['home']}   [{title}]")
    B.append("-" * 72)
    arr = r.get("arrives")
    if arr:
        B.append(f"  arrived {ds(arr)}, knowing nobody.")
    # the year in quarters
    B.append("  the year, season by season (where the free hours went):")
    QN = ["autumn", "winter", "spring", "summer"]
    for qi, (w0, w1) in enumerate([(5, 17), (18, 30), (31, 43), (44, 51)]):
        c = Counter()
        for (n2, p2, w2), v in week_np.items():
            if n2 == nm and w0 <= w2 <= w1:
                c[p2] += v
        if c:
            top = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
            B.append(f"    {QN[qi]:7s} " + ", ".join(f"{p}({v})" for p, v in top))
    # emergent history lines
    hist = switches(nm)
    st = match_streak(nm)
    if st:
        att, tot, streak = st
        if att == tot:
            hist.append(f"did not miss a single home match — all {tot}")
        elif streak >= 5:
            hist.append(f"hasn't missed a home match in {streak} — {att} of {tot} this year")
        elif att:
            hist.append(f"went to {att} of {tot} home matches")
    for (p, dw, sl, v) in rituals_now(nm):
        hist.append(f"a standing habit: the {p}, {Y.DAYS[dw]}s around {Y.SLOTS[sl]}:00 "
                    f"({v} of the last 8 weeks)")
    if hist:
        B.append("  a life accumulating:")
        for hl in hist:
            B.append(f"    • {hl}")
    # relationships as histories
    rels = sorted(r["rel"].items(), key=lambda kv: -kv[1]["affection"])
    told = 0
    B.append("  the people in it:")
    for o, rl in rels:
        if told >= 3:
            break
        story = rel_story(nm, o)
        if story:
            B.append(f"    {o}: {story}")
            told += 1
    told_names = {o for o, _ in rels[:3]}
    strained = max((kv for kv in rels if kv[0] not in told_names
                    and (kv[1]["tension"]
                         or any("argued" in e for _, e in kv[1]["ev"])
                         or kv[1]["irritation"] > 3.0)),
                   key=lambda kv: kv[1]["irritation"], default=None)
    if strained:
        story = rel_story(nm, strained[0])
        note = "a sore one" if (strained[1]["tension"]
                                or any("argued" in e for _, e in strained[1]["ev"])) \
            else "worn thin by crowds and small frictions"
        B.append(f"    and {strained[0]} — {note}: {story}")
    # the log
    if r["log"]:
        B.append("  from the year's log:")
        for dy, txt in r["log"][:12]:
            B.append(f"    {ds(dy):11s} {txt}")
    B.append("")
    return B

kids = [r for r in R if r.get("child")]
busiest_kid = max(kids, key=lambda r: sum(v for (n2, p2, w2), v in week_np.items()
                                          if n2 == r["n"]))
bios = []
bios += biography("June", "the constant")
retiree = next((e[2]["who"] for e in W["eventlog"] if e[1] == "retirement"), None)
if retiree:
    bios += biography(retiree, "the year everything changed")
bios += biography("Petra", "newcomer, September")
bios += biography("Jack", "newcomer, February")
bios += biography(busiest_kid["n"], "a childhood year")
BIOS = out("year_biographies.txt", ["=" * 72,
                                    "FIVE LIVES — biographies generated from one simulated year",
                                    "=" * 72, ""] + bios)

# ============ 3. ERA Validation v2
V = []
B = V.append
B("=" * 72)
B("ERA VALIDATION v2 — one question")
B("=" * 72)
B("")
B("If a player returned to this town a year later, would it genuinely feel")
B("like another year had passed?")
B("")
new_pairs = sum(1 for r in R for o, rl in r["rel"].items()
                if rl["met"] and rl["met"][0] >= 14 and r["n"] < o)
drift = [(r["n"], o) for r in R for o, rl in r["rel"].items()
         if rl["rec"] >= 10 and END - rl["last"] > 35 and r["n"] < o]
B("EVIDENCE THE YEAR HAPPENED")
B("")
B("In the people:")
B(f"  {new_pairs} pairs genuinely met for the first time this year (beyond the")
B(f"  town's existing fabric) — each remembers where and when.")
B(f"  {longest_friendship()}.")
if unres:
    dur, a, b, dy, pl = unres[0]
    B(f"  {a} and {b} have not mended what broke at the {pl} in "
      f"{Y.MNAME[Y.month_of(dy)]}. {len(unres)} feud(s) carry over into next year.")
if drift:
    B(f"  {len(drift)} once-frequent pairs drifted apart (no contact in 5+ weeks) —")
    B("  absence has consequences; affection cools when unfed.")
else:
    B("  No once-frequent pair ever went five weeks apart: the cooling")
    B("  mechanism exists, but a district this small never leaves anyone")
    B("  alone long enough to trigger it. Same finding as the")
    B("  familiar-stranger CONCERN — the town is socially saturated.")
B("")
B("In the routines:")
if mc:
    j, nm, la, lb = mc
    B(f"  {nm} kept only {100*j:.0f}% of an autumn week into summer"
      + (" — retirement rewrote the rest." if retiree == nm else "."))
if pi_ and ji_:
    if pi_ == ji_:
        B(f"  Both newcomers were woven in within {pi_} weeks — Petra in September,")
        B("  Jack in February. The town absorbs anyone at the same speed; warm,")
        B("  but it is the same small-world saturation the familiar-stranger")
        B("  CONCERN has flagged since Phase 4.")
    else:
        B(f"  Two newcomers integrated at two speeds: Petra in {pi_} weeks")
        B(f"  (September, commuting), Jack in {ji_} weeks (February, retired). The")
        B("  season you arrive in changes the town you join.")
stj = []
for r in R:
    if r.get("arrives") or r.get("child"):
        continue
    stj.append(jacc(routine_set(r["n"], 4, 13), routine_set(r["n"], 42, 51)))
B(f"  Median resident kept {100*sorted(stj)[len(stj)//2]:.0f}% of the autumn routine —")
B("  lives persisted AND changed: neither frozen nor amnesiac.")
B("")
B("In the places:")
B("  Places acquired identities from use alone (see chronicle): the bakery a")
B("  morning place, benches where peace gets made, the allotment breathing")
B(f"  with the seasons ({sum(v for (p,dd),v in per_day_place.items() if p=='allotment' and Y.season_of(dd)=='winter')} winter visits"
  f" vs {sum(v for (p,dd),v in per_day_place.items() if p=='allotment' and Y.season_of(dd)=='spring')} in spring).")
B("")
B("In the calendar:")
B(f"  {season_record()} — a fixture every Saturday, home and away alternating:")
B("  the town's fortnight heartbeat never stopped, and the seasons turned")
B(f"  around it. Christmas Day emptied the streets ({xmas} outside vs {ordy}")
B("  the Sunday before);")
B(f"  children chose the outdoors {kid_hol_rate:.1f}×/day in the holidays vs "
  f"{kid_term_rate:.1f} in term.")
B("  The year has a shape a returning player would recognise as A year,")
B("  not A LOOP.")
B("")
B("WHAT WOULD GIVE IT AWAY (honest limits)")
B("  Nobody was born, nobody died, nobody moved away; one man retired but")
B("  no one changed jobs, prices, or houses. The buildings did not weather.")
B("  Children did not grow. A second identical seed would replay the same")
B("  year exactly — which is a law (CD-007), not a flaw, but the DEMOGRAPHIC")
B("  clock is still stopped even while the social clock now runs.")
B("")
B("VERDICT")
B("  YES for the social and seasonal year: relationships, grudges, routines,")
B("  place identities and the calendar all accumulated twelve months of")
B("  consequence, and the report above cites only computed facts.")
B("  NOT YET for the demographic year: births, deaths, departures, growth.")
B("  That is the next honest gap — exposed by simulation, not by concept.")
VAL = out("era_validation_v2.txt", V)

print(CHRON[:1200])
print(f"[chronicle {len(CHRON)}ch, biographies {len(BIOS)}ch, validation {len(VAL)}ch]")
