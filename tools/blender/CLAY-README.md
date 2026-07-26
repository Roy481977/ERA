# The clay plate builder

`clay.py` builds the whole ERA town as a single Blender scene and renders it with
Cycles, headless, using `bpy` installed as a pip module. There is no .blend file
and no manual modelling step — the town is a program, and every pass is a diff.

    python3 clay.py out.png [width] [height] [samples]

At 1100 × 740 / 44 samples a full plate takes about 1m45s on the 2-core container
at roughly 3,300 objects.

A top-down plan check costs 20 seconds and is the fastest way to debug anything
that is wrong at layout level rather than at object level:

    CAM_EL=88 CAM_AZ=90 LENS=54 CAM_D=210 python3 clay.py /tmp/top.png 700 700 10

When a plan render is inconclusive, copy `clay.py` to `/tmp/dbg.py`, string-replace
one suspect material's RGB with magenta, and render that. Two 20-second frames
found the buried-lane bug after two full 1m45s frames had failed to explain it.

    BUILD_ONLY=1 python3 clay.py /tmp/x.png

builds the scene, prints the object count and exits before rendering. **Always run
this after an edit before spending two minutes on a frame.**

`kit.py` is the element bench. It splices `clay.py`'s header — materials, mesh
pools, the roof and façade kits — at the `# --- the house` marker and renders
three houses close up, so iterating on a single element costs about a minute
instead of eight. Nothing is defined twice: every element lives in `clay.py`.

    python3 kit.py out.png [width] [height] [samples]

## Rules the code obeys

Governed by `design/visual-law-precision-diorama.md`. The ones that bite:

**Never leave two surfaces coplanar.** Two slabs at exactly the same z make every
shadow ray leaving one hit the other at zero distance, and the result renders pure
black. Every stacked slab gets a deterministic z-stagger — streets `_si * 0.009`,
fields `((_i+6)*11 + (_j+5)) % 7 * 0.004`, parcels `_gdz`, the square's concentric
discs 10 mm apart.

**Never guess a rotation order.** Author geometry in the target local frame and
apply only `(0, 0, angle)`.

**Precision is cheaper than jitter.** Replacing the church's ~2,600 individually
jittered roof tiles with one hand-wound bmesh prism, and the market square's ~700
cobble dots plus 220 moss scatters with five concentric discs, took the scene from
10,780 objects to ~7,300 *and* made it look better.

**`ribbon()` is a fill, not a stroke.** It fills the entire span between its two
signed offsets. A kerb is therefore two narrow edge ribbons, `(-(HW+0.24), -HW)`
and `(HW, HW+0.24)` — never one wide ribbon at a higher z, which lays a solid
slab over the whole carriageway and buries it.

**Offsetting a polyline round a sharp corner folds it over itself.** A 50° kink
offset by 3.5 m self-intersects for 1.6 m either side of the corner, and the
folded quads render as black bowties. Every lane goes through `_chaikin()` corner
cutting before it is ribboned, so no segment turns more than a few degrees.

**Public ground outranks private ground, and the z-stack says so.** A house lays
a lawn panel topping out at 0.10 and a paved apron at 0.16. A lane laid at 0.07
disappears under them even though the geometry is perfect. The lane stack now
runs verge 0.170 → surface 0.218 → kerb 0.258, above anything a plot can lay.

**Two independently-laid ranks of houses will walk into each other.** `_hfree()`
keeps one shared occupancy list and tests separating axes between the two
footprint rectangles. A circle claim is wrong here: it forbids terraces, which
touch on purpose. Pad the depth (1.3 m) and not the width (0.02 m).

**Texture ribbons from Object coordinates, never Generated.** `ribbon()` leaves
its object at the world origin, so Object coordinates *are* world coordinates and
a road, footway or lane tiles continuously across the whole plate. Generated
coordinates normalise to each object's own bounding box, so every segment would
restart its pattern at a different scale.

**The carriageway has to outweigh the footway.** Widening the pavement to 2.75 m
against a 3.1 m half-road made the town read as a paved yard with a stripe down
it. At half-road 3.85 m and footway 2.35 m the street reads as a street. The
same rule sets the hierarchy for everything else on the ground: high street,
then square, then lane. A back lane in the same pale stone as the footway
competes with the high street; in compacted sett it sits underneath it.

**Terracotta is the town's colour.** Every reference with a pitched roof is
terracotta and nothing else. Slate survives only on civic buildings and a
handful of cottages, and it has to be a warm neutral grey — a blue-grey slate
fights the terracotta and pulls the whole plate cold.

**Tiles read in colour before they read in relief.** The pantile geometry rolls
and steps correctly, but at plate distance what the eye picks up is the course
line. `pantile()` puts a two-tone clay and a dark course joint in the material
via a Brick node on Object coordinates, and that is what made the roofs read.
Note that the Brick node's `Offset`, `Offset Frequency`, `Squash` and
`Squash Frequency` are node *properties* (`br.offset`), not socket inputs.

**Cartoonish is three numbers, not a redesign.** "Rounder and more playful" is
`SAT` (how far every colour sits off grey, applied inside `srgb()` so it is
luminance-preserving and whites stay white), `CARTOON` (a multiplier on every
`lump_box` bevel, clamped to `0.40 × min(w, d, h)` so thin members survive), and
the roof pitch range in `roof_v2`. Turning them at one point keeps the whole
plate coherent; chasing the same look object by object does not. Current values
are `SAT = 1.18`, `CARTOON = 1.95`, pitch `rr(0.56, 0.70)`.

**A steeper roof shows more roof, so every non-terracotta one counts double.**
Raising the pitch made the surviving grey slates read as a cold rash across a
newly saturated town. Slate probability dropped to 0.03 on frontage houses and
0.05 on lane cottages, and the palette moved from neutral to warm brown-grey.
Any future change to pitch has to be followed by a look at the slate count.

**Ground is claimed before it is parcelled.** `built()` — paved or inside the
stadium — covers about 60 % of the annulus r 17–31. Parcels and fields are tested
all-or-nothing against it, so an oversized cell does not shrink, it disappears.

## Construction vocabulary

- `lump_box(w, d, h, bev, seg, wobble)` — a heavy bevel on a low-segment box is
  how hedges, clock faces and any rounded mass are made cheaply.
- `cube_into(bm, ...)` + `_mi(bm, n0, idx)` — one mesh, many parts, several
  material slots. Used for the car, the bench and the market stall, all instanced.
- `linked(name, mesh, loc, rot, sc)` — instance a shared mesh. `obj(...)` — a new
  object, optionally appending one material.
- `disc(nm, r, h, mat, loc, seg, rot)` — a laid floor.
- `bmesh.ops.create_cone(segments=4, radius2≈0)` with `Matrix.Rotation(π/4)` — a
  true four-sided pyramid. Circumradius is half-width × √2.
- Hand-wound bmesh prisms with `recalc_face_normals` and flat shading — gabled
  roofs.

## Editing safely

Edits go through a Python heredoc using an asserting `sub(a, b, n=1)` and a single
`open(p, 'w').write(s)` at the end, so a failed match writes nothing. For whole
functions, splice by marker index rather than reproducing a long body.
