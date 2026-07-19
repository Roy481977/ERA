# ERA — Master Index

The single map of the ERA knowledge repository. Start here. Governance and the
rules that bind this repository live in [GOVERNANCE.md](GOVERNANCE.md); the full
history of changes lives in [CHANGELOG.md](CHANGELOG.md).

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
living-world/       ← the district: places, residents, interwoven lives, mysteries
constitution/       ← ERA's foundational principles (the design Constitution)
canon/              ← CANONICAL, approved by Roy, split by domain
proposed/           ← PROPOSED, awaiting Roy's ruling
open/               ← OPEN unresolved questions
rejected/           ← REJECTED ideas, kept with reasons
superseded/         ← SUPERSEDED material, kept with replacement pointers
research/           ← RESEARCH: external inputs informing ERA
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
| PROPOSED | 2 pkgs + living-world | `intake/IP-001`, `intake/IP-002`, `living-world/` |
| OPEN | 0 | `open/` |
| REJECTED | 0 | `rejected/` |
| SUPERSEDED | 0 | `superseded/` |
| RESEARCH | 0 | `research/` |
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
| sources/ (4 docs + manifest) | SOURCE | Roy's primary ERA corpus, verbatim, pending distillation — Design Bible, Book of ERA, Beginning, proposal chat |
| living-world/README.md | PROPOSED | The Living World (district) — consolidated from all three sources |
| living-world/places.md | PROPOSED | The district's places (emotional-geography spine) + place template |
| living-world/residents.md | PROPOSED | Residents system, template, and full cast biographies |
| living-world/interwoven-lives.md | PROPOSED | The shared-timeline web: lives interacting and aging across years ("the same rails") |
| living-world/the-quiet-mysteries.md | PROPOSED | The never-explained mystical root (the two moons) |
| creative-decisions/README.md | meta | Creative Decisions module: purpose, format, workflow, register |
| creative-decisions/CD-001…CD-005 | PROPOSED | Foundational Creative Decisions (why each survived): Attachment-not-addiction · Grown-not-built · Recognition-beneath-Memory · Meaning-split-from-Recognition · Relational-Axiom |

---

## Decision record

Governance-level decisions, most recent first. Design decisions are recorded in
their own documents and in CHANGELOG.

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
