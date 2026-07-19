# WI-01 — System Contracts & Vertical Slice Specification

**Status: PROPOSED** (inside the ratified `architecture/` module).

## Goal

Turn the conceptual architecture (IP-003, the system map, the execution roadmap)
into something an **engineering team can begin implementing without inventing the
core rules themselves.** This work item defines the shared world-state schema,
the exact boundary of every engine, the contracts between engines, the first
Town Engine vertical slice, its acceptance tests, and the observability required
to prove it.

## Scope guardrail (explicit)

- **No new engines.** Only the 15 engines already in `../system-map.md`.
- **No scope broadening** beyond these contracts and the vertical slice until they
  are sufficiently defined and Roy is satisfied.
- The first target is **a convincing district day**, not a feature-complete game.

## Documents

1. [`world-state-schema.md`](world-state-schema.md) — the authoritative world-state
   schema and per-field ownership.
2. [`engine-boundaries.md`](engine-boundaries.md) — what each engine owns / may
   read / may propose / may mutate / must never control.
3. [`inter-engine-contracts.md`](inter-engine-contracts.md) — inputs, outputs,
   events, commands, failure behavior, determinism per engine.
4. [`vertical-slice.md`](vertical-slice.md) — the Town Engine vertical slice
   (one district, 25–40 residents, weekday + matchday + a disruptive event,
   persistence across absence).
5. [`acceptance-tests.md`](acceptance-tests.md) — the checkable proofs the slice
   must pass.
6. [`observability-and-debugging.md`](observability-and-debugging.md) — the tools
   that make every autonomous action inspectable.

## Invariants these contracts enforce (from IP-003 + the system map)

- **One authoritative persistent world state.** One source of truth per fact.
- **One shared clock.** One `WorldClock`; multiple fidelity tiers read it.
- **Every fact has exactly one owner** engine. Others read, react, or *request* a
  change; they never duplicate authority.
- **Domain systems own facts; presentation systems render them.**
- **AI proposes and orchestrates inside authored bounds; it never owns or silently
  rewrites authoritative truth** (the Human Test governs anything it generates).
- **Every meaningful change is inspectable, attributable, and reversible in
  development** — every autonomous action exposes a *reason chain*.

## Reconciliation

Builds directly on: **CD-006** (simulate intention, not movement; reason codes;
fidelity tiers), the **Town Engine technical strategy** (`WorldState`, `Place`,
`Resident`, `Intention`, `Reservation`, `Encounter`, `ReasonCode`; the
semantic-place graph; the four tiers; the six-week slice), the **system map**
(engine ownership + core data flow), and the **execution roadmap** (Phase 0
contracts/observability → Phase 1 one convincing day). Terminology is kept
identical to those documents.
