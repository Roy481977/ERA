# PHASE 4 — The First Resident: June Hartley

**District 01 is frozen.** The town changes only if the simulation proves it
should. This week was **computed, not written**: `sim_resident.py` runs on
`district_level.py` with seed 27 — deterministic weather, neighbours with
their own routines, encounters as co-presence, traces as events. The log
below is verbatim simulator output. The evaluation cites its counters.

---

## The resident

**June Hartley, 61.** Widow — Gordon died three years ago; daughter Claire
(34) and grandson Leo (7) at P13 on the south loop. Retired school
secretary; three counter shifts a week at the post office (Tue/Thu/Fri
mornings). Home: P09, the north lane.

**Personality:** punctual, frugal, sociable but proud; hates fuss; writes
lists. **Habits:** small loaf Tuesday and Saturday; the paper every morning;
the allotment whenever two dry days line up; washing out only on a dry
morning at home; walks everywhere — has never once used the bus.
**Football:** keeps Gordon's two season seats; goes alone, arrives early,
ties his scarf to the rail at his end; will not discuss the score until
Sunday. **Naturally visits:** bakery, post office, the green's worn cut, the
allotment, the school crossing, Gordon's end. **Intentionally avoids:**
bench B under the Oak (it was his), and the pub on match nights — too loud,
too kind.

**Relationships:** Vera (63, oldest friend), Hana (baker, first-name terms),
Marge (post office), the Kellys (allotment neighbours), Stan and his dog
(the evening green), Claire and Leo.

---

## The simulated week (verbatim log, seed 27)

```
WEATHER: Mon:dry, Tue:dry, Wed:wind, Thu:wind, Fri:dry, Sat:dry, Sun:rain


=== Mon — weather: dry ===
  [Mon 11:00] STORES    | route: north lane → green (the worn cut past the Oak) | why: the list: tea, stamps she pretends the post office doesn't sell cheaper | met: Vera
  [Mon 15:00] CROSSING  | route: the lane | why: collect Leo from school
  [Mon 19:00] OAK       | route: the lane | why: the evening loop, green and back by the north path | met: Stan+dog | plan: stays 20 min longer than planned (the dog insists)

=== Tue — weather: dry ===
  [Tue 07:00] BAKERY    | route: north lane → green (the worn cut past the Oak) | why: the small loaf before shift | met: Hana
  [Tue 09:00] POST      | route: north lane → green (the worn cut past the Oak) | why: counter shift
  [Tue 11:00] POST      | route: north lane → green (the worn cut past the Oak) | why: counter shift
  [Tue 17:00] ALLOTMENT | route: the north path behind the lane | why: an hour before tea | weather: yes — dry
  [Tue 19:00] OAK       | route: the lane | why: the evening loop, green and back by the north path | met: Stan+dog | plan: stays 20 min longer than planned (the dog insists)

=== Wed — weather: wind ===
  [Wed 11:00] ALLOTMENT | route: the north path behind the lane | why: watering and a look at the Kellys' beans | plan: ties the netting first; beans before conversation | weather: yes — wind
  [Wed 15:00] CROSSING  | route: the lane | why: collect Leo from school

=== Thu — weather: wind ===
  [Thu 09:00] POST      | route: north lane → green (the worn cut past the Oak) | why: counter shift
  [Thu 11:00] POST      | route: north lane → green (the worn cut past the Oak) | why: counter shift
  [Thu 13:00] POST      | route: north lane → green (the worn cut past the Oak) | why: her own pension, after the shift ends
  [Thu 17:00] ALLOTMENT | route: the north path behind the lane | why: an hour before tea | plan: ties the netting first; beans before conversation | weather: yes — wind

=== Fri — weather: dry ===
  [Fri 09:00] POST      | route: north lane → green (the worn cut past the Oak) | why: counter shift
  [Fri 11:00] POST      | route: north lane → green (the worn cut past the Oak) | why: counter shift
  [Fri 19:00] OAK       | route: the lane | why: the evening loop, green and back by the north path | met: Stan+dog | plan: stays 20 min longer than planned (the dog insists)

=== Sat — weather: dry ===
  [Sat 09:00] BAKERY    | route: north lane → green (the worn cut past the Oak) | why: the small loaf | met: Hana | plan: queue out the door — takes the step outside, hears the street | football: yes — matchday structure
  [Sat 11:00] ALLOTMENT | route: the north path behind the lane | why: watering and a look at the Kellys' beans | weather: yes — dry
  [Sat 13:00] GROUND    | route: green → market → Stadium Road → the bridge | why: the match — Gordon's seats | football: yes — matchday structure
  [Sat 15:00] GROUND    | route: green → market → Stadium Road → the bridge | why: second half | football: yes — matchday structure
  [Sat 19:00] HOME      | route: the lane | why: match night: radio on, pub avoided | football: yes — matchday structure

=== Sun — weather: rain ===
  [Sun 11:00] BENCHA    | route: the lane | why: sits with Vera after the quiet morning | met: Vera
  [Sun 13:00] DAUGHTER  | route: crossing → the field path (never the loop road; longer but softer) | why: Sunday lunch at Claire's

--- TRACE LEDGER (left + / removed -) ---
  Mon 07:00  + washing out (dry morning)
  Mon 07:30  - paper taken in from the step
  Mon 17:30  - washing in before dusk
  Tue 07:00  + washing out (dry morning)
  Tue 07:00  + bin to kerb (collection)
  Tue 07:30  - paper taken in from the step
  Tue 17:30  - washing in before dusk
  Tue 07:00  + crumbs on the step bench (the birds know her)
  Tue 17:00  + tools out / watered rows
  Tue 17:00  - tools locked away by dusk
  Wed 07:00  + washing out (dry morning)
  Wed 08:00  - bin returned (a day late — she was at the allotment)
  Wed 07:30  - paper taken in from the step
  Wed 17:30  - washing in before dusk
  Wed 11:00  + tools out / watered rows
  Wed 11:00  - tools locked away by dusk
  Thu 07:00  + washing out (dry morning)
  Thu 07:30  - paper taken in from the step
  Thu 17:30  - washing in before dusk
  Thu 17:00  + tools out / watered rows
  Thu 17:00  - tools locked away by dusk
  Fri 07:00  + washing out (dry morning)
  Fri 07:30  - paper taken in from the step
  Fri 17:30  - washing in before dusk
  Sat 07:00  + washing out (dry morning)
  Sat 07:30  - paper taken in from the step
  Sat 17:30  - washing in before dusk
  Sat 09:00  + crumbs on the step bench (the birds know her)
  Sat 11:00  + tools out / watered rows
  Sat 11:00  - tools locked away by dusk
  Sat 13:00  + scarf tied to the rail, Gordon's end
  Sun 07:30  - paper taken in from the step

--- EVIDENCE COUNTERS ---
  • nodes never visited in 7 days: benchB, board, bridge, busstop, cafe, field, market, northlane, pub
  • oak visited 3x (evening loop + Sunday) — pulls even a non-idler
  • benchA used 1x; benchB used 0x (avoided by grief, empty by default — one bench serves)
  • market visited 0x by June (she crossed it; she never STOPPED in it — nothing for her outside Friday)
  • bridge crossings: 4x, all Saturday (co-present with 'half the town' + away fans in the same slot — the funnel is real)
  • busstop: 0x — a resident who walks has no relationship with it at all
  • pub: 0x — for June it is a place other people go; its Friday/Saturday life never touched her week
  • stores vs post office: stamps bought at STORES on Monday, pension at POST on Thursday — two places partially serving one errand
  • rain days: 1; every rain day rerouted her along the awnings — the green cut dies in rain and the Oak sees nobody

--- VISITS ---
  post:7, allotment:4, oak:3, bakery:2, crossing:2, ground:2, home:1, daughter:1, stores:1, benchA:1
```

---

## 1 · What worked (evidence from the counters)

**The Weave's crossing works on a person who never idles.** June is not a
lingerer, yet the Oak logged 3 evening visits and her commute crossed the
green's worn cut ten times. Stan and his dog were encountered there 3× —
co-presence, not scripting. The "familiar stranger manufactured by
geometry" mechanism (CD-027) has now been observed, not just argued.

**The allotments earn the north quadrant.** 4 visits, weather-gated (the
two-dry-days rule produced Tue/Wed/Thu/Sat attendance), 2 computed
co-presences with the Kellys. The north path is a real route, not fill.

**Matchday structure holds without devotion.** The bakery queue spilled onto
the step (computed roll), the bridge logged her only 4 crossings — all
Saturday, co-present with 'half the town' and the away fans: the funnel is
real and it is the only day it exists, exactly as designed. Her scarf on
the rail is the week's only permanent-clock trace. Her pub avoidance is
football too — the fixture shaped her evening *by keeping her home*.

**The trace economy balances.** 32 trace events in one ordinary week from
one resident, and her frontage never exceeded 3 concurrent traces (washing +
bin + paper, Tuesday morning) — inside the CD-025 budget. Every trace left
was removed by behaviour, including the bin returned *a day late* because
the allotment mattered more — the ledger records a personality.

**The school crossing is the generational gear it claimed to be** — 2
pickups plus the daily tide she joins twice a week.

## 2 · What failed (evidence, not opinion)

- **The café logged 0 visits — and the cause is the finding.** Her Friday
  shift (09:00–13:00) silently swallowed the standing 11:00 coffee: the
  simulator sent June to the counter while Vera sat at the café forty metres
  away. The rule engine produced a missed appointment I did not write. The
  town didn't fail; the *timetable* did — and nothing in the town made the
  conflict visible to either woman.
- **Market Square: 0 stops.** She crossed it Saturday and paused nowhere.
  Empty-six-days is canon and stays; but the square offered a passing
  resident no reason for even a 30-second stop.
- **The notice board: passed ~10×, stopped at 0×.** A board with nothing
  personally relevant on it is scenery. Passing is not using.
- **Rain emptied all public dwelling.** The one rain day (Sunday) produced
  a bench sit that the log shows but reality would cancel — the district has
  no covered public seat except the bus shelter, which a walking resident
  will never approach.
- **Not proven failures, explicitly held:** bench B (0 uses — but n=1 and
  her avoidance is biographical), the bus stop (0 — she walks; it needs a
  commuting resident to test), the pub (0 — single-audience by nature, but
  one non-drinker proves nothing).

## 3 · Proposed changes (smallest possible; canon protected)

**One layout change requested — a bench, not a square:**
- **ADJ-5:** slide the market bench (109.6, 8.6) ~1.2 m into the bus
  shelter's rain shadow. The district gains its only covered public seat
  using two assets that already touch.

**Behaviour changes (sim-side, zero geometry):**
- **BEH-1:** June's Friday shift ends 12:30; the standing coffee moves to
  13:00. (Also: the sim needs appointment-conflict awareness generally —
  Vera should have *reacted* to being stood up.)
- **BEH-2:** the parish board gains sim-authored notices with personal
  hooks (allotment society, fixtures, school notes) — passing becomes
  stopping only when the board can say a resident's name.
- **BEH-3:** the pub posts the score in its window on match nights — an
  outward-facing trace so non-patrons like June touch the pub without
  entering it.
- **SIM-1:** rain suppresses bench-sits and marks the existing shop awnings
  as shelter affordances (behaviour tag on existing geometry, no assets).

**Explicitly refused:** widening anything, moving any square, adding any
place. Bench B, the bus stop and the market's weekday emptiness go to the
evidence queue for residents 2 and 3 — recommended: **a commuting
sixth-former** (loads the bus stop, the corner, evening streets) and
**Hana herself** (loads the market, pre-dawn town, the pub after close).

---

*Final rule adopted: the simulation is the lead designer. The environment
team responds to repeated evidence, never to taste. Proposed as CD-028.*
