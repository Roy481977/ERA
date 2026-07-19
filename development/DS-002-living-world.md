# DS-002 — Toward a Living World (Sprint 1, Phases 3–8 progress)

**Status: PROPOSED (implementation tracking).** Continuation of
[`DS-001-first-breath.md`](DS-001-first-breath.md). This document tracks the work
that turns the technically-correct district into a world that visibly *feels*
alive. One section per phase; small reviewable commits; determinism preserved.

**Preserved invariants (every phase):** deterministic from the same start · no
teleportation · valid graph routes · one owner for every state fact · every
resident reaches a valid end-of-day state · AI does not own world truth · tests
for each meaningful behaviour.

Code lives in [`sprint-1/`](sprint-1/). Run with `cargo run`; test with
`cargo test`.

---

## Phase 3 — Believable daily structure ✅

**What became more alive:** the district no longer wakes as one body. Hana lights
the ovens at 04:00; workers open up across 05:00–06:00; Tomas is up at 07:00; Milo
sleeps off the late crowd until 09:00. Everyone lives in an actual home and commutes;
the Bakery and Café open and close; Hana and Karim take a visibly different Sunday.

**Implemented (four commits, 3a–3d):**

- *3a* — wake time derived from each resident's sleep duration → staggered rising.
- *3b* — three residential nodes (Miller's Row, High Street Rooms, Oakside
  Cottages); every resident lives in and returns to one; `HOME` removed from the
  Bakery/Café/Riverside so those are civic/work places. Nobody sleeps in public.
- *3c* — `OpenHours` on locations (Bakery 05–17, Café 07–22); `select` refuses a
  closed destination, while `WORK*`/`HOME`/`REST` bypass hours so staff open their
  own premises.
- *3d* — `WorldClock::weekday()` + `Condition::OnWeekdays`; Hana & Karim work
  Mon–Sat and rest differently on Sunday.

**Files changed:** `world/location.rs` (residential nodes, `OpenHours`),
`world/navigation.rs` (residential edges), `world/mod.rs` (`is_open`),
`sim/clock.rs` (`weekday`), `sim/routine.rs` (`Condition::OnWeekdays`,
`on_weekdays`), `sim/resident.rs` (hours + weekday gating in `select`),
`sim/cast.rs` (homes, timings, weekday activities), `sim/simulation.rs`
(weekday + midnight-carryover fix), `main.rs` (hours in output), tests.

**Architectural choices:** hours live on the location (the owner of "am I open");
weekday variation reuses the existing `Condition` seam rather than a new system;
shared residential nodes (not per-resident dwellings) as the simplest extensible
step.

**Tests added:** eight/eight world + seven routine (15 total) — shop open/close
windows, selection refuses a closed café, weekday routines differ, and *everyone
ends every day at home across a full week*. The week test caught a real
multi-day bug (midnight activity carryover recorded into the next day).

**Known limitations:** residences are shared nodes, not private dwellings; shops'
closed-on-Sunday is modelled at the routine level (workers rest) but the location
hours themselves don't yet vary by weekday; no interactions between co-located
residents yet (Phase 4).

**Commands:** `cd development/sprint-1 && cargo run` · `cargo test`

---

## Phase 4 — First social life ✅

**What became more alive:** the town stopped being a set of solitary paths that
merely cross. Now when people share a place they sometimes *notice* each other —
Hana gives Sofia a word of encouragement at the bakery, Agnes and Eva fall into
conversation on the square, Luca and Victor share a coffee in his corner — and
they carry the memory of it. Bonds visibly strengthen over days.

**Implemented:** `sim/social.rs` — a `Relationships` store (affinity + trust,
seeded from DS-001 §2) and a deterministic interaction resolver. Each tick,
present co-located residents at public places are paired in deterministic order;
a seeded FNV hash (no RNG) decides whether and how they interact, shaped by
relationship and place (encouragement, shared coffee, conversation, greeting,
recognition, disagreement). Residents gained a `memories` list; interactions are
also recorded structurally (`interactions`).

**Files changed:** `sim/social.rs` (new), `sim/resident.rs` (`Memory`,
`memories`, `is_present`), `sim/simulation.rs` (relationships, social pass,
structured interactions), `sim/mod.rs`, `world/location.rs` (`is_residential`),
`main.rs` (connections summary), `tests/social.rs` (new).

**Architectural choices:** the relationship store is the single owner of
affinity/trust; residents own their memories; the interaction system *proposes*
from world state and applies through those owners (never rewrites truth).
Determinism via a seeded hash, not RNG. Caps: one interaction per resident per
tick, one per pair per day; ~24 % base chance so co-location usually passes
quietly.

**Tests added (5):** interactions happen; are deterministic across runs;
strengthen bonds; cap at once per pair per day; leave memories. 20 tests total.

**Known limitations:** interactions don't yet change where a resident goes next
(that's Phase 5); no mood/temporary state yet; residents socialise only at public
places, not at home; dialogue is structured, not generated.

**Commands:** `cargo run` (see "Today's connections") · `cargo test`

---

## Phase 5 — Intentions and small deviations ✅

**What became more alive:** residents stopped being pure routine-executors. Now a
resident heading home who spots a friend nearby may change their mind and go join
them — a small, human swerve that comes from who is where *right now*, not from a
script. Because the bonds that drive it grow through Phase 4, the town's evenings
differ as friendships deepen.

**Implemented:** `sim/intention.rs` — `consider_social_detour`: when the routine
would send a resident home in the late-afternoon window, the intention layer looks
for a present friend at a reachable, open public place, checks there is time to
visit and still get home, and (behind a seeded gate) returns a `Deviation`. The
simulation applies it as a one-off visit, then the routine resumes (they head
home). Bounded to one deviation per resident per day.

**Files changed:** `sim/intention.rs` (new), `sim/resident.rs`
(`deviations_today`), `sim/simulation.rs` (presence snapshot + deviation hook in
selection), `sim/mod.rs`, `sim/social.rs` (one extra seeded bond), `main.rs`
(five-day deviation summary), `tests/intention.rs` (new).

**Architectural choices:** the routine stays the default; deviation only overrides
a "go home" plan (the safe, believable case) and is proven time-safe before it
triggers, so no resident is ever stranded. Determinism via the same seeded hash.
Presence is read from a start-of-tick snapshot to avoid borrow conflicts.

**Tests added (4):** residents deviate; deterministic; capped once per day; never
stranded. 24 tests total.

**Known limitations:** only one deviation type (the social detour); no needs/mood
driving choices yet; deviations read start-of-tick presence, so a friend who
arrives the same tick isn't seen until the next.

**Commands:** `cargo run` (see "Spontaneous deviations over five days") ·
`cargo test`

---

## Phase 6 — The Old Oak becomes living history ✅

**What became more alive:** the Oak stopped being a place to walk to and became a
thing with a past. It remembers that Agnes sat beneath it, that Tomas played
there, that Elias and Tomas met beside it one Wednesday evening — a small, growing
chronicle that exists whether or not the player ever looks.

**Implemented:** `sim/oak.rs` — `OldOak` (identity, age ~400, location, tallies,
append-only `history`) and `Season` (derived from the day; appearance in data).
The simulation records a visit when a resident performs `VISIT_OAK` (a child
"plays", an adult "sits"), gives the visitor an Oak memory, and records a
"gathering" when residents interact at the riverside. `readable_history` renders
the chronicle. Scarf/flowers event kinds are defined ready for matchday.

**Files changed:** `sim/oak.rs` (new), `sim/resident.rs` (`affordance_of`,
`is_child`), `sim/simulation.rs` (Oak field, visit + gathering recording),
`sim/mod.rs`, `main.rs` (Oak section), `tests/oak.rs` (new).

**Architectural choices:** the Oak owns its history (single owner); the simulation
*records into* it through `record`, never edits past entries. Visits are collected
during movement and applied after the borrow scope, keeping the Oak's mutation in
one place. History is plain data, ready to serialise.

**Tests added (5):** accumulates across days; deterministic; the child plays;
residents meet beside it; visitors carry a memory. 29 tests total.

**Known limitations:** seasons change slowly (four-week seasons), so a short run
stays in one season; the Oak's event-driven changes (scarf after a win, flowers
after a loss) arrive with matchday in Phase 7; no save/load yet (state is
serialisation-ready, not yet serialised).

**Commands:** `cargo run` (see "The Old Oak — …") · `cargo test`
