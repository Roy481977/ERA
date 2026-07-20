# DS-007 — The Behaviour Layer: making the simulation observable

**Status: PROPOSED (implementation tracking).** Under the [Book of ERA](../docs/book-of-era/00-the-promise-and-laws.md)
and [DEV-000](DEV-000-development-constitution.md).

Direction (Roy): *"The simulator is becoming richer internally, but I still feel
like I'm reading an event log while dots move around. The next milestone should
not be adding more simulation systems. It should be making the existing
simulation observable. Every important event should have a visible expression in
the world… The simulation should stop producing prose as its primary output.
Instead, it should produce behaviours. The renderer's job is then to visualize
those behaviours."*

And the architecture he asked for:

```
Simulation  →  Behaviour Layer  →  Renderer  →  Observer
```

Two decisions taken with him: **build the Behaviour Layer first, on the current
top-down viewer** (validate the vocabulary and the feel before betting on a new
renderer); and the **eventual real-time district engine will be native Rust +
Bevy** — so the Behaviour Layer is authored as first-class Rust types that a Bevy
client will consume directly, and serialised to JSON for the web viewer in the
meantime. One authoritative world, two renderers over time.

---

## What the Behaviour Layer is

`src/behaviour/` sits between the simulation and any renderer. The simulation
decides *what happens and why*; this layer turns that into **observable behaviour
with space and time** — the data a renderer draws, never a sentence.

It is a stateful **choreographer**. After each simulation tick it observes the
world and produces one `Behaviour` per visible entity:

- **position** (x, y),
- **heading** — which way the thing faces (so people turn toward one another),
- **speed** — movement this tick,
- **pose** — what the body is doing: `walk`, `stand`, `work`, `talk`, `sit`,
  `lie`, `sniff`, `play`, `perch`, `forage`, `alert`,
- **gesture** — a momentary beat over the pose: `laugh`, `gesture`, `nod`,
  `glance`, `wave`, `point`,
- **partner** — who it is attending to.

It keeps memory (last positions and headings, running conversations) so behaviour
is continuous rather than snapped.

### Conversations are the flagship

A meeting is no longer one log line. When the simulation decides two residents
interact, the choreographer **stages** it for a short window (≈20 min): both are
held facing each other in the `talk` pose, with seeded gesture/laugh/glance beats,
and it ends when the window closes or they part. The renderer draws the two a
little apart, turned in, with a soft link and rising speech beats between them —
something you *watch*, not read.

Other behaviours derived today: walkers face their direction of travel; workers,
sitters (the bench), and the schoolchild at play get their own poses; the old dog
walks, then lies / sniffs / looks about where he settles; the animals' poses come
from their activity (a perched bird, a foraging crow, a resting fox).

### The renderer

The current top-down viewer was rebuilt to draw behaviour: facing indicators,
pose-specific marks (a lying oval, a perched chevron, a work tick, a ball at play),
gesture cues, and staged conversations. Co-located, settled entities are scattered
around their node so a gathering reads as individuals. And a **camera** was added
— click anyone to follow-and-zoom, double-click to release — so you can get down
inside a conversation and judge whether it feels alive. The event ticker remains,
demoted to a secondary/debug channel: prose is no longer the product.

---

## The animals (living entities, feeding the behaviour layer)

`src/sim/wildlife.rs` adds seven animals as **persistent entities** — a riverside
fox, two cats, a church owl, a grey heron, the museum crows, a hedgehog — each with
a species, a **character** (how bold around people, how restless), a **home range**
and a **den**, and a **diel rhythm**. Several are nocturnal, so the small hours are
no longer empty. They keep to their range, withdraw when people crowd their spot,
and express through the same poses (`perch`, `forage`, `walk`, `lie`) the renderer
already understands.

### A seed of randomness

`src/sim/rng.rs` adds a small seeded generator (SplitMix64). The residents stay
fully deterministic; the **wildlife** draws from this seed, so a given world seed
always replays the same animal life while a different seed grows a different one —
the small, genuine unpredictability a living thing needs, without giving up
reproducibility. `Simulation::with_seed` / `Engine::with_seed` set it;
`Simulation::new` uses a fixed default (so every existing test is unchanged).

---

## Where this points

The Behaviour Layer is the pivot Roy named: from here, *observation drives design*.
Every future feature becomes valuable the moment it is visible, and the same
behaviour stream that drives the web viewer today will drive the Bevy district
tomorrow — a real-time town with a free camera, follow, and zoom, where we ask
"does this feel alive?" by watching, not by reading logs.

## Files

- `src/behaviour/mod.rs` — poses, gestures, the `Behaviour` type, the `Choreographer`.
- `src/sim/wildlife.rs` — the animals as living entities.
- `src/sim/rng.rs` — the seeded generator.
- `src/engine/` — the engine owns the choreographer, observes each tick, and the
  snapshot carries behaviour per entity (plus the animals).
- `viewer/` — the top-down renderer, now behaviour-driven, with a follow camera.
- `tests/behaviour.rs`, `tests/wildlife.rs` — staged conversations, poses,
  nocturnal life, per-seed reproducibility.
