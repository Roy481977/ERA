# ERA — Architecture Execution Roadmap

**Status: PROPOSED.**

The goal is speed without architectural debt. Build proofs in dependency order and stop any system from expanding before it passes its emotional and technical test.

## Phase 0 — Contracts and observability (1–2 weeks)

Define entity IDs, world clock, event schema, semantic-place schema, state ownership, logging and replay. Build a developer inspector before building life.

**Exit proof:** one resident can be traced through every state transition with an explanation of why it happened.

## Phase 1 — One convincing day (6 weeks)

Build the Town Engine vertical slice with:

- 12 named residents;
- 40 minor residents;
- 8 semantic places;
- one ordinary weekday;
- one matchday;
- weather variation;
- interruptions and relationship-driven encounters;
- four simulation fidelity tiers.

**Exit proof:** observers can watch thirty minutes without seeing obvious looping, impossible travel, crowd teleportation or residents repeatedly choosing inappropriate places.

## Phase 2 — Continuity (4–6 weeks)

Add persistent time, absences, relationship change, memory traces and return-state simulation.

**Exit proof:** after simulated weeks, the district has changed in legible ways and every change has a causal history.

## Phase 3 — Meaning (6–8 weeks)

Add Recognition, Club Culture and Narrative selection.

**Exit proof:** the world reflects a player-authored decision back later without a quest marker, explicit reward panel or fabricated explanation.

## Phase 4 — Football pressure (6–8 weeks)

Add Matchday and Economy integration.

**Exit proof:** one fixture visibly alters anticipation, movement, commerce, rituals, relationships and aftermath across the district.

## Phase 5 — Scale and production hardening

Scale population, years, save migration, deterministic replay, performance budgets, authoring tools and testing automation.

## Build discipline

- Build one vertical slice, not fifteen disconnected prototypes.
- Every system needs a debug view before content scale.
- Every autonomous action must expose a reason chain.
- No LLM may directly mutate authoritative state.
- Off-screen simulation uses lower fidelity but preserves causal consistency.
