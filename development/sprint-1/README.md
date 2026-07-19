# ERA — Sprint 1 code (First Breath)

Headless, deterministic simulation core in **Rust** (see
[`../../creative-decisions/CD-007-core-language-rust.md`](../../creative-decisions/CD-007-core-language-rust.md)).
No game engine (that choice remains open — IP-003). Spec:
[`../DS-001-first-breath.md`](../DS-001-first-breath.md).

## Run

```bash
cd development/sprint-1
cargo run            # build + observe the district (and, from Phase 2, one day)
cargo test           # unit + integration tests
```

## Layout

```
sprint-1/
  Cargo.toml
  src/
    lib.rs               # crate root
    world/               # Phase 1 — world representation
      mod.rs             #   World + validation
      location.rs        #   5 semantic locations + affordances
      navigation.rs      #   nav graph: edges, travel time, shortest path
    sim/                 # Phase 2 — clock, residents, routines, simulation
    main.rs              # observer binary
  tests/                 # integration tests
```

## Phase status

- [x] **Phase 1 — World representation** (locations, affordances, nav graph, validate).
- [ ] Phase 2 — Residents, **routines** (not fixed schedules), simulation clock.
- [ ] Phase 3 — Living-object framework + the Old Oak.
- [ ] Phase 4 — First executable simulation (full observed day/multi-day).
