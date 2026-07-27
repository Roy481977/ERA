"""
district_views — four eye-level views inside District 01, taken at the
camera positions marked V1–V4 on the plan. Ground camera (34/6.5), set by
the board composer. The walker still moves left to right.
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
                     planters, doormat, windowbox)
from streets import (flags, brickpav, tarmac, grass, kerb, gband, tree,
                     hedgerow, bollard, bin70, stall, planter, busstop,
                     shelter, FLAG, FLAGJ, PAVB, PAVBJ)
from places import (oak, wornpath, wornpatch, parishboard, floodlights,
                    barrel, lowwall, WORN)
from walk import house


def v1():
    """V1 — BAKERY SQUARE, 07:10. The notice board heralds the green."""
    def deco(ctx):
        fascia_sign(ctx, "BAKERY", MUS, letters=INK)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        porchlight(ctx)
    sc, ctx = house(None, MUS, -6.5, glass=GLSI, deco=deco)
    house(sc, GRN, -20.5)
    flags(sc, -0.55, -7.2, x0=-26.0, x1=20.0)
    kerb(sc, -7.21, x0=-26.0, x1=20.0)
    aboard(ctx, ctx["x0"] + 4.4, -1.6, MUS)
    bench(ctx, -14.6, -3.6)
    bench(ctx, -10.4, -3.6)
    bicycle(ctx, 2.4, -1.7, col=TEAL)
    parishboard(sc, 8.6, -3.2)                    # the herald at the exit
    grass(sc, -7.4, -9.0, x0=10.0, x1=20.0)       # the green begins
    oak(sc, 17.0, -6.4, s=0.95)                   # seen ahead, not yet reached
    lamppost(ctx, -23.2, -3.2, glow=False)
    return sc


def v2():
    """V2 — THE HIGH STREET. One floodlight in the gap between buildings."""
    def cafe(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    def shop(ctx):
        awning_striped(ctx, NVY)
        fascia_sign(ctx, "STORES", NVY)
    sc, c1 = house(None, ORG, -13.5, glass=GLSI, deco=cafe)
    house(sc, NVY, 1.5, yoff=-0.4, glass=GLSI, deco=shop)
    house(sc, RED, 15.0, yoff=-0.8)
    floodlights(sc, (8.0,), y=11.0, h=12.6)       # the glimpse, in the gap
    brickpav(sc, -0.55, -4.4, x0=-20.0, x1=27.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    kerb(sc, -4.41, x0=-20.0, x1=27.0)
    tarmac(sc, -4.61, -7.0, x0=-20.0, x1=27.0)
    aboard(c1, -10.2, -2.4, ORG)
    barrel(sc, -16.6, -2.2)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, 8.8, -1.9, col=RED)
    bin70(sc, 10.8, -1.9)
    return sc


def v3():
    """V3 — MARKET SQUARE. The pub faces both Friday and Saturday."""
    def pub(ctx):
        fascia_sign(ctx, "THE HOME END", GRN, ww=ctx["gww"] + 0.55,
                    letters=MUS)
        hangingsign(ctx, GRN, MUS)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    sc, ctx = house(None, GRN, 11.0, glass=GLSI, deco=pub)
    brickpav(sc, -0.55, -8.6, x0=-20.0, x1=24.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    stall(sc, -17.0, -4.4, col=RED)
    stall(sc, -11.0, -5.8, col=GRN)
    stall(sc, -5.0, -4.4, col=NVY)
    barrel(sc, 9.0, -2.4)
    barrel(sc, 11.6, -2.9)
    c2 = {"sc": sc, "K": lambda c: c}
    postbox(c2, -0.4, -3.0)
    shelter(sc, 0.8, -7.4)
    busstop(sc, 5.0, -7.6)
    bench(c2, 1.3, -7.15)
    bin70(sc, 6.4, -7.3)
    return sc


def v4():
    """V4 — STADIUM ROAD. The town's quietest street, one hour a fortnight."""
    sc = Scene()
    floodlights(sc, (10.0, 17.5), y=6.5, h=12.8)
    house(sc, GRN, -18.5)                          # the pub's back corner
    grass(sc, -0.4, -2.2, x0=-24.0, x1=26.0)
    wornpatch(sc, [(-23.8, -2.3), (25.8, -2.3), (25.8, -4.9), (-23.8, -4.9)],
              col=mix(WORN, FLAG, 0.35))
    grass(sc, -5.0, -7.4, x0=-24.0, x1=26.0)
    hedgerow(sc, -23.6, -2.0, 16.0, h=0.85)
    hedgerow(sc, -4.4, -2.0, 30.0, h=0.85)
    for rx in (-22.4, -16.4, -10.4, -4.4, 1.6, 7.6, 13.6, 19.6):
        rail(sc, rx, -5.15, 0, 5.4, 0.88, mix(GRN, DRK, 0.35), n=6)
    for (ox, c) in ((2.6, GRN), (3.1, (240, 238, 230)), (3.6, GRN),
                    (14.2, GRN), (14.7, (240, 238, 230))):
        sc.poly([(ox, -5.16, 0.60), (ox + 0.34, -5.16, 0.60),
                 (ox + 0.34, -5.16, 0.97), (ox, -5.16, 0.97)], c, n=NY,
                rad=0.04, sw=1.0)
    bollard(sc, -20.6, -3.6)
    bollard(sc, 23.4, -3.6)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, -12.4, -3.2, col=GRN)
    return sc


VIEWS = [
    ("V1", "BAKERY SQUARE &#183; 07:10",
     "the square opens off the lane; the notice board stands at its exit, and the Oak is already visible beyond",
     v1),
    ("V2", "THE HIGH STREET",
     "compression: awnings nearly touch &#8212; and one floodlight sits exactly in the gap between the stores and the end house",
     v2),
    ("V3", "MARKET SQUARE &#183; THE PUB &#183; THE BUS STOP",
     "the widest floor in town; the pub&#8217;s one door serves Friday and Saturday; arrival lands in the middle of life",
     v3),
    ("V4", "STADIUM ROAD",
     "deliberately plain &#8212; hedges, a rail, two scarves; the quietest street carries the loudest hour",
     v4),
]


def build_view(i):
    return VIEWS[i][3]()
