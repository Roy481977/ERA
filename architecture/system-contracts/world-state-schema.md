# WI-01 · Authoritative World-State Schema

**Status: PROPOSED.** Conceptual schema (engine-decoupled — not a specific engine
or database). Types are logical. Every field names exactly **one owner** engine;
all other engines may read it but must request changes through the owner.

Conventions: `id` fields are **stable across the entire lifetime of the world**
(years). Records are split into **mutable current state** and **append-only
history** where noted (persistence rule, area for World-Persistence Engine).

---

## 0. WorldClock  *(owner: Time Engine)*

| Field | Type | Notes |
|---|---|---|
| `now` | timestamp | canonical simulation time; single source |
| `day_type` | enum | ordinary / matchday / holiday / disrupted |
| `season` | enum | + progress within season |
| `football_calendar_ref` | ref | current real-football context |
| `tick` / `step` | int | monotonic simulation step (deterministic ordering) |

There is exactly **one** WorldClock. No engine keeps a private clock.

## 1. Entity (base)  *(owner: World-Persistence Engine)*

| Field | Type | Owner | Mutability |
|---|---|---|---|
| `id` | EntityId | Persistence | immutable |
| `kind` | enum (person, place, club, object…) | Persistence | immutable |
| `created_at` | timestamp | Persistence | immutable |
| `current_state_ref` | ref | Persistence | mutable |
| `history_ref` | ref (append-only log) | Persistence | append-only |

Persistence owns **identity and the historical ledger**; domain engines own the
*meaning* of the current state (below).

## 2. Place  *(identity: Persistence · semantics: Semantic Place Graph / Town)*

| Field | Owner | Notes |
|---|---|---|
| `id`, `name`, `zone` | Persistence | stable identity |
| `semantic_tags` / `affordances` | Place Graph | e.g. `WORK_BAKERY_COUNTER`, `BUY_BREAD`, `WAIT_FOR_PERSON`, `MEMORIAL_PAUSE`, `MATCH_GATE_ENTRY`, `SHELTER_FROM_RAIN`, `DOG_REST_SHADE` |
| `slots` (typed, count) | Place Graph | reservable interaction points |
| `capacity` | Place Graph | max concurrent occupants |
| `opening_rules` | Place Graph | by time / day_type / season |
| `access_constraints` | Place Graph | who/when may use |
| `coordinates` / navmesh refs | **execution layer only** | never used by intention logic |

Intentions resolve against **affordances**, never raw coordinates.

## 3. Person / Resident  *(split ownership)*

| Field | Owner | Mutability |
|---|---|---|
| `id`, `role`, `home_place`, `workplace` | Persistence (authored identity) | stable |
| `traits`, `habits` | Persistence (authored) | rarely |
| `tier` (0–3 fidelity) | Town Engine | mutable |
| `needs` (hunger, rest, social…) | Town Engine | mutable |
| `mood` | Town Engine | mutable |
| `current_place` | Town Engine | mutable |
| `current_intention_ref` | Town Engine | mutable |
| `arc_state` (milestone progress) | Event Engine (authored arcs) | mutable, attributable |
| `relationships_ref` | Relationship Engine | — |
| `memories_ref` | Memory Engine | — |

A resident's *identity* is authored and stable; their *live behavioral state* is
Town-owned; their *bonds* and *memories* live in their respective engines.

## 4. Relationship  *(owner: Relationship Engine)*

| Field | Notes |
|---|---|
| `id`, `participants[]` | stable edge identity |
| `type` | bond / care / rivalry / romance / cross-species / … |
| `strength` | evolves over time |
| `obligations[]` | duties the edge creates (e.g. "leave the first roll for the Old Dog") |
| `permissions[]` | social permissions (who may interrupt whom) |
| `history_ref` | append-only interaction history |

## 5. Intention  *(owner: Town Engine)*

| Field | Notes |
|---|---|
| `id`, `actor` (resident) | — |
| `purpose` | semantic goal (open the bakery, meet X, look for the dog, attend memorial…) |
| `target` | affordance / place / person |
| `earliest_time`, `latest_time` | scheduling window |
| `priority`, `duration` | arbitration inputs |
| `interruptibility` | may this be interrupted, and by what |
| `provenance` | obligation / relationship / event / habit / **authored** |
| `status` | candidate / scheduled / active / done / failed / cancelled |
| `reason_code_ref` | why it won or failed (see §10) |

## 6. Reservation  *(owner: Town Engine, against Place slots)*

| Field | Notes |
|---|---|
| `place`, `slot`, `actor`, `time_window` | prevents two residents occupying one slot |

## 7. Event  *(owner: Event Engine)*

| Field | Notes |
|---|---|
| `id`, `type` | authored / systemic |
| `scope` | resident / place / district-wide |
| `conditions`, `consequences` | trigger + effects |
| `lifecycle` | pending / active / resolved |
| `timestamps` | on the WorldClock |

## 8. Memory  *(owner: Memory Engine)*

| Field | Notes |
|---|---|
| `id`, `subject(s)` | whose memory |
| `event_ref` | the true event it records (never a fabricated one) |
| `salience`, `decay` | retrieval weighting over time |
| `perspective` | how the subject holds it |
| `retrieval_tags` | context keys |

Memory records **traces of true events**; it never invents facts. *(Per CD-003,
Memory is the mechanism beneath Recognition.)*

## 9. Recognition  *(owner: Recognition Engine)*

| Field | Notes |
|---|---|
| `id`, `player_mark_ref` | the specific player-caused fact being reflected |
| `channel` | person / place / ritual / consequence |
| `constraints` | must be **contingent, specific, unsolicited, revocable** (IP-002) |
| `trigger_conditions` | when the world may truthfully reflect it back |
| `expression_ref` | how it surfaces (never a reward panel / quest marker) |

## 10. ReasonCode  *(cross-cutting; written by Town Engine & AI Director)*

| Field | Notes |
|---|---|
| `id`, `subject_intention` | — |
| `outcome` | won / lost / deferred / interrupted / failed |
| `factors[]` | priority, urgency, capacity, travel time, conflict, permission |
| `explanation` | human-readable "why" for the inspector |

---

## Ownership summary (the single-owner rule)

| Domain | Owner |
|---|---|
| Time, calendar, season, stepping | **Time Engine** |
| Identity, current-state pointers, history ledger, saves | **World-Persistence Engine** |
| Place semantics, slots, capacity, opening rules | **Semantic Place Graph / Town** |
| Resident live state (needs, mood, place, intention, tier) | **Town Engine** |
| Bonds, strength, obligations, permissions | **Relationship Engine** |
| Intentions, reservations, reason codes | **Town Engine** |
| Events and their lifecycle | **Event Engine** |
| Memory traces | **Memory Engine** |
| Recognition eligibility & expression | **Recognition Engine** |

Persistence rule (which fields are immutable history vs. mutable current) is an
**open question** flagged in IP-003 and resolved per-field during Phase 0.
