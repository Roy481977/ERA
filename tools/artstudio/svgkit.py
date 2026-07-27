"""
svgkit — a tiny vector-illustration engine for ERA concept sheets.

Not a modeller. It is a drawing instrument: axonometric three-quarter
projection, painter-sorted flat polygons, one fixed light, soft arris
highlights, and a global corner-rounding pass that gives every form the
slightly-soft edge the ERA language asks for.
"""
import math

# ---------------------------------------------------------------- view
AZ = math.radians(34.0)
EL = math.radians(19.0)
ca, sa = math.cos(AZ), math.sin(AZ)
ce, se = math.cos(EL), math.sin(EL)
CDIR = (sa * ce, -ca * ce, se)          # origin -> camera


def set_view(az_deg, el_deg):
    """Change the shared camera. The sheet camera is 34/19 (production
    three-quarter); the walking camera is 34/6.5 (a resident's eyes)."""
    global AZ, EL, ca, sa, ce, se, CDIR, PERSP
    PERSP = None
    AZ = math.radians(az_deg)
    EL = math.radians(el_deg)
    ca, sa = math.cos(AZ), math.sin(AZ)
    ce, se = math.cos(EL), math.sin(EL)
    CDIR = (sa * ce, -ca * ce, se)


# ------------------------------------------------------------ perspective
PERSP = None                  # (CP, R, U, F, near) when the camera is a person


def set_persp(cx, cy, cz, az_deg, el_deg, near=0.6):
    """The camera stops documenting: a position, an aim, a lens.
    az/el keep their meaning; the camera now stands somewhere."""
    global PERSP, AZ, EL, ca, sa, ce, se, CDIR
    AZ = math.radians(az_deg)
    EL = math.radians(el_deg)
    ca, sa = math.cos(AZ), math.sin(AZ)
    ce, se = math.cos(EL), math.sin(EL)
    CDIR = (sa * ce, -ca * ce, se)          # scene -> camera (culling keeps working)
    F = (-sa * ce, ca * ce, -se)            # camera forward
    R = (ca, sa, 0.0)
    U = (-sa * se, ca * se, ce)
    PERSP = ((cx, cy, cz), R, U, F, near)


def _cam(p):
    CP, R, U, F, near = PERSP
    d = (p[0] - CP[0], p[1] - CP[1], p[2] - CP[2])
    return (d[0] * R[0] + d[1] * R[1] + d[2] * R[2],
            d[0] * U[0] + d[1] * U[1] + d[2] * U[2],
            d[0] * F[0] + d[1] * F[1] + d[2] * F[2])


def _clip_near(cpts, near):
    """Sutherland-Hodgman against z = near, in camera space."""
    out = []
    n = len(cpts)
    for i in range(n):
        a, b = cpts[i], cpts[(i + 1) % n]
        ain, bin_ = a[2] >= near, b[2] >= near
        if ain:
            out.append(a)
        if ain != bin_:
            t = (near - a[2]) / (b[2] - a[2])
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, near))
    return out


def persp_poly(pts):
    """world pts -> (projected pts, sort key) or None if fully behind."""
    CP, R, U, F, near = PERSP
    cpts = [_cam(p) for p in pts]
    cpts = _clip_near(cpts, near)
    if len(cpts) < 3:
        return None
    zs = [c[2] for c in cpts]
    key = -sum(zs) / len(zs)
    return [(c[0] / c[2], -c[1] / c[2]) for c in cpts], key


def persp_line(a, b):
    CP, R, U, F, near = PERSP
    ca_, cb = _cam(a), _cam(b)
    if ca_[2] < near and cb[2] < near:
        return None
    if ca_[2] < near or cb[2] < near:
        t = (near - ca_[2]) / (cb[2] - ca_[2])
        m = (ca_[0] + (cb[0] - ca_[0]) * t, ca_[1] + (cb[1] - ca_[1]) * t, near)
        if ca_[2] < near:
            ca_ = m
        else:
            cb = m
    key = -(ca_[2] + cb[2]) / 2
    return [(ca_[0] / ca_[2], -ca_[1] / ca_[2]),
            (cb[0] / cb[2], -cb[1] / cb[2])], key


def _fixkey(fix):
    """Ground layers use magic ortho fixes (-50..-49); remap them far behind
    everything in perspective mode, preserving their relative order."""
    if PERSP is not None and fix is not None and fix <= -45.0:
        return -100000.0 + (fix + 50.0) * 10.0
    return fix

SUN = (-0.30, -0.52, 0.80)
_sl = math.sqrt(sum(c * c for c in SUN))
SUN = tuple(c / _sl for c in SUN)


def proj(p):
    if PERSP is not None:
        c = _cam(p)
        z = c[2] if c[2] > 0.05 else 0.05
        return (c[0] / z, -c[1] / z)
    X, Y, Z = p
    sx = X * ca + Y * sa
    sy = -X * sa * se + Y * ca * se + Z * ce
    return (sx, -sy)


def depth(p):
    if PERSP is not None:
        return -_cam(p)[2]
    return p[0] * CDIR[0] + p[1] * CDIR[1] + p[2] * CDIR[2]


def _newell(pts):
    nx = ny = nz = 0.0
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    n = (nx / l, ny / l, nz / l)
    if sum(n[i] * CDIR[i] for i in range(3)) < 0:
        n = (-n[0], -n[1], -n[2])
    return n


# ---------------------------------------------------------------- colour
def hexc(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def mul(rgb, f):
    return tuple(max(0, min(255, c * f)) for c in rgb)


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def shade(rgb, n):
    d = max(0.0, sum(n[i] * SUN[i] for i in range(3)))
    f = 0.815 + 0.315 * d
    out = mul(rgb, f)
    if f < 0.93:
        out = mix(out, (96, 116, 148), 0.085)      # sky bounce in shade
    else:
        out = mix(out, (255, 248, 228), 0.06)      # warm sun on the lit planes
    return out


# ---------------------------------------------------------------- rounding
def _round_path(pts, r):
    n = len(pts)
    if n < 3 or r <= 0.15:
        return "M " + " L ".join("%.2f,%.2f" % p for p in pts) + " Z"
    ent, ext, rad = [], [], []
    for i in range(n):
        p0, p1, p2 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1 = math.hypot(*v1) or 1e-6
        l2 = math.hypot(*v2) or 1e-6
        rr = min(r, l1 * 0.45, l2 * 0.45)
        ent.append((p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr))
        ext.append((p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr))
        rad.append(rr)
    d = "M %.2f,%.2f" % ext[0]
    for k in range(1, n + 1):
        i = k % n
        d += " L %.2f,%.2f" % ent[i]
        if rad[i] > 0.30:
            d += " Q %.2f,%.2f %.2f,%.2f" % (pts[i][0], pts[i][1], ext[i][0], ext[i][1])
        else:
            d += " L %.2f,%.2f" % ext[i]
    return d + " Z"


# ---------------------------------------------------------------- scene
class Scene:
    def __init__(self):
        self.items = []
        self.texts = []

    def poly(self, pts, rgb, n=None, bias=0.0, flat=False,
             stroke=True, sw=2.0, op=1.0, scol=None, rad=0.30, fix=None):
        if n is None:
            n = _newell(pts)
        col = rgb if flat else shade(rgb, n)
        s = col if scol is None else scol
        if PERSP is not None:
            pp = persp_poly(pts)
            if pp is None:
                return col
            spts, key = pp
            d = _fixkey(fix) if fix is not None else key + bias
            self.items.append(("poly", d, spts, col, sw, stroke, op, s, rad))
            return col
        d = fix if fix is not None else sum(depth(p) for p in pts) / len(pts) + bias
        self.items.append(("poly", d, [proj(p) for p in pts], col, sw, stroke, op, s, rad))
        return col

    def line(self, a, b, rgb, sw=1.6, bias=0.02, op=1.0, cap="round", fix=None):
        if PERSP is not None:
            pl = persp_line(a, b)
            if pl is None:
                return
            spts, key = pl
            d = _fixkey(fix) if fix is not None else key + bias
            self.items.append(("line", d, spts, rgb, sw, cap, op))
            return
        d = fix if fix is not None else (depth(a) + depth(b)) / 2 + bias
        self.items.append(("line", d, [proj(a), proj(b)], rgb, sw, cap, op))

    def emit(self, ox, oy, s):
        out = []
        for it in sorted(self.items, key=lambda i: i[1]):
            if it[0] == "poly":
                _, _, pts, col, sw, stroke, op, scol, rad = it
                sp = [(ox + x * s, oy + y * s) for x, y in pts]
                c = hexc(col)
                st = (' stroke="%s" stroke-width="%.2f" stroke-linejoin="round"'
                      % (hexc(scol), sw)) if stroke and sw > 0 else ' stroke="none"'
                o = ' fill-opacity="%.3f"' % op if op < 1 else ''
                r_px = rad * s if PERSP is None else min(rad * s, 15.0)
                out.append('<path d="%s" fill="%s"%s%s/>'
                           % (_round_path(sp, r_px), c, st, o))
            else:
                _, _, pts, col, sw, cap, op = it
                (x1, y1), (x2, y2) = pts
                out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                           'stroke-width="%.2f" stroke-linecap="%s" stroke-opacity="%.3f"/>'
                           % (ox + x1 * s, oy + y1 * s, ox + x2 * s, oy + y2 * s,
                              hexc(col), sw, cap, op))
        for m, u, v, txt, size, col, anchor, weight, ls in self.texts:
            M = (m[0] * s, m[1] * s, m[2] * s, m[3] * s,
                 ox + m[4] * s, oy + m[5] * s)
            out.append('<g transform="matrix(%.5f,%.5f,%.5f,%.5f,%.3f,%.3f)">'
                       '<text x="%.4f" y="%.4f" font-family="Helvetica,Arial,sans-serif" '
                       'font-size="%.4f" font-weight="%s" letter-spacing="%.4f" fill="%s" '
                       'text-anchor="%s">%s</text></g>'
                       % (M[0], M[1], M[2], M[3], M[4], M[5], u, -v, size, weight,
                          ls, hexc(col), anchor, txt))
        return "\n".join(out)

    def text3(self, face, u, v, txt, size, col, anchor="middle",
              weight="700", ls=0.0, out=0.02):
        self.texts.append((face.matrix(out), u, v, txt, size, col, anchor, weight, ls))

    def bounds(self):
        xs, ys = [], []
        for it in self.items:
            for x, y in it[2]:
                xs.append(x); ys.append(y)
        return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- faces
class Face:
    """A drawing plane. Everything drawn on it inherits the parent surface's
    sort key, so coplanar detail never falls behind its own wall."""

    def __init__(self, sc, O, ax, ay, n, eps=0.012, ref=None):
        self.sc, self.O, self.ax, self.ay, self.n, self.eps = sc, O, ax, ay, n, eps
        self.bd = depth(ref if ref is not None else O)
        self.layer = 0

    def _k(self):
        self.layer += 1
        return self.bd + 0.0055 * self.layer

    def p(self, u, v, out=0.0):
        e = self.eps + out
        return tuple(self.O[i] + self.ax[i] * u + self.ay[i] * v + self.n[i] * e
                     for i in range(3))

    def rect(self, u, v, w, h, rgb, out=0.0, sw=1.2, stroke=True, flat=False,
             op=1.0, scol=None, rad=0.11):
        pts = [self.p(u, v, out), self.p(u + w, v, out),
               self.p(u + w, v + h, out), self.p(u, v + h, out)]
        return self.sc.poly(pts, rgb, n=self.n, flat=flat, stroke=stroke,
                            sw=sw, op=op, scol=scol, rad=rad, fix=self._k())

    def line(self, u1, v1, u2, v2, rgb, sw=1.4, out=0.0, op=1.0):
        self.sc.line(self.p(u1, v1, out), self.p(u2, v2, out), rgb, sw=sw,
                     op=op, fix=self._k())

    def poly(self, uv, rgb, out=0.0, sw=1.2, stroke=True, flat=False, op=1.0,
             scol=None, rad=0.11):
        pts = [self.p(u, v, out) for u, v in uv]
        return self.sc.poly(pts, rgb, n=self.n, flat=flat, stroke=stroke,
                            sw=sw, op=op, scol=scol, rad=rad, fix=self._k())

    def matrix(self, out=0.0):
        o = proj(self.p(0, 0, out))
        x = proj(self.p(1, 0, out))
        y = proj(self.p(0, 1, out))
        return (x[0] - o[0], x[1] - o[1], -(y[0] - o[0]), -(y[1] - o[1]), o[0], o[1])


X = (1, 0, 0)
Y = (0, 1, 0)
Z = (0, 0, 1)
NX = (-1, 0, 0)
NY = (0, -1, 0)
