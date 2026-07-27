"""
district01 — the first real piece of an ERA town, built on the ratified
Weave (CD-027). ONE continuous worldspace, production camera (34/19).

The moment: SATURDAY, 13:40 — an hour before kickoff. The market is folding,
the scarves are out, the bikes are pointing north-east.

Axes: x east (0..170), y north (0 nearest the viewer .. 56 furthest).
The daily line runs west-east (crossing · bakery square · green · high
street · market). The weekly line runs south-north-east (homes · the Oak ·
the bridge · the ground). They cross at the Oak.
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
                     planters, doormat, windowbox, gardenwall, gutterwork)
from streets import (flags, brickpav, tarmac, grass, kerb, gband, tree,
                     hedgerow, bollard, bin70, belisha, zebra, stall,
                     planter, busstop, shelter, FLAG, FLAGJ, PAVB, PAVBJ,
                     GRASS, GRASSD)
from places import (oak, wornpath, wornpatch, parishboard, floodlights,
                    barrel, lowwall, stream as streamband, WORN)
from walk import house

CTX = {"sc": None, "K": lambda c: c}


def washline(sc, x, y):
    """a Saturday wash, out the front — evidence of life at district scale"""
    for k in (0.0, 3.2):
        mass(sc, x + k - 0.05, y - 0.05, 0, 0.10, 0.10, 1.85, TIMD, sw=1.0,
             top=False, arris=False)
    sc.line((x, y, 1.80), (x + 1.6, y, 1.62), DRK, sw=1.0, bias=0.25)
    sc.line((x + 1.6, y, 1.62), (x + 3.2, y, 1.80), DRK, sw=1.0, bias=0.25)
    for (k, c, w_, h_) in ((0.4, RND, 0.5, 0.7), (1.1, MUS, 0.45, 0.55),
                           (1.9, TEAL, 0.5, 0.6), (2.6, RND2, 0.4, 0.62)):
        zz = 1.80 - abs(k + 0.25 - 1.6) / 1.6 * 0.18
        sc.poly([(x + k, y - 0.02, zz - h_), (x + k + w_, y - 0.02, zz - h_),
                 (x + k + w_, y - 0.02, zz), (x + k, y - 0.02, zz)], c,
                n=NY, rad=0.06, sw=1.0)


def build():
    # ---------------------------------------------------------- backdrop row
    sc, _ = house(None, OLV, 2 + 5.4, yoff=44)
    house(sc, TEAL, 15 + 5.4, yoff=44.8)
    house(sc, PNK, 27.5 + 5.4, yoff=44)
    washline(sc, 30.5, 42.2)

    # ---------------------------------------------------------- the ground
    floodlights(sc, (152.0, 164.0), y=55.5, h=13.0)
    mass(sc, 142.0, 50.0, 0, 26.0, 7.0, 5.6, BRK, sw=1.8, top=False)
    fst = Face(sc, (142.0, 50.0, 0), X, Z, NY, ref=(155.0, 50.0, 2.8))
    fst.rect(0.0, 4.1, 26.0, 0.45, CONC, sw=1.2, rad=0.05)
    slab(sc, 141.7, 49.6, 5.6, 26.6, 7.8, 0.45, FELT, FAS, ov=0.0)
    fst.rect(9.0, 4.6, 8.0, 0.72, GRN, sw=1.4, rad=0.10)
    sc.text3(fst, 13.0, 4.95, "THE HOME GROUND", 0.44, MUS, weight="700",
             ls=0.10, out=0.06)
    for tx in (146.0, 159.0):
        mass(sc, tx, 47.6, 0, 3.0, 2.4, 2.6, BRK, sw=1.4, top=True,
             tmat=CONC, arris=False)
        tf = Face(sc, (tx, 47.6, 0), X, Z, NY, ref=(tx + 1.5, 47.6, 1.3))
        tf.rect(0.55, 0.0, 0.9, 2.0, GRN, sw=1.4, rad=0.08)
        tf.rect(1.65, 0.0, 0.9, 2.0, GRN, sw=1.4, rad=0.08)

    # ---------------------------------------------------------- grounds
    grass(sc, 0.0, 56.0, x0=-2.0, x1=172.0)                     # the base
    # streets
    tarmac(sc, 15.0, 21.5, x0=-2.0, x1=108.0)
    kerb(sc, 21.51, x0=-2.0, x1=38.0)
    kerb(sc, 21.51, x0=64.0, x1=108.0)
    flags(sc, 11.0, 15.0, x0=-2.0, x1=108.0)                    # south pavement
    flags(sc, 21.5, 30.0, x0=-2.0, x1=10.0)
    flags(sc, 21.5, 30.0, x0=10.0, x1=36.0)                     # bakery square
    brickpav(sc, 21.5, 30.0, x0=64.0, x1=102.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    brickpav(sc, 11.0, 30.0, x0=108.0, x1=131.0,                # market square
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    # the green (deep room in the frontage) — grass already under all
    # stream — a near-straight band with one gentle kink
    sc.poly([(139.5, 4.0, 0.006), (144.0, 4.0, 0.006), (142.0, 30.0, 0.006),
             (144.5, 56.0, 0.006), (140.0, 56.0, 0.006), (137.5, 30.0, 0.006)],
            (147, 176, 194), n=Z, rad=0.4, sw=0, stroke=False, fix=-49.85)
    # stadium lane (worn), pub corner -> bridge -> gates
    wornpath(sc, 128.0, 26.0, 138.0, 31.5, w=3.0)
    wornpath(sc, 142.5, 33.5, 152.0, 46.0, w=3.0)
    # bridge
    brickpav(sc, 29.5, 35.5, x0=137.4, x1=143.2,
             col=mix(PAVB, FLAG, 0.30), j=mix(PAVBJ, FLAGJ, 0.3))
    for px in (137.2, 142.7):
        mass(sc, px, 29.2, 0, 0.36, 7.0, 1.08, BRK, sw=1.3, top=True,
             tmat=CONC, arris=False)
    # worn paths across the green — the Weave's crossing, written in grass
    wornpath(sc, 40.0, 21.5, 50.0, 28.0, w=1.2)                 # from the square
    wornpath(sc, 53.5, 29.0, 64.0, 24.0, w=1.2)                 # to high street
    wornpath(sc, 51.5, 31.5, 52.0, 43.5, w=1.0)                 # north to homes
    wornpatch(sc, [(46.5, 25.0), (56.5, 24.6), (57.0, 32.4), (47.0, 32.8)])

    # ---------------------------------------------------------- buildings
    def bakery(ctx):
        fascia_sign(ctx, "BAKERY", MUS, letters=INK)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        porchlight(ctx)
    _, cbak = house(sc, MUS, 16 + 5.4, yoff=30, glass=GLSI, deco=bakery)
    house(sc, RED, 27.5 + 5.4, yoff=30.6)

    def cafe(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
    _, ccaf = house(sc, ORG, 66 + 5.4, yoff=30, glass=GLSI, deco=cafe)

    def stores(ctx):
        awning_striped(ctx, NVY)
        fascia_sign(ctx, "STORES", NVY)
    house(sc, NVY, 78 + 5.4, yoff=30.5, glass=GLSI, deco=stores)

    def post(ctx):
        fascia_sign(ctx, "POST OFFICE", RED, ww=ctx["gww"] + 1.2)
    house(sc, RED, 90.5 + 5.4, yoff=30, deco=post)

    def pub(ctx):
        fascia_sign(ctx, "THE HOME END", GRN, ww=ctx["gww"] + 0.55, letters=MUS)
        hangingsign(ctx, GRN, MUS)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    _, cpub = house(sc, GRN, 119 + 5.4, yoff=30, glass=GLSI, deco=pub)

    def lived(ctx):
        doormat(ctx)
        windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.7, [RED, MUS])
        planters(ctx)
    house(sc, GRN, 2 + 5.4, yoff=30, deco=lived)                # west lane home

    # ---------------------------------------------------------- the Oak
    oak(sc, 51.5, 28.5, s=1.35)
    CTX["sc"] = sc
    bench(CTX, 46.0, 23.4)
    bench(CTX, 55.2, 23.6)

    # ---------------------------------------------------------- furniture
    parishboard(sc, 37.5, 20.0)                                 # green's herald
    zebra(sc, 32.0, 15.2, 21.3)                                 # the crossing
    belisha(sc, 29.6, 14.2)
    belisha(sc, 34.4, 22.3)
    postbox(CTX, 104.5, 13.2)
    shelter(sc, 109.0, 8.2)
    busstop(sc, 115.4, 8.0)
    bench(CTX, 109.6, 8.6)
    bin70(sc, 118.0, 8.4)
    bollard(sc, 107.0, 16.5)
    bollard(sc, 107.0, 20.5)
    # market: Saturday morning folding — two stalls, one already bare poles
    stall(sc, 110.0, 22.0, col=RED)
    stall(sc, 117.5, 17.5, col=NVY)
    aboard(ccaf, 74.0, 18.6, ORG)
    barrel(sc, 117.2, 26.6)
    barrel(sc, 120.0, 25.4)
    planter(sc, 66.5, 22.6, 2.2, cols=(RED, MUS))
    planter(sc, 97.0, 22.6, 2.0, cols=(PNK, RED))
    lamppost(CTX, 40.0, 13.6, glow=False)
    lamppost(CTX, 88.0, 13.6, glow=False)
    lamppost(CTX, 128.5, 12.4, glow=False)
    bin70(sc, 12.5, 22.6)
    # bikes — all pointing the same way today
    bicycle(CTX, 22.5, 21.0, col=TEAL)
    bicycle(CTX, 24.2, 20.8, col=OLV)
    bicycle(CTX, 111.5, 12.6, col=RED)
    bicycle(CTX, 122.6, 24.6, col=MUS)
    bicycle(CTX, 130.5, 24.0, col=NVY)
    # scarves on the lane rail + the gates rail
    for rx in (130.5, 136.4, 144.0):
        rail(sc, rx, 28.4 + (rx - 130.5) * 0.62, 0, 4.2, 0.88,
             mix(GRN, DRK, 0.35), n=5)
    # the empty north-east corner earns a little green
    tree(sc, 136.0, 13.0, s=1.15)
    blob(sc, 148.5, 12.0, 0.7, 0.62, LEAF2)
    flags(sc, 41.5, 43.9, x0=0.0, x1=40.0)      # the backdrop lane's path
    for (ox, oy) in ((132.4, 29.9), (137.8, 33.3), (144.6, 37.4)):
        sc.poly([(ox, oy - 0.01, 0.58), (ox + 0.34, oy - 0.01, 0.58),
                 (ox + 0.34, oy - 0.01, 0.95), (ox, oy - 0.01, 0.95)],
                GRN, n=NY, rad=0.04, sw=1.0)
        sc.poly([(ox + 0.42, oy - 0.01, 0.58), (ox + 0.76, oy - 0.01, 0.58),
                 (ox + 0.76, oy - 0.01, 0.95), (ox + 0.42, oy - 0.01, 0.95)],
                (240, 238, 230), n=NY, rad=0.04, sw=1.0)
    # foreground: garden walls of the south homes (off-frame), trees, verge
    lowwall(sc, 8.0, 8.6, 14.0, h=0.58)
    lowwall(sc, 26.0, 8.6, 8.0, h=0.58)
    blob(sc, 24.0, 8.2, 0.7, 0.62, LEAF2)
    tree(sc, 70.0, 7.0, s=1.25)
    tree(sc, 94.0, 6.2, s=1.15)
    tree(sc, 45.0, 41.0, s=1.1)                                 # behind green
    hedgerow(sc, 128.0, 23.2, 7.0, h=0.8)
    return sc


# world anchor points for board labels: (x, y, z, label, dx, dy)
LABELS = [
    (23.0, 30.0, 11.0, "BAKERY SQUARE", 0, -14),
    (51.5, 28.5, 13.8, "THE OLD OAK", 4, -16),
    (84.0, 30.0, 11.5, "HIGH STREET", 0, -14),
    (115.0, 14.0, 0.2, "MARKET SQUARE", -16, 34),
    (124.5, 30.0, 11.5, "THE HOME END", 6, -14),
    (113.0, 8.0, 4.6, "BUS STOP", 44, 12),
    (37.5, 20.0, 4.2, "NOTICE BOARD", -52, 14),
    (140.0, 32.5, 2.6, "STADIUM ROAD", 16, 30),
    (155.0, 50.0, 20.0, "THE GROUND", 0, -12),
    (32.0, 15.4, 0.2, "THE CROSSING", -14, 30),
]
