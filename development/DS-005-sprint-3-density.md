# DS-005 — Sprint 3: A Continuously Living District (density)

**Status: PROPOSED (implementation tracking).** Under the [Book of ERA](../docs/book-of-era/00-the-promise-and-laws.md)
and [DEV-000](DEV-000-development-constitution.md). Direction (Roy): before weather
and atmosphere, **deepen the simulator** — the systems are sound but the town is too
sparse; residents move between major activities rather than continuously living. The
goal is not new systems but **dramatically more life inside the existing ones**:
more decisions, smaller moments, far more incidental interactions, a breathing
background world, and micro-life — so one simulated hour *feels* richer. Fully
deterministic; deepen, don't replace.

---

## Step 1 — The density layer (background, micro-life, moments) ✅

**What became more alive:** an hour is no longer a short schedule — it's a place
with a lot quietly happening. The town keeps its own routines (the ovens lit before
dawn, the shutters up, a delivery at the café door, the morning and evening trains,
the school bell, the museum unlocking, church bells, the lamps coming on). Small
life moves through it whether or not anyone is watching (sparrows in the Oak,
pigeons at the fountain, a cat between warm sills, crows to the museum chimney at
dusk, a fox along the river after midnight, a cyclist over the bridge). And the
residents themselves have small moments — pausing at a shop window, watching the
children, a brief word with someone they know, scratching the old dog, stepping
aside for a cyclist, pausing on the bridge to watch the water. A day went from
~116 events to **~276**, and small moments vastly outnumber the major ones.

**Implemented:**

- **`sim/ambient.rs`** — a layer *over* the behavioural log (a separate `ambient`
  stream, so nothing existing changed and all prior tests still pass). `Ambient` /
  `AmbientKind { Town, Micro, Moment }`, timestamped within the hour so an hour has
  inner order. Pure deterministic generators: `background(day,hour,weekday)` (the
  town's routines, weekday-aware — school on weekdays, bells on Sunday, the ground
  readied on matchday) and `microlife(day,hour,weekday)` (scheduled + seeded so it
  varies yet replays identically).
- **`moments_pass`** (in `simulation.rs`) — each hour, every *present* resident
  evaluates their surroundings (who else is here, the children, an open shop
  window, the old dog) and may have a small moment; a traveller may pause on the
  bridge or take a shortcut. Emergent from co-presence and place, seeded, bounded
  (≤2 per resident/hour, quieter at night), and **pure texture** — it changes no
  world truth.
- **Observer** now weaves behavioural + ambient into a curated "living hour"
  (every behavioural line, the town and micro-life, and a handful of moments),
  reading like a town rather than a log.
- **Viewer** — the trace now carries the ambient life (tagged `town`/`micro`/
  `moment`), and the event ticker styles and orders it, so watching the map feels
  populated.

**Files changed:** `sim/ambient.rs` (new), `sim/simulation.rs` (`ambient` field,
`density_pass`, `moments_pass`), `sim/mod.rs`, `main.rs` (woven timeline + ambient
in trace), `viewer/viewer.template.html` (styled ticker), `tests/density.rs` (new).

**Architectural choices (deepen, don't replace):** the ambient layer is strictly
additive — a second stream beside the behavioural log — so the deterministic core
is untouched and every prior test passes unchanged. Everything is a pure function
of day/hour (+ seed); no RNG. Moments never mutate relationships, positions, or
endings — they are texture, curated at display time so richness never becomes noise.

**Tests added (5):** an hour is richly populated; town + micro-life + moments all
occur; the town keeps its routines; ambient life is deterministic; ambient does not
disturb the behavioural world. **57 tests total.**

**Known limitations / next within density:** moment variety can grow further; some
micro-life could move as dots on the map (not only in the ticker); incidental
resident *encounters while passing* could be richer; the background world could
react to weather once weather exists.

**Commands:** `cargo run` (a living hour) · `cargo run -- trace 7` + the viewer ·
`cargo test`

---

## Then

Once the district feels continuously alive, resume the world-building order:
**weather & atmosphere**, then more of the old dog, the two moons, and the rest —
each enhancing an already-living world rather than compensating for a sparse one.
