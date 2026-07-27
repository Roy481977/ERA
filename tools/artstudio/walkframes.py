"""
walkframes — DISTRICT 01, Walking the Town.

Twenty consecutive eye-level frames. One ordinary Tuesday, morning to dusk.
The camera is a person: it looks left, looks ahead, stops, sits, looks back.
Nothing is labelled. The town is allowed to hide.

Each frame: (time, note_or_None, az, el, scale, builder).
The builder runs AFTER set_view — projection is per-frame.
"""
import math
import svgkit
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY
from era_lang import (BRK, BRK2, BRK3, RND, RND2, FAS, CONC, TIMD, TIML,
                      TILB, TILG, FELT, GLS, GLSI, DRK, INK,
                      GRN, NVY, RED, ORG, MUS, TEAL, OLV, PNK,
                      nrm, vis, face, mass, slab, rail, win, door)
from charm import hero
from lovable import (base, blob, vdot, hdisc, flowerrow, bench, bicycle,
                     lamppost, postbox, LEAF, LEAF2, WARM, halo, porchlight,
                     awning_striped, fascia_sign, hangingsign, aboard,
                     planters, doormat, windowbox, gardenwall)
from streets import (flags, brickpav, tarmac, grass, kerb, gband, tree,
                     hedgerow, bollard, bin70, belisha, zebra, stall,
                     planter, busstop, shelter, FLAG, FLAGJ, PAVB, PAVBJ)
from places import (oak, wornpath, wornpatch, parishboard, floodlights,
                    barrel, lowwall, WORN)
from walk import house
from district01 import washline

EVE = (246, 210, 130)         # evening glass
C = lambda sc: {"sc": sc, "K": lambda c: c}


# ------------------------------------------------------------- builders
def f01():
    """the gate, morning — bin out, paper waiting"""
    def deco(ctx):
        doormat(ctx)
        windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.7, [RED, MUS])
        gardenwall(ctx, gy=-4.4)
        ctx["F"].rect(ctx["du"] + 0.2, 0.02, 0.5, 0.34, (250, 248, 240),
                      out=0.16, sw=1.0, rad=0.03)
    sc, ctx = house(None, GRN, 0.0, deco=deco)
    bin70(sc, ctx["x0"] + ctx["w"] + 1.4, -4.9)
    flags(sc, -4.6, -6.2, x0=-8.0, x1=18.0)
    tarmac(sc, -6.4, -8.4, x0=-8.0, x1=18.0)
    tree(sc, 12.6, -5.4, s=1.0)
    return sc


def f02():
    """ahead down the lane"""
    sc, _ = house(None, OLV, -3.0)
    house(sc, TEAL, 9.5, yoff=-0.8)
    grass(sc, -0.5, -1.9, x0=-9.0, x1=22.0)
    flags(sc, -1.9, -3.6, x0=-9.0, x1=22.0)
    tarmac(sc, -3.8, -6.4, x0=-9.0, x1=22.0)
    tree(sc, -6.8, -1.3, s=1.15)
    tree(sc, 5.0, -1.3, s=1.05)
    ctx = C(sc)
    bicycle(ctx, 13.4, -2.4, col=RED)
    zebra(sc, 19.5, -3.9, -6.3, w=2.6)
    belisha(sc, 17.6, -3.2)
    return sc


def f03():
    """left: the neighbour's Tuesday"""
    def deco(ctx):
        doormat(ctx)
        planters(ctx)
        windowbox(ctx, 3.45, ctx["bv"] - 0.55, 1.7, [PNK, RED])
    sc, ctx = house(None, NVY, 0.0, deco=deco)
    washline(sc, ctx["x0"] + ctx["w"] + 1.8, -1.4)
    flags(sc, -3.4, -5.0, x0=-7.0, x1=15.0)
    blob(sc, -5.4, -2.4, 0.6, 0.55, LEAF2)
    return sc


def f04():
    """the crossing, close"""
    sc = Scene()
    tarmac(sc, -1.5, -6.5, x0=-7.0, x1=16.0)
    flags(sc, 0.6, -1.5, x0=-7.0, x1=16.0)
    flags(sc, -6.5, -8.2, x0=-7.0, x1=16.0)
    zebra(sc, 3.0, -1.7, -6.3, w=4.2)
    belisha(sc, 0.2, -0.9)
    belisha(sc, 5.8, -7.3)
    house(sc, RED, 2.0, yoff=2.2)
    hedgerow(sc, 7.8, 1.4, 7.0, h=0.8)
    return sc


def f05():
    """the square opens"""
    def deco(ctx):
        fascia_sign(ctx, "BAKERY", MUS, letters=INK)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        porchlight(ctx)
    sc, ctx = house(None, MUS, 0.0, glass=GLSI, deco=deco)
    flags(sc, -0.5, -7.0, x0=-10.0, x1=16.0)
    aboard(ctx, ctx["x0"] + 4.5, -1.7, MUS)
    bench(ctx, -6.6, -3.8)
    bicycle(ctx, 7.6, -1.6, col=TEAL)
    bicycle(ctx, 9.2, -1.55, col=OLV)
    lamppost(ctx, -8.4, -3.2, glow=False)
    return sc


def f06():
    """the warm step — stop"""
    sc = Scene()
    p = base(MUS)
    p["glass"] = GLSI
    ctx = {}
    s2 = hero(p, ctx)
    sc.items += s2.items
    sc.texts += s2.texts
    fascia_sign(ctx, "BAKERY", MUS, letters=INK)
    halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    doormat(ctx)
    mass(sc, ctx["x0"] + 5.9, -0.85, 0, 0.55, 0.4, 0.35, TIML, sw=1.1,
         arris=False)
    flags(sc, -0.5, -5.0, x0=-7.5, x1=8.0)
    aboard(ctx, ctx["x0"] + 4.5, -1.6, MUS)
    return sc


def f07():
    """leaving the square — the board has new paper on it"""
    sc = Scene()
    flags(sc, -0.5, -5.6, x0=-8.0, x1=8.0)
    grass(sc, -0.5, -8.0, x0=8.0, x1=22.0)
    parishboard(sc, 2.4, -2.6)
    wornpath(sc, 8.5, -3.4, 20.0, -4.2, w=1.15)
    oak(sc, 19.5, -3.0, s=1.05)
    ctx = C(sc)
    bicycle(ctx, -4.8, -1.7, col=OLV)
    return sc


def f08():
    """onto the green"""
    sc = Scene()
    grass(sc, 1.0, -9.5, x0=-12.0, x1=18.0)
    wornpath(sc, -10.0, -4.6, 0.0, -4.9, w=1.2)
    wornpath(sc, 2.8, -5.0, 12.0, -4.4, w=1.2)
    wornpatch(sc, [(-1.8, -3.2), (3.4, -3.0), (3.8, -6.8), (-1.4, -7.0)])
    oak(sc, 1.0, -3.6, s=1.45)
    ctx = C(sc)
    bench(ctx, -5.6, -6.4)
    house(sc, PNK, -12.5, yoff=3.5)
    return sc


def f09():
    """sitting. no reason to move."""
    sc = Scene()
    grass(sc, 1.5, -8.0, x0=-9.0, x1=13.0)
    oak(sc, 6.2, -1.8, s=1.5)
    wornpatch(sc, [(3.2, -0.6), (9.4, -0.4), (9.8, -3.8), (3.6, -4.0)])
    ctx = C(sc)
    bench(ctx, -1.4, -3.4)
    blob(sc, -7.4, -2.0, 0.6, 0.5, LEAF2)
    return sc


def f10():
    """left, across the green — someone's washing is up"""
    sc, _ = house(None, OLV, -2.0, yoff=6.0)
    house(sc, TEAL, 10.5, yoff=6.8)
    washline(sc, 6.4, 4.4)
    grass(sc, 8.0, -6.0, x0=-10.0, x1=20.0)
    flags(sc, 5.6, 7.2, x0=-10.0, x1=20.0)
    tree(sc, -7.6, 4.6, s=1.2)
    wornpath(sc, -8.0, -2.0, 18.0, -3.0, w=1.1)
    return sc


def f11():
    """up again — the street narrows ahead"""
    def deco(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
    sc, ctx = house(None, ORG, 4.0, glass=GLSI, deco=deco)
    house(sc, NVY, 16.5, yoff=-0.6)
    grass(sc, -0.5, -2.0, x0=-10.0, x1=8.0)
    brickpav(sc, -0.5, -4.4, x0=8.0, x1=26.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    tarmac(sc, -4.6, -7.0, x0=-10.0, x1=26.0)
    planter(sc, 0.4, -2.9, 2.2, cols=(RED, MUS))
    ctx2 = C(sc)
    lamppost(ctx2, -6.0, -5.2, glow=False)
    return sc


def f12():
    """the high street, mid — everything at once"""
    def cafe(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
    def shop(ctx):
        awning_striped(ctx, NVY)
        fascia_sign(ctx, "STORES", NVY)
    sc, c1 = house(None, ORG, -6.0, glass=GLSI, deco=cafe)
    house(sc, NVY, 6.5, yoff=-0.4, glass=GLSI, deco=shop)
    brickpav(sc, -0.5, -4.2, x0=-13.0, x1=20.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    tarmac(sc, -4.4, -6.8, x0=-13.0, x1=20.0)
    barrel(sc, -9.4, -2.1)
    aboard(c1, -2.6, -2.5, ORG)
    ctx = C(sc)
    bicycle(ctx, 13.6, -1.9, col=RED)
    bin70(sc, 15.8, -2.0)
    return sc


def f13():
    """the caf&#233; window — linger"""
    def cafe(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    sc, ctx = house(None, ORG, 0.0, glass=GLSI, deco=cafe)
    brickpav(sc, -0.5, -4.0, x0=-7.0, x1=9.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    from streets import stall as _stall  # noqa
    from lovable import terrace
    terrace(ctx, ctx["x0"] + 1.6, -2.2)
    aboard(ctx, ctx["x0"] + 5.2, -2.0, ORG)
    return sc


def f14():
    """the market, empty — Tuesday's whole square to yourself"""
    sc = Scene()
    brickpav(sc, 1.0, -8.5, x0=-12.0, x1=18.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    from streets import chalk
    chalk(sc, -6.0, -4.0, 2.6, 1.6)
    def pub(ctx):
        fascia_sign(ctx, "THE HOME END", GRN, ww=ctx["gww"] + 0.55, letters=MUS)
        hangingsign(ctx, GRN, MUS)
    house(sc, GRN, 6.0, yoff=1.0, deco=pub)
    shelter(sc, -10.0, -6.8)
    ctx = C(sc)
    bin70(sc, -1.6, -6.6)
    postbox(ctx, 1.8, -6.2)
    return sc


def f15():
    """the pub, shut till evening — barrels wait"""
    def pub(ctx):
        fascia_sign(ctx, "THE HOME END", GRN, ww=ctx["gww"] + 0.55, letters=MUS)
        hangingsign(ctx, GRN, MUS)
        doormat(ctx)
    sc, ctx = house(None, GRN, 0.0, deco=pub)
    flags(sc, -0.5, -4.6, x0=-7.0, x1=10.0)
    barrel(sc, -3.6, -1.9)
    barrel(sc, -1.2, -2.5)
    planters(ctx)
    return sc


def f16():
    """the lane mouth. not today."""
    sc = Scene()
    floodlights(sc, (9.5, 15.5), y=9.0, h=12.4)
    grass(sc, -0.4, -2.2, x0=-12.0, x1=18.0)
    wornpatch(sc, [(-11.8, -2.3), (17.8, -2.3), (17.8, -4.7), (-11.8, -4.7)],
              col=mix(WORN, FLAG, 0.35))
    grass(sc, -4.8, -7.0, x0=-12.0, x1=18.0)
    hedgerow(sc, -11.6, -2.0, 12.0, h=0.85)
    hedgerow(sc, 2.4, -2.0, 15.0, h=0.85)
    for rx in (-10.4, -4.4, 1.6, 7.6):
        rail(sc, rx, -4.95, 0, 5.4, 0.88, mix(GRN, DRK, 0.35), n=6)
    sc.poly([(3.0, -4.96, 0.60), (3.34, -4.96, 0.60),
             (3.34, -4.96, 0.97), (3.0, -4.96, 0.97)],
            mix(GRN, (200, 200, 195), 0.45), n=NY, rad=0.04, sw=1.0)
    bollard(sc, -9.0, -3.5)
    bollard(sc, 14.6, -3.5)
    return sc


def f17():
    """the bridge instead — lean"""
    sc = Scene()
    grass(sc, -0.4, -2.8, x0=-10.0, x1=16.0)
    from places import stream as _stream
    _stream(sc, -2.8, -7.2, x0=-10.0, x1=16.0)
    grass(sc, -7.2, -9.0, x0=-10.0, x1=16.0)
    from places import bridge as _bridge
    _bridge(sc, -1.5, 5.8, -2.8, -7.2)
    ctx = C(sc)
    bicycle(ctx, 5.4, -2.45, col=MUS)
    vdot(sc, -8.2, -2.5, 2.2, 1.5, LEAF2)
    vdot(sc, -7.0, -2.6, 1.4, 1.0, mix(LEAF2, LEAF, 0.5))
    mass(sc, -7.8, -2.3, 0, 0.22, 0.22, 1.5, mix(TIMD, (90, 70, 50), 0.3),
         sw=1.2, top=False, arris=False)
    return sc


def f18():
    """looking back — just roofs and the tree"""
    sc = Scene()
    grass(sc, 2.0, -6.0, x0=-16.0, x1=16.0)
    house(sc, GRN, -14.0, yoff=8.0)
    house(sc, RED, -3.0, yoff=9.2)
    house(sc, NVY, 8.0, yoff=8.4)
    oak(sc, 1.5, 5.2, s=1.4, scarves=False)
    wornpath(sc, -12.0, -1.0, 14.0, -2.2, w=1.05)
    blob(sc, 12.4, -0.6, 0.65, 0.55, LEAF2)
    return sc


def f19():
    """the lamps come on before you're home"""
    def deco(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    sc, ctx = house(None, ORG, 2.0, glass=EVE, deco=deco)
    house(sc, NVY, 14.5, yoff=-0.6, glass=EVE)
    brickpav(sc, -0.5, -4.2, x0=-11.0, x1=24.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    tarmac(sc, -4.4, -6.8, x0=-11.0, x1=24.0)
    ctx2 = C(sc)
    lamppost(ctx2, -7.0, -2.4, glow=True)
    lamppost(ctx2, 20.0, -2.6, glow=True)
    belisha(sc, -9.6, -3.0)
    return sc


def f20():
    """the gate again — bin in, paper gone, light on"""
    def deco(ctx):
        doormat(ctx)
        windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.7, [RED, MUS])
        gardenwall(ctx, gy=-4.4)
        porchlight(ctx, glow=True)
    sc, ctx = house(None, GRN, 0.0, glass=EVE, deco=deco)
    flags(sc, -4.6, -6.2, x0=-8.0, x1=18.0)
    tarmac(sc, -6.4, -8.4, x0=-8.0, x1=18.0)
    tree(sc, 12.6, -5.4, s=1.0)
    ctx2 = C(sc)
    lamppost(ctx2, 15.4, -5.0, glow=True)
    return sc


FRAMES = [
    ("07:52", None, 44, 6.0, 15.5, f01),
    ("07:56", None, 64, 6.0, 14.5, f02),
    ("07:57", None, 20, 6.0, 16.5, f03),
    ("08:01", None, 58, 5.5, 16.0, f04),
    ("08:04", None, 40, 6.0, 14.5, f05),
    ("08:07", "you can smell it from the corner", 24, 6.0, 19.5, f06),
    ("08:13", None, 55, 6.0, 15.5, f07),
    ("08:16", None, 34, 6.0, 14.0, f08),
    ("08:20", "no reason to move", 34, 3.6, 17.0, f09),
    ("08:31", None, 18, 4.5, 13.5, f10),
    ("10:42", None, 66, 6.0, 14.5, f11),
    ("10:47", None, 44, 6.0, 14.0, f12),
    ("10:52", None, 18, 6.0, 18.5, f13),
    ("10:58", "on Fridays you can&#8217;t see the bricks", 60, 6.0, 13.5, f14),
    ("11:03", None, 28, 6.0, 16.0, f15),
    ("11:09", "not today", 62, 6.0, 14.0, f16),
    ("11:15", None, 38, 5.0, 15.5, f17),
    ("11:22", "from here it&#8217;s just roofs and the tree", 26, 5.0, 13.0, f18),
    ("17:41", None, 55, 6.0, 14.5, f19),
    ("17:48", None, 44, 6.0, 15.5, f20),
]
