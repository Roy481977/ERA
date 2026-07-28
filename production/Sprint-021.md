# Sprint 021 — The Ground Gets Paint (terrain Priority 1, solved)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — the ground material and wear are presentation.**

## What was built

**A painted ground.** The single matte green is replaced by a rich
multi-scale ground material: broad sun-baked straw patches and deep cool
patches (15–30 m), mid-scale mottling, and a fine speckle — hand-drawn
into one large canvas so the terrain reads painted, not procedural.

**Temperature drift.** Every terrain tile takes a smooth warmth tint
from its distance to the village heart — warm and light where life is,
cooling gently toward the edges and hills. The drift is continuous, so
tile seams stay invisible while wide shots gain a broad value gradient.

**Surfaces that were flat colour join in.** The playing field, the
precinct surround and the green's plateau now carry the same painted
grass under their own mown tints.

**Pathing wear.** Soft warm-earth halos — radial, translucent, no hard
edges — sit where the record says feet actually concentrate: the green's
mouth, around the oak, the square, the bus stop, the school corner, the
bridge crossing and the turnstile approach. They complement the crisp
desire lines grown from the simulation record (ADJ-12) with the broad
wear the brief asked for.

## Success criteria, answered

Broad value gradients — the tile temperature drift plus the large
blotch layer. Sun-baked colour temperature shifts — straw-warm patches
against cool deep greens, warmest at the heart. Gentle pathing wear
between high-traffic zones — seven halos at the places the year's
record names busiest. The before/after reads instantly: the old frame
is a green sheet; the new one is ground.

## Honest notes

The blotch canvas repeats every ~71 m; no repetition was visible in any
verification frame, but a second rotated overlay octave is the upgrade
path if it ever shows. The wear halos are hand-placed from record
knowledge; deriving them directly from the movement heatmap (as the
desire lines are) is the data-native version, queued for a sim-open.

## Deliverables

`era-town-3d.html` · `ground_sheet.png` · this record.
