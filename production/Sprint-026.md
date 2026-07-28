# Sprint 026 — The Roofscape (Priority 6, rendering, solved completely)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — the engine, the fixtures, the residents and the walk
graph are byte-identical. Every change is in the viewer's render layer.**

## The brief (Roy)

> **Priority 6**
>
> * Problem: Rooflines are completely flat and uniform across structures,
>   creating a rigid horizontal horizon line.
> * Why it weakens the scene: Lack of roof pitch variation, dormers, or
>   chimney accents destroys the whimsical diorama silhouette essential for a
>   cozy aesthetic.
> * Instruction for Claude: Add staggered terracotta and slate roof tiles,
>   terracotta chimney pots, and slight pitch variations across all connected
>   building rooftops.

## The diagnosis

I ran the critique from the frames, not from the code, and the frames disagreed
with the obvious reading of the brief. Sprint 020 had already added a pitch
factor and a seeded height step. Pitch variation was not missing. Something
else was drawing the rigid line, and it took the profile capture to see it.

Ranked, worst first:

1. **The eleven link sections were flat slabs at one height.** Every pair of
   terraced houses on Market Street and North Lane is joined by a link, and
   each link's roof was `box(lw+1.0, 0.34, 6.1)` sitting at a constant
   `y = 2.72`. Eleven identical horizontal bars, evenly spaced, at exactly one
   height, threaded through the whole street. *That* was the rigid horizontal
   line. It was not a roof problem at all — it was eleven bars pretending to
   be roofs.
2. **One eaves level and a near-single ridge level.** Height variation came
   from a five-value hash lookup, which lets two neighbours land on the same
   value; when they do, the eye reads two houses as one building.
3. **Every roof was the identical symmetric prism.** No hips, no half-hips, no
   cross-wings — one extruded triangle, scaled.
4. **The chimney was one object repeated.** Same stack, same cap, same two
   pots, same position `w*0.28`, on every house. In silhouette: a comb.
5. **Tiles read as flat colour** beyond about twenty metres. One neutral
   texture, no lap shadow, no ridge tile, no fascia line to catch the light.
6. **Roof colour merged neighbours**, because the colour was hash-chosen per
   plot with no rule against two the same side by side.
7. No fascia, no gutter line, no eaves shadow.
8. One dormer type, one size, one position.
9. The ridge was a single long box.
10. The stand roof is flat — correct for a football stand. Noted, not changed.

So the brief's stated cause was wrong and its stated cure was right. The town
did need staggered terracotta and slate, terracotta pots and pitch variation.
It also needed the eleven bars to die.

## The design

Not a tuned prototype — a replaced one.

**A roof is a shape, not a prism.** `roofMesh(span, run, colour, opts)` builds
the roof as a hand-authored `BufferGeometry` from one parameter set. `hip`
runs from 1 to 0 and gives a plain gable at 1, a half-hipped (jerkinhead) roof
around 0.5, and a full hip at 0 — one formula, three vernaculars. Face winding
is auto-corrected against a desired normal so no face can end up inside out,
and degenerate cases (a gable's collapsed gablet, a hip's collapsed ridge) are
handled rather than avoided.

**The tiles are laid along the slope, not across the box.** The roof UV is
`u = (y / rise) · halfWidth · slopeLength`, which means the course lines are
true horizontals at a constant spacing whatever the pitch, and they carry
across the hip ends of the same roof without a jump.

**Two tile families, hand-drawn.** `panTex` is a pantile: four courses of five,
staggered half a tile on alternate courses, each tile carrying a left-to-right
roll gradient so it has a bright crown and a dark pan, a lap shadow and a
highlight at every course head, and nine weathering blooms. `slaTex` is slate:
seven courses of six, cool and blue-shifted, thin highlight per slate, deeper
course shadow, eleven blooms. Both are shared, not cloned — a material cache
keyed on `colour|slate` means the whole town's roofs use two textures and a
handful of materials.

**The step is ordered, not hashed.** Plots are bucketed into rows by `y`,
sorted by `x`, and given an index. Ridge height, pitch and tile family are
then drawn from that index, not from the plot's hash. A hash can put two
neighbours on the same value; an ordered walk cannot. Ridge steps run through
seven values, pitch through six (33° to 43°), tile family through nine in a
terracotta/deep-terracotta/slate pattern that never repeats side by side.

**A chimney kit, because one stack repeated is a comb.** Stack width, depth,
brick colour, oversailing course, cap, pot count (one to four), pot type
(plain, tall, crenellated) and pot lean are all seeded per stack, and about one
house in three carries a second stack. Pots are terracotta only — four warm
values, no cream.

**The stacks are sized off the roof they pierce.** The height is computed from
the actual roof surface at the stack's own position — including the drop over a
hipped end — so a stack finishes 0.44 to 0.89 m clear of the tiles it comes
through, wherever it stands.

**Ridge tiles, hip rolls, fascia, bargeboards.** The ridge is a run of
half-rounds, not one box. Every hip gets its four rolls, which is what makes a
hip read as a hip at distance. Every eaves gets a fascia and every gable a pair
of bargeboards, in a warm off-white, at a trim scale that shrinks for small
roofs.

**Dormers sit on the slope.** Position, pitch and hip are seeded; the body is
sized from the actual slope height at its own front and back faces, so the
cheeks always clear the tiles and the apex always stays below the main ridge.

**One house in nine turns a gable to the street** — a cross-wing with its own
steeper roof, its own two windows, and the front window it displaces removed.

**The link sections are roofs now, and deliberately subordinate.** Each gets a
pitched, tiled roof with its own seeded pitch, its own tile family, sometimes a
half-hip, and a proper stack. Their pitch band (0.60–0.75) sits below the
houses' (0.64–0.93) on purpose: a link that rises to its neighbours' ridge
stops being a link and becomes a house.

## Verification — what the frames caught, and what it cost

Six cameras, before and after, at the same clock: the roofline against the sky,
Market Street at eye level, the north row from the green, the three-quarter,
the square, and the canon view. Plus four close diagnostics.

**Three defects the first pass shipped and the frames caught:**

1. **The stacks were totem poles.** The height formula added the roof rise a
   second time on top of a 1.30–2.44 m base, so every chimney stood one to two
   and a half metres too tall. In profile the town read as a picket fence of
   red posts. Fixed by deriving the height from the roof surface at the stack's
   own position and adding a small, seeded clearance.
2. **The dormers were buried.** Sized by hand rather than from the slope, the
   body sat entirely inside the roof and only its white trim came through — a
   bone through the tiles. Fixed by computing the dormer's base and top from
   the roof height at its own front and back faces, and dropping its trim scale
   to 0.55 so a dormer is not trimmed like a house.
3. **The chimney brick was all one red.** Three of five palette entries were
   the same dark red, which is what made the totem poles read as a row. Now six
   values across brick, render and grey-brown.

I also chased a cream box on the north row for three captures before a raycast
identified it as the post-office tower — an existing feature, not a defect.
Worth recording: I should have raycast first and squinted second.

Trim was calmed at the same time — fascia 0.24→0.21, bargeboard 0.19→0.17, and
the near-white `PAL.RND` replaced by a warmer `0xf6f0e4`.

**Page errors: none, in every capture pass.**

## Against the brief

| Roy asked for | Delivered |
|---|---|
| staggered terracotta tiles | `panTex` — four courses of five, half-tile stagger, roll gradient, lap shadow, weathering |
| slate tiles | `slaTex` — seven courses of six, cool, per-slate highlight, deeper course shadow |
| terracotta chimney pots | four terracotta values, one to four pots per stack, three pot types, seeded lean |
| slight pitch variations | six pitch values, 33°–43°, ordered by position in the row |
| across all connected rooftops | 23 plots, 11 link sections, farm, barn, privy, stable, clubhouse, tea hut, gatehouse, hill roofs — every legacy `gableRoof` call site upgraded through the wrapper |
| dormers | seeded position, pitch and hip; sized off the slope |
| a whimsical diorama silhouette | gable / half-hip / full hip, ordered ridge steps, cross-wings, ridge tiles, hip rolls, seeded stacks |

## The Continuous Creative Direction review

**Did I protect language or composition?** Language. The roof system is a new
piece of vocabulary — one parameterisation, three vernacular roof forms — and
the composition was destroyed to get it: the eleven link slabs are gone, every
plot's roof block was rewritten, and the old `gableRoof` prism no longer
exists.

**Did I optimise a prototype or replace it?** Replaced. The extruded triangle
was not tuned; it was deleted and a shape builder put in its place. `gableRoof`
survives only as a two-line wrapper so the ten call sites I did not want to
touch this sprint inherit the new roof for free.

**Is the town noticeably more beautiful?** Yes, and it reads in the five-second
test. The before/after sheet is the evidence: the before frames show a flat
band of low roofs at one height with a comb of identical red stacks; the after
frames show a stepped roofscape in two tile families with hips, dormers,
cross-wings and terracotta pots.

**Is it more alive?** Indirectly. Nothing moves that did not move before. But
the roofscape now records that the houses were built at different times by
different hands, which is the kind of evidence-of-life the constitution asks
for (CD-025).

**What did I not do?** The stand roof is still flat, which I believe is
correct. The shop fronts still carry a shop's roof rather than a shop's
parapet. And the gable-end triangle is tiled rather than rendered — it reads as
tile-hanging, which is authentic Sussex vernacular, but it was not a decision,
it was a consequence, and I am flagging it as one.

## Honest notes

- Ordering by row index rather than by hash is the single highest-value change
  in this sprint and the least visible in the code. It is what guarantees a
  step between neighbours instead of merely making one likely.
- The pitch band deliberately does not reach the steep end. A 50° roof would
  read as a chalet, not an English village. 43° is the ceiling.
- Roof geometry is now three to four times the vertex count it was. The town
  still renders at frame rate in a headless capture; if this ever becomes a
  cost, the ridge tiles and hip rolls are the first things to merge.
- The link sections are the part I would look at again first. They are correct
  now, but they are still generated from a pair of plot IDs rather than being
  real objects in the district data.

## Deliverables

- `era-town-3d.html` — the town, rebuilt
- `roofscape_before_after.png` — six cameras, before above after
- `Sprint-026.md` — this record
- `era-sprint026-topup.bundle` — the commit, chained off Sprint 025
