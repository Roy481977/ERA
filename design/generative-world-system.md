# ERA — Generative World & Asset System

*How ERA grows: a deterministic World Generator that mints new residents,
generations, plants, animals, possessions, seasons and buildings from seed and
history — and slowly reshapes the one home district in place (it never spawns a new
district) — while an Asset Generator, governed by the style guide, dresses each new
thing on-style by reusing the canonical library first and generating only what is
genuinely new.*

**Status: FOUNDATION / PROPOSED.** Prepared for Roy. Sits under the
[Book of ERA](../docs/book-of-era/00-the-promise-and-laws.md) and
[DEV-000](../development/DEV-000-development-constitution.md), and **dovetails with
the [Asset Design Model](asset-design-model.md)** — this document supplies the *what
appears and when*; the asset model supplies the *how it is drawn and gated*. It is
downstream of [research/visual-engine-and-design-strategy.md](../research/visual-engine-and-design-strategy.md)
(stack: Rust sim core → behaviour stream → PixiJS renderer, Spine/Rive residents; the
sim is authoritative) and continues the disposition and togetherness work of
[DS-008](../development/DS-008-social-realism.md).

This is design, not a report of built code. Where it names Rust modules it names the
**proposed** shape; the one increment already in flight — the micro-POI layer
(`world/poi.rs` + incidental dwelling) — is called out as such, and the rest is the
architecture it should slot into.

---

## The core principle: grown, not authored — and still deterministic

ERA's world is not a finite, authored set of places and people that the player
exhausts. It is meant to *keep becoming*. The one home district reshapes slowly in
place (it never spawns a second); residents are born, age,
court, raise children, grow old and die; trees put on rings and drop their leaves;
foxes den and litter; a resident who was cold last winter is wearing a scarf this
one; a season re-dresses everything at once; and every so often the town mines
something new — a bench, a lane, a whole terrace of cottages under construction. The
Vision already asks for exactly this: *buildings age, trees grow, children become
adults, new traditions emerge, the passage of time should be visible.* This document
is the machine that makes that literal.

The crux — and the hard part — is that **all of this stays deterministic.** ERA's
first law is that the same seed replays the same town (CD-007; DS-008: *"a given seed
replays identically"*). A world that grows must not become a world that drifts. The
resolution is a clean separation between *what is decided* and *what is drawn*:

- **The decisions are seeded and procedural.** Whether a new resident is born this
  season, who their parents are, what mini-palette a child inherits, which building
  plot breaks ground, whether a squirrel appears on Mill Lane at 08:14 — all of it is
  a pure function of *(world seed + world history + world time)*, computed in the
  deterministic core the same way `Season::for_day` already computes a season purely
  from the day. Same seed and same history ⇒ the same evolution, down to *which
  library asset* is chosen to represent each new thing.
- **Only the art bytes come from AI, and only once.** When the World Generator mints
  something the canonical library cannot yet dress, the Asset Generator produces new
  pixels through the gate (Asset Model Layers 3–4). Those bytes are then **fixed and
  versioned in the library forever.** They are not re-rolled on the next run.

So the determinism guarantee holds in the exact form that matters: *a world replays
identically, while the library grows across runs.* Two players on the same seed see
the same child born to the same parents wearing the same inherited colours; the first
run may have *minted* those colours as new art, the second run *reuses* them from the
library — but both runs make the same decision and reference the same asset id. The
simulation is deterministic; the asset library is append-only and monotonic. Nothing
about growth reaches into world truth and changes it. This is the same discipline the
Oak already keeps — *history accumulates; nothing already recorded is rewritten* —
applied to the whole world and to its art.

One consequence worth stating plainly: **the library is a shared, cross-run artifact,
not part of any single world's state.** A world's replay depends on its seed and
history; it depends on the library only to the extent of *reading* asset bytes by id.
If an id is present, it is drawn; if it is not yet present (a fresh seed reaching new
territory), it is minted once and then present. The world never asks *when* an asset
was minted, only *which* id it needs — and that id is chosen deterministically.

---

## The two engines, and the link between them

### 1. The World Generator — deterministic, in the sim

The World Generator lives inside the Rust simulation and runs on a cadence tied to
world time (below). Each time it runs it may **mint entities and world changes**:
new districts, residents, generations, plants, animals, possessions, seasonal
re-dressings, and buildings. It draws every choice from a seeded stream derived from
the world seed, salted by *what* it is deciding and *when* — never from wall-clock,
never from uncaptured state. It obeys ERA's standing rules: one owner for every world
fact, every mint explainable from world state, bounded per period so the world grows
gradually rather than lurching.

Crucially, the World Generator decides in terms of **entities and their data**, not
art. It does not know or care how a thing looks. It knows that resident `res_ada` is
a child of `res_mara` and `res_luca`, born in autumn of year 3, sociability derived
from her id, and a mini-palette drawn from her parents' palettes. Turning that record
into something drawable is the other engine's job.

### 2. The Asset Generator — governed by the style guide

For every new thing the World Generator mints, an **AssetRequest** is emitted: a
schema record in exactly the form the [Asset Design Model](asset-design-model.md)
already specifies (Layer 2 — the character / prop / effect schemas). The AssetRequest
is the contract. What happens to it is a three-step funnel, and the ordering is the
whole point:

1. **Library check first.** The Asset Generator tries to satisfy the request from the
   **canonical asset library** — the approved, provenance-tracked, on-style assets we
   already own. Most new things are *variations*, not novelties: a new townsperson is
   a generic rigged body recoloured by her mini-palette; a new bench is the bench prop
   we already have; a new maple is the maple at growth-stage 3 in its autumn skin. The
   Asset Model's mini-palette system (Layer 1.3 / 2.1) exists precisely so identity
   can be expressed as *a recolour of a canonical base*, not a new asset. Reuse is the
   default and by far the common case.
2. **AI mint only for the genuinely novel.** When nothing in the library can honestly
   dress the request — a building typology we have never drawn, a plant species new to
   the world, a possession with no near neighbour — and only then, the request is sent
   to AI generation through the **single model-agnostic funnel** (Asset Model Layer 3):
   master style prompt + the schema clause + reference/pose control.
3. **The gate, then the library grows.** Nothing enters the game unmade or unchecked.
   Every minted asset passes the **acceptance tests** (Asset Model Layer 4 — AT-STYLE,
   AT-CHAR, AT-PROP/FX, and AT-MOTION for anything rigged) and is logged with full
   **provenance** (schema, prompt, seed, model/LoRA version, reviewer). A passing
   asset is added to the canonical library with a stable id — so the *next* request
   for anything like it is answered by step 1. The library compounds: the more the
   world has grown, the less the AI has left to do.

The link, in one line: **schema record → library check → (AI mint → gate) → library
grows → manifest → renderer draws.** The World Generator and the Asset Generator are
coupled only through the AssetRequest and the returned asset id; neither reaches into
the other. The model behind step 2 is swappable exactly as the Asset Model decrees
(§3.0): *the style guide and the canonical library are canonical; the model is not.*
When a better model arrives, we re-derive the style adapter from the library and
re-validate against the same gate — the world's evolution schedule does not change,
because it never depended on the model.

---

## The eight evolution dimensions

Roy named eight ways the world should keep evolving. Each is a distinct generator
with its own cadence, its own deterministic rule, and its own asset implication. The
table fixes the shape; the prose carries the reasoning, because the reasoning is where
the design lives.

| Dimension | Cadence (typical) | Bound per period | Asset path (common → rare) |
|---|---|---|---|
| The district (in place) | years, very slow | change *within* the one district | rearrange the existing kit → AI for a novel typology |
| Residents (arrivals) | weeks–months | ≤1–2 arrivals | recolour generic body → AI for a new archetype |
| Generations (lineage) | life-timed | births rare, deaths rarer | inherited-palette recolour; age-band swap |
| Plants (flora) | seasonal + slow | bounded spread | growth-stage + seasonal skin from library |
| Animals (fauna) | daily–seasonal | population caps | recolour/variant of a species base |
| Possessions | days–weeks | ≤1 item change / resident / period | wardrobe/prop overlay from library |
| Seasons | fixed quarterly | whole world, at once | runtime grade + per-species skins (no new bytes) |
| Architecture | months–years | ≤1 build in progress / district | prop kit → AI for a new building form |

**The district — one home, changing slowly in place (Roy, revised).** ERA does *not*
generate new districts. A player is always placed in *this* one district; it is the
home, and it stays the home. What it does is change *within itself*, very slowly — a
new bench, a grown tree, a market pitch that becomes a permanent stall, a building
plot that breaks ground and, months on, a new frontage where a gap used to be. So the
"district" dimension is really slow **in-place change**: rearrangement and accretion
of the existing modular kit at the district's own edges and corners, on a cadence of
*years*, never a second district. Asset-wise it is mostly *arrangement* of the modular
kit (the visual-engine strategy already argues for a kit "so the town can grow without
bespoke art per building"); only a genuinely new building typology reaches AI. This
folds together with **Architecture** below — they are the same slow hand reshaping the
one place, not a map that sprawls into new tiles.

**Residents (arrivals).** People move to town, not only are born into it. An arrival
is minted with an id, an archetype, a stable `sociability` derived from its bytes
(DS-008 already does exactly this for arbitrary ids), and a mini-palette. Cadence is
weeks-to-months, bounded to one or two per period so recognition survives — *living
before large*: a town whose faces you can learn beats a churn of strangers. Almost
every arrival is dressed by **recolouring a canonical generic body** by the new
mini-palette; only a genuinely new archetype (a role the town has never had) is worth
an AI mint.

**Generations (lineage, aging, death).** The deepest dimension, and the one the
Vision names most explicitly — *children become adults*. Residents age through the
existing age-bands (child → teen → young_adult → adult → elder); close bonds may, over
a long, gated courtship, produce a child; elders decline and, eventually, die. Aging
is deterministic and time-driven; courtship and birth are seeded and *rare*, gated on
relationship depth exactly as DS-008 gates togetherness (bonds "are not created in one
day"). Inheritance is the elegant part: a child's **mini-palette is drawn from the
parents' palettes** — a blend of two curated identities, harmonised back to the master
palette (Asset Model 1.3), with perhaps one accent carried whole from a parent. That
is a *library operation*, not an AI one: the child is a generic child-body recoloured
by an inherited palette, so a new person costs no new art. Death does not delete; the
resident becomes history the way Agnes does in DEV-000 — the Oak remembers, and the
absence itself changes the town. (What a *visibly* aging face needs across age-bands
is an open question below.)

**Plants (flora).** Trees and plants have growth stages, seasonal foliage, and slow
spread. A sapling advances stage over years; each species has a small set of
**seasonal skins** (full leaf / turning / bare / bud), selected by `Season::for_day` —
already a pure function of the day. Spread is seeded and bounded (a verge greens over
seasons; a self-seeded sapling appears near its parent), never a lurch. The Oak is the
worked example already in the code: it owns its season and age and accumulates
history. Asset path: growth-stage frames and seasonal skins are **library variants of
a species base**; a plant *species* the world has never contained is the only thing
that reaches AI.

**Animals (fauna).** Populations rise and fall; new individuals appear; behaviour
shifts with the season (the fox that denned in winter litters in spring). Wildlife is
the one system that *already* draws from the seeded RNG (`rng.rs`), so it is the
natural first home for population dynamics: seeded births and deaths within
per-species caps, seasonal behaviour keyed to the clock. A new individual is a
**recolour or minor variant of the species base**; a new *species* is the rare AI
mint.

**Possessions.** Residents visibly acquire, wear, and lose things — a scarf before
winter, a coat in the rain, a tool for a new trade, a matchday scarf after a victory.
This is `wardrobe_states` and small props in the Asset Model (2.1 / 2.3) driven by the
sim: a possession change is a seeded, explainable event (cold season → scarf; new job
→ tool), bounded to roughly one change per resident per period so wardrobes evolve
rather than shuffle. Almost always a **library overlay/skin swap** on an existing rig;
a truly novel object is the rare mint. This is where "the passage of time is visible"
reads at human scale — you notice Milo has started wearing his father's coat.

**Seasons.** The whole world re-dresses four times a year. This dimension is special:
it mints **almost no new bytes.** Time-of-day and season are *runtime treatments* in
the Asset Model — a light grade LUT (2.4) plus per-species seasonal skins that already
live in the library. Snow, bare branches, warm dusk light: grades and skins, applied
globally, driven by the sim clock, never baked into assets. Season is the cheapest,
most visible evolution we have, and by design it costs the Asset Generator nothing but
selection.

**Architecture (expansion & construction).** New buildings appear over time, and —
because *observation is a design activity* — they should appear *as construction*, not
pop in finished. A building plot (minted with a district, or later on demand) advances
through visible stages (hoarding → frame → clad → finished) over months, deterministic
and time-driven. Most buildings assemble from the **modular prop kit**; a new building
*form* is one of the few things genuinely worth an AI mint, and once minted it joins
the kit for reuse. Construction stages are themselves prop states (2.3), so a
half-built house is library art, not new art.

Across all eight, the pattern repeats: **the sim decides deterministically; the Asset
Generator satisfies from the library first; AI is the rare exception, gated and
versioned.** Growth is mostly *recombination and recolour* of a canon we already own —
which is exactly why it can be unbounded without becoming unruly.

---

## The micro-POI layer: spatial resolution and level of detail

A living place is not a nav node. Between and within the town's locations there is a
finer grain — **points of interest**: sub-locations that give a place its inhabited
texture. Under the stadium's east wing there is a warm spot where the dog naps.
Beside the path there are benches, a verge, a fountain, a den in the roots of the Oak,
a nook out of the wind. Some POIs are *fixtures* (the bench, the fountain, the den);
some are *transient* (a squirrel that appears mid-street and is gone in a minute; a
puddle after rain). Entities interact with POIs by *dwelling* on them: nap, sit,
watch, forage, play, chase.

POIs are the level-of-detail layer that turns travel from teleport-between-nodes into
something incidental and alive. Today a resident going from home to the stadium
resolves a path between locations; with POIs, that same journey can *pass* a bench
someone is resting on, *skirt* a verge a fox is foraging, *pause* while a child breaks
off to chase a squirrel that just appeared. Nothing about the destination changes —
this is finer resolution *within* the world graph, not a new graph — but the space
between places stops being empty. This is the spatial complement to DS-008's
"partial shared paths": there, togetherness was found in movement the sim already
produced; here, incident is found in the space movement already crosses.

POIs are first-class world facts with one owner each, and they **evolve like
everything else** — a new bench is minted (a possession/prop event), a sapling becomes
a tree whose shade is a new nap-spot, a squirrel's appearance is a seeded transient
POI the fauna generator spawns and reaps. So the micro-POI layer is not separate from
the eight dimensions; it is where several of them (flora, fauna, possessions,
architecture) *land spatially*. Each POI carries an AssetRequest like anything visible
— overwhelmingly satisfied by the library (a bench, a fountain, a squirrel), because
the whole point of POIs is density of *familiar* small things.

A first implementation increment of this layer is being built in parallel in the Rust
sim — a `world/poi.rs` module and an "incidental dwelling" behaviour that lets an idle
resident or animal occupy a nearby POI. This document is the architecture that
increment fits into: start with fixture POIs and a handful of dwelling verbs, prove it
reads (a dog that naps in *its* spot, a child who chases *a* squirrel), then let the
generators mint and evolve POIs on cadence. Begin, as always, with the simplest thing
that produces believable life.

---

## The mining cadence model

"Once in a while" has to be made precise, because *when* things appear is as much
world truth as *that* they appear. The cadence model is a deterministic schedule
layered on world time.

The unit is a **generation tick** — a coarse cadence (say, once per world day, or once
per week per dimension; the exact period is tuned per dimension per the table above),
distinct from the fine simulation step. On each generation tick, for each dimension,
the World Generator derives a seeded stream `hash(world_seed, dimension, world_time)`
and asks a bounded question: *does this dimension mint anything this period, and if so,
what?* The bounds are hard caps (≤1 district, ≤2 arrivals, population ceilings, one
build in flight per district) so that growth is **gradual and legible** — the town is
never unrecognisable from one week to the next, which is what recognition and *living
before large* require. Because the schedule is a pure function of seed and time, it is
fully **replayable**: the same seed grows the same town on the same calendar, and a
different seed grows a different one.

Two properties make this safe. First, **idempotence within a run**: a generation tick
that has already fired for a given `(dimension, world_time)` is recorded in history and
never re-fires — the generators read from and write to the same append-only world
state the Oak already models, so replay reconstructs the identical schedule. Second,
**time-safety**, borrowed straight from DS-008's outing logic: no mint may strand the
world (no building blocks the only path, no birth without a viable home, no resident
minted with nowhere to sleep) — the same class of invariant that keeps a resident from
being stranded at 03:00. Growth is bounded, scheduled, replayable, and safe.

---

## Governance: nothing changes silently

Growth does not loosen ERA's discipline; it extends it. Three things are canonical and
change only by deliberate, recorded amendment, exactly as the Asset Model and the
Bible already require:

- **The style guide** ([asset-design-model.md](asset-design-model.md)) governs every
  byte the Asset Generator produces. A minted asset that fails the gate does not enter
  the game — grown or not, the art obeys the same law.
- **The canonical library** is the source of truth for what the town looks like. It
  grows only by **addition**, through the gate, versioned — never edited in place,
  never silently reskinned. The Asset Model's rule holds: *the library outlives the
  model.*
- **Provenance** attaches to everything minted, on both sides. Every generated asset
  carries its schema, prompt, seed, and model version (Asset Model Layer 4); every
  minted *entity* carries the seed, cadence tick, and world-state reason that produced
  it, so we can always answer *why did this district / child / building appear?* from
  world state — ERA's explainability law, applied to creation itself.

The through-line from DEV-000 and the Asset Model is exact: **nothing changes
silently.** A world that grows itself is precisely the case where silent change would
be most corrosive, so it is precisely where provenance and change control matter most.
Growth is not randomness; it is *understandable emergence* — a new thing appears
because the world's state and seed made it appear, and we can show the receipt.

---

## Proposed Rust module plan

The World Generator is a new subsystem in the deterministic core, alongside the
existing `sim/` modules. Nothing here redesigns what exists (DEV-000: *do not
redesign existing architecture*); it extends the world with new owners and a
generator that runs on cadence inside the existing `step()`.

```
src/
  world/
    poi.rs          # NEW (in flight): points of interest — fixtures & transients,
                    #   owner of sub-locations; dwelling targets. LOD within the graph.
    location.rs     # existing: logical places (unchanged)
    navigation.rs   # existing: the nav graph (unchanged)
  sim/
    worldgen/       # NEW: the World Generator
      mod.rs        #   Generator: run(world, history, time, seed) on cadence
      cadence.rs    #   the generation-tick schedule; bounds; seeded streams
      district.rs   #   slow in-place change to the ONE district (no new districts)
      residents.rs  #   arrivals; ids, sociability, mini-palette
      generations.rs#   aging, courtship→birth, inheritance, eldering, death
      flora.rs       #   growth stages, seasonal skins, seeded spread
      fauna.rs       #   populations, individuals, seasonal behaviour (uses rng.rs)
      possessions.rs #   acquire/wear/lose; wardrobe & small-prop events
      seasons.rs     #   whole-world re-dress: grades + per-species skin selection
      architecture.rs#   building plots; construction stages over time
      asset_request.rs#  emits AssetRequests (Asset Model Layer-2 schema records)
    rng.rs          # existing seeded SplitMix64 — the generators' entropy source
    simulation.rs   # existing loop; step() gains a cadence-gated Generator.run()
```

The **Generator** runs inside `step()` but only on generation ticks (cadence.rs),
keeping the fine loop cheap. Each dimension module is a pure-ish function of
*(world, history, world_time, seed)* → bounded set of mints, written into the
append-only world state with one owner per fact. Every visible mint produces an
**AssetRequest** (`asset_request.rs`) — a Layer-2 schema record — which the Asset
Generator (outside the sim, in the pipeline) resolves against the library or mints.
The renderer never talks to the generators; it reads an **asset-library manifest**
(the same manifest the Asset Model's pipeline already defines — ids, pivots,
footprints, states) plus the behaviour stream, and draws. The contract between sim and
renderer stays exactly what DS-008 and the visual-engine strategy fixed: *the sim is
the source of truth; the renderer expresses it.*

The mini-palette is the quiet hero of this plan: because identity is a small colour
record harmonised to the master palette (Asset Model 2.1), `residents.rs` and
`generations.rs` mint *data* (a palette, an archetype, an age-band) and the Asset
Generator turns that into a **recolour of a canonical base** — so an unbounded stream
of new people costs, in the common case, no new art at all.

---

## Acceptance and invariants

This system is only correct if it grows without ever breaking replay. The gates:

**Determinism / replay.** The load-bearing test: *same seed + same history replays
identically* — the same districts, residents, births, buildings and POIs, on the same
calendar, and the *same asset ids chosen* for each. Two runs on one seed must produce
byte-identical world state and identical AssetRequests, whether or not the library
happened to already contain the assets. This is the DS-008 determinism test extended
to creation: run twice, diff the mint log, require zero difference.

**Library monotonicity.** The library only grows, and growth does not perturb replay.
A test runs a seed against an *empty* library (mints everything) and against a *full*
one (reuses everything) and asserts the **world state is identical** in both — only the
provenance log differs (mint vs. reuse). This is the formal statement of "only the
bytes come from AI": the art path must be observationally invisible to the world.

**Bounded growth.** Every dimension honours its per-period caps; no generation tick
exceeds them; the town remains recognisable week to week. A test walks a long horizon
and asserts population, district count, and build-in-progress stay within bounds and
grow monotonically, never lurching.

**Time-safety.** No mint strands the world: every birth has a home, every building
leaves the graph connected, no POI or construction blocks the last path. Reuse the
DS-008 invariant harness ("no one stranded at 03:00") generalised to creation.

**Provenance & the gate.** Every minted entity has a world-state reason; every minted
asset has full provenance and has passed AT-STYLE/-CHAR/-PROP/-FX (and AT-MOTION when
rigged). A thing with no receipt does not exist. Nothing changes silently.

**Observability.** Per DEV-000, every one of these must be *watchable*: the observer
and `chronicle` should narrate a birth, an arrival, a season turning, a house going
up — *"a sapling by the bridge has grown enough to shade the new bench"* — because a
system that cannot be observed is incomplete.

---

## Open questions for Roy

1. **Aging faces across age-bands.** A child becoming an adult over years is the
   Vision's signature promise, but a *visibly* aging face is more than a mini-palette
   recolour — it may want per-age-band base bodies, or a small AI mint per resident at
   each band transition. How literal should aging look: distinct silhouettes per band
   (library bases), or genuinely evolving faces (rarer, costlier)?
2. **Death, and how much the world keeps.** DEV-000's example is Agnes: after she
   dies, the Oak goes unvisited for weeks. Should death ever remove a resident's
   *asset*, or is the rule strictly append-only — the person becomes history and their
   art is retired but never deleted? (Proposed: never deleted.)
3. **Cadence, felt.** How fast should the town *feel* like it's growing — a birth a
   season and a building a year (a slow, human town), or livelier? This tunes the
   per-dimension periods in the cadence table and trades recognisability against
   visible change.
4. **New species and typologies — how novel is too novel?** The system will happily
   mint a new plant species or building form when the world reaches for one. Do we want
   a curated whitelist of what the generators may *reach for* (keeping the town's
   identity tight), or an open hand (letting the town surprise us within the style
   gate)?
5. **Where the library lives.** The canonical library is a shared, cross-run artifact
   that grows over time. Is it a repository-versioned asset store (auditable, diffable,
   the DEV-000 way), and if so, how do we keep replay reproducible for a player whose
   local library is behind the latest mints? (Proposed: manifest carries the ids a
   replay needs; missing ids mint on demand, deterministically.)
