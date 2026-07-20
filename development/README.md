# ERA — Development

Implementation of ERA, working **from** the ratified `architecture/` module — not
redesigning it. Each sprint has a spec (`DS-###`) and code.

- [`DS-001-first-breath.md`](DS-001-first-breath.md) — Sprint 1 spec: the smallest
  living district that can be executed and observed.
- [`DS-002-living-world.md`](DS-002-living-world.md) — intentions, relationships,
  the Old Oak, matchday, the observer.
- [`DS-003-sprint-1-report.md`](DS-003-sprint-1-report.md) — Sprint 1 report.
- [`DS-004-sprint-2.md`](DS-004-sprint-2.md) — Sprint 2: relationships change
  behaviour; social memory and continuity.
- [`DS-005-sprint-3-density.md`](DS-005-sprint-3-density.md) — Sprint 3: a
  continuously living district (ambient density).
- [`DS-006-live-engine.md`](DS-006-live-engine.md) — prototype → the beginning of
  the live engine: a continuously-ticking `Engine`, live inspectable snapshots, and
  a renderer driven from state.
- [`sprint-1/`](sprint-1/) — the code: a headless, deterministic core in **Rust**
  (per [`CD-007`](../creative-decisions/CD-007-core-language-rust.md)), plus the
  `Engine` and the live viewer.

All implementation is PROPOSED until Roy ratifies. Build in phases, small
reviewable commits; stop and ask when the architecture is genuinely missing.
