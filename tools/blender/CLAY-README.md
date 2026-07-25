# The clay plate builder

`clay.py` builds the whole ERA town as a single Blender scene and renders it with
Cycles, headless, using `bpy` installed as a pip module. There is no .blend file
and no manual modelling step — the town is a program, and every pass is a diff.

    python3 clay.py out.png [width] [height] [samples]

At 1100 × 740 / 44 samples a full plate takes about 1m50s on the 2-core container
at roughly 7,300 objects.

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
