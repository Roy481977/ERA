"""
walk — ERA Sheet 06, "The Walk Through Town".

One continuous journey, home to the stadium, at a resident's eye height
(view 34/6.5 — set by the composer before building). The resident always
walks LEFT to RIGHT; each panel's exit is the next panel's entrance.

Places are the protagonists. Buildings frame; they never anchor. Every
composition here starts from the void the walker moves through.
"""
import math
import svgkit
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY
from era_lang import (BRK, BRK2, BRK3, RND, RND2, FAS, CONC, TIMD, TIML,
                      TILB, TILG, FELT, GLS, GLSI, DRK, INK,
                      GRN, NVY, RED, ORG, MUS, TEAL, OLV, PNK,
                      nrm, vis, face, mass, slab, rail)
from charm import hero
from lovable import (base, blob, vdot, hdisc, flowerrow, bench, bicycle,
                     lamppost, postbox, LEAF, LEAF2, WARM, halo, porchlight,
                     awning_striped, fascia_sign, hangingsign, aboard,
                     planters, doormat, windowbox, gutterwork)
from streets import (flags, brickpav, tarmac, grass, kerb, gband, tree,
                     hedgerow, bollard, bin70, belisha, zebra, stall,
                     planter, fingerpost, FLAG, FLAGJ, PAVB, PAVBJ, TAR,
                     GRASS, SOIL)
from places import (oak, stream, bridge, wornpath, wornpatch, parishboard,
                    lowwall, floodlights, barrel, WORN)


def house(sc, accent, xoff, yoff=0.0, glass=None, deco=None):
    ctx = {}
    p = base(accent)
    p["xoff"], p["yoff"] = xoff, yoff
    if glass is not None:
        p["glass"] = glass
    s2 = hero(p, ctx)
    if deco:
        deco(ctx)
    if sc is None:
        return s2, ctx
    sc.items += s2.items
    sc.texts += s2.texts
    return sc, ctx


def street_band(sc, x0, x1, road=True):
    flags(sc, -0.55, -2.65, x0=x0, x1=x1)
    kerb(sc, -2.66, x0=x0, x1=x1)
    if road:
        tarmac(sc, -2.86, -5.6, x0=x0, x1=x1)


# ------------------------------------------------------------------ beats
def b1():
    """0:00 — YOUR DOOR. The town starts at a green gate."""
    from lovable import gardenwall
    def deco(ctx):
        doormat(ctx)
        porchlight(ctx, glow=False)
        windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.7, [RED, MUS])
        planters(ctx)
        gardenwall(ctx, gy=-3.6)                          # the gate is the beat
    sc, ctx = house(None, GRN, -1.0, deco=deco)
    flags(sc, -3.8, -5.4, x0=-9.5, x1=27.0)
    kerb(sc, -5.41, x0=-9.5, x1=27.0)
    tarmac(sc, -5.6, -7.6, x0=-9.5, x1=27.0)
    house(sc, NVY, 17.0)
    bin70(sc, ctx["x0"] + ctx["w"] + 1.6, -4.6)          # collection morning
    f = ctx["F"]
    f.rect(ctx["du"] + 0.15, 0.02, 0.5, 0.34, (250, 248, 240), out=0.16,
           sw=1.0, rad=0.03)                              # the paper, waiting
    tree(sc, 13.2, -4.0, s=1.05)
    return sc


def b2():
    """0:30 — THE QUIET STREET. Houses keep a respectful rhythm."""
    sc, _ = house(None, OLV, -8.0)
    house(sc, TEAL, 4.0, yoff=-0.8)
    house(sc, NVY, 16.0, yoff=-1.6)
    grass(sc, -0.55, -1.75, x0=-15.0, x1=27.0)
    flags(sc, -1.75, -3.4, x0=-15.0, x1=27.0)
    kerb(sc, -3.41, x0=-15.0, x1=27.0)
    tarmac(sc, -3.61, -6.2, x0=-15.0, x1=27.0)
    tree(sc, -13.6, -1.15, s=1.15)
    tree(sc, 1.5, -1.15, s=1.2)
    tree(sc, 13.6, -1.9, s=1.1)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, 9.0, -2.2, col=RED)
    return sc


def b3():
    """1:00 — THE BAKERY SQUARE. You smell it before you see it."""
    def deco(ctx):
        fascia_sign(ctx, "BAKERY", MUS, letters=INK)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        porchlight(ctx)
    sc, ctx = house(None, MUS, 0.5, glass=GLSI, deco=deco)
    house(sc, GRN, -14.5)                                  # the square's far wall
    flags(sc, -0.55, -6.8, x0=-20.0, x1=18.0)              # forecourt, no road
    kerb(sc, -6.81, x0=-20.0, x1=18.0)
    tarmac(sc, -7.0, -9.0, x0=-20.0, x1=18.0)
    aboard(ctx, ctx["x0"] + 4.4, -1.6, MUS)
    bench(ctx, -8.0, -3.4)
    bench(ctx, -3.6, -3.4)
    bicycle(ctx, 9.6, -1.6, col=TEAL)
    bicycle(ctx, 11.2, -1.55, col=OLV)
    planter(sc, 13.4, -2.4, 2.2, cols=(RED, MUS))
    lamppost(ctx, -11.6, -3.0, glow=False)
    return sc


def b4():
    """1:30 — UNDER THE OAK. The town holds its breath."""
    sc = Scene()
    grass(sc, -0.4, -8.6, x0=-24.0, x1=22.0)
    house(sc, GRN, -19.0)
    house(sc, NVY, 14.5, yoff=-1.2)
    wornpatch(sc, [(-4.6, -2.6), (2.6, -2.8), (3.0, -6.4), (-4.2, -6.6)])
    wornpath(sc, -14.0, -4.4, -4.0, -4.6, w=1.0)
    wornpath(sc, 3.0, -4.6, 12.0, -4.2, w=1.0)
    oak(sc, -0.8, -4.4, s=1.5)
    ctx = {"sc": sc, "K": lambda c: c}
    bench(ctx, -6.4, -6.2)
    return sc


def b5():
    """1:55 — THE SMALL BRIDGE. The water asks you to pause."""
    sc = Scene()
    grass(sc, -0.4, -3.4, x0=-16.0, x1=24.0)
    stream(sc, -3.4, -7.6, x0=-16.0, x1=24.0)
    grass(sc, -7.6, -9.2, x0=-16.0, x1=24.0)
    house(sc, TEAL, 14.5)
    bridge(sc, -2.5, 5.8, -3.4, -7.6)
    wornpath(sc, -12.0, -2.0, -2.6, -2.8, w=1.1)
    wornpath(sc, 4.0, -8.0, 13.0, -8.6, w=1.1)
    # willows lean over the water
    vdot(sc, -11.8, -3.2, 2.4, 1.6, LEAF2)
    vdot(sc, -10.6, -3.3, 1.5, 1.1, mix(LEAF2, LEAF, 0.5))
    mass(sc, -11.4, -3.0, 0, 0.24, 0.24, 1.6, mix(TIMD, (90, 70, 50), 0.3),
         sw=1.2, top=False, arris=False)
    vdot(sc, 9.4, -3.1, 1.9, 1.25, LEAF)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, 0.2, -3.05, col=MUS)                    # left mid-errand
    lamppost(ctx, 4.1, -3.1, glow=False)
    return sc


def b6():
    """2:20 — THE HIGH STREET. Colour arrives all at once."""
    def cafe(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    def shop(ctx):
        awning_striped(ctx, NVY)
        fascia_sign(ctx, "STORES", NVY)
    sc, c1 = house(None, ORG, -7.5, glass=GLSI, deco=cafe)
    house(sc, NVY, 5.5, yoff=-0.5, glass=GLSI, deco=shop)
    brickpav(sc, -0.55, -4.6, x0=-14.0, x1=26.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    kerb(sc, -4.61, x0=-14.0, x1=26.0)
    tarmac(sc, -4.81, -7.2, x0=-14.0, x1=26.0)
    barrel(sc, -10.4, -2.2)
    aboard(c1, -4.4, -2.4, ORG)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, 16.4, -1.8, col=RED)
    bin70(sc, 18.6, -1.9)
    lamppost(ctx, -12.8, -2.3, glow=False)
    return sc


def b7():
    """2:45 — THE MARKET SQUARE. Friday's whole town in forty metres."""
    sc = Scene()
    brickpav(sc, -0.55, -8.4, x0=-18.0, x1=24.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    house(sc, RED, -13.5)
    stall(sc, -5.6, -4.2, col=RED)
    stall(sc, 0.4, -5.6, col=GRN)
    stall(sc, 6.4, -4.2, col=NVY)
    parishboard(sc, 13.2, -3.0)
    ctx = {"sc": sc, "K": lambda c: c}
    postbox(ctx, 16.2, -2.6)
    tree(sc, 19.6, -2.0, s=1.15)
    bench(ctx, 11.0, -6.6)
    return sc


def b8():
    """3:05 — THE LANE. You hear the ground before you see it."""
    sc = Scene()
    floodlights(sc, (14.0, 20.5), y=7.5, h=12.2)
    house(sc, GRN, -16.5)
    grass(sc, -0.4, -2.2, x0=-22.0, x1=26.0)
    wornpatch(sc, [(-21.8, -2.3), (25.8, -2.3), (25.8, -4.9), (-21.8, -4.9)],
              col=mix(WORN, FLAG, 0.35))
    grass(sc, -5.0, -7.6, x0=-22.0, x1=26.0)
    hedgerow(sc, -21.6, -2.0, 18.0, h=0.85)
    hedgerow(sc, -1.4, -2.0, 27.0, h=0.85)
    for rx in (-20.4, -14.4, -8.4, -2.4, 3.6, 9.6, 15.6, 21.6):
        rail(sc, rx, -5.15, 0, 5.4, 0.88, mix(GRN, DRK, 0.35), n=6)
    for (ox, c) in ((4.8, GRN), (5.3, (240, 238, 230)), (5.8, GRN),
                    (12.4, GRN), (12.9, (240, 238, 230))):
        sc.poly([(ox, -5.16, 0.60), (ox + 0.34, -5.16, 0.60),
                 (ox + 0.34, -5.16, 0.97), (ox, -5.16, 0.97)], c, n=NY,
                rad=0.04, sw=1.0)
    bollard(sc, -18.6, -3.6)
    bollard(sc, 23.4, -3.6)
    return sc


def b9():
    """3:20 — THE GROUND. Everyone you passed is walking the same way."""
    sc = Scene()
    floodlights(sc, (-6.0, 16.0), y=6.8, h=13.0)
    # the stand: one long, honest brick wall — no spectacle
    mass(sc, -14.0, 0.0, 0, 34.0, 8.0, 6.2, BRK, sw=2.2, top=False)
    f = Face(sc, (-14.0, 0.0, 0), X, Z, NY, ref=(3.0, 0.0, 3.1))
    f.rect(0.0, 4.6, 34.0, 0.5, CONC, sw=1.4, rad=0.05)
    slab(sc, -14.3, -0.4, 6.2, 34.6, 8.6, 0.5, FELT, FAS, ov=0.0)
    f.rect(13.2, 5.15, 7.6, 0.78, GRN, sw=1.6, rad=0.10)
    sc.text3(f, 17.0, 5.5, "THE HOME GROUND", 0.44, MUS, weight="700",
             ls=0.10, out=0.06)
    # turnstile huts
    for tx in (-9.0, 7.4):
        mass(sc, tx, -2.6, 0, 3.0, 2.6, 2.7, BRK, sw=1.6, top=True,
             tmat=CONC, arris=False)
        tf = Face(sc, (tx, -2.6, 0), X, Z, NY, ref=(tx + 1.5, -2.6, 1.4))
        tf.rect(0.55, 0.0, 0.9, 2.05, GRN, sw=1.6, rad=0.08)
        tf.rect(1.65, 0.0, 0.9, 2.05, GRN, sw=1.6, rad=0.08)
        tf.rect(0.55, 2.18, 2.0, 0.34, FAS, sw=1.2, rad=0.05)
    flags(sc, -2.6, -6.8, x0=-20.0, x1=22.0)
    for rx in (-16.4, -12.9, 1.2, 4.7, 12.4, 15.9):
        rail(sc, rx, -5.4, 0, 3.2, 0.95, DRK, n=4)
    for (ox, c) in ((2.0, GRN), (2.5, (240, 238, 230)), (13.2, GRN)):
        sc.poly([(ox, -5.41, 0.62), (ox + 0.34, -5.41, 0.62),
                 (ox + 0.34, -5.41, 1.0), (ox, -5.41, 1.0)], c, n=NY,
                rad=0.04, sw=1.0)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, -18.2, -3.4, col=GRN)
    bicycle(ctx, -19.6, -3.3, col=NVY)
    bin70(sc, 19.4, -3.4)
    return sc


BEATS = [
    ("1", "0:00", "YOUR DOOR", "quiet",
     "the paper on the step, the bin at the kerb &#8212; Tuesday is already written", b1),
    ("2", "0:30", "THE QUIET STREET", "rhythm",
     "houses keep time; trees carry the beat; nothing asks for attention", b2),
    ("3", "1:00", "THE BAKERY SQUARE", "warmth",
     "the road steps back, the forecourt opens &#8212; you smell it before you see it", b3),
    ("4", "1:30", "UNDER THE OAK", "breath",
     "the widest, emptiest moment of the walk &#8212; buildings retreat to the edges", b4),
    ("5", "1:55", "THE SMALL BRIDGE", "pause",
     "parapet at leaning height; the one stop that needs no excuse", b5),
    ("6", "2:20", "THE HIGH STREET", "colour",
     "compression after the green &#8212; awnings, signs, and both accents at once", b6),
    ("7", "2:45", "THE MARKET SQUARE", "gathering",
     "the second opening, social this time &#8212; stalls, notices, the pillar box", b7),
    ("8", "3:05", "THE LANE", "anticipation",
     "hedges narrow, houses fall away, scarves multiply &#8212; you hear it first", b8),
    ("9", "3:20", "THE GROUND", "arrival",
     "an honest brick wall, two turnstiles, lights overhead &#8212; no spectacle needed", b9),
]


def build_beat(i):
    return BEATS[i][5]()
