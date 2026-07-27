"""
concepts.py — twelve architectural concepts for ERA, drawn.

Each builder returns a Scene authored with the front elevation on y = 0.
Twelve directions, deliberately divergent, one world.
"""
from svgkit import Scene, Face, X, Y, Z, NX, NY, shade, mix, mul, depth
from era_lang import *


def rec(col):
    """the colour of a recess — darker, cooler, no new material"""
    return mix(mul(col, 0.60), (78, 96, 124), 0.22)


# ------------------------------------------------------------------ 01
def h01():
    """DETACHED / DATUM — brick base, render above, shallow pitch. The control."""
    sc = Scene()
    w, d = 9.6, 7.4
    x0 = -6.6
    e1, e2 = 2.92, 5.62
    f1, r1, _ = mass(sc, x0, 0, 0, w, d, e1, BRK, top=False)
    f2, r2, _ = mass(sc, x0, 0, e1, w, d, e2 - e1, RND, top=False)
    roof_x(sc, x0, 0, e2, w, d, 1.95, TILB, ov=0.62, ovg=0.52, fas=0.40)
    flue(sc, x0 + w * 0.66, d * 0.44, e2 + 1.50, 1.30, CONC, 0.38)
    win(f1, 0.80, 0.90, 3.05, 1.75, bars=2)
    door(f1, 4.75, 0.0, 1.10, 2.25, GRN, glazed=0.85)
    win(f1, 6.55, 0.90, 2.15, 1.75, bars=1)
    slab(sc, x0 + 4.45, 0, 2.48, 1.75, 1.05, 0.24, FELT, FAS, ov=0.0)
    for u, ww in ((0.80, 2.55), (3.85, 2.05), (6.55, 2.15)):
        win(f2, u, 0.55, ww, 1.65, bars=1)
    win(r1, 1.30, 0.90, 2.20, 1.75, bars=1)
    win(r2, 1.30, 0.55, 2.20, 1.65, bars=1)
    gx = x0 + w
    fg, rg, _ = mass(sc, gx, 1.10, 0, 3.60, 5.50, 2.62, BRK, top=False)
    slab(sc, gx, 1.10, 2.62, 3.60, 5.50, 0.32, FELT, FAS, ov=0.26)
    fg.rect(0.40, 0.0, 2.85, 2.12, mix(CONC, FAS, 0.45), sw=2.0, rad=0.14)
    for i in range(1, 6):
        fg.line(0.48, 2.12 * i / 6.0, 3.17, 2.12 * i / 6.0,
                mul(shade(CONC, NY), 0.86), sw=1.5)
    return sc


# ------------------------------------------------------------------ 02
def h02():
    """DETACHED / GABLE TO STREET — one shape, cut open by a full-height light slot."""
    sc = Scene()
    w, d = 8.2, 9.4
    x0 = -4.1
    e = 5.30
    f, r, _ = mass(sc, x0, 0, 0, w, d, e, BRK, top=False)
    roof_y(sc, x0, 0, e, w, d, 3.05, TILG, ov=0.55, ovg=0.16, gmat=BRK)
    g = Face(sc, (x0 - 0.55, -0.16, e), X, Z, NY,
             ref=(x0 + w / 2, -0.16, e + 1.0))
    su = 2.55
    sw_ = 2.30
    f.rect(su - 0.22, 0.0, sw_ + 0.44, e, rec(BRK), sw=2.0, rad=0.16)
    win(f, su, 0.28, sw_, 2.20, hbar=1, bars=1, cill=None)
    win(f, su, 2.88, sw_, 2.10, hbar=1, bars=1, cill=None)
    gu = su + 0.55
    g.poly([(gu - 0.22, 0.0), (gu + sw_ + 0.22, 0.0),
            (gu + sw_ + 0.22 - 0.72, 1.62), (gu + 0.22 + 0.50, 1.62)],
           rec(BRK), sw=2.0, rad=0.16)
    g.poly([(gu, 0.10), (gu + sw_, 0.10),
            (gu + sw_ - 0.62, 1.48), (gu + 0.62, 1.48)],
           GLS, sw=3.0, scol=shade(FAS, NY), rad=0.12)
    boarding(f, 0.45, 0.0, 1.85, e - 0.15, TIMD, 0.28)
    win(f, 5.55, 0.90, 1.90, 1.70, bars=1)
    win(f, 5.55, 3.35, 1.90, 1.45, bars=1)
    door(f, 0.95, 0.0, 1.10, 2.25, MUS, glazed=0.85)
    slab(sc, x0 + 0.35, 0, 2.50, 2.10, 1.20, 0.24, FELT, FAS, ov=0.0)
    win(r, 1.10, 0.90, 2.40, 1.70, bars=1)
    win(r, 4.60, 0.90, 1.70, 1.70, bars=1)
    win(r, 1.10, 3.35, 2.40, 1.45, bars=1)
    win(r, 4.60, 3.35, 1.70, 1.45, bars=1)
    return sc


# ------------------------------------------------------------------ 03
def h03():
    """DETACHED / DEEP OVERSAIL — the roof is the architecture. Timber over glass."""
    sc = Scene()
    gw, gd = 10.8, 7.8
    x0 = -5.4
    z1 = 3.05
    mass(sc, x0, 0, 0, gw, gd, z1, mul(GLS, 0.86), top=False, arris=False, sw=1.4)
    fg = Face(sc, (x0, 0, 0), X, Z, NY, ref=(x0 + gw / 2, 0, z1 / 2))
    rg = Face(sc, (x0 + gw, 0, 0), Y, Z, X, ref=(x0 + gw, gd / 2, z1 / 2))
    shopfront(fg, 0.35, 0.0, 5.55, z1 - 0.18, stall=0.0, bays=4)
    door(fg, 6.45, 0.0, 1.15, 2.35, NVY, glazed=1.50)
    shopfront(fg, 8.00, 0.0, 2.35, z1 - 0.18, stall=0.0, bays=2)
    shopfront(rg, 0.55, 0.0, 6.65, z1 - 0.18, stall=0.0, bays=4)
    for xx in (x0 + 0.14, x0 + 6.10, x0 + gw - 0.14):
        post(sc, xx, 0.05, 0, z1, DRK, 0.085)
    # brick spine, ground to sky
    fsp, rsp, _ = mass(sc, x0 + gw - 1.20, -0.35, 0, 1.75, 3.30, z1 + 4.35,
                       BRK, top=True, tmat=CONC)
    rsp.rect(0.95, 1.30, 0.52, z1 + 2.40, rec(BRK), sw=1.6, rad=0.12)
    # first floor: timber box, set back at the front
    uw, ud = 9.15, 6.30
    ux, uy = x0 + 1.30, 0.95
    z2 = z1 + 2.85
    fu = Face(sc, (ux, uy, z1), X, Z, NY, ref=(ux + uw / 2, uy, z1 + 1.4))
    ru = Face(sc, (ux + uw, uy, z1), Y, Z, X, ref=(ux + uw, uy + ud / 2, z1 + 1.4))
    mass(sc, ux, uy, z1, uw, ud, 2.85, TIMD, top=False)
    boarding(fu, 0.0, 0.0, uw, 2.85, TIMD, 0.30)
    for u in (0.85, 3.70, 6.55) :
        win(fu, u, 0.60, 1.95, 1.70, bars=1, cill=None)
    win(ru, 1.10, 0.60, 2.55, 1.70, bars=1, cill=None)
    win(ru, 4.30, 0.60, 1.45, 1.70, cill=None)
    slab(sc, ux, uy, z2, uw, ud, 0.36, FELT, FAS, ov=1.65)
    return sc


# ------------------------------------------------------------------ 04
def h04():
    """SEMI-DETACHED / STAGGERED MONOPITCH — one family, two steps, one slope each."""
    sc = Scene()
    uw, ud = 7.9, 8.4

    def unit(ax, ay, plinth, wall, col, mirror):
        f0, r0, _ = mass(sc, ax, ay, 0, uw, ud, plinth, BRK, top=False)
        f1, r1, _ = mass(sc, ax, ay, plinth, uw, ud, wall, RND, top=False)
        zf = plinth + wall
        mono(sc, ax, ay, 0, uw, ud, zf, zf + 1.85, TILG, ov=0.52, t=0.44, fmat=FAS)
        bu = 0.55 if not mirror else uw - 3.35
        boarding(f0, bu, 0.0, 2.80, plinth, TIMD, 0.28)
        boarding(f1, bu, 0.0, 2.80, wall, TIMD, 0.28)
        win(f1, bu + 0.30, 0.35, 2.20, 1.70, bars=1, cill=None)
        win(f1, bu + 0.30, 2.50, 2.20, 1.30, bars=1, cill=None)
        win(f0, bu + 0.30, 0.20, 2.20, 1.15, cill=None)
        du = 4.00 if not mirror else 2.75
        door(f0, du, 0.0, 1.12, 2.30, col, glazed=0.85)
        slab(sc, ax + du - 0.35, ay, 2.52, 1.85, 1.15, 0.24, FELT, FAS, ov=0.0)
        wu = 5.80 if not mirror else 0.55
        win(f0, wu, 0.85, 1.75, 1.55, bars=1)
        win(f1, wu, 0.35, 1.75, 1.70, bars=1)
        return f0, f1, r0, r1

    unit(-8.15, 0.0, 1.05, 3.95, OLV, False)
    fb0, fb1, rb0, rb1 = unit(-0.25, 3.40, 1.05, 5.20, NVY, True)
    win(rb1, 1.40, 0.55, 2.10, 1.70, bars=1)
    win(rb0, 1.40, 0.85, 2.10, 1.20, cill=None)
    win(rb1, 4.60, 0.55, 1.55, 1.70, bars=1)
    return sc


# ------------------------------------------------------------------ 05
def f01():
    """APARTMENTS / SHIFTED STACK — brick base, banded render, one tall stair tower."""
    sc = Scene()
    w, d = 13.6, 9.4
    x0 = -6.2
    sh = 2.92
    H = sh * 3
    # brick ground floor
    f0, r0, _ = mass(sc, x0, 0, 0, w, d, sh, BRK, top=False)
    # two render storeys, banded
    f, r, _ = mass(sc, x0, 0, sh, w, d, sh * 2, RND, top=False)
    slab(sc, x0, 0, H, w, d, 0.46, FELT, FAS, ov=0.34)
    f.rect(0.0, 0.0, w, 0.32, CONC, sw=1.6, rad=0.10)
    f.rect(0.0, sh, w, 0.32, CONC, sw=1.6, rad=0.10)
    r.rect(0.0, 0.0, d, 0.32, CONC, sw=1.6, rad=0.10)
    r.rect(0.0, sh, d, 0.32, CONC, sw=1.6, rad=0.10)
    # ground floor openings
    win(f0, 0.85, 0.85, 2.60, 1.85, bars=2)
    win(f0, 4.20, 0.85, 2.20, 1.85, bars=1)
    win(f0, 7.15, 0.85, 2.05, 1.85, bars=1)
    win(r0, 1.60, 0.85, 2.40, 1.85, bars=1)
    win(r0, 5.20, 0.85, 2.40, 1.85, bars=1)
    # upper floors: a recessed balcony and a window pair, twice
    for lvl in (0, 1):
        z = lvl * sh + 0.36
        f.rect(0.65, z, 3.75, 2.30, rec(RND), sw=1.8, rad=0.16)
        win(f, 1.05, z + 0.18, 1.50, 1.95, bars=1, cill=None)
        door(f, 2.95, z, 1.15, 2.12, ORG, glazed=1.52)
        rail(sc, x0 + 0.70, 0.03, sh + z, 3.65, 1.06, ORG, n=10)
        win(f, 5.15, z + 0.30, 2.15, 1.85, bars=1)
        win(f, 7.60, z + 0.30, 1.70, 1.85, bars=1)
        win(r, 1.60, z + 0.30, 2.40, 1.85, bars=1)
        win(r, 5.20, z + 0.30, 2.40, 1.85, bars=1)
    # stair tower — brick, forward of the wall, taller than the block
    tw, ty = 3.55, -1.85
    tx = x0 + w - tw
    fs, rs, _ = mass(sc, tx, ty, 0, tw, 4.05, H + 1.35, BRK, top=True, tmat=CONC)
    fs.rect(1.05, 0.45, 1.55, H + 0.55, rec(BRK), sw=1.8, rad=0.14)
    fs.rect(1.22, 0.60, 1.22, H + 0.28, GLS, sw=2.8, scol=shade(FAS, NY), rad=0.12)
    for i in range(1, 4):
        v = 0.60 + (H + 0.28) * i / 4.0
        fs.line(1.22, v, 2.44, v, shade(FAS, NY), sw=2.6)
    door(fs, 1.05, 0.0, 1.42, 2.45, ORG, glazed=1.65)
    slab(sc, tx - 0.30, ty - 0.80, 3.35, 4.15, 0.82, 0.26, FELT, FAS, ov=0.0)
    # tower return, brick, with a slot
    rs.rect(1.35, 2.10, 0.62, H - 1.60, rec(BRK), sw=1.6, rad=0.12)
    win(rs, 0.85, 2.55, 1.15, 1.55, bars=1)
    win(rs, 0.85, 5.47, 1.15, 1.55, bars=1)
    return sc



# ------------------------------------------------------------------ 06
def f02():
    """MAISONETTES / DECK ACCESS — the horizontal building. Four doors, four colours."""
    sc = Scene()
    w, d = 16.0, 7.6
    x0 = -8.0
    z1 = 2.90
    f1, r1, _ = mass(sc, x0, 0, 0, w, d, z1, BRK, top=False)
    f2, r2, _ = mass(sc, x0, 0, z1, w, d, 2.86, RND, top=False)
    slab(sc, x0, 0, z1 + 2.86, w, d, 0.38, FELT, FAS, ov=0.32)
    for i, col in enumerate((ORG, MUS, OLV, NVY)):
        u = 0.80 + i * 3.85
        door(f1, u, 0.0, 1.08, 2.20, col, glazed=0.78)
        win(f1, u + 1.50, 0.80, 1.95, 1.65, bars=1)
    for i, col in enumerate((MUS, ORG, NVY, OLV)):
        u = 0.80 + i * 3.85
        door(f2, u, 0.0, 1.08, 2.20, col, glazed=0.78)
        win(f2, u + 1.50, 0.70, 1.95, 1.55, bars=1, cill=None)
    dy = -1.95
    slab(sc, x0 + 0.25, dy, z1 - 0.38, w - 0.50, 1.97, 0.34, CONC, FAS, ov=0.0)
    for i in range(6):
        post(sc, x0 + 0.9 + i * 2.86, dy + 0.35, 0, z1 - 0.38, DRK, 0.08)
    rail(sc, x0 + 0.25, dy, z1 - 0.04, w - 0.50, 1.05, TIMD, n=24, sw=1.7)
    sx = x0 + w
    mass(sc, sx, -1.95, 0, 2.45, 3.45, z1 + 1.45, BRK3, top=True, tmat=CONC)
    fst = Face(sc, (sx, -1.95, 0), X, Z, NY, ref=(sx + 1.2, -1.95, 1.6))
    fst.rect(0.22, 0.10, 2.00, z1 + 0.95, rec(BRK3), sw=1.6, rad=0.12)
    for i in range(9):
        fst.line(0.30 + i * 0.21, 0.18 + i * 0.44, 0.30 + (i + 1) * 0.21,
                 0.18 + i * 0.44, mix(FAS, CONC, 0.4), sw=2.4)
    win(r1, 1.70, 0.80, 1.85, 1.65, bars=1)
    win(r2, 1.70, 0.70, 1.85, 1.55, bars=1)
    win(r1, 4.60, 0.80, 1.55, 1.65, bars=1)
    win(r2, 4.60, 0.70, 1.55, 1.55, bars=1)
    return sc


# ------------------------------------------------------------------ 07
def v01():
    """VILLAGE HALL / BUTTERFLY — one civic shape, clerestory light, deep canopy."""
    sc = Scene()
    w, d = 17.4, 10.6
    x0 = -8.7
    e = 5.10
    zc = e - 1.35
    f0, r0, _ = mass(sc, x0, 0, 0, w, d, 1.25, BRK, top=False)
    f1, r1, _ = mass(sc, x0, 0, 1.25, w, d, zc - 1.25, RND, top=False)
    mass(sc, x0, 0, zc, w, d, 1.35, GLS, top=False, arris=False, sw=1.4)
    fcl = Face(sc, (x0, 0, zc), X, Z, NY, ref=(x0 + w / 2, 0, zc + 0.7))
    rcl = Face(sc, (x0 + w, 0, zc), Y, Z, X, ref=(x0 + w, d / 2, zc + 0.7))
    for i in range(7):
        win(fcl, 0.55 + i * 2.42, 0.22, 1.95, 0.92, cill=None)
    for i in range(4):
        win(rcl, 0.70 + i * 2.42, 0.22, 1.95, 0.92, cill=None)
    butterfly(sc, x0, 0, e, w, d, 2.35, FELT, ov=0.62, t=0.46, fmat=FAS)
    for i in range(4):
        win(f1, 0.95 + i * 2.30, 0.45, 1.70, 2.15, bars=1)
    for i in range(2):
        win(r1, 1.20 + i * 3.40, 0.45, 2.45, 2.15, bars=1)
    ex = x0 + 10.6
    shopfront(f1, 10.6, 0.0, 5.00, 2.55, stall=0.0, bays=4)
    door(f1, 12.55, 0.0, 1.20, 2.35, GRN, glazed=1.60)
    slab(sc, ex - 0.70, -3.30, 3.10, 6.30, 3.35, 0.38, FELT, FAS, ov=0.0)
    for px in (ex - 0.35, ex + 5.25):
        for py in (-3.00, -0.45):
            post(sc, px, py, 0, 3.10, DRK, 0.095)
    nb = Face(sc, (ex - 0.70, -3.30, 3.10), X, Z, NY, ref=(ex + 2.4, -3.30, 3.3))
    nb.rect(0.22, -0.62, 5.86, 0.92, MUS, sw=1.6, rad=0.12)
    sc.text3(nb, 3.15, -0.28, "VILLAGE HALL", 0.48, INK, weight="700", ls=0.10, out=0.06)
    return sc


# ------------------------------------------------------------------ 08
def v02():
    """SURGERY / ROOF MONITORS — light comes from the roof, not the wall."""
    sc = Scene()
    w, d = 13.8, 10.0
    x0 = -6.9
    h = 3.60
    f, r, _ = mass(sc, x0, 0, 0, w, d, h, BRK, top=False)
    slab(sc, x0, 0, h, w, d, 0.52, FELT, FAS, ov=0.40)
    # entrance recess, teal soffit
    f.rect(4.85, 0.0, 4.45, 2.95, rec(BRK), sw=1.8, rad=0.16)
    fr = Face(sc, (x0 + 4.85, 0, 0), X, Z, NY, ref=(x0 + 7.0, 0, 1.5))
    shopfront(fr, 0.30, 0.0, 3.85, 2.85, stall=0.0, bays=3)
    door(fr, 1.45, 0.0, 1.20, 2.30, TEAL, glazed=1.60)
    slab(sc, x0 + 4.60, -1.55, 2.95, 4.95, 1.60, 0.28, FELT, TEAL, ov=0.0)
    for px in (x0 + 4.85, x0 + 9.20):
        post(sc, px, -1.30, 0, 2.95, DRK, 0.085)
    win(f, 0.80, 1.05, 3.55, 1.85, bars=2)
    win(f, 10.05, 1.05, 3.05, 1.85, bars=1)
    win(r, 1.10, 1.05, 3.05, 1.85, bars=1)
    win(r, 5.30, 1.05, 2.55, 1.85, bars=1)
    # three roof monitors, glass to the street
    for i in range(3):
        mx = x0 + 1.20 + i * 4.30
        mono(sc, mx, 2.55, 0, 3.35, 2.20, h + 2.30, h + 1.25, FELT, ov=0.22, t=0.18,
             fmat=FAS)
        mass(sc, mx, 2.55, h + 0.52, 3.35, 0.34, 1.60, mul(GLS, 0.86), top=False,
             arris=False, sw=1.2)
        fmg = Face(sc, (mx, 2.55, h + 0.52), X, Z, NY, ref=(mx + 1.7, 2.55, h + 1.3))
        win(fmg, 0.14, 0.14, 3.07, 1.35, bars=2, cill=None)
    # brick screen wall, sign
    mass(sc, x0 - 3.90, 0.70, 0, 3.30, 0.50, 2.30, BRK, top=True, tmat=CONC)
    sign = Face(sc, (x0 - 3.70, 0.70, 0.85), X, Z, NY, ref=(x0 - 2.2, 0.70, 1.2))
    sign.rect(0.0, 0.0, 2.90, 0.70, TEAL, out=0.05, sw=1.4, rad=0.10)
    sc.text3(sign, 1.45, 0.25, "SURGERY", 0.34, FAS, weight="700", ls=0.06, out=0.10)
    return sc


# ------------------------------------------------------------------ 09
def p01():
    """PUB / LONG PITCH + WING — the town's one dark colour, held low."""
    sc = Scene()
    w, d = 15.2, 8.8
    x0 = -5.8
    e1, e2 = 3.15, 6.05
    f1, r1, _ = mass(sc, x0, 0, 0, w, d, e1, BRK, top=False)
    f2, r2, _ = mass(sc, x0, 0, e1, w, d, e2 - e1, RND2, top=False)
    roof_x(sc, x0, 0, e2, w, d, 2.35, TILB, ov=0.68, ovg=0.55, fas=0.42)
    stack(sc, x0 + 3.20, d * 0.42, e2 + 1.65, 1.90, 1.30, 0.90, BRK, CONC)
    band(f1, 0.0, 2.66, w, 0.48, GRN, out=0.07)
    for u, ww in ((0.75, 2.55), (3.75, 2.55), (9.85, 1.95), (12.35, 1.95)):
        win(f1, u, 0.90, ww, 1.60, bars=2, cill=CONC)
    door(f1, 6.95, 0.0, 1.30, 2.40, GRN, glazed=1.60)
    win(f1, 8.55, 0.90, 1.00, 1.60, bars=1)
    for i in range(6):
        win(f2, 0.85 + i * 2.42, 0.50, 1.55, 1.70, bars=1)
    win(r1, 1.20, 0.90, 2.55, 1.60, bars=2)
    win(r2, 1.20, 0.50, 1.85, 1.70, bars=1)
    win(r2, 4.30, 0.50, 1.85, 1.70, bars=1)
    lx = x0 - 5.50
    fl, rl, _ = mass(sc, lx, 1.30, 0, 5.50, 6.40, 3.25, BRK, top=False)
    slab(sc, lx, 1.30, 3.25, 5.50, 6.40, 0.38, FELT, FAS, ov=0.34)
    shopfront(fl, 0.55, 0.55, 4.40, 2.25, stall=0.55, stallmat=BRK2, bays=3)
    sc.line((x0 + 5.60, -0.05, 4.55), (x0 + 5.60, -2.05, 4.55), DRK, sw=3.4, bias=0.9)
    sc.line((x0 + 5.60, -0.05, 3.45), (x0 + 5.60, -1.90, 4.48), DRK, sw=2.2, bias=0.9)
    sgn = Face(sc, (x0 + 4.55, -1.92, 2.45), X, Z, NY, ref=(x0 + 5.6, -1.92, 3.4))
    sgn.rect(0.0, 0.0, 2.10, 2.05, GRN, sw=2.6, scol=shade(FAS, NY), rad=0.14)
    sgn.rect(0.18, 0.18, 1.74, 1.69, mul(GRN, 0.82), sw=1.2, rad=0.10)
    sc.text3(sgn, 1.05, 1.12, "FREE", 0.38, MUS, weight="700", ls=0.03, out=0.06)
    sc.text3(sgn, 1.05, 0.58, "HOUSE", 0.38, MUS, weight="700", ls=0.03, out=0.06)
    return sc


# ------------------------------------------------------------------ 10
def r01():
    """CORNER SHOP / CHAMFER — the plan turns the corner, the fascia wraps."""
    sc = Scene()
    foot = [(-5.8, 0.0), (2.70, 0.0), (5.80, 2.70), (5.80, 9.40), (-5.8, 9.40)]
    z1, z2 = 3.65, 6.75
    fl = prism(sc, foot, 0, z1, BRK2, top=False)
    fu = prism(sc, foot, z1, z2 - z1, BRK, top=False)
    parapet(sc, -5.8, 0.0, z2, 11.6, 9.4, 0.62, 0.28, BRK, CONC)
    F, C, R = fl[0], fl[1], fl[2]
    FU, CU, RU = fu[0], fu[1], fu[2]
    shopfront(F, 0.45, 0.0, 6.55, 2.72, stall=0.66, stallmat=BRK2, bays=4)
    shopfront(C, 0.40, 0.0, 2.55, 2.72, stall=0.0, bays=1)
    door(C, 1.15, 0.0, 1.20, 2.35, MUS, glazed=1.60)
    shopfront(R, 0.55, 0.0, 4.85, 2.72, stall=0.66, stallmat=BRK2, bays=3)
    F.rect(0.0, 2.80, 8.50, 0.80, NVY, out=0.07, sw=1.8, rad=0.10)
    C.rect(0.0, 2.80, 4.39, 0.80, NVY, out=0.07, sw=1.8, rad=0.10)
    R.rect(0.0, 2.80, 9.40, 0.80, NVY, out=0.07, sw=1.8, rad=0.10)
    sc.text3(F, 3.90, 3.06, "STORES", 0.46, FAS, weight="700", ls=0.15, out=0.13)
    for u in (0.85, 3.45, 6.00) :
        win(FU, u, 0.65, 1.80, 1.85, bars=1)
    win(CU, 1.15, 0.65, 2.10, 1.85, bars=1)
    for u in (1.05, 4.10, 7.15):
        win(RU, u, 0.65, 1.90, 1.85, bars=1)
    sc.line((2.20, -0.04, 4.75), (2.20, -1.55, 4.75), DRK, sw=3.2, bias=0.8)
    hs = Face(sc, (1.15, -1.50, 3.35), X, Z, NY, ref=(2.2, -1.50, 3.9))
    hs.rect(0.0, 0.0, 2.10, 1.30, MUS, sw=2.4, scol=shade(FAS, NY), rad=0.12)
    return sc


# ------------------------------------------------------------------ 11
def r02():
    """CAFE / GLASS PAVILION — the smallest building carries the loudest colour."""
    sc = Scene()
    w, d = 10.0, 6.8
    x0 = -5.0
    h = 3.40
    mass(sc, x0, 2.30, 0, 3.05, d - 2.30, h + 0.12, BRK, top=False)
    mass(sc, x0, 0, 0, w, d, h, GLS, top=False, arris=False, sw=1.4)
    f = Face(sc, (x0, 0, 0), X, Z, NY, ref=(x0 + w / 2, 0, h / 2))
    r = Face(sc, (x0 + w, 0, 0), Y, Z, X, ref=(x0 + w, d / 2, h / 2))
    shopfront(f, 0.30, 0.0, 4.65, h - 0.22, stall=0.0, bays=3)
    door(f, 5.45, 0.0, 1.25, 2.40, ORG, glazed=1.75)
    shopfront(f, 7.05, 0.0, 2.65, h - 0.22, stall=0.0, bays=2)
    shopfront(r, 0.45, 0.0, 5.90, h - 0.22, stall=0.0, bays=4)
    for xx in (x0 + 0.14, x0 + 5.15, x0 + w - 0.14):
        post(sc, xx, 0.05, 0, h, DRK, 0.085)
    slab(sc, x0, 0, h, w, d, 0.68, FELT, ORG, ov=0.92)
    for xx in (x0 - 0.70, x0 + w + 0.70):
        post(sc, xx, -0.70, 0, h, DRK, 0.085)
    cf = Face(sc, (x0 - 0.92, -0.92, h), X, Z, NY, ref=(x0 + w / 2, -0.92, h + 0.34))
    sc.text3(cf, (w + 1.84) / 2, 0.19, "CAF&#201;", 0.44, FAS, weight="700",
             ls=0.20, out=0.06)
    flue(sc, x0 + 1.45, 3.90, h + 0.62, 1.00, CONC, 0.32)
    return sc


# ------------------------------------------------------------------ 12
def r03():
    """POST OFFICE / HYBRID — pitched house, flat wing. Red used once, hard."""
    sc = Scene()
    hw, hd = 7.20, 7.80
    x0 = -7.0
    e1, e2 = 2.95, 5.70
    f1, r1, _ = mass(sc, x0, 0, 0, hw, hd, e1, BRK, top=False)
    f2, r2, _ = mass(sc, x0, 0, e1, hw, hd, e2 - e1, RND, top=False)
    roof_x(sc, x0, 0, e2, hw, hd, 1.70, TILG, ov=0.58, ovg=0.48, fas=0.38)
    flue(sc, x0 + hw * 0.26, hd * 0.45, e2 + 1.30, 1.20, CONC, 0.36)
    for u, ww in ((0.70, 2.10), (3.35, 1.65), (5.35, 1.15)):
        win(f2, u, 0.55, ww, 1.55, bars=1)
    win(f1, 0.70, 0.90, 2.45, 1.65, bars=2)
    door(f1, 3.70, 0.0, 1.10, 2.25, GRN, glazed=0.85)
    win(f1, 5.35, 0.90, 1.15, 1.65, bars=1)
    win(r2, 1.20, 0.55, 1.85, 1.55, bars=1)
    win(r1, 1.20, 0.90, 2.15, 1.65, bars=1)
    sx = x0 + hw
    sw_, sd = 7.10, 6.90
    fw, rw, _ = mass(sc, sx, 0.60, 0, sw_, sd, 3.52, BRK, top=False)
    slab(sc, sx, 0.60, 3.52, sw_, sd, 0.44, FELT, RED, ov=0.34)
    shopfront(fw, 0.50, 0.0, 4.15, 2.80, stall=0.62, stallmat=BRK2, bays=3)
    door(fw, 5.20, 0.0, 1.25, 2.35, RED, glazed=1.60)
    fs = Face(sc, (sx - 0.34, 0.26, 3.52), X, Z, NY, ref=(sx + 3.5, 0.26, 3.74))
    sc.text3(fs, 3.90, 0.13, "POST OFFICE", 0.30, FAS, weight="700", ls=0.11, out=0.06)
    shopfront(rw, 0.60, 0.0, 5.20, 2.80, stall=0.62, stallmat=BRK2, bays=3)
    return sc


CONCEPTS = [
    ("H-01", "DETACHED &#183; DATUM",           "brick base, render above, shallow pitch — the control",  "9.6 &#215; 7.4 m &#183; 2 storeys &#183; pitched", h01),
    ("H-02", "DETACHED &#183; GABLE TO STREET", "one shape, cut open by a full-height light slot",        "8.2 &#215; 9.4 m &#183; 2 storeys &#183; pitched", h02),
    ("H-03", "DETACHED &#183; DEEP OVERSAIL",   "the roof is the architecture — timber over glass",       "10.8 &#215; 7.8 m &#183; 2 storeys &#183; flat", h03),
    ("H-04", "SEMI &#183; STAGGERED MONOPITCH", "one family, two steps, one slope each",                  "15.8 &#215; 10.9 m &#183; 2 storeys &#183; mono", h04),
    ("F-01", "APARTMENTS &#183; SHIFTED STACK", "brick base, banded render, one tall stair tower",     "13.6 &#215; 9.4 m &#183; 3 storeys &#183; flat", f01),
    ("F-02", "MAISONETTES &#183; DECK ACCESS",  "the horizontal building — four doors, four colours",     "16.0 &#215; 9.6 m &#183; 2 storeys &#183; flat", f02),
    ("V-01", "VILLAGE HALL &#183; BUTTERFLY",   "one civic shape, clerestory light, deep canopy",         "17.4 &#215; 10.6 m &#183; 1 volume &#183; butterfly", v01),
    ("V-02", "SURGERY &#183; ROOF MONITORS",    "light from the roof, not the wall",                      "13.8 &#215; 10.0 m &#183; 1 storey &#183; flat + monitors", v02),
    ("P-01", "PUB &#183; LONG PITCH + WING",    "the town's one dark colour, held low",                   "20.7 &#215; 8.8 m &#183; 2 storeys &#183; pitched + flat", p01),
    ("R-01", "CORNER SHOP &#183; CHAMFER",      "the plan turns the corner, the fascia wraps",            "11.6 &#215; 9.4 m &#183; 2 storeys &#183; flat", r01),
    ("R-02", "CAF&#201; &#183; GLASS PAVILION", "smallest building, loudest colour",                      "10.0 &#215; 6.8 m &#183; 1 storey &#183; flat", r02),
    ("R-03", "POST OFFICE &#183; HYBRID",       "pitched house, flat wing — red used once",               "14.3 &#215; 7.8 m &#183; 2 storeys &#183; pitched + flat", r03),
]
