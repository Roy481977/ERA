# ERA — Town composition (the basic layout)

**Status: REFERENCE / PROPOSED.** The composition north-star for the town area,
from Roy's reference images. Sits alongside the [Asset Design Model](asset-design-model.md)
(the *look*) and the [Generative World System](generative-world-system.md) (what
grows). This document fixes *where the pieces sit and how the town reads*.

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
