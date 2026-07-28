# Sprint 027 — The Town Gets Storeys (Priority 6, second pass)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — the engine, the fixtures, the residents and the walk
graph are byte-identical. Every change is in the viewer's render layer.**

## Why there is a second pass

Roy sent Priority 6 again, verbatim, immediately after Sprint 026 shipped. I am
treating a re-issued brief as a rejection, not a repeat. Sprint 026 built a real
roof system — pitch bands, two tile families, hips, dormers, seeded chimney
kits — and the rigid horizontal line survived it. That means Sprint 026's
diagnosis was wrong, and a correct fix built on a wrong diagnosis is still a
wrong fix.

## The diagnosis Sprint 026 missed

I re-ran the critique from the shipped frames rather than from the code, and the
frames say something the brief's wording hides.

**The line the eye reads is not the ridge. It is the eaves.**

Sprint 026 stepped the ridges by up to a metre and gave every roof its own
pitch. But the wall underneath never changed: `ht = (shop?3.4:2.9) + htVar`
with `htVar` between 0 and 1.13. Twenty-three buildings, all 2.9 to 4.0 m to the
gutter, standing on flat ground. A one-metre spread over a four-metre building
is noise. The gutter line was effectively one level across the whole town, and
every fascia board — bright `0xf6f0e4`, catching the afternoon sun, running the
full length of every eaves — joined its neighbours into a single white stripe
from one side of the frame to the other.

No roof can fix that. Only storeys can.

Ranked, worst first, as read off `C26_profile` and `C26_northrow`:

1. **Every building is the same height.** The eaves band is one level.
2. **The white fascia draws the line for us** — 0.21 m deep, full length, at
   nearly one height, on twenty-three buildings.
3. **The roof is too small a share of the building.** A 1.7–2.5 m rise against a
   2.9–4.0 m wall. A cottage silhouette wants the roof to out-mass the wall.
4. **One footprint, one building line.** Widths 5.6/6.4, depth 4.6, every front
   face coplanar.
5. **Only about one house in seven turns a gable to the street.**
6. **The ridge band is about a metre wide across twenty-three plots**, and
   nothing in the residential rows is tall.
7. Dormers barely register in profile.
8. Terracotta dominates; slate reads as an accent rather than a second family.

## The design

Not a tuned prototype. The massing rule was deleted and replaced.

**Five storey classes.** `RSTEP` and `htVar` are gone. Every plot now draws a
class from its position in the row, and the class carries eaves height, roof
pitch and eaves overhang together, because those three things co-vary in real
buildings:

| class | eaves | pitch | overhang | what it is |
|---|---|---|---|---|
| 0 | 2.60 | 1.06 | 0.58 | single-storey cottage — low eaves, huge roof |
| 1 | 3.35 | 0.92 | 0.50 | one-and-a-half storey — it lives inside its roof |
| 2 | 4.75 | 0.78 | 0.40 | two storey |
| 3 | 5.60 | 0.72 | 0.34 | two-and-a-half |
| 4 | 6.60 | 0.66 | 0.30 | three-storey townhouse — rare, an accent |

The eaves now spread across four metres instead of one, and the ridge across
roughly 5.6 to 8.4 m. The class sequence is a twelve-value walk indexed by
position in the row, so no two neighbours can land on the same class — the
Sprint 026 lesson about ordering over hashing, applied to the thing that
actually mattered.

**The roof out-masses the wall on the small houses.** Pitch is inversely tied to
class, so a cottage gets a 1.06 pitch and a 0.58 m overhang while a townhouse
gets 0.66 and 0.30. The cottage silhouette is now mostly roof, which is what
makes a village read as cosy rather than as a row of blocks.

**The building line breaks.** Depth varies by ±0.5 m per plot, so the fronts are
no longer coplanar and the shadows down the street step in and out.

**Gable-to-street rises to about one house in three**, from a nine-value ordered
pattern rather than a hash.

**The high street stands taller.** Shops draw from their own class sequence
(2, 3, 2, 4, 3, 2, 3) — living quarters above the trade, which is both correct
and the reason the square now has a skyline.

**Everything hung on the wall follows the wall up.** Chimney stacks scale with
class. Link sections take their height from the shorter of the two houses they
join, so they stay subordinate now that the houses no longer match. The matchday
flag clamps below whatever eaves it hangs under.

**The fascia stops shouting** — `0xf6f0e4` to `0xe9dcc6`. A warm board, not a
white stripe.

## What the frames caught — two further passes

**Stage two: a house has four elevations, and stage one gave storeys to one of
them.** The verification frames showed the cost immediately. On a 2.9 m cottage
a blank back wall is a wall; on a 6.6 m townhouse it is a cliff. A raycast into
the market-square frame identified the largest surface in the shot as exactly
that — one 6.6 m square of unbroken render, doing nothing. (Recording that I
raycast first and squinted second this time, which was Sprint 026's honest note.)

So `winFace` was added — the same window unit, hung on any of the four walls —
and the back and the flanks were given work to do. The back gets a back door, a
scullery window and a deliberately asymmetric tier of upper windows, because
symmetry is what makes a wall read as a front. It also gets a downpipe and
hopper: a vertical line down a flat wall, and evidence that it rains here.

The flanks get a **chimney breast** — a shallow pilaster running ground to
eaves. This is the right answer rather than more windows, because an English
gable end is broken by its breast, and because what actually kills a blank plane
is a vertical shadow. The gable triangle gets an apex window wherever the roof is
gabled enough to have one.

**Stage three: a tall house is public on both sides.** Stage two put the breast
on one seeded flank, and on the class-4 townhouse it landed on the side the
square cannot see. Corrected: class 3 and above get both flanks treated, a full
tier of windows either side of the breast on every storey, and a ground-floor
pair. Three tiers of window and two shadow lines is what turns a 6.6 m plane
back into a building.

**Page errors: none, in all three capture passes.**

## Against the brief

| Roy asked for | Delivered in 026 | Added in 027 |
|---|---|---|
| slight pitch variations | six values, 33°–43° | pitch now tied to storey class — 0.66 to 1.06, a genuinely different roof shape per house type |
| staggered terracotta and slate | two hand-drawn tile families | unchanged, but now seen against a stepped skyline instead of a flat one |
| terracotta chimney pots | seeded kit, 1–4 pots | stacks scale with the house they stand on |
| dormers | seeded, sized off the slope | now fired by storey class — the one-and-a-half storey house always has one |
| no rigid horizontal line | ridges stepped; the line survived | **the eaves themselves now step across four metres** |
| a whimsical diorama silhouette | roof forms | actual variety of building size — cottage next to townhouse |

## The Continuous Creative Direction review

**Did I protect language or composition?** Language, and this time at some cost.
The composition Sprint 026 shipped was coherent — one town, one scale, one
rhythm. It was destroyed. The town now has cottages beside three-storey
townhouses, which is less tidy and much more like a place.

**Did I optimise a prototype or replace it?** Replaced. `RSTEP`, `htVar` and
`pf` were deleted outright, not tuned. The height of a building is no longer a
seeded wobble on a constant; it is a property of what kind of building it is.

**Is the town noticeably more beautiful?** Yes, and it passes the five-second
test in the profile and square frames. Before: one band of roofs at one height.
After: a skyline that steps from 2.6 m cottages to a 6.6 m townhouse, with the
roof dominating the small houses and the wall dominating the tall ones.

**Is it more alive?** Yes, and by more than the last sprint. Back doors,
scullery windows, downpipes and blocked-up windows are all evidence that people
live on the other side of these walls (CD-025). Nothing moves that did not move
before, but the buildings now record what they are for.

**What did I not do?** The population data still gives households to only some
of the rows — raised for the eighth sprint running and still awaiting a ruling.
The rear elevations are generated, not authored; a real back is untidier than a
seeded pattern. And the class sequence is fixed rather than derived from the
district data, which means the town's social geography is decorative rather than
simulated — the townhouse is tall because the sequence says so, not because
anyone rich lives in it. That is the next real question.

## Honest notes

- Sprint 026 was not wasted — the roof system it built is what makes the storey
  classes legible. But it answered the brief's stated cause instead of the one
  in the frames, and it cost a full sprint. The lesson is the one already in the
  Continuous Creative Direction brief: critique the frames, not the words.
- Three capture passes for one sprint is the right number, not a failure. Each
  pass caught a defect the previous one created. The cliff wall in stage one and
  the wrong-side breast in stage two were both invisible in code and obvious in
  a frame.
- Geometry cost is up again — four elevations of windows across twenty-three
  plots. Still at frame rate headless. Window frames and sills are the first
  thing to instance if it ever bites.

## Deliverables

- `era-town-3d.html` — the town, rebuilt
- `roofscape_v2_before_after.png` — six cameras, Sprint 026 above Sprint 027
- `Sprint-027.md` — this record
- `era-sprint027-topup.bundle` — the commit, chained off Sprint 026 (`f2cf9c3`)
