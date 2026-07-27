"""
player_year — a year of representative HUMAN decisions for the resident
called Roy, expressed as a scripted controller. This file is INPUT, not
engine: it sees only what the in-game view shows (date, weather, open
places and their capabilities, its own habits and memories, fixtures)
and returns a place id, "home", or None to let ordinary life happen.

The shape of the year it plays:
  weeks 1-3     explore — try every open door once
  weeks 4-19    settle — bread in the morning, the pub on Fridays,
                every home match, quiet places when dry
  weeks 20-32   AWAY — no input for three months. The town must not
                notice; the resident's ordinary simulated life continues.
  weeks 33-51   return — pick the old threads back up
"""
from world.player import ScriptedController


def decide(v):
    week = v.day // 7
    # --- three months away: the controller goes silent
    if 20 <= week < 33:
        return None
    opts = v.options

    def has(cap):
        best = None
        for pid, o in sorted(opts.items()):
            if cap in o["provides"] and not o["sore"]:
                if best is None or len(o["provides"]) > len(opts[best]["provides"]):
                    best = pid
        return best

    # --- exploration: first weeks, go somewhere you've barely been
    if week < 4:
        fresh = sorted(opts, key=lambda p: (opts[p]["your habit"], p))
        if fresh and v.slot in (1, 2, 3, 5):
            return fresh[0]
        if v.slot == 0 and has("bread"):
            return has("bread")
        return None
    # --- a settled human week
    if v.fixture and v.fixture[1] == "home" and v.slot in (3, 4):
        g = has("football")
        if g:
            return g                      # never miss a home match
    if v.slot == 0 and has("bread"):
        return has("bread")               # bread first, most mornings
    if v.dow == 4 and v.slot == 1 and has("errand"):
        return has("errand")              # the Friday market run
    if v.dow in (4, 5) and v.slot == 6 and has("drink"):
        return has("drink")               # the weekend pint
    if v.dow == 6 and v.slot == 1 and has("purpose"):
        return has("purpose")             # Sunday morning at the allotment
    if v.slot == 5 and v.weather == "dry" and has("quiet"):
        return has("quiet")               # a dry evening's quiet
    if v.pressing and "repair" in v.pressing and has("repair"):
        return has("repair")
    return None                           # otherwise: let the day be ordinary


CONTROLLERS = {"Roy": ScriptedController(decide)}
