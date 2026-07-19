# DS-003 — Sprint 1 Final Report (Phases 3–8)

**Status: PROPOSED (report).** Consolidated report for the "living world" arc of
Sprint 1, delivered as a sequence of small reviewable commits per Roy's directive.
Paused here for review. GitHub `Roy481977/ERA` is canonical; this doc mirrors to
the project.

---

## 1. Commit list (this arc, oldest → newest)

| Commit | Summary |
|---|---|
| `2585f32` | Enrich routines to proto-intentions (preferred arrival, flexibility, dest, condition) |
| `7b8319e` | **Phase 3a** — stagger waking; narrate homes beside the square |
| `41da38f` | **Phase 3b** — residential nodes (nobody sleeps in public) |
| `af752c7` | **Phase 3c** — opening/closing hours + closed-destination gate |
| `7660eca` | **Phase 3d** — weekday routine variation + midnight-carryover fix |
| `f4d383b` | DS-002 progress tracker |
| `a2c9520` | **Phase 4** — first social life (relationships, interactions, memories) |
| `4d398bd` | **Phase 5** — intention layer + social detours |
| `358530a` | **Phase 6** — the Old Oak becomes a persistent world object |
| `12f8b05` | **Phase 7** — first matchday life (result, town reaction, Oak mark) |
| `fec2ec1` | **Phase 8** — structured terminal observer + demonstration |

## 2. Implemented systems

- **World** (`world/`): 8 locations — 5 civic/work + 3 residential — with
  affordances and **opening hours**; a connected weighted nav graph; validation.
- **Clock** (`sim/clock.rs`): one authoritative WorldClock (1 tick = 1 hour), day
  and **weekday**.
- **Routines as proto-intentions** (`sim/routine.rs`): each activity has a
  preferred arrival, a flexibility window, an optional destination override, a
  priority/duration, and a **condition** gate (`Always` / `OnWeekdays`).
- **Residents** (`sim/resident.rs`): live status (idle / travelling / performing
  with a start-day stamp), `done_today`, and **memories**.
- **Social life** (`sim/social.rs`): a `Relationships` store (affinity/trust, one
  owner) and a deterministic, seeded interaction resolver (greeting, conversation,
  shared coffee, encouragement, recognition, disagreement) shaped by relationship
  and place.
- **Intentions** (`sim/intention.rs`): a lightweight, bounded, provably-safe
  deviation — the social detour — that overrides "go home" to join a nearby friend.
- **The Old Oak** (`sim/oak.rs`): a persistent world object with age, seasonal
  state, tallies, and an append-only history (visits, children playing, gatherings,
  scarves, flowers).
- **Matchday** (`sim/matchday.rs`): a seeded weekly result and the town's reaction
  (attend / work / gather / go home), with a consequence on the Oak.
- **Simulation** (`sim/simulation.rs`): the deterministic tick loop tying it
  together, plus the **observer** (`main.rs`).

## 3. Test results

**34 tests pass** (`cargo test`), across `world` (8), `routine` (7), `social` (5),
`intention` (4), `oak` (5), `matchday` (5). They cover the invariants — determinism,
no teleportation, valid routes, one-owner-per-fact, and **everyone reaches a valid
home every day of a full week including matchday** — plus each phase's behaviour.
Two genuine multi-day correctness bugs were caught by the week-long test and fixed
(the midnight activity-carryover, in two forms).

## 4. Run commands

```bash
cd development/sprint-1
cargo run                  # a normal day, hour by hour
cargo run -- matchday      # a Saturday
cargo run -- week          # a seven-day summary
cargo run -- days 14       # an N-day summary
cargo run -- explain Tomas # one resident's six days, with reasons
cargo run -- district      # the world alone
cargo test                 # 34 tests
```

## 5. Sample timeline (normal day, abridged)

```
=== A day in the district — Mon ===
-- 03:00 --  Hana   sets out for loc_bakery (fires the ovens before dawn) via loc_millers_row -> loc_bakery
-- 05:00 --  Elias  sets out for loc_stadium (mows the pitch at first light) via loc_oakside -> loc_main_square -> loc_stadium
-- 07:00 --  Hana & Sofia shared a word of encouragement (affinity 4, trust 5)
-- 12:00 --  who is where: Bakery: Hana, Sofia · Café: Luca, Milo · Square: Eva, Karim, Agnes, Tomas · Stadium: Victor
-- 15:00 --  Agnes  sat a while beneath the Oak
-- 16:00 --  Eva meant to head home, but Karim was at the Main Square and the two are close — Eva detours to join them
-- 20:00 --  end of day — all ten (home)
```

Matchday (Saturday) sample:

```
08:00 Matchday. The Bakery opens early and scarves come out along the High Street.
13:00 Karim, Agnes set out for the Stadium.
15:00 Kick-off at the Stadium.  (Karim, Agnes, Milo, Elias in the crowd)
17:00 Full time — Rain Town drew today.
18:00 supporters linger in the square after the draw
(win → a scarf is tied to the Old Oak; loss → flowers are left)
```

## 6. Output samples

Captured live from `cargo run` and `cargo run -- matchday` (see §5 and the
Sprint-1 README's "Expected output"). No screenshots — the deliverable is a
terminal observer by design (a graphical viewer would be disproportionate now).

## 7. Unresolved issues / limitations

- Residences are **shared nodes**, not private dwellings.
- **One deviation type** (social detour); no needs/mood model yet driving choices.
- Matchday: **one club, one weekly fixture, a seeded scoreline**; supporters are a
  fixed list; "bakery busier / café busier" is conveyed by announcement and
  foot-traffic, not by changed stock or hours.
- **Seasons turn slowly** (four-week seasons); short runs stay in summer.
- **No save/load** — state is serialisation-ready but not serialised.
- Interactions are **structured events**, not generated dialogue.
- Occupancy snapshots **rebuild the run to a tick** (cheap now; would want an
  incremental snapshot at larger scale).

## 8. The five highest-value next steps

1. **A needs/mood layer feeding selection** — hunger, tiredness, sociability as
   inputs to `select`/intentions, so deviations and routines flex for reasons the
   world can see. The `Condition` seam and the intention layer are already shaped
   for this.
2. **Serialization / save-load** — persist world state, relationships, memories,
   and the Oak's history (all already plain data) so a world can be paused,
   resumed, and inspected across runs.
3. **Per-resident dwellings + a richer map** — turn shared residential nodes into
   individual homes and grow the district toward the WI-01 vertical slice
   (~12 locations, 25–40 residents), stress-testing determinism at scale.
4. **A fuller matchday & season model** — real (if simple) fixtures over a season,
   form/standings, and seasonal effects on the Oak and routines, so the weekly
   rhythm compounds into a story.
5. **Engine integration spike** — feed this deterministic core to a thin renderer
   (the game-engine choice in IP-003) to prove the headless-core / engine-decoupled
   architecture end-to-end.

---

*Detail per phase: [`DS-002-living-world.md`](DS-002-living-world.md). District
spec: [`DS-001-first-breath.md`](DS-001-first-breath.md). Code + how to run:
[`sprint-1/README.md`](sprint-1/README.md).*
