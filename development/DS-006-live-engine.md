# DS-006 — From prototype to the beginning of the actual engine

**Status: PROPOSED (implementation tracking).** Under the [Book of ERA](../docs/book-of-era/00-the-promise-and-laws.md)
and [DEV-000](DEV-000-development-constitution.md).

Direction (Roy): *"Convert the prototype into the first version of the live ERA
engine. Refactor the current architecture so the simulation runs continuously
rather than replaying exported data. The renderer should observe the live world
state directly. Preserve determinism, but build the engine around a continuously
ticking world with persistent entities, inspectable state and rendering driven
from that state. The objective is not graphics. The objective is to create a
platform where we can watch ERA live."*

And, alongside it: *"Don't optimize the simulation to keep every resident perfectly
on schedule. Small deviations are desirable… prevent runaway drift and impossible
schedules, but… shouldn't eliminate ordinary human variation. Imperfection is part
of the simulation, not a flaw in it."*

---

## What changed

### The engine is now a thing you hold, not a batch you run

Before, the shape was *run N days → export a flat trace → replay the file*. The
world only existed as a finished recording. Now there is an **`Engine`**
(`src/engine/`): a persistent, continuously-ticking world.

```
let mut engine = Engine::new();   // the district at the first breath (tick 0)
engine.tick();                    // advance one hour
let snap = engine.snapshot();     // a pure window onto the live state — right now
```

`tick()` advances the world one hour. `snapshot()` reads whatever the world *is*
at this instant and changes nothing — taking a snapshot never moves the clock. The
world persists between ticks; entities keep their identity across time.

### Rendering is driven from state, by construction

A `Snapshot` carries everything an observer needs and nothing it must compute
itself: every entity's live position (as ready screen coordinates *and* the
semantic "at a node / fraction along an edge" form), per-place **occupancy**, the
current **busiest** public gathering, **activity callouts**, the **Old Oak**, the
**events** emitted during the tick that produced this state, and the **bonds**
forming between residents (inspectable state). The engine owns the map layout
(`src/view/layout.rs`), so the snapshot can hand the renderer geometry directly.

The viewer (`viewer/`) was rebuilt to hold **no simulation logic**. It draws the
snapshot, interpolating positions between hours for smooth motion, and shows the
callouts, occupancy badges, busiest-place highlight, a live event ticker, an
inspectable per-resident panel, and the forming bonds. It is a pure observer.

### The snapshot is the single interface

The batch exporter is gone as a bespoke thing: `cargo run -- stream <days>` now
ticks one `Engine` and records the snapshot it reports each hour
(`{world, frames:[…]}`). `cargo run -- snapshot [ticks]` prints a single live
snapshot to the terminal. Both go through the same `snapshot()` — there is one
source of truth for "what the world looks like."

### Determinism preserved

The engine inherits the core simulation's determinism (no wall clock, no RNG; all
variation seeded). Tests assert it directly: two engines ticked alike produce
byte-identical `world_json()` and `snapshot().to_json()`, and a live snapshot at
tick N equals a fresh engine ticked N times. **68 tests pass.**

### Ordinary human variation is allowed to stand

Per Roy, the scheduling was *not* tightened to force punctuality. The strict
"everyone home at midnight" invariant was relaxed to the true one: no runaway
drift and no impossible schedule — everyone is home asleep in the small hours
(verified at 03:00, zero strandings over 28 days). A late evening after the match
or after lingering with a friend is left alone.

---

## Honest limitation — what "live" means today, and the open decision

The frames the browser plays are produced by ticking the engine **here** and
embedding the stream; the page then plays that faithful recording on a real-time
clock. The *architecture* is the live one — engine authoritative, snapshot the sole
interface, renderer purely observing — but the tick loop is not yet running **inside
the browser**. Truly continuous in-browser ticking needs one of two long-term
paths, and this is a reserved decision (architecture + a genuine fork):

1. **One engine, compiled to WebAssembly.** The real Rust engine ticks inside the
   page and emits these same snapshots; the browser is a thin client. Highest
   fidelity, single source of truth, determinism guaranteed. *Blocked in the cloud
   build sandbox right now:* the `wasm32` standard library can't be fetched
   (`static.rust-lang.org` is unreachable here); it needs a build environment that
   can install the target.

2. **A browser-side engine mirror (JS/TS).** A deterministic core ticks live in the
   page today with no toolchain dependency, the Rust engine kept as the reference
   implementation and cross-check. Immediate, but two engines to keep in step.

The snapshot contract is designed to be **identical either way**, so whichever path
is chosen, the renderer built here is reused unchanged.

---

## Files

- `src/engine/mod.rs` — the `Engine`, `Snapshot`, and the live-state readout.
- `src/engine/snapshot_json.rs` — the JSON wire contract (`world_json`, `to_json`).
- `src/view/layout.rs` — district map coordinates + entity colours (engine-owned).
- `src/main.rs` — `stream` and `snapshot` subcommands built on the engine.
- `viewer/viewer.template.html`, `viewer/build.sh` — the pure-observer renderer.
- `tests/engine.rs` — persistence, snapshot purity, determinism, live-position tests.
