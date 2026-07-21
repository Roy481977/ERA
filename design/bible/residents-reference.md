# Residents — visual reference (from the bible lineage)

**Status: REFERENCE (locked bible lineage, Roy-approved direction).** The figures
that populated the concept images before we emptied the plate are the style guide
for ERA's future residents. Crops in [`residents/`](residents/). The plate itself
is empty (CD-008); everything here describes the **living layer**.

## What the reference figures teach

**Proportions & material.** Chunky clay figurines, ~2.5–3 heads tall, simple
rounded limbs, no faces, no fingers — silhouette and colour do all the work.
Matte clay/felt surface like the buildings; figures read as *part of the same
handmade miniature*, never glossy or photoreal.

**Scale rule.** A standing adult ≈ **0.9× a front-door height** (≈ 1.7 m at
world scale). In the 1024-px bible frame figures stand ~28–32 px tall; at the
final wide plate's resolution that projects to roughly **120–250 px** depending
on depth — enough for readable pose sprites, not enough (or needed) for faces.
Children ≈ 0.6× adult height.

**Colour language.** One solid, saturated torso colour per figure (terracotta
orange, teal, olive, mustard, brick red, cornflower blue — the town's palette),
muted trousers, small warm-tone head. Colour is identity at a glance — this maps
directly onto our per-resident `color` in the behaviour stream.

**Poses seen in the reference set** (the starting pose library): walk (pairs
walking together — chosen togetherness reads instantly), stand-and-chat pairs,
café sitting on chairs at round tables, market browsing (slight lean toward
stall), dog-walking. Matches the sim's existing pose/gesture vocabulary.

**The crowd rule** (`residents/stand-crowd.png`): a full stand is not hundreds of
sprites — it reads as a **stochastic texture of colour dots in seat rows** under
the roof shadow. Implement matchday crowds as a generated crowd-texture layer
(animated by subtle shimmer/wave), with individual sprites only for the front
rows or zoomed moments.

**Follow-up (Roy):** the dog and other animals need proper design passes — cats, birds with real wing poses, river ducks. Scheduled for the creature part of the character phase; the crops here set material/scale only.

## Production notes (living layer)

- Sprite sheets per resident archetype: 8 headings × pose cycles (walk/stand/
  sit/greet), rendered in the clay style (Meshy rig→animate→render, or
  image-model sheets — decide at character phase).
- Figures are tinted by the same time-of-day LUT as the plate, get a soft blob
  shadow, and depth-test against the plate's depth mask.
- Passages in the bible were deliberately widened so these sprites stay clearly
  visible on streets (Roy).

## The street set (Roy: "they were perfect for there")

- **`residents/riverside-dog.png` — the definitive street reference.** A man in a
  mustard sweater walking his felt dog mid-stride, and a *pair walking close
  together* along the river wall (chosen togetherness made visible). Proportions
  read perfectly against the picket fence and kerb. This is how ERA streets
  should feel.
- `residents/square-street.png` — square + street walkers among stalls and
  parked cars, all colour-as-identity.
- `residents/crossing.png` — the corner group by the zebra crossing.
- `residents/xwalk-figures.png` — market-stall browsers; note the **felt bird on
  the rooftop** — ambient wildlife belongs to the same material world.
- **`residents/pitch-players.png` — matchday reference:** an orange-kitted keeper
  at a goal with a woven net, outfield players in dark kits, the packed stand
  behind, tiny ad boards on the perimeter wall. Players are sprites; the crowd
  is texture.

Other crops: `residents/sq-figures.png` (square walkers + stalls),
`residents/street-cafe.png` (café sitters, walking pair, browsing),
`residents/stand-crowd.png` (crowd-as-texture). Source images in the
`../bible/` lineage.
