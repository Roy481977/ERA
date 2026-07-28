# Sprint 029 — The Town Gets Its Glass, and the Centre Grows Out of the Town

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — the engine, the fixtures, the residents, the walk graph
and the historian are byte-identical. Every change is in the viewer's render
layer, exactly as the brief scoped it. The footprint has not grown. No building
family was replaced and no new architectural system was introduced.**

Roy approved the direction of Sprint 028 and refused the visual finish, with one
priority:

> *"The high street currently feels like a detailed red-brick kit inserted into
> a much simpler white-rendered town. Create a gradual architectural transition
> toward the centre. … The centre should feel like it grew from the surrounding
> town rather than being placed into it."*

That brief was executed. But chasing one shopfront that would not photograph
found something larger, and it is the headline of this sprint.

## The headline: 253 of the town's 278 windows were inside the wall

The modest converted shopfront built in Stage A did not appear in its own close
frame. The panes existed, the camera was right, the material was right — and the
glass was still not there. Raycasting the façade found the shop's window sitting
**seven centimetres inside** the building's front wall.

The cause is one number. `roundedBox` — which draws every building body in this
town — is an `ExtrudeGeometry` with `bevelEnabled` and `bevelSize: 0.09`. A body
of nominal depth `dep` therefore has its real face at `dep/2 + 0.09`. Every
façade helper in the project has been placing its glass at `dep/2 + 0.012` to
`dep/2 + 0.03`. Six to eight centimetres short. On every window. Since the
blockout.

An audit of every pane in the town — four sample points per pane, raycast from
four metres out along the pane's own normal — returned **25 clear, 253 buried**.

What we have been looking at for twenty-nine sprints is a white surround with
the *wall* showing through the middle of it. Not a window: a picture frame
nailed to a wall. Which explains two things that had been filed as taste
problems:

- The buildings read as a kit. A wall with no openings in it is exactly what a
  kit reads as, and no amount of architectural family work was going to fix a
  town whose façades had no holes in them.
- The evening window-light system, built four sprints ago, had never visibly
  done anything — because there was no pane in the town for it to light.

The fix is four lines. `winRec` now adds the bevel outset by default
(`zf += (o.bv === undefined) ? 0.09 : o.bv`), a bay window passes `bv: 0.012`
because it is a plain box already standing proud, and both shopfronts take
`zf = dep/2 + 0.09`. The audit went to **185 clear**, the residue being
legitimate occlusion — hedges, roofs, yard walls, lean-tos and party walls.

Then the lighting rule had to be corrected, because it had never been tested
against a pane that existed. It said a shop window is lit whenever anyone is
inside, at any hour — which in daylight paints pale cream on a pale cream wall
and puts a hole in the building. A shop window in daylight is the darkest thing
on the street; you cannot see into it. It is now dark by day (`0x43555f`) and
goes warm only when occupied after dusk. `X29_dusk` is the first frame in this
project's history in which the town's windows are lit.

## The ranked critique of the Sprint 028 frames

Read off `L28b_walkin`, `L28b_iso30`, `L28b_terrace` and `L28b_westshops`, worst
first, before any code was opened.

1. **The centre is a different town.** Roy's fault, and correct. Red brick,
   bays, fascias and slate stop dead at a line, and beyond that line every
   building is white render with a terracotta roof. There is no intermediate
   condition anywhere — no rendered house with a brick flank, no brick ground
   floor under a rendered upper, no house that has had a shop cut into its front
   room. A town does not change material at a boundary; it changes over a
   quarter of a mile.
2. **The west approach is empty.** The visitor's first frame has buildings on
   the near left and near right and then a long gap before anything. The centre
   is dense, the approach is not, and the sequence reads as *nothing, nothing,
   nothing, town.*
3. **The desire lines float.** The worn paths were flat polylines laid over a
   tiered ground, so they hovered above the green plateau and sank into the
   north terrace, and they ran straight over kerbs and pavements as though
   nobody in this town has ever walked on a footway.
4. **The gable ends are blank.** Big unbroken wall with one small window in the
   middle. This is the Sprint 027 "scattered specks on big blank walls" fault
   surviving on the one elevation nobody had a camera on.
5. **The carriageway is a large dead grey mass.** Forty to fifty per cent of
   the ground-level frames. Noted, out of scope for this brief.

## What was built

### Stage A — the transition, and four infill plots

A centrality field, one number per plot:

```js
CEN[p.id] = clamp01((112 - hypot(p.x - 115, (p.y - 20) * 1.9)) / 96)
```

Zero at the fields, one at the square. Everything material in the town now reads
from it rather than from a plot's index:

- **Wall colour** ramps from limewash to warm render and then to brick.
- **Roof material** mixes terracotta and slate by centrality, with individual
  buildings taking mixed additions.
- **Brick flanks** (`brickFlanks`) put a brick side wall on a rendered house.
- **Brick bases** (`brickBase`) put a brick ground floor under a rendered upper
  floor, correctly outset by the bevel.
- **Modest shopfronts** (`shopFrontPlain`) — a stallriser, one window, a plain
  lintel, a small painted fascia and a domestic door beside it. This is the
  corner shop cut into somebody's front room. It is not the authored high-street
  shopfront and it is deliberately much plainer.
- **Small attached commercial extensions** (`shopExt`, driven by `EXT`) — a
  dairy on M3, a store on P03.
- **Restrained bays** on residential buildings only.

Four infill plots — M1, M4 on the west approach, M3, M5 on the mid street — fill
the gap without moving the town's edge. Two are two-unit terraces, two are
ordinary village houses.

The resulting order, west to east, is Roy's, in the ground:

```
small cottages → ordinary village houses → modest terraces
→ mixed residential and commercial → authored high street and square
```

### Stage B — the desire lines follow the ground

Every worn path is subdivided into ~1.10 m pieces, each sampling the terrain at
five points and tilting to match (`rotation.order = "YXZ"`). A path now runs up
onto the green plateau and down onto the north terrace instead of cutting
through them.

### Stage C — a desire line stops at the kerb

A `PAVED` list and an `onPaved(x, y)` test cull worn-path pieces that fall on
carriageway or footway. People wear grass, not pavement.

### Stage D — the glass (above)

### Stage E — the gradient reaches its own edge, and the gables compose

Two faults, both read off the post-Stage-D `walkin` frame.

**The ramp had no bottom.** The old rule gave a building at the town's edge a
sixty per cent chance of a warm body, so the last house before the fields came
out salmon pink. Roy's transition *starts* at limewash and arrives at brick; it
does not start halfway. Recalibrated to 92 per cent pale at the fields, 12 per
cent at the square.

**The gables.** `flankWorks` now runs both sides of a cottage, a village house
and a converted shop rather than one, adds a ground-floor tier so a two-storey
house is not a face with one eye, and grows a foot to the gable: a plinth
return, and by seed either a trained creeper, a log store with a stack of split
logs, or a water butt on a brick stand. Everything is under half a metre deep,
because the gap to the next plot is often only sixty centimetres.

### Stage F — the creeper meets the ground

The close frame showed the trained shrubs hanging eighty centimetres clear of
the earth. A plant that does not touch the ground is not a plant; it is a green
blob glued to a wall, and it reads as an error rather than as evidence of life.
Grounded, stretched up the wall so it reads as trained rather than as topiary,
and given a bed of soil to grow out of.

## Canon review (Continuous Visual Development Directive)

**Did I protect language or composition?** Language. The bevel-outset fix is a
language fix — it changes what a window *is* in this project — and it was found
by refusing to accept a composition ("the shopfront doesn't read") as a
composition problem.

**Did I optimise a prototype or replace it?** Neither, deliberately. Roy's brief
said preserve the building families and introduce no new architectural system,
and none was introduced. The one thing that *was* replaced rather than tuned is
the window-placement rule, which was wrong rather than weak.

**Is the town noticeably more beautiful?** Yes, and it passes the five-second
test on the western approach, the high street and the square. The single largest
visual gain in the project's history is Stage D, and it is a bug fix.

**Is it more alive?** Yes. Windows now read as openings, shops read as dark by
day and warm at dusk, desire lines sit on the ground and respect the kerb, and
the sides of houses carry the ordinary junk of living in them.

**What did I not do?** The carriageway is still a large dead grey mass and the
lower half of the profile frame is still empty field — both noted, neither in
this brief. Every pane in the town is still the same blue-grey value: no
curtains, no blinds, no reflection variation. The population data still gives
households to only some of the rows — raised for the tenth consecutive sprint,
and now costing more, because four more specific-looking empty buildings were
added this sprint. The twitten, the north walk and the school-corner shortcut
still have no walk-graph edges.

## Honest notes

- The buried-glass fault has been visible in every frame of every sprint and I
  described the result as "flat" and "kit-like" five times without finding it.
  It was found by chasing one small object that refused to photograph, and by
  raycasting rather than squinting. That is the second consecutive sprint in
  which the frames caught a fault the code review did not.
- The pane audit's first version was a false negative: a ray to the centre of a
  pane hits the pane's own glazing bar. Sampling four points at ±28 per cent of
  the pane's width and height fixed it. Recording that because an audit that
  lies is worse than no audit.
- Post-Stage-E the audit reads 206 clear of 327, up from 185 of 278 — the new
  gable windows added 49 panes, of which about half sit on walls that abut a
  neighbouring building and are correctly hidden by it. That residue is
  geometry drawn for nothing. It is cheap; it should be culled when a plot
  adjacency map exists.

## Deliverables

- `era-town-3d.html` — the town, rebuilt
- `sprint029-before-after.png` — six cameras, Sprint 028 left, Sprint 029 right
- `Sprint-029.md` — this record
- `era-sprint029-topup.bundle` — the commit, chained off Sprint 028 (`d061505`)
