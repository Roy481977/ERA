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
