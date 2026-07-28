# Sprint 025 — The River (Priority 5, rendering, solved completely)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — the engine, the fixtures, the residents and the walk
graph are byte-identical. Every change is in the viewer's render layer.**

## The brief (Roy)

> The river channel is a solid, featureless cyan strip with sharp geometric
> borders and no depth or water response. It looks like a drawn blue line on
> paper rather than a natural, inviting river with depth and reflections.
> Render the river with a soft-edged translucent water shader, adding subtle
> depth gradients, soft shoreline foam, and gentle sky reflections.

## The diagnosis

Roy named four symptoms, and they have two different causes. Only one of them
is a shader problem.

The **material** cause is the obvious one: the water was a single flat
`PAL.WATER` fill, opaque, unlit by anything but ambient, identical from bank
to bank and identical at every hour of the year.

The **geometric** cause is the one that actually did the damage. Since
Sprint 015 the river's arm had been a chain of nine straight `box()` strips of
constant width laid end to end. A river built from rectangles *cannot* have a
soft edge, because its edge is a straight line by construction — and the
channel it ran in was a set of four axis-aligned holes in the ground with
1.25 m brown skirt walls around them. No amount of shader work fixes a
rectangle. The strip was cyan because it was flat, but it read as *drawn*
because it was straight.

So the sprint replaced the prototype rather than tuning it.

## The design

**The arm is a curve.** The nine waypoints are now the control points of a
`CatmullRomCurve3`, and every part of the channel is generated as a ribbon
swept along it — 280 samples, explicit up-normals, hand-built index buffer.
The river bends because the geometry bends.

**The channel breathes.** Half-width is a function of arc position, not a
constant: pinched through the straights, broad on the bends. There is no
longer any length of river with two parallel banks.

**Seven layers in section**, so the water sits in something carved rather than
on something drawn:

1. the channel floor, so nothing under the water is void;
2. the silt bed the water is read *through*;
3. the cut bank — wet earth climbing from the bed lip to the ledge;
4. the grass ledge halfway down the cut;
5. the shoulder, climbing out and dissolving into the field;
6. the water;
7. the foam and the sky lying on it.

**The soft edge is geometric, not painted.** The shoulder ribbon carries RGBA
vertex colours — opaque at the inner edge, alpha zero at the outer — so the
bank *fades* into the meadow instead of ending. The water's own cross-channel
texture reaches alpha zero at both banks, which means the water mesh's
geometric edge is never visible: what you see as the waterline is a gradient,
not a polygon boundary.

**Depth is a gradient across the channel**, painted into the water canvas:
near-black teal at the centre, shoaling through slate to a pale green-grey,
to nothing at the banks. The silt bed reads through the shallows and does not
read through the middle, which is what "deep" looks like.

**Current** is 66 seeded bézier streamlines composited `source-atop` into the
water canvas, half pale and half dark, and three texture layers drifting
downstream at three different rates every frame — water, foam, and reflection
each move at their own speed, so the surface never reads as one sliding image.

**Foam** is a separate broken-lace canvas masked to two narrow bands with a
`destination-out` gradient, laid just inside each bank. It is lace, not a line.

**The sky** is an additive sheet over the centre of the channel plus a Lambert
emissive on the water itself, and both take their colour from the hour: pale
blue by day, warm amber through golden hour, grey under rain, and a cold
moonlit blue at night. This is the "water response" the brief asked for, and
it is driven from the same clock the rest of the town is lit by.

**One structural fix taken on the way.** The bridge's arch opening was 2.3 m
wide over a 5.9 m river — the water visibly ran through solid stone. A
semicircle cannot widen without its crown breaking the deck, so the arch is
now segmental: an ellipse spanning ~6.3 m with a 1.22 m rise. The bridge
finally crosses the water instead of standing in it.

## Verification found three defects. All three are fixed.

Working from the capture frames rather than from the code:

- **The silt bed was invisible.** It was laid at −1.22, below the −1.15 deep
  ground plane that has been there since Phase 12, so the bed the whole design
  reads the water through was buried under an olive plane. Raised to −1.10.
- **The old trench walls were still standing.** The four rectangular pit
  skirts survived from the straight-strip river and now stuck up as brown
  walls beside a river that curves away from them. Deleted; the channel's own
  cut bank does that work now. The shoulder ribbon grows until it covers the
  rectangular ground-hole, whatever the curve is doing, so the old rectangle
  can never show — and the shoulder is drawn with the *field's* grass material,
  not a bank green, because an edge between two different greens draws itself.
- **The hole ran further south than the water did**, leaving a bare rectangle
  of channel floor lying in the meadow, plainly visible from the canonical
  aerial. Hole trimmed to the waterline.

An early tone pass was also needed: the first build rendered milky white,
because emissive, additive reflection and foam all stacked under ACES over a
gradient whose "deep" stop was already light. Every stop was deepened and the
three additive terms cut roughly in half.

No page errors at any point.

## Success criteria, answered

**"Soft-edged."** There is no hard border anywhere in the crossing: water
alpha reaches zero before the water mesh ends, the shoulder's vertex alpha
reaches zero before the shoulder ends, and both the ledge and the cut bank are
swept ribbons that follow the curve. The `bank` and `bend` frames are the
proof — the before has a straight brown rectangle crossing the grass, the
after has a bank.

**"Translucent, with subtle depth gradients."** The silt bed is visible
through the shallows at both banks and invisible in the middle, in the same
frame, from the same camera. That is the definition of depth being read rather
than stated.

**"Soft shoreline foam."** Broken lace inside each bank, brightening from 0.12
to 0.38 with the daylight and drifting downstream 1.4× faster than the water.

**"Gentle sky reflections."** `river_takes_the_hour.png` — the same camera at
dawn, noon, golden hour, night and in rain. The water is pale blue, then warm,
then grey, then a cold blue sheen against the lamplight. Gentle is the
operative word: the reflection never exceeds 0.20 opacity and is never a
mirror.

## The five-question review

**1. The five biggest weaknesses now.** The residents, still (sixth sprint
running — the town is beautiful and its people are tokens). The river reads
dark from the canonical aerial, where the eye wants more sky in it. There is
no sound of water and no wet-stone darkening where the bridge meets it. The
banks have no reeds, no shingle, no waterline stain — the section is right and
the botany is missing. And the water still does not *move* anything: no
floating leaf, no duck, no reflection of the ATHLETIC board.

**2. Bold decisions.** The river was not improved; it was destroyed and
rebuilt from a curve. The trench walls that have defined the channel since
Phase 12 were deleted outright. The bridge arch — canon geometry, untouched
for ten sprints — was widened, because it was wrong.

**3. Layout changes.** None. The river's centreline is exactly the nine
Sprint 015 waypoints; the bridge is where canon fixed it. The channel is
wider and softer, and the ground-hole's south end moved 7 m north to meet the
water.

**4. Language kept identical.** No new colour, kit, tree or figure. The water
palette is the Museum's cool end; the banks are the ground material of
Sprint 021; the foam and sky are the existing light model. `mkTex`/`matT`
from Sprint 024 do all the painting.

**5. Substantially closer to the target?** Yes, and the five-second test is
not close. Before: a cyan rectangle in a brown trench. After: a river with a
bed, banks, current and weather, curving out of frame under a bridge that
actually spans it.

## Honest notes

The channel is still carved out of an axis-aligned set of holes in the
terrain; the shoulder now covers them reliably, but the correct fix is a
ground mesh that follows the curve, and that is a terrain-layer sprint, not a
render-layer one. From the canonical aerial the river reads darker than it
should at early hours. The bank trees were not re-seeded along the new curve —
they still sit on the Sprint 015 offsets, which is close but not deliberate.

And the standing one, unchanged and now six sprints old: **Ground Row, the
north row, the farm and the stable are viewer-layer fabric — no households
live in them.** One population-data ruling from Roy would people all of them.

## Deliverables

`era-town-3d.html` · `river_before_after.png` (six cameras, before above
after) · `river_takes_the_hour.png` (dawn, noon, golden, night, rain) ·
this record.
