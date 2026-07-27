# DISTRICT 01 IN THREE DIMENSIONS — the Phase 11 verdict

**Status: PROPOSED. The blockout is evidence; the changes await Roy.**
Blockout: `era-town-3d.html` (self-contained, Three.js inlined, the full living
simulation running inside it). Six state contact-sheets: `state_*.png`.

---

## Spatial metric sheet

Scale: 1 world unit ≈ 1.1 m (person 1.55 u against a 1.9 u door).
Town extent 192 × 116 u ≈ 210 × 128 m — a five-minute walk end to end,
including the ground. That is smaller than the fiction implies and is the
right size for ONE district of a larger town.

| metric | value |
|---|---|
| road widths | 4.0 / 6.0 / 6.5 u (Loop widest) |
| pavement width | 2.6 u typical |
| kerb upstand | 0.09 u |
| building heights | homes 2.9 u · shops 3.4 u · stand 2.2 u + roof |
| door / person | 1.9 u / 1.55 u (0.82 ratio ✓) |
| the green | ≈ 28 × 9 u — LONG AND THIN (see failures) |
| pitch / stand | 30 × 20 u / 26 u frontage |
| ground apron | 60 × 42 u (oversized — see failures) |

**The ten journeys** (street-factor distance ≈ straight-line × 1.3; minutes at
a real 80 m/min):

| journey | ≈ m | ≈ min | character |
|---|---|---|---|
| Bill's house → bakery | 107 | 1.3 | one straight street; passes café, stores — 3 encounter chances |
| June's house → post office | 118 | 1.5 | North Lane → cut to Market St; quiet→busy gradient ✓ |
| child's home → school | 24 | 0.3 | one zebra; safe, legible ✓ |
| bakery → green & oak | 64 | 0.8 | worn cut; the oak visible whole way ✓ |
| pub → ground | 46 | 0.6 | the threshold walk: tightens at bridge, opens at apron ✓ |
| allotments → Market St | 59 | 0.7 | gate → lane → street; good gradient |
| bus shelter → café | 55 | 0.7 | dull: crosses the empty square (see failures) |
| ground → pub (post-match) | 46 | 0.6 | the pour-back reads perfectly on matchday capture |
| Roy's home → allotments | 84 | 1.1 | crosses the whole quiet north — good morning walk |
| full circuit of the Loop | ≈ 340 | 4.2 | perimeter feel ✓ but half of it faces nothing |

Alternate meaningful routes between centre and green: 3 (street, worn cut,
North Lane back way) ✓. Between centre and ground: 1 — the bridge is the only
crossing, which is CORRECT (threshold law).

---

## What worked better than expected

1. **The threshold.** River + bridge + pylons: the ground is separate but
   always present. On matchday the convergence down Bridge Road and the
   pour-back at 17:30 read spatially with zero labels. The town's best idea
   survives 3D intact.
2. **The oak is the landmark.** Biggest single form in the skyline; the worn
   spokes converge on it; "meet me by the oak" is a place you can see.
3. **The painted street works without labels.** Awning + accent + sign at
   blockout finish already distinguishes bakery/café/stores/post/pub at
   three-quarter AND eye level.
4. **One module, one town (SL-7).** Same storey, same roofline family — the
   blockout already reads as ERA, not as developer-grey.
5. **The states carry atmosphere with fixed geometry.** Pre-dawn's lit
   windows, the rainy evening's glowing pub, post-loss dusk — same town,
   different feeling. The living systems are doing the scenography.

## What failed in three dimensions

1. **Market Street is single-sided.** The whole south side is bare pavement.
   At eye level it is a row of shops facing nothing — no enclosure, no
   corridor, no corner to turn. The 2D plan never showed this; the first
   eye-level frame did.
2. **The green has no built edge.** 28 × 9 u of lawn defined only by the oak
   and two benches; agents cross it diagonally and never dwell on its edges.
   It reads as leftover space — the exact thing the brief forbids.
3. **The south row floats.** Loop houses sit in open lawn with no gardens,
   walls or street relationship; they read as scattered monopoly pieces.
4. **The pedestrian network is gappy — by design, not by bug.** Graph
   analysis: 8 disconnected islands. North Lane and the Loop had NO designed
   footpath into the centre; the shops row has no continuous front-door
   pavement spine. The agents were quietly beelining across grass all along.
5. **The east quarter is dead lawn.** Between the square and the river
   nothing invites the crossing; the bus-shelter→café walk is the dullest in
   town.
6. **One house kit reads repetitive.** In 2D the accents carried variety; in
   3D a single massing cannot.
7. **The ground apron is oversized.** The pitch reads small inside 2,500 u²
   of empty apron; the stand floats in it.

## Proposed changes (all PROPOSED, smallest-change discipline)

- **ADJ-6** Formal footpaths: North Lane↔green link; Loop↔School Lane link;
  continuous Market Street pavement spine along the shop doors.
- **ADJ-7** Enclose Market Street's south side: relocate two Loop houses to
  face the shops as a short terrace (kills failures 1 and 3 together);
  minimum fallback: low wall + tree line.
- **ADJ-8** Give the green a built edge: shift the P01–P03 garden line to
  face it across a narrow lane; benches move to the built edge.
- **ADJ-9** Shrink the ground apron ~30% and pull stand + turnstiles toward
  the bridge; the ground gains presence, the walk gains compression.
- **ADJ-10** Two additional house kits (terrace pair; L-plan) inside the
  same module — variety without breaking SL-7.
- **ADJ-11** A riverside path from the square to the bridge — activates the
  east lawn and gives the bus-shelter→café walk a reason to be pleasant.
- **ADJ-12** Regenerate worn paths from the year's actual walk record.

## Recommendation

**Preserve with targeted changes.** The composition — the Weave, the
anchors, the threshold, the journey gradients — survives three dimensions
intact; every failure found is an *edge and enclosure* problem, not a
structure problem. Nothing calls for a rebuild. The seven ADJ items above
are the price of admission to final environment production, and none of them
moves a meaning-anchor.

The living systems were the review instrument: the network gaps were found
by routing the residents, the green's weakness by watching where they
refuse to linger, Market Street's missing side by standing at eye level in
the morning queue. The simulation is still the lead designer (CD-028).
