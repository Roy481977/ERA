"""
world.engine — assembly. WORLD ← TOWN ← DISTRICT ← PEOPLE ← SIMULATION.

Builds a runnable world from a district data module, wires institutions,
households and the football world, generates the year's life events, runs
behaviour, then hands the record to the historian and the metrics.

    python3 -m world.engine district01_data [weeks]
"""
import importlib
import sys
from . import core, people as PP
from .core import Rng, Clock, Weather, DEFAULT_SEASON_PROFILES
from .football import FootballWorld
from .entities import Place, Institution, Household


class Historian:
    """recording API — four levels. Rendering lives in world.historian."""
    def __init__(self):
        self.town_log = []

    def town(self, day, text):
        self.town_log.append((day, text))


class World:
    pass


def build_world(dd, weeks=None):
    W = World()
    W.dd = dd
    W.rng = Rng(dd["seed"])
    W.clock = Clock(weeks or dd["weeks"])
    W.weather = Weather(W.rng, W.clock)
    W.season_profiles = DEFAULT_SEASON_PROFILES
    W.football = FootballWorld(W.rng, W.clock, dd["football"]) if dd.get("football") else None
    W.places = {pid: Place(pid, d) for pid, d in dd["places"].items()}
    W.insts = {iid: Institution(iid, d) for iid, d in dd.get("institutions", {}).items()}
    W.plot_loc = dd["plot_loc"]
    W.hist = Historian()

    # ---- people from data
    W.residents = PP.make_population(W.rng, dd, W.clock.ndays)
    W.by_name = {r["n"]: r for r in W.residents}
    occs = dd["occupations"]
    for r in W.residents:
        od = occs.get(r["occ"], {})
        r["anchors"] = list(od.get("shifts", [])) + list(r.get("commitments", []))
        r["term_bound"] = od.get("term_bound", False)

    # ---- households as entities
    W.households = {}
    for r in W.residents:
        hh = W.households.get(r["hh"])
        if hh is None:
            hh = W.households[r["hh"]] = Household(r["hh"], r["home"])
        hh.members.append(r["n"])
    h = W.rng.h
    for hid, hh in sorted(W.households.items(), key=lambda kv: str(kv[0])):
        for item in dd.get("household_items", []):
            if h("hitem", hid, item) < 4000:
                hh.poss.append(item)

    # ---- institutions staffed and membered from data, at day 0
    for r in W.residents:
        od = occs.get(r["occ"], {})
        iid = od.get("institution")
        if iid and iid in W.insts:
            if od.get("pupil"):
                W.insts[iid].members[r["n"]] = 0
            else:
                W.insts[iid].staff[r["n"]] = r["occ"]
    if W.football:
        fc = next((i for i in W.insts.values() if i.kind == "football_club"), None)
        if fc:
            for r in W.residents:
                if "season ticket" in r.get("poss", []):
                    fc.members[r["n"]] = 0
            fc.note(0, f"{len(fc.members)} season-ticket holders at the start of the year")

    # ---- the year's life events (generic; rates are district data)
    ev = []
    rates = dd.get("event_rates", {})
    adults = [r for r in W.residents if not r.get("child") and not r.get("arrives")]
    for w in range(W.clock.weeks):
        base = w * 7
        if h("ill", w) < rates.get("illness", 0):
            v = adults[h("illwho", w) % len(adults)]
            ev.append((base + h("illd", w) % 5, "illness",
                       {"who": v["n"], "days": 2 + h("illn", w) % 3}))
        if h("wp", w) < rates.get("pressure", 0):
            work = [a for a in adults if a["occ"] != "retired"]
            v = work[h("wpw", w) % len(work)]
            ev.append((base, "pressure", {"who": v["n"], "days": 5}))
        if h("hp", w) < rates.get("household", 0):
            v = adults[h("hpw", w) % len(adults)]
            ev.append((base + h("hpd", w) % 6, "household",
                       {"who": v["n"], "what": ["leaking gutter", "stuck gate",
                                                "broken pane", "wobbly shelf"][h("hpx", w) % 4]}))
        if h("bor", w) < rates.get("borrow", 0):
            a = adults[h("borA", w) % len(adults)]
            b = adults[h("borB", w) % len(adults)]
            if a["n"] != b["n"]:
                ev.append((base + h("bord", w) % 6, "borrow",
                           {"who": a["n"], "lender": b["n"],
                            "item": dd["household_items"][h("bori", w) % len(dd["household_items"])]}))
        if h("arg", w) < rates.get("argument", 0):
            ev.append((base + h("argd", w) % 6, "argument", {"seed": w}))
        if h("inv", w) < rates.get("invitation", 0):
            a = adults[h("invA", w) % len(adults)]
            ev.append((base + h("invd", w) % 5, "invitation", {"who": a["n"]}))
    for nc in dd.get("newcomers", []):
        ev.append((nc["arrives"], "arrival", {"who": nc["n"]}))
    if dd.get("retirement_day"):
        canon = dd.get("canon", {})
        olds = [a for a in adults if a["occ"] != "retired"
                and a["age"] >= dd.get("retirement_age", 60) and a["n"] not in canon]
        if olds:
            v = max(olds, key=lambda r: r["age"])
            ev.append((dd["retirement_day"], "retirement", {"who": v["n"], "was": v["occ"]}))
    ev.sort(key=lambda e: (e[0], e[1]))
    W.events = ev
    return W


def run_world(module_name, weeks=None, outputs=True):
    dd = importlib.import_module(module_name).DISTRICT
    W = build_world(dd, weeks)
    from . import behaviour
    behaviour.run(W)
    if outputs:
        from . import historian, metrics
        historian.write_all(W)
        metrics.write_all(W)
    return W


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "district01_data"
    wks = int(sys.argv[2]) if len(sys.argv) > 2 else None
    W = run_world(mod, wks)
    st = W.state
    print(f"{W.dd['name']}: {len(W.residents)} residents, {W.clock.weeks} weeks, "
          f"{len(st['visits'])} visit records, {len(st['eventlog'])} events, "
          f"intentions {st['int_done']} done / {st['int_forgot']} forgotten")
    if W.football:
        print(f"football: {W.football.season_record()}; "
              f"balance {W.football.balance}, morale {W.football.morale}")
