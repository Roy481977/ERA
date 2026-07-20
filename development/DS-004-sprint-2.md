# DS-004 — Sprint 2: A Town You Recognise (progress)

**Status: PROPOSED (implementation tracking).** Sprint 2 works under
[`DEV-000`](DEV-000-development-constitution.md), climbing the **Ladder of Life**
from where Sprint 1 left off (the world exists, residents act and remember): making
**memory and relationships change behaviour** (rung 4–5) and become **observable**
without numbers. Small reviewable commits; determinism preserved.

Guiding tests from DEV-000: does it improve the engine? does it improve the lived
experience? If a change can't be observed, it isn't done.

---

## Step 1 — Relationships become visible through behaviour ✅

**What became more alive:** you can now *see* who is close to whom without being
told a number. Close friends who find themselves together **stay a little longer** —
Hana lingers with Sofia at the bakery, Victor and Luca over coffee — and, watched
across a month, each resident's **signature habit** and the town's **bonds and
gathering places** surface on their own.

**Implemented:**

- **Lingering (behaviour changed by a relationship).** When a resident's activity
  is ending at a public place and a close friend (affinity ≥ 3) is present, they
  extend their stay — logged as behaviour ("lingers a little longer, enjoying
  Sofia's company"). Bounded (≤ 2 extra ticks/resident/day, daytime only) so the
  day stays coherent and no one is stranded.
- **The `chronicle` observer.** `cargo run -- chronicle` watches the town for a
  month and reports, as behaviour not numbers: what each resident is *known for*
  (their most-repeated daytime pursuit and when), who *keeps finding each other*
  and where, where the town *gathers*, and the weekly matchday *rhythm*. This is
  DEV-000's success test — watch without touching the controls and start telling
  stories.

**Files changed:** `sim/resident.rs` (`lingered_today`), `sim/simulation.rs`
(`linger_with_friend` in the Performing branch), `main.rs` (`chronicle` mode),
`tests/companionship.rs` (new).

**Architectural choices:** lingering reuses the start-of-tick presence snapshot and
the relationships store — no new system, no lookahead, no architecture change. The
chronicle derives everything from already-recorded structured data (interactions,
Oak history) and the event log.

**Tests added (4):** friends linger; bounded per day; deterministic; never
stranded. **38 tests total.**

**Known limitations:** lingering is the only relationship-driven behaviour so far;
deeper companionship — *waiting for* a friend and *leaving together* — needs each
resident to know others' intended next destination, i.e. a "decide-then-act"
two-phase tick. That is an architectural evolution (it also underpins group
movement and emergent traditions), so it is flagged for a decision rather than
built silently.

**Commands:** `cargo run -- chronicle` · `cargo test`

---

## Step 2 — Decide-then-act tick + companionship ✅

**Decision:** Roy chose to evolve the tick (over staying single-pass) so residents
can coordinate. This was the arc's first *architectural* change.

**What became more alive:** friends now move through the town *together*. Agnes and
Eva leave for the riverside side by side; Luca and Victor walk home together after
the café; Elias waits a moment for Agnes, Hana for Sofia. "Victor waited for
Elias" is real — and it emerges from world state (who's here, who's close, where
they're bound), not a script.

**Implemented:** the core tick became **four phases** — *advance* (continue what
you're doing), *decide* (every idle resident forms an intention without moving),
*reconcile* (companionship: close friends co-located and bound the same way leave
together; a resident waits, bounded, for a close friend just finishing up), *act*
(apply intentions). All prior behaviour (routines, deviations, matchday, lingering,
Oak, social) is preserved exactly — verified by the unchanged tests — because
cross-resident reads already used the start-of-tick snapshot.

**Files changed:** `sim/simulation.rs` (four-phase `step`, `Intent`/`Coord`,
`reconcile_companionship`), `sim/resident.rs` (`waited_today`), `main.rs` (chronicle
"who walks together"), `tests/companionship.rs` (+4).

**Architectural choices:** decide-then-act is now the tick's shape — the seam every
future coordinated behaviour (meeting up, group traditions, saving a seat) will use.
Companionship thresholds: affinity ≥ 3; wait only for a friend with one tick left;
≤ 2 waits/resident/day. Deterministic (stable order throughout).

**Tests added (4):** friends set off together; residents wait for a friend; waiting
bounded per day; companionship deterministic. **42 tests total.**

**Known limitations:** waiting is a short, hopeful pause (the friend may still go
elsewhere — read as "waited a moment for them"); companionship is pairwise, not yet
group-sized; no "save a seat"/greeting-across-the-square yet.

**Commands:** `cargo run` (watch the timeline) · `cargo run -- chronicle` (see
"Who walks together") · `cargo test`

---

## Step 3 — Social memory & continuity between residents ✅

**Direction (Roy):** postpone formal traditions; first give residents *social
continuity* — remembering shared experiences with specific others and letting that
history change future behaviour. Traditions should later *emerge* from this, not be
minted when a counter crosses a threshold.

**What became more alive:** the town now has a past between people. Encounters that
began as cool nods **warm up** as history accumulates — Karim and Milo, once
strangers on the square, now "share a word of encouragement — old friends, and it
shows." And residents act on memory: someone will **drift to a shared place**,
"half-expecting to find" a friend, because it's where they always meet. Places take
on meaning from what happened there ("the Main Square has become Eva and Karim's
place").

**Implemented:**

- **Shared bonds store** (`social::Bonds` / `SharedBond`): per pair, how often
  they've met, *where* (tallied → their "usual place"), and when last. One owner;
  recorded on every interaction. Distinct from the affinity/trust summary.
- **Familiarity warms encounters.** `decide` now takes the pair's meeting count;
  past meetings add warmth (capped) on top of affinity, raising both the chance of
  stopping and the warmth of what passes — and the reason names it ("old friends,
  and it shows"). Memory changing behaviour, shown as behaviour.
- **Reunion at a usual place** (`intention::consider_reunion`): when winding down,
  a resident with a strong shared place (≥ 6 remembered meetings) may head there on
  the memory of it, expecting — not knowing — a friend might be there. Bounded
  (shares the one-deviation-a-day cap), deterministic, never strands anyone.

**Files changed:** `sim/social.rs` (`Bonds`/`SharedBond`, familiarity in `decide`),
`sim/intention.rs` (`consider_reunion`), `sim/simulation.rs` (bonds field, record
meetings, familiarity + reunion wiring), `sim/mod.rs`, `main.rs` (chronicle "Signs
of continuity"), `tests/social_memory.rs` (new).

**Architectural choices:** affinity/trust remains the fast summary; the bond store
holds the *texture* (where, how often) the summary can't. Behaviour reads the
texture. No thresholds mint traditions — the engine only records and lets patterns
show; hardening them into named traditions stays future work, on purpose.

**Tests added (5):** shared history accumulates; familiarity warms encounters;
residents return to a shared place; deterministic; never stranded. **47 tests
total.**

**Known limitations:** "warmth" is derived from meeting count (not yet from the
*quality* of specific remembered events); reunion expects but can't yet *arrange*
to meet (no promises/plans); memory doesn't fade.

**Commands:** `cargo run -- chronicle` (see "Signs of continuity") · `cargo test`

---

## Step 4 — The old dog (deepening the district, Book IV) ✅

**Direction (Roy):** under the Book of ERA, deepen the existing district before
expanding; choose the feature that most increases the feeling of a living place.
Priority #1 was the old dog.

**What became more alive:** the district now has a life in it that owes the player
nothing. The old dog keeps his own rounds — the café door in the morning where they
set down water, a warm patch on the square at midday, the shade outside the Club in
the afternoon, and the Old Oak by evening — and the child, Tomas, has come to know
him, a bond that deepens through repeated quiet meetings. He ages: his movement
slows, and as he grows old he gives up the long walk to the Club and keeps closer to
the Oak.

**Implemented:** `sim/dog.rs` — the dog as a persistent, ambient presence with his
own daily rhythm and preferred places, a bond with the child that grows through
co-located moments (seeded — "they sometimes find one another"), and gentle ageing
that changes his route. He is **not a resident** (no job, no home, no end-of-day
duty), grants nothing, and is not a quest or mechanic. Deterministic. The observer
gains a `dog` view and he appears in the timeline, occupancy, and chronicle.

**Files changed:** `sim/dog.rs` (new), `sim/simulation.rs` (dog field + `dog_pass`),
`sim/mod.rs`, `main.rs` (`dog` view, occupancy, chronicle line), `tests/dog.rs`
(new). The Book's implementation-status note was updated honestly.

**Architectural choices:** the dog is his own small entity beside the residents, not
forced into the resident model; his route is a pure function of time and age
(weather/noise hooks noted for later); the child-bond is recorded but never surfaced
as a score — only its moments are shown.

**Tests added (5):** he keeps a daily rhythm; he is not a resident; the child comes
to know him; he ages and roams less; deterministic. **52 tests total.**

**Known limitations / deliberately deferred:** his death and its aftermath (the
bowl that remains, the child still looking, the Oak feeling emptier); weather and
noise shaping his route (pending weather); his ageing cadence is compressed for
observability.

**Commands:** `cargo run -- dog` · `cargo run` (he's in the timeline) · `cargo test`

---

## Next candidates (climbing the ladder)

Per Roy's ordering (deepen the district): **weather & atmosphere** (rain, changing
light, fog, seasonal feeling, and their effect on routines and appearance) → then
**micro-life** (birds, cats, foxes) → then **physical continuity** (scarves
remaining, flowers, matchday litter, muddy paths, lit windows — signs of yesterday).
Also still open from earlier: meaningful-event memory weighting; plans/expectations;
and emergent (described, never minted) traditions.
