"""
charm — the parametric hero for ERA Sheet 02, the stylization passes.

One building, every axis of charm exposed as a knob. The architecture is held
constant so that the ONLY variable on the sheet is the voice:

    chunk   proportion / weight        (plinth, fascia, chimney, canopy)
    swell   walls lean outward, m      (storybook taper, top wider than base)
    belly   mid-height bulge, m        (the loaf-of-bread silhouette)
    roofk   roof rise multiplier
    ov      eaves overhang, metres
    fas     fascia depth, metres       (scaled by chunk)
    rrad    corner rounding on roof planes, metres
    wins    window scale               (about the opening centre)
    doors   door scale
    sat     saturation push            (roof and brick internally capped)
    line    base stroke weight
    wob     deterministic vertex jitter, metres   (built by hands)
    sag     ridge sag, metres
    awning  accent awning over the ground-floor window + accent garage door
    barge   barge boards take the accent colour
    ink     uniform dark drawn outline on everything (post-process)
    accent  the one accent colour
"""
import math
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY
from era_lang import (BRK, BRK2, BRK3, RND, RND2, FAS, CONC, TIMD, TIML,
                      TILB, TILG, FELT, GLS, GLSI, DRK, INK,
                      nrm, vis, face, win, door, boarding, slab, stack)

INKC = (56, 50, 46)


def satf(c, k):
    """push a colour away from grey — the vibrancy knob"""
    if k <= 0:
        return c
    m = (c[0] + c[1] + c[2]) / 3.0
    return tuple(max(0, min(255, m + (ci - m) * (1 + k) + 4 * k)) for ci in c)


def _h(a, b, c):
    """deterministic noise in [-1, 1] from three coordinates"""
    s = math.sin(a * 12.9898 + b * 78.233 + c * 37.719) * 43758.5453
    return (s - math.floor(s)) * 2.0 - 1.0


def hero(P, ctx=None):
    sc = Scene()
    sat = P["sat"]
    K = lambda c: satf(c, sat)            # accents, joinery
    KW = lambda c: satf(c, sat * 0.55)    # walls, roof — capped so brick
    ac = K(P["accent"])                   # and tile stay materials
    ch = P["chunk"]
    lw = P["line"]
    wob = P["wob"]
    belly = P.get("belly", 0.0)

    def W(p):
        if wob <= 0:
            return p
        z = p[2] + _h(p[2], p[0], p[1]) * wob * 0.55 if p[2] > 0.05 else p[2]
        return (p[0] + _h(p[0], p[1], p[2]) * wob,
                p[1] + _h(p[1], p[2], p[0]) * wob * 0.8, z)

    # ------------------------------------------------------------ main mass
    w, d = 7.4, 6.2
    x0, y0 = -5.4 + P.get("xoff", 0.0), P.get("yoff", 0.0)
    wh = 5.0
    s = P["swell"]                        # top rect grows s on every side
    mat = KW(BRK)
    wrad = P["wrad"] * 2.2 if belly <= 0 else 0.9

    # walls — planar trapezoids, or bellied 6-gons when the loaf knob is on
    hm, sm = wh * 0.52, s * 0.52
    cb = (sm + belly) * 0.7               # shared corner bulge, front-right edge
    fq = [(x0, y0, 0), (x0 + w, y0, 0)]
    if belly > 0:
        fq += [(x0 + w + cb, y0 - cb, hm)]
    fq += [(x0 + w + s, y0 - s, wh), (x0 - s, y0 - s, wh)]
    if belly > 0:
        fq += [(x0 - sm - belly, y0 - (sm + belly) * 0.4, hm)]
    rq = [(x0 + w, y0, 0), (x0 + w, y0 + d, 0)]
    if belly > 0:
        rq += [(x0 + w + cb, y0 + d + cb, hm)]
    rq += [(x0 + w + s, y0 + d + s, wh), (x0 + w + s, y0 - s, wh)]
    if belly > 0:
        rq += [(x0 + w + cb, y0 - cb, hm)]
    fn = nrm((0, -wh, -s))
    rn = nrm((wh, 0, -s))
    from svgkit import depth as _d
    fref = (x0 + w / 2, y0, wh / 2)
    rref = (x0 + w, y0 + d / 2, wh / 2)
    sc.poly([W(p) for p in fq], mat, n=fn, sw=lw, rad=wrad, fix=_d(fref) - 0.012)
    sc.poly([W(p) for p in rq], mat, n=rn, sw=lw, rad=wrad, fix=_d(rref) - 0.012)
    hl = mix(shade(mat, Z), (255, 255, 255), 0.24)
    sc.line(W((x0 - s, y0 - s, wh)), W((x0 + w + s, y0 - s, wh)), hl, sw=1.6, bias=0.09)
    sc.line(W((x0 + w + s, y0 - s, wh)), W((x0 + w + s, y0 + d + s, wh)), hl, sw=1.6, bias=0.09)

    # drawing planes riding the tapered walls
    F = Face(sc, (x0, y0, 0), X, (0, -s / wh, 1), fn, ref=fref)
    R = Face(sc, (x0 + w, y0, 0), Y, (s / wh, 0, 1), rn, ref=rref)

    # plinth — the house plants itself
    pl = 0.14 + 0.24 * ch
    F.rect(-0.02, 0.0, w + 0.04, pl, KW(BRK2), sw=1.4, rad=0.06)
    R.rect(-0.02, 0.0, d + 0.04, pl, KW(BRK2), sw=1.4, rad=0.06)

    # first-floor band in render — one move of relief
    F.rect(0.0, 2.86, w, 2.14, KW(RND), sw=1.6, rad=0.10)
    R.rect(0.0, 2.86, d, 2.14, KW(RND), sw=1.6, rad=0.10)

    # ------------------------------------------------------------ openings
    ws, ds = P["wins"], P["doors"]
    ws2 = min(ws, 1.32)                   # first floor capped clear of eaves

    def cwin(f, cu, cv, ww, hh, k, **kw):
        win(f, cu - ww * k / 2, cv - hh * k / 2, ww * k, hh * k, **kw)

    gkw = {}
    if P.get("glass") is not None:
        gkw = {"glass": K(P["glass"])}
    bv = 3.90 - 0.30 * max(0.0, P["ov"] - 0.45)         # duck under deep eaves
    cwin(F, 1.85, 1.55, 2.30, 1.55, ws, bars=2, **gkw)  # big ground window
    cwin(F, 1.15, bv, 1.35, 1.30, ws2, bars=1, **gkw)   # bedroom 1
    cwin(F, 3.45, bv, 1.35, 1.30, ws2, bars=1, **gkw)   # bedroom 2
    cwin(F, 5.95, bv, 1.10, 1.20, ws2, bars=1, **gkw)   # over the door
    cwin(R, 1.70, 1.60, 1.30, 1.40, ws, bars=1, **gkw)  # return, ground
    cwin(R, 1.70, bv, 1.15, 1.20, ws2, bars=1, **gkw)   # return, first

    dw, dh = 1.02 * ds, 2.12 * min(ds, 1.14)
    du = 5.30 - dw / 2
    door(F, du, 0.0, dw, dh, ac, glazed=1.35 * min(ws, 1.2))
    F.rect(du - 0.22, 0.0, dw + 0.44, 0.10, KW(CONC), sw=1.0, rad=0.04)  # step

    # door canopy — the friendliness of the entrance
    cw = dw + 0.55 + 0.55 * ch
    cd = 0.52 + 0.48 * ch
    slab(sc, x0 + du - (cw - dw) / 2, y0 - cd, dh + 0.24,
         cw, cd, 0.13 + 0.13 * ch, K(FAS), ac, ov=0.05 * ch)

    # awning over the big window
    if P["awning"]:
        gw2 = 2.30 * ws
        au, aw = 1.85 - gw2 / 2 - 0.20, gw2 + 0.40
        az = 1.55 + (1.55 * ws) / 2 + 0.20
        ad = 0.85
        aq = [(x0 + au, y0 + 0.02, az + 0.46), (x0 + au + aw, y0 + 0.02, az + 0.46),
              (x0 + au + aw, y0 - ad, az), (x0 + au, y0 - ad, az)]
        sc.poly(aq, ac, n=nrm((0, -0.46, ad)), sw=lw, rad=0.14)
        sc.line((x0 + au, y0 - ad, az), (x0 + au + aw, y0 - ad, az),
                mix(ac, (255, 255, 255), 0.35), sw=2.2, bias=0.16)

    # ------------------------------------------------------------ roof
    rise = 2.30 * P["roofk"]
    ov = P["ov"]
    sag = P["sag"]
    fasd = P["fas"] * (0.7 + 0.4 * ch)
    rrad = min(P["rrad"], 0.55)
    tx0, tx1 = x0 - s, x0 + w + s
    ty0, ty1 = y0 - s, y0 + d + s
    ex0, ex1 = tx0 - ov * 0.8, tx1 + ov * 0.8
    ey0, ey1 = ty0 - ov, ty1 + ov
    ym, zr = (ty0 + ty1) / 2.0, wh + rise
    xm = (ex0 + ex1) / 2.0
    tile = KW(TILB)

    fslope = [(ex0, ey0, wh), (ex1, ey0, wh), (ex1, ym, zr)]
    if sag > 0:
        fslope += [(xm, ym, zr - sag)]
    fslope += [(ex0, ym, zr)]
    sc.poly([W(p) for p in fslope], tile, n=nrm((0, -rise, (d / 2 + ov))),
            sw=lw, rad=rrad)
    bslope = [(ex0, ym, zr), (ex1, ym, zr), (ex1, ey1, wh), (ex0, ey1, wh)]
    sc.poly([W(p) for p in bslope], tile, n=nrm((0, rise, (d / 2 + ov))),
            sw=lw, rad=rrad)
    # gable on the camera end
    sc.poly([W(p) for p in [(tx1, ty0, wh), (tx1, ty1, wh), (tx1, ym, zr - sag * 0.6)]],
            KW(RND), n=X, sw=lw, rad=min(rrad, 0.4))

    # eaves fascia (front) + barge boards following the +X slopes
    bmat = ac if P["barge"] else K(FAS)
    face(sc, [W(p) for p in [(ex0, ey0, wh - fasd), (ex1, ey0, wh - fasd),
                             (ex1, ey0, wh), (ex0, ey0, wh)]], NY, bmat, sw=lw * 0.9)
    face(sc, [W(p) for p in [(ex1, ey0, wh - fasd), (ex1, ym, zr - fasd - sag),
                             (ex1, ym, zr - sag), (ex1, ey0, wh)]], X, bmat, sw=lw * 0.9)
    face(sc, [W(p) for p in [(ex1, ym, zr - fasd - sag), (ex1, ey1, wh - fasd),
                             (ex1, ey1, wh), (ex1, ym, zr - sag)]], X, bmat, sw=lw * 0.9)
    sc.line(W((ex0, ym, zr)), W((xm, ym, zr - sag)),
            mix(shade(tile, Z), (255, 255, 255), 0.34), sw=2.0, bias=0.12)
    sc.line(W((xm, ym, zr - sag)), W((ex1, ym, zr)),
            mix(shade(tile, Z), (255, 255, 255), 0.34), sw=2.0, bias=0.12)

    # chimney — girth follows chunk, plumb follows wob
    cwd = 0.55 + 0.55 * ch
    cx = x0 + w * 0.66
    tilt = wob * 2.4
    czb = zr - rise * 0.55
    stack(sc, cx + tilt, ym - cwd * 0.55 + tilt * 0.5, czb,
          zr + 0.80 + 0.42 * ch - czb, w=cwd, d=cwd * 0.78, mat=KW(BRK))

    # ------------------------------------------------------------ annex
    aw_, ad_, ah = 3.05, 5.30, 2.62
    ax0, ay0 = x0 + w - 0.02, y0 + 0.55
    s6 = s * 0.6
    aq1 = [(ax0, ay0, 0), (ax0 + aw_, ay0, 0),
           (ax0 + aw_ + s6, ay0 - s6, ah), (ax0, ay0 - s6, ah)]
    aq2 = [(ax0 + aw_, ay0, 0), (ax0 + aw_, ay0 + ad_, 0),
           (ax0 + aw_ + s6, ay0 + ad_ + s6, ah), (ax0 + aw_ + s6, ay0 - s6, ah)]
    am = KW(RND)
    arad = P["wrad"] * 2.2                # the annex never bellies — it stays crisp
    afr = (ax0 + aw_ / 2, ay0, ah / 2)
    arr = (ax0 + aw_, ay0 + ad_ / 2, ah / 2)
    sc.poly([W(p) for p in aq1], am, n=nrm((0, -ah, -s6)), sw=lw, rad=arad,
            fix=_d(afr) - 0.012)
    sc.poly([W(p) for p in aq2], am, n=nrm((ah, 0, -s6)), sw=lw, rad=arad,
            fix=_d(arr) - 0.012)
    AF = Face(sc, (ax0, ay0, 0), X, (0, -s6 / ah, 1),
              nrm((0, -ah, -s6)), ref=afr)
    AR = Face(sc, (ax0 + aw_, ay0, 0), Y, (s6 / ah, 0, 1),
              nrm((ah, 0, -s6)), ref=arr)
    AF.rect(0.0, 0.0, aw_, pl, KW(BRK2), sw=1.4, rad=0.06)
    gd = ac if P["awning"] else K(TIML)
    boarding(AF, 0.42, pl, 2.20, 2.05 - pl, gd)
    win(AR, 1.30, 1.30, 1.15 * ws, 1.05 * ws, bars=1)
    slab(sc, ax0 - s6, ay0 - s6, ah, aw_ + s6 * 2, ad_ + s6 * 2,
         0.14 + 0.16 * ch, KW(FELT), K(FAS), ov=0.12 + 0.28 * ch)

    # ------------------------------------------------------------ anchors
    if ctx is not None:
        ctx.update(dict(
            sc=sc, F=F, R=R, AF=AF, AR=AR, K=K, KW=KW,
            x0=x0, y0=y0, w=w, d=d, wh=wh, pl=pl, ch=ch, lw=lw, ac=ac,
            du=du, dw=dw, dh=dh, ws=ws, bv=bv, gwc=1.85, gwv=1.55,
            gww=2.30 * ws, gwh=1.55 * ws,
            ax0=ax0, ay0=ay0, aw=aw_, ad=ad_, ah=ah,
            cx=cx, ym=ym, zr=zr, cwd=cwd,
            ctop=zr + 0.80 + 0.42 * ch + 0.16,
            ov=ov, rise=rise, ex0=ex0, ex1=ex1, ey0=ey0, fasd=fasd,
            cz=dh + 0.24 + 0.13 + 0.13 * ch))

    # ------------------------------------------------------------ ink pass
    if P["ink"]:
        items = []
        for it in sc.items:
            if it[0] == "poly":
                kind, dd, pts, col, sw, stroke, op, scol, rad = it
                if stroke and op >= 1.0:
                    items.append((kind, dd, pts, col, max(sw, 2.5), True,
                                  op, INKC, rad))
                else:
                    items.append(it)
            else:
                items.append(it)
        sc.items = items

    return sc
