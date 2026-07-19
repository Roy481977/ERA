# WI-01 · Acceptance Tests

**Status: PROPOSED.** The slice is not "done" until every test passes. Each test
states a checkable assertion and how it is verified (via the tools in
`observability-and-debugging.md`). These consolidate Roy's list, the Town Engine
strategy's ten tests, and the roadmap exit proofs.

## Core behavioral tests

**AT-1 — Semantically correct places.** Every resident action targets an
**affordance** appropriate to its purpose (Hana → `WORK_BAKERY_COUNTER`, not a
random tile).
*Verify:* the "why is this person here?" trace shows purpose → affordance match
for a full day, zero mismatches.

**AT-2 — Schedules bend, not break.** When a place is closed / full / unreachable
or an intention is blocked, the resident **defers, re-routes, or substitutes** and
records a reason — never freezes, teleports, or drops the intention.
*Verify:* inject closures/capacity limits; the reason log shows fallbacks, the
contradiction report is empty.

**AT-3 — Relationships alter behavior.** A relationship (obligation/bond) visibly
changes what a resident does (Hana leaves the first roll; Tomas *sometimes*
searches for the Old Dog; the storm sends the couple to shelter together).
*Verify:* disable an edge → the dependent intention disappears; re-enable → it
returns. Behavior is attributable to the edge in the trace.

**AT-4 — Interruptions propagate correctly.** An interruption (the storm, a
relationship event) alters the current plan *and* its downstream consequences
(a missed appointment is noticed; a deferred task resumes).
*Verify:* the event causality graph links interruption → changed intentions →
resumed/failed outcomes with reason codes.

**AT-5 — No teleport, no silent reset.** No resident occupies two places at once;
travel time is accounted for before appointments; no one is silently relocated or
reset.
*Verify:* automated contradiction report over a simulated month returns zero
impossible-position and zero unexplained-relocation events.

**AT-6 — One world state, visible from every system.** Every engine reads the
same authoritative facts; there are no contradictory copies (no two memories of
one event, no divergent clocks).
*Verify:* cross-engine state diff at random ticks shows a single owner per fact
and identical reads; no duplicated authority.

**AT-7 — AI cannot rewrite authoritative truth.** The AI Director can only rank
already-valid options; it cannot author or mutate a fact.
*Verify:* attempt an AI mutation of owned state → rejected with reason; the
`SelectionSuggested` log shows only choices among valid options.

## Continuity & determinism tests

**AT-8 — Matchday transforms flows, not skins.** `day_type = matchday` materially
changes movement, work, gathering, and aftermath across the district — not just
decoration.
*Verify:* compare weekday vs matchday flow maps; distributions differ
structurally (convergence on the gate, pub after).

**AT-9 — Offscreen continuity matches.** Fast-forwarded Tier-2/3 outcomes remain
causally consistent when residents become visible again (no snap corrections).
*Verify:* simulate two weeks absent, then embody; the world-state timeline shows a
continuous causal chain, no discontinuities.

**AT-10 — Deterministic replay.** The same seed reproduces the same day exactly.
*Verify:* run twice from one seed → identical event logs and final state.

**AT-11 — Designer legibility (<10s).** A designer can answer *"Why is Hana
here?"* in under ten seconds.
*Verify:* the intention inspector surfaces purpose, provenance, affordance, and
reason code in one view.

**AT-12 — No permanent stuck / silent disappearance.** Across a simulated month,
no resident becomes permanently stuck or silently vanishes.
*Verify:* liveness monitor over the month; every resident has forward progress or
an explained absence.

## Emotional exit proof (roadmap Phase 1)

**AT-13 — Believability.** Observers can watch **thirty minutes** without seeing
obvious looping, impossible travel, crowd teleportation, or residents repeatedly
choosing inappropriate places — and spontaneously infer routines and
relationships.
*Verify:* structured observation session; note any immersion-breaking event.
