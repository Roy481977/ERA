# ERA — Changelog

Every change to the repository, dated, newest first. Nothing changes silently.
Historical reasoning is never deleted — superseded and rejected material is
retained in place, this log records the reasoning.

Format: `YYYY-MM-DD — summary`, followed by details.

---

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
