"""
lovable — ERA Sheet 03, "Becoming Lovable".

The building is locked at the S-06/S-07 voice. Nothing here touches massing,
roof pitch, window sizes or proportions. Every treatment is an act of care
added AROUND the constant building: paint, plants, light, signage, furniture.
Charm from care, not clutter — each treatment is one coherent story, six or
fewer elements.
"""
import math
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY, depth as _d
from era_lang import (BRK, BRK2, BRK3, RND, RND2, FAS, CONC, TIMD, TIML,
                      TILB, TILG, FELT, GLS, GLSI, DRK, INK,
                      GRN, NVY, RED, ORG, MUS, TEAL, OLV, PNK,
                      nrm, vis, face, win, door, boarding, slab, mass, stack)
from charm import hero, satf
from stylize import ladder

LEAF = (104, 138, 66)
LEAF2 = (84, 120, 58)
WARM = (255, 214, 120)


def base(accent, **kw):
    """the locked voice: midpoint of S-06 and S-07, dressing knobs off"""
    return ladder(0.625, accent=accent, awning=False, barge=False, **kw)


def build(accent=GRN, glass=None, deco=None):
    ctx = {}
    p = base(accent)
    if glass is not None:
        p["glass"] = glass
    sc = hero(p, ctx)
    if deco:
        deco(ctx)
    return sc


# ------------------------------------------------------------------ atoms
def vdot(sc, x, y, z, r, col, op=1.0, n=NY):
    """a soft dot in the vertical camera-facing plane"""
    sc.poly([(x - r, y, z - r), (x + r, y, z - r),
             (x + r, y, z + r), (x - r, y, z + r)],
            col, n=n, rad=r, sw=0, stroke=False, op=op)


def hdisc(sc, x, y, z, r, col, sw=1.2):
    """a horizontal disc (table top, pot rim)"""
    sc.poly([(x - r, y - r, z), (x + r, y - r, z),
             (x + r, y + r, z), (x - r, y + r, z)], col, n=Z, rad=r, sw=sw)


def blob(sc, x, y, z, r, col):
    """a shrub / foliage ball: two offset dots"""
    vdot(sc, x, y, z, r, mul(col, 0.88))
    vdot(sc, x - r * 0.28, y - 0.02, z + r * 0.30, r * 0.72,
         mix(col, (255, 255, 240), 0.16))


def pot(sc, x, y, r, col=CONC, planted=LEAF):
    sc.poly([(x - r, y, 0), (x + r, y, 0), (x + r * 0.78, y, r * 1.5),
             (x - r * 0.78, y, r * 1.5)][::-1], col, n=NY, rad=0.05, sw=1.2)
    blob(sc, x, y - 0.02, r * 1.5 + r * 0.85, r * 0.95, planted)


def flowerrow(sc, x, y, z, w, cols, r=0.10):
    n = max(3, int(w / 0.30))
    for i in range(n):
        xx = x + w * (i + 0.5) / n
        blobcol = LEAF if i % 2 else LEAF2
        vdot(sc, xx, y - 0.03, z + 0.06, 0.13, blobcol)
        vdot(sc, xx, y - 0.06, z + 0.20, r, cols[i % len(cols)])


def windowbox(ctx, cu, cv, ww, cols, boxcol=None):
    """a timber box under a window cill, planted"""
    sc, F, K = ctx["sc"], ctx["F"], ctx["K"]
    x0, y0 = ctx["x0"], ctx["y0"]
    u0, w = cu - ww / 2, ww
    v0 = cv - 0.22 - 0.30
    F.rect(u0 - 0.06, v0, w + 0.12, 0.30, K(boxcol or TIMD), out=0.20, sw=1.5,
           rad=0.06)
    flowerrow(sc, x0 + u0, y0 - 0.30, v0 + 0.26, w, [K(c) for c in cols])


def climber(ctx, u=0.30, spread=1.9, bloom=None):
    """a trained climbing plant up the wall corner — wires, not wilderness"""
    sc, F, K = ctx["sc"], ctx["F"], ctx["K"]
    x0, y0, wh = ctx["x0"], ctx["y0"], ctx["wh"]
    F.line(u, 0.3, u, wh - 0.7, mul(LEAF2, 0.8), sw=2.0, out=0.06)
    pts = [(u, 0.5, 0.46), (u - 0.1, 1.4, 0.55), (u + 0.28, 2.3, 0.50),
           (u - 0.05, 3.2, 0.58), (u + 0.36, 4.0, 0.46), (u, 4.55, 0.40),
           (u + spread * 0.45, 4.72, 0.34), (u + spread * 0.9, 4.60, 0.28)]
    for (uu, vv, r) in pts:
        vdot(sc, x0 + uu, y0 - 0.16, vv, r, K(LEAF) if (vv * 7) % 2 < 1
             else K(LEAF2))
    if bloom:
        for (uu, vv, r) in pts[1::2]:
            vdot(sc, x0 + uu + r * 0.5, y0 - 0.22, vv + r * 0.5, 0.11, K(bloom))


def doormat(ctx):
    sc, x0, y0, du, dw = ctx["sc"], ctx["x0"], ctx["y0"], ctx["du"], ctx["dw"]
    sc.poly([(x0 + du - 0.1, y0 - 0.12, 0.02), (x0 + du + dw + 0.1, y0 - 0.12, 0.02),
             (x0 + du + dw + 0.1, y0 - 0.78, 0.02), (x0 + du - 0.1, y0 - 0.78, 0.02)],
            mul(TIMD, 0.85), n=Z, rad=0.08, sw=1.0)


def housenumber(ctx):
    F, K, du, dw, dh = ctx["F"], ctx["K"], ctx["du"], ctx["dw"], ctx["dh"]
    F.rect(du + dw + 0.22, dh - 0.42, 0.30, 0.30, K(FAS), out=0.05, sw=1.3,
           rad=0.05)


def porchlight(ctx, glow=True):
    sc, F, K = ctx["sc"], ctx["F"], ctx["K"]
    x0, y0, du, dh = ctx["x0"], ctx["y0"], ctx["du"], ctx["dh"]
    u = du - 0.42
    F.rect(u - 0.09, dh - 0.30, 0.18, 0.34, DRK, out=0.10, sw=1.2, rad=0.05)
    F.rect(u - 0.06, dh - 0.25, 0.12, 0.20, WARM, out=0.12, sw=0, stroke=False)
    if glow:
        vdot(sc, x0 + u, y0 - 0.24, dh - 0.14, 0.34, WARM, op=0.30)


def bracketlamp(ctx, xu, zv, on_annex=False):
    """a wall lamp on an arm"""
    ctxF = ctx["AF"] if on_annex else ctx["F"]
    sc, K = ctx["sc"], ctx["K"]
    xw = (ctx["ax0"] if on_annex else ctx["x0"]) + xu
    yw = (ctx["ay0"] if on_annex else ctx["y0"])
    ctxF.line(xu, zv, xu, zv - 0.30, DRK, sw=2.4, out=0.05)
    sc.line((xw, yw, zv - 0.30), (xw, yw - 0.42, zv - 0.36), DRK, sw=2.4, bias=0.3)
    vdot(sc, xw, yw - 0.46, zv - 0.52, 0.13, WARM)
    vdot(sc, xw, yw - 0.46, zv - 0.52, 0.30, WARM, op=0.25)


def gutterwork(ctx, col):
    """gutter along the eaves + a downpipe with a shoe — in a chosen colour"""
    sc, K = ctx["sc"], ctx["K"]
    ex0, ex1, ey0 = ctx["ex0"], ctx["ex1"], ctx["ey0"]
    wh, fasd = ctx["wh"], ctx["fasd"]
    x0, y0, w = ctx["x0"], ctx["y0"], ctx["w"]
    c = K(col)
    zg = wh - fasd + 0.10                 # tucked against the fascia
    sc.line((ex0, ey0, zg), (ex1, ey0, zg), c, sw=3.4, bias=0.30)
    px = x0 + w - 0.30
    sc.line((px, y0 - 0.10, zg), (px, y0 - 0.10, 0.25), c, sw=3.4, bias=0.28)
    sc.line((px, y0 - 0.10, 0.25), (px - 0.28, y0 - 0.22, 0.10), c, sw=3.4, bias=0.28)
    for zz in (1.2, 2.6, 4.0):
        sc.line((px - 0.09, y0 - 0.08, zz), (px + 0.09, y0 - 0.08, zz), c,
                sw=2.0, bias=0.29)


def soldiercourse(ctx, cu, cv, ww):
    """a flat band of upright bricks over an opening — craft, not ornament"""
    F, KW = ctx["F"], ctx["KW"]
    c = KW(BRK2)
    u0 = cu - ww / 2 - 0.10
    F.rect(u0, cv, ww + 0.20, 0.17, c, out=0.03, sw=1.2, rad=0.03)
    n = int((ww + 0.2) / 0.16)
    for i in range(1, n):
        uu = u0 + (ww + 0.2) * i / n
        F.line(uu, cv + 0.015, uu, cv + 0.155, mul(c, 0.82), sw=0.9, out=0.05)


def chimneypots(ctx):
    sc, KW = ctx["sc"], ctx["KW"]
    cx, ym, ctop, cwd = ctx["cx"], ctx["ym"], ctx["ctop"], ctx["cwd"]
    for k in (-0.25, 0.25):
        px = cx + cwd / 2 + k * cwd * 0.8
        mass(sc, px - 0.13, ym - 0.13, ctop, 0.26, 0.26, 0.46, KW(TILB),
             sw=1.2, arris=False)
        hdisc(sc, px, ym, ctop + 0.47, 0.10, DRK, sw=0)


def aerial(ctx):
    sc = ctx["sc"]
    cx, ym, ctop, cwd = ctx["cx"], ctx["ym"], ctx["ctop"], ctx["cwd"]
    mx = cx + cwd * 0.15
    sc.line((mx, ym, ctop + 0.2), (mx, ym, ctop + 1.35), DRK, sw=1.4, bias=0.2)
    for i, ll in enumerate((0.55, 0.42, 0.30)):
        zz = ctop + 1.30 - i * 0.16
        sc.line((mx - ll / 2, ym, zz), (mx + ll / 2, ym, zz), DRK, sw=1.2, bias=0.2)


def pad(sc, x, y, w, d, col=None):
    """a paving pad that grounds a freestanding prop — care, not shadow"""
    sc.poly([(x, y, 0.012), (x + w, y, 0.012), (x + w, y + d, 0.012),
             (x, y + d, 0.012)], col or (228, 224, 214), n=Z, rad=0.12, sw=1.0,
            scol=(210, 205, 192))


def gardenwall(ctx, gy=-4.25, gatecol=None):
    """lawn, low brick wall, timber gate on the door axis, path, two shrubs"""
    sc, K, KW = ctx["sc"], ctx["K"], ctx["KW"]
    x0, y0, w, du, dw = ctx["x0"], ctx["y0"], ctx["w"], ctx["du"], ctx["dw"]
    gx0, gx1 = x0 + du - 0.30, x0 + du + dw + 0.30          # gate gap
    lawn = (196, 214, 158)
    # lawn panels flanking the path (lowest)
    sc.poly([(x0 - 0.45, y0 - 0.35, 0.008), (gx0 - 0.15, y0 - 0.35, 0.008),
             (gx0 - 0.15, gy + 0.35, 0.008), (x0 - 0.45, gy + 0.35, 0.008)],
            lawn, n=Z, rad=0.18, sw=1.0, scol=(178, 196, 142))
    sc.poly([(gx1 + 0.15, y0 - 0.35, 0.008), (x0 + w + 0.9, y0 - 0.35, 0.008),
             (x0 + w + 0.9, gy + 0.35, 0.008), (gx1 + 0.15, gy + 0.35, 0.008)],
            lawn, n=Z, rad=0.18, sw=1.0, scol=(178, 196, 142))
    # path
    sc.poly([(gx0 + 0.02, y0 - 0.05, 0.015), (gx1 - 0.02, y0 - 0.05, 0.015),
             (gx1 - 0.02, gy - 0.05, 0.015), (gx0 + 0.02, gy - 0.05, 0.015)],
            (232, 228, 218), n=Z, rad=0.10, sw=1.1, scol=(210, 205, 192))
    for k in range(1, 5):
        yy = y0 - 0.05 + (gy - y0) * k / 5.0
        sc.line((gx0 + 0.10, yy, 0.02), (gx1 - 0.10, yy, 0.02),
                (208, 202, 190), sw=1.0, bias=0.02)
    wallh, wt = 0.58, 0.30
    mass(sc, x0 - 0.45, gy, 0, gx0 - (x0 - 0.45), wt, wallh, KW(BRK),
         sw=1.5, tmat=KW(CONC), arris=False)
    mass(sc, gx1, gy, 0, x0 + w + 0.9 - gx1, wt, wallh, KW(BRK),
         sw=1.5, tmat=KW(CONC), arris=False)
    gc = K(gatecol or ctx["ac"])
    gf = Face(sc, (gx0, gy + 0.02, 0), X, Z, NY, ref=(gx0 + 0.5, gy, 0.5))
    for i in range(5):
        uu = 0.06 + (gx1 - gx0 - 0.12 - 0.14) * i / 4
        gf.rect(uu, 0.04, 0.14, wallh + 0.14 - 0.10 * abs(i - 2), gc,
                sw=1.1, rad=0.05)
    gf.line(0.04, 0.30, gx1 - gx0 - 0.08, 0.30, mul(gc, 0.80), sw=1.6)
    blob(sc, x0 + 1.15, gy + 0.85, 0.62, 0.58, LEAF)
    blob(sc, x0 + w - 0.55, gy + 0.85, 0.50, 0.48, LEAF2)


def bench(ctx, bx, by):
    sc, K = ctx["sc"], ctx["K"]
    for k in (0.14, 1.46):
        mass(sc, bx + k, by, 0, 0.10, 0.42, 0.42, DRK, sw=1.0, top=False,
             arris=False)
    slab(sc, bx, by, 0.42, 1.70, 0.46, 0.07, K(TIML), K(TIML), ov=0.0,
         arris=False)
    sc.line((bx, by + 0.02, 0.78), (bx + 1.70, by + 0.02, 0.78), shade(K(TIML), NY),
            sw=3.4, bias=0.3)
    sc.line((bx, by + 0.02, 0.92), (bx + 1.70, by + 0.02, 0.92), shade(K(TIML), NY),
            sw=3.4, bias=0.3)


def bicycle(ctx, bx, by, col=None):
    sc, K = ctx["sc"], ctx["K"]
    c = K(col or ctx["ac"])
    r = 0.33
    for k in (0.0, 1.06):
        vdot(sc, bx + k, by, r, r, DRK)
        vdot(sc, bx + k, by, r, r * 0.62, mix(DRK, (255, 255, 255), 0.28))
        vdot(sc, bx + k, by, r, r * 0.16, DRK)
    fb = (bx + 0.53, by, r + 0.02)
    sc.line((bx, by, r), fb, c, sw=2.6, bias=0.31)
    sc.line(fb, (bx + 0.92, by, 0.86), c, sw=2.6, bias=0.31)
    sc.line(fb, (bx + 0.40, by, 0.92), c, sw=2.6, bias=0.31)
    sc.line((bx + 0.40, by, 0.92), (bx + 1.06, by, r), c, sw=2.6, bias=0.31)
    sc.line((bx + 0.92, by, 0.86), (bx + 1.06, by, r), c, sw=2.6, bias=0.31)
    sc.line((bx + 0.34, by, 0.92), (bx + 0.46, by, 0.92), DRK, sw=3.0, bias=0.31)
    sc.line((bx + 0.88, by, 0.86), (bx + 1.00, by, 0.95), DRK, sw=2.4, bias=0.31)


def lamppost(ctx, lx, ly, glow=True):
    sc = ctx["sc"]
    mass(sc, lx - 0.06, ly - 0.06, 0, 0.12, 0.12, 3.5, DRK, sw=1.2, top=False,
         arris=False)
    mass(sc, lx - 0.15, ly - 0.15, 3.5, 0.30, 0.30, 0.34, DRK, sw=1.2,
         arris=False)
    if glow:
        vdot(sc, lx, ly - 0.16, 3.66, 0.16, WARM)
        vdot(sc, lx, ly - 0.16, 3.66, 0.40, WARM, op=0.22)


def postbox(ctx, px, py):
    sc = ctx["sc"]
    r = (206, 32, 41)
    mass(sc, px - 0.24, py - 0.24, 0, 0.48, 0.48, 1.15, r, sw=1.6, top=False,
         arris=False)
    hdisc(sc, px, py, 1.15, 0.30, mul(r, 0.92), sw=1.4)
    hdisc(sc, px, py, 1.24, 0.10, mul(r, 0.8), sw=0)
    sc.line((px - 0.13, py - 0.25, 0.92), (px + 0.13, py - 0.25, 0.92), INK,
            sw=2.6, bias=0.3)


def noticeboard(ctx, cu, cv, ww=1.5, hh=1.05):
    F, K = ctx["F"], ctx["K"]
    F.rect(cu - ww / 2 - 0.07, cv, ww + 0.14, hh + 0.14, K(TIMD), out=0.08,
           sw=1.5, rad=0.06)
    F.rect(cu - ww / 2, cv + 0.07, ww, hh, mix(K(FAS), (200, 190, 160), 0.35),
           out=0.10, sw=1.2)
    for (a, b, pw, ph) in ((0.12, 0.16, 0.30, 0.38), (0.55, 0.30, 0.34, 0.30),
                           (1.02, 0.14, 0.30, 0.42), (0.20, 0.62, 0.42, 0.28)):
        F.rect(cu - ww / 2 + a, cv + 0.07 + b, pw, ph, (252, 250, 242),
               out=0.12, sw=0.8)


def awning_striped(ctx, col, drop=0.5):
    """a striped shop awning over the big ground window"""
    sc, K, ws = ctx["sc"], ctx["K"], ctx["ws"]
    x0, y0 = ctx["x0"], ctx["y0"]
    gww = ctx["gww"]
    au = ctx["gwc"] - gww / 2 - 0.22
    aw = gww + 0.44
    az = ctx["gwv"] + ctx["gwh"] / 2 + 0.34
    ad = 0.72
    c = K(col)
    n = 7
    for i in range(n):
        u0 = au + aw * i / n
        u1 = au + aw * (i + 1) / n
        cc = c if i % 2 == 0 else (252, 250, 244)
        sc.poly([(x0 + u0, y0 + 0.02, az + drop), (x0 + u1, y0 + 0.02, az + drop),
                 (x0 + u1, y0 - ad, az), (x0 + u0, y0 - ad, az)],
                cc, n=nrm((0, -drop, ad)), sw=0.8, rad=0.03)
    # scalloped hem
    for i in range(n):
        u0 = au + aw * (i + 0.5) / n
        cc = c if i % 2 == 0 else (252, 250, 244)
        vdot(sc, x0 + u0, y0 - ad, az - 0.055, aw / n / 2 * 0.92, cc)


def fascia_sign(ctx, text, col, cu=None, ww=None, letters=FAS):
    """a painted sign board on the front wall, over the ground window"""
    sc, F, K = ctx["sc"], ctx["F"], ctx["K"]
    cu = cu if cu is not None else ctx["gwc"]
    ww = ww if ww is not None else ctx["gww"] + 0.7
    F.rect(cu - ww / 2, 2.62, ww, 0.56, K(col), out=0.10, sw=1.6, rad=0.09)
    sc.text3(F, cu, 2.78, text, 0.30, K(letters), weight="700", ls=0.07,
             out=0.14)


def hangingsign(ctx, boardcol, blobcol):
    """a projecting pub/shop sign on an iron bracket"""
    sc, K = ctx["sc"], ctx["K"]
    x0, y0, w = ctx["x0"], ctx["y0"], ctx["w"]
    sx = x0 + w - 0.55
    sc.line((sx, y0, 4.35), (sx, y0 - 1.05, 4.35), DRK, sw=2.6, bias=0.3)
    sc.line((sx, y0, 4.35), (sx, y0 - 0.55, 4.62), DRK, sw=1.8, bias=0.3)
    bx, bz = sx, 4.30
    for (yy0, yy1) in ((-0.82, -0.28),):
        sc.poly([(bx, y0 + yy0, bz), (bx, y0 + yy1, bz),
                 (bx, y0 + yy1, bz - 0.72), (bx, y0 + yy0, bz - 0.72)],
                K(boardcol), n=X, sw=1.8, rad=0.06)
    sc.poly([(bx, y0 - 0.72, bz - 0.14), (bx, y0 - 0.38, bz - 0.14),
             (bx, y0 - 0.38, bz - 0.58), (bx, y0 - 0.72, bz - 0.58)],
            K(blobcol), n=X, sw=0, stroke=False, rad=0.17)


def aboard(ctx, bx, by, col):
    sc, K = ctx["sc"], ctx["K"]
    c = K(col)
    sc.poly([(bx - 0.34, by, 0), (bx + 0.34, by, 0),
             (bx + 0.26, by - 0.16, 0.88), (bx - 0.26, by - 0.16, 0.88)],
            c, n=nrm((0, -0.88, 0.16)), sw=1.6, rad=0.05)
    sc.poly([(bx - 0.26, by - 0.02, 0.16), (bx + 0.26, by - 0.02, 0.16),
             (bx + 0.22, by - 0.14, 0.74), (bx - 0.22, by - 0.14, 0.74)],
            INK, n=nrm((0, -0.88, 0.16)), sw=0, stroke=False, rad=0.03)
    for (za, zb) in ((0.60, 0.60), (0.48, 0.48), (0.36, 0.36)):
        sc.line((bx - 0.15, by - 0.12, za), (bx + 0.12, by - 0.12, zb),
                (250, 248, 240), sw=1.3, bias=0.31, op=0.8)


def terrace(ctx, tx, ty):
    """one round table, two stools — a café's front step"""
    sc, K = ctx["sc"], ctx["K"]
    mass(sc, tx - 0.045, ty - 0.045, 0, 0.09, 0.09, 0.70, DRK, sw=1.0,
         top=False, arris=False)
    hdisc(sc, tx, ty, 0.70, 0.44, K(FAS), sw=1.6)
    for k in (-0.75, 0.75):
        mass(sc, tx + k - 0.17, ty + 0.10 - 0.17, 0, 0.34, 0.34, 0.44, K(TIML),
             sw=1.2, arris=False)


def planters(ctx, col=None):
    sc, K = ctx["sc"], ctx["K"]
    x0, y0, w, du, dw = ctx["x0"], ctx["y0"], ctx["w"], ctx["du"], ctx["dw"]
    pot(sc, x0 + du - 0.75, y0 - 0.42, 0.26)
    pot(sc, x0 + du + dw + 0.75, y0 - 0.42, 0.26)


# ------------------------------------------------------------- treatments
def t01(ctx):        # control
    pass


def t02(ctx):        # the front door
    doormat(ctx)
    housenumber(ctx)
    porchlight(ctx)
    planters(ctx)


def t03(ctx):        # window boxes
    K = ctx["K"]
    windowbox(ctx, ctx["gwc"], ctx["gwv"] - ctx["gwh"] / 2 + 0.32,
              ctx["gww"] * 0.96, [RED, MUS, PNK])
    windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.35 * 1.25, [PNK, RED])
    windowbox(ctx, 3.45, ctx["bv"] - 0.55, 1.35 * 1.25, [MUS, RED])
    doormat(ctx)


def t04(ctx):        # the climber
    climber(ctx, u=0.32, spread=2.1, bloom=PNK)
    doormat(ctx)
    porchlight(ctx, glow=False)


def t05(ctx):        # the front garden
    gardenwall(ctx, gatecol=None)
    doormat(ctx)


def t06(ctx):        # craft — the fabric cared for
    gutterwork(ctx, ctx["ac"])
    soldiercourse(ctx, ctx["gwc"], ctx["gwv"] + ctx["gwh"] / 2 + 0.14, ctx["gww"])
    soldiercourse(ctx, 1.15, ctx["bv"] + 1.30 * 1.25 / 2 + 0.12, 1.35 * 1.25)
    soldiercourse(ctx, 3.45, ctx["bv"] + 1.30 * 1.25 / 2 + 0.12, 1.35 * 1.25)
    soldiercourse(ctx, ctx["du"] + ctx["dw"] / 2, ctx["dh"] + 0.16, ctx["dw"] + 0.3)
    chimneypots(ctx)
    aerial(ctx)


def halo(ctx, cu, cv, ww, hh):
    ctx["F"].rect(cu - ww / 2 - 0.20, cv - hh / 2 - 0.20, ww + 0.40, hh + 0.40,
                  WARM, out=0.17, sw=0, stroke=False, op=0.20, rad=0.24)


def t07(ctx):        # evening — architectural light
    ws, ws2, bv = ctx["ws"], min(ctx["ws"], 1.32), ctx["bv"]
    halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    halo(ctx, 1.15, bv, 1.35 * ws2, 1.30 * ws2)
    halo(ctx, 3.45, bv, 1.35 * ws2, 1.30 * ws2)
    halo(ctx, 5.95, bv, 1.10 * ws2, 1.20 * ws2)
    porchlight(ctx)
    bracketlamp(ctx, 1.10, 2.30, on_annex=True)
    pad(ctx["sc"], ctx["x0"] - 2.2, -2.6, 1.2, 1.2)
    lamppost(ctx, ctx["x0"] - 1.6, -2.0)


def t08(ctx):        # café
    awning_striped(ctx, ctx["ac"])
    fascia_sign(ctx, "CAF&#201;", ctx["ac"])
    pad(ctx["sc"], ctx["x0"] + 0.4, -2.75, 3.4, 2.1)
    terrace(ctx, ctx["x0"] + 1.75, -1.85)
    aboard(ctx, ctx["x0"] + 4.35, -1.55, ctx["ac"])


def t09(ctx):        # pub identity
    fascia_sign(ctx, "THE HOME END", ctx["ac"], cu=ctx["gwc"],
                ww=ctx["gww"] + 0.55, letters=MUS)
    hangingsign(ctx, ctx["ac"], MUS)
    bracketlamp(ctx, 1.10, 2.30, on_annex=True)
    planters(ctx)
    doormat(ctx)


def t10(ctx):        # post & parish
    pad(ctx["sc"], ctx["x0"] - 2.0, -1.95, 1.1, 1.1)
    postbox(ctx, ctx["x0"] - 1.45, -1.4)
    noticeboard(ctx, 4.10, 0.55, ww=0.85, hh=0.95)
    fascia_sign(ctx, "POST OFFICE", ctx["ac"], ww=ctx["gww"] + 1.3)
    doormat(ctx)


def t11(ctx):        # the street's edge
    pad(ctx["sc"], ctx["x0"] + 0.55, -2.85, 2.4, 1.3)
    bench(ctx, ctx["x0"] + 0.9, -2.35)
    bicycle(ctx, ctx["x0"] + 4.6, -1.45)
    pad(ctx["sc"], ctx["x0"] + ctx["w"] + 1.0, -2.3, 1.2, 1.2)
    lamppost(ctx, ctx["x0"] + ctx["w"] + 1.55, -1.75, glow=False)


def t12(ctx):        # lived-in — the synthesis
    doormat(ctx)
    porchlight(ctx)
    windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.35 * 1.25, [RED, MUS])
    windowbox(ctx, 3.45, ctx["bv"] - 0.55, 1.35 * 1.25, [PNK, RED])
    gutterwork(ctx, ctx["ac"])
    chimneypots(ctx)
    bicycle(ctx, ctx["x0"] + 4.35, -1.35)


TREATMENTS = [
    ("L-01", "CONTROL &#183; THE LOCKED VOICE",
     "S-06/S-07 undressed — the yardstick every treatment answers to",
     "no additions", ORG, None, t01),
    ("L-02", "THE FRONT DOOR",
     "number, porch light, doormat, two pots — the smallest act of pride",
     "entrance treatment only", GRN, None, t02),
    ("L-03", "WINDOW BOXES",
     "planted timber boxes under three cills; flowers in the accent family",
     "3 boxes &#183; tended, not overgrown", RED, None, t03),
    ("L-04", "THE CLIMBER",
     "one plant trained up the corner on wires — care visible in the training",
     "1 climber &#183; restrained bloom", OLV, None, t04),
    ("L-05", "THE FRONT GARDEN",
     "low brick wall, timber gate on the door axis, path, two shrubs",
     "boundary &#183; threshold &#183; path", NVY, None, t05),
    ("L-06", "CRAFT",
     "painted gutters and downpipe, soldier courses, chimney pots, an aerial",
     "the fabric itself cared for", TEAL, None, t06),
    ("L-07", "EVENING",
     "lit rooms, a porch lamp, a wall lantern, one street lamp — home at dusk",
     "architectural lighting", MUS, (246, 210, 130), t07),
    ("L-08", "CAF&#201;",
     "striped awning, painted fascia, one table and two stools, an A-board",
     "commerce as hospitality", ORG, GLSI, t08),
    ("L-09", "PUB &#183; THE HOME END",
     "painted fascia, hanging sign on an iron bracket, lantern, planted pots",
     "identity worn on the building", GRN, GLSI, t09),
    ("L-10", "POST &#38; PARISH",
     "pillar box, parish notice board, painted fascia — the civic version",
     "the building serves the town", RED, None, t10),
    ("L-11", "THE STREET&#8217;S EDGE",
     "a bench, a leaning bicycle, a lamp post — life implied, no people",
     "public furniture only", NVY, None, t11),
    ("L-12", "LIVED-IN &#183; SYNTHESIS",
     "door + boxes + gutters + pots + a bicycle — several small acts, one home",
     "the candidate blend", GRN, None, t12),
]


def build_treatment(i):
    code, name, note, spec, accent, glass, fn = TREATMENTS[i]
    return build(accent=accent, glass=glass, deco=fn)
