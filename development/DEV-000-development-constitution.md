# DEV-000 — ERA Development Constitution

**Version: 1.0 · Status: Active (RATIFIED by Roy).**

This document governs all implementation work on ERA. Read it before beginning any
implementation. If implementation convenience conflicts with this document, follow
this document.

*Preserved verbatim as delivered by Roy on 2026-07-19. This is the governing law
for the `development/` module; it sits alongside `GOVERNANCE.md` (the repository /
CKO charter) — GOVERNANCE governs how knowledge is preserved; DEV-000 governs how
the simulation is built.*

---

## Purpose

ERA has two inseparable goals.

1. Build an exceptional deterministic world simulation engine.
2. Use that engine to create one of the most believable living worlds ever experienced.

Neither goal exists without the other. The engine exists to support life. The
living world validates the engine. Every engineering decision should strengthen
both whenever possible.

## Vision

ERA is not a collection of game systems. ERA is a world. The player should
eventually feel that the town would continue existing even if they never logged in.

Football is the cultural heart of the first world. It is not the entire world.
People have jobs. Friendships. Habits. Traditions. Memories. Dreams. Places matter.
Time matters. History matters. The simulation should continuously produce stories
that nobody explicitly authored.

## Current State

Sprint 1 established the foundation. The project already contains: deterministic
simulation, replayability, world graph, simulation clock, residents, routines,
proto-intentions, relationships, deterministic interactions, the Old Oak, matchday,
a structured observer, and comprehensive tests. These foundations should be
preserved. Do not redesign existing architecture unless there is a compelling
long-term benefit.

## Development Philosophy

From this point forward, every implementation should make the world feel more
alive. Every sprint should produce behavior that is immediately observable. If a
system cannot be observed, it is incomplete. If a system does not influence future
behavior, question whether it should exist. Prefer extending existing systems over
creating new ones. Prefer depth over breadth. A believable town of 25 residents is
worth more than a shallow city of 10,000.

## The Ladder of Life

Development should generally climb this ladder.

1. The world exists.
2. Residents act.
3. Residents remember.
4. Residents develop habits.
5. Relationships become visible.
6. Places accumulate history.
7. Communities develop traditions.
8. Players become emotionally attached.

Avoid skipping levels by implementing sophisticated systems while lower levels
remain weak.

## Engineering Principles

Maintain: deterministic simulation · engine independence · reproducible replay ·
one owner for every world fact · explainable behavior · comprehensive testing ·
small reviewable commits.

Avoid: speculative architecture · unnecessary abstraction · premature optimization ·
systems without observable purpose.

## Living World Principles

The simulation exists to produce believable life. Every new feature should answer
both questions.

- **Engine Question** — Does this improve the simulation engine?
- **World Question** — Does this improve the lived experience of the town?

If the answer to both questions is "no", do not build it.

## People

Residents should gradually become recognizable individuals. Recognition should
emerge naturally. Players should eventually think things like: "Victor always
arrives early." "Luca never leaves the café before closing." "Karim disappears
after defeats." "The children gather beneath the Oak every Friday." The UI should
not need to explain these things. The player should discover them.

## Memory

Memory is only valuable if it changes the future.

- Bad: Victor remembers Elias. — Good: Victor remembers Elias and therefore waits
  for him before walking to the stadium.
- Bad: Agnes visited the Oak. — Good: After Agnes dies, nobody visits the Oak at
  sunset for weeks. The town itself has changed.

Memory should influence future choices. Otherwise it is merely stored data.

## Relationships

Relationships should rarely appear as numbers. Players should experience
relationships through behavior. Instead of "Affinity +2", prefer: Victor waited for
Elias. Emma crossed the square to greet Karim. Luca saved Victor his usual table.
Residents should reveal relationships naturally.

## Places

Places are long-lived characters. A place should develop identity. Identity comes
from accumulated history: children always play beneath the Oak; supporters
celebrate championships there; flowers appear after tragedies; musicians gather
every Friday evening; the bakery becomes known for early-morning conversations.
People return because of memories, not because of scripts.

## Traditions

One of ERA's long-term goals is the emergence of traditions — repeated behaviors
that become part of the identity of the town: supporters always gather in the
Square before kickoff; the Old Oak receives scarves after victories; residents meet
at the café after evening matches; children race across the bridge every Saturday
morning. Traditions should emerge gradually through repeated behavior.

## Explainability

Every meaningful action should be understandable. At any point we should be able to
inspect a resident and answer: What are they doing? Why? For example — Victor,
current intention: visit Bakery; reason: hungry, bakery is open, Hana is working,
enough time before work. The explanation should come from world state, never from
arbitrary scripting.

## Emergence

We do not seek randomness. We seek understandable emergence. Residents should behave
differently because their circumstances differ, not because random values changed.
Every significant decision should eventually be explainable through the current
world state.

## Complexity

Always begin with the simplest implementation capable of producing believable
behavior. Only add complexity after observing that simplicity has become
insufficient. The simulation should evolve through observation, not speculation.

## Observation First

Every implementation should become visible immediately. Watching the simulation is
part of development. After every meaningful milestone we should be able to observe:
movement, interactions, intentions, habits, memories, relationships, traditions. If
we cannot observe progress, the implementation is incomplete.

## Scope Discipline

Prioritize: memories influencing behavior · recognizable habits · believable
routines · meaningful interactions · evolving places · visible consequences ·
community traditions.

Delay: graphical polish · optimization · advanced AI · massive maps · unnecessary
systems.

## Working Style

Continue implementation through small reviewable commits. Continue automatically.
Stop only when: architecture must change · multiple long-term approaches exist · the
repository requires restructuring · clarification is required to preserve the
vision. Ordinary engineering decisions do not require approval.

## Success

The project succeeds when someone watches the simulation without touching the
controls and begins telling stories: "Victor waited for Elias." "I haven't seen
Agnes today." "The Oak looks different after the victory." "Everyone seems to end up
at Luca's café after matches." "The town feels quieter since Agnes died." Those
stories are the product. The simulation engine exists to make those stories
possible.
