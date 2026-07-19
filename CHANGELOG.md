# ERA — Changelog

Every change to the repository, dated, newest first. Nothing changes silently.
Historical reasoning is never deleted — superseded and rejected material is
retained in place, this log records the reasoning.

Format: `YYYY-MM-DD — summary`, followed by details.

---

## 2026-07-19 — RATIFIED: architecture/ permanent module + WI-01 created

**Ratification (first in the repository).** Roy ratified `architecture/` as a
**permanent, first-class repository module**. Only the module's *permanence* is
canonical; **IP-003 and every architecture document remain PROPOSED.** Resolves
the IP-003 placement open question. Recorded in `architecture/README.md`
(Placement — RATIFIED) and INDEX.

**New work item — WI-01: System Contracts & Vertical Slice Specification.** Created
`architecture/system-contracts/` to make the conceptual architecture implementable
without engineers inventing the core rules:
- `world-state-schema.md` — authoritative schema (WorldClock, Entity, Place,
  Resident, Relationship, Intention, Reservation, Event, Memory, Recognition,
  ReasonCode) with **per-field single ownership**.
- `engine-boundaries.md` — for all 15 engines: owns / may read / may propose / may
  mutate / must never control.
- `inter-engine-contracts.md` — the event + command model; per-engine inputs,
  outputs, events, commands, failure behavior, determinism (deterministic vs
  seeded-probabilistic).
- `vertical-slice.md` — the Town Engine slice: one district (~12 semantic places),
  25–40 persistent residents, ordinary weekday + matchday + a disruptive storm,
  persistence across two weeks of absence, all four fidelity tiers.
- `acceptance-tests.md` — 13 checkable tests (semantic correctness, bend-not-break,
  relationships alter behavior, interruption propagation, no teleport/reset, one
  visible world state, AI cannot rewrite truth, determinism, offscreen continuity,
  believability).
- `observability-and-debugging.md` — intention inspector, "why is this person
  here?" trace, world-state timeline, relationship-change log, event causality
  graph, deterministic replay + contradiction/liveness reports.

Reconciled with CD-006, the Town Engine strategy, the system map and the execution
roadmap; terminology kept identical. **Scope-guarded: no new engines, no
broadening.** All WI-01 material PROPOSED — not promoted to canonical.

## 2026-07-19 — Intake: IP-003 + architecture module (Systems Architecture Foundation) — PROPOSED

Roy provided the "ERA Systems Architecture Foundation" package (ChatGPT-authored),
declared as net-new only. Intake per protocol:

- **Consistency check.** Every file was net-new (nothing live replaced, as
  stated). All 15 subsystem briefs carry Status: PROPOSED and a "Constitutional
  connection" citing the Human Test and the Relational Axiom. Recognition Engine
  maps to IP-002 A2; the roadmap's 6-week Town Engine slice matches
  `research/town-engine-technical-strategy.md`. **No contradictions with
  canon-track.**
- **Integrated (wrapper folder stripped):**
  - `intake/IP-003-systems-architecture-foundation.md` — the Import Package
    (Design Translation): ERA as a **federation of bounded living systems sharing
    one authoritative world state and one clock; AI proposes/orchestrates inside
    authored bounds and never silently owns or rewrites world truth.**
  - `architecture/` (top-level module): `README.md`, `system-map.md`,
    `execution-roadmap.md`, and `systems/` (15 engine briefs: town, time,
    world-persistence, relationship, memory, recognition, event, matchday,
    club-culture, economy, narrative, ai-director, crowd, weather-season,
    audio-ecology).
- **Reconciliation.** IP-003 numbering correct (after IP-002). Placed
  `architecture/` top-level (per the module's own tree), noting its permanence is
  Roy's to ratify (IP-003 open question). Added a CKO **reconciliation map** in
  `architecture/README.md` (each engine → its IP/CD/living-world roots) and
  cross-linked the Town Engine brief ↔ CD-006 ↔ the technical strategy ↔
  `living-world/interwoven-lives.md`. The intake instruction file
  (`README-FOR-CLAUDE.md`) was not committed (transient guidance, not a repo
  artifact).
- **Status.** All PROPOSED. **Not promoted to canonical.**

## 2026-07-19 — Intake: CD-006 + Town Engine (repo-update zip) — PROPOSED

Roy provided an updated-repository zip (ChatGPT-authored) adding CD-006 and a
Town Engine technical strategy. Intake per the CKO protocol:

- **Consistency check.** Compared the zip against the live repo file-by-file:
  `intake/` (IP-001/002), all of `living-world/`, and all of `sources/` were
  **identical**. The only genuinely new files were CD-006 and the Town Engine doc.
- **Not taken (parallel/older state).** The zip's `GOVERNANCE.md` was an *older*
  copy missing live **§7 (Creative Decisions)**; its `INDEX.md`, `CHANGELOG.md`
  and `creative-decisions/README.md` reflected a state that did not include the
  live **CD-001…CD-005**. These were kept from the live repo, not overwritten.
- **Integrated.** Added `creative-decisions/CD-006-simulate-intention-not-movement.md`
  ("ERA simulates intention; movement is its visible consequence" — the Town
  Engine) and `research/town-engine-technical-strategy.md` (build-vs-buy, tiers,
  semantic-place graph, six-week vertical slice).
- **Reconciliation.** Numbering **CD-006** is correct (next after CD-005).
  Cross-refs verified (CD-006 ↔ town-engine ↔ IP-002 AR ↔ living-world). Added an
  `ID` row to CD-006 for format parity; adopted the broadened `research/`
  definition ("external inputs and technical evaluations"); linked the chain from
  `living-world/interwoven-lives.md` → CD-006 → the technical strategy. Register,
  INDEX and dashboard (RESEARCH → 1) updated.
- **Status.** All PROPOSED. **Not promoted to canonical.**

## 2026-07-19 — Foundational Creative Decisions backfilled (CD-001…CD-005) — PROPOSED

At Roy's request, backfilled the five foundational Creative Decisions, each with
its alternatives, the reasoning that made it win, what it rejects/supersedes,
consequences, and cross-references to the Import Packages:

- **CD-001 — Attachment, not addiction** (North Star) → IP-001 AT-1/AT-3/DR-001.
- **CD-002 — Grown, not built** (over "Club as Partner") → IP-002 AT-4/RJ-1;
  IP-001 AT-5.
- **CD-003 — Recognition beneath Memory** → IP-002 A2/CE-1/CR-1; IP-001 AT-9.
- **CD-004 — Meaning split from Recognition** → IP-002 A3/A2/CE-3/CR-2.
- **CD-005 — The Relational Axiom** (over "Non-Control") → IP-002 AR/CE-6/CR-8/
  RQ-1; supersedes AT-6.

All PROPOSED (CKO seeds), awaiting Roy's ratification. Register updated in
`creative-decisions/README.md`; INDEX updated. From here, every significant
philosophical or design breakthrough receives a Creative Decision as part of the
normal workflow.

## 2026-07-19 — New module: Creative Decisions (permanent architecture)

Roy established a permanent workflow/architecture change: a new top-level module
`creative-decisions/` to preserve the **reasoning behind major creative decisions
— why a discovery won over the alternatives** — a gap the repository did not
explicitly cover (it held discoveries via Import Packages and canon, but not the
*why it survived*).

- **Import Package vs. Creative Decision:** IP describes the discovery (the WHAT);
  CD explains why it survived (the WHY). Distinct artifacts, cross-linked, never
  merged.
- **Rule:** when ChatGPT + Roy reach a significant conclusion that changes ERA's
  philosophy, world or design, ChatGPT produces a Creative Decision; the CKO
  classifies, cross-references, links to the Import Package(s), updates the INDEX,
  and preserves it permanently (reversed decisions are superseded, never deleted).
- Recorded in **GOVERNANCE §7**. Added `creative-decisions/README.md` (purpose,
  CD template, workflow, register) and seeded **CD-001 — Attachment, not
  addiction** as a CKO-backfilled example (PROPOSED; also resolves the sources'
  addiction-vs-attachment contradiction in attachment's favour).

## 2026-07-19 — Living World: interwoven lives ("the same rails") — PROPOSED

Per Roy: all the living must interact, in a town, on the same rails — bonding and
aging across years; tens of lives on different days/occasions; scripted for
years. Added `living-world/interwoven-lives.md`, the connective system beneath
residents + places:

- **One shared clock** — all lives on a single persistent timeline, so
  interactions are consistent, co-witnessed and rememberable (a world with a
  past, not a loop).
- **Three levels of life** — named residents · minor residents (the "tens of
  lives") · micro-life (squirrels, cats, foxes) — all on the same rails.
- **The web** — relationships as edges (bonds, chance "sometimes" encounters,
  care, rivalry, romance, cross-species) with evolving strength and encounter rules.
- **Scripted for years** — authored milestone arcs (aging, loss, growing up) +
  emergent daily texture; AI orchestrates within authored bounds, Human Test
  governs. The agency–otherness balance applied to authorship of the world.
- **Worked example** — the boy (provisional "Tomas") and the Old Dog: a bond, the
  "sometimes" search, the squirrels, multi-year aging, and a loss that strikes all
  four textures at once and is never undone.
- Player sees only fragments over years; never the cause, never a quest.

Cross-linked from residents.md and README. PROPOSED.

## 2026-07-19 — Living World: places defined + the two moons — PROPOSED

Defined the district's places in `living-world/places.md` (Club/Stadium, Main
Street, Plaza & Fountain, the Riverside — Bridge/River/Old Oak, Museum Quarter,
Academy, Railway), each on a shared place template, filling the Book of ERA's
open questions. Proposed a map unification (emotional zones = canonical spine,
concentric rings = a supporting radial reading).

Introduced the never-explained **mystical root** per Roy in
`living-world/the-quiet-mysteries.md`: the district was designed **under two
moons** — a football place *just beside the real*. The layer is **"seen, never
said"**: no resident remarks on it, no lore/menu/quest/text ever names it, it
grants no advantage, and one quiet thread runs through each place (the fountain's
two reflections, the river's double-tide and the old oak, the museum's oldest
photograph, the academy's double shadow, the railway line into a distance no map
shows). Tied to Wonder (IP-001) and the deepest Independence (IP-002 AR). All
PROPOSED.

## 2026-07-19 — Residents cast expanded (13 biographies) — PROPOSED

Wrote full template biographies for the rest of the canonical cast in
`living-world/residents.md`: Daniel & Sofia (the couple), Elias (groundskeeper),
Mrs. Hana (baker), Luca (café), Karim (kiosk), Eva (florist), Milo (musician),
Nora (curator), Otto (publican), the Twins (children), Agnes (oldest supporter),
Victor (retired legend), Emma (journalist). Roles are CKO-proposed and grounded
in the district's places/rhythms; the cast is cross-linked so the world coheres,
and each quietly instantiates the attachment mechanisms (Living Memory,
Recognition via Victor/Emma/Nora, honest history via Nora/Agnes/Otto, and
"never performs for the player" = independence). PROPOSED — awaiting Roy's
approval/edits on roles and content.

## 2026-07-19 — Living World module started (district / living aspect) — PROPOSED

Per Roy: follow the proposal ChatGPT chat closely as the evolution of the idea,
document the living aspect well and within the main files, and continue the work
ChatGPT crashed mid-way through. Consolidated the living-world layer from all
three sources (proposal chat, Book of ERA v1.2, Design Bible Vols V–VII) into a
new `living-world/` module:

- `living-world/README.md` — The Living World (district): what it is,
  constitutional discoveries about place, district identity, emotional geography
  (both the zone view and the ring view, flagged for unification), composition &
  camera, landmarks, daily rhythms & match day, "the world continues without the
  player," visible-consequence table, weather/time, AI-as-world-building (tied to
  the Human Test), visual direction (four rules, density, Nintendo principle,
  "come and look not use me," the art north star), richness standard, open
  questions. Cross-referenced to IP-002 axioms (Independence/AR, Recognition,
  Meaning, Human Test).
- `living-world/residents.md` — residents system: canonical draft resident list,
  the resident design template, and a first fully-drafted example biography (the
  Old Dog) to fill the "expand each resident" gap.

Faithful to the sources; CKO-proposed additions marked `_[CKO-proposed]_`. All
PROPOSED — nothing canonical until Roy ratifies.

## 2026-07-19 — Source corpus received & secured (4 documents)

Roy handed over the full accumulated ERA material for documentation. All four
preserved verbatim under `sources/` (originals + `.txt` extracts), classified as
**SOURCE MATERIAL — unclassified, not canonical**:

- `design-bible-v0.1.pdf` — ERA Design Bible, Foundational Edition v0.1 (9
  volumes; its own 7-law Constitution; 5 core emotions; design chain).
- `book-of-era-edition-I-v1.2.docx` — The Book of ERA v1.2, the district /
  living-world layer.
- `era-the-beginning-for-gamma.docx` — "The Beginning," the manifesto.
- `proposal-chatgpt-chat.pdf` — the raw ChatGPT proposal chat (world visual
  design + early strategy).

Manifest at `sources/README.md` maps each document, the alignments with IP-001/
IP-002, and the contradictions to resolve (addiction vs attachment;
football-as-skin vs constitutive; two parallel "Constitutions"). Next step:
distil into PROPOSED Import Packages and produce a reconciliation — nothing
canonical until Roy ratifies.

## 2026-07-19 — IP-002: Relational compression (CE-6 / axiom AR) — PROPOSED

RQ-1 paid out. The "self past its boundary" root yielded a compression: **deep
attachment requires consequential agency inside an independent world** —
provisional constitutional expression *"the player shapes the Club but never
solely authors it"*; the relationship is **stewardship, not sovereignty.**

Recorded in IP-002:
- New candidate primary axiom **AR** (wording open); design is an inverted-U
  (agency without sovereignty), with a *per-domain* peak on the agency–otherness
  curve.
- **A1 (authorship half) + A4 (Independence) fuse into AR;** Independence and
  Vulnerability become *derived*. Meaning (A3) stands apart. Axiom set compresses
  4 → 3 (Relational · Recognition · Meaning).
- Added compression event **CE-6**; candidate ratification **CR-8**.
- **Four textures of loss** (place/form, regard, narrative, uncontrollable
  reality) preserved as a *derived research model* — not an axiom — with the
  compounding-loss prediction.
- **Rejected** the CKO's over-strong "you can only bond with what you do not fully
  control" (counterexamples: house, painting, manuscript — loved because they
  *resisted*).

All PROPOSED; final wording of AR deliberately open. INDEX updated.

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
