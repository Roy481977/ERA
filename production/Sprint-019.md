# Sprint 019 — Organic Circulation, Terminated Sightlines (Priority 4, solved)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — all viewer-layer; the new paths are drawn (walk-graph
edges for them are queued for the next sim-open, with the twitten's).**

## What was built

**Every street axis now ends at something.**
- **Market Street, west** — THE FARM: farmhouse with its door facing down
  the street, timber barn, gravel yard, gate posts, trough and two trees.
  The village's western vista terminates in a working edge, and the
  village-to-landscape transition (named in Sprint 015's review) begins.
- **School Lane, south** — the field barn: a timber shed with a green door
  and a bench, closing the lane against the playing field.
- **North Lane, east** — the allotment stable on the terrace, its dark
  door facing back down the lane.
- **North Lane, west** — gate posts and a hedge return cap the lane.
- **Market Street, east** — already terminates in the square's north row,
  then opens deliberately to the Bridge Road reveal (canon, untouched).

**The routes bend.**
- **The north walk** — a curving path from North Lane's end, behind the
  north row's gardens, down to the square: five bearing changes framing
  the pub corner as it descends.
- **The school-corner shortcut** — a worn diagonal from Market Street to
  School Lane, the first non-orthogonal line in the west of the village.
- With the Bridge Road sweep, the riverside path, and the record-grown
  desire lines, the pedestrian network now bends at its edges while the
  historic street grid stays honest.

**Junctions vary.** A paved apron widens the school crossing; a gravel
apron splays the green-west/North Lane corner; the square's mouth, the
sweep's oblique entry and the twitten give the network five distinct
junction characters.

## Success criteria, answered

**"Primary pedestrian routes feature subtle, non-linear paths framing
focal points."** The north walk frames the pub corner; the sweep frames
the bridge and ATHLETIC beyond; the green mouth frames the oak; the
twitten frames the railway. (The brief's "museum facade" does not exist
in District 01 yet — the Museum Quarter is Book canon awaiting its
district; noted, not faked.)

**"Views along major street axes terminate into building facades or
landmarks."** West → farmhouse gable. South → field barn. North Lane
east → stable; west → gate and hedge. East → square row, then the one
sanctioned opening: the reveal. Verified frame by frame in
`sightlines_sheet.png`.

**"Street junctions vary in angle and width."** Two new aprons, one
oblique sweep entry, one narrow twitten, one wide square mouth.

## Honest notes

The farm, barns and stable are viewer-layer set pieces — no farmer
household yet (the same data question as Ground Row and the north row;
one ruling would people all three). The north walk and shortcut have no
walk-graph edges yet, so residents don't use them — queued with the
twitten edge for the next simulation change. P01's garden shed sits
hard against the north pavement and reads stray — flagged for the next
charm pass.

## Deliverables

`era-town-3d.html` · `sightlines_sheet.png` (five terminated/bending
views) · this record.
