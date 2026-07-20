# DS-004 — Sprint 2: A Town You Recognise (progress)

**Status: PROPOSED (implementation tracking).** Sprint 2 works under
[`DEV-000`](DEV-000-development-constitution.md), climbing the **Ladder of Life**
from where Sprint 1 left off (the world exists, residents act and remember): making
**memory and relationships change behaviour** (rung 4–5) and become **observable**
without numbers. Small reviewable commits; determinism preserved.

Guiding tests from DEV-000: does it improve the engine? does it improve the lived
experience? If a change can't be observed, it isn't done.

---

## Step 1 — Relationships become visible through behaviour ✅

**What became more alive:** you can now *see* who is close to whom without being
told a number. Close friends who find themselves together **stay a little longer** —
Hana lingers with Sofia at the bakery, Victor and Luca over coffee — and, watched
across a month, each resident's **signature habit** and the town's **bonds and
gathering places** surface on their own.

**Implemented:**

- **Lingering (behaviour changed by a relationship).** When a resident's activity
  is ending at a public place and a close friend (affinity ≥ 3) is present, they
  extend their stay — logged as behaviour ("lingers a little longer, enjoying
  Sofia's company"). Bounded (≤ 2 extra ticks/resident/day, daytime only) so the
  day stays coherent and no one is stranded.
- **The `chronicle` observer.** `cargo run -- chronicle` watches the town for a
  month and reports, as behaviour not numbers: what each resident is *known for*
  (their most-repeated daytime pursuit and when), who *keeps finding each other*
  and where, where the town *gathers*, and the weekly matchday *rhythm*. This is
  DEV-000's success test — watch without touching the controls and start telling
  stories.

**Files changed:** `sim/resident.rs` (`lingered_today`), `sim/simulation.rs`
(`linger_with_friend` in the Performing branch), `main.rs` (`chronicle` mode),
`tests/companionship.rs` (new).

**Architectural choices:** lingering reuses the start-of-tick presence snapshot and
the relationships store — no new system, no lookahead, no architecture change. The
chronicle derives everything from already-recorded structured data (interactions,
Oak history) and the event log.

**Tests added (4):** friends linger; bounded per day; deterministic; never
stranded. **38 tests total.**

**Known limitations:** lingering is the only relationship-driven behaviour so far;
deeper companionship — *waiting for* a friend and *leaving together* — needs each
resident to know others' intended next destination, i.e. a "decide-then-act"
two-phase tick. That is an architectural evolution (it also underpins group
movement and emergent traditions), so it is flagged for a decision rather than
built silently.

**Commands:** `cargo run -- chronicle` · `cargo test`

---

## Next candidates (climbing the ladder)

- **Decide-then-act tick** → true companionship (wait for / leave with a friend),
  the first clearly *architectural* step; surfaced for Roy's decision.
- **Needs/mood** feeding selection, so routines and deviations flex for reasons the
  world can see (DEV-000: Explainability, Emergence).
- **Emergent traditions** (rung 7): detect a repeated behaviour and let it harden
  into a named tradition the town keeps.
