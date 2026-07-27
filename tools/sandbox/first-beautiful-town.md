# THE FIRST BEAUTIFUL TOWN — Phase 13 run record

**Status: PROPOSED.** Every artistic decision below awaits Roy. The simulation
was not touched — the year, the lives, and the record are byte-identical to
Phase 12. Everything here is presentation: the same town, finally lit and
dressed the way it deserves.

---

## What was built (two passes, one intention)

### Pass one — the camera learns to love the town

The whole rendering pipeline was replaced. Filmic tone mapping (ACES) with
proper colour management ended the washed-out pastel of the blockout era —
brick is now brick-red, the greens are deep, whites are cream rather than
glare. A real sun now travels the sky: it rises low in the east, throws long
morning shadows down Market Street, stands high and neutral at noon, and
comes back low and golden after eight in the evening. The sky is painted by
the hour — warm at the shoulders of the day, deep navy at night. Fog holds
the horizon without milking the middle distance. The grass has grain now
instead of being a flat green screen.

### Pass two — the heroes become unforgettable

**The oak** was rebuilt: nine lobes, a root flare you could sit against, and
one long bough reaching over the worn path — with a rope swing hanging from
it. The swing is not decoration: the first young child at the green takes it,
and it sways. **The bakery** gained a cross-gable wing and, on working
mornings, steam rising from the ridge while the bakers are in — visible from
the street until mid-morning. **The bridge** is now a humpback stone arch:
the barrel straddles the actual river line, the water passes through a true
arch opening, the parapets follow the hump — and residents *rise over it* as
they cross, so a matchday crowd crests the bridge in silhouette. **The
ground** declares itself: A T H L E T I C in painted capitals above the
stand roof, facing the town, readable from Bridge Road exactly where the
Phase-12 reveal delivers walkers; corner flags at the pitch. **The pub**
gained planters and its outside bench. **The houses** hang washing out on dry
days — lines behind the houses (away from whichever road each house faces),
cloths swaying, gone by evening and never out in rain. **Night** finally
behaves: ambient falls to moonlight blue, street lamps drop warm pools on
Market Street and Bridge Road only, and lived-in windows glow amber — the
brightest things in town after dark, exactly as CD-025 wants.

## What verification caught (and fixed, this phase)

Honest inspection of the first hero build found five defects, all repaired:
the night scene was as bright as an overcast noon under a black sky (ambient
was never graded down — now it is, and night exists); the ATHLETIC board
faced away from everyone (now it faces the town and the bridge approach);
the first bridge arch read as a solid dome beached beside the water, and the
bridge itself missed the river line by four metres (the barrel now spans the
computed river crossing, with a real opening); laundry lines stood in front
gardens on north-facing houses (they now hang behind, per house facing); and
the golden-hour window opened too late to be seen (widened).

## Creative Director review — the emotional qualities

Judged against the Constitution's two-question test, in order.

**"I want to live there."** The night frame is the first ERA image that
produces this sentence unprompted: dark street, three pools of lamplight, a
lit window, one resident walking home. The matchday frame — bunting overhead,
a knot of scarved neighbours mid-street — is the second. The golden-hour
green and the steam over the bakery ridge are quieter but carry the same
signal: *someone keeps this place*. The morning long-shadow pass gives even
the fixed three-quarter view a time of day, which it never had.

**"I wonder who these people are."** The swing answers it best: a child on a
rope swing under the big tree is a person, not an agent. Washing behind the
houses implies mornings we never see. The crowd cresting the humpback bridge
on a Saturday is the town's whole football story in one silhouette.

**Screenshot identity test.** The night, matchday, and bridge frames could
not be from another game: green-and-white bunting, a red pillar box, a
humpback bridge with ATHLETIC beyond it. The daytime fixed cameras are
recognisably ERA but not yet arresting — see the critique.

## Honest critique — what still prevents "desperately want to inhabit"

Held to the Nintendo / Team ASOBI / Tiny Glade standard, the gap is real:

The residents are the weakest link now. The capsule figures read as warm
tokens, not lovable characters — no faces, no hands, no silhouette variety
beyond height and colour. The Constitution asks for iconic and expressive;
these are neither yet. This is the single highest-value next investment.

Golden hour is warm but not magic. The light goes amber; it does not yet
*rake* — no rim light on figures, no long tree shadows across the green at
20:00 because shadow softness and sun elevation flatten together. The gap
between our golden frame and a Tiny Glade golden frame is mostly shadow
quality and bloom, neither of which the current renderer attempts.

Materials are one flat tone per surface. No brick courses, no roof texture,
no window reflections. The Museum's cut-not-moulded language survives scale
honestly, but close-up frames want at least a hint of surface life.

The ground between things is still too empty. The grass has grain but no
daisies, no verge, no ditch, no fence lines between fields; middle distance
in wide shots reads as untextured lawn. Depth in the canon camera needs
foreground interest it does not have.

Steam is honest but shy — a plume you believe rather than notice. It should
be the first thing your eye finds at 07:30, and it is the third or fourth.

None of this is structural. The palette, the massing, the light direction,
and the living layer underneath are now pulling together; what remains is
craft density — characters, shadow quality, surface life, ground cover — each
of which can be a future iteration's noticeable leap without touching canon.

## Deliverables

`era-town-3d.html` — the beautiful town, living engine intact.
`beautiful_before_after.png` — four fixed cameras, before and after.
`beautiful_heroes.png` — eight hero frames: oak & swing, bakery steam,
golden hour, night, matchday, the humpback bridge, ATHLETIC, washing out.
