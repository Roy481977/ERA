# ERA — Creative Decisions

**Repository module (architecture).** This module preserves the **reasoning
behind major creative decisions — why a discovery ultimately won over the
alternatives.** Not the conversations, and not the discoveries themselves.

---

## Why this module exists

The repository already preserves governance, **Import Packages** (discoveries),
**canon**, and the **living world**. What it did *not* explicitly preserve is
*why* a discovery survived over the roads not taken. A discovery can be recorded
(an Import Package) and ratified (canon) while the reasoning that made it win
evaporates — and once that's gone, rejected ideas get re-litigated and no one
remembers why the alternative lost. Creative Decisions close that gap.

## Import Package vs. Creative Decision

- An **Import Package** describes the **discovery** — *what* was found (worldview,
  axioms, compression events). **The WHAT.**
- A **Creative Decision** explains why that discovery **survived** — the
  alternatives it beat and the reasoning that made it win. **The WHY.**

They are different artifacts, cross-linked, never merged.

## When a Creative Decision is produced

Whenever ChatGPT and Roy reach a significant conclusion that changes ERA's
**philosophy, world, or design**, ChatGPT produces a Creative Decision. (The CKO
may also *backfill* Creative Decisions for conclusions already reached — clearly
marked as backfilled and held PROPOSED for Roy's confirmation.)

## The CKO's duties for every Creative Decision

For each incoming Creative Decision the CKO will:

1. **Classify** it (status + domain).
2. **Cross-reference** it (to the axioms, canon, and rejected/superseded items it
   concerns).
3. **Link** it to the relevant Import Package(s).
4. **Update the INDEX** (register, dashboard, decision record).
5. **Preserve it permanently** — a Creative Decision is never deleted. If a
   decision is later reversed, a new CD **supersedes** it and *both are kept.*

## Creative Decision format (template)

Each Creative Decision is its own file, `CD-###-slug.md`:

- **ID / Title / Date**
- **Status** — PROPOSED until Roy ratifies the decision; then RATIFIED. A reversed
  decision becomes SUPERSEDED (pointing to the CD that replaced it).
- **The decision** — one line: what was decided.
- **Links** — Import Package(s), axioms/canon, and REJECTED/SUPERSEDED items.
- **Alternatives considered** — what else was on the table.
- **Why this won** — the core: the reasoning that made it survive over the
  alternatives.
- **What it rejects or supersedes** — the roads not taken, with the reason.
- **Consequences** — what the decision commits ERA to.
- **Open threads** — anything still unresolved about it.
- **Authority** — who decided / awaiting ratification.

## Register of Creative Decisions

| CD | Title | Status | Links |
|---|---|---|---|
| [CD-001](CD-001-attachment-not-addiction.md) | Attachment, not addiction (the North Star) | PROPOSED (CKO seed) | IP-001 AT-1/AT-3/DR-001; resolves the sources' addiction-vs-attachment contradiction |
| [CD-002](CD-002-grown-not-built.md) | Grown, not built (over "Club as Partner") | PROPOSED (CKO seed) | IP-002 AT-4, RJ-1; IP-001 AT-5; feeds CD-005 |
| [CD-003](CD-003-recognition-beneath-memory.md) | Recognition beneath Memory | PROPOSED (CKO seed) | IP-002 A2, CE-1, CR-1; IP-001 AT-9 |
| [CD-004](CD-004-meaning-split-from-recognition.md) | Meaning split from Recognition | PROPOSED (CKO seed) | IP-002 A3, A2, CE-3, CR-2 |
| [CD-005](CD-005-relational-axiom.md) | The Relational Axiom (over "Non-Control") | PROPOSED (CKO seed) | IP-002 AR, CE-6, CR-8, RQ-1; supersedes AT-6 |
| [CD-006](CD-006-simulate-intention-not-movement.md) | Simulate Intention, Not Movement (the Town Engine) | PROPOSED | IP-002 AR; living-world (README, interwoven-lives, places); tech companion `research/town-engine-technical-strategy.md` |
| [CD-007](CD-007-core-language-rust.md) | The authoritative core is written in Rust | PROPOSED | IP-003; CD-006; Town Engine strategy; DS-001 |
| [CD-008](CD-008-plate-world.md) | The Plate World — pre-rendered 2.5D fabric, live composited layer | **LOCKED (Roy)** | supersedes runtime-3D world fabric; design/asset-design-model.md; design/town-composition.md; research/visual-engine-and-design-strategy.md |
| [CD-024](CD-024-modern-english-village-baseline.md) | The modern English village is ERA's architectural baseline | PROPOSED (Roy, 2026-07-26; held open — era found, voice in review) | Sheets 01–05 (`design/boards/`); supersedes the Museum as architectural baseline |
| [CD-025](CD-025-evidence-of-life.md) | The town is continuously authored by the simulation | PROPOSED (Roy, 2026-07-26) | evidence-of-life design; CD-006/007/008/009; Oak scarves precedent |
| [CD-026](CD-026-space-is-the-unit.md) | The primary design unit is space, not architecture | PROPOSED (Roy, 2026-07-27) | Sheet 06 the walk; two cameras (34/19, 34/6.5) |
| [CD-027](CD-027-the-weave-composed-in-time.md) | The Weave is the canonical town composition, composed in space AND time | **RATIFIED (Roy, 2026-07-27)** | closes composition; T1–T8 archetypes only; District 01 built |
| [CD-028](CD-028-simulation-is-lead-designer.md) | The simulation is the lead designer | PROPOSED (Roy, 2026-07-27) | Phase 4; sandbox + story metrics (`tools/sandbox/`); District 01 frozen |
