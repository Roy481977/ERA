# WI-01 · Observability & Debugging

**Status: PROPOSED.** Per the roadmap, the **developer inspector is built before
life** (Phase 0). The governing invariant: **every autonomous action exposes a
reason chain, and no LLM/AI may directly mutate authoritative state.** These tools
make the invariant checkable and power the acceptance tests.

Shared substrate they all rely on: **deterministic seeds**, an **append-only event
log** (every event/command with `tick`, source, payload), and **reason codes** on
every autonomous decision.

## 1. Intention Inspector
Live view of every resident's **current intention, destination, provenance,
affordance, and reason code**, plus the next candidate intentions and why they
lost. Filter by resident, place, or provenance.
*Powers:* AT-1, AT-2, AT-11.

## 2. "Why is this person here?" Trace
Point at any resident → a readable chain: *need/obligation/event → intention →
arbitration factors → chosen affordance → route → arrival*, each step with its
reason code. Answerable in **under ten seconds**.
*Powers:* AT-1, AT-3, AT-11.

## 3. World-State Timeline
A scrubber over the WorldClock showing authoritative state at any tick, with a
**time-scrubber and fast-forward**. Lets a designer replay a day, pause, and
inspect the single source of truth for any fact.
*Powers:* AT-6, AT-9.

## 4. Relationship-Change Log
An append-only record of every `RelationshipChanged` / `ObligationTriggered`,
with the encounter or event that caused it and the resulting behavioral change.
*Powers:* AT-3, AT-4.

## 5. Event Causality Graph
A directed graph linking **event → affected intentions → outcomes → downstream
events/memories**. Makes interruption propagation and consequence chains visible.
*Powers:* AT-4, AT-8.

## 6. Deterministic Replay
Re-run any period from `(snapshot + event log + seed)` to reproduce it exactly;
diff two runs to prove determinism or locate a divergence. Includes an
**automated contradiction report** (impossible positions, double-bookings,
unexplained relocations, permanent-stuck / silent-disappearance) and a
**liveness monitor**.
*Powers:* AT-5, AT-7, AT-10, AT-12.

---

## Coverage matrix

| Tool | Acceptance tests it verifies |
|---|---|
| Intention Inspector | AT-1, AT-2, AT-11 |
| "Why is this person here?" | AT-1, AT-3, AT-11 |
| World-State Timeline | AT-6, AT-9 |
| Relationship-Change Log | AT-3, AT-4 |
| Event Causality Graph | AT-4, AT-8 |
| Deterministic Replay (+ contradiction report, liveness) | AT-5, AT-7, AT-10, AT-12 |

Every acceptance test maps to at least one tool; every tool exists to make the
architecture's invariants **inspectable, attributable, and reproducible** —
which is the whole point of contracts before content.
