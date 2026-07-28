# Sprint 028 — Building Families, Mass and Enclosure (Sprint 027 rejection)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — the engine, the fixtures, the residents, the walk graph
and the historian are byte-identical. Every change is in the viewer's render
layer and in settlement composition, exactly as the brief scoped it.**

## The ranked critique of the Sprint 027 frames

Read off `F27_profile`, `F27_square`, `F27_northrow` and `F27_iso30`, worst
first, before any code was opened. Roy's rejection and this list agree, which is
the useful part: the fault was visible in the images and I shipped anyway.

1. **Every building is the same object.** Same width band, same plinth, same
   white window unit, same canopy, same wall-colour family. Only the height
   varied. Sprint 027 replaced uniform height with varied height and left
   uniform *architecture* untouched — which is why the skyline changed and the
   town did not.
2. **P15 is sheer.** Windows float on a blank field; no ground-floor
   differentiation, no cornice, no plinth reading at distance. It is the biggest
   object in the square frame and the weakest. Roy named this one himself.
3. **Roofs read as flat orange fields beyond about fifteen metres.** Slate reads
   as a blue-grey field. No ageing, no variation between roofs, no course
   definition at any real camera distance.
4. **Grass and road dominate.** The profile frame is roughly forty per cent
   mown grass. `iso30` shows large meaningless lawns between houses that no one
   owns, uses or fences.
5. **The Sprint 027 rear windows read as scattered specks on big blank walls.**
   Worse than blank, and Roy said so in the same words.
6. **No hierarchy.** The oak is the only unique object in the town.

## The core correction

> *"A taller building must not be the same cottage stretched vertically."*

The generic house generator is gone. `RFAM`, `SCL`, `SC`, `SCS` and `FGB` were
deleted, not tuned. In their place is an authored kit of seven builders
dispatched off an explicit role map, one entry per plot — twenty-three plots,
each assigned by hand from the district geography rather than by a positional
sequence.

| family | plots | what it is |
|---|---|---|
| low cottage | P11, P12, P08, P10, G1–G4 | one to one-and-a-half storeys; the roof out-masses the wall; low irregular eaves; small deep-set windows |
| two-storey village house | P09, P01, P03 | balanced wall-to-roof; aligned floor levels; stronger doorway; varied bay spacing |
| terraced worker housing | P14, P13, N3 | attached runs; shared eaves; party-wall chimneys; no front setback; a continuous street edge |
| high-street shop-house | P02, P05, P04, N1, N2, P07 | shopfront and fascia at ground level, residence above; large ground-floor glazing; short attached runs |
| corner anchor | W1 | wider footprint; turns the corner architecturally; rises above its neighbours on purpose |
| civic | P06 | unique silhouette, distinct material and proportion, placed where it terminates a view |
| inn | P15 | the replacement for the tall pale block — see below |

Height is no longer a positional sequence. It is a property of what kind of
building something is, and the families were assigned by district role:
cottages at the peripheral residential edges, terraces and two-storey houses
along the continuous streets, shop-houses grouped on the high street, and the
only tall things in the town at the corner, the square and the view
terminations. The hierarchy Roy drew — landscape edge → cottages → ordinary
two-storey housing → denser terraces and shops → one or two deliberate civic
anchors — is now the actual authored order of the plot list, not an emergent
accident.

## The specific required correction: the tall pale block

P15 is now an inn. Not a taller house: a different building. Wider footprint,
a fully differentiated ground floor with its own material and fenestration, a
clear floor division band, a deliberate entrance with a hood, bay windows to the
square, a hanging sign, a roof proportioned to the larger mass, and composed
flank elevations because the square sees three of its sides at once. In
`L28_square` it is the thing the eye lands on and the thing that tells you where
you are — which is what an anchor is for. The accidental landmark has become an
intentional one.

## Façade depth

> *"Add actual massing depth rather than surface decoration."*

Every family now draws from a shared depth kit rather than a decoration kit:
window reveals cut into the wall, projecting sills, door surrounds, shallow
bays, porches, recessed shopfronts, drainpipes and hoppers, plinth and
foundation courses, stepped party walls, attached side structures, and rear
additions. Nothing on that list is a texture; all of it is geometry that casts
a shadow, because a shadow is the only thing that reads at thirty metres.

Roy's instruction not to paper every wall with windows to avoid blankness was
followed literally. The back walls have fewer openings than Sprint 027, not
more. What replaced the specks is mass: a door that sits in a surround, a
downpipe with a water butt under it, and — on one house in three — an attached
scullery wing with its own gabled roof, which breaks the flattest plane the town
owns without adding a single window.

## Roof material pass

The roof geometry was correct in Sprint 026 and invisible in Sprint 027. The
tile textures were redrawn for the distance at which they are actually seen:
stronger individual course definition, darker overlap lines under every course,
hue and value drift between tile groups, restrained weathering, soot around the
chimney bases, moss at shaded roof edges, occasional repaired and mismatched
patches, thicker roof edges, and dormers with visible cheeks and frames. Slate
is now a true second family with its own four-value palette rather than a rare
accent — in `L28_profile` and `L28_iso30` you can count the slate roofs and they
group.

It stays stylised. Nothing here moves toward photorealism; the tile is a drawn
tile, not a photographed one.

## Town composition and enclosure

> *"Do not expand the town footprint. Make the existing centre feel denser and
> more intentional."*

Not one metre of footprint was added. What was added is the thing that was
missing: **an English house does not sit on grass, it sits in a plot.**

Every house now has a walled back plot — a coursed-rubble boundary wall with
coping and piers, side walls, a flagged hard yard, a coal store, a washing line
with sheets on it, a log stack and shrubs. That single change is what closed the
lawn between the buildings, because the lawn was never a garden; it was the
absence of one.

Beyond the yard walls the middle ground was eighteen metres of mown nothing and
then a fence. It is now field parcels with hedged boundaries, a cross-hedge or
two, and trees in family groups. The western green became a hedged paddock with
an orchard corner. Ground-level cameras now see overlapping façades, walls,
roofs, trees and street furniture at three depths instead of one object against
open land.

The ground itself stopped being two flat colours. The carriageway is granite
setts with a gutter channel and a run of kerb stones down both edges; the
footway is York-stone flags; the square is brick setts; the lanes are coarser.
The high street gained lamp standards, planters and bollards, so the kerb is a
place rather than an edge. And every low wall in the town — yard walls, garden
walls, the twitten, both edges of the square — is coursed rubble with lichen
rather than a flat cream plane, which is what the raycast found lurking ten
metres from the square camera and doing nothing.

## What the frames caught — the fault I built myself

Stage F shipped hedges. Stage F's frames showed three dead-parallel green
ribbons of even height crossing the whole profile frame, each topped with an
evenly spaced row of identical bumps.

That is Sprint 027's fault, rebuilt by me, one sprint after being rejected for
it. Uniformity does not become acceptable because it is horticultural.

So `hedgeRun` was rewritten. A hedge is no longer one extrusion: it is a run of
2.2–4.3 m panels, each with its own height (±17 %), its own depth, its own green
and its own lateral drift off the line, because each panel was laid in a
different decade by a different hand and the top line is where that history
shows. The crown lumps take radius, spacing, height and colour from a position
hash, with genuine gaps where nothing grew and the occasional big one. The two
full-width boundary hedges became six parcel boundaries at differing y with two
cross-hedges, so the middle ground reads as fields rather than stripes. The
seven evenly spaced trees became fourteen in five family groups. The 3×2 orchard
grid drifted.

**Page errors: none, in all six capture passes (G28 through L28).**

## Against the acceptance standard

Roy set eight tests and required them to be proved in the images, not the code.
Read left-to-right in `sprint028-before-after.png`:

| the test | where it is proved |
|---|---|
| the town no longer looks generated from one house template | `profile`, `iso30` — cottage, terrace, shop-house, inn and civic are distinguishable at a glance |
| tall buildings look architecturally designed, not stretched | `square` — the inn has a ground floor, a middle and a top, and each is a different thing |
| the skyline has hierarchy rather than random variation | `profile` — it steps from the low cottages up to the anchors and back down |
| the high street reads as a coherent place | `terrace` — continuous frontage, fascias, awnings, setts, kerb, lamps |
| the square has a deliberate architectural anchor | `square` — the inn terminates the view |
| roofs visibly carry texture and age | `northrow`, `square` — courses, overlap lines, soot, moss, two families |
| central streets feel enclosed and layered | `terrace`, `northrow` — nothing stands isolated against open land |
| more charming and memorable within five seconds | the sheet itself; the before column is a diagram, the after column is a town |

## The Continuous Creative Direction review

**Did I protect language or composition?** Language. The composition Sprint 027
shipped was destroyed outright — the generic generator that had produced every
building in this town since the blockout was deleted, along with the height
sequence that was its only source of variety.

**Did I optimise a prototype or replace it?** Replaced, twice. Once at the
start, deliberately: seven authored builders in place of one parameterised one.
Once at the end, unwillingly: `hedgeRun` had to be replaced rather than tuned,
because a straight hedge with variation added to it is still a straight hedge.

**Is the town noticeably more beautiful?** Yes, and it passes the five-second
test in every one of the six pairs — which the previous two sprints did not.

**Is it more alive?** Yes, and for a reason that matters more than the geometry:
the town is now full of the evidence of ordinary work (CD-025). Sheets on a
line, coal in a store, wood stacked against a wall, a water butt under a
downpipe, a scullery built on the back when the family grew. None of it moves.
All of it says that someone lives here and has for a while.

**What did I not do?** The population data still gives households to only some
of the rows — raised for the ninth consecutive sprint and still awaiting a
ruling, and it now costs more than it did, because the buildings have become
specific enough that an empty terrace is a visible lie. The building families
are assigned by an authored map rather than derived from the simulation, so the
town's social geography remains decorative: the inn is an inn because I said so,
not because anyone drinks there. And the twitten, the north walk and the
school-corner shortcut still have no walk-graph edges, so the residents cannot
use the streets this sprint built.

## Honest notes

- Seven capture passes for one sprint. Each caught something the previous one
  created, and Stage G existed solely to repair a regularity I introduced in
  Stage E. Recording that plainly: I rebuilt the exact fault I had just been
  rejected for, and only the frames caught it. The brief's instruction to
  critique the images rather than the code is not a formality.
- The pale wall by the square that Sprint 027's raycast should have found was
  found this time by raycasting first, not squinting. It was pre-existing scene
  geometry, not new work — which is the argument for raycasting the whole frame
  rather than the thing you just built.
- Geometry cost is up substantially: twenty-three walled yards, six ground
  textures, a furnished high street. Still at frame rate headless, and the
  ground textures are cached and repeat-snapped rather than cloned per mesh,
  which was a real VRAM fault caught before it shipped. Yard walls and window
  units are the first things to instance if it ever bites.

## Deliverables

- `era-town-3d.html` — the town, rebuilt
- `sprint028-before-after.png` — six cameras, Sprint 027 left, Sprint 028 right
- `Sprint-028.md` — this record
- `era-sprint028-topup.bundle` — the commit, chained off Sprint 027 (`38a973b`)
