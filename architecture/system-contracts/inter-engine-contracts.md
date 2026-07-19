# WI-01 · Inter-Engine Contracts

**Status: PROPOSED.** How engines communicate. Two channels only, so authority
never leaks:

- **Events** (broadcast, past tense): "this happened." Emitted by the owner after
  it commits a change. Others react; they cannot veto.
- **Commands** (directed, imperative): "please do X." A *request* to the owner of
  the affected fact. The owner validates and either commits (emitting an event)
  or rejects (with a reason code). **Commands are the only way to change state you
  don't own.**

Shared conventions:
- Every event and command carries `id`, `tick` (WorldClock), `actor/source`,
  `payload`, and — for anything autonomous — a `reason_code_ref`.
- Ordering is by `tick`; within a tick, by a deterministic priority so replays are
  identical.
- **No engine reads another engine's private memory; it reads published state and
  events only.**

---

## Contract template

Each engine publishes a contract of: **Inputs (reads) · Outputs (published state)
· Events emitted · Commands accepted · Failure behavior · Determinism.**

---

## Time Engine
- **Inputs:** football calendar; scheduled global transforms.
- **Outputs:** `WorldClock`.
- **Events emitted:** `TickAdvanced`, `DayTypeChanged`, `SeasonChanged`.
- **Commands accepted:** `RequestTimeScale(rate)` (dev/tooling only).
- **Failure:** never stalls; if a consumer is slow, it back-pressures, never skips
  ticks silently.
- **Determinism:** **fully deterministic.**

## World-Persistence Engine
- **Inputs:** committed state changes from all owners.
- **Outputs:** current-state store; append-only history; save files.
- **Events emitted:** `StateCommitted(entity, delta)`, `SnapshotTaken`.
- **Commands accepted:** `Commit(delta)`, `Snapshot()`, `Restore(seed/snapshot)`.
- **Failure:** rejects a commit that violates single-owner or schema; never
  partially writes (transactional).
- **Determinism:** deterministic; replay from `(snapshot + event log + seed)`
  reproduces state exactly.

## Semantic Place Graph
- **Inputs:** Time, Weather.
- **Outputs:** affordance availability, capacity, open/closed.
- **Events emitted:** `PlaceOpened/Closed`, `PlaceFull`, `SlotFreed`.
- **Commands accepted:** `ReserveSlot(place, slot, actor, window)` → `Reserved` /
  `Rejected(reason)`.
- **Failure:** reservation on a full/closed/unreachable place returns
  `Rejected(reason_code)`; never double-books a slot.
- **Determinism:** deterministic given request order.

## Town Engine
- **Inputs:** Time, Place Graph, Relationships, Events, Weather.
- **Outputs:** resident live state; intentions; reservations; reason codes.
- **Events emitted:** `IntentionFormed`, `IntentionScheduled`, `Arrived`,
  `Interrupted`, `IntentionFailed`, `EncounterOccurred`.
- **Commands accepted:** `ProposeIntention(actor, purpose, window, provenance)`
  (from Relationship/Event); `Interrupt(actor, cause)`.
- **Failure:** a blocked/failed intention triggers **bend, not break** — arbitrate
  a fallback (wait, re-route, defer, substitute affordance) and record the reason;
  never teleport, never silently drop the resident.
- **Determinism:** **deterministic given seed + input order** (arbitration is a
  pure function of state); no hidden randomness.

## Relationship Engine
- **Inputs:** `EncounterOccurred` events; `Event` outcomes.
- **Outputs:** bond strengths, obligations, permissions.
- **Events emitted:** `RelationshipChanged`, `ObligationTriggered`.
- **Commands accepted:** `RecordEncounterOutcome(...)`.
- **Failure:** conflicting obligations resolve by priority; unresolved ones are
  logged, never silently dropped.
- **Determinism:** deterministic given event order.

## Event Engine
- **Inputs:** WorldClock, world state, conditions.
- **Outputs:** active events; consequence commands.
- **Events emitted:** `EventTriggered`, `EventResolved`.
- **Commands accepted:** `ScheduleEvent`, `CancelEvent` (authored/dev).
- **Failure:** an event whose consequences a target rejects is logged as a
  contradiction (surfaced by the contradiction report), never force-applied.
- **Determinism:** authored events deterministic; systemic events **seeded-
  probabilistic** (reproducible from seed).

## Weather & Season Engine
- **Inputs:** Time; optional real-world weather.
- **Outputs:** conditions; seasonal biases.
- **Events emitted:** `WeatherChanged`, `SeasonPressureChanged`.
- **Commands accepted:** `ForceWeather(...)` (dev/tooling).
- **Failure:** falls back to a default region if a data source is unavailable.
- **Determinism:** **seeded-probabilistic** (reproducible); never affects
  competitive outcomes.

## Crowd Engine
- **Inputs:** Time, Place Graph, day_type, Weather.
- **Outputs:** aggregate density/flow.
- **Events emitted:** `CrowdStateChanged`.
- **Commands accepted:** none authoritative.
- **Failure:** degrades to lower fidelity under load; never teleports individuals.
- **Determinism:** **seeded-probabilistic** at the aggregate level.

## AI Director
- **Inputs:** world state, events, pacing signals.
- **Outputs:** **preferences/rankings only** — never state.
- **Events emitted:** `SelectionSuggested(options, chosen, reason)`.
- **Commands accepted:** none that mutate truth.
- **Failure:** if it proposes an invalid option, the owner rejects it; the world
  continues on the default valid option.
- **Determinism:** seeded; **may never directly mutate authoritative state.**

*(Memory, Recognition, Club Culture, Narrative, Matchday, Economy, Audio publish
contracts in the same shape; they enter in roadmap Phases 2–4 and are out of the
first slice's mutation path — see `vertical-slice.md` for what the slice actually
runs.)*
