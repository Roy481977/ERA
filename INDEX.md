# ERA — Master Index

The single map of the ERA knowledge repository. Start here. Governance and the
rules that bind this repository live in [GOVERNANCE.md](GOVERNANCE.md); the full
history of changes lives in [CHANGELOG.md](CHANGELOG.md).

**Status:** Initialized 2026-07-19. GitHub mirror live. No design content yet —
this is scaffolding, awaiting the first material.

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

Live counts. All zero at initialization.

| Status | Count | Location |
|---|---|---|
| CANONICAL | 0 | `canon/` |
| PROPOSED | 0 | `proposed/` |
| OPEN | 0 | `open/` |
| REJECTED | 0 | `rejected/` |
| SUPERSEDED | 0 | `superseded/` |
| RESEARCH | 0 | `research/` |
| DRAFT | 0 | `draft/` |

---

## Document register

No design documents yet. As documents are created, each is listed here with its
status, purpose, and cross-references.

| Doc | Status | Purpose |
|---|---|---|
| GOVERNANCE.md | meta | Repository constitution & classification law |
| INDEX.md | meta | This master map |
| CHANGELOG.md | meta | Change history |

---

## Decision record

Governance-level decisions, most recent first. Design decisions are recorded in
their own documents and in CHANGELOG.

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

Unresolved questions the repository is tracking. None design-level yet.

- **OQ-1 (infrastructure) — RESOLVED 2026-07-19.** GitHub authentication for the
  mirror push. Resolved via fine-grained PAT; mirror live at `Roy481977/ERA`.
  Retained here for traceability.

---

## How to use this repository

- To understand the rules: read GOVERNANCE.md.
- To find any document: use the Document register above.
- To see what changed and when: read CHANGELOG.md.
- To hand this to a new team member or AI: INDEX.md → GOVERNANCE.md →
  `constitution/` → the canonical domains. That path should be self-sufficient
  without the original conversations.
