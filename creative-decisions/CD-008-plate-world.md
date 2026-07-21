# CD-008 — The Plate World (pre-rendered 2.5D)

**Status: LOCKED (Roy, 2026-07-21).** Supersedes the runtime-3D asset path for the
*world fabric*. The simulation is untouched.

## The decision

The town is rendered as a **pre-rendered master plate**: one very-high-resolution
AI-generated image of the whole district in the locked clay/felt macro-diorama
style, sliced into a streaming tile pyramid. Everything alive is composited on
top of it at runtime. The camera direction is fixed (already decided); the plate
exploits that fully.

The layer stack, bottom to top:

1. **Plate** — the district as one ~8K image, tiled (map-style pyramid). Mobile
   scrolls a crop; desktop shows the wide view; zoom streams sharper tiles.
   Whole-town payload ≈ 5–15 MB.
2. **Depth mask** — rendered from the Three.js blockout at plate resolution;
   per-pixel occlusion so residents walk *behind* buildings.
3. **Living layer** — residents/dogs/birds/cars from the behaviour stream
   (sprites or mini-3D), depth-tested, tinted by time-of-day.
4. **Light & weather** — additive night-lights overlay (windows, lamp pools),
   time-of-day colour LUTs, weather particles/shaders; seasons as plate variants.
5. **Ambient life** — chimney smoke, laundry, flags, water shimmer: looping
   micro-effects pinned to the plate.

## Why

- **The 40 MB café made the math undeniable.** A full town in runtime 3D is
  hundreds of MB even after heavy optimization, weeks of per-asset labour — and
  still caps *below* the reference look, because the reference's richness
  (painterly GI, moss, clay glow, prop density) is rendered-image quality that
  real-time low-poly 3D cannot reach on a phone.
- **The camera never rotates.** With a fixed view direction, a pre-rendered
  plate buys reference-exact pixels at ~1% of the weight. (The lineage:
  Disco Elysium, classic pre-rendered adventure games.)
- **AI image models are already masters of exactly this style** — the reference
  images *are* this medium. We stop reconstructing the look from triangles.

## How it stays ERA

- The Rust sim and behaviour stream are unchanged; determinism untouched.
- The existing Three.js scene becomes the **control rig**: built from true world
  coordinates, it renders the blockout + depth + masks that structure-lock the
  image generation (depth ControlNet), so every sim coordinate maps to an exact
  plate pixel forever.
- **Meshy's role sharpens**: characters + motion (rig/animate → render walk/sit/
  greet cycles from the canonical camera into sprite sheets, baking the clay
  look into every frame), plus occasional hero 3D. The café GLB becomes a
  *source* asset placed in the blockout so the plate matches its silhouette.
- The slow generative world works as **plate edits**: district evolution is
  offline AI-inpainting ("a market stall appears by the square"), versioned in
  git like all art bytes. Runtime-placed items are composited sprites.

## Accepted trade-offs

- Camera truly locked (already our choice).
- Deep zoom bounded by plate resolution — mitigated by tiles; later,
  per-location close-up plates (adventure-game style) for interwoven-lives
  moments.
- World-fabric changes require a plate edit, not a code line — acceptable at the
  generative world's slow pace.

## Rejected alternatives

- **Optimized true 3D** (decimate + Draco/KTX2 everything): 150–400 MB, heavy
  per-asset labour, look caps below the reference. Revisit only if free camera
  or deep continuous zoom ever becomes core.
- **Hybrid plate + 3D heroes**: two pipelines to maintain; deferred, not dead —
  close-up plates likely cover the need.
