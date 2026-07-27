"""
world.football — the competition exists whether anyone watches or not.

An independent simulation: a league of clubs, a fixture every week of the
fantasy calendar (two series a year, double round-robin), a squad with
form and injuries, morale, finances fed by real gate receipts, and a
reputation that follows results. Residents RESPOND to all of this through
events the engine forwards; nothing in here knows a resident exists.
"""


class FootballWorld:
    def __init__(self, rng, clock, cfg):
        self.rng, self.clock = rng, clock
        self.name = cfg["club"]
        self.league = list(cfg["league"])          # 13 opponents
        self.fixture_dow = cfg.get("fixture_dow", 5)
        self.squad = []
        for i, nm in enumerate(cfg["squad"]):
            self.squad.append({"n": nm, "skill": 4 + rng.h("sk", nm) % 7,
                               "out_until": -1, "apps": 0, "goals": 0})
        # two series per year: double round-robin over 13 opponents = 26 each
        self.fixtures = {}                          # week -> (opp, venue)
        for series in (0, 1):
            order = sorted(self.league, key=lambda c: rng.h("ord", series, c))
            for i, opp in enumerate(order + order):
                w = series * 26 + i
                if w >= clock.weeks:
                    break
                self.fixtures[w] = (opp, "home" if (w % 2 == 0) else "away")
        self.results = {}                           # week -> dict
        self.morale = 0
        self.balance = cfg.get("start_balance", 2000)
        self.gate_price = cfg.get("gate_price", 8)
        self.sponsors = cfg.get("sponsors", 160)
        self.wages = cfg.get("wages", 180)
        self.points = {0: {}, 1: {}}                # series -> opp table (ours under name)
        self.history = []                           # (day, text) — institution history
        self.attend = {}                            # week -> gate

    def fixture(self, w):
        return self.fixtures.get(w)

    def _strength(self, w):
        fit = [p for p in self.squad if p["out_until"] < w * 7]
        return (sum(p["skill"] for p in fit) * 10 / max(1, len(self.squad))
                + self.morale * 2.5)

    def play_week(self, w):
        """called once per week by the engine; returns the match event or None"""
        fx = self.fixtures.get(w)
        if not fx:
            return None
        opp, venue = fx
        day = w * 7 + self.fixture_dow
        h = self.rng.h
        # injuries roll before kickoff
        if h("inj", w) < 1500:
            fit = [p for p in self.squad if p["out_until"] < day]
            if fit:
                p = fit[h("injw", w) % len(fit)]
                p["out_until"] = day + 14 + h("injd", w) % 21
                self.history.append((day, f"{p['n']} injured — out ~{(p['out_until']-day)//7} weeks"))
        us = self._strength(w) + (6 if venue == "home" else 0)
        them = 42 + h("opps", opp) % 18 + h("oppf", opp, w) % 10
        diff = us - them
        roll = h("res", w) + diff * 28
        result = "win" if roll > 6200 else ("draw" if roll > 3600 else "loss")
        gf = {"win": 1 + h("gf", w) % 3, "draw": h("gd", w) % 3, "loss": h("gl", w) % 2}[result]
        ga = {"win": max(0, gf - 1 - h("ga", w) % 2), "draw": gf, "loss": gf + 1 + h("gx", w) % 2}[result]
        scorers = []
        fit = [p for p in self.squad if p["out_until"] < day]
        for p in fit:
            p["apps"] += 1
        for g in range(gf):
            if fit:
                p = sorted(fit, key=lambda q: -q["skill"] * self.rng.h("gs", w, g, q["n"]))[0]
                p["goals"] += 1
                scorers.append(p["n"])
        self.morale = max(-5, min(5, self.morale + {"win": 1, "draw": 0, "loss": -1}[result]))
        series = 0 if w < 26 else 1
        tbl = self.points[series]
        tbl[self.name] = tbl.get(self.name, 0) + {"win": 3, "draw": 1, "loss": 0}[result]
        # the rest of the league plays itself, coarsely
        for o in self.league:
            if o != opp:
                tbl[o] = tbl.get(o, 0) + (3 if h("lg", w, o) < 4200 else
                                          (1 if h("lg", w, o) < 7000 else 0))
        tbl[opp] = tbl.get(opp, 0) + {"win": 0, "draw": 1, "loss": 3}[result]
        res = {"week": w, "day": day, "opp": opp, "venue": venue,
               "result": result, "score": (gf, ga), "scorers": scorers,
               "series": series}
        self.results[w] = res
        self.balance -= self.wages                  # the squad is paid every week
        # institution history for the memorable ones
        if result == "win" and gf - ga >= 3:
            self.history.append((day, f"beat {opp} {gf}–{ga} — talked about for weeks"))
        if result == "loss" and ga - gf >= 3:
            self.history.append((day, f"lost {gf}–{ga} at {opp} — a dark Saturday"))
        # series end: championship check
        if w in (25, self.clock.weeks - 1):
            pos = self.position(series)
            snm = "autumn" if series == 0 else "spring"
            if pos == 1:
                self.history.append((day, f"CHAMPIONS of the {snm} series"))
            else:
                self.history.append((day, f"finished {pos} of {len(self.league)+1} in the {snm} series"))
        return res

    def take_gate(self, w, attendance):
        self.attend[w] = attendance
        self.balance += attendance * self.gate_price + self.sponsors
        if attendance and attendance == max(self.attend.values()):
            best = max((v for k, v in self.attend.items() if k != w), default=0)
            if attendance > best and len(self.attend) > 4:
                day = w * 7 + self.fixture_dow
                self.history.append((day, f"record gate: {attendance}"))

    def position(self, series):
        tbl = self.points[series]
        rank = sorted(tbl.items(), key=lambda kv: (-kv[1], kv[0]))
        for i, (nm, _) in enumerate(rank):
            if nm == self.name:
                return i + 1
        return len(rank)

    def reputation(self):
        played = len(self.results)
        if not played:
            return 0.5
        wins = sum(1 for r in self.results.values() if r["result"] == "win")
        return wins / played

    def season_record(self):
        c = {"win": 0, "draw": 0, "loss": 0}
        for r in self.results.values():
            c[r["result"]] += 1
        return f"{c['win']}W {c['draw']}D {c['loss']}L over {len(self.results)} matches"
