# CD-006 — Simulate Intention, Not Movement

| Field | Value |
|---|---|
| ID | CD-006 |
| Status | **PROPOSED — awaiting Roy's ratification** |
| Date | 2026-07-19 |
| Domain | Living World · Simulation Architecture |
| Related material | `living-world/README.md`, `living-world/interwoven-lives.md`, `living-world/places.md`, IP-002 axiom AR |
| Technical companion | `research/town-engine-technical-strategy.md` |

## Problem

ERA's district cannot feel alive if residents merely spawn near the player, follow decorative loops, or select arbitrary destinations. Every visible movement must have a credible reason: a resident should be in the right place, at the right time, for a reason consistent with their obligations, relationships, history, the football calendar, weather, and events.

The visible requirement sounds like pathfinding, but pathfinding only answers **how an agent reaches a destination**. It does not answer **why that destination was selected**, whether the timing is appropriate, or whether an interruption should alter the plan.

## Alternatives considered

### 1. Script every route and appearance

Rejected as the primary architecture. It gives exact authorial control but becomes brittle, expensive, repetitive, and unable to support years of shared life. It can still be used for milestone scenes and protected narrative beats.

### 2. Spawn contextual ambience around the player

Rejected. It produces apparent activity without a coherent world state. Residents can appear in contradictory places, relationships do not persist, and the town performs for the player rather than continuing independently.

### 3. Let generative AI decide what everyone does

Rejected as the authority layer. It is difficult to reproduce, test, constrain, budget, and debug. It risks violating the Human Test and silently inventing story. Generative systems may later add bounded texture, but must not own schedules, world truth, or movement authority.

### 4. Buy a complete off-the-shelf NPC solution

Rejected as the full answer. Existing navigation, crowd, behavior, and conversational products solve valuable lower layers, but none should be assumed to provide ERA's persistent social timetable, relationship web, football context, long-term causality, and authored multi-year arcs as one coherent system.

## Discovery

**ERA should not primarily simulate movement. It should simulate intention. Movement is the visible consequence.**

A resident first forms or receives an intention:

- open the bakery before dawn;
- meet someone at the café;
- look for the Old Dog;
- attend a memorial;
- avoid the plaza after an argument;
- leave early for a derby;
- shelter when the weather turns;
- revisit a place connected to an old memory.

The execution layer then turns that intention into a destination, route, animation, interaction, delay, interruption, or cancellation.

## Decision

ERA will develop a proprietary orchestration layer, provisionally named **the Town Engine**, responsible for selecting, reconciling, and executing resident intentions inside one persistent shared world state.

The Town Engine is not a replacement for the game engine. It sits above navigation, crowd avoidance, animation, and rendering, and below authored world design.

Its minimum conceptual stack is:

1. **World truth** — time, calendar, weather, football state, places, closures, occupancy and persistent history.
2. **Resident state** — role, home, needs, obligations, habits, mood, relationships, current context and long-term arc.
3. **Intention generation** — scheduled obligations, relationship-driven goals, event-driven goals, personal habits and bounded authored opportunities.
4. **Arbitration** — priority, urgency, compatibility, travel time, capacity, conflicts and interruption rules.
5. **Execution** — destination reservation, path request, interaction slot, animation and fallback behavior.
6. **Continuity** — outcomes update memory, relationships, future schedules and world state.
7. **Presentation fidelity** — full simulation near the player; cheaper state transitions and statistical movement when distant.

## Why this survived

It preserves the constitutional balance in IP-002's Relational Axiom: the player may influence the Club, but the world has independent momentum. Residents do not exist solely for presentation, yet their behavior remains authored, bounded, testable and meaningful.

It also supports the Living World's requirement that all lives run on **the same rails**. A shared scheduler and world state allow encounters to be consistent, co-witnessed and remembered instead of generated as isolated scenes.

## Design consequences

- Every visible resident action should have an inspectable reason in the simulation state, even when that reason is never shown to the player.
- Places require semantic functions and capacity, not only coordinates: bakery counter, café table, bridge viewpoint, stadium gate, memorial position, shelter point, and so on.
- Relationships must be capable of creating, modifying and cancelling intentions.
- Match days, seasons, weather and major events operate as global schedule transforms rather than decorative skins.
- Authored multi-year milestones remain protected; daily life fills the spaces between them without contradicting them.
- The player sees fragments, not the scheduler. The system must never expose itself as a task board or quest machine.

## Technical consequences

- Build the **Town Engine brain** as ERA-owned code and data.
- Use off-the-shelf technology underneath it for navigation, pathfinding, crowd avoidance, animation, state machines and optional conversation.
- Keep deterministic seeds, event logs and reason codes so every surprising movement can be reproduced and debugged.
- Separate logical simulation from visual embodiment so distant residents can continue living without full character actors.
- Treat generative AI as an optional bounded service for expression or low-stakes variation, never as the authoritative simulation clock.

## Risks and failure modes

- **Over-simulation:** engineering a city simulator when the player only needs convincing fragments.
- **Mechanical regularity:** schedules become visible loops and residents feel robotic.
- **Chaos without meaning:** too many interruptions create noise rather than life.
- **Contradiction:** residents appear in mutually impossible places or miss protected events.
- **Performance:** all residents run expensive logic at full fidelity.
- **Authoring burden:** every resident requires too much bespoke data.
- **Invisible excellence:** significant complexity produces behavior the player never notices.

These risks require aggressive tooling, simulation-level LOD, authored templates, automated validation, and a small vertical slice before scaling.

## Open questions

1. Which engine will host ERA: Unreal, Unity, or another stack?
2. How many named, minor and micro-life agents must be logically simulated at once?
3. What time scale and offline progression rules apply when the player is absent?
4. Which events are protected authored milestones, and which may emerge?
5. How much resident reasoning must be inspectable to designers in editor tooling?
6. Where, if anywhere, should generative dialogue or planning enter the stack?

## Ratification required

Roy must ratify the principle and provisional name before either becomes canonical:

> **ERA simulates intention; movement is its visible consequence.**

> **The Town Engine** is ERA's proprietary orchestration layer for persistent resident life.
