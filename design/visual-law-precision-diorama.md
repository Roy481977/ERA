# The Visual Law — Precision Diorama

**Status: governing. Supersedes `design/visual-law-clay-diorama.md` in every
place the two disagree.** Established 2026-07-25 from five reference images
supplied by Roy, with the instruction: *"the last ones that are more simple I
actually love most — green, elegant, place for the different structures and town
center. In all I attached, see the finesse. It's that level that is a must. See
the google building — that's how I would like to construct our town."*

The five references, and what each one contributes:

1. **Low-poly faceted diorama** (log cabin, cut rock cliff, waterfall, chamfered
   plate edge). Contributes: the clean cut edge of the plate, and permission for
   flat faceted masses where they are *deliberate*.
2. **Clay/felt tilt-shift city** (ferris wheel, orange and cream buildings, blue
   river, tiny cars). Contributes: colour confidence, and the fact that traffic
   is what makes a model city feel alive.
3. **Illustrated isometric city** (dense street trees, multi-lane roads with
   markings, central park). Contributes: the rhythm of street trees, and roads
   read as *circulation* rather than as grey stripes.
4. **Tilt-shift suburb.** Contributes the single most important idea in this
   document: **every house sits on its own crisply defined plot** — mown lawn,
   path, drive, boundary. Nothing floats on undifferentiated ground.
5. **Physical miniature of a Google office on a turned wooden base.**
   Contributes the *construction method*: plinth, repeated bay module, crisp cap,
   then dressed with props. And the standard of finish — a razor-sharp mullion
   grid, a clean white parapet, a base that is itself a designed object.

## Law 1 — Precision, not jitter

**This reverses Law 1 of the clay-diorama document, which required that nothing
be sharp.** That law was written from a hand-thrown-pottery reference. Every one
of Roy's five references is the opposite: sharp kerbs, clean roof edges, a mown
lawn with a cut edge, a mullion grid you could cut yourself on.

At plate scale, jitter does not read as *handmade*. It reads as *sloppy*. A 2 cm
wobble on a 4 m wall is invisible as craft and visible as noise. The thumb-press
displacement is retired. Bevels stay — a 3–5 cm radius that catches a highlight
and proves the object has mass — but they are even, and the edges they soften are
straight.

The test is inverted from the old one: **if you can find a wobble in a
silhouette that should be straight, it is wrong.**

Randomness survives where it is *structural* rather than *surface*: house widths,
heights, roof colours, plot sizes, tree species and spacing, which windows have
shutters. Vary the parts, not the edges.

## Law 2 — The ground is the star, and it is green

Saturated, fresh, clean-cut green. Not the yellow-olive of the earlier passes.
Four or five real greens in play, from a bright mown lawn through to a deep
conifer green, and they are allowed to be *saturated* — reference 4's lawns are
vivid and that is why the frame sings.

The ground surface itself is flat and clean. No vertex noise on a mown lawn.

## Law 3 — Clean ground between things is a feature

**This reverses Law 4 of the clay-diorama document, which required that no square
metre of ground be bare.** That law produced thousands of tufts, shrubs, pebbles
and flowers, and it was the single biggest thing destroying the read. Removing
them raised quality *and* cut the object count by a third.

Empty green between structures is not a gap to be filled. It is what lets the
structures be legible. Density belongs in a few designed places — a bed, a
hedgerow, a planted corner — and nowhere else.

## Law 4 — Everything sits on a defined plot

No object stands on undifferentiated ground. A house gets a cut panel of mown
lawn, a paved apron tight to its walls, a clipped hedge marking the boundary, and
usually one specimen tree. A tree in a street gets a square earth pit. A stadium
gets a walled perimeter and a marked car park. A field gets hedgerows on its
boundaries.

The plot is what says *someone owns this and looks after it* — which is the
entire emotional content of reference 4.

## Law 5 — The road is engineering

A road flush with the grass reads as a painted stripe. A road held by a raised
stone kerb reads as engineering, and that difference is worth more than any
amount of surface detail.

Every street therefore carries: a carriageway; a raised kerb standing proud of
the pavement; a pale paved footway behind it; a continuous painted edge line;
dashed centre markings, dead straight and evenly spaced; crossings; and **parked
cars at the kerb**. Cars are not decoration — references 2, 3 and 5 all read as
circulation before they read as architecture. Traffic is the fastest way to make
a model town feel inhabited.

Technical note, learned the hard way: side streets that join a main street must
be **staggered in height**. Coplanar carriageways make every shadow ray leaving
one surface hit the other at zero distance, and the junction renders pure black.

## Law 6 — Build the way the Google model is built

Plinth → repeated bay module → crisp cap → dressed with props. Modular and
precise first, decorated second. This is the construction order for every
building in ERA, and it is why the punched-wall panel (a slab of real thickness
with openings cut clean through, giving real reveals, jambs and shadow) is the
correct primitive rather than a plane with a window decal on it.

Decoration applied to an imprecise mass never recovers. Precision applied to a
plain mass always reads.

## Law 7 — Trees are clean solid masses, deliberately placed

Real greens, solid readable volumes, two species families in play (broadleaf and
conifer). Placement is designed, not scattered: rows along streets at an even
rhythm, one specimen per garden, clusters as mass planting, a belt holding the
rim of the plate.

One tree is one object. A tree assembled from fifty scattered lobes costs fifty
times as much and reads worse.

## Law 8 — Open ground is organised, not empty and not busy

The land beyond the town is neither bare lawn nor random scatter. It is
**parcelled** — a grid of fields on a consistent skew angle, each with its own
green, bounded by hedgerows, with the occasional standard tree left in the hedge.
Elegance comes from the green being *organised*, not from it being crowded.

Measured constraint, worth keeping: the built town claims roughly 60 % of the
ground in the annulus r 17–31 m (streets, lanes, the square and the stadium).
A parcel tested all-or-nothing against `built()` therefore has to be small to
survive — 4.4 × 5.2 m in the near ring, 8.6 × 10.4 m for fields beyond r 24.5.
Oversized cells do not get rejected gracefully; they vanish entirely.

## Law 9 — The base and the backdrop are designed objects

The plate edge is a clean cut with a band of exposed earth beneath the turf — a
designed section, not a rubble heap. Reference 5's turned wooden base is the
ambition.

The backdrop is a deliberate gradient, dark enough that the model pops against
it, and it must be wired to the camera ray only so that darkening it does not
darken the lighting of the scene.

## Law 10 — Light is soft and open-shadowed

Carried over from the previous law and still correct: a large soft key, generous
fill, deep contact occlusion doing the shape-reading rather than shadow contrast.
The amendment is that shadows must stay *open* — a street in the shade of tall
houses should read mid-grey, not black. Ambient sits high enough that no surface
in the town falls out of the image.

## Checklist for any new asset

1. Straight things are straight. No surface wobble.
2. It sits on a defined plot, apron or pit — never on raw ground.
3. Built as plinth → module → cap → props, in that order.
4. Its colours are inside the palette, and its greens are real greens.
5. It does not require scatter around it to look finished.
6. Variation is in the parts and the arrangement, not in the edges.
7. It reads at plate distance, not just in close-up.

## What this law replaced, and why

The clay-diorama law was written from a single Mediterranean clay-village
reference and was internally consistent. It failed against Roy's five references
on two specific points, both of which had to be reversed rather than tuned:
requiring that nothing be sharp, and requiring that no ground be bare. Together
those two rules guaranteed a frame that was simultaneously soft-edged and
cluttered — precisely the "messy" quality Roy kept naming.

The Law 2 (moss in the seams), Law 5 (narrow palette) and Law 6 (soft bounced
light) provisions of the old document remain broadly sound and are folded in
above, with moss dosed far lower and the palette permitted to be more saturated.
