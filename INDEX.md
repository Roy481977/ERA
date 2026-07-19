# ERA — Master Index

The single map of the ERA knowledge repository. Start here. Governance and the
rules that bind this repository live in [GOVERNANCE.md](GOVERNANCE.md); the full
history of changes lives in [CHANGELOG.md](CHANGELOG.md).

**Status:** 2026-07-19. GitHub mirror live. First Import Package **IP-001
(Worldview Foundation)** distilled, organized into five sections, and confirmed
by Roy — held **PROPOSED**, pending explicit ratification. No canonical content
yet. Next phase: Human Attachment Research (see GOVERNANCE §6).

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
intake/             ← ERA Import Packages (IP-###), the intake records
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
| PROPOSED | 1 | `intake/IP-001` |
| OPEN | 0 | `open/` |
| REJECTED | 0 | `rejected/` |
| SUPERSEDED | 0 | `superseded/` |
| RESEARCH | 0 | `research/` |
| DRAFT | 0 | `draft/` |

Note: IP-001 holds **15 accepted truths + 1 candidate** (AT-4, proposed/not
final), **8 key constitutional principles**, **7 open questions** (OQ-2…OQ-8) and
**4 rejected directions**. On ratification these split into `constitution/`,
`open/` and `rejected/`, and the counts update accordingly.

---

## Document register

| Doc | Status | Purpose |
|---|---|---|
| GOVERNANCE.md | meta | Repository constitution & classification law |
| INDEX.md | meta | This master map |
| CHANGELOG.md | meta | Change history |
| intake/IP-001-worldview-foundation.md | PROPOSED | First Import Package: the converged worldview (accepted / open / rejected) |

---

## Decision record

Governance-level decisions, most recent first. Design decisions are recorded in
their own documents and in CHANGELOG.

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

- **OQ-2 — Presence vs. authenticity (AI vs. human).** Is authentic simulation
  sufficient for belonging, or is real human presence required? Largest open
  question.
- **OQ-3 — Does "grown, not built" under-serve football's competitiveness?**
- **OQ-4 — The arrow of real time / stepping away.** Returning to a Club reshaped
  in your absence: strength or alienation?
- **OQ-5 — Newcomers vs. veterans.** Does accumulated history gatekeep the new?
- **OQ-6 — Structure of the Emotional Pillars.**
- **OQ-7 — The negative promises** (what ERA constitutionally refuses to do).
- **OQ-8 — The boundary of emergent culture** (can the Club hold ground against
  the owner?).

---

## How to use this repository

- To understand the rules: read GOVERNANCE.md.
- To find any document: use the Document register above.
- To see what changed and when: read CHANGELOG.md.
- To hand this to a new team member or AI: INDEX.md → GOVERNANCE.md →
  `constitution/` → the canonical domains. That path should be self-sufficient
  without the original conversations.
