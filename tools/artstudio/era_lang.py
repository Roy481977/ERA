"""
era_lang — the drawing vocabulary for the ERA architectural language sheet.

Masses, roofs and openings expressed as drawing operations, not assets.
"""
import math
import svgkit
from svgkit import (Scene, Face, proj, depth, shade, mix, mul, hexc,
                    X, Y, Z, NX, NY)

# ------------------------------------------------------------------ palette
BRK  = (200, 100,  72)   # the town brick
BRK2 = (160,  70,  58)   # dark plinth / engineering brick
BRK3 = (216, 164, 120)   # buff brick
RND  = (248, 244, 235)   # white render
RND2 = (236, 226, 208)   # warm render
FAS  = (253, 251, 246)   # painted fascia + joinery
CONC = (210, 204, 192)   # concrete, cills, copings
TIMD = (132,  88,  58)   # stained timber
TIML = (208, 164, 114)   # light timber
TILG = (134, 142, 160)   # blue slate tile
TILB = (200, 128,  90)   # warm clay tile
FELT = (148, 152, 160)   # single-ply flat roof
GLS  = ( 98, 128, 150)   # sky in the glass
GLSI = (214, 190, 146)   # a lit interior behind the glass
DRK  = ( 68,  70,  74)
INK  = ( 38,  40,  44)

ORG  = (242, 120,  44)
MUS  = (248, 188,  58)
OLV  = (138, 156,  72)
RED  = (218,  58,  44)
GRN  = ( 30, 108,  76)
NVY  = ( 28,  84, 136)
TEAL = ( 34, 148, 154)
PNK  = (232, 138, 124)

STOREY = 2.90
COMM   = 3.55


def nrm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / l for c in v)


def vis(n):
    return sum(n[i] * svgkit.CDIR[i] for i in range(3)) > 0.004


def face(sc, pts, n, mat, **kw):
    if not vis(n):
        return None
    return sc.poly(pts, mat, n=n, **kw)


# ------------------------------------------------------------------ masses
def mass(sc, x, y, z, w, d, h, mat, sw=2.2, top=True, arris=True, tmat=None):
    """Rectangular block. Returns (front, right, top) Faces."""
    f = Face(sc, (x, y, z), X, Z, NY, ref=(x + w / 2, y, z + h / 2))
    r = Face(sc, (x + w, y, z), Y, Z, X, ref=(x + w, y + d / 2, z + h / 2))
    t = Face(sc, (x, y, z + h), X, Y, Z, ref=(x + w / 2, y + d / 2, z + h))
    face(sc, [(x, y, z), (x + w, y, z), (x + w, y, z + h), (x, y, z + h)], NY, mat, sw=sw)
    face(sc, [(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)],
         X, mat, sw=sw)
    if top:
        face(sc, [(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)],
             Z, tmat or mat, sw=sw)
    if arris:
        hl = mix(shade(mat, Z), (255, 255, 255), 0.30)
        sc.line((x, y, z + h), (x + w, y, z + h), hl, sw=1.7, bias=0.09)
        sc.line((x + w, y, z + h), (x + w, y + d, z + h), hl, sw=1.7, bias=0.09)
        sc.line((x + w, y, z), (x + w, y, z + h),
                mix(shade(mat, X), (255, 255, 255), 0.22), sw=1.5, bias=0.09)
    return f, r, t


def prism(sc, foot, z, h, mat, sw=2.2, top=True, arris=True, tmat=None):
    """Vertical prism from a CCW footprint [(x,y),...]. Returns side Faces."""
    n = len(foot)
    faces = []
    for i in range(n):
        ax, ay = foot[i]
        bx, by = foot[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1.0
        nn = (dy / L, -dx / L, 0.0)
        if vis(nn):
            sc.poly([(ax, ay, z), (bx, by, z), (bx, by, z + h), (ax, ay, z + h)],
                    mat, n=nn, sw=sw)
            if arris:
                hl = mix(shade(mat, Z), (255, 255, 255), 0.30)
                sc.line((ax, ay, z + h), (bx, by, z + h), hl, sw=1.7, bias=0.09)
        faces.append(Face(sc, (ax, ay, z), (dx / L, dy / L, 0), Z, nn,
                          ref=((ax + bx) / 2, (ay + by) / 2, z + h / 2)))
    if top:
        sc.poly([(px, py, z + h) for px, py in foot], tmat or mat, n=Z, sw=sw)
    return faces


# ------------------------------------------------------------------ roofs
def roof_x(sc, x, y, z, w, d, rise, mat, ov=0.50, ovg=0.40, fas=0.34, fmat=FAS):
    """Pitched roof, ridge parallel to X — the slope faces the street."""
    y0, y1 = y - ov, y + d + ov
    x0, x1 = x - ovg, x + w + ovg
    ym, zr = y + d / 2.0, z + rise
    face(sc, [(x0, y0, z), (x1, y0, z), (x1, ym, zr), (x0, ym, zr)],
         nrm((0, -rise, (d / 2 + ov))), mat, sw=2.2)
    face(sc, [(x0, ym, zr), (x1, ym, zr), (x1, y1, z), (x0, y1, z)],
         nrm((0, rise, (d / 2 + ov))), mat, sw=2.2)
    face(sc, [(x1, y0, z), (x1, y1, z), (x1, ym, zr)], X, mat, sw=2.2)
    # eaves fascia
    face(sc, [(x0, y0, z - fas), (x1, y0, z - fas), (x1, y0, z), (x0, y0, z)], NY, fmat, sw=2.0)
    face(sc, [(x1, y0, z - fas), (x1, y1, z - fas), (x1, y1, z), (x1, y0, z)], X, fmat, sw=2.0)
    sc.line((x0, ym, zr), (x1, ym, zr), mix(shade(mat, Z), (255, 255, 255), 0.34),
            sw=2.0, bias=0.12)
    return zr


def roof_y(sc, x, y, z, w, d, rise, mat, ov=0.45, ovg=0.45, fas=0.34, fmat=FAS,
           gmat=None, gable=True):
    """Pitched roof, ridge parallel to Y — the gable faces the street."""
    y0, y1 = y - ovg, y + d + ovg
    x0, x1 = x - ov, x + w + ov
    xm, zr = x + w / 2.0, z + rise
    face(sc, [(x1, y0, z), (x1, y1, z), (xm, y1, zr), (xm, y0, zr)],
         nrm((rise, 0, w / 2 + ov)), mat, sw=2.2)
    face(sc, [(x0, y0, z), (xm, y0, zr), (xm, y1, zr), (x0, y1, z)],
         nrm((-rise, 0, w / 2 + ov)), mat, sw=2.2)
    if gable:
        face(sc, [(x0, y0, z), (x1, y0, z), (xm, y0, zr)], NY, gmat or mat, sw=2.2)
    face(sc, [(x1, y0, z - fas), (x1, y1, z - fas), (x1, y1, z), (x1, y0, z)], X, fmat, sw=2.0)
    sc.line((xm, y0, zr), (xm, y1, zr), mix(shade(mat, Z), (255, 255, 255), 0.34),
            sw=2.0, bias=0.12)
    return zr


def slab(sc, x, y, z, w, d, t, mat, fmat=None, ov=0.0, arris=True):
    """Flat roof / canopy slab with a painted edge."""
    fmat = fmat or mat
    x0, x1, y0, y1 = x - ov, x + w + ov, y - ov, y + d + ov
    face(sc, [(x0, y0, z), (x1, y0, z), (x1, y0, z + t), (x0, y0, z + t)], NY, fmat, sw=2.0)
    face(sc, [(x1, y0, z), (x1, y1, z), (x1, y1, z + t), (x1, y0, z + t)], X, fmat, sw=2.0)
    face(sc, [(x0, y0, z + t), (x1, y0, z + t), (x1, y1, z + t), (x0, y1, z + t)],
         Z, mat, sw=2.0)
    if arris:
        hl = mix(shade(mat, Z), (255, 255, 255), 0.34)
        sc.line((x0, y0, z + t), (x1, y0, z + t), hl, sw=1.8, bias=0.10)
        sc.line((x1, y0, z + t), (x1, y1, z + t), hl, sw=1.8, bias=0.10)
    return z + t


def mono(sc, x, y, z, w, d, zf, zb, mat, ov=0.45, t=0.26, fmat=FAS):
    """Single-slope slab. zf = front edge height, zb = back edge height."""
    x0, x1 = x - ov, x + w + ov
    y0, y1 = y - ov, y + d + ov
    n = nrm((0, -(zb - zf), (y1 - y0)))
    face(sc, [(x0, y0, zf), (x1, y0, zf), (x1, y1, zb), (x0, y1, zb)], n, mat, sw=2.2)
    face(sc, [(x0, y0, zf - t), (x1, y0, zf - t), (x1, y0, zf), (x0, y0, zf)], NY, fmat, sw=2.0)
    face(sc, [(x1, y0, zf - t), (x1, y1, zb - t), (x1, y1, zb), (x1, y0, zf)], X, fmat, sw=2.0)
    hl = mix(shade(mat, Z), (255, 255, 255), 0.30)
    sc.line((x0, y0, zf), (x1, y0, zf), hl, sw=1.7, bias=0.10)


def butterfly(sc, x, y, z, w, d, drop, mat, ov=0.45, t=0.26, fmat=FAS):
    x0, x1 = x - ov, x + w + ov
    y0, y1 = y - ov, y + d + ov
    ym, zl = y + d / 2.0, z - drop
    face(sc, [(x0, y0, z), (x1, y0, z), (x1, ym, zl), (x0, ym, zl)],
         nrm((0, drop, (d / 2 + ov))), mat, sw=2.2)
    face(sc, [(x0, ym, zl), (x1, ym, zl), (x1, y1, z), (x0, y1, z)],
         nrm((0, -drop, (d / 2 + ov))), mat, sw=2.2)
    face(sc, [(x0, y0, z - t), (x1, y0, z - t), (x1, y0, z), (x0, y0, z)], NY, fmat, sw=2.0)
    face(sc, [(x1, y0, z - t), (x1, ym, zl - t), (x1, ym, zl), (x1, y0, z)], X, fmat, sw=2.0)
    face(sc, [(x1, ym, zl - t), (x1, y1, z - t), (x1, y1, z), (x1, ym, zl)], X, fmat, sw=2.0)
    hl = mix(shade(mat, Z), (255, 255, 255), 0.32)
    sc.line((x0, y0, z), (x1, y0, z), hl, sw=1.8, bias=0.10)


def parapet(sc, x, y, z, w, d, h, t, mat, cap=CONC):
    mass(sc, x, y, z, w, t, h, mat, top=True, tmat=cap, arris=False)
    mass(sc, x + w - t, y, z, t, d, h, mat, top=True, tmat=cap, arris=False)
    hl = mix(shade(cap, Z), (255, 255, 255), 0.30)
    sc.line((x, y, z + h), (x + w, y, z + h), hl, sw=1.8, bias=0.12)
    sc.line((x + w, y, z + h), (x + w, y + d, z + h), hl, sw=1.8, bias=0.12)


# ------------------------------------------------------------------ openings
def win(f, u, v, w, h, glass=GLS, frame=FAS, cill=CONC, bars=0, hbar=0,
        out=0.0, refl=True, rec=0.10):
    fc = shade(frame, f.n)
    f.rect(u, v, w, h, mul(glass, 0.70), out=out - rec, sw=0, stroke=False)
    f.rect(u + 0.07, v + 0.07, w - 0.14, h - 0.14, glass, out=out - rec + 0.01,
           sw=3.0, scol=fc)
    for i in range(bars):
        uu = u + w * (i + 1) / (bars + 1)
        f.line(uu, v + 0.08, uu, v + h - 0.08, fc, sw=2.6, out=out - rec + 0.03)
    for i in range(hbar):
        vv = v + h * (i + 1) / (hbar + 1)
        f.line(u + 0.08, vv, u + w - 0.08, vv, fc, sw=2.6, out=out - rec + 0.03)
    if refl and w > 0.7 and h > 0.7:
        k = min(w, h) * 0.60
        f.poly([(u + 0.10, v + h - 0.10 - k), (u + 0.10 + k, v + h - 0.10),
                (u + 0.10 + k * 0.45, v + h - 0.10), (u + 0.10, v + h - 0.10 - k * 0.45)],
               (255, 255, 255), out=out - rec + 0.04, sw=0, stroke=False,
               flat=True, op=0.10)
    if cill:
        f.rect(u - 0.10, v - 0.16, w + 0.20, 0.16, cill, out=out + 0.05, sw=1.4)


def door(f, u, v, w, h, col, frame=FAS, glazed=0.0, out=0.0, handle=True):
    fc = shade(frame, f.n)
    f.rect(u - 0.09, v, w + 0.18, h + 0.09, frame, out=out - 0.09, sw=1.6)
    f.rect(u, v, w, h, col, out=out, sw=2.0)
    if glazed > 0:
        f.rect(u + 0.14, v + h - 0.14 - glazed, w - 0.28, glazed, GLS,
               out=out + 0.02, sw=2.2, scol=fc)
    if handle:
        f.rect(u + w - 0.20, v + h * 0.45, 0.06, 0.20, mix(CONC, (255, 255, 255), 0.3),
               out=out + 0.04, sw=0.8)


def shopfront(f, u, v, w, h, glass=None, frame=FAS, stall=0.62, stallmat=BRK2, bays=3,
              out=0.0):
    glass = glass or GLSI
    fc = shade(frame, f.n)
    if stall > 0:
        f.rect(u, v, w, stall, stallmat, out=out + 0.03, sw=1.8)
    zz = v + stall
    hh = h - stall
    f.rect(u, zz, w, hh, mul(glass, 0.72), out=out - 0.09, sw=0, stroke=False)
    f.rect(u + 0.06, zz + 0.06, w - 0.12, hh - 0.12, glass, out=out - 0.08, sw=3.2, scol=fc)
    for i in range(bays - 1):
        uu = u + w * (i + 1) / bays
        f.line(uu, zz + 0.06, uu, zz + hh - 0.06, fc, sw=3.4, out=out - 0.05)
    f.poly([(u + 0.14, zz + hh * 0.10), (u + 0.14 + hh * 0.55, zz + hh * 0.72),
            (u + 0.14 + hh * 0.25, zz + hh * 0.72), (u + 0.14, zz + hh * 0.42)],
           (255, 255, 255), out=out - 0.04, sw=0, stroke=False, flat=True, op=0.10)


def band(f, u, v, w, h, col, out=0.06, sw=2.0):
    return f.rect(u, v, w, h, col, out=out, sw=sw)


def boarding(f, u, v, w, h, col, pitch=0.24, out=0.0):
    f.rect(u, v, w, h, col, out=out, sw=1.8)
    dk = mul(shade(col, f.n), 0.86)
    n = int(w / pitch)
    for i in range(1, n):
        uu = u + w * i / n
        f.line(uu, v + 0.03, uu, v + h - 0.03, dk, sw=1.2, out=out + 0.02, op=0.75)


def hslats(f, u, v, w, h, col, pitch=0.22, out=0.0):
    f.rect(u, v, w, h, col, out=out, sw=1.8)
    dk = mul(shade(col, f.n), 0.84)
    n = int(h / pitch)
    for i in range(1, n):
        vv = v + h * i / n
        f.line(u + 0.03, vv, u + w - 0.03, vv, dk, sw=1.2, out=out + 0.02, op=0.75)


def post(sc, x, y, z, h, mat=DRK, r=0.09):
    mass(sc, x - r, y - r, z, 2 * r, 2 * r, h, mat, sw=1.2, top=False, arris=False)


def rail(sc, x, y, z, w, h, col, n=6, sw=2.2):
    sc.line((x, y, z + h), (x + w, y, z + h), shade(col, NY), sw=sw + 1.0, bias=0.30)
    sc.line((x, y, z + h * 0.5), (x + w, y, z + h * 0.5), shade(col, NY), sw=sw, bias=0.30)
    for i in range(n + 1):
        xx = x + w * i / n
        sc.line((xx, y, z), (xx, y, z + h), shade(col, NY), sw=sw * 0.7, bias=0.30)


def flue(sc, x, y, z, h, mat=CONC, w=0.42):
    mass(sc, x, y, z, w, w, h, mat, sw=1.6, arris=False)


def stack(sc, x, y, z, h, w=1.0, d=0.7, mat=BRK, cap=CONC):
    mass(sc, x, y, z, w, d, h, mat, sw=1.8, top=False, arris=False)
    mass(sc, x - 0.06, y - 0.06, z + h, w + 0.12, d + 0.12, 0.16, cap, sw=1.4, arris=False)
