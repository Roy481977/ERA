"""
stylize — the twelve passes of ERA Sheet 02.

Row 1 isolates the axes (one accent per row so colour never confounds the
form). Row 2 is the charm ladder, ending in a deliberate overshoot. Row 3 is
character: different KINDS of playfulness, not amounts.
"""
from era_lang import GRN, NVY, RED, ORG, MUS, TEAL, OLV, PNK
from charm import hero

BASE = dict(chunk=1.0, swell=0.0, belly=0.0, roofk=1.0, ov=0.45, fas=0.34,
            rrad=0.30, wrad=0.11, wins=1.0, doors=1.0, sat=0.0, line=2.2,
            wob=0.0, sag=0.0, awning=False, barge=False, ink=False, accent=GRN)

# the far end of the ladder — deliberately past the target
MAXP = dict(chunk=2.1, swell=0.42, belly=0.0, roofk=1.42, ov=1.35, fas=0.66,
            rrad=0.55, wrad=0.26, wins=1.62, doors=1.42, sat=0.45, line=2.7,
            wob=0.0, sag=0.0, awning=True, barge=True, ink=False, accent=GRN)


def P(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def ladder(t, **kw):
    p = {}
    for k in BASE:
        a, b = BASE[k], MAXP[k]
        if isinstance(a, bool) or not isinstance(a, (int, float)):
            p[k] = a
        else:
            p[k] = a + (b - a) * t
    p["awning"] = t >= 0.70
    p["barge"] = t >= 0.70
    p.update(kw)
    return p


PASSES = [
    # ---- row 1: the axes, isolated (accent held at orange) -------------
    ("S-01", "CONTROL &#183; SHEET 01",
     "the language as delivered — the yardstick, not a contender",
     "all knobs at baseline", P(accent=ORG)),
    ("S-02", "PROPORTION &#183; CHUNK",
     "walls gain weight; plinth, fascia, chimney and canopy thicken",
     "chunk &#215;2.1 &#183; swell 0.16 m", P(chunk=2.1, swell=0.16, accent=ORG)),
    ("S-03", "ROOF &#183; GENEROUS",
     "the roof becomes the character — deep eaves, soft edges, big fascia",
     "eaves 1.35 m &#183; rise &#215;1.42 &#183; soft edge",
     P(roofk=1.42, ov=1.35, fas=0.62, rrad=0.55, chunk=1.2, accent=ORG)),
    ("S-04", "OPENINGS &#183; GENEROUS",
     "bigger glass, wider door, deeper canopy — the house gets a face",
     "windows &#215;1.6 &#183; door &#215;1.4",
     P(wins=1.62, doors=1.42, chunk=1.35, accent=ORG)),

    # ---- row 2: the ladder (accent held at green) ----------------------
    ("S-05", "CHARM +10", "every axis together, gently", "ladder t = 0.25",
     ladder(0.25)),
    ("S-06", "CHARM +20", "the brief's 10&#8211;15% push, all axes at once",
     "ladder t = 0.50", ladder(0.50)),
    ("S-07", "CHARM +30", "past the brief on purpose — testing the ceiling",
     "ladder t = 0.75", ladder(0.75)),
    ("S-08", "CHARM +45 &#183; OVERSHOOT",
     "too far, deliberately — you find the line by crossing it",
     "ladder t = 1.0", ladder(1.0)),

    # ---- row 3: character — kinds of playfulness -----------------------
    ("S-09", "HAND &#183; WOBBLE",
     "nothing quite parallel; ridge sags, chimney off plumb — built by hands",
     "charm +20 &#183; jitter 0.16 m &#183; sag 0.32 m",
     ladder(0.50, wob=0.16, sag=0.32, accent=MUS)),
    ("S-10", "SWOLLEN &#183; CLAY",
     "walls belly outward, edges melt — the loaf-of-bread reading",
     "belly 0.55 m &#183; max rounding",
     ladder(0.45, swell=0.20, belly=0.55, rrad=0.55, wrad=0.30, line=1.8,
            accent=PNK)),
    ("S-11", "COLOUR &#183; SPENT HARD",
     "accent stops being a garnish: door, awning, barge, garage",
     "charm +20 &#183; saturation +0.45",
     ladder(0.50, sat=0.45, awning=True, barge=True, accent=TEAL)),
    ("S-12", "INK &#183; STORYBOOK",
     "a dark drawn line joins the language; the sheet becomes a picture book",
     "charm +25 &#183; uniform ink outline",
     ladder(0.55, ink=True, sat=0.18, accent=RED)),
]
