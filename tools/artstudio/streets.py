"""
streets — ERA Sheet 04, "Streets That Feel Like ERA".

Everything between the buildings. The same two locked houses stand at the
back of every tile (green door, navy door — they never change); only the
public realm evolves. Every ground poly draws first (fix = -50) so furniture
and buildings always sit on top.
"""
import math
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY, depth as _d
from era_lang import (BRK, BRK2, BRK3, RND, RND2, FAS, CONC, TIMD, TIML,
                      TILB, TILG, FELT, GLS, GLSI, DRK, INK,
                      GRN, NVY, RED, ORG, MUS, TEAL, OLV, PNK,
                      nrm, vis, face, mass, slab)
from charm import hero, satf
from lovable import (base, blob, vdot, hdisc, flowerrow, bench, bicycle,
                     lamppost, postbox, noticeboard, LEAF, LEAF2, WARM, pad)

# ------------------------------------------------------------- palette
FLAG = (223, 219, 209)      # concrete paving flags
FLAGJ = (204, 199, 187)     # flag joints
PAVB = (186, 118, 88)       # brick pavers
PAVBJ = (158, 98, 74)       # paver joints
TAR = (139, 135, 129)       # quiet tarmac
KERBC = (199, 193, 179)     # granite/concrete kerb
GRASS = (184, 205, 141)
GRASSD = (166, 189, 126)
SOIL = (112, 88, 66)

XA, XB = -6.0, 17.0          # street extent in x
HOUSE_GAP_X = 12.3


def houses():
    """the two locked houses — identical in every tile"""
    p1 = base(GRN)
    p2 = base(NVY)
    p2["xoff"] = HOUSE_GAP_X
    sc = hero(p1)
    sc2 = hero(p2)
    sc.items += sc2.items
    sc.texts += sc2.texts
    return sc


# ------------------------------------------------------------- grounds
def gband(sc, y0, y1, col, scol=None, fix=-50.0, x0=XA, x1=XB, rad=0.10):
    sc.poly([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)],
            col, n=Z, rad=rad, sw=1.0, scol=scol or mul(col, 0.94), fix=fix)


def flags(sc, y0, y1, x0=XA, x1=XB):
    gband(sc, y0, y1, FLAG, x0=x0, x1=x1)
    n = int((x1 - x0) / 1.35)
    for i in range(1, n):
        xx = x0 + (x1 - x0) * i / n
        sc.line((xx, y0, 0.004), (xx, y1, 0.004), FLAGJ, sw=1.0, fix=-49.8)


def brickpav(sc, y0, y1, x0=XA, x1=XB, col=PAVB, j=PAVBJ):
    gband(sc, y0, y1, col, x0=x0, x1=x1)
    d = y1 - y0
    n = max(2, int(abs(d) / 0.42))
    for i in range(1, n):
        yy = y0 + d * i / n
        sc.line((x0 + 0.1, yy, 0.004), (x1 - 0.1, yy, 0.004), j, sw=0.9,
                fix=-49.8)
    m = int((x1 - x0) / 2.6)
    for i in range(1, m):
        xx = x0 + (x1 - x0) * i / m
        sc.line((xx, y0 + d * 0.08, 0.004), (xx, y1 - d * 0.08, 0.004), j,
                sw=0.7, fix=-49.8, op=0.6)


def tarmac(sc, y0, y1, x0=XA, x1=XB):
    gband(sc, y0, y1, TAR, scol=mul(TAR, 0.92), x0=x0, x1=x1)


def grass(sc, y0, y1, x0=XA, x1=XB):
    gband(sc, y0, y1, GRASS, scol=GRASSD, x0=x0, x1=x1, rad=0.16)


def kerb(sc, y, x0=XA, x1=XB):
    gband(sc, y - 0.26, y, KERBC, fix=-49.6, x0=x0, x1=x1, rad=0.03)
    sc.line((x0, y, 0.006), (x1, y, 0.006), mul(KERBC, 0.68), sw=2.0, fix=-49.5)


# ------------------------------------------------------------- furniture
def tree(sc, x, y, s=1.0, col=None):
    mass(sc, x - 0.13 * s, y - 0.13 * s, 0, 0.26 * s, 0.26 * s, 2.30 * s,
         mix(TIMD, (90, 70, 50), 0.3), sw=1.4, top=False, arris=False)
    c = col or LEAF
    vdot(sc, x, y - 0.05, 3.30 * s, 1.55 * s, mul(c, 0.86))
    vdot(sc, x - 0.65 * s, y - 0.08, 2.85 * s, 1.05 * s, mix(c, LEAF2, 0.5))
    vdot(sc, x + 0.55 * s, y - 0.10, 3.75 * s, 1.10 * s,
         mix(c, (255, 255, 235), 0.14))


def hedgerow(sc, x, y, w, h=0.85, d=0.6, col=LEAF2):
    sc.poly([(x, y, 0), (x + w, y, 0), (x + w, y, h), (x, y, h)],
            mul(col, 0.92), n=NY, rad=min(0.35, h * 0.42), sw=1.3)
    sc.poly([(x, y, h), (x + w, y, h), (x + w, y + d, h), (x, y + d, h)],
            mix(col, (255, 255, 235), 0.10), n=Z, rad=0.30, sw=1.3)


def bollard(sc, x, y):
    mass(sc, x - 0.10, y - 0.10, 0, 0.20, 0.20, 0.72, CONC, sw=1.2,
         top=False, arris=False)
    vdot(sc, x, y - 0.10, 0.74, 0.105, mix(CONC, (255, 255, 255), 0.25))


def bin70(sc, x, y):
    mass(sc, x - 0.21, y - 0.21, 0, 0.42, 0.42, 0.78, (72, 76, 72), sw=1.3,
         top=True, tmat=(60, 63, 60), arris=False)
    sc.line((x - 0.19, y - 0.22, 0.60), (x + 0.19, y - 0.22, 0.60),
            (150, 152, 148), sw=1.6, bias=0.3)


def belisha(sc, x, y):
    """the Belisha beacon — utterly English, utterly 1970s"""
    for i in range(6):
        z0 = i * 0.42
        col = (240, 238, 232) if i % 2 == 0 else (44, 46, 48)
        mass(sc, x - 0.055, y - 0.055, z0, 0.11, 0.11, 0.42, col, sw=0.8,
             top=False, arris=False)
    vdot(sc, x, y - 0.08, 2.75, 0.21, ORG)
    vdot(sc, x, y - 0.08, 2.75, 0.42, ORG, op=0.22)


def zebra(sc, xc, y0, y1, w=3.2):
    n = 5
    for i in range(n):
        x0 = xc - w / 2 + w * i / n
        sc.poly([(x0 + 0.06, y0, 0.005), (x0 + w / n - 0.06, y0, 0.005),
                 (x0 + w / n - 0.06, y1, 0.005), (x0 + 0.06, y1, 0.005)],
                (238, 236, 228), n=Z, rad=0.05, sw=0, stroke=False, fix=-49.7)


def busstop(sc, x, y):
    mass(sc, x - 0.06, y - 0.06, 0, 0.12, 0.12, 3.1, DRK, sw=1.2, top=False,
         arris=False)
    f = Face(sc, (x - 0.55, y - 0.07, 2.30), X, Z, NY, ref=(x, y - 0.07, 2.6))
    f.rect(0.0, 0.0, 1.10, 0.62, NVY, sw=1.4, rad=0.07)
    f.rect(0.12, 0.14, 0.86, 0.34, FAS, sw=1.0, rad=0.05)
    f.rect(0.10, 1.05, 0.55, 0.75, FAS, sw=1.2, rad=0.04)   # timetable
    f.line(0.16, 1.20, 0.58, 1.20, (160, 160, 158), sw=1.0)
    f.line(0.16, 1.35, 0.58, 1.35, (160, 160, 158), sw=1.0)
    f.line(0.16, 1.50, 0.58, 1.50, (160, 160, 158), sw=1.0)


def shelter(sc, x, y, w=3.4):
    for k in (0.12, w - 0.12):
        mass(sc, x + k - 0.07, y - 0.07, 0, 0.14, 0.14, 2.35, DRK, sw=1.2,
             top=False, arris=False)
    slab(sc, x - 0.15, y - 0.75, 2.35, w + 0.30, 1.30, 0.14, FELT, FAS, ov=0.0)
    sc.poly([(x, y + 0.42, 0.5), (x + w, y + 0.42, 0.5),
             (x + w, y + 0.42, 2.2), (x, y + 0.42, 2.2)],
            GLS, n=NY, rad=0.08, sw=1.4, op=0.45)


def stall(sc, x, y, w=3.0, d=2.0, col=RED):
    for (kx, ky) in ((0.1, 0.1), (w - 0.1, 0.1), (0.1, d - 0.1),
                     (w - 0.1, d - 0.1)):
        mass(sc, x + kx - 0.05, y + ky - 0.05, 0, 0.10, 0.10, 2.05, TIMD,
             sw=1.0, top=False, arris=False)
    mass(sc, x + 0.1, y + 0.15, 0.85, w - 0.2, d - 0.3, 0.10, TIML, sw=1.3,
         arris=False)
    n = 6
    for i in range(n):
        u0, u1 = x + w * i / n, x + w * (i + 1) / n
        cc = col if i % 2 == 0 else (250, 248, 240)
        sc.poly([(u0, y - 0.15, 2.05), (u1, y - 0.15, 2.05),
                 (u1, y + d / 2, 2.55), (u0, y + d / 2, 2.55)],
                cc, n=nrm((0, -0.5, d / 2 + 0.15)), sw=0.8, rad=0.03)
        sc.poly([(u0, y + d / 2, 2.55), (u1, y + d / 2, 2.55),
                 (u1, y + d + 0.15, 2.05), (u0, y + d + 0.15, 2.05)],
                mul(cc, 0.93), n=nrm((0, 0.5, d / 2 + 0.15)), sw=0.8, rad=0.03)
    for (gx, gc) in ((0.55, ORG), (1.35, MUS), (2.25, GRN)):
        for k in range(3):
            vdot(sc, x + gx + k * 0.17, y + 0.05, 1.06 + (k % 2) * 0.1, 0.10, gc)


def planter(sc, x, y, w, d=0.85, cols=(RED, MUS, PNK)):
    mass(sc, x, y, 0, w, d, 0.48, BRK, sw=1.4, top=True, tmat=SOIL,
         arris=False)
    flowerrow(sc, x + 0.1, y + 0.1, 0.50, w - 0.2, list(cols))


def fingerpost(sc, x, y):
    mass(sc, x - 0.05, y - 0.05, 0, 0.10, 0.10, 2.9, (52, 82, 60), sw=1.1,
         top=False, arris=False)
    f = Face(sc, (x - 1.15, y - 0.06, 2.35), X, Z, NY, ref=(x, y - 0.06, 2.5))
    f.rect(0.0, 0.0, 1.10, 0.26, FAS, sw=1.2, rad=0.10)
    f.rect(1.25, 0.30, 0.95, 0.26, FAS, sw=1.2, rad=0.10)


def chalk(sc, x, y, w, d):
    """children's chalk on the paving — the play street's signature"""
    c = (252, 250, 244)
    for k in range(4):
        yy = y - d * k / 4
        sc.poly([(x, yy, 0.006), (x + w, yy, 0.006),
                 (x + w, yy - d / 5, 0.006), (x, yy - d / 5, 0.006)],
                c, n=Z, rad=0.05, sw=1.2, scol=c, op=0.0, fix=-49.7)
    for k in range(4):
        sc.line((x, y - d * k / 4, 0.006), (x + w, y - d * k / 4, 0.006), c,
                sw=1.4, fix=-49.6, op=0.55)
    sc.line((x, y, 0.006), (x, y - d, 0.006), c, sw=1.4, fix=-49.6, op=0.55)
    sc.line((x + w, y, 0.006), (x + w, y - d, 0.006), c, sw=1.4, fix=-49.6,
            op=0.55)
    vdot(sc, x + w + 0.8, y - d * 0.4, 0.13, 0.13, (250, 248, 242))


# ------------------------------------------------------------- streets
# band geometry shared by most tiles
PV0, PV1 = -0.55, -2.65          # near pavement
RD0, RD1 = -2.85, -7.15          # carriageway
FP0, FP1 = -7.35, -9.05          # far pavement


def plain(sc):
    flags(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    lamppost({"sc": sc, "K": lambda c: c}, 8.2, PV1 + 0.55, glow=False)
    bin70(sc, -4.6, PV1 + 0.5)


def avenue(sc):
    grass(sc, PV0, -1.75)
    flags(sc, -1.75, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    grass(sc, FP0, FP1)
    for tx in (-3.4, 5.6, 14.6):
        tree(sc, tx, -1.15, s=1.25)
    tree(sc, 1.2, FP0 - 0.55, s=1.05, col=mix(LEAF, ORG, 0.18))
    tree(sc, 10.4, FP0 - 0.55, s=1.10)


def green(sc):
    grass(sc, PV0, -2.2, x0=XA, x1=XB)
    flags(sc, -2.2, -3.35)
    tarmac(sc, -3.55, -6.05)
    grass(sc, -6.25, FP1)
    kerb(sc, -3.36)
    kerb(sc, -6.06)
    blob(sc, -2.5, -1.3, 0.55, 0.5, LEAF2)
    blob(sc, 9.0, -1.5, 0.62, 0.55, LEAF)
    tree(sc, 15.4, -6.9, s=0.95)
    blob(sc, 3.5, -7.4, 0.5, 0.48, LEAF2)


def brickst(sc):
    brickpav(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    brickpav(sc, RD0, RD1, col=mix(PAVB, (120, 80, 62), 0.35),
             j=mul(PAVBJ, 0.85))
    kerb(sc, RD1 - 0.01)
    brickpav(sc, FP0, FP1)
    for bx in (-3.9, 1.4, 7.0, 12.6):
        bollard(sc, bx, RD0 + 0.45)
    planter(sc, 14.6, PV1 + 0.55, 2.1)


def social(sc):
    flags(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    ctx = {"sc": sc, "K": lambda c: c}
    bench(ctx, -1.4, -1.9)
    bench(ctx, 2.6, -1.9)
    hedgerow(sc, 5.6, -2.05, 3.2, h=0.62)
    bench(ctx, 12.4, -1.9)
    bin70(sc, 10.6, -2.0)
    lamppost(ctx, 0.8, -2.15, glow=False)


def bloom(sc):
    flags(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    planter(sc, -4.6, PV1 + 0.5, 2.6, cols=(RED, MUS))
    planter(sc, 2.4, PV1 + 0.5, 2.6, cols=(PNK, RED))
    planter(sc, 9.6, PV1 + 0.5, 2.6, cols=(MUS, PNK))
    planter(sc, -1.2, FP0 - 0.25, 2.2, cols=(RED, PNK))
    planter(sc, 7.4, FP0 - 0.25, 2.2, cols=(MUS, RED))


def play(sc):
    brickpav(sc, PV0, FP1, col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    for bx in (-4.8, -0.6, 3.6, 7.8, 12.0, 16.2):
        bollard(sc, bx, PV1 - 0.15)
    chalk(sc, 2.4, -4.4, 3.0, 1.8)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, 9.8, -3.4, col=TEAL)
    bicycle(ctx, 11.4, -3.25, col=MUS)
    blob(sc, -4.4, -7.6, 0.5, 0.48, LEAF)


def busstop_st(sc):
    flags(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    shelter(sc, 6.4, -1.95)
    busstop(sc, 10.6, -2.15)
    ctx = {"sc": sc, "K": lambda c: c}
    bench(ctx, 6.9, -1.75)
    bin70(sc, 12.0, -2.0)
    sc.poly([(5.4, RD0, 0.005), (12.2, RD0, 0.005),
             (12.2, RD0 - 1.15, 0.005), (5.4, RD0 - 1.15, 0.005)],
            (208, 190, 130), n=Z, rad=0.05, sw=0, stroke=False, fix=-49.7,
            op=0.55)


def crossing(sc):
    flags(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    zebra(sc, 5.6, RD0 - 0.25, RD1 + 0.25)
    belisha(sc, 3.5, PV1 + 0.42)
    belisha(sc, 7.7, FP0 - 0.42)
    bollard(sc, 1.6, PV1 + 0.42)
    bollard(sc, 9.6, PV1 + 0.42)


def square(sc):
    flags(sc, PV0, PV1, x0=XA, x1=1.4)
    flags(sc, PV0, PV1, x0=9.2, x1=XB)
    brickpav(sc, PV0, -5.3, x0=1.4, x1=9.2)
    kerb(sc, PV1 - 0.01, x0=XA, x1=1.4)
    kerb(sc, PV1 - 0.01, x0=9.2, x1=XB)
    kerb(sc, -5.31, x0=1.4, x1=9.2)
    tarmac(sc, RD0, RD1, x0=XA, x1=1.4)
    tarmac(sc, -5.5, RD1, x0=1.4, x1=9.2)
    tarmac(sc, RD0, RD1, x0=9.2, x1=XB)
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    tree(sc, 5.3, -3.6, s=1.3)
    ctx = {"sc": sc, "K": lambda c: c}
    bench(ctx, 2.6, -4.35)
    bench(ctx, 6.4, -4.35)
    postbox(ctx, 8.5, -2.1)
    fingerpost(sc, 1.9, -2.1)


def market(sc):
    flags(sc, PV0, PV1)
    kerb(sc, PV1 - 0.01)
    brickpav(sc, RD0, RD1, col=mix(PAVB, FLAG, 0.42),
             j=mix(PAVBJ, FLAGJ, 0.4))
    kerb(sc, RD1 - 0.01)
    flags(sc, FP0, FP1)
    stall(sc, -3.6, -5.6, col=RED)
    stall(sc, 4.4, -5.6, col=GRN)
    stall(sc, 12.2, -5.6, col=NVY)
    ctx = {"sc": sc, "K": lambda c: c}
    bicycle(ctx, 15.6, -2.9, col=OLV)
    bollard(sc, -5.0, RD0 - 0.4)
    bollard(sc, 16.4, RD0 - 0.4)


def era_street(sc):
    grass(sc, PV0, -1.55)
    brickpav(sc, -1.55, PV1)
    kerb(sc, PV1 - 0.01)
    tarmac(sc, RD0, RD1)
    kerb(sc, RD1 - 0.01)
    brickpav(sc, FP0, FP1)
    tree(sc, -3.2, -1.05, s=1.15)
    tree(sc, 8.6, -1.05, s=1.15)
    planter(sc, 12.6, PV1 + 0.55, 2.0, cols=(RED, MUS))
    ctx = {"sc": sc, "K": lambda c: c}
    bench(ctx, 14.9, -1.85)
    zebra(sc, 2.6, RD0 - 0.25, RD1 + 0.25)
    belisha(sc, 0.5, PV1 + 0.42)
    bollard(sc, 5.4, PV1 + 0.42)
    bollard(sc, 16.2, PV1 + 0.42)
    bin70(sc, 6.4, PV1 + 0.5)


STREETS = [
    ("ST-01", "CONTROL &#183; THE PLAIN STREET",
     "what does the street look like before we try?",
     "flags &#183; kerb &#183; quiet tarmac &#183; one lamp, one bin", plain),
    ("ST-02", "THE AVENUE", "what if trees dominate?",
     "grass verge &#183; five limes &#183; canopy over the walk", avenue),
    ("ST-03", "THE GREEN", "what if grass dominates?",
     "deep verges both sides &#183; the road narrows to fit", green),
    ("ST-04", "THE BRICK STREET", "what if brick paving dominates?",
     "pavers wall-to-wall &#183; darker course for the carriageway", brickst),
    ("ST-05", "THE SOCIAL STREET", "what if seating becomes social?",
     "three benches, a hedge backrest, a lamp to talk under", social),
    ("ST-06", "IN BLOOM", "what if flowers are the identity?",
     "raised brick planters both sides &#183; colour with a reason", bloom),
    ("ST-07", "THE PLAY STREET", "what if traffic almost disappears?",
     "bollards close it &#183; one surface &#183; chalk and bicycles", play),
    ("ST-08", "THE BUS STOP", "what if arrival defines the street?",
     "shelter, flag, timetable, bench &#183; the town&#8217;s front door", busstop_st),
    ("ST-09", "THE CROSSING", "what if crossing is the safest act?",
     "zebra &#183; two Belisha beacons &#183; tightened kerbs", crossing),
    ("ST-10", "THE POCKET SQUARE", "what if the street pauses?",
     "paving swells into a square &#183; tree, two benches, pillar box", square),
    ("ST-11", "MARKET MORNING", "what if Friday writes the street?",
     "three striped stalls on the closed carriageway &#183; evidence of life",
     market),
    ("ST-12", "THE ERA STREET &#183; SYNTHESIS", "all of it, in measure",
     "verge + trees + brick walk + zebra + planter + bench", era_street),
]


def build_street(i):
    code, name, q, spec, fn = STREETS[i]
    sc = houses()
    fn(sc)
    # terminate the slice cleanly at its near edge
    sc.line((XA, FP1, 0.006), (XB, FP1, 0.006), (188, 183, 171), sw=1.8,
            fix=-49.4)
    return sc
