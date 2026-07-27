"""
world.historian — history at four levels, rendered from the record.

Resident, household, institution, town. Nothing here is authored: place
identities, personal histories, traditions and the town chronicle are all
detected in the simulation's own logs. The historian never mentions a
place the data didn't define or an event the run didn't produce.
"""
from collections import defaultdict, Counter
from .core import DAYS

SLOTS = ["07", "09", "11", "13", "15", "17", "19"]


def _idx(W):
    """shared indices over the visit record"""
    ix = {}
    VIS = W.state["visits"]
    chosen_nd = defaultdict(list)
    week_np = defaultdict(int)
    occ_at = defaultdict(list)
    per_day_place = defaultdict(int)
    all_np = defaultdict(int)
    for (day, s, n, p, why, iu, wx) in VIS:
        if p == "home":
            continue
        occ_at[(day, s, p)].append(n)
        all_np[(n, p)] += 1
        per_day_place[(p, day)] += 1
        if _is_chosen(why):
            chosen_nd[(n, p)].append(day)
            week_np[(n, p, day // 7)] += 1
    ix.update(chosen_nd=chosen_nd, week_np=week_np, occ_at=occ_at,
              per_day_place=per_day_place, all_np=all_np, VIS=VIS)
    # fixture attendance: presence at any football-capability place on fixture days
    fb = W.football
    ix["homewk"] = []
    ix["ground_sat"] = defaultdict(set)
    if fb:
        vplaces = {pid for pid, pl in W.places.items()
                   if "football" in pl.sat and pl.public}
        ix["homewk"] = [w for w, (opp, ven) in sorted(fb.fixtures.items()) if ven == "home"]
        for (day, s, n, p, why, iu, wx) in VIS:
            if p in vplaces and day % 7 == fb.fixture_dow:
                ix["ground_sat"][day // 7].add(n)
    return ix


def _is_chosen(why):
    return why.startswith("cho") or why.startswith("inten")


def routine_set(W, ix, nm, w0, w1):
    c = Counter()
    for (day, s, n, p, why, iu, wx) in ix["VIS"]:
        if n == nm and p != "home" and w0 <= day // 7 <= w1:
            c[(p, day % 7, s)] += 1
    return {k for k, v in c.items() if v >= 3}


def jacc(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 1.0


def switches(W, ix, nm):
    out = []
    r = W.by_name[nm]
    arrives = r.get("arrives", 0)
    wk_np = ix["week_np"]
    weeks = W.clock.weeks
    for p in sorted({pl for (n2, pl) in ix["chosen_nd"] if n2 == nm}):
        wk = [wk_np.get((nm, p, w), 0) for w in range(weeks)]
        w0 = max(4, arrives // 7 + 1)
        bestt, bestd, kind = None, 0.0, None
        for t in range(w0 + 2, weeks - 3):
            before = sum(wk[w0:t]) / max(1, t - w0)
            after = sum(wk[t:t + 10]) / min(10, weeks - t)
            if before < 0.3 and after >= 1.0 and after - before > bestd:
                bestt, bestd, kind = t, after - before, "started"
            if before >= 1.0 and after < 0.25 and before - after > bestd:
                bestt, bestd, kind = t, before - after, "stopped"
        if bestt:
            day0 = bestt * 7
            why = ""
            for (dy, txt) in r["log"]:
                if abs(dy - day0) <= 12 and ("retired" in txt or "words with" in txt
                                             or "made peace" in txt or "moved into" in txt
                                             or "joined" in txt):
                    why = f" — around the time of: “{txt}” ({W.clock.date_str(dy)})"
                    break
            verb = "started using" if kind == "started" else "stopped visiting"
            out.append(f"{verb} the {p} around {W.clock.mname[W.clock.month_of(day0)]}{why}")
    return out


def match_streak(W, ix, nm):
    hw = ix["homewk"]
    if not hw:
        return None
    att = [w for w in hw if nm in ix["ground_sat"][w]]
    if not att:
        return None
    streak = 0
    for w in reversed(hw):
        if nm in ix["ground_sat"][w]:
            streak += 1
        else:
            break
    return len(att), len(hw), streak


def rituals_now(W, ix, nm):
    weeks = W.clock.weeks
    c = Counter()
    for (day, s, n, p, why, iu, wx) in ix["VIS"]:
        if n == nm and _is_chosen(why) and day // 7 >= weeks - 8:
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


def rel_story(W, nm, o):
    END = W.clock.ndays - 1
    r = W.by_name[nm]
    rl = r["rel"].get(o)
    if not rl or rl["rec"] == 0:
        return None
    bits = []
    if rl["met"]:
        md, mp = rl["met"]
        newpair = W.by_name[nm].get("arrives") or W.by_name.get(o, {}).get("arrives")
        if md < 14 and not newpair:
            bits.append("known since before the year")
        else:
            bits.append(f"first crossed paths at the {mp} on {W.clock.date_str(md)}")
    ev = Counter(kind.split(" at ")[0] for _, kind in rl["ev"])
    for k, v in sorted(ev.items()):
        if k.startswith("match"):
            bits.append(f"{v} matches together" if v > 1 else "one match together")
        elif k.startswith("argued"):
            bits.append("argued" + (f" ×{v}" if v > 1 else " once"))
        elif k.startswith("made peace"):
            bits.append("made peace")
        else:
            bits.append(k + (f" ×{v}" if v > 1 else ""))
    tops = [(c, pl) for (a, b, pl), c in W.state["copresence"].items()
            if {a, b} == {nm, o}]
    if tops:
        c, pl = max(tops)
        if c >= 8:
            bits.append(f"most often meet at the {pl}")
    gap = END - rl["last"]
    if gap > 21:
        bits.append(f"haven't crossed paths in {gap // 7} weeks")
    if rl["tension"]:
        bits.append(f"still not speaking (since {W.clock.date_str(rl['tension'])})")
    return "; ".join(bits)


def place_identity(W, ix, pid):
    per_day_place = ix["per_day_place"]
    tot = sum(v for (p2, dd), v in per_day_place.items() if p2 == pid)
    if tot == 0:
        return None
    slots = Counter()
    solo = groups = 0
    for (day, s, p2), names in ix["occ_at"].items():
        if p2 != pid:
            continue
        slots[s] += len(names)
        groups += 1
        if len(names) == 1:
            solo += 1
    morning = sum(slots[s] for s in (0, 1)) / tot
    evening = sum(slots[s] for s in (5, 6)) / tot
    args = sum(1 for (dy, a, b, k, pl) in W.state["argulog"] if pl == pid and k == "argument")
    peace = sum(1 for (dy, a, b, k, pl) in W.state["argulog"] if pl == pid and k == "resolved")
    met_here = sum(1 for r in W.residents for o, rl in r["rel"].items()
                   if rl["met"] and rl["met"][1] == pid and r["n"] < o)
    regs = Counter()
    for (n2, p2), v in ix["all_np"].items():
        if p2 == pid:
            regs[n2] += v
    sea = W.clock.season_of
    wtr = sum(v for (p2, dd), v in per_day_place.items() if p2 == pid and sea(dd) == "winter")
    smr = sum(v for (p2, dd), v in per_day_place.items() if p2 == pid and sea(dd) == "summer")
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
    top3 = ", ".join(n2 for n2, _ in sorted(regs.items(), key=lambda kv: (-kv[1], kv[0]))[:3])
    return tot, tags, top3


# ---------------------------------------------------------------- chronicle
def write_all(W):
    ix = _idx(W)
    clock, ds = W.clock, W.clock.date_str
    END = clock.ndays - 1
    weeks = clock.weeks
    week_np = ix["week_np"]
    per_day_place = ix["per_day_place"]

    def public_place(pid):
        pl = W.places[pid]
        return pl.public and pl.sat

    # records
    def longest_friendship():
        best = None
        for r in W.residents:
            for o, rl in r["rel"].items():
                if r["n"] < o and rl["met"] and rl["met"][0] >= 14 and rl["affection"] >= 5:
                    rl2 = W.by_name[o]["rel"].get(r["n"], {})
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
        for (dy, a, b, k, pl) in W.state["argulog"]:
            if k != "argument":
                continue
            healed = next((dy2 for (dy2, a2, b2, k2, pl2) in W.state["argulog"]
                           if k2 == "resolved" and {a2, b2} == {a, b} and dy2 > dy), None)
            if healed is None:
                unres.append((END - dy, a, b, dy, pl))
            elif longest_heal is None or healed - dy > longest_heal[0]:
                longest_heal = (healed - dy, a, b, dy, pl, healed)
        unres.sort(reverse=True)
        return unres, longest_heal

    def attachment_shift():
        h1, h2 = Counter(), Counter()
        half = weeks // 2
        for (n2, p2, w2), v in week_np.items():
            if w2 < 5:
                continue
            (h1 if w2 < half else h2)[p2] += v
        grow = max((p for p in W.places if public_place(p)),
                   key=lambda p: h2.get(p, 0) - h1.get(p, 0), default=None)
        fade = None
        for p in W.places:
            if not public_place(p) or W.places[p].matchday_only or h1.get(p, 0) < 40:
                continue
            drop = (h1[p] - h2.get(p, 0)) / h1[p]
            if drop >= 0.15 and (fade is None or drop > fade[0]):
                fade = (drop, p)
        return (grow, h1.get(grow, 0), h2.get(grow, 0)), \
               (fade[1], h1[fade[1]], h2.get(fade[1], 0)) if fade else None

    def most_changed():
        best = None
        for r in W.residents:
            if r.get("arrives") or r.get("child"):
                continue
            a = routine_set(W, ix, r["n"], 4, 13)
            b = routine_set(W, ix, r["n"], weeks - 10, weeks - 1)
            j = jacc(a, b)
            if best is None or j < best[0]:
                best = (j, r["n"], a, b)
        return best

    def integration(nm):
        r = W.by_name[nm]
        a0 = r.get("arrives", 0)
        slotwk = defaultdict(set)
        cum = defaultdict(int)
        for w in range(a0 // 7 + 1, weeks - 2):
            for (day, s, n, p, why, iu, wx) in ix["VIS"]:
                if n == nm and day // 7 == w and _is_chosen(why):
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
        fb = W.football
        if not fb:
            return None
        best = None
        for w, res in sorted(fb.results.items()):
            sat = res["day"]
            att = len(ix["ground_sat"].get(w, ()))
            pub_eve = sum(len(names) for (day2, s2, p2), names in ix["occ_at"].items()
                          if day2 == sat and s2 >= 5 and "drink" in W.places[p2].sat)
            impact = att + pub_eve
            if best is None or impact > best[0]:
                best = (impact, w, att, pub_eve, res)
        imp, w, att, pub_eve, res = best
        gf, ga = res["score"]
        return (f"{ds(res['day'])} ({res['venue']} v {res['opp']}, "
                f"{'a ' + res['result'] if res['result'] != 'draw' else 'a draw'} {gf}–{ga}) — "
                f"{att} at the ground, {pub_eve} pub visits that evening")

    L = []
    A = L.append
    A("=" * 72)
    A(f"{W.dd['name'].upper()} — CHRONICLE OF THE YEAR (seed {W.dd['seed']})")
    A("=" * 72)
    A("")
    st = W.state
    A(f"population {len(W.residents)}; {len(st['visits'])} lived moments; "
      f"{len(st['eventlog'])} events; intentions {st['int_done']} kept, "
      f"{st['int_forgot']} forgotten")
    if W.football:
        fb = W.football
        A(f"football: {fb.season_record()} — positions: autumn series "
          f"{fb.position(0)}, spring series {fb.position(1)}; balance {fb.balance}")
    A("")
    A("THE RECORD")
    mkt = max(((v, dd_, p2) for (p2, dd_), v in per_day_place.items()
               if "errand" in W.places[p2].sat and W.places[p2].days is not None),
              default=(0, None, None))
    if mkt[1] is not None:
        A(f"  busiest {mkt[2]} day ...... {ds(mkt[1])} — {mkt[0]} visits ({W.weather.at(mkt[1])})")
    A(f"  longest friendship formed . {longest_friendship()}")
    unres, heal = disagreements()
    if unres:
        dur, a, b, dy, pl = unres[0]
        A(f"  longest unresolved feud ... {a} & {b} — words at the {pl} on {ds(dy)}, "
          f"unhealed for {dur // 7} weeks and counting")
    if heal:
        hd, a, b, dy, pl, dy2 = heal
        A(f"  slowest reconciliation .... {a} & {b} — argued {ds(dy)}, made peace {ds(dy2)} ({hd} days)")
    (gp, g1, g2), fd = attachment_shift()
    A(f"  attachment grew most ...... the {gp} ({g1} chosen visits in the first half → {g2} in the second)")
    if fd:
        A(f"  quietly faded ............. the {fd[0]} ({fd[1]} → {fd[2]} chosen visits)")
    else:
        A("  quietly faded ............. no place lost more than 15% of its life — the district floor held")
    mc = most_changed()
    if mc:
        j, nm, ra, rb = mc
        ca = Counter(p for (p, dw, sl) in ra)
        cb = Counter(p for (p, dw, sl) in rb)
        dv = {p: cb.get(p, 0) - ca.get(p, 0) for p in set(ca) | set(cb)}
        lost = sorted((p for p in dv if dv[p] <= -2), key=lambda p: (dv[p], p))[:2]
        gained = sorted((p for p in dv if dv[p] >= 2), key=lambda p: (-dv[p], p))[:2]
        why = next((f" — {txt} ({ds(dy)})" for dy, txt in W.by_name[nm]["log"] if "retired" in txt), "")
        det = (" — less: " + (", ".join(lost) or "—") + "; more: " + (", ".join(gained) or "—")) \
            if (lost or gained) else ""
        A(f"  routine changed most ...... {nm} (only {100*j:.0f}% of the autumn week survived){why}{det}")
    intg = [(nc["n"], integration(nc["n"])) for nc in W.dd.get("newcomers", [])]
    if intg:
        A("  newcomer integration ...... " + "; ".join(
            f"{n} ({ds(W.by_name[n]['arrives'])}): " +
            (f"woven in by week {v}" if v else "not yet woven in") for n, v in intg))
    bm = biggest_match()
    if bm:
        A(f"  biggest match ............. {bm}")
    A("")
    A("WHAT THE PLACES BECAME")
    for pid in W.places:
        if not public_place(pid):
            continue
        ident = place_identity(W, ix, pid)
        if not ident:
            continue
        tot, tags, regs = ident
        A(f"  {pid:10s} {tot:5d} visits" + ((" — " + "; ".join(tags)) if tags else ""))
        A(f"  {'':10s} regulars: {regs}")
    A("")
    A("THE YEAR'S SHAPE (out-of-home visits by month)")
    bym = Counter()
    for (p2, dd_), v in per_day_place.items():
        bym[clock.month_of(dd_)] += v
    A("  " + "  ".join(f"{clock.mname[i]} {bym[i]}" for i in range(12)))
    fam = clock.family_day
    xmas = sum(v for (p2, dd_), v in per_day_place.items() if dd_ == fam)
    ordy = sum(v for (p2, dd_), v in per_day_place.items() if dd_ == fam - 7)
    A(f"  the family day: {xmas} moments outside vs {ordy} a week before — the town stays home")
    kidset = {r["n"] for r in W.residents if r.get("child")}
    outp = {pid for pid, pl in W.places.items()
            if "play" in pl.sat or "outdoors" in pl.sat}
    term_kid = hol_kid = 0
    for (day2, s2, n2, p2, why2, iu2, wx2) in ix["VIS"]:
        if n2 in kidset and p2 in outp and _is_chosen(why2):
            if clock.school_holiday(day2):
                hol_kid += 1
            else:
                term_kid += 1
    hol_days = sum(1 for dd_ in range(clock.ndays) if clock.school_holiday(dd_))
    khr = hol_kid / max(1, hol_days)
    ktr = term_kid / max(1, clock.ndays - hol_days)
    A(f"  children choosing the outdoors: {khr:.1f}/day in the school holidays vs {ktr:.1f}/day in term")
    A("")
    # ---------------- multi-scale history
    A("=" * 72)
    A("HISTORY AT FOUR LEVELS")
    A("=" * 72)
    A("")
    A("TOWN")
    for (dy, txt) in W.hist.town_log:
        A(f"  {ds(dy):11s} {txt}")
    if W.football:
        srs = [x for x in W.football.history if "series" in x[1] or "CHAMPIONS" in x[1]]
        for (dy, txt) in srs:
            A(f"  {ds(dy):11s} the club {txt}")
    A("")
    A("INSTITUTIONS")
    for iid, inst in W.insts.items():
        hist = inst.history
        if inst.kind == "football_club" and W.football:
            hist = sorted(hist + W.football.history)
        if not hist and not inst.members and not inst.staff:
            continue
        A(f"  {inst.name} ({inst.kind}) — staff {len(inst.staff)}, members {len(inst.members)}")
        for (dy, txt) in hist[:8]:
            A(f"     {ds(dy):11s} {txt}")
    A("")
    A("HOUSEHOLDS (the five most eventful)")
    hhs = sorted(W.households.values(), key=lambda hh: (-len(hh.history), str(hh.id)))[:5]
    for hh in hhs:
        A(f"  {hh.plot} — {', '.join(hh.members)} (balance {hh.balance:.0f})")
        for (dy, txt) in hh.history[:6]:
            A(f"     {ds(dy):11s} {txt}")
    with open((W.dd["id"] + "_chronicle.txt"), "w") as fout:
        fout.write("\n".join(L) + "\n")

    # ---------------- biographies
    write_biographies(W, ix)
    return L


def write_biographies(W, ix):
    clock, ds = W.clock, W.clock.date_str

    def biography(nm, title):
        r = W.by_name[nm]
        B = []
        B.append("-" * 72)
        occ = r["occ"]
        ret = next(((dy, txt) for dy, txt in r["log"] if "retired" in txt), None)
        if ret:
            occ = f"retired since {clock.mname[clock.month_of(ret[0])]}"
        B.append(f"{nm}, {r['age']} — {occ} — {r['home']}   [{title}]")
        B.append("-" * 72)
        if r.get("arrives"):
            B.append(f"  arrived {ds(r['arrives'])}, knowing nobody.")
        B.append("  the year, season by season (where the free hours went):")
        weeks = clock.weeks
        q = max(1, (weeks - 4) // 4)
        QN = ["first quarter", "second", "third", "fourth"]
        for qi in range(4):
            w0, w1 = 4 + qi * q, min(weeks - 1, 4 + (qi + 1) * q - 1)
            c = Counter()
            for (n2, p2, w2), v in ix["week_np"].items():
                if n2 == nm and w0 <= w2 <= w1:
                    c[p2] += v
            if c:
                top = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
                B.append(f"    {QN[qi]:14s} " + ", ".join(f"{p}({v})" for p, v in top))
        hist = switches(W, ix, nm)
        stk = match_streak(W, ix, nm)
        if stk:
            att, tot, streak = stk
            if att == tot:
                hist.append(f"did not miss a single home match — all {tot}")
            elif streak >= 5:
                hist.append(f"hasn't missed a home match in {streak} — {att} of {tot} this year")
            elif att:
                hist.append(f"went to {att} of {tot} home matches")
        for (p, dw, sl, v) in rituals_now(W, ix, nm):
            hist.append(f"a standing habit: the {p}, {DAYS[dw]}s around {SLOTS[sl]}:00 "
                        f"({v} of the last 8 weeks)")
        for iid, inst in W.insts.items():
            if nm in inst.members and inst.members[nm] > 0:
                hist.append(f"joined {inst.name} ({ds(inst.members[nm])})")
        if hist:
            B.append("  a life accumulating:")
            for hl in hist:
                B.append(f"    • {hl}")
        rels = sorted(r["rel"].items(), key=lambda kv: -kv[1]["affection"])
        B.append("  the people in it:")
        told = 0
        for o, rl in rels:
            if told >= 3:
                break
            story = rel_story(W, nm, o)
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
            note = "a sore one" if (strained[1]["tension"]
                                    or any("argued" in e for _, e in strained[1]["ev"])) \
                else "worn thin by crowds and small frictions"
            B.append(f"    and {strained[0]} — {note}: {rel_story(W, nm, strained[0])}")
        if r["log"]:
            B.append("  from the year's log:")
            for dy, txt in r["log"][:12]:
                B.append(f"    {ds(dy):11s} {txt}")
        B.append("")
        return B

    picks = []
    canon = list(W.dd.get("canon", {}))
    if canon:
        picks.append((canon[0], "the constant"))
    retiree = next((e[2]["who"] for e in W.state["eventlog"] if e[1] == "retirement"), None)
    if retiree:
        picks.append((retiree, "the year everything changed"))
    for nc in W.dd.get("newcomers", []):
        picks.append((nc["n"], f"newcomer, {W.clock.mname[W.clock.month_of(nc['arrives'])]}"))
    kids = [r for r in W.residents if r.get("child")]
    if kids and len(picks) < 5:
        busiest = max(kids, key=lambda r: (sum(v for (n2, p2, w2), v in ix["week_np"].items()
                                               if n2 == r["n"]), r["n"]))
        picks.append((busiest["n"], "a childhood year"))
    while len(picks) < 5:
        chosen_names = {n for n, _ in picks}
        rest = [r for r in W.residents if r["n"] not in chosen_names and not r.get("child")]
        if not rest:
            break
        ev = max(rest, key=lambda r: (len(r["log"]), r["n"]))
        picks.append((ev["n"], "an eventful year"))
    bios = ["=" * 72,
            "FIVE LIVES — biographies generated from one simulated year",
            "=" * 72, ""]
    for nm, title in picks[:5]:
        bios += biography(nm, title)
    with open((W.dd["id"] + "_biographies.txt"), "w") as fout:
        fout.write("\n".join(bios) + "\n")
