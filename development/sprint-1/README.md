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

## Demonstration — watch a resident live a believable day

Everything needed to run the simulation and watch the first resident complete a
believable routine, in one place.

### Exact commands

```bash
# from the repository root
cd development/sprint-1
cargo run            # prints the district, then one full simulated day
cargo test           # optional: proves the run is correct (11 tests)
```

(Rust toolchain required — install once from https://rustup.rs if `cargo` is
missing. No other dependencies; the core is standard-library only.)

### Expected output

`cargo run` prints two parts:

1. **Phase 1 — the district:** the five locations with their affordances, the
   navigation graph (edges + travel ticks), and a validation line ending
   `Validation: OK`.
2. **Phase 2 — one day:** an hour-by-hour timeline from `00:00` onward. Each line
   is a resident either *setting out for* a place (with the route) or *arriving*
   to do something. It closes with an **end-of-day roll-call** (every resident
   should read `(home)`) and a **Spotlight** on Tomas listing what he did today.

The run is deterministic: the same build always prints the exact same day.

### What to observe — Tomas (age 9), the first resident to follow

- **00:00** he `sleeps — at loc_riverside` (his home).
- **06:00** he `sets out for loc_bakery (gets a warm roll)` — note the *route*
  `loc_riverside -> loc_cafe -> loc_bakery`: he walks it, edge by edge, never
  teleporting.
- **09:00** he arrives: `gets a warm roll — at loc_bakery`.
- **10:00–11:00** he heads to and `plays in the square`.
- **14:00–16:00** he walks back to the riverside and `visits the Old Oak`.
- **18:00** he is `home for the evening — at loc_riverside`.
- The **Spotlight** line confirms: `tomas_sleep, tomas_roll, tomas_play,
  tomas_oak, tomas_home` — a whole believable day, chosen tick by tick, not
  scripted to the clock.

Watch the world *converge* on its own, too: around **14:00** both Elias and Victor
drift into the café, and the Old Oak draws Elias, Agnes, and Tomas across the
afternoon — nobody coordinated that; it falls out of independent routines sharing
one world.

### Why this is believable, not scheduled

Each resident chooses each activity from a *preferred arrival time* it can slip
within, an *overridable destination*, and a *condition* gate — a proto-intention
(CD-006), not a fixed timestamp. Today the conditions are always true and choices
are deterministic; the same shape is what a later needs/mood/relationship layer
will steer, with no redesign.

### Known limitations (Sprint 1, by design)

- **No Old Oak object yet.** Residents *visit* the oak via the `VISIT_OAK`
  affordance, but the living world-object (seasonal state, interaction history)
  is Phase 3 — not built here.
- **Home = one of the five locations.** No separate residential nodes yet
  (Sprint-1 reduction).
- **Conditions are always `Always`.** The decision-making gate exists structurally
  but does nothing yet — deliberately.
- **No needs, mood, or relationship influence on selection.** Relationships are
  documented in DS-001 §2 but do not yet bend behaviour.
- **Seasons/weather not modelled.** One generic day; the clock tracks hours only.
- **Reduced scale:** 5 locations / 10 residents, versus the WI-01 vertical slice.

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
      mod.rs             #   re-exports
      clock.rs           #   WorldClock (hour counter; 24 ticks/day)
      routine.rs         #   Activity/Routine/Condition (proto-intention model)
      resident.rs        #   Resident + live status; hour-based selection
      cast.rs            #   the 10 residents' routines
      simulation.rs      #   the tick loop + event log
    main.rs              # observer binary
  tests/                 # integration tests
```

## Phase status

- [x] **Phase 1 — World representation** (locations, affordances, nav graph, validate).
- [x] **Phase 2 — Residents, routines (not fixed schedules), WorldClock, sim loop.**
      10 residents complete believable routines through the world; deterministic;
      no teleporting; everyone ends the day at home. 11 tests pass.
- [ ] Phase 3 — Living-object framework + the Old Oak.
- [ ] Phase 4 — First executable simulation (full observed day/multi-day).
