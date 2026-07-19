# DS-001 — First Breath (Sprint 1 Implementation Spec)

**Status: PROPOSED (implementation spec).** *Filename normalized from
"DS-001 - First Breath.md" to remove spaces for repo/tooling hygiene.*

Sprint 1 transitions ERA from architecture into implementation. It builds **the
smallest possible living district that can be executed and observed** — the
foundation, not a throwaway prototype.

**This works from the ratified architecture; it does not redesign it.** DS-001 is
a *reduced* instance of the WI-01 vertical slice
([`architecture/system-contracts/vertical-slice.md`](../architecture/system-contracts/vertical-slice.md)):
5 locations instead of ~12, 10 residents instead of 25–40, and **deterministic
proto-intention routines instead of the full intention/arbitration layer** — a
legitimate first-step simplification that already carries the seams (soft time,
overridable place, condition gate) the fuller layer will grow into. Terminology follows
[`world-state-schema.md`](../architecture/system-contracts/world-state-schema.md)
(Place/affordances, Resident, WorldClock) and honours the invariants (one world
state, one clock, no teleporting, deterministic replay).

---

## Implementation decision (ratified path)

The architecture deliberately keeps the Town Engine **logical core headless and
engine-decoupled** ("its logical tests run headlessly" — Town Engine strategy).
Sprint 1 implements that logical core in **Rust** (see
[`CD-007`](../creative-decisions/CD-007-core-language-rust.md)): a deterministic,
engine-decoupled sovereign core, chosen to optimise the long-term production
architecture rather than short-term development speed. *(An earlier draft of this
spec proposed Python for speed-to-running; that was superseded by CD-007 while the
codebase was still tiny and the migration cheap.)*

- This is the **logical-core language only.** It does **not** choose the game
  engine (Unreal / Unity), which remains an open question in IP-003 and is
  untouched.
- The model is plain structs, portable and rewritable later.

---

## 1. The first district — five semantic locations

Logical locations (not graphical assets), each with semantic affordances:

| id | Name | Affordances |
|---|---|---|
| `loc_stadium` | Stadium | `WORK_GROUNDSKEEP`, `MATCH_GATE`, `GATHER` |
| `loc_main_square` | Main Square | `MARKET`, `KIOSK`, `SIT_BENCH`, `BUSK`, `GATHER` |
| `loc_bakery` | Bakery | `WORK_BAKERY_COUNTER`, `BUY_BREAD`, `HOME` |
| `loc_cafe` | Café | `WORK`, `DRINK_COFFEE`, `LEGENDS_CORNER`, `HOME` |
| `loc_riverside` | Riverside | `WALK`, `SIT_BENCH`, `VISIT_OAK`, `HOME` |

**Navigation graph** (undirected; weight = travel time in ticks). The Main Square
is the hub:

```
Main Square — Bakery      (1)
Main Square — Café        (1)
Main Square — Stadium     (2)
Main Square — Riverside   (2)
Bakery      — Café        (1)
Café        — Riverside   (2)
```

The graph must be **connected** (every location reachable). Movement happens along
edges over travel-time ticks — **no teleporting**.

*(Sprint-1 reduction: there are no separate residential nodes yet; a resident's
"home" is one of the five locations.)*

## 2. Ten residents

Fields per resident (from the schema): `id`, `name`, `age`, `occupation`, `home`,
`current_location`, `routine`, `relationships`. **Routines, not fixed
schedules** (per Roy): a routine is a set of *activities*, and each activity is a
**proto-intention** (CD-006) rather than a clock→place entry. An activity carries:

- a **needed affordance** (what the resident wants to do), plus an optional
  **preferred destination** that pins an exact place when an affordance is shared
  by several locations;
- a **preferred arrival time** — the hour the resident *aims* to be doing it;
- a **flexibility window** — how many hours around that preference the activity may
  still be chosen (so time bends instead of snapping to a timestamp);
- a **condition** gate that must hold for the activity to be considered at all
  (today always `Always`; the seam where future needs/mood/relationship gates
  attach);
- a **priority** (tie-break) and a **duration**.

Each idle tick a resident selects the most appropriate eligible, not-yet-done
activity: eligible = condition holds **and** the hour lies inside the flexibility
window; among those it prefers the one it wants to do *soonest* (earliest
preferred arrival), breaking ties by higher priority then routine order — fully
deterministic. Because *when* and *where* are already soft (a preference and an
overridable destination) and selection already passes through a condition gate,
future decision-making (needs, mood, relationships, interruptions) can change
*selection* without changing the structure — **deterministic today, ready for
decision-making tomorrow, no redesign required.**

| id | Name | Age | Occupation | Home |
|---|---|---|---|---|
| `res_hana` | Mrs. Hana | 58 | Baker | `loc_bakery` |
| `res_sofia` | Sofia | 27 | Baker's assistant | `loc_main_square` |
| `res_luca` | Luca | 29 | Café owner | `loc_cafe` |
| `res_victor` | Victor | 63 | Retired footballer | `loc_cafe` |
| `res_elias` | Elias | 66 | Groundskeeper | `loc_main_square` |
| `res_eva` | Eva | 41 | Florist | `loc_main_square` |
| `res_karim` | Karim | 34 | Kiosk vendor | `loc_main_square` |
| `res_agnes` | Agnes | 81 | Retired (oldest supporter) | `loc_main_square` |
| `res_milo` | Milo | 22 | Street musician | `loc_main_square` |
| `res_tomas` | Tomas | 9 | Schoolchild | `loc_riverside` |

**Time** comes from one shared WorldClock (1 tick = 1 hour, 24 ticks/day). The
clock is a plain hour counter; activities reason about the hour directly through
their preferred arrival + flexibility window rather than through named blocks. A
resident *navigates* to each selected activity's location over travel time.
Routines are defined in code (Phase 2, `sim/routine.rs` for the model,
`sim/cast.rs` for the ten residents' routines).

**Relationships** (edges, lightweight this sprint): Hana–Sofia (mentor), Hana–Tomas
(gives him a roll), Luca–Victor (keeps his corner), Elias–Agnes (old friends),
Eva–Agnes (leaves flowers), Elias–Oak (tends), Tomas–Oak (visits), Agnes–Oak
(visits), Milo–Karim (busks by the kiosk).

## 3. One living world object — the Old Oak

A persistent world object that **exists independently of the player**:

| Field | Value |
|---|---|
| `id` | `obj_old_oak` |
| `age` | ~400 (years) |
| `location` | `loc_riverside` |
| `seasonal_state` | derived from WorldClock season (bare / budding / full / gold) |
| `interaction_history` | append-only list of `{tick, resident_id, action}` |

Residents (Tomas, Elias, Agnes) already visit it via `VISIT_OAK`; each visit
appends to `interaction_history`. The Oak changes with the seasons regardless of
whether anyone is watching (Independence / IP-002 AR). *(This is the "living
object framework" — Phase 3.)*

## 4. Implementation roadmap

- **Phase 1 — World representation.** Locations, affordances, the navigation graph;
  a loader/validator that executes and prints the district and proves connectivity.
- **Phase 2 — Residents.** Resident entities, deterministic routines
  (proto-intentions: preferred arrival, flexibility window, optional destination,
  condition gate), and the simulation clock (WorldClock ticks); residents move
  along the nav graph over travel time.
- **Phase 3 — Living object framework.** A persistent world-object model and the
  Old Oak; residents' visits append to its interaction history; seasonal state.
- **Phase 4 — First executable simulation.** Run the clock for one day (and a
  multi-day run), moving residents by schedule, recording Oak interactions, and
  observing the result as a printed timeline + a "why is this resident here?"
  reason line — deterministic and repeatable from a seed.

## 5. Acceptance for Sprint 1 (reduced from WI-01)

- Residents reach the locations their **routines** intend (semantic correctness). *(AT-1)*
- Movement respects the nav graph and travel time — **nobody teleports**. *(AT-5)*
- The run is **deterministic**: same inputs → identical timeline. *(AT-10)*
- One shared **WorldClock**; one authoritative world state. *(AT-6)*
- The Oak accrues **interaction history** and changes by season **independently**.
- Every resident's location at any tick has an **inspectable reason** (the
  activity it selected, logged as it sets out and arrives). *(AT-11, reduced)*

## 6. Working discipline

Small, reviewable commits, one phase (or sub-step) at a time. **Where the
architecture is genuinely missing, STOP and ask** rather than inventing large
systems. Objective: a running simulation as quickly as possible.

Code lives in [`development/sprint-1/`](sprint-1/).
