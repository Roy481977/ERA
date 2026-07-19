# ERA — Matchday Engine

**Status: PROPOSED.**

## Purpose

Transforms a fixture into anticipation, preparation, travel, ritual, crowd state, commerce, emotion and aftermath.

## Constitutional connection

Supports attachment by making the Club and district persistent, independent, legible and capable of reflecting consequence over time. Every implementation must pass the Human Test and preserve the Relational Axiom: consequential agency inside an independent world.

## Owns

The authoritative state and rules implied by the purpose above. Exact schemas remain open.

## Must not own

It does not simulate the football match itself unless separately assigned.

## Dependencies

Time, Town, Crowd, Weather, Economy, Events, Audio.

## Inputs and outputs

Inputs are explicit state reads or requests from dependent systems. Outputs are versioned state changes and domain events, never hidden side effects.

## First proof

One fixture changes the whole district before, during and after kickoff.

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
