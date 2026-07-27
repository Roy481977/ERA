# CD-028 — The simulation is the lead designer

**Date:** 2026-07-27
**Status:** PROPOSED (from Roy's Phase 4 directive; awaiting ratification)
**Domain:** Process — how ERA evolves from here

## The decision

From Phase 4 onward, **ERA's evolution comes primarily from observing
believable lives, not from inventing design ideas.** District 01 is frozen;
the town may change only when repeated simulated evidence justifies it. The
environment team responds to evidence; it does not originate change.

## The method (established by the first resident)

- Residents' weeks are **computed, never written** — deterministic seed,
  frozen level data (`district_level.py`), neighbours with independent
  routines, encounters as co-presence, traces as events (`sim_resident.py`,
  superseded by `sandbox.py` + `story_metrics.py`).
- Findings are **counters, not impressions**; unnatural moments are recorded
  as evidence, never fixed inline.
- Changes are the smallest possible: a bench before a square, behaviour
  before layout, and "insufficient evidence — hold" is a valid verdict.

## First applications

- **June Hartley week (seed 27):** validated the Weave crossing, allotments,
  school crossing; surfaced one emergent defect (her Friday shift silently
  swallowed the standing café date); produced ADJ-5 (market bench into the
  bus-shelter rain shadow) + BEH-1..3 + SIM-1; explicitly held bench B, the
  bus stop and weekday market emptiness at n=1.
- **Sandbox month (14 residents):** rhythms, routines (65→73% stability) and
  the trace clock emerged unscheduled; the bus shelter manufactured the
  Dev–Tomas friendship; bench B exonerated (41 visits, no grief rule);
  social saturation at n=14 identified (40+ residents needed for
  familiar-stranger texture).
- **Story Metrics layer:** rituals / looms / adoption / intersection /
  forgotten / attachment drivers, operationally defined. Headlines: the Oak
  is adopted by few, deeply (the service workers); **scarcity creates
  ritual** — narrow-hours places out-attach all-day places 0.43 vs 0.29,
  independently confirming CD-027's time-composition from behaviour alone;
  attachment metrics amplify instrument error (audit the sim through the
  story layer first).

## Consequences

- A standing evidence queue replaces design sprints; residents are chosen to
  load untested places, not to be interesting.
- Every proposed town change must cite log lines or counters.
- CD-025's trace economy is measured per resident-week (June: 32 events,
  max 3 concurrent — within budget).

## Authority

Directed by Roy (Phase 4 brief). Recorded by the environment team, which
hereby demotes itself to second designer.
