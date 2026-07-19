# ERA — Weather & Season Engine

**Status: PROPOSED.**

## Purpose

Owns weather, daylight, seasonal patterns and environmental effects on access, routines, mood probabilities and sound.

## Constitutional connection

Supports attachment by making the Club and district persistent, independent, legible and capable of reflecting consequence over time. Every implementation must pass the Human Test and preserve the Relational Axiom: consequential agency inside an independent world.

## Owns

The authoritative state and rules implied by the purpose above. Exact schemas remain open.

## Must not own

It does not directly dictate emotion or story.

## Dependencies

Time, Persistence.

## Inputs and outputs

Inputs are explicit state reads or requests from dependent systems. Outputs are versioned state changes and domain events, never hidden side effects.

## First proof

A rainy winter day changes place use and movement without scripted exceptions.

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
