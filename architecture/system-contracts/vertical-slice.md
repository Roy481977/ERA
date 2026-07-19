# WI-01 · Town Engine Vertical Slice

**Status: PROPOSED.** The first buildable proof. Goal (from the roadmap and the
Town Engine strategy): *prove that lives reliably reach the right places for the
right reasons* across an ordinary day, a matchday, and a disruption — and that the
world persists when the player leaves. **Not** a beautiful town, and **not**
feature-complete.

## Engines in scope (scope guard)

Only what the slice needs: **Town, Time, World-Persistence, Semantic Place Graph,
Relationship, Event, Weather, Crowd (aggregate)**. Matchday appears as a **day_type
transform**, not the full Matchday Engine. The Meaning engines (Memory,
Recognition, Culture, Narrative), Economy, Audio, and the AI Director are **not**
in the slice's mutation path (they arrive in roadmap Phases 2–4). One **Tier-0
protected milestone** is included to prove authored beats survive.

## The district (subset)

~12 semantic places, each with affordances (see `world-state-schema.md`):

| Place | Type | Key affordances |
|---|---|---|
| Residential lane (homes) | home | `SLEEP`, `HOME_MORNING`, `SHELTER_FROM_RAIN` |
| Bakery (Mrs. Hana) | work / social | `WORK_BAKERY_COUNTER`, `BUY_BREAD`, `DOG_REST_SHADE` |
| Café (Luca) | work / social | `WORK`, `DRINK_COFFEE`, `WAIT_FOR_PERSON`, `LEGENDS_CORNER` |
| Pub (Otto) | work / social | `WORK`, `GATHER`, `POST_MATCH` |
| Florist (Eva) | work | `WORK`, `TEND_MEMORIAL` |
| Kiosk / Station (Karim) | work / transit | `WORK`, `BUY_PAPER`, `WATCH_TRAIN`, `ARRIVE`, `DEPART` |
| Plaza & Fountain | social | `MARKET`, `BUSK`, `SIT_BENCH`, `MEMORIAL_PAUSE`, `SING` |
| Riverside (bridge, oak) | quiet | `WALK`, `SIT_BENCH`, `SHELTER`, `DOG_CHASE_SQUIRREL` |
| Academy | club | `TRAIN`, `WATCH_FROM_FENCE` |
| Museum | club / quiet | `WORK`(Nora), `VISIT`, `REMEMBER` |
| Stadium gate & forecourt | club | `WORK`(Elias/pitch), `MATCH_GATE_ENTRY`, `GATHER` |
| Grounds / pitch | club (back) | `GROUNDSKEEP` |

## The residents (25–40 persistent)

The **named cast** (~14, from `living-world/residents.md`): the Old Dog, Mrs.
Hana, Elias, Eva, Luca, Otto, Karim, Milo, Nora, Agnes, Victor, Emma, Daniel &
Sofia, the Twins, plus the minor child **Tomas**. To reach 25–40, add **~15–20
minor residents** with lighter authored data (commuters, market traders, a
dog-walker, academy children, museum visitors, away-day arrivals) simulated at
Tier 2/3. Micro-life: the squirrels, cats, the riverside fox.

## Scenario A — ordinary weekday

Residents form intentions from obligations (Hana opens the bakery pre-dawn; Elias
mows), habits (Karim opens with the first train), and relationships (Tomas
*sometimes* looks for the Old Dog; Eva tends the memorial). Encounters occur on
the shared rails; the plaza fills at lunch; the pub fills in the evening; the town
goes quiet at night. Crowd density tracks time of day.

## Scenario B — matchday

`Time` sets `day_type = matchday`. This is a **global schedule transform**, not a
skin: work shifts (Hana at full production; Otto braces the pub), flows converge
on the stadium gate, Karim sells out, Milo leads the plaza song, the Twins are
everywhere, Victor holds court at the café; after the final whistle the town
exhales and the pub becomes the truest place. Away supporters arrive by train
(Tier-3 crowd).

## Scenario C — one disruptive world event

A **sudden severe storm** mid-afternoon (Event Engine + Weather). It closes
outdoor affordances (market, riverside), triggers `SHELTER_FROM_RAIN` intentions,
reroutes residents indoors (bakery, café, pub, museum), cancels the plaza market,
and interrupts in-progress intentions — which must **bend, not break** (defer,
re-route, or substitute). The Old Dog seeks the bakery doorway; Tomas, if
mid-search, gives up believably. When the storm passes, deferred intentions
resume. *(Alternative disruptive event for a later run: a shock result on
matchday. Only one is run per slice.)*

## Persistence across the player's absence

The player leaves; the slice simulates **two weeks at Tier 2/3** (logical, no full
actors). On return: legible changes with **causal history** — e.g. the memorial
has grown, a relationship strength has shifted from repeated encounters, the
Tier-0 milestone has advanced one step, a minor resident's routine changed. Every
change must be explainable via the observability tools. Nothing resets; nobody
vanished silently.

## Fidelity tiers exercised

- **Tier 0** — one protected authored milestone (proves authored beats survive).
- **Tier 1** — full embodiment near the player.
- **Tier 2** — district-logical intentions/encounters without full actors.
- **Tier 3** — background/aggregate (away crowds, distant minor residents).
Residents must promote/demote between tiers without breaking continuity.

## Relationship to the roadmap

This is **Phase 1 ("one convincing day")**, and it presumes **Phase 0**
(contracts, schema, event log, inspector, replay) is already standing — which is
what the rest of WI-01 defines.
