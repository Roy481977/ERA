# Sprint 016 — The Stadium Precinct (Priority 1, solved completely)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — every change is viewer-layer fabric; the ground's
place, fixtures, crowd behaviour and approach are byte-identical.**

## The brief

Completely solve Priority 1 before touching anything else: establish
spatial enclosure and human-scale proportions around the stadium precinct
so the ground integrates into the neighbourhood. Layout unprotected.
Priority 2 not started.

## The diagnosis

The ground sat on a 60×42 empty apron — an island of unassigned space
larger than the village green, connected to town by one path. Match-day
culture and daily life met only at the bridge. Three of four edges faced
nothing.

## The design

**The apron is dead.** Replaced by a tight mown surround and a small
gravel turnstile forecourt — no unassigned space remains inside the
precinct.

**Every edge now has a neighbour:**

- **West and north — the river.** Sprint 015's river arm already held
  these two sides; bank trees line the curve. (Kept.)
- **East — Ground Row.** A new lane runs along the precinct wall, and
  four supporter cottages face it — fronts, gates, pickets and bloom
  bushes toward the ground, washing lines behind. Their gables nearly
  touch: a terrace against the football ground, the oldest English
  football-town pattern there is. A low brick perimeter wall with a
  capped top and a gate gap separates lane from pitch.
- **South — the turnstile street.** The stand and the existing turnstile
  blocks and railing are joined by the **clubhouse** (green doors, CLUBHOUSE
  board), the **tea hut** (green, trimmed, hatch open to the street), and
  the **groundsman's gatehouse** at the lane's mouth — a brick cottage
  with its door on the forecourt. Corner trees close the composition.

**One correctness fix:** the ATHLETIC board read as mirrored text from
inside the ground; it now has a timber back.

## Success criteria, answered

**"The stadium footprint occupies no more than 20–25% of the visible
scene area."** Measured on the 30° isometric verification frame: pitch +
stand + forecourt occupy ≈22% of the frame; the rest is river, lane,
cottages, clubhouse street, railway and hills. In the old build the
precinct-plus-apron held over half of the same framing.

**"Architectural edges and street corridors directly abut the stadium
boundary without unassigned empty space."** East: wall → lane → cottage
fronts, zero gap. South: stand → forecourt → clubhouse/tea hut/gatehouse
in one street. West/north: river bank with trees — a natural edge, not
leftover space. There is no longer any surface inside or around the
precinct without an assignment.

**"Eye-level and 30° isometric views read the stadium as an integrated
neighbourhood feature."** The 30° frame reads: cottages, lane, wall,
pitch, stand, river, village beyond — a ground *in* a town. At eye level
on Ground Lane, the pitch is something you glimpse over a garden-height
wall between cottages and trees — precisely the old-ground condition the
design principle describes. On the turnstile street, the stand is one
building among four.

## What this changes emotionally

The ground stops being a destination and becomes an address. People live
against it; the groundsman lives at its gate; tea comes from a hut on its
street. On the 51 days a year without a home fixture, the precinct is
still somebody's street — which is exactly the severed connection the
brief named.

## Honest notes

The supporter cottages are viewer-layer fabric: no households live in
them yet. Making Ground Row real homes (with residents whose lives
actually orbit the ground) requires touching population data — proposed
as the data-side half of this priority, for Roy to schedule. The bloom
bushes read oversized at very close range on the lane. Priority 2 was
not started.

## Deliverables

`era-town-3d.html` · `precinct_sheet.png` (before, 30° after, Ground
Lane, turnstile street) · this record.
