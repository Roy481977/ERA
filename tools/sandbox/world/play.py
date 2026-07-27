"""
world.play — live the town from a terminal.

    python3 -m world.play district01_data Roy

Runs the same engine, day by day. At each of your free slots you are
shown what any resident in your position would know — the date, the
weather, the open doors and what they offer, the faces you associate
with each — and asked where to go. Enter a place, "home", nothing to
let your ordinary life decide, "day" to let the whole day pass, or
"quit" to leave the town running without you (it will).

This module contains no simulation logic: it is one Controller plus a
loop that prints the view. The engine cannot tell it from player_year's
script — which is the whole point.
"""
import importlib
import sys
from .engine import build_world
from . import behaviour
from .player import Controller


class Interactive(Controller):
    def __init__(self, clock):
        self.clock = clock
        self.skip_until = -1              # day index to fast-forward through

    def choose(self, v):
        if v.day <= self.skip_until:
            return None
        print()
        print(f"— {v.date}, {['07','09','11','13','15','17','19'][v.slot]}:00 · {v.weather}"
              + (" · public holiday" if v.holiday else ""))
        if v.fixture:
            print(f"  matchday: {v.fixture[1]} fixture")
        if v.pressing:
            print(f"  on your mind: {', '.join(v.pressing)}")
        for kind, tgt, note in v.open_intents:
            print(f"  you keep meaning to: {kind} {note or tgt}")
        for pid, o in sorted(v.options.items()):
            faces = ", ".join(o["usually there"]) or "—"
            print(f"    {pid:12s} offers {', '.join(o['provides']):32s} "
                  f"(been {o['your habit']}x this slot; usually: {faces})"
                  + ("  [sore]" if o["sore"] else ""))
        try:
            ans = input("  go > ").strip()
        except EOFError:
            self.skip_until = 10 ** 9     # input gone: ordinary life takes over
            return None
        if ans == "quit":
            raise KeyboardInterrupt
        if ans == "day":
            self.skip_until = v.day
            return None
        if ans in v.options or ans == "home":
            return ans
        return None


def main():
    mod = sys.argv[1] if len(sys.argv) > 1 else "district01_data"
    who = sys.argv[2] if len(sys.argv) > 2 else "Roy"
    dd = importlib.import_module(mod).DISTRICT
    W = build_world(dd, controllers=None)
    if who not in W.by_name:
        print(f"no resident called {who} in {dd['name']}")
        return
    W.controllers = {who: Interactive(W.clock)}
    W.out_prefix = dd["id"] + "_live"
    print(f"You are {who}. The town is {dd['name']}. It was here before you"
          " and it will carry on without you. Ctrl-C or 'quit' to leave.")
    try:
        behaviour.run(W)
    except KeyboardInterrupt:
        print("\nYou step back. The town keeps walking.")
    r = W.by_name[who]
    print(f"\nYour log so far:")
    for dy, txt in r["log"][-10:]:
        print(f"  {W.clock.date_str(dy):11s} {txt}")


if __name__ == "__main__":
    main()
