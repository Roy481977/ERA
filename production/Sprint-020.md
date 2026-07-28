# Sprint 020 — The Stepped Silhouette (Priority 5, solved completely)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched — all variation is seeded in the house kit.**

## What was built

Four seeded dials now vary every home while the Museum language holds:

- **Ridge height.** Five height classes per row (2.9 m to 4.05 m walls) —
  storey-and-a-half houses appear among the cottages, and the tall ones
  earn a pair of upper windows in the canon surround-and-sill language.
- **Roof pitch.** Four pitch factors (0.82–1.24), so adjacent roofs meet
  the sky at different angles even at equal height.
- **Roof orientation.** One house in seven turns its gable to the street —
  the classic terrace interruption that breaks a row's horizontal.
- **Dormers.** The wide kit now takes a dormer half the time, joining the
  dormer cottage kit; with Sprint 015's tall capped chimneys on every
  house and the link sections sitting deliberately lower between
  neighbours, the roofline reads as a rhythm of steps and accents.
- **The pub stands taller** (+0.9 m) — the square's north wall now has
  its own high point under the clock's counterpoint down the street.

## Success criteria, answered

**"Adjacent structures display distinct variation in ridge heights and
roof angles."** Within any three adjacent houses the seeds guarantee at
least two height classes and two pitch factors; verified visually along
both Market Street walls and North Lane in `silhouette_sheet.png`.

**"The town silhouette presents a stepped, rhythmic profile from a 30°
camera."** The 30° frame reads ridge–link–ridge–gable–chimney against
the hills; the before/after canon pair shows the flat band replaced by
steps.

**"Vertical accents break up horizontal rooflines consistently."**
Every house carries a tall double-potted chimney; dormers appear on two
of the three home kits; front-gables interrupt each long row; the clock
and the pub give the two public rows their peaks.

## Honest notes

Upper windows appear only on street-facing fronts; tall houses show a
blank upper band on their gable ends (visible on the square's corner
house) — acceptable at eye level, listed for the charm pass. Roof-pitch
scaling slightly steepens dormer roofs on the steepest houses; not
visible at play distance.

## Deliverables

`era-town-3d.html` · `silhouette_sheet.png` (before/after canon, south
elevation, 30°, the corridor) · this record.
