# ERA Import Package IP-003 — Systems Architecture Foundation

| Field | Value |
|---|---|
| Package | IP-003 |
| Stream | Design Translation / Architecture |
| Title | Systems Architecture Foundation |
| Date | 2026-07-19 |
| Status | **PROPOSED — nothing canonical.** |
| Source | Developed by Roy and ChatGPT after CD-006 and the Town Engine technical strategy. |

## Intent

ERA now has enough philosophical and living-world clarity to identify the major systems that must exist beneath the experience. This package creates a first architecture layer so the team can solve existential systems early, in dependency order, rather than discovering them piecemeal during implementation.

It does not specify production code. It defines system responsibilities, boundaries, dependencies, risks, and the first proof each system must pass.

## Core architectural proposition

ERA should be built as a **federation of living systems** sharing one authoritative world state and one persistent clock. No single “AI director” should secretly own the world. Each system has a narrow responsibility, publishes legible state changes, and can be tested independently.

The player should experience one coherent Club and district. Engineering should see explicit domains with clear contracts.

## New module

Create:

```text
architecture/
  README.md
  system-map.md
  execution-roadmap.md
  systems/
    town-engine.md
    time-engine.md
    world-persistence-engine.md
    relationship-engine.md
    memory-engine.md
    recognition-engine.md
    event-engine.md
    matchday-engine.md
    club-culture-engine.md
    economy-engine.md
    narrative-engine.md
    ai-director.md
    crowd-engine.md
    weather-season-engine.md
    audio-ecology-engine.md
```

## Classification recommendation

All architecture documents remain **PROPOSED** until Roy ratifies their boundaries. Their existence as repository artifacts does not make their design decisions canonical.

## Why now

CD-006 established the first major subsystem decision: ERA simulates intention and uses movement as its visible consequence. That decision exposed the need for neighboring systems: time, persistence, relationships, events, memory, recognition, culture, matchday, economy, narrative and presentation layers.

Without an architecture map, these systems will overlap, contradict one another, or be hidden inside a monolithic AI layer.

## Key decisions proposed

1. One authoritative persistent world state.
2. One shared simulation clock, with multiple fidelity tiers.
3. Domain systems own facts; presentation systems render them.
4. AI proposes and orchestrates inside authored bounds; it does not own truth.
5. Every meaningful change is inspectable, attributable and reversible in development.
6. Systems are built in dependency order through vertical slices, not all at once.
7. The first target is a convincing district day, not a feature-complete game.

## Open questions

- Whether `architecture/` should become a permanent first-class repository module or remain under `research/` until a second architecture decision is ratified.
- Engine choice and implementation language.
- Required offline simulation depth while the player is absent.
- Which systems run deterministically and which permit stochastic variation.
- Which state changes require immutable historical records versus mutable current state.
