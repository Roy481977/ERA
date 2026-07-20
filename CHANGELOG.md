# ERA — Changelog

Every change to the repository, dated, newest first. Nothing changes silently.
Historical reasoning is never deleted — superseded and rejected material is
retained in place, this log records the reasoning.

Format: `YYYY-MM-DD — summary`, followed by details.

---

## 2026-07-19 — Phase 3c: opening hours + closed-destination gate — PROPOSED

Locations gained optional **opening hours**: the Bakery opens 05:00–17:00 and the
Café 07:00–22:00; civic places and residences never close. Activity selection now
**refuses a closed destination** — a visitor cannot choose the café before it
opens — while staff/owner work affordances (`WORK*`) and going `HOME`/`REST`
bypass hours, so proprietors still open their own premises before dawn. New tests
cover the open/close windows and the selection gate. **13 tests pass**; the
observer now prints each location's hours.

## 2026-07-19 — DEV-000 Development Constitution ratified — ACTIVE

Roy delivered the **ERA Development Constitution** (DEV-000, v1.0), now the
governing law for all implementation. Preserved verbatim at
`development/DEV-000-development-constitution.md`. It defines the two inseparable
goals (an exceptional deterministic engine + one of the most believable living
worlds), the **Ladder of Life** (world exists → residents act → remember → habits →
relationships visible → places accumulate history → traditions → attachment), and
firm principles: **memory is only valuable if it changes the future**;
**relationships should be experienced through behavior, not numbers**; understandable
**emergence** over randomness; **observation-first** (a system that can't be observed
is incomplete); depth over breadth; extend before creating; small reviewable commits,
continue automatically. Sits alongside GOVERNANCE.md (knowledge preservation);
DEV-000 governs how the simulation is built. Recorded in INDEX.

Next work climbs the ladder from where Sprint 1 left off (rungs 4–5): making
memory/relationships change behavior and become observable.

## 2026-07-19 — Phase 8: observation & demonstration — PROPOSED

Rewrote `main.rs` into a structured terminal **observer** with modes (the earlier
per-phase print sections were scaffolding, now replaced):

- `cargo run` — a normal day, hour by hour, with a midday occupancy snapshot,
  the day's connections, and the Oak's state.
- `cargo run -- matchday` — a Saturday: buildup, converging supporters, kick-off
  occupancy, result, post-match, Oak mark.
- `cargo run -- week` / `-- days N` — a per-day summary table (interactions,
  deviations, matchday result) plus Oak growth and the strongest bonds formed.
- `cargo run -- explain NAME` — one resident's six days with the reason attached
  to every move, and everything they remember.
- `cargo run -- district` — the world alone (locations, hours, nav graph).

The observer shows simulation time, locations and routes, current intentions
(who is where / en route), occupancy, interactions, state changes, and the Oak's
history — all deterministic. The Sprint-1 README now documents setup, every run
command, expected output, and limitations. **34 tests pass.** This completes the
Phases 3–8 arc; stopping here for review.

## 2026-07-19 — Phase 7: first matchday life — PROPOSED

New `sim/matchday.rs`: every Saturday the club plays (kick-off 15:00), and the
result is seeded per week (win / draw / loss) — football kept minimal so the focus
is the town's reaction. Supporters (a deliberately partial list — Victor, Elias,
Agnes, Tomas, Milo, Karim) form an intention to attend: they head to the stadium,
watch, and afterwards the result shapes the evening — a win is celebrated in the
square, a draw is mulled there, a defeat sends them home quietly. Non-supporters
keep the town running (Luca keeps the café open, Eva tends her flowers). The
district gets buildup announcements through the day, and the result **marks the
Old Oak** — a scarf tied to a branch after a win, flowers left after a loss.
Matchday convergence also produces its own interactions (supporters meet at the
ground).

Also fixed a subtler version of the midnight-carryover bug: activities are now
stamped with the day they began (`Status::Performing { start_day }`) and only
credited to that day, so a task begun at 23:00 that finishes after midnight no
longer suppresses the same activity on the new day. Five new tests (matchday
differs from a normal day; residents stay individual, not one crowd; deterministic;
the result marks the Oak; everyone still gets home). **34 tests pass.**

## 2026-07-19 — Phase 6: the Old Oak becomes living history — PROPOSED

New `sim/oak.rs`: the Old Oak is now a persistent world object, not just a
destination. It has identity, an age (~400), a location, a seasonal state derived
from the day (`Season`: summer→autumn→winter→spring, appearance in data), and an
**append-only history**. When a resident visits, the Oak records it (children
"play beneath" it, adults "sit a while"), the visitor gains a memory of the Oak,
and its tallies update; when two residents meet at the riverside, the Oak records
that they "met beside" it. The Oak owns its own history — other systems record
into it, never rewrite it — and it's ready for later serialisation. A readable
history renders as "Day 2 (Wed) 18:00 — Elias and Tomas met beside the Oak".

Scarf/flowers event kinds exist for Phase 7 (matchday). Five new tests (history
accumulates across days, deterministic, the child plays, residents meet beside it,
visitors carry a memory). **29 tests pass.** Observer prints the Oak's state and
recent history.

## 2026-07-19 — Phase 5: intentions & small deviations — PROPOSED

New `sim/intention.rs`: a lightweight, deterministic layer above the routine. The
routine is still the default plan, but a resident who is winding down to go home
may instead **detour to join a nearby friend** — if that friend is present at an
open public place, reachable, the bond is strong enough (affinity ≥ 2), a seeded
gate passes, and there is provably still time to visit *and* get home. Bounded to
one deviation per resident per day. Every deviation is logged with its reason
("Eva meant to head home, but Karim was at the Main Square and the two are
close — Eva detours to join them"), and the deviations emerge from relationships
built up in Phase 4 rather than any script.

Four new tests (residents deviate; deterministic; capped once per day; never
stranded — everyone still reaches home every day). **24 tests pass.** The observer
lists the week's spontaneous visits.

## 2026-07-19 — Phase 4: first social life — PROPOSED

Residents who share a public place at a compatible time may now interact. New
`sim/social.rs`: a `Relationships` store (single owner of affinity/trust, seeded
from DS-001 §2) and a deterministic interaction resolver. Each tick, co-located,
present residents (travellers and sleepers excluded) are paired in deterministic
order; a seeded FNV hash — no RNG — gates whether they interact, with likelihood
and type shaped by their relationship and the place: close friends encourage or
share coffee, acquaintances converse, strangers nod or greet, poor terms bicker.
Consequences flow through the owners — affinity/trust adjust in the store, and
**each resident records its own memory** — and every interaction is logged with
its reason and the affinity/trust change. A once-per-pair-per-day cap and a
~24 %-base chance mean co-location usually *doesn't* produce an interaction.

Five new tests (interactions happen, are deterministic, strengthen bonds, cap at
once per pair per day, and leave memories). **20 tests pass.** Observer prints a
"Today's connections" summary and Tomas's memories.

## 2026-07-19 — Phase 3d: weekday routine variation — PROPOSED

The `Condition` seam now does real work. The WorldClock gained `weekday()`
(0 = Mon … 6 = Sun) and `Condition` gained `OnWeekdays(days)`; `select` takes the
weekday and filters on it. Two residents now visibly differ by day: Hana and Karim
work Mon–Sat and take a distinct Sunday (a river walk / a quiet square), via a
fluent `Activity::on_weekdays(..)` builder.

Fixed a **multi-day correctness bug** surfaced by a new week-long test: an activity
still performing at midnight (e.g. arriving home at 20:00 for a 4-hour stay)
finished on the day-rollover tick and was recorded into the *next* day's
`done_today`, so the resident thought it had already gone home and never returned
(failing every other day). Completions that land on the rollover tick are no
longer recorded against the new day. New tests: weekday routines differ;
**everyone ends every day at home across a full week**. **15 tests pass.**

This completes **Phase 3**. Acceptance met: residents wake at different times,
nobody sleeps in a public location, occupations show distinct rhythms, shops open
and close, every move follows graph edges, and all residents reach a valid home
every day of the week.

## 2026-07-19 — Phase 3b: residential nodes (no public sleeping) — PROPOSED

The district gained three residential locations — **Miller's Row**, **High Street
Rooms**, **Oakside Cottages** (`HOME`/`REST` only) — wired into the nav graph off
the square and nearest shops. All ten residents now live in and return to a
residential node; `HOME` and `REST` were removed from the Bakery/Café/Riverside so
those read as civic/work places, not dwellings. Routine timings were re-tuned for
the new commutes. Determinism, no-teleport, and end-at-home invariants all hold;
world tests updated (now eight locations, three residential). **11 tests pass.**

## 2026-07-19 — Phase 3a: staggered waking + home narration — PROPOSED

Roy approved Phase 2 and authorised autonomous progression through Phases 3–8
(small reviewable commits; stop only for architecture-level decisions). Phase 3
opens with a deterministic pass on the cast data only — no architecture change:

- **Staggered waking.** Wake time is now set by each resident's sleep *duration*
  (sleep is chosen at tick 0 and runs for its duration), so the district rises in
  a natural spread instead of all at 06:00: Hana the baker at 04:00, working
  residents 05:00–06:00, Tomas 07:00, Milo the musician 09:00. Morning activities'
  preferred arrivals were nudged to match each wake time.
- **Home narration softened.** The six Main-Square residents are now narrated as
  living in rooms *beside* the square ("sleeps above the kiosk", "his cottage by
  the square"), removing the "sleeping in the public square" read. This is text
  only — the home node is still `loc_main_square`; a structural fix needs
  residential nodes, deliberately deferred (Sprint-1 reduction).
- **Re-verified:** all **11 tests still pass**; every resident still completes a
  believable routine and ends the day at home; determinism holds. Sprint-1 README
  demonstration updated to the new timeline. No engine/architecture files touched.

## 2026-07-19 — Routine model enriched to proto-intentions — PROPOSED

Roy directed the routine model be upgraded to carry, per activity: a **preferred
destination**, a **preferred arrival time**, a **flexibility window**, and an
**optional condition** — deterministic today, but with room for future
decision-making without a redesign. Done, and the Phase-2 simulation re-verified.

- **`routine.rs`:** `Activity` now carries `dest: Option<LocationId>` (overrides
  affordance resolution when a place is ambiguous), `preferred_arrival` (hour),
  `flexibility` (± hours around it), `priority`, `duration`, and `condition`. New
  `Condition` enum (`Always` today) with `holds()` — the seam where future
  needs/mood/relationship gates attach. `Routine::target_location` honours `dest`.
- **Selection is now hour-based, not block-based.** `WorldClock` lost its `Block`
  enum (now a plain hour counter). `Resident::select(hour)` picks the eligible,
  not-yet-done activity whose *preferred arrival is soonest* (ties → higher
  priority → routine order): eligible = condition holds **and** hour ∈
  `[pref−flex, pref+flex]`. Fully deterministic.
- **`cast.rs`:** the 10 residents' routines re-expressed in the new model;
  ambiguous square activities pinned with explicit `dest`. The earlier "SQUARE"
  affordance hack was removed.
- **Result (re-verified):** all **11 tests still pass**; the observed day is
  believable and everyone still ends at home; the *when/where* of an activity is
  now soft and gated, so a later decision layer can steer *selection* without
  restructuring. DS-001 §2 and the Sprint-1 README (incl. a **Demonstration**
  section) updated to match.
- Stopped at the end of Phase 2 for Roy's review, per instruction.

## 2026-07-19 — Core = Rust (CD-007); Sprint 1 Phase 2 — PROPOSED

Roy directed optimizing for the final architecture over dev speed. Outcome:

- **CD-007 — the authoritative core is Rust** (PROPOSED). Engine-decoupled
  sovereign brain: compiles to a native lib (FFI to Unreal/Unity), WASM, or a
  server; best control over deterministic replay; GC-free scale; ECS-native;
  memory-safe. The *core language only* — the game-engine choice (Unreal/Unity)
  stays open (IP-003). The four-file Python spike was migrated to Rust while tiny.
- **Phase 2 (Rust):** WorldClock (1h ticks + time-blocks); Resident entities;
  **routines** — goal-and-time proto-intentions (CD-006), *not* fixed schedules,
  so future decision-making can evolve without restructuring; a deterministic
  simulation loop that navigates residents through the world over travel time.
- **Result (verified):** 10 residents complete believable routines (wake →
  work/errands → visit the Old Oak → home); the run is deterministic; nobody
  teleports; everyone ends the day at home. **11 tests pass** (7 world + 4
  routine). Observed via `cargo run`.
- Stopped at the end of Phase 2 for Roy's review, per instruction. Next: Phase 3
  (the Old Oak living object) + Phase 4 (full observed simulation).

## 2026-07-19 — Sprint 1 (DS-001 First Breath): spec + Phase 1 — PROPOSED

Transitioned ERA from architecture into implementation, working from the ratified
contracts (world-state schema, semantic places, CD-006, WI-01 vertical slice) —
no redesign, no new philosophy, no scope expansion.

- New `development/` module + **DS-001 spec** ("First Breath"): the smallest
  living district that can be executed and observed — 5 semantic locations
  (Stadium, Main Square, Bakery, Café, Riverside), 10 residents (id/name/age/
  occupation/home/current-location/deterministic schedule/relationships), the
  **Old Oak** persistent living object (independent of the player), and a 4-phase
  roadmap.
- **Implementation-language decision (flagged for veto):** the logical core is
  built in Python 3 (stdlib only) — headless, deterministic, engine-decoupled, per
  the Town Engine strategy. This is the *logical core only*; the **game-engine
  choice (Unreal/Unity) is untouched and remains open (IP-003)**.
- **Phase 1 shipped:** `development/sprint-1/` — locations + affordances, the
  navigation graph (edges, travel time, deterministic shortest path), the World
  container with validation (connected graph, no islands, affordances present), an
  executable observer (`run_phase1.py`), and 7 unit tests. **Runs; all tests
  pass.** Code lives in GitHub (canonical); the project mirrors the specs/docs.
- Next: Phase 2 (residents + deterministic schedules + WorldClock), on Roy's go.
  All PROPOSED; not promoted to canonical.

## 2026-07-19 — RATIFIED: architecture/ permanent module + WI-01 created

**Ratification (first in the repository).** Roy ratified `architecture/` as a
**permanent, first-class repository module**. Only the module's *permanence* is
canonical; **IP-003 and every architecture document remain PROPOSED.** Resolves
the IP-003 placement open question. Recorded in `architecture/README.md`
(Placement — RATIFIED) and INDEX.

**New work item — WI-01: System Contracts & Vertical Slice Specification.** Created
`architecture/system-contracts/` to make the conceptual architecture implementable
without engineers inventing the core rules:
- `world-state-schema.md` — authoritative schema (WorldClock, Entity, Place,
  Resident, Relationship, Intention, Reservation, Event, Memory, Recognition,
  ReasonCode) with **per-field single ownership**.
- `engine-boundaries.md` — for all 15 engines: owns / may read / may propose / may
  mutate / must never control.
- `inter-engine-contracts.md` — the event + command model; per-engine inputs,
  outputs, events, commands, failure behavior, determinism (deterministic vs
  seeded-probabilistic).
- `vertical-slice.md` — the Town Engine slice: one district (~12 semantic places),
  25–40 persistent residents, ordinary weekday + matchday + a disruptive storm,
  persistence across two weeks of absence, all four fidelity tiers.
- `acceptance-tests.md` — 13 checkable tests (semantic correctness, bend-not-break,
  relationships alter behavior, interruption propagation, no teleport/reset, one
  visible world state, AI cannot rewrite truth, determinism, offscreen continuity,
  believability).
- `observability-and-debugging.md` — intention inspector, "why is this person
  here?" trace, world-state timeline, relationship-change log, event causality
  graph, deterministic replay + contradiction/liveness reports.

Reconciled with CD-006, the Town Engine strategy, the system map and the execution
roadmap; terminology kept identical. **Scope-guarded: no new engines, no
broadening.** All WI-01 material PROPOSED — not promoted to canonical.

## 2026-07-19 — Intake: IP-003 + architecture module (Systems Architecture Foundation) — PROPOSED

Roy provided the "ERA Systems Architecture Foundation" package (ChatGPT-authored),
declared as net-new only. Intake per protocol:

- **Consistency check.** Every file was net-new (nothing live replaced, as
  stated). All 15 subsystem briefs carry Status: PROPOSED and a "Constitutional
  connection" citing the Human Test and the Relational Axiom. Recognition Engine
  maps to IP-002 A2; the roadmap's 6-week Town Engine slice matches
  `research/town-engine-technical-strategy.md`. **No contradictions with
  canon-track.**
- **Integrated (wrapper folder stripped):**
  - `intake/IP-003-systems-architecture-foundation.md` — the Import Package
    (Design Translation): ERA as a **federation of bounded living systems sharing
    one authoritative world state and one clock; AI proposes/orchestrates inside
    authored bounds and never silently owns or rewrites world truth.**
  - `architecture/` (top-level module): `README.md`, `system-map.md`,
    `execution-roadmap.md`, and `systems/` (15 engine briefs: town, time,
    world-persistence, relationship, memory, recognition, event, matchday,
    club-culture, economy, narrative, ai-director, crowd, weather-season,
    audio-ecology).
- **Reconciliation.** IP-003 numbering correct (after IP-002). Placed
  `architecture/` top-level (per the module's own tree), noting its permanence is
  Roy's to ratify (IP-003 open question). Added a CKO **reconciliation map** in
  `architecture/README.md` (each engine → its IP/CD/living-world roots) and
  cross-linked the Town Engine brief ↔ CD-006 ↔ the technical strategy ↔
  `living-world/interwoven-lives.md`. The intake instruction file
  (`README-FOR-CLAUDE.md`) was not committed (transient guidance, not a repo
  artifact).
- **Status.** All PROPOSED. **Not promoted to canonical.**

## 2026-07-19 — Intake: CD-006 + Town Engine (repo-update zip) — PROPOSED

Roy provided an updated-repository zip (ChatGPT-authored) adding CD-006 and a
Town Engine technical strategy. Intake per the CKO protocol:

- **Consistency check.** Compared the zip against the live repo file-by-file:
  `intake/` (IP-001/002), all of `living-world/`, and all of `sources/` were
  **identical**. The only genuinely new files were CD-006 and the Town Engine doc.
- **Not taken (parallel/older state).** The zip's `GOVERNANCE.md` was an *older*
  copy missing live **§7 (Creative Decisions)**; its `INDEX.md`, `CHANGELOG.md`
  and `creative-decisions/README.md` reflected a state that did not include the
  live **CD-001…CD-005**. These were kept from the live repo, not overwritten.
- **Integrated.** Added `creative-decisions/CD-006-simulate-intention-not-movement.md`
  ("ERA simulates intention; movement is its visible consequence" — the Town
  Engine) and `research/town-engine-technical-strategy.md` (build-vs-buy, tiers,
  semantic-place graph, six-week vertical slice).
- **Reconciliation.** Numbering **CD-006** is correct (next after CD-005).
  Cross-refs verified (CD-006 ↔ town-engine ↔ IP-002 AR ↔ living-world). Added an
  `ID` row to CD-006 for format parity; adopted the broadened `research/`
  definition ("external inputs and technical evaluations"); linked the chain from
  `living-world/interwoven-lives.md` → CD-006 → the technical strategy. Register,
  INDEX and dashboard (RESEARCH → 1) updated.
- **Status.** All PROPOSED. **Not promoted to canonical.**

## 2026-07-19 — Foundational Creative Decisions backfilled (CD-001…CD-005) — PROPOSED

At Roy's request, backfilled the five foundational Creative Decisions, each with
its alternatives, the reasoning that made it win, what it rejects/supersedes,
consequences, and cross-references to the Import Packages:

- **CD-001 — Attachment, not addiction** (North Star) → IP-001 AT-1/AT-3/DR-001.
- **CD-002 — Grown, not built** (over "Club as Partner") → IP-002 AT-4/RJ-1;
  IP-001 AT-5.
- **CD-003 — Recognition beneath Memory** → IP-002 A2/CE-1/CR-1; IP-001 AT-9.
- **CD-004 — Meaning split from Recognition** → IP-002 A3/A2/CE-3/CR-2.
- **CD-005 — The Relational Axiom** (over "Non-Control") → IP-002 AR/CE-6/CR-8/
  RQ-1; supersedes AT-6.

All PROPOSED (CKO seeds), awaiting Roy's ratification. Register updated in
`creative-decisions/README.md`; INDEX updated. From here, every significant
philosophical or design breakthrough receives a Creative Decision as part of the
normal workflow.

## 2026-07-19 — New module: Creative Decisions (permanent architecture)

Roy established a permanent workflow/architecture change: a new top-level module
`creative-decisions/` to preserve the **reasoning behind major creative decisions
— why a discovery won over the alternatives** — a gap the repository did not
explicitly cover (it held discoveries via Import Packages and canon, but not the
*why it survived*).

- **Import Package vs. Creative Decision:** IP describes the discovery (the WHAT);
  CD explains why it survived (the WHY). Distinct artifacts, cross-linked, never
  merged.
- **Rule:** when ChatGPT + Roy reach a significant conclusion that changes ERA's
  philosophy, world or design, ChatGPT produces a Creative Decision; the CKO
  classifies, cross-references, links to the Import Package(s), updates the INDEX,
  and preserves it permanently (reversed decisions are superseded, never deleted).
- Recorded in **GOVERNANCE §7**. Added `creative-decisions/README.md` (purpose,
  CD template, workflow, register) and seeded **CD-001 — Attachment, not
  addiction** as a CKO-backfilled example (PROPOSED; also resolves the sources'
  addiction-vs-attachment contradiction in attachment's favour).

## 2026-07-19 — Living World: interwoven lives ("the same rails") — PROPOSED

Per Roy: all the living must interact, in a town, on the same rails — bonding and
aging across years; tens of lives on different days/occasions; scripted for
years. Added `living-world/interwoven-lives.md`, the connective system beneath
residents + places:

- **One shared clock** — all lives on a single persistent timeline, so
  interactions are consistent, co-witnessed and rememberable (a world with a
  past, not a loop).
- **Three levels of life** — named residents · minor residents (the "tens of
  lives") · micro-life (squirrels, cats, foxes) — all on the same rails.
- **The web** — relationships as edges (bonds, chance "sometimes" encounters,
  care, rivalry, romance, cross-species) with evolving strength and encounter rules.
- **Scripted for years** — authored milestone arcs (aging, loss, growing up) +
  emergent daily texture; AI orchestrates within authored bounds, Human Test
  governs. The agency–otherness balance applied to authorship of the world.
- **Worked example** — the boy (provisional "Tomas") and the Old Dog: a bond, the
  "sometimes" search, the squirrels, multi-year aging, and a loss that strikes all
  four textures at once and is never undone.
- Player sees only fragments over years; never the cause, never a quest.

Cross-linked from residents.md and README. PROPOSED.

## 2026-07-19 — Living World: places defined + the two moons — PROPOSED

Defined the district's places in `living-world/places.md` (Club/Stadium, Main
Street, Plaza & Fountain, the Riverside — Bridge/River/Old Oak, Museum Quarter,
Academy, Railway), each on a shared place template, filling the Book of ERA's
open questions. Proposed a map unification (emotional zones = canonical spine,
concentric rings = a supporting radial reading).

Introduced the never-explained **mystical root** per Roy in
`living-world/the-quiet-mysteries.md`: the district was designed **under two
moons** — a football place *just beside the real*. The layer is **"seen, never
said"**: no resident remarks on it, no lore/menu/quest/text ever names it, it
grants no advantage, and one quiet thread runs through each place (the fountain's
two reflections, the river's double-tide and the old oak, the museum's oldest
photograph, the academy's double shadow, the railway line into a distance no map
shows). Tied to Wonder (IP-001) and the deepest Independence (IP-002 AR). All
PROPOSED.

## 2026-07-19 — Residents cast expanded (13 biographies) — PROPOSED

Wrote full template biographies for the rest of the canonical cast in
`living-world/residents.md`: Daniel & Sofia (the couple), Elias (groundskeeper),
Mrs. Hana (baker), Luca (café), Karim (kiosk), Eva (florist), Milo (musician),
Nora (curator), Otto (publican), the Twins (children), Agnes (oldest supporter),
Victor (retired legend), Emma (journalist). Roles are CKO-proposed and grounded
in the district's places/rhythms; the cast is cross-linked so the world coheres,
and each quietly instantiates the attachment mechanisms (Living Memory,
Recognition via Victor/Emma/Nora, honest history via Nora/Agnes/Otto, and
"never performs for the player" = independence). PROPOSED — awaiting Roy's
approval/edits on roles and content.

## 2026-07-19 — Living World module started (district / living aspect) — PROPOSED

Per Roy: follow the proposal ChatGPT chat closely as the evolution of the idea,
document the living aspect well and within the main files, and continue the work
ChatGPT crashed mid-way through. Consolidated the living-world layer from all
three sources (proposal chat, Book of ERA v1.2, Design Bible Vols V–VII) into a
new `living-world/` module:

- `living-world/README.md` — The Living World (district): what it is,
  constitutional discoveries about place, district identity, emotional geography
  (both the zone view and the ring view, flagged for unification), composition &
  camera, landmarks, daily rhythms & match day, "the world continues without the
  player," visible-consequence table, weather/time, AI-as-world-building (tied to
  the Human Test), visual direction (four rules, density, Nintendo principle,
  "come and look not use me," the art north star), richness standard, open
  questions. Cross-referenced to IP-002 axioms (Independence/AR, Recognition,
  Meaning, Human Test).
- `living-world/residents.md` — residents system: canonical draft resident list,
  the resident design template, and a first fully-drafted example biography (the
  Old Dog) to fill the "expand each resident" gap.

Faithful to the sources; CKO-proposed additions marked `_[CKO-proposed]_`. All
PROPOSED — nothing canonical until Roy ratifies.

## 2026-07-19 — Source corpus received & secured (4 documents)

Roy handed over the full accumulated ERA material for documentation. All four
preserved verbatim under `sources/` (originals + `.txt` extracts), classified as
**SOURCE MATERIAL — unclassified, not canonical**:

- `design-bible-v0.1.pdf` — ERA Design Bible, Foundational Edition v0.1 (9
  volumes; its own 7-law Constitution; 5 core emotions; design chain).
- `book-of-era-edition-I-v1.2.docx` — The Book of ERA v1.2, the district /
  living-world layer.
- `era-the-beginning-for-gamma.docx` — "The Beginning," the manifesto.
- `proposal-chatgpt-chat.pdf` — the raw ChatGPT proposal chat (world visual
  design + early strategy).

Manifest at `sources/README.md` maps each document, the alignments with IP-001/
IP-002, and the contradictions to resolve (addiction vs attachment;
football-as-skin vs constitutive; two parallel "Constitutions"). Next step:
distil into PROPOSED Import Packages and produce a reconciliation — nothing
canonical until Roy ratifies.

## 2026-07-19 — IP-002: Relational compression (CE-6 / axiom AR) — PROPOSED

RQ-1 paid out. The "self past its boundary" root yielded a compression: **deep
attachment requires consequential agency inside an independent world** —
provisional constitutional expression *"the player shapes the Club but never
solely authors it"*; the relationship is **stewardship, not sovereignty.**

Recorded in IP-002:
- New candidate primary axiom **AR** (wording open); design is an inverted-U
  (agency without sovereignty), with a *per-domain* peak on the agency–otherness
  curve.
- **A1 (authorship half) + A4 (Independence) fuse into AR;** Independence and
  Vulnerability become *derived*. Meaning (A3) stands apart. Axiom set compresses
  4 → 3 (Relational · Recognition · Meaning).
- Added compression event **CE-6**; candidate ratification **CR-8**.
- **Four textures of loss** (place/form, regard, narrative, uncontrollable
  reality) preserved as a *derived research model* — not an axiom — with the
  compounding-loss prediction.
- **Rejected** the CKO's over-strong "you can only bond with what you do not fully
  control" (counterexamples: house, painting, manuscript — loved because they
  *resisted*).

All PROPOSED; final wording of AR deliberately open. INDEX updated.

## 2026-07-19 — IP-002 (Human Attachment Research) captured — PROPOSED

Second Import Package, opening the Human Attachment research repository. Curated
from the Phase 2 dialogue into six sections: Candidate Axioms (externalized/
vulnerable self, Recognition, Meaning, Independence, plus an exploratory root and
the tension meta-truth), Compression Events (five discoveries that reduced the
philosophy), Constitutional Consequences (what each discovery strengthens/
weakens/replaces/creates), Active Research Questions (RQ-1…RQ-3), Rejected/
Demoted Ideas, and Candidate Ratifications (CR-1…CR-7).

Notable movements (all PROPOSED, none canonical):
- Recognition rises toward bedrock; **Memory demoted** to a mechanism.
- **"The player is never the sole author"** generalizes and would supersede
  "reality is the Club's co-author" (AT-6).
- The four Internal-Recognition conditions collapse into one ("independent of the
  present self").
- OQ-2 (presence vs authenticity) tentatively resolving: belonging does not
  require multiplayer.

Governance:
- Added the **discovery-vs-explanation rule** to GOVERNANCE §6: discoveries
  change the philosophy and are recorded first-class; explanations only clarify
  and never stand alone.

INDEX updated (dashboard → 2 PROPOSED, register, decision record, open/research
questions). Phase 2 continues on RQ-1 before the axioms are locked.

## 2026-07-19 — IP-001 confirmed, restructured; next phase set — PROPOSED

Roy confirmed the IP-001 distillation and directed three changes plus a
forward-looking phase.

Changed in IP-001:
- Reorganized into five sections: Accepted Philosophical Truths, Open
  Philosophical Questions, Rejected Philosophical Directions, Key Constitutional
  Principles (8), and Decision Rationale (why each accepted truth survived
  challenge).
- **AT-4 ("a Club is grown, not built") demoted to a Candidate Truth** — held
  PROPOSED and not final, per Roy. Removed from accepted truths; OQ-3 remains.
- **AT-2 (Core Loop) amended:** the Club's economy is part of the loop, driven by
  the fantasy score (real results → fantasy → economy).
- Still fully PROPOSED; nothing canonical.

Changed in GOVERNANCE:
- Added §6 **Package Streams & Research Phases**: future packages declare a
  stream — Philosophy, Human Attachment Research, Constitutional Decisions, or
  Design Translation. Phase shift recorded: after IP-001 the goal moves from
  refining wording to discovering deeper human truths about attachment that may
  change the Constitution itself. Added the meta-principle "preserve what proved
  meaningful, not everything that happened."

## 2026-07-19 — IP-001 (Worldview Foundation) received — PROPOSED

First ERA Import Package. Roy directed capture of the *converged philosophy*
only — accepted truths, open questions, rejected ideas — as the beginning of
institutional memory, deliberately excluding brainstorming. The CKO curated the
"Emotional Foundation" philosophy and the subsequent design review into
`intake/IP-001-worldview-foundation.md`.

Contents: 16 accepted truths (proposed → canonical), 7 open constitutional
questions (OQ-2…OQ-8), 4 rejected/superseded ideas, a placement map, and 7
drafted decision records (DR-001…DR-007).

Status: held **PROPOSED**. Per SOP, nothing is canonical until Roy ratifies.
On approval the accepted truths split into `constitution/`, open questions into
`open/`, rejected ideas into `rejected/`, and the decision records are
finalized. INDEX updated (dashboard, register, decision record, open-questions
register).

## 2026-07-19 — ERA Import Package intake ratified as SOP

Roy restated and ratified the ERA Import Package intake as the standard
operating procedure. Two refinements folded into GOVERNANCE §3 to match the
stated steps exactly: duplicate detection is now explicit alongside
contradiction detection, and decision records may be "drafted or updated" (not
only drafted). No change to authority, classification law, or the verbatim
charter.

## 2026-07-19 — Intake protocol changed to ERA Import Packages

Roy directed that design material no longer be imported as raw conversations.
The unit of intake is now a structured **ERA Import Package** prepared by
ChatGPT (curated design material). On each package the CKO verifies consistency,
identifies conflicts, recommends classifications, suggests placement, drafts
decision records, and waits for approval before updating canonical documents.
Raw conversations are bounced with a recommendation to package them first,
unless Roy explicitly asks to proceed with the raw material.

Changed:
- `GOVERNANCE.md` §3 — rewritten as the Import Package intake protocol. The
  verbatim charter in §1 is untouched; §3 refines its operational steps.

## 2026-07-19 — GitHub mirror live

The canonical GitHub mirror is now live at `Roy481977/ERA`. The three
foundational documents were pushed to the repository root as the initial
commit.

Details:
- **Authentication:** a fine-grained Personal Access Token (Contents:
  read/write) scoped to `Roy481977/ERA`.
- **Transport note (for future sessions):** `api.github.com` is blocked by the
  container's egress proxy ("builtin injection failed", HTTP 502). The git
  transport over HTTPS works normally, so sync is done with plain `git`
  (clone/commit/push), **not** the GitHub REST API. Create commits with git,
  not the API.
- **Path mapping:** the ERA Claude project stores these files under an `era/`
  path; they map to the **root** of the GitHub repo.
- Resolves OQ-1 (GitHub authentication).

## 2026-07-19 — Repository initialized

The ERA knowledge repository was initialized as the live working copy inside
the ERA Claude project. No design content yet; this is scaffolding only.

Added:
- `GOVERNANCE.md` — the CKO charter preserved verbatim, plus classification law
  (7 statuses), intake protocol, design-governance trace, and document-quality
  rules.
- `INDEX.md` — master map, directory plan, status dashboard (all zero),
  document register, decision record, and open-questions register.
- `CHANGELOG.md` — this file.

Governance decisions recorded:
- **Canonical home = GitHub; ERA project = live working copy** (chosen by Roy).
- **Classification set = 7 statuses**, default-to-Open when uncertain (per
  charter).

Known status / pending at the time of this entry (later resolved — see the
entry above):
- GitHub mirror was not yet live; auth path was pending. Resolved 2026-07-19 via
  fine-grained PAT.
- No `constitution/` or `canon/` content exists yet — awaiting first material.
