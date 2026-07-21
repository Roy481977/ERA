# ERA — Town composition (the basic layout)

> **THE COMPOSITION BIBLE — LOCKED (Roy, 2026-07-21).**
> [`design/bible/composition-bible.png`](bible/composition-bible.png) is the
> canonical image of ERA's district. Generated in Krea (concept-first, per
> CD-008), picked and iterated by Roy. It defines:
>
> - **Scale canon:** a compact quarter, ~200 m of frontage (~300 m deep). The
>   stadium is a small-town football ground — one main stand, cropped by the
>   right frame edge (~70 % visible), garden/park in front and beside it.
> - **Fabric:** dense joined terraces, terracotta/cream/teal clay-felt style,
>   **winding organic streets** (residents never walk straight lines — nav paths
>   curve; passages sized so walking figures read clearly), clock-tower square
>   with market stalls + café umbrellas (static props), river + stone bridge
>   sweeping the foreground, station with **empty tracks** on the horizon.
> - **The plate is empty of life:** no people, no crowd, no train, no weather,
>   no time-of-day — all of that is the composited living layer (CD-008).
>   Parked cars are props and stay.
> - Lineage in [`design/bible/`](bible/); the alt with a cleaner square kept as
>   `lineage-3`. Bible is square; the wide desktop plate comes from the 2.4:1
>   blockout + tiled depth-locked generation using the bible as style reference.

**Status: REFERENCE / superseded in part by the bible above.** The composition
north-star for the town area,
from Roy's reference images. Sits alongside the [Asset Design Model](asset-design-model.md)
(the *look*) and the [Generative World System](generative-world-system.md) (what
grows). This document fixes *where the pieces sit and how the town reads*.

> **Style decision (Roy) — the clay/felt macro diorama (LOCKED).** The definitive
> look is a soft handmade clay/felt miniature shot macro: matte clay & felt
> materials, cream/terracotta/**teal** palette, soft warm sun with gentle occlusion,
> strong **macro depth of field** (close hero sharp, the rest blurred), and dense
> human-scale props. Detail is reached via the **AI-3D asset path** (Meshy/Tripo/
> Rodin image→3D → glTF, style-gated). See
> [asset-design-model.md](asset-design-model.md) §1.1/§3.6. Camera: bring the **hero
> (stadium/square) close and large in the foreground**.
>
> **View decision (Roy) — true 3D perspective with a real horizon.** From Roy's
> framing sketch: **sky occupies the top ~25–30%** of the frame; the **town recedes to
> a real horizon** (far objects — a train station, distant houses — get *smaller*, not
> same-size); the **stadium is large in the foreground**, the **central square** and the
> **café / lively area** sit mid-ground. This is a **perspective camera**, not flat
> isometric — distance is real and hazes into the horizon. It supersedes the locked
> 2:1 iso; see [asset-design-model.md §0.1](asset-design-model.md). A first true-3D
> prototype (Three.js) is live at `/ERA/scene3d.html`, driven by the same behaviour
> stream.

## The reference, in words

An aerial, tilt-shift isometric miniature town in bright daylight — the same
scale-model diorama the asset model calls for. Its composition:

- **A big town square at the heart** — a paved plaza with a **central monument
  column on a roundabout**, ringed by café terraces with **coloured umbrellas** and
  tables, and by tall **terraced shopfronts with awnings** (a grocer, a café, shops).
  The square is the busiest, most legible space.
- **A modern stadium** off to one side (the east in the reference) — large, distinct,
  with visible stands and a roof lip. It reads immediately as *the ground*, not a
  building.
- **A river winding through**, crossed by a **stone arch bridge**, with **riverside
  houses** behind garden walls and hedges, gardens down to the water, a small boat.
- **Terraced housing blocks** — rows of joined houses with pitched roofs, front
  gardens, tree-lined, filling the blocks around the centre.
- **Streets that curve** organically (not a rigid grid), with **sidewalks**, a
  roundabout at the square, parked and moving **cars**, and generous **trees, hedges
  and greenery** throughout.

This validates ERA's existing structure exactly: stadium, main square, café, pub,
bakery, museum, school, the river and the Old Bridge, and residential lanes — the
twelve simulated places plus the wider town's homes.

## Streets (Roy's street references — the street language)

Streets are a lead compositional element, not filler. From the references: **roads
curve and wind** (not a rigid grid), with a **dashed centre line** and edge markings;
**raised sidewalks / kerbs** flank every road (paved or cobbled), distinct from the
asphalt; **crosswalks** (zebra stripes) at intersections; **roundabouts** at the
square; roads are **tree-and-lamp lined**, with planters and flowering trees along the
kerb; **cars** parked and moving; and **buildings front directly onto the street**
with shopfronts, awnings and stoops, the sidewalk between building and road. All under
the clay/macro-DOF look.

*First pass (3D scene, done):* every road now has asphalt + flanking sidewalks + a
dashed centre line, with **street trees, lamps (glowing at night) and cars** along the
kerb. *Next:* make the roads **curve** (spline roads, not the grid), add **crosswalks**
and a **roundabout** at the square, and front the buildings onto the sidewalks.

## How the prove-it slice reflects it (first pass)

The Pixi slice now composes toward this: the **square** is a paved plaza with a
monument column, a green roundabout island and café umbrellas; the **stadium** is
drawn as stands with a pitch and a roof lip; a **river** winds through the map on the
ground and the **bridge** is a stone deck with an arch over the water; **café and
pub** get pavement umbrellas; the twelve places sit inside a **greater town** of
streets, sidewalks and building blocks under an open sky.

## Still to close toward the reference

- **Terraced rows**: filler buildings are currently free-standing boxes; the reference
  has *joined terraces* along the streets — draw blocks as connected rows.
- **Curving streets**: the fabric is a grid; the reference streets bend and meet at
  the roundabout. A more organic road layout (and real sidewalks the sim knows about)
  is the next step.
- **Shopfront detail**: awnings, coloured facades, ground-floor shops on the square.
- **Cars and street life** as ambient props.
- These are renderer/composition steps; the authoritative simulation is unchanged.
