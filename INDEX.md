# ERA — Master Index

The single map of the ERA knowledge repository. Start here. The apex canonical
philosophy is **[The Book of ERA](docs/book-of-era/00-the-promise-and-laws.md)** —
the canonical opening (`docs/book-of-era/00-the-promise-and-laws.md`), authored by
Roy (+ ChatGPT), which must not be edited directly (amendments are proposed
separately). It **supersedes** the earlier leaner drafts [BIBLE.md](BIBLE.md) and
[VISION.md](VISION.md), which are retained in place with pointers. Governance and
the rules that bind this repository live in [GOVERNANCE.md](GOVERNANCE.md); the full
history of changes lives in [CHANGELOG.md](CHANGELOG.md).

**Order of authority:** The Book of ERA → GOVERNANCE.md → development/DEV-000
(development constitution) → architecture → specs → code. When philosophy and
implementation conflict, philosophy wins and the implementation adapts. The engine
serves the world (the Book's *The Engine's Place*): the world is upstream.

**Status:** 2026-07-19. GitHub mirror live. Two Import Packages captured, both
**PROPOSED**: **IP-001 (Worldview Foundation)** and **IP-002 (Human Attachment
Research)**. No canonical content yet. Phase 2 reached a compression (axiom AR /
CE-6: "the player shapes the Club but never solely authors it"); axioms not yet
locked, wording open.

---

## Repository model

GitHub (`Roy481977/ERA`) is the **canonical** source of truth; the ERA Claude
project is the **live working copy** that mirrors to it. The mirror went live
2026-07-19. Path mapping: the project's `era/` path ↔ this repository's **root**.

---

## Directory plan

Folders are created only when the first real document needs them — no empty
structure invented ahead of content. Planned layout (relative to repo root):

```
INDEX.md            ← this file: master map + status dashboard
GOVERNANCE.md       ← constitution: authority, classification law, protocols
CHANGELOG.md        ← every change, dated. Nothing changes silently.
intake/             ← ERA Import Packages (IP-###): discoveries (the WHAT)
creative-decisions/ ← Creative Decisions (CD-###): why a discovery won (the WHY)
research/           ← external inputs + technical evaluations (e.g. Town Engine)
architecture/       ← systems architecture (RATIFIED permanent module; contents PROPOSED)
development/        ← implementation: sprint specs (DS-###) + code (works from architecture)
living-world/       ← the district: places, residents, interwoven lives, mysteries
constitution/       ← ERA's foundational principles (the design Constitution)
canon/              ← CANONICAL, approved by Roy, split by domain
proposed/           ← PROPOSED, awaiting Roy's ruling
open/               ← OPEN unresolved questions
rejected/           ← REJECTED ideas, kept with reasons
superseded/         ← SUPERSEDED material, kept with replacement pointers
research/           ← RESEARCH: external inputs and technical evaluations informing ERA
draft/              ← DRAFT incomplete working material
```

Note: "Constitution" in the governance trace refers to ERA's foundational
design principles, which will live in `constitution/` once Roy establishes
them. It is distinct from GOVERNANCE.md, which governs the *repository*.

---

## Status dashboard

| Status | Count | Location |
|---|---|---|
| CANONICAL | 0 | `canon/`, `constitution/` |
| PROPOSED | 3 pkgs + living-world + architecture + 6 CDs | `intake/IP-001…IP-003`, `living-world/`, `architecture/`, `creative-decisions/` |
| OPEN | 0 | `open/` |
| REJECTED | 0 | `rejected/` |
| SUPERSEDED | 0 | `superseded/` |
| RESEARCH | 1 | `research/` (Town Engine technical strategy) |
| DRAFT | 0 | `draft/` |

Note: IP-001 holds **15 accepted truths + 1 candidate** (AT-4, proposed/not
final), **8 key constitutional principles**, **7 open questions** (OQ-2…OQ-8) and
**4 rejected directions**. IP-002 holds candidate axioms compressing toward
**three** (Relational · Recognition · Meaning), **6 compression events**, and
**8 candidate ratifications**. On ratification these split into `constitution/`,
`open/`, `rejected/` and `superseded/`, and the counts update accordingly.

---

## Document register

| Doc | Status | Purpose |
|---|---|---|
| GOVERNANCE.md | meta | Repository constitution & classification law |
| INDEX.md | meta | This master map |
| CHANGELOG.md | meta | Change history |
| intake/IP-001-worldview-foundation.md | PROPOSED | First Import Package (Philosophy): the converged worldview |
| intake/IP-002-human-attachment.md | PROPOSED | Second Import Package (Human Attachment Research): candidate axioms, compression events, constitutional consequences |
| intake/IP-003-systems-architecture-foundation.md | PROPOSED | Third Import Package (Design Translation): the federation-of-systems architecture proposition |
| sources/ (4 docs + manifest) | SOURCE | Roy's primary ERA corpus, verbatim, pending distillation — Design Bible, Book of ERA, Beginning, proposal chat |
| living-world/README.md | PROPOSED | The Living World (district) — consolidated from all three sources |
| living-world/places.md | PROPOSED | The district's places (emotional-geography spine) + place template |
| living-world/residents.md | PROPOSED | Residents system, template, and full cast biographies |
| living-world/interwoven-lives.md | PROPOSED | The shared-timeline web: lives interacting and aging across years ("the same rails") |
| living-world/the-quiet-mysteries.md | PROPOSED | The never-explained mystical root (the two moons) |
| creative-decisions/README.md | meta | Creative Decisions module: purpose, format, workflow, register |
| creative-decisions/CD-001…CD-005 | PROPOSED | Foundational Creative Decisions (why each survived): Attachment-not-addiction · Grown-not-built · Recognition-beneath-Memory · Meaning-split-from-Recognition · Relational-Axiom |
| creative-decisions/CD-006-simulate-intention-not-movement.md | PROPOSED | Simulate intention, not movement — the Town Engine principle |
| research/town-engine-technical-strategy.md | RESEARCH / PROPOSED | Town Engine build-vs-buy architecture + six-week vertical slice (technical companion to CD-006) |
| architecture/ (README, system-map, execution-roadmap) | PROPOSED | Systems architecture: federation of bounded systems, one world state + one clock; layer map; phased roadmap |
| architecture/systems/ (15 briefs) | PROPOSED | Subsystem briefs: town, time, world-persistence, relationship, memory, recognition, event, matchday, club-culture, economy, narrative, ai-director, crowd, weather-season, audio-ecology |
| architecture/system-contracts/ (WI-01, 7 docs) | PROPOSED | System Contracts & Vertical Slice: world-state schema, engine boundaries, inter-engine contracts, Town Engine vertical slice, acceptance tests, observability |
| **`architecture/` module itself** | **RATIFIED (permanent)** | The module is a permanent first-class part of the repository (contents remain PROPOSED) |
| development/DEV-000-development-constitution.md | **Active (RATIFIED)** | The development constitution: governs all implementation (Ladder of Life, memory-changes-behavior, relationships-through-behavior, emergence, observation-first). Sits alongside GOVERNANCE.md. |
| development/DS-001-first-breath.md | PROPOSED | Sprint 1 implementation spec (First Breath): district (now 8 locations), 10 residents, Old Oak, roadmap |
| development/DS-002-living-world.md | PROPOSED | Sprint 1 Phases 3–8 progress tracker (per-phase: what/files/choices/tests/limits) |
| development/DS-003-sprint-1-report.md | PROPOSED | Sprint 1 final report: commits, systems, tests, run commands, samples, next steps |
| development/DS-004-sprint-2.md | PROPOSED | Sprint 2 progress (under DEV-000): Step 1 — relationships change behaviour (lingering) + the `chronicle` observer |
| development/sprint-1/ (code) | in progress | **Rust** headless core, Phases 1–8: believable routines, residences + opening hours + weekday variation, social life (relationships/interactions/memories), small deviations, the living Old Oak, matchday, and a terminal observer. Deterministic; everyone home every day incl. matchday; **34 tests pass**. Lives in GitHub. |

---

## Decision record

Governance-level decisions, most recent first. Design decisions are recorded in
their own documents and in CHANGELOG.

- **2026-07-19 — Core language = Rust (CD-007); Sprint 1 Phase 2 shipped.** At
  Roy's direction, chose Rust for the authoritative engine-decoupled core
  (CD-007, PROPOSED) and migrated the tiny Phase-1 codebase from Python. Built
  **Phase 2**: WorldClock, resident entities, **routines** (goal+time proto-
  intentions, not fixed schedules), and a deterministic simulation loop. 10
  residents complete believable routines through the world (wake → work/errands →
  visit the Old Oak → home); deterministic, no teleporting, everyone ends at
  home; 11 tests pass. Game-engine choice still open (IP-003). Stopped at Phase 2
  for review.
- **2026-07-19 — Sprint 1 begins (DS-001 First Breath): Phase 1 shipped.**
  Transitioned from architecture into implementation, working from the ratified
  contracts. New `development/` module with the DS-001 spec (5 semantic locations,
  10 residents, the Old Oak living object, 4-phase roadmap) and **Phase 1 code**:
  world representation — locations + affordances, navigation graph (travel time,
  shortest path), World container + validation, an executable observer, and 7
  passing unit tests. Headless deterministic Python core; the game-engine choice
  (IP-003) is untouched and remains open. PROPOSED.
- **2026-07-19 — RATIFIED: `architecture/` is a permanent module** (Roy). First
  ratification in the repository. Only the *module's permanence* is canonical;
  IP-003 and every architecture document remain PROPOSED. Resolves the IP-003
  placement open question.
- **2026-07-19 — New work item: WI-01 System Contracts & Vertical Slice.** Created
  `architecture/system-contracts/` (7 docs): authoritative world-state schema with
  per-field ownership, engine boundaries (owns/reads/proposes/mutates/never), the
  inter-engine event+command contracts, the Town Engine vertical slice (one
  district, 25–40 residents, weekday/matchday/storm, persistence across absence),
  13 acceptance tests, and the six observability tools. Reconciled to CD-006, the
  Town Engine strategy, the system map, and the roadmap. Scope-guarded: no new
  engines. PROPOSED.
- **2026-07-19 — Intake: IP-003 + `architecture/` module (Systems Architecture
  Foundation).** All net-new; nothing live was replaced. Added IP-003 and a
  top-level `architecture/` module (README, system-map, execution-roadmap, 15
  subsystem briefs) proposing ERA as a **federation of bounded systems sharing one
  authoritative world state and one clock; AI proposes/orchestrates but never owns
  or rewrites world truth.** Added a CKO reconciliation map (each engine → its
  IP/CD/living-world roots) and cross-linked the Town Engine brief ↔ CD-006 ↔ the
  technical strategy. No contradictions found. PROPOSED — not promoted.
- **2026-07-19 — Intake: CD-006 + Town Engine (from Roy's repo update).** Intook
  an updated-repo zip; philosophy, living-world and sources were identical, so
  integrated only the new material: **CD-006 — Simulate Intention, Not Movement**
  (the Town Engine principle) and `research/town-engine-technical-strategy.md`
  (build-vs-buy + six-week vertical slice). Numbering (CD-006) and cross-refs
  verified; the zip's INDEX/CHANGELOG/GOVERNANCE/CD-README were **not** taken
  (older/parallel state missing CD-001–005 and GOVERNANCE §7). PROPOSED — not
  promoted.
- **2026-07-19 — Foundational Creative Decisions backfilled (CD-001…CD-005).**
  The reasoning behind the five foundational decisions is now captured: CD-001
  Attachment-not-addiction, CD-002 Grown-not-built (over "Partner"), CD-003
  Recognition-beneath-Memory, CD-004 Meaning-split-from-Recognition, CD-005 the
  Relational Axiom (over "Non-Control"). Each cross-referenced to its Import
  Packages. PROPOSED (CKO seeds) — awaiting ratification. New CDs now come from
  ChatGPT + Roy per the workflow.
- **2026-07-19 — New module: Creative Decisions (permanent architecture).** Added
  `creative-decisions/` to preserve *why* a discovery won over the alternatives —
  distinct from Import Packages (which describe the discovery). ChatGPT produces
  Creative Decisions; the CKO classifies, cross-references, links to Import
  Packages, indexes, and preserves them permanently. Recorded in GOVERNANCE §7.
- **2026-07-19 — Living World: interwoven lives ("the same rails").** Per Roy,
  documented the connective system: all lives interact on one shared timeline,
  bonding and aging across years, scripted at milestones with emergent daily
  texture (tens of lives, named + minor + micro). Boy-and-the-Old-Dog developed
  as the canonical worked example (bond, "sometimes" searches, squirrels, aging,
  a four-textures loss). New doc `living-world/interwoven-lives.md`. PROPOSED.
- **2026-07-19 — Living World: places + the two moons.** Defined the district's
  places (Club, Main Street, Plaza & Fountain, Riverside/Bridge/Oak, Museum
  Quarter, Academy, Railway) with a place template, and introduced the
  never-explained mystical root per Roy — the **two moons** — threaded silently
  through every place ("seen, never said"). Proposed the map unification (zones =
  spine, rings = radial reading). PROPOSED.
- **2026-07-19 — Living World module started.** Following Roy's steer to document
  the living aspect (the leading edge of the idea) well and within the main files,
  the living-world layer was consolidated from all three sources into
  `living-world/` (overview + residents), deduplicated and cross-referenced to the
  IP-002 axioms. First resident biography (the Old Dog) drafted to fill a
  ChatGPT-left gap. PROPOSED; CKO-proposed additions flagged.
- **2026-07-19 — Source corpus received (4 documents).** Roy handed over the
  full accumulated ERA material: the **Design Bible v0.1** (9-volume bible with
  its own 7-law Constitution), the **Book of ERA v1.2** (district / living-world
  layer), **"The Beginning"** (manifesto), and the **proposal ChatGPT chat**.
  Preserved verbatim under `sources/` (originals + text), unclassified and NOT
  canonical. To be distilled into Import Packages and reconciled with IP-001/
  IP-002. Two constitutional threads now coexist — reconciliation pending; key
  contradictions flagged (addiction vs attachment; football-as-skin vs
  constitutive). See `sources/README.md`.
- **2026-07-19 — IP-002 updated: Relational compression (CE-6 / axiom AR).**
  RQ-1 paid out: *deep attachment requires consequential agency inside an
  independent world* — "the player shapes the Club but never solely authors it";
  stewardship, not sovereignty. Fuses A1-authorship + A4; Independence and
  Vulnerability become derived; Meaning stands apart (set compresses 4 → 3). Four
  textures of loss kept as a derived model. CKO's "non-control" formulation
  rejected. Added CR-8. All PROPOSED, final wording open.
- **2026-07-19 — IP-002 (Human Attachment Research) captured.** Candidate axioms
  (externalized/vulnerable self, Recognition, Meaning, Independence), compression
  events, constitutional consequences, active research questions, and candidate
  ratifications. All PROPOSED. Adds the discovery-vs-explanation rule to
  GOVERNANCE §6.
- **2026-07-19 — IP-001 confirmed & restructured.** Roy confirmed the
  distillation and set the five-section form (Accepted Truths / Open Questions /
  Rejected Directions / Key Constitutional Principles / Decision Rationale). AT-4
  ("grown, not built") demoted to a candidate (proposed/not final). Core Loop
  (AT-2) amended: the economy is part of the loop, driven by the fantasy score.
  Package streams + phase shift recorded in GOVERNANCE §6. Still PROPOSED.
- **2026-07-19 — IP-001 (Worldview Foundation) received.** First Import Package;
  worldview distilled. Held PROPOSED, awaiting Roy's ratification to promote
  accepted truths to CANONICAL. See `intake/IP-001-worldview-foundation.md`.
- **2026-07-19 — Intake = ERA Import Packages.** Design material enters as
  structured ERA Import Packages from ChatGPT, not raw conversations. Raw
  conversations are recommended for packaging first unless Roy says otherwise.
  See GOVERNANCE §3.
- **2026-07-19 — GitHub mirror live.** Authenticated via a fine-grained PAT
  (Contents: read/write) scoped to `Roy481977/ERA`. Note: `api.github.com` is
  blocked by the container egress proxy, so sync uses the git transport over
  HTTPS, not the REST API.
- **2026-07-19 — Canonical home = GitHub; ERA project = live working copy.**
  Chosen by Roy.
- **2026-07-19 — Classification set = 7 statuses** (Canonical, Proposed, Open,
  Rejected, Superseded, Research, Draft), default-to-Open when uncertain. Per
  the CKO charter.

---

## Open questions register

- **OQ-1 (infrastructure) — RESOLVED 2026-07-19.** GitHub authentication for the
  mirror push. Resolved via fine-grained PAT; mirror live at `Roy481977/ERA`.
  Retained here for traceability.

Design-level open questions (from IP-001, full text in the package):

- **OQ-2 — Presence vs. authenticity (AI vs. human).** *Tentatively resolving via
  IP-002:* Recognition is a property of a living Club (Internal), amplified by
  real others (External) — belonging does not depend on multiplayer. Awaiting
  ratification.
- **OQ-3 — Does "grown, not built" under-serve football's competitiveness?**
- **OQ-4 — The arrow of real time / stepping away.** Returning to a Club reshaped
  in your absence: strength or alienation?
- **OQ-5 — Newcomers vs. veterans.** Does accumulated history gatekeep the new?
- **OQ-6 — Structure of the Emotional Pillars.**
- **OQ-7 — The negative promises** (what ERA constitutionally refuses to do).
- **OQ-8 — The boundary of emergent culture** (can the Club hold ground against
  the owner?).

Phase 2 research questions (from IP-002):

- **RQ-1 — PAID OUT (2026-07-19).** The root yielded the Relational compression
  (axiom AR / CE-6): *deep attachment requires consequential agency inside an
  independent world* — "the player shapes the Club but never solely authors it";
  stewardship, not sovereignty. Independence and Vulnerability become derived.
  Final wording open.
- **RQ-2 — Does vulnerability break out as its own axiom?** (Likely resolved:
  derived from AR — pending confirmation.)
- **RQ-3 — Is Internal Recognition sufficient on independence alone,** or must it
  channel a genuine valuing perspective (the Human Test tether)?

---

## How to use this repository

- To understand the rules: read GOVERNANCE.md.
- To find any document: use the Document register above.
- To see what changed and when: read CHANGELOG.md.
- To hand this to a new team member or AI: INDEX.md → GOVERNANCE.md →
  `constitution/` → the canonical domains. That path should be self-sufficient
  without the original conversations.
