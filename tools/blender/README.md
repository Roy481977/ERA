# ERA — animal sprite pipeline (Blender)

The behaviour-authoring + sprite-render half of the animal pipeline, proven on the
fox 2026-07-23. Meshy gives us a rigged, textured animal but only a single canned
"Walking" clip (no Text-to-Motion for animal rigs). Everything else — idle, run,
sniff, sit, and the render to plate-ready sprite sheets — is authored here in
Blender via the `bpy` module.

## Environment
- `pip install bpy --break-system-packages` → bpy 5.0.1 (Python 3.11). Downgrades
  numpy to 1.26.4; harmless opencv warning.
- **Rendering: Cycles CPU only.** EEVEE and Workbench need a GPU/EGL context that
  the headless cloud container lacks (EGL_BAD_MATCH → blank frames). `CYCLES` +
  `cycles.device='CPU'` renders reliably. ~16–24 samples is plenty for matte clay
  at sprite size; ~8s/frame at 640².

## Input
The Meshy export (Download → Format glb, **Rigged Character ON**, **Single file
ON**) is a zip with two glb:
- `*_Character_output.glb` — rigged, textured, **rest pose** → author behaviours on this.
- `*_model_Animation_Walking_withSkin.glb` — same rig with the Walking action baked in.

## The fox skeleton (Meshy "Quadruped Dog" rig — 27 bones)
`Hips` (root) · `chest` · `head` `headend` `earend` `R_earend` ·
tail chain `tail tailstart tail1 tail2 tail3` ·
front legs `frontleg frontleg0 frontleg1 frontleg2` + `R_frontleg…2` ·
back legs `backleg backleg0 backleg1 backleg2` + `R_backleg…2`.
Bone names are consistent across Quadruped-Dog rigs (fox, both cats). **Smart-Rig
animals (owl, crow, heron, hedgehog) will have different skeletons** — inspect each
with `inspect_rig.py` before authoring.

## The bird skeleton (Meshy "Smart Rig (Beta)" — 26 generic bones)
Owl, crow, heron, hedgehog go through **Smart Rig (Beta)**: fully automatic (no
manual markers, unlike the Quadruped-Dog rig) but it produces a GENERIC skeleton —
bones named `Bone_000 … Bone_025` inside a `UniRigArmature`, and it does **NOT**
support Meshy's motion library, so there's no canned Walking clip either. Every
clip is authored in Blender. Because the names carry no meaning, run `map_bones.py`
first to identify root / spine / wing chains by their position, then edit the bone
constants in `author_bird.py`.

Proven on the owl 2026-07-24: `Bone_000` = root (whole-body pitch/roll),
`Bone_002` = spine/head, `Bone_005`/`Bone_009` = long fore/aft chains used as
candidate wings. From the plate's overhead ¾ view the soar clip reads as gliding
flight, but those candidate bones don't yet spread the wing — the true wing bones
still need confirming per animal via `map_bones.py`.

## Scripts (proven)
- `inspect_rig.py <glb>` — dump objects, armature bones, meshes, actions.
- `map_bones.py <glb>` — position-map a generic Smart-Rig skeleton (per-bone world
  head, length, parent + normalized position vs mesh center/size). Run before
  authoring any Smart-Rig (bird) behaviour.
- `author_bird.py <glb> <perch|soar> <outdir>` — bird behaviour authoring on the
  Smart-Rig skeleton. `perch` = upright + slow head turn; `soar` = pitch to gliding
  attitude + slow roll/rise + candidate wing beat. Plate ¾ ortho, Cycles-CPU.
- `render_cyc2.py <glb> <out.png>` — import, frame the *deformed* mesh (evaluated
  depsgraph — the rest bound-box is wrong for skinned meshes), plate ¾ ortho camera,
  Cycles-CPU render, transparent bg. The core render step.
- `author_idle.py <base_glb> <outdir>` — TEMPLATE for behaviour authoring: keyframe
  named pose bones parametrically (sinusoidal loop) to build a behaviour, then render
  frames. Idle = Hips/chest breathing bob + head/tail sway. Copy per behaviour.

## Camera (plate ¾ view, matches Krea reference)
Ortho, elevation ≈24°, azimuth ≈+40° (front three-quarter), `ortho_scale = size*1.7`.
Frame from the **evaluated (deformed) mesh bounds** at the cycle's mid-frame.

## Behaviour set → sim Acts (`development/sprint-1/src/sim/wildlife.rs`)
Author, per animal, cycles mapped to the sim's `Act` enum:
- Rest → `idle` (breathing, occasional head turn) ✅ template proven
- Roam → `walk` (Meshy Walking, or re-authored)
- Flee → `run`
- Forage/Hunt → `sniff` (head low, nose down)
- Watch/Perch → `sit`/`alert` (often a near-static pose)
- Groom/Play → optional extras
Still states (sit/watch/rest) can be single posed frames; only locomotion needs a cycle.

## Status (2026-07-24)
- **Fox** (Quadruped-Dog rig): idle / run / sniff / sit authored + Meshy Walk. ✅
- **Bakery cat, black cat** (same 27-bone Quadruped-Dog rig): fox templates reused
  verbatim → idle / run / sniff / sit. ✅
- **Church owl** (Smart Rig): perch + soar authored. ✅ First bird path proven.
- **Crow / heron / hedgehog**: mechanical repetition of a proven path (crow → owl's
  bird path; heron → bird path with long-legs tuning; hedgehog → small-ground). 3D
  meshes generated; texture → remesh → Smart Rig → author remain.

## Roy's flight-atmosphere requirement (birds)
Birds should "free-roam slowly in the sky on flight, then land where they should."
`soar` is the airborne glide clip. Still open:
1. Confirm the true wing bones per bird (`map_bones.py`) for real wing-spread/flap.
2. Author **take-off** + **land** clips to bracket soar.
3. **Compositor change**: move birds along slow sky paths (the atmosphere) and
   trigger the land clip at the destination — this is where flight actually lands
   on-plate, in `web/compositor.js`.

## Remaining phases
1. Tune + lock the plate camera to the compositor's exact projection.
2. Finish crow / heron / hedgehog behaviour sets.
3. Bird flight: wing-bone ID, take-off/land clips, compositor sky traversal (above).
4. Render sprite sheets (N frames/behaviour × headings) → asset manifest
   `id → {reference, glb, sheets, pivot, states, provenance}` → compositor sprite swap.
