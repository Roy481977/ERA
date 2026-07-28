# Sprint 024 — Tactile Facades (materials Priority 4, solved)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — four neutral canvases, colour-modulated by the
existing palette, so every kit hue stays canon.**

## What was built

Four hand-drawn material canvases now clothe the village, each drawn in
neutral tones and multiplied by the kit's own colours:

- **Brickwork** — running-bond courses with light mortar joints and
  per-brick value jitter, world-scaled so courses stay 20 cm on every
  building regardless of size.
- **Plaster** — soft mottle with faint trowel arcs; the render finish
  that reads hand-finished at arm's length and calm at street distance.
- **Weathered tile** — staggered courses with per-tile jitter and
  vertical weather streaking, applied to *every* roof through the
  gable-roof builder itself — pantile, warm clay and slate all read as
  laid coverings now, not painted prisms.
- **Plank timber** — grained boards for the barn, the field barn, the
  stable and every garden shed.

The extruded geometry's UVs turn out to run in world metres around each
building's perimeter, so one texture serves every footprint at a
consistent physical scale — verified before committing.

## Success criteria, answered

Warm brickwork — coursed, jittered, mortar-jointed. Soft plaster —
mottled and trowelled. Aged timber trims — the plank grain on the
working buildings (painted trim boards stay flat-colour: Museum trim is
painted joinery, which *should* read smooth). Weathered tile roofs —
every roof, both tile families. Before/after: the Sprint 018 corridor's
walls are sheet plastic; the same corridor now has surfaces.

## Honest notes

Brick appears only on the ~30% of homes the palette seeds as brick —
the rest are render, which is the canon village mix; if Roy wants a
brickier town it is one palette weight. The trowel arcs read slightly
strong on the largest uninterrupted walls (the bakery flank); one
alpha step down if it bothers. Box-geometry elements (links) keep
plain plaster colour since their UVs are per-face; invisible in
practice.

## Deliverables

`era-town-3d.html` · `materials_sheet.png` · this record.
