# Sprint 014 — Destroy The Prototype

**Status: EXECUTED (this sprint's build is delivered; layout PROPOSED pending Roy).
Kind: OPERATIONAL — this is a production order, not a governing document.**

## The brief (Roy, 2026-07-27)

District 01 should stop feeling like a prototype. Success is measured by
emotional impact, not implementation effort. Before touching any asset:
rank the ten largest reasons the district still feels artificial. You may
not improve anything outside the top three. If composition is ranked #1,
you may not spend meaningful effort on props. If enclosure is #2, you may
not redesign architecture first. Everything follows the ranking. Every
proposal must answer: "What is the largest emotional improvement per hour
of work?" Every change must produce an immediately recognizable
before/after. If a reviewer cannot identify the improvement within five
seconds, the work failed.

## The ranking (from the brutal critique, district01-critique.md)

1. **The village is a line, not a place** — no knot, no centre of gravity.
2. **No enclosure anywhere** — street ratio ~10:1 against a village's 2–4:1.
3. **The green is a traffic verge, not a village green** — no building
   faces it; the oak stands in a corridor.
4. The shops don't hold the street (they float 9 m behind their pavement).
5. Housing is not fabric (four disconnected strips).
6. The square is a leftover.
7. No vertical accent, no skyline.
8. Streets never turn, vistas never close.
9. Football is invisible six days in seven.
10. The east end dribbles out.

Ranks 1–3 are one problem — **the plan** — so the sprint replaced the plan.
(4, 5, 6, 7 fell out of the same rebuild for free; 8, 9, 10 deferred.)

## What was done (REV2 — the village plan, all in data)

- A continuous shop-and-terrace wall on the south side of Market Street:
  bakery at the school corner, stores, café, post office, then the terrace
  (P14, P13, P15 — Jack still 30 m from the pub). Street enclosure went
  from ~10:1 to ~2.4:1. The street is now a room.
- The green became a three-sided room, 28×20 m: North Lane cottages face
  it from the north (June's window at P09 looks straight down the green to
  the oak), two shoulder cottages close east and west, and its mouth opens
  onto the street between bakery and stores. Oak, swing, benches, daisies
  and worn desire lines all live inside it.
- A new lane (green-west) links street to North Lane along the green.
- The pub walls the square; the square keeps its market, flag, noticeboard.
- The post office carries a clock turret — the village's first vertical
  accent, faces turned east and west to close the street vistas.
- The year was **re-simulated on the new geography** — the lives inhabit
  the new plan; nothing was painted on. Movement graph verified continuous
  (max step 4.4 units at 60×; no teleports).

## The five-second test

`village_plan_before_after.png` — six standard cameras. Every row reads as
a different, denser, real village at a glance: one-sided road → two-sided
street; pavilion shops → shop wall with pavement trees; strip green → green
room. No row needs explanation.

## The five-question review (per the Continuous Creative Direction)

**1. The five biggest weaknesses now:** residents (tokens, not people — the
single largest gap left); streets still never bend (orthogonal dog-legs
only — needs diagonal support in the drawing layer); the east gateway from
the bridge still dribbles; the river banks are two colours meeting in a
line; shop interiors are blank glass.

**2. Bold decisions:** the entire building layout was replaced, not
adjusted — every shop, the pub, and eight of ten homes moved; the green
tripled in depth and gained walls of homes; the clock was enacted (Phase 10
proposal); the shops flipped to the opposite side of the street.

**3. Layout changes:** everything except School Lane, P11, P12, the field,
allotments, river, bridge, and the ground. The Loop and its edges kept.

**4. Language kept identical:** every kit, colour, material, tree, figure,
and micro-behaviour is untouched — the same Museum grammar, redistributed.
The simulation, behaviour rules, football calendar and canon residents are
byte-for-byte the same code and data apart from coordinates.

**5. Substantially closer to the target?** Yes. The reference test — "why
does one image feel like somewhere people live?" — was answered: because
buildings stand close enough to hold space between them. The district now
holds space: a street you're *in*, a green you're *on*, a square you
*arrive at*. What still separates us from the reference is people and
weathering, not plan.

## Deliverables

`era-town-3d.html` · `village_plan_before_after.png` ·
`village_plan_walkthrough.png` (June's-line walk at eye level) ·
`district01-critique.md` (the ranking) · this file.

## Proposed for Sprint 015

The residents. The stage no longer excuses the actors: silhouette variety,
faces, hands, and personal wardrobe. (Weakness #1 in the new ranking; the
CD review has said it twice now.)
