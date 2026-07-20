# DS-008 — Social realism: disposition and chosen togetherness

**Status: PROPOSED (implementation tracking).** Under the [Book of ERA](../docs/book-of-era/00-the-promise-and-laws.md)
and [DEV-000](DEV-000-development-constitution.md). Builds on the social layer of
[DS-001](DS-001-first-breath.md) and the behaviour work of [DS-007](DS-007-behaviour-layer.md).

Direction (Roy): *"I would like to try to make the behaviours realistic using
you. Like reality. Bonds are not created in 1 day usually; people and generally
living things relate to each other in a lot of different ways."* And: *"What is
missing to make it feel real? For example — close people will generally start
walking together and doing stuff together. Please find what's not mature enough
here."* On seeing the plan: *"Start there but let's continue to all."* And,
mid-work: *"all the residents don't always have to remain or even reside in town.
You can take also partial paths together and then go separate ways."*

From that, eight maturity gaps were named, to be worked in order:

1. **Chosen togetherness / shared plans** — deciding to do something *together*.
2. Groups (three or more, not just pairs).
3. Mood / energy / sociability — an inner state that shapes the day.
4. Social personality — stable temperament (this turned out to be part of #3).
5. Life events / change over time.
6. The physical language of closeness (spacing, walking pace, sitting near).
7. Seeking and noticing (looking for someone, spotting them across a square).
8. Roles and asymmetry (who leads, who defers).

This document covers the **first increment: #1 and #3/#4**. The rest remain open.

---

## Principle: the sim is the source of truth; the renderer expresses it

Nothing here is faked in the renderer. Disposition and togetherness are computed
in the deterministic simulation; the district (Bevy) and the top-down viewer show
them because the residents' *positions and choices* change. In particular, two
friends who set off together physically occupy the same path nodes — the renderer
shows them side by side for free, through the same steering (spacing, yielding)
that governs every figure.

Everything stays deterministic. Residents draw from **no** random source (only
wildlife uses the seeded RNG). Mood and energy are `f32`, updated in a fixed order,
so a given seed replays identically.

---

## Disposition: sociability, mood, energy

Every resident now carries three new fields (`sim/resident.rs`):

- **`sociability: i32`** — a *stable trait*, set once and never changed. The known
  cast is hand-authored (Milo the busker is +3; Luca, who keeps his corner, is −1);
  any other id derives a stable value in −1..=2 from its bytes, so an arbitrary cast
  still has a spread of temperaments.
- **`mood: f32` (−1..=1)** — how they feel now. Eases toward neutral each tick
  (`*0.98`), lifted by warm encounters (+0.10), dented by a sour one (−0.15). Carries
  a little from day to day.
- **`energy: f32` (~0.05..=1)** — what they have left. Wanes while out (−0.003, a
  little more while travelling), recovers while resting at home (+0.03), reset to
  1.0 each morning. A day therefore has an arc: rested at dawn, spent by evening.

These fold into one dial:

```
social_readiness() = sociability
                   + round(mood   * 3)       // −3..=3
                   + round((energy − 0.5)*4)  // −2..=2
```

Zero is an average person, ordinary mood, half a day's energy. Every social gate
reads this one number, so the same town behaves differently morning vs. night and
person to person: an outgoing pair in good spirits stop to talk far more than two
tired introverts crossing the same square.

**Where it bends behaviour** (`simulation.rs`, `social.rs`, `intention.rs`):
interaction odds (`social::decide` takes a `social_lift`), lingering with a friend,
the detour and reunion gates, and waiting for a friend to finish up — all now bend
to both people's readiness.

## Chosen togetherness — shared outings (gap #1)

Two close friends **at a loose end together** — both idle, out in public, up for
company, no errand pulling them anywhere but home — may *decide* to spend a while
somewhere together (the café, the square) rather than drift off separately. The
agreement is formed in DECIDE, before either decides alone, as a shared intention
to the same destination; RECONCILE then walks them out as a pair:

> *Karim and Milo are close, and neither wants the afternoon to end — they decide
> to head to the Café together* → *sets off with Milo for the Café* → *a while
> together — at the Café.*

Bounded (it is the day's one deviation for each), time-safe (`pick_shared_leisure`
only proposes a place both can reach, enjoy, and get home from before the evening),
and deterministic (a seeded choice, likelier the more up for company the two are).

## Partial shared paths (Roy's mid-work note)

Two friends leaving the same place for **different** destinations, whose shortest
routes share the opening stretch, keep company as far as the fork and then part:

> *Sofia and Elias walk out together to the Main Square, where Sofia stops and
> Elias carries on to the Oakside Cottages.*

Because their paths genuinely coincide on that stretch, this only *recognises and
narrates* what the movement already does — no special-case motion. It is the
cheapest, most frequent form of togetherness, and the one closest to Roy's "take
partial paths together and then go separate ways."

---

## Tests

`tests/disposition.rs` (9): sociability seeding and stability; the daily energy arc
and overnight recovery; mood moving off neutral with encounters; full determinism
of disposition and of togetherness across two runs; outings chosen *and* taken, and
bounded to one per resident per day; partial walks occurring; and — the invariant
that matters — no one ever stranded at 03:00 by an outing or a shared walk. Whole
suite green (85).

---

## Still open (Roy: "continue to all")

Gap #2 groups · #5 life events / change over time · #6 the physical language of
closeness · #7 seeking and noticing · #8 roles and asymmetry. And the larger world
change Roy raised alongside partial paths: **residents who do not only reside in
town** — leaving and returning, an off-map destination — which needs world/navigation
support (an "edge of town" node and an errand that goes through it) rather than only
a behaviour change, so it is its own next step.
