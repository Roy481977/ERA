#!/usr/bin/env python3
"""Phase 1 observer: build the district, print it, and prove it is valid.

Run from the sprint-1 directory:  python3 run_phase1.py
Exits 0 if the world is valid; non-zero (and prints problems) if not.
This is the "executed and observed" deliverable for Phase 1.
"""

from __future__ import annotations

import sys

from world.world import build_world


def main() -> int:
    world = build_world()

    print("=== ERA — First Breath · Phase 1: the district ===\n")

    print("Locations (5):")
    for loc in world.locations.values():
        print(f"  {loc.id:<16} {loc.name:<12} affordances: {', '.join(loc.affordances)}")

    print("\nNavigation graph (undirected; weight = travel ticks):")
    seen: set[frozenset[str]] = set()
    for node in world.nav.nodes():
        for other, w in world.nav.neighbors(node):
            key = frozenset((node, other))
            if key in seen:
                continue
            seen.add(key)
            print(f"  {node:<16} <-> {other:<16} {w} tick(s)")

    print("\nSample shortest paths:")
    for a, b in (("loc_bakery", "loc_riverside"), ("loc_stadium", "loc_cafe")):
        path = world.nav.shortest_path(a, b)
        t = world.nav.travel_time(a, b)
        print(f"  {a} -> {b}: {' -> '.join(path)}  ({t} ticks)")

    problems = world.validate()
    print("\nValidation:")
    if problems:
        for p in problems:
            print(f"  PROBLEM: {p}")
        print("\nWorld is INVALID.")
        return 1
    print("  OK — 5 locations, graph connected, all affordances present.")
    print("\nPhase 1 complete: the district can be executed and observed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
