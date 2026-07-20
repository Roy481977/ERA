# ERA — Sprint 1 code (First Breath)

A headless, deterministic simulation core in **Rust** (see
[`../../creative-decisions/CD-007-core-language-rust.md`](../../creative-decisions/CD-007-core-language-rust.md)) —
no game engine (that choice stays open, IP-003). It grows a small district into a
world that visibly lives: people wake at different times, keep individual routines,
meet and remember one another, occasionally change their minds, tend a 400-year-old
oak, and react to the Saturday football.

Specs: [`../DS-001-first-breath.md`](../DS-001-first-breath.md) (the district) and
[`../DS-002-living-world.md`](../DS-002-living-world.md) (phases 3–8, per-phase
progress).

## Setup

Requires the Rust toolchain (`cargo`). One-time install if you don't have it:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

No other dependencies — the core is standard-library only.

## Run

From this folder (`development/sprint-1`):

```bash
cargo run                  # a normal day, hour by hour (Monday)
cargo run -- matchday      # a Saturday: how the town reacts to the football
cargo run -- week          # a seven-day summary (interactions, deviations, results)
cargo run -- days 14       # an N-day summary
cargo run -- explain Tomas # one resident's six days, with the reason for every move
cargo run -- chronicle     # a month watched from afar: habits, bonds, traditions
cargo run -- district      # just the world (locations, hours, nav graph)
cargo test                 # the full test suite (38 tests)
```

Everything is deterministic: the same command always prints the same world.

## What the observer shows

- **Simulation time** — day, weekday, and hour on every line.
- **Resident locations & routes** — each move prints where they set out for, the
  purpose, and the exact path walked (never a teleport).
- **Current intention** — the occupancy snapshot shows who is where and who is
  *en route* to where.
- **Location occupancy** — a "who is where at HH:00" snapshot (midday on a normal
  day; kick-off on a matchday).
- **Interactions** — who met whom, what passed between them, and the running
  affinity/trust.
- **Important state changes** — matchday buildup and result, deviations, the Oak's
  scarves and flowers.
- **The Old Oak** — its age, season, tallies, and recent history.
- **Decision explanations** — `explain NAME` prints a resident's whole day with the
  reason attached to every choice (route, detour, interaction, matchday).

## Expected output (normal day, abridged)

```
=== A day in the district — Mon ===
-- 04:00 --
  Hana     fires the ovens before dawn — at loc_bakery
...
-- who is where at 12:00 --
  Bakery             Hana, Sofia
  Café               Luca, Milo
  Main Square        Eva, Karim, Agnes, Tomas
  Stadium            Victor
...
-- connections today (8) --
  07:00 Hana    & Sofia   shared a word of encouragement (affinity 4, trust 5)
...
-- The Old Oak (400 yrs, in full green leaf this Summer) --
  3 visits · 0 scarves · 0 bouquets
    · Day 0 (Mon) 15:00 — Agnes sat a while beneath the Oak
-- end of day --
  Hana     Miller's Row       (home)
  ...                          (home)
```

On a matchday you additionally see the buildup, supporters converging on the
stadium for kick-off, the result, the post-match square, and the Oak's scarf/flowers.

## Layout

```
sprint-1/
  Cargo.toml
  src/
    lib.rs
    world/               # the district
      location.rs        #   8 locations (5 civic + 3 residential), affordances, opening hours
      navigation.rs      #   nav graph: edges, travel time, shortest path
      mod.rs             #   World + validation + is_open
    sim/                 # the living simulation
      clock.rs           #   WorldClock (hour counter; weekday)
      routine.rs         #   Activity/Routine/Condition (proto-intention model)
      resident.rs        #   Resident, live status, memories
      cast.rs            #   the 10 residents' routines
      social.rs          #   relationships + deterministic interactions
      intention.rs       #   small deviations (the social detour)
      oak.rs             #   the Old Oak: seasonal state + living history
      matchday.rs        #   the Saturday match and its consequences
      simulation.rs      #   the tick loop
    main.rs              # the observer (this file's commands)
  tests/                 # world, routine, social, intention, oak, matchday
```

## Phase status (Sprint 1)

- [x] **Phase 1** — world representation (locations, affordances, nav graph).
- [x] **Phase 2** — residents, proto-intention routines, WorldClock, sim loop.
- [x] **Phase 3** — believable daily structure (residences, staggered waking, opening hours, weekday variation).
- [x] **Phase 4** — first social life (relationships, interactions, memories).
- [x] **Phase 5** — intentions and small deviations (the social detour).
- [x] **Phase 6** — the Old Oak becomes living history.
- [x] **Phase 7** — first matchday life.
- [x] **Phase 8** — observation & demonstration (this observer).

## Known limitations (Sprint 1, by design)

- **Terminal only** — a structured text observer, not a graphical viewer (a viewer
  would be disproportionate work at this stage).
- **Shared residences** — three residential nodes house several residents each; no
  private dwellings yet.
- **One club, one fixture a week**, with a seeded scoreline — the town's reaction is
  the content, not match play.
- **Fixed supporter list; one deviation type** (the social detour); no needs/mood
  driving behaviour yet.
- **Seasons turn slowly** (four-week seasons), so short runs stay in one season.
- **No save/load** — all state is serialisation-ready, not yet serialised.
- **Structured interactions**, not generated dialogue.
