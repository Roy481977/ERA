# ERA — Systems Architecture

**Status: PROPOSED.**

This module describes how ERA's major living systems divide responsibility and cooperate. It sits between design philosophy and technical implementation.

It is not source code, not a feature backlog, and not a replacement for research. It defines:

- what each system owns;
- what it must never own;
- which systems it depends on;
- what state it publishes;
- what emotional promise it protects;
- what proof must exist before implementation expands.

## Architectural law

ERA is one living world, but it should not be one giant system.

The architecture is a federation of bounded systems sharing:

- a persistent world identity;
- one authoritative clock;
- explicit events and state transitions;
- a common semantic place graph;
- stable entity identities across years.

AI may recommend, compose and schedule. It may not silently rewrite authoritative facts.

## Layers

1. **Foundation:** Time, persistence, semantic geography.
2. **Life:** Town, relationships, crowd, weather and seasons.
3. **Meaning:** Memory, recognition, culture and narrative.
4. **Football:** Matchday and real-football consequence.
5. **Economy:** Resources, constraints and long-term consequence.
6. **Orchestration:** Event Engine and AI Director.
7. **Expression:** Audio ecology and visual movement.

See `system-map.md` and `execution-roadmap.md`.

## Placement

`architecture/` is a **top-level module** (Design Translation stream). Its
*content* is PROPOSED; whether it is a permanent first-class module is Roy's to
ratify (IP-003 open question) — the CKO has placed it top-level rather than under
`research/` because it is a distinct, growing domain.

## Reconciliation with the repository (CKO)

Each engine implements truths already in the repository. This map is the
cross-reference; the engine briefs need not be read to see their roots.

| Engine | Roots (philosophy · decision · design) |
|---|---|
| Time · World-Persistence · Semantic Place Graph | CD-006 "one shared clock / one authoritative world state" (= the living world's *same rails*); Town Engine strategy (semantic-place graph) |
| Town Engine | **CD-006** (simulate intention, not movement) · `research/town-engine-technical-strategy.md` · `living-world/interwoven-lives.md` |
| Relationship Engine | `living-world/interwoven-lives.md` (the web of edges); IP-002 A2 (bonds) |
| Crowd Engine · Weather & Season Engine | `living-world/README.md` (match day, richness, weather/time); Design Bible Vols V–VI |
| Memory Engine | IP-002 AT-9 / **CD-003** (Memory is the *mechanism* beneath Recognition) |
| Recognition Engine | IP-002 axiom A2 · **CD-003** · Relational Axiom AR (the independent Club reflects the player's mark back) |
| Club Culture Engine | **CD-002** (grown, not built) · IP-001 AT-5 (the Club owns its culture) |
| Narrative Engine | IP-002 A3 Meaning · **CD-004** · honest history AT-7 ("no false facts" = the Human Test) |
| Matchday Engine | `living-world` match day; IP-001 AT-2 Core Loop |
| Economy Engine | IP-001 AT-2 (the economy is part of the Core Loop, driven by the fantasy score) |
| Event Engine | `living-world/interwoven-lives.md` (authored milestones + emergent texture) |
| AI Director | the **Human Test** (AT-11 / CR-6) + Design Bible Vol VII: AI proposes/orchestrates inside authored bounds, never owns world truth |
| Audio Ecology Engine | `living-world` richness & sound; Design Bible Vol V |

**Architectural law ↔ constitution:** "one authoritative world state, one clock,
AI may not silently rewrite truth" is the engineering form of CD-006 and the
Human Test, and of the Relational Axiom (an *independent* world with consequential
player agency). No contradictions with canon-track were found on intake.
