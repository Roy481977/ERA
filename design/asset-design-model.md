# ERA — Asset Design Model

*A strict, layered specification for generating every visual asset in ERA —
residents, motion and body language, props, light and effect — consistently, at
scale, mostly with AI, and rig-ready for PixiJS + Spine/Rive.*

**Status: FOUNDATION / v0.1.** Prepared for Roy. Downstream of
[research/visual-engine-and-design-strategy.md](../research/visual-engine-and-design-strategy.md)
(stack: Rust sim core → behaviour stream → PixiJS renderer, Spine/Rive residents).
This document is **canonical and strict**: an asset that does not pass the
[acceptance tests](#layer-4--acceptance-tests-the-gate) does not enter the game.

**The north star (Roy):** *stylized isometric with painterly rendering — an
isometric miniature-world diorama, soft depth-of-field, semi-realistic materials,
painterly lighting, architectural-visualization polish, tilt-shift photography.
Almost as if someone built a beautiful scale model of the town and filmed it.*

**How this document is layered** (you asked for both a bible and a machine model):

- **Layer 0 — the invariants.** The style law. Non-negotiable, applies to every asset.
- **Layer 1 — the art bible.** The *taste*: the feeling, references, palette, what
  makes ERA look like ERA. For human eyes.
- **Layer 2 — the machine model.** Strict schemas for characters, motion/body
  language, props, and light/effects. Machine-usable; the source of prompts.
- **Layer 3 — the AI generation protocol.** Master prompt, per-asset prompt schema,
  the hybrid/phased consistency strategy, and rig-prep rules.
- **Layer 4 — the acceptance tests.** The gate every asset passes before use.
- **Layer 5 — the pipeline & tooling.**

Layers 1 governs *why*; Layers 0/2/3/4 govern *how*. When they seem to disagree,
Layer 0 wins.

---

## Layer 0 — the invariants (the style law)

These are fixed once and rarely changed. Every asset, AI-generated or hand-made,
obeys all of them.

**0.1 Projection & angle. — LOCKED.** True **2:1 isometric**, camera pitch **≈30°**
(the "crafted diorama" read; see the board). No perspective convergence — parallel
projection only. Every asset is authored and rendered at this single angle. *One
angle, forever.* This is a locked invariant (Roy, decision): a change would obsolete
every asset, so it changes only by a formal amendment. (If we ever add a second
camera, it is a new asset set, not a re-projection.)

**0.2 Scale & grid.** The world is a **miniature**. One iso tile = **1×1 world
unit**; base tile footprint **128×64 px** at 1× (authored at 2× / 256×128 for
retina, downscaled at runtime). A standing adult resident is **~2.6 tiles tall**
(figurine proportions — slightly large head, sturdy stance, for readability from
above). All props are sized as if on the same model-maker's table.

**0.3 Materials — "semi-realistic model materials."** Surfaces read as a beautiful
scale model, not a cartoon and not photoreal: matte painted wood, fired-clay roof
tile, soft plaster, brushed metal, still water with a gentle specular. **Subtle
hand-painted texture, low-to-mid gloss, rounded bevels.** No hard cel-shading, no
flat vector fills, no photographic grain.

**0.4 Lighting model.** A single warm **key light** (the sun) at a fixed azimuth
(**upper-right**, so shadows fall lower-left), a cool **sky fill**, and a soft
**ambient occlusion** in contact shadows. Painterly, not physically exact — light
is *designed* per time of day (see 0.6). Every asset is authored under **bright,
high-key midday daylight** (the reference brightness); time-of-day is a renderer
treatment (Layer 2.4), not baked in unless a variant is explicitly specified.

**0.5 Tilt-shift depth of field.** The signature. A **sharp focal band** across the
mid-ground; **foreground and background softly blurred**, saturation and contrast
gently lifted in the focal band. This is a **runtime Pixi treatment** (depth-graded
blur + saturation), *not* painted into assets — so it stays consistent and
responsive. Assets must be authored **fully sharp**; blur is applied by the engine.

**0.6 Palette system.** A **single master palette** (Layer 1.3) with four
time-of-day **lighting grades** (dawn / midday / dusk / small-hours). Assets use the
neutral palette; grades are LUT-like tints applied at runtime, driven by the sim
clock. No asset may introduce a hue outside the master palette without a palette
amendment (change control).

**0.7 Silhouette law.** Every character and key prop must be **identifiable in pure
black silhouette** at gameplay zoom. Readability from above beats detail. Author
silhouette first; detail second.

**0.8 Output formats & resolution.**
- Sprites / atlases: **WebP** (fallback PNG), authored at **2×**, power-of-two atlas
  pages, trimmed, with a **1px transparent bleed**.
- Rigged residents: **Spine** (`.json` + `.atlas` + page) *or* **Rive** (`.riv`).
- Naming: `kind.subject.variant@scale` → e.g. `res.milo.idle@2x`,
  `prop.market_stall.dusk@2x`, `fx.window_glow.loop@2x`. Lowercase, dot-separated,
  no spaces. IDs match the simulation's ids where one exists (`res_milo` → `res.milo`).

**0.9 Anchor & footprint.** Every asset declares a **pivot** (the ground-contact
point, for iso depth-sorting) and a **tile footprint** (which tiles it occupies).
Depth sort key = pivot's iso `(x+y)`; taller objects declare height for correct
occlusion.

---

## Layer 1 — the art bible (the taste)

**1.1 The feeling.** ERA should feel *cherished and small* — a town someone loved
enough to build by hand, bathed in **bright, clean midday daylight**, watched from
just above. Fresh and vivid over muted; warmth over spectacle; quiet over busy. The
camera adores the place; the tilt-shift tells you it's a little world you could
hold. Bright and saturated, but never garish; sunny, never grimdark.

**Brightness reference (Roy, canonical):** the shared bright isometric-miniature
town render — vivid grass and trees, a bright football pitch, clean brick and
charcoal-blue roofs under high-key daylight. **This is the target brightness and
saturation.** The palette below (1.3) is tuned to it; if in doubt, err brighter and
more saturated, not muted.

**1.2 References (touchstones, not to copy).** Tilt-shift miniature photography;
architectural-viz "physical model" renders; the diorama warmth of *Monument Valley*
and *Townscaper*; the painted light of *Gris* and studio-Ghibli backgrounds; the
cosy isometric of *Cozy Grove* / *Dorfromantik*. ERA's own thread: the Old Oak, the
river and bridge, market stalls, terracotta roofs, a matchday scarf.

**1.3 The master palette.** **Bright, saturated, high-key daylight** — tuned to the
canonical brightness reference (1.1). Anchors:

| Role | Hue family | Notes |
|---|---|---|
| Warm roofs / accents | bright terracotta `#c65a3a`, brick `#b5613f` | the town's signature warmth |
| Cool roofs | charcoal-blue `#566270`, slate `#6d7a86` | flat modern roofs (as in the ref) |
| Walls (warm) | brick `#b46b4c`, cream `#ece0c4` | plaster & brick, matte |
| Walls (clean) | bright white `#eef0ee` | modern buildings, high-key |
| Foliage | **bright grass `#5aa842`**, tree `#4c9c39`, lit `#6fc253` | vivid, fresh |
| Pitch / lawn | pitch green `#57ab46`, mow-stripe `#66bd53` | the football ground |
| Water | bright teal `#3f9aa6`, lit `#5fc0cc` | river, gentle specular |
| Pavement | warm light grey `#ccc6b8` | paths, plaza |
| Key light | bright daylight `#fbf3dd`, highlight `#fffdf5` | high-key, upper-right |
| Shadow / cool | blue-grey `#45566b` | contact shadows lean cool |
| Night glow | lamp `#f6b74f` | lit windows in the small hours |

Saturation runs **high** (fresh, sunny); values run **light** (high-key). Each
character carries a **mini-palette** (Layer 2.1): a small curated colour identity of
4–6 swatches harmonized to this master palette, with one or two signature accents
that may sit just outside it for individuality. Rules for a mini-palette: it must
read cleanly *together* and *against the town* (no resident dressed head-to-toe in a
town role-hue like roof-terracotta); at most two accents; no neon, no pure black, no
muddy/greyed-out mixes. No neon, no pure black, no muddy mixes anywhere.

**1.4 Do / don't.**
- **Do:** rounded forms, soft contact shadows, hand-painted micro-texture, generous
  negative space, one clear focal subject per scene, warm-cool light contrast.
- **Don't:** hard black outlines, flat vector fills, photoreal skin/faces, harsh
  rim light, busy clutter, more than one hue outside the master palette, baked-in
  blur or baked-in time-of-day.

---

## Layer 2 — the machine model (strict schemas)

Every asset is described by a schema record before it is generated. The record is
the single source of truth for its prompt (Layer 3) and its acceptance test
(Layer 4). Schemas are shown as annotated YAML.

### 2.1 Character schema

```yaml
character:
  id: res.milo                    # matches sim id res_milo
  display_name: Milo
  archetype: busker               # role in town
  age_band: young_adult           # child | teen | young_adult | adult | elder
  build: wiry                      # petite | wiry | average | sturdy | stooped
  height_tiles: 2.6                # per Layer 0.2 (children ~1.9)
  silhouette_tags: [slouch_easy, hands_expressive, instrument_case]
  mini_palette:                    # 4–6 swatches: the character's colour identity
    skin: "#c9926b"
    hair: "#3a2a22"
    garment_primary: "#5a7d86"     # harmonized to the master palette (1.3)
    garment_secondary: "#d9bd8f"
    accent_warm: "#e0a24a"         # 1–2 signature accents; may sit just outside
    accent_cool: "#3f7d86"         # the master palette for individuality
  materials: [woven_cloth, worn_leather, brass]
  wardrobe_states: [default, matchday_scarf]   # optional swappable skins
  # --- the link to the simulation ---
  temperament:                     # sourced from sim: sociability/mood baseline
    sociability: 3                 # -2..3  (Milo is the town extravert)
    resting_posture: open          # open | neutral | closed | guarded
    default_gait: bounce           # bounce | easy | brisk | shuffle | measured
    gesture_frequency: high        # low | medium | high
    personal_space: close          # close | normal | wide
  rig:
    type: spine                    # spine (heroes) | rive (heroes) | sprite (crowd)
    required_states: [idle, walk, hurry, greet, converse, sit, play_music, startle]
    turnaround: [iso_front, iso_back]   # both facings the iso angle needs
  acceptance_ref: AT-CHAR          # which test set applies
```

**Rule:** `temperament` is **not invented by the artist** — it is read from the
simulation (the `sociability`, and the `mood`/`energy` ranges we already model). The
design job is to make that data *visible* (Layer 2.2). This is what keeps the look
and the behaviour telling the same story.

### 2.2 Motion & body-language model (the elaborate part)

Motion is where "alive" is won, so it gets the strictest treatment. Three coupled
pieces: a **state vocabulary** (what), an **expression spec per state** (how), and
**temperament modifiers** (how *this* person does it).

**2.2.1 State vocabulary — locked to the behaviour stream.** The simulation already
emits *behaviour states that unfold* (DS-007) and now a disposition (DS-008). The
animation state machine mirrors them **one-to-one** — no animation state exists that
the sim can't request, and no sim behaviour lacks a visible state:

| Behaviour (sim) | Animation state | Reads as |
|---|---|---|
| idle / present | `idle` | breathing, small weight shifts, look-around |
| travelling | `walk` / `hurry` | going somewhere, purposeful |
| detour / reunion approach | `approach` | closing on a person, orienting to them |
| converse / interaction | `converse` | facing, listening, gesturing, turn-taking |
| greet (start of interaction) | `greet` | nod / wave / raised hand |
| linger with friend | `dwell` | relaxed stance, weight on one leg |
| shared outing depart | `walk` (paired) | two figures matched in pace |
| perform activity (work/sit/play) | role state | `work`, `sit`, `play`, `play_music`… |
| wildlife startle / flee | `startle`, `flee` | quick anticipation then break |

**2.2.2 Expression spec — the twelve-principle checklist, per state.** Each state is
authored against a strict motion spec so figures move with weight, not like sliders:

```yaml
motion_state:
  id: walk
  loop: true
  timing: { anticipation_ms: 90, action_ms: 520, settle_ms: 120 }
  must_have:
    - weight_shift            # hips carry the step; no floating
    - arc_on_limbs            # hands/feet travel arcs, not straight lines
    - overlap_and_follow      # cloth/hair lag the body
    - contact_shadow_tracks   # shadow stays glued to the feet
    - face_leads_turn         # head/eyes turn BEFORE the body (anticipation)
  transitions:
    from_idle: { blend_ms: 160, via: weight_preload }   # never a hard cut
    to_converse: { blend_ms: 200, via: decelerate_then_face }
  forbid:
    - linear_translation_without_gait
    - instant_facing_flip
```

The engine's **steering layer** (arrive, separation, face-before-move, hesitation —
already proven in the Bevy prototype) supplies *velocity and spacing*; the **rig
state machine** supplies *body*. The contract between them is the behaviour stream:
behaviour → animation state; steering → velocity; rig blends accordingly.

**2.2.3 Gesture library — a controlled vocabulary.** Gestures are small overlays
that can play on top of a base state (e.g., a wave during `greet`). Each is defined
once and reused:

```yaml
gesture:
  id: greet_wave
  layer: additive_upper_body
  duration_ms: 700
  intensity_curve: ease_out
  temperament_scale: gesture_frequency   # who does it, how much (2.2.4)
  variants: [small_nod, raised_hand, warm_wave, two_handed]  # by warmth
```

Base gesture set (v0.1): `small_nod`, `raised_hand`, `warm_wave`, `point`,
`beckon`, `shrug`, `head_tilt_listen`, `laugh`, `check_time`, `shush`,
`crouch_to_child`, `crouch_to_dog`, `offer` (hand out), `recoil`. Grows over time;
every addition is versioned.

**2.2.4 Temperament modifiers — the disposition made visible.** The same
`sociability` / `mood` / `energy` that drive behaviour **modulate the animation**, so
a resident's body tells you who they are and how their day is going:

```yaml
temperament_modifiers:
  sociability:                       # stable trait
    high:  { posture: open,   personal_space: close,  gesture_freq: high,  approach_speed: +10% }
    low:   { posture: closed, personal_space: wide,   gesture_freq: low,   approach_speed: -10% }
  mood:                              # drifts through the day
    bright: { spine: lifted, head: up,   gait_bounce: +,  gesture_amp: + }
    low:    { spine: sunk,   head: down, gait_bounce: -,  gesture_amp: - }
  energy:                            # wanes, recovers
    high:  { pace: +,  idle_fidget: + }
    low:   { pace: -,  idle_fidget: -,  lean_on_things: allowed }
```

So Milo (sociability 3) stands open, closes distance, gestures freely; Luca
(sociability −1) holds his space and moves measuredly — and *both* slump a little
when their `mood`/`energy` are low late in the day. **No new data needed; it already
exists in the sim.** This is the design system's payoff.

**2.2.5 Proxemics.** Personal-space rings (close/normal/wide) are honoured by the
steering layer's separation radius per character, and by `converse` staging
(conversation distance = the closer of the two rings). Close friends stand nearer;
strangers keep a wider ring — visible social truth.

### 2.3 Item / prop schema

```yaml
prop:
  id: prop.market_stall
  category: structure          # structure | furniture | vegetation | vehicle | small_prop
  footprint_tiles: [[0,0],[1,0]]
  height_units: 1.2
  pivot: bottom_center
  materials: [woven_cloth, painted_wood]
  palette_roles: [walls, warm_accent]
  states: [closed, open]       # e.g. shutters, awning
  time_variants: []            # usually none; renderer relights
  animated: false              # true → declare a motion_state (e.g. awning sway)
  acceptance_ref: AT-PROP
```

### 2.4 Light & effect schema

Light and effect are mostly **runtime**, driven by the sim clock and behaviour —
kept out of baked art so they stay consistent.

```yaml
light_grade:                   # a time-of-day treatment, applied globally
  id: grade.dusk
  driven_by: sim_clock         # hour → grade blend
  key_tint: "#f0b073"
  fill_tint: "#7c5f8f"
  ambient: 0.55
  saturation: 1.08
  focal_band_boost: 1.12       # tilt-shift focal contrast/saturation lift

effect:
  id: fx.window_glow
  type: emissive_sprite        # emissive_sprite | particle | decal | shader
  trigger: sim.night AND building.occupied
  color: "#f2b45a"
  loop: gentle_flicker
  blend: add
  budget_hint: cheap
```

Effect catalogue (v0.1): `window_glow`, `chimney_smoke`, `river_shimmer`,
`dust_motes` (focal band), `footstep_puff`, `leaf_fall` (Oak), `lantern_bob`,
`rain` (weather engine), `scarf_flutter` (matchday). Each declares a **budget hint**
so a living town of many small effects stays within frame.

---

## Layer 3 — the AI generation protocol

Assets are mostly AI-generated. Consistency across hundreds of them is engineered,
not hoped for. Strategy (your pick): **hybrid, phased.**

**3.0 What is canonical — and what is swappable (Roy, decision).** Two things are
canonical: the **ERA style guide** (this document) and the **canonical asset
library** (the approved, provenance-tracked assets). The generation *model* is not
canonical — it is a swappable part. Concretely:

- **One primary generation workflow.** Standardize on a single funnel now; *every*
  asset passes through it and through this style guide. One road in, one gate
  (Layer 4), one library out. No parallel ad-hoc pipelines.
- **But vendor-agnostic by design.** That funnel is a **model-agnostic adapter**:
  its inputs (master prompt, reference sheets, pose/angle control) and its
  acceptance gate are stable; the model *behind* them is replaceable. When a better
  model appears, we swap the adapter's backend and re-validate against the same
  style guide and library — no change to either. Loyalty is to ERA's look and its
  asset library, **never to a particular model or vendor.**
- **The library outlives the model.** If we change base models, we re-derive any
  style adapter (3.4) from the **canonical library**, so the look is reproduced from
  our own approved assets rather than relearned from scratch.

**3.1 Master style prompt (the constant preamble).** Every generation begins with a
locked block, edited only through change control:

> *isometric miniature diorama, true 2:1 isometric angle, ~30° top-down, parallel
> projection; painterly semi-realistic model materials — matte painted wood, fired
> clay roof tiles, soft plaster, still water; single warm upper-right sun key with
> cool sky fill and soft contact shadows; **bright, saturated, high-key midday
> daylight**; fresh vivid palette [bright grass green, terracotta & brick,
> charcoal-blue roofs, clean white walls, bright pitch green, teal water]; clean
> focal subject, generous negative space; architectural-visualization polish;
> **fully sharp, no depth-of-field, no motion blur, no baked shadows beyond
> contact**; centered on transparent/neutral ground.*

**3.2 Per-asset prompt = master + schema.** The schema record (Layer 2) is compiled
into the specific clause: character build, palette hex, signature accent, wardrobe,
required turnaround facings; or prop category, materials, footprint. **Negative
prompt (constant):** *perspective, vanishing point, cel shading, hard black
outlines, flat vector, photoreal face, neon, harsh rim light, text, watermark,
tilt-shift blur, drop shadow, busy background.*

**3.3 Consistency locking (Phase 1 — start here).**
- **Reference sheet per subject.** Generate and *lock* a canonical reference (a
  character's face/build/palette; a prop's form). Every later generation is
  conditioned on it (image-to-image / IP-adapter / reference).
- **Pose & angle control.** Use a pose/edge control (ControlNet-style) to force the
  iso angle and the exact turnaround facings — the angle is never left to chance.
- **Fixed seeds** per subject family for repeatability; log seed + prompt + model
  version with every asset (provenance, Layer 5).
- **Palette clamp.** Post-process every generation through the master-palette LUT so
  stray hues are pulled into line before review.

**3.4 Consistency locking (Phase 2 — once the look is proven).** Train a **style
adapter (LoRA / fine-tune)** on the *approved* canonical library, baking ERA's
diorama look into the model of the day. Then generation is master-prompt-light and
far more consistent, and new residents/props inherit the style automatically.
Trigger for Phase 2: ~30–50 approved assets that unmistakably share a look. Keep
Phase-1 reference/pose control on top for angle and identity. Because the adapter is
trained from the **canonical library** (3.0), it is **re-derivable on any future
base model** — the style survives a model swap.

**3.5 Rig-prep requirements (AI output → animatable).** A generated resident is not
finished art — it is raw material for a rig. Generations for rigged characters must
provide, or be processed into:
- a **clean turnaround** at the iso facings the rig needs (2.1 `rig.turnaround`);
- **separable layers/parts** (head, torso, upper/lower limbs, hair, accessory) for
  mesh/cutout rigging — generated as parts, or segmented in post;
- consistent **pivot and proportions** across facings (Layer 0.2 / 0.9);
- a **neutral, sharp** render (no DOF, no time-of-day) per 3.1.

Pre-rendered crowd sprites (the non-rigged path) instead provide full **animation
cycles** rendered to sheets at the iso angle.

---

## Layer 4 — acceptance tests (the gate)

The "strict" in "strict model." An asset enters the game only if it passes its test
set. Anything that fails is regenerated or fixed — never waved through.

**AT-STYLE (all assets).**
1. Angle is true 2:1 iso, ~30°, no perspective convergence.
2. Every hue lies in the master palette (LUT diff within tolerance).
3. Authored sharp — no baked DOF, no baked time-of-day, no baked drop shadow.
4. Materials read as painted model, not cartoon or photo.
5. Correct scale vs the reference figurine; pivot & footprint declared.
6. Silhouette test: identifiable in pure black at gameplay zoom.

**AT-CHAR (characters).**
7. Matches the locked reference sheet (identity, build, palette, signature accent).
8. All `rig.required_states` are riggable from the provided parts/turnaround.
9. `resting_posture` / `default_gait` visibly match the temperament from the sim.
10. Child vs adult proportions correct for `age_band`.

**AT-MOTION (rigged states & gestures).**
11. Every state honours its `must_have` list and none of its `forbid` list (2.2.2).
12. Transitions blend (no hard cuts, no instant facing flips).
13. Temperament modifiers are visible (an extravert and an introvert differ on
    screen; a low-mood/low-energy day reads in the body).
14. Contact shadow tracks the feet; cloth/hair overlap present.
15. The five-minute silent test (project-wide): a stranger watching for five
    minutes with no text can read who is who and what is happening.

**AT-PROP / AT-FX.**
16. Prop: footprint, pivot, and depth-sort height correct; states supplied.
17. Effect: within budget hint; driven by sim/behaviour trigger; blends correctly.

**Provenance.** Every accepted asset stores: schema record, final prompt, seed,
model/LoRA version, reference used, and reviewer. So any asset can be regenerated
on-style later. (Nothing changes silently — the art obeys the same law as the code.)

---

## Layer 5 — pipeline & tooling

```
schema record  →  AI generate (master + schema + refs)  →  palette LUT + curate
      │                                                            │
      │                                              AT-STYLE / AT-CHAR gate
      ▼                                                            ▼
  provenance log  ◀────────────────────────────  rig (Spine/Rive) or slice (sheets)
                                                               │
                                                    AT-MOTION gate
                                                               ▼
                                         Pixi atlas + manifest  →  runtime:
                                         depth sort · tilt-shift DOF · time grade
```

**Tools.** AI image/style model of choice (kept behind the master prompt + a LoRA in
Phase 2); a control/reference step for angle & identity; **Spine** or **Rive** editor
for hero rigs; **Blender** for the pre-rendered-crowd path; a palette-LUT + atlas
packing step; a small **asset manifest** the Pixi renderer loads (ids, pivots,
footprints, states) — the same behaviour-stream contract the sim already speaks.

**Definition of done for an asset:** schema record written → generated on-spec →
palette-clamped → passes AT gates → rigged/sliced → packed → manifest entry →
provenance logged. Then, and only then, the renderer may draw it.

---

## Resolutions to the open questions (from the engine doc)

Your north star answers most of them:

1. **Isometric angle:** the miniature-diorama look wants the **true 2:1 isometric**
   (~30°) — Option A on the board. Locked in Layer 0.1 unless you say otherwise.
2. **Residents:** **hybrid** — rig the named cast (Spine/Rive over AI-painted parts)
   for endless expressive motion; pre-render the background crowd to sheets. Layer
   2.1 `rig.type` encodes the split.
3. **Bring in an artist:** not yet. This model is designed so **AI + the acceptance
   gate** carry us to a proven look first; a human art-director/rigger becomes worth
   hiring once Phase-2 (the trained style model) is ready to scale.
4. **Prove-it slice:** unchanged and recommended next — **one resident** crossing an
   iso square, alive, driven entirely by the live behaviour stream, authored to this
   model. It doubles as the first real test of Layers 2–4.

---

## Change control

This model is strict, which means changes are deliberate. Any change to Layer 0
(invariants) or Layer 1.3 (palette) is a **versioned amendment** with a reason,
recorded here and in the CHANGELOG, exactly as code changes are. Layers 2–5 grow
(new states, gestures, props, effects) by **addition**, versioned, never silently.

---

## Decisions taken (Roy) — locked into this model

1. **Isometric angle: LOCKED** to true 2:1 iso (~30°). Layer 0.1.
2. **Colour identity: mini-palette** per resident (4–6 swatches, ≤2 accents), not a
   single accent. Layers 1.3 and 2.1.
3. **Generation: one primary workflow, one style guide — but model-agnostic.** A
   single funnel every asset passes through, built as a swappable adapter so better
   models drop in without touching the style guide or the canonical library. The
   style guide and the asset library are canonical; the model is not. Layer 3.0.
4. **Prove-it slice: yes, broadened.** Not one resident in isolation — a small
   *scene*: two or three residents of visibly different temperament, at least one
   interaction (an approach → greet → converse), on a true-2:1 iso ground in the
   bright palette, **driven entirely by the live behaviour stream**. It exercises
   Layers 0/2/4 end to end (angle, motion/body-language, temperament made visible,
   acceptance) while staying a slice, not the town. Placeholder expressive figures
   first (behaviour over art); real rigged assets follow once the look is proven.
