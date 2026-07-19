# ERA Research — Town Engine Technical Strategy

| Field | Value |
|---|---|
| Status | **RESEARCH / PROPOSED technical direction** |
| Date | 2026-07-19 |
| Related decision | `creative-decisions/CD-006-simulate-intention-not-movement.md` |

## Executive conclusion

ERA should **build the orchestration brain and buy the execution muscles**.

Do not begin by building custom pathfinding, crowd avoidance, locomotion, or generative conversation. Use mature engine technology for those layers. Build the unique layer that commercial products do not provide: persistent intentions, social causality, shared time, semantic places, relationship-driven interruptions, multi-year continuity and deterministic authoring controls.

## Recommended architecture

### A. Authoritative simulation core — ERA-owned

A headless, data-oriented simulation that can run without rendering.

Core records:

- `WorldState`: game time, day type, season, weather, football calendar, active events.
- `Place`: semantic tags, opening rules, capacity, interaction slots, access constraints.
- `Resident`: identity, role, home, traits, needs, obligations, relationships, arc state.
- `Intention`: actor, purpose, target, earliest/latest time, priority, duration, interruptibility, provenance.
- `Reservation`: place/slot occupancy and time window.
- `Encounter`: participants, trigger, duration, outcome and memory effects.
- `ReasonCode`: exact explanation of why an intention won or failed.

Suggested logic:

1. Generate candidate intentions.
2. Score and arbitrate them.
3. Reserve destination and interaction resources.
4. Ask the engine navigation layer to execute.
5. Detect arrival, delay, blockage, interruption or failure.
6. Commit outcomes to world state and memories.

Use deterministic random seeds and an append-only event log for reproducibility.

### B. Simulation fidelity levels

- **Tier 0 — authored milestone:** protected scene with explicit prerequisites and outcomes.
- **Tier 1 — embodied local:** full pathfinding, animation, interactions and perception near the player.
- **Tier 2 — district logical:** intentions, travel estimates and encounters simulated without full actors.
- **Tier 3 — background life:** coarse state transitions and probabilistic resolution for distant or low-importance residents.

A resident must be promotable between tiers without changing their logical identity or creating impossible continuity.

### C. Semantic-place graph

NavMeshes know where agents can walk. ERA additionally needs to know what places **mean**.

Each place should expose typed slots and affordances such as:

- `WORK_BAKERY_COUNTER`
- `BUY_BREAD`
- `DRINK_COFFEE`
- `WAIT_FOR_PERSON`
- `WATCH_TRAIN`
- `MEMORIAL_PAUSE`
- `MATCH_GATE_ENTRY`
- `SHELTER_FROM_RAIN`
- `DOG_REST_SHADE`

Intentions resolve against affordances, not raw coordinates. The execution layer selects an available slot and route.

## Off-the-shelf layers worth using

### Unreal Engine path

**Strong candidate when ERA wants a dense 3D district and large visible populations.**

- **Mass Entity / Mass Crowd:** scalable data-oriented representation, crowd LOD and replication foundations.
- **ZoneGraph + NavMesh:** lane-style and free navigation.
- **StateTree:** structured behavior execution.
- **Smart Objects:** reservable world interactions and semantic-use points.
- **Animation systems / motion matching:** embodiment after intent is selected.

Epic's current materials specifically combine Mass AI, ZoneGraph, NavMesh, StateTree, Smart Objects and LOD for scalable crowds. This is close to the execution substrate ERA needs, but the Town Engine's persistent social scheduler remains custom.

### Unity path

**Viable when team familiarity, deployment breadth or faster lightweight iteration dominates.**

- **AI Navigation package:** runtime/edit-time NavMesh building, agents, links and obstacles.
- **Entities/ECS:** data-oriented logical simulation at scale.
- **Behavior tooling or custom utility/GOAP layer:** execution of selected intentions.
- **Animation and avoidance packages:** selected based on target fidelity.

Unity's official AI Navigation package solves navigation rather than persistent social orchestration, so the same custom Town Engine requirement remains.

### Commercial AI middleware

Evaluate only after the vertical slice defines exact gaps.

- **Kythera AI:** potentially useful for advanced navigation, behavior authoring and large-agent execution. Validate current engine support, licensing, source access, determinism and runtime cost directly with the vendor.
- **Inworld Runtime:** potentially useful for bounded conversations, character knowledge, memory and goal-triggered expression. It should not control the authoritative town schedule or world truth. Its current documentation emphasizes composable character, memory, voice and goal capabilities, which are complementary rather than a Town Engine replacement.

## Build-versus-buy ruling

| Layer | Default ruling |
|---|---|
| Navigation mesh and pathfinding | Buy/use engine |
| Local avoidance and crowd locomotion | Buy/use engine |
| Animation selection and motion matching | Buy/use engine |
| Semantic interaction slots | Use engine feature where possible; ERA schemas above it |
| Behavior execution | Use engine StateTree/BT/GOAP substrate |
| Persistent schedule and intentions | **Build** |
| Relationship and encounter causality | **Build** |
| Shared long-term world state | **Build** |
| Simulation LOD continuity | **Build**, integrated with engine LOD |
| Conversational generation | Optional buy; bounded and replaceable |
| Designer debugging and replay | **Build** |

## Fast vertical slice — six weeks

The goal is not a beautiful town. It is proof that lives reliably reach the right places for the right reasons.

### Scope

- One small plaza, bakery, café, bridge and stadium gate.
- Eight named residents plus the Old Dog.
- Three day types: ordinary weekday, match day, rainy Sunday.
- Two relationship interruptions.
- One protected milestone event.
- Tier 1 and Tier 2 simulation only.

### Required tools

- Live map showing every resident's current intention, destination and reason code.
- Time scrubber and fast-forward.
- Resident inspector with schedule, relationships and next candidates.
- Place-capacity and reservation inspector.
- Deterministic replay from seed.
- Automated contradiction report.

### Acceptance tests

1. No resident occupies two places at once.
2. Every movement has a valid reason code and destination affordance.
3. Travel time is accounted for before appointments.
4. Closed/full/unreachable places trigger believable fallback behavior.
5. Match day materially transforms flows rather than swapping ambience.
6. Relationship interruptions occur without breaking protected obligations.
7. Fast-forwarded Tier 2 outcomes match continuity when residents become visible.
8. The same seed reproduces the same day.
9. Designers can answer “Why is Hana here?” in under ten seconds.
10. Across a simulated month, no resident becomes permanently stuck or silently disappears.

## Decision gates after the slice

- **Gate 1 — Believability:** do observers spontaneously infer routines and relationships?
- **Gate 2 — Control:** can designers shape outcomes without scripting every route?
- **Gate 3 — Debuggability:** can every failure be reproduced and explained?
- **Gate 4 — Scale:** can the architecture support tens of meaningful lives plus background population?
- **Gate 5 — Engine choice:** does Unreal's Mass/Smart Object stack or Unity's lighter stack better match the actual product target?

Do not license major NPC middleware before these gates expose a specific deficiency.

## Current recommendation

Prototype in **Unreal Engine** if no engine has yet been chosen and the envisioned district is a visually rich 3D space with many concurrent embodied residents. Mass Entity, Mass Crowd, StateTree, Smart Objects and ZoneGraph provide the strongest integrated substrate for the visible layer. Keep the Town Engine itself engine-decoupled enough that its logical tests run headlessly.

This recommendation is technical, not canonical, and should be revisited after target platform, camera, population scale and team expertise are fixed.
