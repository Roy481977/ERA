"""
world.behaviour — the day loop, capability-driven.

This module contains ZERO place identities, ZERO resident names and ZERO
district knowledge. It sees: places with capabilities and hours,
institutions with rosters, households with possessions and money, a
football world it can query, and residents with needs, memories and
intentions. District 01 is somewhere in the data; District 02 would look
exactly the same from here.

Ported from year.py with behaviour preserved wherever a capability could
express the same rule; every divergence is a generalisation, not a tune.
"""
import math
from collections import defaultdict
from .people import NEEDS, GROW, rel, pmem, add_intent

# an intention kind targets a capability; resolution = strongest open provider
CAP_INTENTS = {"buy", "repair", "prep"}
PROVIDER_MIN = 1.0          # incidental stockists don't satisfy a purposeful trip


def provider(world, cap, open_now):
    best, bestv = None, PROVIDER_MIN - 1e-9
    for pid in sorted(open_now):
        st = world.places[pid].sat.get(cap, 0.0)
        if st > bestv:
            best, bestv = pid, st
    return best


def dist(a, b):
    if a is None or b is None:
        return 0.0
    return math.hypot(a[0] - b[0], a[1] - b[1])


def run(world):
    W = world
    rng, clock, wxw, fb = W.rng, W.clock, W.weather, W.football
    h, f = rng.h, rng.f
    R, BY = W.residents, W.by_name
    NS = 7
    state = W.state = {"visits": [], "traces": [], "copresence": defaultdict(int),
                       "argulog": [], "eventlog": [], "occ": defaultdict(int),
                       "int_done": 0, "int_forgot": 0, "famday": set()}
    hist = W.hist
    place_inst = {}                                  # place -> auto-member institution
    for inst in W.insts.values():
        if inst.auto_member:
            place_inst[inst.auto_member["place"]] = inst

    def active(r, day):
        return day >= r.get("arrives", -1)

    def matchday_open(pid, w):
        if not W.places[pid].matchday_only:
            return True
        fx = fb.fixture(w) if fb else None
        return bool(fx and fx[1] == "home")

    def anchored(r, d, s, day):
        if r["ill_until"] >= day:
            return None, None
        if day in clock.holidays:
            return None, None
        if r.get("term_bound") and clock.school_holiday(day):
            return None, None
        for (dayf, slots, place) in r["anchors"]:
            if (dayf is None or d in dayf) and s in slots:
                if not matchday_open(place, day // 7):
                    continue
                return place, "work/school"
        if r["pressure_until"] >= day and s == 4 and r["anchors"] and not r.get("child"):
            return r["anchors"][0][2], "staying late (pressure)"
        return None, None

    events = list(W.events)
    for day in range(clock.ndays):
        w, d = divmod(day, 7)
        wx = wxw.at(day)
        sn = clock.season_of(day)
        fx = fb.fixture(w) if fb else None
        # ---- events fire
        while events and events[0][0] == day:
            _, kind, pay = events.pop(0)
            state["eventlog"].append((day, kind, dict(pay)))
            if kind == "illness":
                v = BY[pay["who"]]
                v["ill_until"] = day + pay["days"]
                v["log"].append((day, f"ill for {pay['days']} days"))
            elif kind == "pressure":
                v = BY[pay["who"]]
                v["pressure_until"] = day + pay["days"]
                v["log"].append((day, "a hard week at work"))
            elif kind == "household":
                v = BY[pay["who"]]
                add_intent(v, "repair", "repair", 3.2, day, day + 6, pay["what"])
                v["log"].append((day, f"household problem: {pay['what']}"))
                hh = W.households[v["hh"]]
                hh.upkeep.append(pay["what"])
                hh.note(day, f"problem: {pay['what']}")
            elif kind == "borrow":
                a, b = BY[pay["who"]], BY[pay["lender"]]
                if active(a, day) and active(b, day):
                    hb = W.households.get(b["hh"])
                    item = pay["item"]
                    if hb and hb.poss:
                        item = hb.poss[h("bitem", day) % len(hb.poss)]
                    add_intent(a, "return", pay["lender"], 2.4, day, day + 7, item)
                    rel(a, b["n"])["obligation"] += 1.0
                    rel(a, b["n"])["ev"].append((day, "borrowed " + item))
                    rel(b, a["n"])["ev"].append((day, "lent " + item))
                    a["log"].append((day, f"borrowed the {item} from {b['n']}"))
                    W.households[a["hh"]].note(day, f"borrowed the {item} from the {b['n']} household")
            elif kind == "invitation":
                a = BY[pay["who"]]
                best = sorted(((rl["affection"], o) for o, rl in a["rel"].items()
                               if rl["rec"] >= 4), reverse=True)[:1]
                if best:
                    o = best[0][1]
                    add_intent(a, "visit", o, 2.2, day, day + 5)
                    a["log"].append((day, f"means to call on {o}"))
            elif kind == "arrival":
                v = BY[pay["who"]]
                v["log"].append((day, f"moved into {v['home']} — knows nobody"))
                W.households[v["hh"]].note(day, "moved in — new to the town")
                hist.town(day, f"{v['n']} moved into {v['home']}")
            elif kind == "retirement":
                v = BY[pay["who"]]
                occ_d = W.dd["occupations"].get(v["occ"], {})
                iid = occ_d.get("institution")
                if iid and iid in W.insts:
                    W.insts[iid].retire(day, v["n"])
                v["occ"] = "retired"
                v["anchors"] = []
                v["log"].append((day, f"retired — last shift as {pay['was']}"))
                W.households[v["hh"]].note(day, f"{v['n']} retired")
                hist.town(day, f"{v['n']} retired ({pay['was']})")
        # birthdays
        for r in R:
            if active(r, day) and r["bday"] == day and not r.get("child"):
                r["log"].append((day, "birthday"))
                W.households[r["hh"]].note(day, f"{r['n']}'s birthday")
                invited = sorted(((rl["affection"], o) for o, rl in r["rel"].items()
                                  if rl["rec"] >= 5), reverse=True)[:3]
                for _, o in invited:
                    add_intent(BY[o], "celebrate", r["n"], 3.0, day, day + 1)
        # matchday mood — residents RESPOND to the club's fixture
        if fx and day % 7 == fb.fixture_dow:
            opp, venue = fx
            for r in R:
                if active(r, day):
                    r["needs"]["football"] += 5.5 * r["tr"]["foot"] * (1.0 if venue == "home" else 0.45)
        # holidays fill the houses
        if day in clock.holidays:
            for r in R:
                if active(r, day):
                    r["needs"]["family"] += 4.0 if day in (clock.family_day, clock.family_day + 1) else 1.2
        # ---- needs grow, intents form
        for r in R:
            if not active(r, day):
                continue
            for n in NEEDS:
                g = GROW[n]
                if n == "play" and not r.get("child"):
                    g *= 0.25
                if n == "play" and r.get("child") and clock.school_holiday(day):
                    g *= 1.5
                r["needs"][n] += g * (0.8 + f("g", r["n"], day, n) / 2.5)
            if r["needs"]["bread"] > 2.6:
                add_intent(r, "buy", "bread", 2.0 + r["needs"]["bread"] * 0.2, day, day + 2)
            if not r.get("child") and r["tr"]["soc"] > 0.55:
                lonely = [o for o, rl in r["rel"].items()
                          if rl["affection"] >= 2.5 and day - rl["last"] > 9]
                if lonely and f("visit", r["n"], day) > 0.6:
                    add_intent(r, "visit", lonely[h("vw", r["n"], day) % len(lonely)],
                               1.8, day, day + 6)
            if d == 4 and r["tr"]["foot"] > 0.6 and fx and fx[1] == "home":
                add_intent(r, "prep", "errand", 1.6, day, day + 1, "matchday shop")
            if wx != "rain" and not r.get("child") and f("wash", r["n"], day) > 0.45:
                state["traces"].append((day, r["n"], "washing out/in"))
            if d == 1:
                state["traces"].append((day, r["n"], "bin out"))

        # ---- whereabouts guesses + social shortlist
        guess = {}
        for r in R:
            g = {}
            for (pl, dd_, ss), c in r["habit"].items():
                if dd_ == d and (ss not in g or c > g[ss][0]):
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
                        for pid, pl in W.places.items():
                            if not pl.public or not pl.sat:
                                continue
                            if pl.adults_only and r.get("child"):
                                continue
                            if day in clock.holidays and pl.closes_holidays:
                                continue
                            if not matchday_open(pid, w):
                                continue
                            if not pl.open_at(d, s):
                                continue
                            open_now[pid] = pl
                        for it in sorted(r["intents"], key=lambda i: -i["prio"]):
                            if it["state"] != "open":
                                continue
                            tgt = it["target"]
                            if it["kind"] in CAP_INTENTS:
                                pv = provider(W, tgt, open_now)
                                if pv:
                                    place, why, intent_used = pv, f"intention: {it['kind']} ({it['note'] or tgt})", it
                                    break
                            else:                    # visit / return / celebrate a person
                                o = BY.get(tgt)
                                if o and active(o, day):
                                    gp = guess.get(tgt, {}).get(s)
                                    if it["kind"] == "celebrate":
                                        gp = provider(W, "celebration", open_now) or gp
                                    if gp and gp in open_now:
                                        place, why, intent_used = gp, f"intention: {it['kind']} {tgt}", it
                                        break
                        if place is None:
                            for pid, pl in open_now.items():
                                v = sum(r["needs"].get(n, 0) * st for n, st in pl.sat.items())
                                v *= W.season_profiles.get(pl.season_profile, {}).get(sn, 1.0)
                                v *= (1.5 if s >= 5 and "drink" in pl.sat else 1.0)
                                v -= dist(W.plot_loc.get(r["home"]), pl.loc) / (55.0 * r["tr"]["range"])
                                v += min(r["habit"].get((pid, d, s), 0), 8) * 0.5 * r["tr"]["rout"]
                                if wx == "rain" and not pl.cover:
                                    v -= 2.6
                                if wx == "wind" and not pl.cover:
                                    v -= 0.7
                                if wxw.dark(day, s) and not pl.cover:
                                    v -= 1.6
                                m = pmem(r, pid)
                                if m["sore_until"] >= day:
                                    v -= 2.0
                                v += min(m["warm"], 3) * 0.25
                                pull = 0.0
                                for o, rl in r["_top"]:
                                    if guess.get(o, {}).get(s) == pid:
                                        pull += -1.8 if rl["tension"] else 0.5 * r["tr"]["soc"]
                                v += max(-3.6, min(pull, 1.2))
                                v += (f("j", r["n"], day, s, pid) - 0.5) * 0.8
                                if v > bestv:
                                    best, bestv = pid, v
                            place, why = best, ("chose it" if best != "home" else None)
                # ---- commit
                r["cur"] = place
                if place != "home":
                    pl = W.places[place]
                    for n, st in pl.sat.items():
                        if n in r["needs"]:
                            r["needs"][n] = max(0.0, r["needs"][n] - st * 1.4)
                    if "football" in pl.sat and ("season ticket" in r.get("poss", [])
                                                 or r["tr"]["foot"] > 0.55):
                        state["traces"].append((day, r["n"], "scarf on the rail"))
                    r["habit"][(place, d, s)] = r["habit"].get((place, d, s), 0) + 1
                    state["occ"][(place, s)] += 1
                    m = pmem(r, place)
                    m["uses"] += 1
                    m["last"] = day
                    present[place].append(r["n"])
                    inst = place_inst.get(place)
                    if inst and m["uses"] == inst.auto_member["uses"] \
                            and r["n"] not in inst.members:
                        inst.join(day, r["n"])
                        r["log"].append((day, f"joined {inst.name}"))
                    # commerce: a small spend against the household purse
                    if any(c in pl.sat for c in ("bread", "food", "drink", "errand")):
                        W.households[r["hh"]].balance -= 0.8
                else:
                    r["needs"]["rest"] = max(0, r["needs"]["rest"] - 1.2)
                    r["needs"]["family"] = max(0, r["needs"]["family"] - 0.8)
                state["visits"].append((day, s, r["n"], place,
                                        why or "", intent_used is not None, wx))
                if intent_used is not None:
                    intent_used["state"] = "done"
                    intent_used["done"] = day
                    state["int_done"] += 1
                    if intent_used["kind"] == "repair":
                        hh = W.households[r["hh"]]
                        if intent_used["note"] in hh.upkeep:
                            hh.upkeep.remove(intent_used["note"])
                            hh.note(day, f"fixed: {intent_used['note']}")
                    if intent_used["kind"] == "return":
                        o = BY[intent_used["target"]]
                        rel(r, o["n"])["obligation"] = 0.0
                        rel(o, r["n"])["trust"] += 1.0
                        rel(r, o["n"])["trust"] += 0.5
                        rel(r, o["n"])["ev"].append((day, "returned " + intent_used["note"]))
                        r["log"].append((day, f"returned the {intent_used['note']} to {o['n']}"))
            # ---- co-presence -> relationships
            for pid, names in present.items():
                pl = W.places[pid]
                quiet = pl.quiet
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        a, b = BY[names[i]], BY[names[j]]
                        key = (names[i], names[j], day)
                        if key in state["famday"]:
                            continue
                        state["famday"].add(key)
                        ra, rb = rel(a, b["n"]), rel(b, a["n"])
                        if ra["met"] is None:
                            ra["met"] = (day, pid)
                            rb["met"] = (day, pid)
                        if "football" in pl.sat:
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
                            ra["tension"] = rb["tension"] = 0
                            ra["comfort"] += 1.0
                            rb["comfort"] += 1.0
                            ra["ev"].append((day, "made peace at the " + pid))
                            rb["ev"].append((day, "made peace at the " + pid))
                            a["log"].append((day, f"made peace with {b['n']} at the {pid}"))
                            state["argulog"].append((day, a["n"], b["n"], "resolved", pid))
                        state["copresence"][(names[i], names[j], pid)] += 1
                for nm in names:
                    m = pmem(BY[nm], pid)
                    for other in names:
                        if other != nm:
                            m["assoc"][other] += 1
                # a visit intent landing at someone's home would be hosted —
                # households count their visitors via co-presence at the plot
        # ---- arguments pick their pair at day end
        for (dy, kind, pay) in list(state["eventlog"]):
            if kind == "argument" and dy == day and "done" not in pay:
                pay["done"] = True
                cands = [(k, v) for k, v in state["copresence"].items() if v >= 4]
                if cands:
                    (a, b, pl), _ = cands[h("argpick", pay["seed"]) % len(cands)]
                    ra, rb = rel(BY[a], b), rel(BY[b], a)
                    ra["tension"] = rb["tension"] = day
                    ra["irritation"] += 1.2
                    rb["irritation"] += 1.2
                    ra["ev"].append((day, "argued at the " + pl))
                    rb["ev"].append((day, "argued at the " + pl))
                    pmem(BY[a], pl)["sore_until"] = day + 6
                    pmem(BY[b], pl)["sore_until"] = day + 6
                    BY[a]["log"].append((day, f"words with {b} at the {pl}"))
                    BY[b]["log"].append((day, f"words with {a} at the {pl}"))
                    state["argulog"].append((day, a, b, "argument", pl))
        # ---- the match is played (independently); the town reacts
        if fx and day % 7 == fb.fixture_dow:
            opp, venue = fx
            att = 0
            if venue == "home":
                venue_places = [pid for pid, pl in W.places.items() if "football" in pl.sat and pl.public]
                att = len({n for (dy2, s2, n, p2, w2, i2, x2) in state["visits"]
                           if dy2 == day and p2 in venue_places})
            res = fb.play_week(w)
            if res:
                state["eventlog"].append((day, "match", {"venue": res["venue"],
                                                         "result": res["result"],
                                                         "opp": res["opp"],
                                                         "score": res["score"]}))
                if venue == "home":
                    fb.take_gate(w, att)
                for r in R:
                    if active(r, day) and r["tr"]["foot"] > 0.3:
                        r["needs"]["cheer"] += {"win": 2.2, "draw": 0.6,
                                                "loss": -1.0}[res["result"]] * r["tr"]["foot"]
                        r["needs"]["cheer"] = max(0.0, r["needs"]["cheer"])
        # ---- moods fade; unfed relationships cool
        for r in R:
            r["needs"]["football"] *= 0.55
            r["needs"]["cheer"] *= 0.75
            for rl in r["rel"].values():
                if day - rl["last"] > 14:
                    rl["affection"] *= 0.985
                    rl["comfort"] *= 0.99
                rl["irritation"] *= 0.995
        # ---- intention lifecycle
        for r in R:
            for it in r["intents"]:
                if it["state"] == "open" and day > it["deadline"]:
                    it["state"] = "forgotten"
                    state["int_forgot"] += 1
                    if it["kind"] == "return":
                        o = BY.get(it["target"])
                        if o:
                            rel(o, r["n"])["irritation"] += 0.8
                            rel(o, r["n"])["trust"] -= 0.5
                            rel(o, r["n"])["ev"].append((day, "never got the " + it["note"] + " back"))
                            o["log"].append((day, f"still hasn't got the {it['note']} back from {r['n']}"))
            r["intents"] = [it for it in r["intents"] if it["state"] == "open" or
                            day - it.get("done", it["deadline"]) < 30]
        # ---- weekly household economics
        if d == 6:
            for hh in W.households.values():
                if not any(active(BY[m], day) for m in hh.members):
                    continue                    # nobody lives here yet
                inc = sum(W.dd["occupations"].get(BY[m]["occ"], {}).get("income", 0)
                          for m in hh.members if active(BY[m], day))
                was = hh.balance
                hh.balance += inc - 25
                if hh.balance < 0 and was >= 0:
                    hh.note(day, "money got tight")
    return state
