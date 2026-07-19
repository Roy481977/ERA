# ERA — Event Engine

**Status: PROPOSED.**

## Purpose

Owns event definitions, eligibility, triggers, stages, participants, consequences, cooldowns and resolution.

## Constitutional connection

Supports attachment by making the Club and district persistent, independent, legible and capable of reflecting consequence over time. Every implementation must pass the Human Test and preserve the Relational Axiom: consequential agency inside an independent world.

## Owns

The authoritative state and rules implied by the purpose above. Exact schemas remain open.

## Must not own

It does not choose every event for pacing; that belongs to the AI Director.

## Dependencies

Time, Persistence and all domain systems.

## Inputs and outputs

Inputs are explicit state reads or requests from dependent systems. Outputs are versioned state changes and domain events, never hidden side effects.

## First proof

An event begins, evolves and resolves without orphaned state or contradictory participants.

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
