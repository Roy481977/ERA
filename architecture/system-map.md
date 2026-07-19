# ERA — System Map

**Status: PROPOSED.**

## Authoritative foundations

### Time Engine
Owns the shared clock, calendars, seasons, elapsed time and simulation stepping.

### World Persistence Engine
Owns stable identity, current state, historical state changes, saves, migrations and recovery.

### Semantic Place Graph
Owned jointly by architecture and the Town Engine: places are not coordinates only; they have purpose, capacity, accessibility, social meaning and temporal rules.

## Living-world systems

### Town Engine
Turns resident intentions into situated activity and movement.

### Relationship Engine
Owns evolving bonds, tensions, familiarity, obligations and social permissions.

### Crowd Engine
Owns anonymous and semi-persistent population behavior at scale.

### Weather & Season Engine
Owns environmental conditions and seasonal pressure on routines and place use.

## Meaning systems

### Memory Engine
Records meaningful traces and retrieves the right ones in context.

### Recognition Engine
Determines when the Club independently reflects the player's mark back to them.

### Club Culture Engine
Owns emergent traditions, norms, symbols, preferences, grudges and identity.

### Narrative Engine
Shapes legible arcs from true world events without inventing false facts.

## Football and consequence

### Matchday Engine
Transforms fixtures into district-wide anticipation, ritual, attendance, emotion and aftermath.

### Economy Engine
Turns football and fantasy performance into resources, constraints, trade-offs and long-term consequences.

## Orchestration

### Event Engine
Owns authored and systemic events, conditions, consequences and event lifecycles.

### AI Director
Selects among valid possibilities to improve pacing, variety and emotional coherence. It cannot author facts outside system permissions.

## Expression

### Audio Ecology Engine
Renders place, time, weather, crowd, memory and matchday state through sound.

## Core data flow

```text
Time + Persistent State
        ↓
World conditions and available places
        ↓
Resident needs, relationships and obligations
        ↓
Intentions
        ↓
Town execution and crowd expression
        ↓
Events and consequences
        ↓
Memory, recognition, culture, narrative and economy
        ↓
New persistent state
```

## Ownership rule

Every fact has one owner.

Other systems may read it, react to it or request a change, but they do not duplicate authority. This prevents contradictory memories, impossible schedules and AI-generated state drift.
