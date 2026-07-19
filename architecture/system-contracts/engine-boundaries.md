# WI-01 · Engine Boundaries

**Status: PROPOSED.** For every engine: what it **owns** (sole authority), what it
**may read**, what it **may propose** (request of another engine), what it **may
mutate** (only its own owned state), and what it **must never control**. This is
the enforcement of the single-owner rule.

Universal rule for all engines: *may mutate* is restricted to **its own owned
state**; changes to anything else happen only by **proposing** a command to the
owner. **No engine — and no AI layer — may mutate authoritative truth it does not
own.**

---

## Foundation

### Time Engine
- **Owns:** WorldClock (`now`, day_type, season, tick), simulation stepping.
- **Reads:** football calendar; scheduled global transforms (matchday).
- **Proposes:** day_type transitions to Event Engine.
- **Mutates:** the clock only.
- **Never controls:** any domain fact; it advances time, it does not decide events.

### World-Persistence Engine
- **Owns:** entity identity, current-state pointers, append-only history, saves,
  migrations, recovery.
- **Reads:** all engines' committed state changes (to persist them).
- **Proposes:** nothing (it records; it does not decide).
- **Mutates:** the ledger and current-state store.
- **Never controls:** the *meaning* of state (domains own that); it persists, it
  does not interpret.

### Semantic Place Graph *(shared: architecture + Town)*
- **Owns:** affordances, slots, capacity, opening rules, access constraints.
- **Reads:** Time (opening by day_type/season), Weather.
- **Proposes:** availability answers to Town.
- **Mutates:** place semantic state (open/closed/full).
- **Never controls:** who goes where (that's Town intention), navmesh geometry
  (execution layer).

## Life

### Town Engine
- **Owns:** resident live state, intentions, reservations, reason codes.
- **Reads:** Time, Place Graph, Relationships, Events, Weather.
- **Proposes:** path requests to navigation (execution); reservation requests;
  encounter creation.
- **Mutates:** intentions, reservations, resident current place/mood/needs, tier.
- **Never controls:** relationships, memories, culture, economy, narrative truth,
  event authority.

### Relationship Engine
- **Owns:** bonds, strength, obligations, permissions, relationship history.
- **Reads:** Encounters (from Town), Events.
- **Proposes:** relationship-driven intentions/interruptions to Town.
- **Mutates:** relationship state only.
- **Never controls:** where residents physically go (Town executes).

### Crowd Engine
- **Owns:** anonymous / semi-persistent population behavior at scale.
- **Reads:** Time, Place Graph, Matchday/day_type, Weather.
- **Proposes:** density/flow expression.
- **Mutates:** crowd aggregate state only.
- **Never controls:** named-resident authoritative state.

### Weather & Season Engine
- **Owns:** environmental conditions and seasonal pressure.
- **Reads:** Time; (opt-in) real-world weather.
- **Proposes:** condition changes that bias routines/place use.
- **Mutates:** weather/season state only.
- **Never controls:** competitive/fantasy outcomes; it enriches, never determines.

## Meaning

### Memory Engine
- **Owns:** memory traces, salience, decay, retrieval.
- **Reads:** Events, Encounters.
- **Proposes:** relevant memories in context (to Recognition, Narrative, Town).
- **Mutates:** memory state only.
- **Never controls:** what *happened* (Events own truth); it records, it never invents.

### Recognition Engine
- **Owns:** recognition eligibility and expression timing.
- **Reads:** Memory, Culture, Relationships, Narrative, the player's marks.
- **Proposes:** a truthful recognition expression (via people/places/rituals).
- **Mutates:** recognition state only.
- **Never controls:** rewards/progression; it must be contingent, specific,
  unsolicited, revocable — never a reward panel.

### Club Culture Engine
- **Owns:** emergent traditions, norms, symbols, grudges, identity.
- **Reads:** Events, Memory, results, long-term history.
- **Proposes:** cultural expressions and biases.
- **Mutates:** culture state only.
- **Never controls:** the player's *direction* (the player owns direction; the
  Club owns culture — CD-002 / AT-5). Culture emerges; it is never authored on demand.

### Narrative Engine
- **Owns:** selection of legible arcs from **true** world events.
- **Reads:** Events, Memory, Recognition, Culture.
- **Proposes:** framings/emphases.
- **Mutates:** narrative-selection state only.
- **Never controls:** the facts — it shapes legible arcs, it **never invents false
  facts** (the Human Test).

## Football & Economy

### Matchday Engine
- **Owns:** transformation of fixtures into district anticipation, ritual,
  attendance, emotion, aftermath.
- **Reads:** football calendar (Time), results, Crowd, Weather.
- **Proposes:** matchday day-type transforms and flows.
- **Mutates:** matchday state only.
- **Never controls:** the objective football result (reality is shared/immutable).

### Economy Engine
- **Owns:** resources, constraints, trade-offs, long-term consequence.
- **Reads:** football + fantasy performance, institution state.
- **Proposes:** economic consequences.
- **Mutates:** economy state only.
- **Never controls:** the fantasy score itself (objective; the institution never
  alters the score — Design Bible Law 2).

## Orchestration

### Event Engine
- **Owns:** authored + systemic events, conditions, consequences, lifecycles.
- **Reads:** WorldClock, world state.
- **Proposes:** consequence commands to affected engines.
- **Mutates:** event state; publishes domain events.
- **Never controls:** the internal state other engines own (it proposes; they commit).

### AI Director
- **Owns:** *selection among already-valid possibilities* to improve pacing,
  variety, emotional coherence.
- **Reads:** world state, events, pacing signals.
- **Proposes:** which valid option to prefer.
- **Mutates:** **nothing authoritative** — it ranks/selects; owners commit.
- **Never controls:** world truth. It cannot author facts outside system
  permissions and may never directly mutate authoritative state (the Human Test
  bounds anything it influences).

## Expression

### Audio Ecology Engine
- **Owns:** sonic rendering of place, time, weather, crowd, memory, matchday.
- **Reads:** all relevant domain state.
- **Proposes:** nothing to domains.
- **Mutates:** audio presentation only.
- **Never controls:** any authoritative fact (presentation renders, never decides).
