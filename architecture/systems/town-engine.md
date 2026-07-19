# ERA — Town Engine

**Status: PROPOSED.**

> **Related repository documents.** This is the *architecture-layer* brief for the
> Town Engine. Its founding **decision** is
> [`CD-006 — Simulate Intention, Not Movement`](../../creative-decisions/CD-006-simulate-intention-not-movement.md);
> its **technical strategy** (build-vs-buy, fidelity tiers, semantic-place graph,
> the six-week vertical slice) is
> [`research/town-engine-technical-strategy.md`](../../research/town-engine-technical-strategy.md);
> its **design intent** is [`living-world/interwoven-lives.md`](../../living-world/interwoven-lives.md).

## Purpose

Turns needs, routines, obligations, relationships and world conditions into resident intentions, then executes those intentions through semantic places and movement.

## Constitutional connection

Supports attachment by making the Club and district persistent, independent, legible and capable of reflecting consequence over time. Every implementation must pass the Human Test and preserve the Relational Axiom: consequential agency inside an independent world.

## Owns

The authoritative state and rules implied by the purpose above. Exact schemas remain open.

## Must not own

It does not own relationships, memories, culture, economy or narrative truth.

## Dependencies

Time, Persistence, Place Graph, Relationship, Event, Weather.

## Inputs and outputs

Inputs are explicit state reads or requests from dependent systems. Outputs are versioned state changes and domain events, never hidden side effects.

## First proof

A resident reaches an appropriate place for an intelligible reason, can be interrupted, and recovers without breaking the day.

## Failure modes

- hidden authority overlap with another system;
- behavior that cannot explain its cause;
- content loops visible to the player;
- state that cannot survive save/load or off-screen simulation;
- AI-generated exceptions that bypass authored rules.

## Open questions

- Exact data model and update frequency.
- Deterministic versus stochastic behavior boundaries.
- Authoring tools required for designers.
- Performance and simulation-fidelity budgets.
