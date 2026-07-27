"""
places — ERA Sheet 05, "Places You Remember".

Twelve public places that could only exist in an ERA town. Not landmarks —
gathering points. Every tile answers one question: why do people naturally
stop here? Built entirely from the locked vocabulary: the hero building,
Sheet 03's acts of care, Sheet 04's street ground. Football exists quietly
in the background where it belongs.
"""
import math
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY, depth as _d
from era_lang import (BRK, BRK2, BRK3, RND, RND2, FAS, CONC, TIMD, TIML,
                      TILB, TILG, FELT, GLS, GLSI, DRK, INK,
                      GRN, NVY, RED, ORG, MUS, TEAL, OLV, PNK,
                      nrm, vis, face, mass, slab, rail)
from charm import hero, satf
from lovable import (base, blob, vdot, hdisc, flowerrow, bench, bicycle,
                     lamppost, postbox, LEAF, LEAF2, WARM, pad, halo,
                     porchlight, awning_striped, fascia_sign, hangingsign,
                     aboard, terrace, planters, bracketlamp, doormat,
                     windowbox)
from streets import (flags, brickpav, tarmac, grass, kerb, gband, tree,
                     hedgerow, bollard, bin70, belisha, zebra, busstop,
                     shelter, stall, planter, fingerpost, chalk,
                     FLAG, FLAGJ, PAVB, PAVBJ, TAR, KERBC, GRASS, GRASSD,
                     SOIL, XA, XB)

WORN = (191, 172, 138)      # worn earth — the town's signatures
WATER = (147, 176, 194)


def H(accent, glass=None, deco=None, xoff=0.0):
    ctx = {}
    p = base(accent)
    if glass is not None:
        p["glass"] = glass
    p["xoff"] = xoff
    sc = hero(p, ctx)
    if deco:
        deco(ctx)
    return sc, ctx


def wornpatch(sc, pts, col=WORN):
    sc.poly([(x, y, 0.010) for (x, y) in pts], col, n=Z, rad=0.55, sw=0,
            stroke=False, fix=-49.75)


def wornpath(sc, x0, y0, x1, y1, w=0.9):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    wornpatch(sc, [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                   (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])


def oak(sc, x, y, s=1.0, scarves=True):
    """the Old Oak — trunk with weight, canopy with age, scarves with memory"""
    tk = mix(TIMD, (84, 66, 48), 0.42)
    # a trunk that tapers, and one low bough
    sc.poly([(x - 0.55 * s, y - 0.30 * s, 0), (x + 0.55 * s, y - 0.30 * s, 0),
             (x + 0.30 * s, y - 0.30 * s, 3.0 * s),
             (x - 0.30 * s, y - 0.30 * s, 3.0 * s)], tk, n=NY, rad=0.18, sw=1.8)
    sc.poly([(x + 0.22 * s, y - 0.28 * s, 2.0 * s),
             (x + 1.55 * s, y - 0.28 * s, 3.1 * s),
             (x + 1.15 * s, y - 0.28 * s, 3.35 * s),
             (x + 0.10 * s, y - 0.28 * s, 2.5 * s)], tk, n=NY, rad=0.10, sw=1.4)
    for (ox, oz, r, c) in ((0.0, 5.6, 3.4, LEAF), (-2.4, 4.4, 2.3, LEAF2),
                           (2.5, 4.7, 2.4, mix(LEAF, (255, 255, 230), 0.10)),
                           (0.6, 7.4, 2.0, mix(LEAF, (255, 255, 235), 0.16)),
                           (-1.2, 6.9, 1.6, LEAF2),
                           (1.7, 6.6, 1.5, mix(LEAF2, LEAF, 0.5))):
        vdot(sc, x + ox * s, y - 0.10, oz * s, r * s, c)
    if scarves:
        for (ox, oz, c) in ((-0.34, 1.15, GRN), (0.02, 1.75, (240, 238, 230)),
                            (0.30, 0.85, GRN), (-0.10, 2.35, RED),
                            (0.95, 2.55, GRN)):
            sc.poly([(x + ox * s - 0.11, y - 0.32 * s, oz),
                     (x + ox * s + 0.11, y - 0.32 * s, oz),
                     (x + ox * s + 0.11, y - 0.32 * s, oz + 0.42),
                     (x + ox * s - 0.11, y - 0.32 * s, oz + 0.42)],
                    c, n=NY, rad=0.05, sw=1.1)


def stream(sc, y0, y1, x0=XA, x1=XB):
    gband(sc, y0, y1, WATER, scol=mul(WATER, 0.9), x0=x0, x1=x1, rad=0.14)
    for k in (0.3, 0.62):
        yy = y0 + (y1 - y0) * k
        sc.line((x0 + 1.2, yy, 0.006), (x1 - 1.2, yy + 0.25, 0.006),
                mix(WATER, (255, 255, 255), 0.35), sw=1.3, fix=-49.8, op=0.7)


def bridge(sc, bx, bw, sy0, sy1):
    brickpav(sc, sy0 - 0.8, sy1 + 0.8, x0=bx, x1=bx + bw,
             col=mix(PAVB, FLAG, 0.30), j=mix(PAVBJ, FLAGJ, 0.3))
    ylo = min(sy0, sy1)
    for px in (bx, bx + bw - 0.36):
        mass(sc, px, ylo - 0.95, 0, 0.36, abs(sy1 - sy0) + 1.9, 1.12, BRK,
             sw=1.6, top=True, tmat=CONC, arris=False)


def floodlights(sc, xs, y=8.6, h=10.6):
    """the ground's lights, over the rooftops — football in the background"""
    for x in xs:
        mass(sc, x - 0.11, y - 0.11, 0, 0.22, 0.22, h, (98, 100, 104),
             sw=1.1, top=False, arris=False)
        sc.line((x - 0.55, y, h - 1.6), (x, y, h - 0.4), (98, 100, 104),
                sw=1.6, bias=0.05)
        sc.line((x + 0.55, y, h - 1.6), (x, y, h - 0.4), (98, 100, 104),
                sw=1.6, bias=0.05)
        mass(sc, x - 0.80, y - 0.07, h, 1.60, 0.14, 1.00, (66, 68, 72),
             sw=1.1, arris=False)
        for i in range(4):
            for j in range(2):
                vdot(sc, x - 0.57 + i * 0.38, y - 0.12, h + 0.28 + j * 0.44,
                     0.13, (252, 240, 186))
        vdot(sc, x, y - 0.14, h + 0.5, 1.15, (252, 240, 186), op=0.16)


def barrel(sc, x, y):
    mass(sc, x - 0.30, y - 0.30, 0, 0.60, 0.60, 0.88, mix(TIMD, TIML, 0.3),
         sw=1.4, top=True, tmat=mix(TIMD, TIML, 0.5), arris=False)
    sc.line((x - 0.29, y - 0.31, 0.28), (x + 0.29, y - 0.31, 0.28), DRK,
            sw=1.3, bias=0.3)
    sc.line((x - 0.29, y - 0.31, 0.62), (x + 0.29, y - 0.31, 0.62), DRK,
            sw=1.3, bias=0.3)


def parishboard(sc, x, y):
    """freestanding notice board with its own little roof — the town's front page"""
    for k in (-0.75, 0.75):
        mass(sc, x + k - 0.06, y - 0.06, 0, 0.12, 0.12, 2.05, TIMD, sw=1.1,
             top=False, arris=False)
    f = Face(sc, (x - 0.85, y - 0.07, 0.95), X, Z, NY, ref=(x, y - 0.07, 1.5))
    f.rect(0.0, 0.0, 1.70, 1.05, TIMD, sw=1.4, rad=0.06)
    f.rect(0.08, 0.08, 1.54, 0.89, mix(FAS, (200, 190, 160), 0.35), sw=1.0)
    for (a, b, pw, ph) in ((0.18, 0.16, 0.32, 0.40), (0.62, 0.28, 0.36, 0.32),
                           (1.12, 0.14, 0.30, 0.44), (0.30, 0.62, 0.44, 0.26),
                           (0.95, 0.66, 0.38, 0.24)):
        f.rect(a, b, pw, ph, (252, 250, 242), out=0.03, sw=0.8)
    slab(sc, x - 1.0, y - 0.35, 2.10, 2.0, 0.55, 0.10, TILG, FAS, ov=0.10)


def lowwall(sc, x, y, w, d=0.34, h=0.52):
    """a wall at exactly sitting height — the corner's whole secret"""
    mass(sc, x, y, 0, w, d, h, BRK, sw=1.5, top=True, tmat=CONC, arris=False)


# --------------------------------------------------------------- places
def p01():
    """THE BAKERY STEP — the day starts here"""
    def deco(ctx):
        fascia_sign(ctx, "BAKERY", MUS, letters=INK)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        porchlight(ctx)
    sc, ctx = H(MUS, glass=GLSI, deco=deco)
    flags(sc, -0.55, -2.65, x0=-6.5, x1=13.5)
    kerb(sc, -2.66, x0=-6.5, x1=13.5)
    tarmac(sc, -2.86, -5.2, x0=-6.5, x1=13.5)
    aboard(ctx, ctx["x0"] + 4.35, -1.5, MUS)
    bench(ctx, 6.4, -1.9)
    bicycle(ctx, -4.5, -1.35, col=TEAL)
    bicycle(ctx, -3.1, -1.3, col=RED)
    mass(sc, 5.6, -0.85, 0, 0.55, 0.4, 0.35, TIML, sw=1.1, arris=False)
    return sc


def p02():
    """THE OLD OAK — it was here first"""
    sc, ctx = H(GRN, xoff=-2.5)
    grass(sc, -0.4, -7.6, x0=-8.4, x1=16.5)
    wornpath(sc, -7.8, -3.4, 6.6, -3.9, w=1.0)
    wornpatch(sc, [(8.2, -2.2), (13.8, -2.4), (14.2, -5.6), (8.5, -5.9)])
    oak(sc, 11.2, -4.0, s=1.28)
    bench(ctx, 6.6, -5.7)
    return sc


def p03():
    """THE CORNER WALL — exactly the height of sitting"""
    sc, ctx = H(NVY)
    flags(sc, -0.55, -2.65, x0=-6.5, x1=15.0)
    flags(sc, -2.65, -5.75, x0=10.6, x1=15.0)      # the corner apron
    kerb(sc, -2.66, x0=-6.5, x1=10.6)
    tarmac(sc, -2.86, -5.55, x0=-6.5, x1=10.6)
    lowwall(sc, 6.0, -2.35, 5.6)
    lowwall(sc, 11.26, -5.35, 0.34, d=3.0)
    bicycle(ctx, 7.2, -1.6, col=MUS)
    bicycle(ctx, 8.9, -1.55, col=TEAL)
    lamppost(ctx, 13.7, -3.4, glow=False)
    bollard(sc, 11.6, -5.15)
    bollard(sc, 13.8, -5.15)
    return sc


def p04():
    """THE BUS STOP AFTER SCHOOL — everyone's day starts and ends here"""
    sc, ctx = H(RED)
    flags(sc, -0.55, -2.65, x0=-6.5, x1=15.5)
    kerb(sc, -2.66, x0=-6.5, x1=15.5)
    tarmac(sc, -2.86, -6.4, x0=-6.5, x1=15.5)
    shelter(sc, 6.2, -1.95)
    busstop(sc, 10.4, -2.15)
    bench(ctx, 6.7, -1.75)
    chalk(sc, 11.6, -0.9, 2.2, 1.3)
    bicycle(ctx, -3.4, -1.4, col=OLV)
    bicycle(ctx, -4.9, -1.35, col=ORG)
    bin70(sc, 12.6, -2.0)
    return sc


def p05():
    """THE SHORTCUT — it saves three minutes and everyone knows"""
    p2 = base(TEAL)
    p2["xoff"] = 12.3
    sc, ctx = H(GRN)
    sc2 = hero(p2)
    sc.items += sc2.items
    sc.texts += sc2.texts
    grass(sc, -0.4, -4.6, x0=-6.5, x1=18.5)
    flags(sc, -4.6, -6.6, x0=-6.5, x1=18.5)
    wornpath(sc, 5.65, 0.4, 5.4, -2.4, w=0.85)
    wornpath(sc, 5.4, -2.4, 4.2, -5.4, w=0.95)
    hedgerow(sc, -1.4, -2.15, 5.4, h=0.72)
    hedgerow(sc, 7.6, -2.15, 5.6, h=0.72)
    bollard(sc, 4.6, -5.0)
    bollard(sc, 6.4, -5.05)
    bicycle(ctx, 8.6, -5.5, col=RED)
    return sc


def p06():
    """THE CAFÉ TERRACE — you can see the whole street from a chair"""
    def deco(ctx):
        awning_striped(ctx, ORG)
        fascia_sign(ctx, "CAF&#201;", ORG)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    sc, ctx = H(ORG, glass=GLSI, deco=deco)
    brickpav(sc, -0.55, -4.4, x0=-6.5, x1=13.5,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    kerb(sc, -4.41, x0=-6.5, x1=13.5)
    tarmac(sc, -4.61, -6.8, x0=-6.5, x1=13.5)
    terrace(ctx, -3.4, -2.3)
    terrace(ctx, -0.4, -2.9)
    terrace(ctx, 2.5, -2.3)
    aboard(ctx, 5.6, -2.1, ORG)
    planter(sc, 6.8, -1.3, 1.9, cols=(RED, MUS))
    return sc


def p07():
    """OUTSIDE THE PUB — the door faces the evening sun"""
    def deco(ctx):
        fascia_sign(ctx, "THE HOME END", GRN, ww=ctx["gww"] + 0.55,
                    letters=MUS)
        hangingsign(ctx, GRN, MUS)
        bracketlamp(ctx, 1.10, 2.30, on_annex=True)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        doormat(ctx)
    sc, ctx = H(GRN, glass=GLSI, deco=deco)
    flags(sc, -0.55, -3.6, x0=-6.5, x1=13.5)
    kerb(sc, -3.61, x0=-6.5, x1=13.5)
    tarmac(sc, -3.81, -6.2, x0=-6.5, x1=13.5)
    barrel(sc, -3.3, -1.7)
    barrel(sc, -0.9, -2.2)
    planters(ctx)
    bench(ctx, 6.2, -1.9)
    bin70(sc, 8.4, -1.9)
    return sc


def p08():
    """THE SMALL BRIDGE — licensed idleness; you lean and watch the water"""
    sc, ctx = H(TEAL, xoff=-1.5)
    grass(sc, -0.4, -3.6, x0=-8.0, x1=16.5)
    stream(sc, -3.6, -6.3, x0=-8.0, x1=16.5)
    grass(sc, -6.3, -8.0, x0=-8.0, x1=16.5)
    bridge(sc, 8.6, 3.6, -3.6, -6.3)
    wornpath(sc, 3.2, -1.9, 9.6, -2.9, w=0.95)
    wornpath(sc, 11.2, -7.0, 15.2, -7.6, w=0.95)
    bicycle(ctx, 5.9, -3.1, col=MUS)
    blob(sc, -4.6, -7.0, 0.55, 0.5, LEAF2)
    return sc


def p09():
    """THE NOTICE BOARD — news lives here before it is news"""
    sc, ctx = H(RED, xoff=-2.0)
    grass(sc, -0.4, -7.4, x0=-8.0, x1=15.5)
    wornpath(sc, -7.4, -4.2, 6.2, -4.4, w=1.0)
    wornpath(sc, 6.2, -4.4, 14.8, -2.6, w=0.95)
    wornpath(sc, 6.2, -4.4, 9.4, -7.2, w=0.85)
    parishboard(sc, 6.6, -3.5)
    postbox(ctx, 9.0, -3.2)
    fingerpost(sc, 4.4, -3.3)
    return sc


def p10():
    """THE SQUARE — Fridays it smells of flowers; other days it belongs to kids"""
    sc, ctx = H(NVY, xoff=-2.0)
    brickpav(sc, -0.55, -7.2, x0=-8.0, x1=15.5,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    tree(sc, 11.6, -2.2, s=1.25)
    stall(sc, 3.4, -5.4, col=GRN)
    bench(ctx, 9.4, -5.6)
    postbox(ctx, 13.4, -2.4)
    chalk(sc, -4.4, -4.6, 2.4, 1.5)
    return sc


def p11():
    """THE STADIUM PATH — you walk it with everyone, every other Saturday"""
    sc, ctx = H(GRN, xoff=-2.5)
    floodlights(sc, (10.5, 14.0))
    grass(sc, -0.4, -2.5, x0=-8.4, x1=16.5)
    wornpatch(sc, [(-8.2, -2.6), (16.3, -2.6), (16.3, -4.8), (-8.2, -4.8)],
              col=mix(WORN, FLAG, 0.35))
    grass(sc, -4.9, -7.4, x0=-8.4, x1=16.5)
    hedgerow(sc, -7.6, -2.25, 9.4, h=0.78)
    hedgerow(sc, 3.4, -2.25, 12.6, h=0.78)
    for rx in (-6.4, -1.4, 3.6, 8.6, 13.6):
        rail(sc, rx, -5.05, 0, 4.4, 0.85, mix(GRN, DRK, 0.35), n=5)
    for (ox, c) in ((5.2, GRN), (5.65, (240, 238, 230)), (6.1, GRN)):
        sc.poly([(ox, -5.06, 0.62), (ox + 0.3, -5.06, 0.62),
                 (ox + 0.3, -5.06, 0.95), (ox, -5.06, 0.95)], c, n=NY,
                rad=0.04, sw=1.0)
    bollard(sc, -5.4, -3.7)
    bollard(sc, 13.8, -3.7)
    return sc


def p12():
    """THE DOCTOR'S GREEN — you wait out here instead of inside"""
    def deco(ctx):
        fascia_sign(ctx, "SURGERY", TEAL, ww=ctx["gww"] + 0.9)
        windowbox(ctx, ctx["gwc"], ctx["gwv"] - ctx["gwh"] / 2 + 0.32,
                  ctx["gww"] * 0.96, [RED, MUS])
    sc, ctx = H(TEAL, deco=deco)
    grass(sc, -0.4, -7.2, x0=-6.5, x1=15.5)
    wornpath(sc, ctx["x0"] + ctx["du"] + 0.6, -0.4, 12.8, -6.6, w=0.95)
    tree(sc, 11.8, -2.4, s=1.2)
    bench(ctx, 8.6, -4.9)
    bench(ctx, 11.6, -6.3)
    planter(sc, 4.6, -3.4, 2.0, cols=(PNK, RED))
    return sc


PLACES = [
    ("PL-01", "THE BAKERY STEP", "bread comes out at seven; the step is warm",
     "lit window before dawn &#183; bench &#183; two bikes &#183; the crate", p01),
    ("PL-02", "THE OLD OAK", "you touch it before matches; it was here first",
     "worn ring &#183; scarves after wins &#183; one bench, no design", p02),
    ("PL-03", "THE CORNER WALL", "it is exactly the height of sitting, and sees both streets",
     "low brick wall &#183; two bikes &#183; a lamp for after dark", p03),
    ("PL-04", "THE BUS STOP AFTER SCHOOL", "everyone&#8217;s day starts and ends here",
     "shelter &#183; timetable &#183; chalk on the flags &#183; dropped bikes", p04),
    ("PL-05", "THE SHORTCUT", "it saves three minutes, and everyone knows",
     "the gap between houses &#183; worn line across the grass", p05),
    ("PL-06", "THE CAF&#201; TERRACE", "you can see the whole street from a chair",
     "three tables under the awning &#183; the A-board promise", p06),
    ("PL-07", "OUTSIDE THE PUB", "the door faces the evening sun",
     "two barrels on the flags &#183; lantern &#183; Friday implied", p07),
    ("PL-08", "THE SMALL BRIDGE", "the one place you may lean and do nothing",
     "brick parapet &#183; the stream &#183; a bike left mid-errand", p08),
    ("PL-09", "THE NOTICE BOARD", "news lives here before it is news",
     "parish board with its own roof &#183; pillar box &#183; three paths meet", p09),
    ("PL-10", "THE SQUARE", "Fridays it smells of flowers; other days it belongs to the kids",
     "one stall, not a market &#183; tree &#183; chalk in the corner", p10),
    ("PL-11", "THE STADIUM PATH", "you walk it with everyone, every other Saturday",
     "hedge one side, rail the other &#183; a scarf on the fence &#183; floodlights beyond", p11),
    ("PL-12", "THE DOCTOR&#8217;S GREEN", "you wait out here instead of inside",
     "grass, one tree, two benches &#183; the path everyone cuts", p12),
]


def build_place(i):
    return PLACES[i][4]()
