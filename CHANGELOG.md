# ERA — Changelog

Every change to the repository, dated, newest first. Nothing changes silently.
Historical reasoning is never deleted — superseded and rejected material is
retained in place, this log records the reasoning.

Format: `YYYY-MM-DD — summary`, followed by details.

---

## 2026-07-19 — IP-002 (Human Attachment Research) captured — PROPOSED

Second Import Package, opening the Human Attachment research repository. Curated
from the Phase 2 dialogue into six sections: Candidate Axioms (externalized/
vulnerable self, Recognition, Meaning, Independence, plus an exploratory root and
the tension meta-truth), Compression Events (five discoveries that reduced the
philosophy), Constitutional Consequences (what each discovery strengthens/
weakens/replaces/creates), Active Research Questions (RQ-1…RQ-3), Rejected/
Demoted Ideas, and Candidate Ratifications (CR-1…CR-7).

Notable movements (all PROPOSED, none canonical):
- Recognition rises toward bedrock; **Memory demoted** to a mechanism.
- **"The player is never the sole author"** generalizes and would supersede
  "reality is the Club's co-author" (AT-6).
- The four Internal-Recognition conditions collapse into one ("independent of the
  present self").
- OQ-2 (presence vs authenticity) tentatively resolving: belonging does not
  require multiplayer.

Governance:
- Added the **discovery-vs-explanation rule** to GOVERNANCE §6: discoveries
  change the philosophy and are recorded first-class; explanations only clarify
  and never stand alone.

INDEX updated (dashboard → 2 PROPOSED, register, decision record, open/research
questions). Phase 2 continues on RQ-1 before the axioms are locked.

## 2026-07-19 — IP-001 confirmed, restructured; next phase set — PROPOSED

Roy confirmed the IP-001 distillation and directed three changes plus a
forward-looking phase.

Changed in IP-001:
- Reorganized into five sections: Accepted Philosophical Truths, Open
  Philosophical Questions, Rejected Philosophical Directions, Key Constitutional
  Principles (8), and Decision Rationale (why each accepted truth survived
  challenge).
- **AT-4 ("a Club is grown, not built") demoted to a Candidate Truth** — held
  PROPOSED and not final, per Roy. Removed from accepted truths; OQ-3 remains.
- **AT-2 (Core Loop) amended:** the Club's economy is part of the loop, driven by
  the fantasy score (real results → fantasy → economy).
- Still fully PROPOSED; nothing canonical.

Changed in GOVERNANCE:
- Added §6 **Package Streams & Research Phases**: future packages declare a
  stream — Philosophy, Human Attachment Research, Constitutional Decisions, or
  Design Translation. Phase shift recorded: after IP-001 the goal moves from
  refining wording to discovering deeper human truths about attachment that may
  change the Constitution itself. Added the meta-principle "preserve what proved
  meaningful, not everything that happened."

## 2026-07-19 — IP-001 (Worldview Foundation) received — PROPOSED

First ERA Import Package. Roy directed capture of the *converged philosophy*
only — accepted truths, open questions, rejected ideas — as the beginning of
institutional memory, deliberately excluding brainstorming. The CKO curated the
"Emotional Foundation" philosophy and the subsequent design review into
`intake/IP-001-worldview-foundation.md`.

Contents: 16 accepted truths (proposed → canonical), 7 open constitutional
questions (OQ-2…OQ-8), 4 rejected/superseded ideas, a placement map, and 7
drafted decision records (DR-001…DR-007).

Status: held **PROPOSED**. Per SOP, nothing is canonical until Roy ratifies.
On approval the accepted truths split into `constitution/`, open questions into
`open/`, rejected ideas into `rejected/`, and the decision records are
finalized. INDEX updated (dashboard, register, decision record, open-questions
register).

## 2026-07-19 — ERA Import Package intake ratified as SOP

Roy restated and ratified the ERA Import Package intake as the standard
operating procedure. Two refinements folded into GOVERNANCE §3 to match the
stated steps exactly: duplicate detection is now explicit alongside
contradiction detection, and decision records may be "drafted or updated" (not
only drafted). No change to authority, classification law, or the verbatim
charter.

## 2026-07-19 — Intake protocol changed to ERA Import Packages

Roy directed that design material no longer be imported as raw conversations.
The unit of intake is now a structured **ERA Import Package** prepared by
ChatGPT (curated design material). On each package the CKO verifies consistency,
identifies conflicts, recommends classifications, suggests placement, drafts
decision records, and waits for approval before updating canonical documents.
Raw conversations are bounced with a recommendation to package them first,
unless Roy explicitly asks to proceed with the raw material.

Changed:
- `GOVERNANCE.md` §3 — rewritten as the Import Package intake protocol. The
  verbatim charter in §1 is untouched; §3 refines its operational steps.

## 2026-07-19 — GitHub mirror live

The canonical GitHub mirror is now live at `Roy481977/ERA`. The three
foundational documents were pushed to the repository root as the initial
commit.

Details:
- **Authentication:** a fine-grained Personal Access Token (Contents:
  read/write) scoped to `Roy481977/ERA`.
- **Transport note (for future sessions):** `api.github.com` is blocked by the
  container's egress proxy ("builtin injection failed", HTTP 502). The git
  transport over HTTPS works normally, so sync is done with plain `git`
  (clone/commit/push), **not** the GitHub REST API. Create commits with git,
  not the API.
- **Path mapping:** the ERA Claude project stores these files under an `era/`
  path; they map to the **root** of the GitHub repo.
- Resolves OQ-1 (GitHub authentication).

## 2026-07-19 — Repository initialized

The ERA knowledge repository was initialized as the live working copy inside
the ERA Claude project. No design content yet; this is scaffolding only.

Added:
- `GOVERNANCE.md` — the CKO charter preserved verbatim, plus classification law
  (7 statuses), intake protocol, design-governance trace, and document-quality
  rules.
- `INDEX.md` — master map, directory plan, status dashboard (all zero),
  document register, decision record, and open-questions register.
- `CHANGELOG.md` — this file.

Governance decisions recorded:
- **Canonical home = GitHub; ERA project = live working copy** (chosen by Roy).
- **Classification set = 7 statuses**, default-to-Open when uncertain (per
  charter).

Known status / pending at the time of this entry (later resolved — see the
entry above):
- GitHub mirror was not yet live; auth path was pending. Resolved 2026-07-19 via
  fine-grained PAT.
- No `constitution/` or `canon/` content exists yet — awaiting first material.
