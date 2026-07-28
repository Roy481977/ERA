# Sprint 022 — The Long Light (lighting Priority 2, solved)

**Status: EXECUTED (delivered; PROPOSED pending Roy). Kind: OPERATIONAL.
Simulation untouched. This sprint enacts Book III's "long light" —
"a near-perpetual state of almost-evening: warm windows, lengthening
shadows" — as the district's lighting law.**

## What was built

**The sun stays low.** The solar arc's maximum elevation drops by nearly
half, so even midday light rakes across the town; every hour now throws
long, directional shadows, and the neutral noon key warms from white to
cream. Grey mornings, rain and night remain themselves — the Book keeps
its ordinary days.

**Shadows soften and sharpen at once.** The shadow map doubles to 4096
on tighter bounds with soft-PCF filtering, bias and radius tuned — eave
shadows, awning shadows and tree shade now read as soft-edged and
deep instead of stair-stepped.

**Everything touches the ground.** A radial contact-occlusion blob sits
under every house and shop (with its plinth), every tree, the oak, and
— crucially — every walking resident, who now carries a soft shadow
puck. Nothing floats; the figures sit *in* the scene for the first time.

**Bounced light.** A warm low-intensity fill light mirrors the sun from
the opposite azimuth each frame, and the hemisphere's ground bounce
warms — shade sides are no longer dead grey but carry the ground's
warmth, the cheap-and-honest version of global illumination.

## Success criteria, answered

Warm late-afternoon key with soft, long contact shadows — the arc
change makes it the day's default, verified at 10:40, 16:00 and 20:05.
Deep ambient occlusion around building bases — the AO blobs plus plinth
shadows. Subtle bounced light — the mirrored fill plus warmed ground
bounce. Before/after: Sprint 020's 15:00 frame is flat; the same town
at 16:00 now has every roof drawing its shape on the ground.

## Honest notes

The AO blobs are painterly fakes, not screen-space AO — at very close
range under a house corner the gradient edge can be found if hunted.
The lowered arc slightly dims interiors-of-north-facing frames at noon;
within the Book's intent. The "long light" bias is an aesthetic law
enacted from canon — flagged for Roy's explicit ratification since it
changes every daytime frame.

## Deliverables

`era-town-3d.html` · `longlight_sheet.png` · this record.
