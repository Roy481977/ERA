# ERA — Sprint 1 code (First Breath)

Headless, deterministic logical core. Python 3, standard library only. No game
engine (that choice remains open — IP-003). Spec:
[`../DS-001-first-breath.md`](../DS-001-first-breath.md).

## Run

```bash
cd development/sprint-1
python3 run_phase1.py                 # build + print + validate the district
python3 -m unittest discover tests    # unit tests
```

## Layout

```
sprint-1/
  world/
    locations.py     # the 5 semantic locations + affordances
    navigation.py    # the navigation graph (edges, travel time, shortest path)
    world.py         # the World container + validation
  run_phase1.py      # Phase 1 observer (executed + observed)
  tests/
    test_world.py    # Phase 1 tests
```

## Phase status

- [x] **Phase 1 — World representation** (locations, affordances, nav graph, validate).
- [ ] Phase 2 — Residents, deterministic schedules, simulation clock.
- [ ] Phase 3 — Living-object framework + the Old Oak.
- [ ] Phase 4 — First executable simulation (one day, observed timeline).
