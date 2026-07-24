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

## Scripts (proven)
- `inspect_rig.py <glb>` — dump objects, armature bones, meshes, actions.
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

## Remaining phases
1. Tune + lock the plate camera to the compositor's exact projection.
2. Author the full behaviour set for the fox (template), review, lock the parametric
   recipes per body-plan (quadruped / bird / wader / small-ground).
3. Meshy-rig + export the other 6 animals; author their sets.
4. Render sprite sheets (N frames/behaviour × headings) → asset manifest
   `id → {reference, glb, sheets, pivot, states, provenance}` → compositor sprite swap.
