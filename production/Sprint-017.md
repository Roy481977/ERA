# Sprint 017 — The Tiered Ground (Priority 2, solved completely)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — one data edit splits a drawn path at a tier edge;
all heights are presentation-layer.**

## What was carved

The single flat plane is gone. The district now stands on five levels:

1. **The sunken river channel (−1.0).** The water drops a full metre into
   a cut channel: dark earth faces, a grass ledge half-way down each bank,
   and the humpback bridge's jambs now reach the channel floor — the arch
   finally spans something. The channel's stepped rectangular cuts follow
   the cut-not-moulded law rather than faking erosion.
2. **The mid plane (0)** — streets, square, field, precinct.
3. **The green plateau (+0.35).** The village green rises behind a stone
   retaining edge with two steps at its mouth; oak, benches, swing,
   flowerbed, daisies and worn paths all ride the plateau.
4. **The north terrace (+0.63).** North Lane's cottages, the allotments
   and the orchard stand on a raised terrace behind a capped retaining
   wall, with stone steps at each of the three garden gates. June's
   window now looks *down* the green to the oak — literally.
5. **The ridge** — railway embankment, hills and the stopped train close
   the composition above everything.

A single ground-height function anchors every object and every walking
resident to its tier: houses, trees, hedges, fences, sheds, washing
lines, match flags, benches, the oak, the daisies. Nothing floats;
nothing sinks.

## Success criteria, answered

**"At least three distinct elevation tiers."** Five: sunken riverbed
(−1.0), mid street grid (0), green plateau (+0.35), north terrace
(+0.63), elevated background boundary (embankment +2.2 and the hill
ring). All are visible simultaneously in the western isometric frame.

**"Buildings and infrastructure visually anchor into micro-terraces."**
North Lane's row sits behind a real retaining wall with gate steps; the
green's furniture stands on the plateau above the street; the allotment
beds and sheds ride the terrace; the bridge rises over a channel that is
actually below grade. Plinths (already canon) meet the tiers, so houses
read set-in, not placed-on.

**"Foreground and background instantly distinguishable via elevation."**
In the canonical view the eye now steps down into the channel, across
the mid plane, up the plateau and terrace, and out to the ridge — the
isometric depth the brief asked for, verified in the before/after where
the previous frame reads flat by comparison.

## Honest notes

The channel's pit edges are straight cuts, visibly rectangular at the
bends — inside the shape language, but a finer polyline pit would read
more fluvial; recorded as a refinement candidate. Walking residents
step tier heights instantly at boundary lines rather than climbing the
steps; at 2-second behaviour resolution this reads acceptably but is
named honestly. Priority 3 was not started.

## Deliverables

`era-town-3d.html` · `tiers_sheet.png` (flat vs tiered, the western
tiers, the channel at eye level) · this record.
