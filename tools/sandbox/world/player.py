"""
world.player — the human hand, held at arm's length from the engine.

A Controller supplies a decision for a resident's free slot, or None.
That is the ENTIRE interface. The simulation does not know which
resident is the player; it only knows some residents have a controller,
and asks it before falling back to ordinary utility choice.

The View a controller receives is built ONLY from what that resident
could honestly know: the date, the weather, the open places and what
they offer, their own habits and memories of who tends to be where, and
faces gated by recognition — a name only after enough real encounters,
before that "a familiar face", before that "a stranger".
"""

NAME_AT = 7          # encounters before a face becomes a name
FAMILIAR_AT = 2      # before this, people are strangers


class View:
    """what one resident can see of one moment — no omniscience"""
    def __init__(self, **kw):
        self.__dict__.update(kw)


def render_view(W, r, day, d, s, open_now):
    clock = W.clock
    opts = {}
    for pid, pl in open_now.items():
        m = r["pmem"].get(pid)
        faces = []
        if m:
            for other, cnt in sorted(m["assoc"].items(),
                                     key=lambda kv: (-kv[1], kv[0]))[:4]:
                rl = r["rel"].get(other)
                rec = rl["rec"] if rl else 0
                if rec >= NAME_AT:
                    faces.append(other)
                elif rec >= FAMILIAR_AT:
                    faces.append("a familiar face")
                else:
                    faces.append("a stranger")
        opts[pid] = {
            "provides": sorted(pl.sat),
            "covered": pl.cover,
            "your habit": r["habit"].get((pid, d, s), 0),
            "usually there": faces,
            "sore": r["pmem"].get(pid, {}).get("sore_until", -1) >= day,
        }
    pressing = sorted(r["needs"].items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    fx = W.football.fixture(day // 7) if W.football else None
    return View(
        day=day, dow=d, slot=s, date=clock.date_str(day),
        weather=W.weather.at(day), season=clock.season_of(day),
        holiday=day in clock.holidays,
        options=opts,
        pressing=[n for n, v in pressing if v > 1.2],
        open_intents=[(it["kind"], it["target"], it["note"])
                      for it in r["intents"] if it["state"] == "open"],
        fixture=(fx if fx and day % 7 == (W.football.fixture_dow if W.football else -1)
                 else None),
        recent=[(clock.date_str(dy), txt) for dy, txt in r["log"][-3:]],
    )


class Controller:
    def choose(self, view):
        """return a place id from view.options, "home", or None (defer to AI)"""
        return None


class NullController(Controller):
    """a player who is away — the town must not notice"""
    pass


class ScriptedController(Controller):
    """wraps a decide(view) function — the validation harness's human"""
    def __init__(self, decide):
        self._decide = decide

    def choose(self, view):
        return self._decide(view)
