# ERA Bible

Version: 1.0 (Living Document)

---

## Purpose

This Bible is the canonical description of ERA.

It describes what ERA is, how it should evolve, and the principles that govern every design and engineering decision.

It is intentionally independent of implementation details.

The implementation may change.

The architecture may evolve.

The technology stack may be replaced.

The principles described here should remain stable.

When uncertainty exists, this document takes precedence over implementation convenience.

---

## Living Document

This Bible is expected to evolve throughout the lifetime of ERA.

Every significant design decision should be reflected here before becoming permanent implementation.

The repository—not conversation history—is the source of truth.

If discussions produce lasting design decisions, those decisions belong in this Bible.

---

## What is ERA?

ERA is a living world platform.

Its first world is a football town.

Football gives the town purpose, rhythm, identity and emotion, but it is not the entire world.

Residents have lives beyond football.

They work.

They rest.

They build relationships.

They develop routines.

They remember.

They celebrate.

They grieve.

They influence one another.

The objective is not to script stories.

The objective is to build a world capable of continuously producing authentic stories through simulation.

---

## Two Equal Goals

ERA has two inseparable objectives.

### 1. Build a world-class deterministic simulation engine.

The engine should be:

- deterministic
- explainable
- scalable
- replayable
- engine-independent
- modular
- observable

It should be capable of simulating believable societies over long periods of time.

---

### 2. Build living worlds.

The engine exists for a purpose.

Its purpose is to create places that feel alive.

Every advancement of the engine should ultimately improve the lived experience of the simulated world.

Likewise, every new world feature should strengthen—not compromise—the quality of the underlying engine.

Neither objective is subordinate to the other.

---

## The Philosophy

Traditional games create stories by scripting events.

ERA creates stories by simulating life.

The simulation should not ask:

"What story should happen?"

It should ask:

"What would naturally happen here?"

The resulting stories belong to the world.

Not to the designers.

---

## The Player Experience

The player should gradually stop thinking about systems.

Instead they should think about people.

Examples:

"I wonder where Victor is."

"I haven't seen Agnes recently."

"Everyone gathers beneath the Oak after victories."

"Karim seems different since the relegation."

When players naturally describe residents instead of mechanics, ERA is succeeding.

---

## Living Before Large

Scale is not the objective.

Believability is.

A town of twenty believable residents is more valuable than a city of twenty thousand shallow ones.

ERA will always prioritize depth before expansion.

Expansion should only occur when the existing simulation already feels alive.

---

## Explainability

Nothing in ERA should feel arbitrary.

Every meaningful action should eventually be explainable.

The question:

"Why did this happen?"

should always have an answer that comes from the simulated world itself.

Explainability is not only a debugging tool.

It is part of the design philosophy.

A believable world is an understandable world.

---

## Observation

Watching the simulation is a core design activity.

Every completed feature should produce observable changes in behavior.

Invisible systems are incomplete systems.

The simulation should increasingly become enjoyable to observe without player interaction.

---

## Canonical Rule

Whenever implementation and philosophy conflict:

The philosophy wins.

The implementation must adapt.

Never simplify the vision merely because implementation is difficult.

Instead, search for a simpler implementation that preserves the vision.

---
---

<!-- ============================================================= -->
<!-- The section below is REPOSITORY METADATA maintained by the CKO. -->
<!-- It is NOT part of the canonical Bible text above, which is       -->
<!-- authored by Roy + ChatGPT and preserved verbatim.               -->
<!-- ============================================================= -->

## — Repository metadata (not part of the canonical Bible) —

**Status: CANONICAL.** The ERA Bible is the apex governing document of the
repository. Authored by **Roy + ChatGPT**. Ratified and made canonical by Roy on
2026-07-19.

**Amendment rule (per Roy).** The Bible must **not** be modified directly. If a
change is warranted, it is proposed as an *amendment* under "Proposed amendments"
below and left for Roy + ChatGPT to author into the canonical text. The CKO
preserves and cross-references; it does not rewrite the Bible.

**Precedence.** When anything conflicts, order of authority is:

1. **BIBLE.md** — canonical philosophy (what ERA is; philosophy wins over implementation).
2. **GOVERNANCE.md** — repository / CKO charter (how knowledge is preserved and classified).
3. **development/DEV-000-development-constitution.md** — how the simulation is built (the Ladder of Life, engineering principles).
4. Architecture (`architecture/`), specs (`development/DS-###`), then code.

The three governing documents are consistent by design: the Bible states the
*why*, DEV-000 the *how*, GOVERNANCE the *how it is kept*.

**Consistency check (2026-07-19).** Current implementation (Sprint 1 + Sprint 2
Steps 1–3) is consistent with the Bible: the core is deterministic, replayable, and
engine-independent (CD-007); behaviour is explainable (every move logged with its
reason from world state); the simulation is observable and enjoyable to watch
(`cargo run`, `chronicle`); it is built living-before-large (10 residents, deep);
and stories emerge from simulation rather than scripting (companionship, reunions,
the Oak's history). No conflicts requiring adaptation were found.

### Proposed amendments

*(none)*
