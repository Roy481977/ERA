# ERA — Visual engine & design strategy

*A decision document: how to give ERA a high-end look — town, movement, and
residents — while keeping it in the browser and keeping the simulation
authoritative.*

**Status: RESEARCH / PROPOSED.** Prepared for Roy. Sits alongside
[research/town-engine-technical-strategy.md](town-engine-technical-strategy.md)
and the renderer thinking in [DS-006](../development/DS-006-live-engine.md) /
[DS-007](../development/DS-007-behaviour-layer.md). Facts current as of July 2026;
sources listed at the end.

---

## 1. What we're deciding, and the three constraints you set

We need a **visual engine** — a rendering stack — that can carry ERA to a genuinely
high-end look for the town, its movement, and its residents. You set three
constraints that decide almost everything:

1. **It stays in the browser.** Everyone plays at a URL; no download, no terminal.
   That rules the target platform to WebGL2 / WebGPU via WebAssembly.
2. **The art direction is polished top-down / isometric.** Not photoreal 3D — a
   beautiful, readable, stylized world seen from above.
3. **You want a recommended split** between keeping the deterministic Rust
   simulation authoritative and consolidating everything into one engine.

The short version of the recommendation, so the rest of the document has somewhere
to land: **keep the Rust simulation as an authoritative WebAssembly core, and build
the polished top-down renderer in a 2D-native web stack (PixiJS v8) with a
state-machine character system (Rive or Spine) for residents.** The renderer stays
a pure observer of the behaviour stream we already designed. Bevy — the current
district — becomes an internal reference build during the transition, not the
shipping renderer. Section 8 lays out why and how; the middle sections are the
evidence.

This is the natural continuation of the architecture we already committed to:

```
Simulation (Rust)  →  Behaviour Layer  →  Renderer  →  Observer
     the truth          states, not          the       you
                        prose                variable
```

Everything below only changes the **Renderer** box. The truth stays put.

---

## 2. The one decision that matters most: keep the sim, swap the renderer

Before comparing engines, resolve the split — because it determines *what kind* of
engine we're even shopping for.

The deterministic Rust simulation is ERA's crown jewel. It is what lets the same
seed replay the same town, what makes bonds forming over weeks trustworthy, what
keeps the world honest ("nothing changes silently"). Rewriting the sim inside a
game engine's scripting language would trade that away for nothing — the sim
doesn't need a renderer's help to be correct.

So the split is not "sim vs. engine." It is: **the sim is an authoritative core that
runs headless and emits a behaviour stream; the renderer is a replaceable client
that consumes it.** This is a well-worn, proven pattern — a Rust/WASM core doing the
heavy, correctness-critical work, with a rendering layer over the top. It gives us
three things at once:

- **Determinism is preserved absolutely.** The renderer can never change world truth
  because it only ever reads it. If the renderer has a bug, the world is still right.
- **The renderer becomes a low-risk experiment.** We can try Pixi, keep Bevy as a
  reference, even run two renderers off one core, without touching the simulation.
- **We hire/skill for the renderer independently.** High-end 2D art and animation
  live in a different toolchain and talent pool than systems programming.

What this rules out: consolidating sim + visuals into Unity/Unreal/Godot as one
project. That path (Section 4, "consolidate") is viable but it dissolves the
pure-Rust determinism guarantee, and we'd gain little for a top-down 2D game that
Pixi already serves better. **Recommendation: keep the sim authoritative; treat the
renderer as the variable.** Every option below is judged as a *renderer over the
existing core*, not as a replacement for it.

---

## 3. The renderer options, compared

For a **browser, top-down/isometric, high-end 2D** game, the field splits into three
families. The table is a first pass; the prose after it is where the real judgement
is.

| Option | Type | Web target | 2D/iso fit | Art & animation pipeline | Keeps Rust core | License |
|---|---|---|---|---|---|---|
| **PixiJS v8** | 2D renderer | WebGPU + WebGL2 | ★★★★★ native 2D | ★★★★★ huge web-2D ecosystem | ✅ pure observer | MIT |
| **Bevy (current)** | Rust game engine | WebGL2 *or* WebGPU | ★★★☆ 2D works | ★★☆ thinner 2D art tooling | ✅ shares types | MIT/Apache |
| **Three.js** | 3D library | WebGPU (growing) + WebGL2 | ★★★☆ 2.5D via ortho cam | ★★★★ large community | ✅ observer | MIT |
| **Babylon.js** | 3D engine | WebGPU (advanced) + WebGL2 | ★★★☆ 2.5D via ortho cam | ★★★★ most complete free engine | ✅ observer | Apache 2.0 |
| **PlayCanvas** | 3D engine + editor | WebGL2 (WebGPU maturing) | ★★★☆ 2.5D | ★★★★ Unity-like hosted editor | ✅ observer | MIT engine / paid editor |
| **Godot 4** | Full 2D+3D engine | WASM export (memory caveats) | ★★★★ strong 2D/iso | ★★★★ full editor | ⚠️ only as embedded wasm lib | MIT |
| **Unity WebGL** | Full engine, export | WebGL2 (WebGPU experimental) | ★★★ | ★★★★★ but heavy | ⚠️ | Proprietary |

### The 2D-native path — PixiJS v8 (recommended foundation)

PixiJS is a **2D-first rendering engine for the web**, which is exactly the shape of
our problem. v8 ships **dual backends — a modern WebGPU renderer and a maintained
WebGL renderer — and only the selected one loads for a given user**, so we get
tomorrow's performance where it's available and universal fallback where it isn't.
Its v8 rewrite posts large gains over v7 (sprite-heavy scenes render several times
faster on both CPU and GPU), and it carries the features a *polished* town needs:
Photoshop-like filters and blend modes, gradients, masks, and hardware-accelerated
2D camera through render groups. A living town is thousands of small moving sprites,
lights, and shadows — Pixi's entire reason for existing.

Its one "weakness" — it is a renderer, not a whole engine, so game systems sit on
top of it — is not our weakness: **our game systems already live in the Rust core.**
Pixi does the one thing we need (draw a beautiful 2D world fast) and stays out of
the way of the one thing we've already built (the simulation). That is a near-ideal
fit.

### The single-language path — stay in Bevy

Bevy is where the district lives today, and it has real virtues: it is Rust end to
end, so the renderer can share types with the simulation with no serialization
boundary, and determinism is trivially intact. It renders both 2D and 3D and runs in
the browser on **either WebGL2 or WebGPU** — though notably *not both from one wasm
bundle today* (a known limitation), so we'd pick a backend or ship two builds.

Where it strains against *this* brief is the art direction. "High-end top-down/iso
designs" is an **art-and-animation** problem more than a rendering-horsepower
problem, and Bevy's 2D content pipeline — sprite atlases, skeletal animation,
tilemaps, the tools an artist actually touches — is younger and thinner than the web
2D world's, and its designer/artist talent pool is far smaller than "someone who
knows Pixi/Spine/Aseprite." Bevy is an excellent *engineer's* engine; it is a harder
place to make a game *look* expensive. Keep it as a reference build (it already
validates the behaviour stream natively), but it is not the fastest road to beauty.

### The 2.5D path — Three.js / Babylon.js / PlayCanvas

These are 3D engines. For a stylized isometric look they're used with an **orthographic
camera pointed at low-poly or pre-lit 3D models** — "2.5D." That buys real-time
lighting, smooth rotation, and true depth for free, at the cost of a 3D asset
pipeline (modelling, rigging, materials) that is heavier than 2D sprites. Of the
three, **Babylon.js** is the most feature-complete free option (Apache 2.0,
integrated Havok physics, a free web editor, advanced WebGPU); **Three.js** offers
maximum control and the largest community but you assemble the game systems (fine —
ours are in Rust); **PlayCanvas** gives a Unity-like hosted editor (MIT engine, paid
editor). This family is the right call *only if* we decide residents should be
actual 3D figures seen from an iso camera. For hand-crafted 2D charm, it's more
pipeline than payoff.

### The consolidate path — Godot 4 (or Unity)

Godot 4 is a full 2D+3D engine with genuinely strong isometric/tilemap tooling and
an improving web export (4.3/4.5), though browser builds carry **WASM memory-ceiling
caveats** worth prototyping before betting on. The catch is philosophical: Godot
wants to *be* the game, including its logic. To keep our Rust core we'd embed it as a
wasm library Godot calls — doable, but it fights the engine's grain and re-introduces
a boundary without the ecosystem win Pixi gives us. Unity WebGL is heavier still and
oriented toward porting existing Unity projects; not our situation. **Consolidation
is the option we're deliberately not taking**, for the reasons in Section 2.

---

## 4. Residents: the character-animation layer (this is where "alive" is won)

The town is tiles and props; the *residents* are where high-end reads as high-end,
and where all your movement notes (anticipation, acceleration/deceleration,
secondary motion, spacing, yielding) actually live. Three approaches, and they
compose with any renderer above:

- **Rive** — interactive vector + mesh animation built around **state machines**. Its
  runtime is tiny and renders on WebGL/WebGPU. The reason it matters for ERA
  specifically: **Rive's state machines map almost one-to-one onto our behaviour
  states.** The simulation already emits *states that unfold* — idle, walking,
  talking, sitting, playing, fleeing (DS-007). Feed those to a Rive state machine and
  the character animates itself correctly and continuously, with blends between
  states, no per-frame puppeteering from us. Editor is freemium; runtimes are open
  source. This is the most natural fit for a behaviour-driven world.

- **Spine** — the **industry standard** for skeletal 2D game characters: mesh
  deformation, skins, IK, mature `pixi-spine` integration. Slightly more "animator
  authors clips, code triggers them" than Rive's state-first model, and it's a
  per-seat commercial license, but the animation quality ceiling is very high and the
  tooling is battle-tested in shipped games. If we hire a 2D character animator, this
  is the tool they'll likely already know.

- **Sprite sheets / pre-rendered 3D** — the classic high-end isometric technique
  (the Diablo / Age of Empires / SimCity lineage): model and animate residents in
  Blender, **pre-render them to sprite sheets from the iso angle**, and draw them as
  sprites. It gives a rich, lit, "expensive" look at browser-cheap runtime cost, and
  degrades gracefully. The trade-off is that pre-rendered frames are fixed — less
  runtime flexibility than Rive/Spine skeletal rigs, and a bigger asset footprint.

**Recommendation for residents:** start with **Rive**, because behaviour-state →
animation-state is the cleanest possible mapping to what the sim already produces,
and it keeps residents *continuously* animated (your "states that unfold" principle)
for very little runtime weight. Hold **Spine** in reserve for the day we want a
dedicated 2D animator pushing the fidelity ceiling; reserve **pre-rendered sprites**
for set-dressing and crowds where individual rig flexibility doesn't matter.

---

## 5. Design — art direction for a polished isometric living town

The "+ design" half. An engine renders whatever we design; the design is what makes
it look high-end. Six decisions to make, roughly in order.

**Projection and camera.** Choose between *true isometric* (2:1 dimetric tiles, the
classic look), a gentler *dimetric*, or a *top-down orthographic* tilt. Isometric
reads as "crafted world"; top-down reads as "map/board." For a town of people you
want to *know*, a true or near-true isometric angle gives faces and body language
room to read while keeping buildings legible. Lock this early — it dictates every
asset's angle.

**Residents, silhouette-first.** With a small named cast, individuality is
everything and it starts with silhouette: distinct body shapes, gait, and a signature
palette per person before any detail. From an iso camera you have limited pixels for
a face, so **posture and motion carry identity** — Milo (outgoing, +3) moves and
stands differently from Luca (keeps his corner, −1). This is where the disposition
work we just shipped pays off visually: temperament is already in the data; the
design job is to make it *visible* in stance and pace.

**Movement and animation, mapped to behaviour.** You've been consistent that "alive"
is proven by *how* figures move, not how they're drawn: anticipation before a turn,
acceleration and deceleration, natural stopping, secondary motion, spacing and
yielding, hesitation. Two systems produce these together — the **steering** layer (in
the renderer or the behaviour layer: arrive, separation, face-before-move, all of
which the Bevy prototype already does) governs *paths and spacing*, while the
**character rig's state machine** (Rive/Spine) governs *body*. The behaviour stream
is the contract between them: each resident's current behaviour state selects an
animation state; the steering gives it a velocity; the rig blends accordingly. Design
the **state vocabulary** deliberately — idle, walk, hurry, greet, converse, sit,
play, shoo, startle — one visible pose-set per behaviour the sim can emit.

**The world: tiles, props, depth.** An isometric town is a tile-and-prop kit plus
correct **depth sorting** (who occludes whom) — the perennial isometric engineering
detail, cleanly handled in Pixi with sorted render groups. Design a modular kit
(paths, walls, roofs, market stalls, the Old Oak, the river/bridge) so the town can
grow without bespoke art per building.

**Light and time.** ERA already has an authoritative day/night clock. Design lighting
as a *function of sim time*: warm low sun in the afternoon, blue small hours when the
animals are abroad, lit windows at night. In Pixi this is tint + additive light
sprites + soft shadows; it is one of the highest-impact, lowest-cost ways to look
expensive, and it's *driven by the simulation*, so it's always truthful.

**The asset pipeline and tools.** Decide the toolchain and stick to it: **Aseprite**
for hand-pixelled sprites and tiles; **Blender** for pre-rendered iso characters/props
if we take that path; **Rive** or **Spine** editors for rigged residents; a texture
atlas step for load performance. Define formats (atlas JSON + PNG/WebP, Rive `.riv`
or Spine JSON/atlas) and how the renderer loads them, so an artist can add a resident
or a building without touching engine code.

---

## 6. How to choose objectively — a weighted rubric

If we want to defend the choice (or re-run it later), score each renderer on these
weighted criteria rather than on taste:

| Criterion | Weight | Why it matters for ERA |
|---|---|---|
| Browser fidelity ceiling (2D/iso) | 25% | The whole point: how good can it *look* in a browser |
| Keeps Rust sim authoritative | 20% | Non-negotiable architectural principle |
| Art & animation pipeline / talent | 20% | "High-end designs" is an art-tooling problem |
| Iteration speed to a beautiful build | 15% | How fast we learn what reads and what doesn't |
| Performance at town scale (100s of sprites, lights) | 10% | A living town is many small moving things |
| Ecosystem, docs, longevity | 10% | We'll live in this for years |

Against this rubric, **PixiJS v8 + Rive over the Rust/WASM core** scores highest for
*this* brief: top marks on fidelity ceiling, sim-authoritative, art pipeline, and
iteration speed; strong on performance and ecosystem. Bevy scores well on
sim-authoritative but loses on art pipeline and iteration-to-beauty. The 3D engines
score well on fidelity but pay an asset-pipeline tax we don't need for 2D. Godot
scores well broadly but costs us the clean determinism boundary.

---

## 7. Recommended stack, and a plan to de-risk it

**The stack:**

- **Core (unchanged):** the deterministic Rust simulation, compiled to WebAssembly,
  running headless and emitting the behaviour stream. Already built.
- **Renderer:** **PixiJS v8** (WebGPU with WebGL2 fallback) — a pure observer of the
  behaviour stream, drawing a polished isometric town.
- **Residents:** **Rive** state-machine characters, driven by behaviour states;
  **Spine** held in reserve for a dedicated animator.
- **Steering/motion:** the arrive/separation/face-before-move logic (proven in the
  Bevy prototype) ported into the renderer or the behaviour layer, feeding the rigs.
- **Reference build:** keep the **Bevy district** as an internal, native, no-JS
  sanity check that the behaviour stream is complete and correct.

**A "prove-it" milestone before committing** (mirrors how we've worked so far — one
unforgettable thing, judged by eye): stand up a Pixi + Rive slice showing **one
resident** crossing an isometric square with real anticipation, accel/decel, and a
state change (idle → walk → greet → converse) **driven entirely by the live behaviour
stream** — no scripted animation. If that reads as alive and expensive in a browser,
the stack is proven and we scale it up. If it doesn't, we've spent a slice, not a
rewrite, and the core is untouched.

**Risks and mitigations:**

- *WebGPU maturity varies by browser* → Pixi's dual backend gives automatic WebGL2
  fallback; no action needed but worth testing on target browsers.
- *A JS ↔ WASM boundary is new surface area* → the behaviour stream is already a
  clean, serializable contract (JSON today); keep it small and typed.
- *Rive for game characters is newer than Spine* → the prove-it milestone tests
  exactly this; Spine is the fallback with identical architecture.
- *Isometric depth-sorting bugs* → a known, solved problem in Pixi; budget a little
  time for it in the first slice.

---

## 8. Open questions for you

1. **Isometric angle:** true 2:1 isometric (most "crafted"), or a gentler top-down
   tilt (more legible map)? This locks every asset's angle, so it's worth deciding
   early — I can mock both.
2. **Residents:** hand-crafted 2D charm (Rive/Spine rigs, Aseprite tiles) or the
   pre-rendered-3D look (Blender → iso sprites, richer lighting, bigger pipeline)?
3. **Do you want to bring in a 2D artist/animator**, or should we get a long way on
   procedural/kit art first and hire once the look is proven?
4. **The prove-it slice:** shall I build the Pixi + Rive one-resident milestone next,
   keeping the Rust core and the Bevy reference exactly as they are?

---

## Sources

- [PixiJS v8 launch — dual WebGPU/WebGL renderers, performance, features](https://pixijs.com/blog/pixi-v8-launches)
- [PixiJS renderers guide (backend selection)](https://pixijs.com/8.x/guides/components/renderers)
- [Web game engines in 2026: PlayCanvas / Three.js / Babylon.js / Unity WebGL](https://app.cinevva.com/blog/2026-06-09-web-game-engines-2026-comparison)
- [Three.js vs Babylon.js vs PlayCanvas comparison (2026)](https://www.utsubo.com/blog/threejs-vs-babylonjs-vs-playcanvas-comparison)
- [What changed in Three.js (2026): WebGPU & workflows](https://www.utsubo.com/blog/threejs-2026-what-changed)
- [Bevy + WebGPU (web rendering backends)](https://bevy.org/news/bevy-webgpu/)
- [Bevy WASM / browser notes (Unofficial Bevy Cheat Book)](https://bevy-cheatbook.github.io/platforms/wasm.html)
- [Bevy issue: WebGL2 and WebGPU in one WASM file](https://github.com/bevyengine/bevy/issues/13168)
- [Godot 4 web export optimization guide (2026)](https://best-games.io/blog/godot-web-export-optimization-guide)
- [Godot 4.5 web export WASM memory ceiling (2026)](https://gamineai.com/blog/godot-4-5-web-export-wasm-memory-ceiling-h2-2026-browser-demo-trend-playbook)
- [Spine character animation runtimes (Esoteric Software forum)](https://en.esotericsoftware.com/forum/d/16118-character-animation-runtimes-spine-and-rive)
- [Rust + WebAssembly book (core-in-WASM pattern)](https://rustwasm.github.io/docs/book/print.html)
