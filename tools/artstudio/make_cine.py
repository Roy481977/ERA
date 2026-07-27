import sys
import math
import svgkit
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY, hexc
from era_lang import *
from charm import hero
from lovable import (base, blob, vdot, hdisc, bench, bicycle, lamppost,
                     postbox, LEAF, LEAF2, WARM, halo, porchlight,
                     awning_striped, fascia_sign, hangingsign, aboard,
                     planters, doormat, windowbox, gardenwall)
from streets import (flags, brickpav, tarmac, grass, kerb, gband, tree,
                     hedgerow, bollard, bin70, belisha, zebra, planter,
                     chalk, FLAG, FLAGJ, PAVB, PAVBJ)
from places import (oak, wornpath, wornpatch, parishboard, floodlights,
                    barrel, lowwall, stream, WORN)
from walk import house
from district01 import washline

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-cine.svg"

W = 2124
MG = 40
GUT = 22
FW = (W - 2 * MG - GUT) / 2.0
FH = 620
ROWS = 4
H = int(64 + ROWS * (FH + GUT) + 30)

EVE = (246, 210, 130)
C = lambda sc: {"sc": sc, "K": lambda c: c}


def aim(cam, tgt):
    dx, dy, dz = tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    az = math.degrees(math.atan2(-dx / L, dy / L))
    el = math.degrees(math.asin(max(-1, min(1, -dz / L))))
    return az, el


# ---------------------------------------------------------------- frames
def f_oak():
    """standing beneath the Oak, looking toward the bakery"""
    sc = Scene()
    grass(sc, -6.0, 70.0, x0=-75.0, x1=45.0)
    oak(sc, 2.4, 7.5, s=1.6)
    vdot(sc, 1.2, 7.8, 4.1, 2.6, LEAF2)             # the low bough, top right
    vdot(sc, -0.6, 8.4, 4.6, 1.9, mix(LEAF2, LEAF, 0.5))
    wornpath(sc, 1.2, 6.5, -6.0, 16.0, w=1.15)
    parishboard(sc, -4.0, 14.5)
    def bak(ctx):
        fascia_sign(ctx, "BAKERY", MUS, letters=INK)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
    house(sc, MUS, -8.0, yoff=24.0, glass=GLSI, deco=bak)
    house(sc, GRN, -21.0, yoff=27.0)
    flags(sc, 22.5, 24.0, x0=-24.0, x1=2.0)
    ctx = C(sc)
    bench(ctx, 3.6, 9.5)
    bicycle(ctx, -5.5, 22.6, col=TEAL)
    return sc, (0, 0, 1.55), (-2.0, 24.0, 1.5), 1300, 0.55


def f_ginnel():
    """the gap between houses -- the green only hinted"""
    sc = Scene()
    grass(sc, -4.0, 60.0, x0=-40.0, x1=40.0)
    house(sc, OLV, -6.0, yoff=2.0)
    house(sc, TEAL, 6.8, yoff=2.0)
    washline(sc, -0.6, 9.0)
    wornpath(sc, 0.4, 3.0, 0.1, 17.0, w=1.0)
    flags(sc, 18.0, 20.5, x0=-20.0, x1=25.0)
    oak(sc, 1.2, 42.0, s=1.3, scarves=False)
    blob(sc, -2.2, 13.5, 0.7, 0.6, LEAF2)
    return sc, (0.25, -3.2, 1.5), (0.2, 18.0, 1.25), 1300, 0.56


def f_bridge():
    """leaning on the parapet; the children were here first"""
    sc = Scene()
    grass(sc, 9.5, 55.0, x0=-45.0, x1=45.0)
    stream(sc, 2.6, 9.5, x0=-45.0, x1=45.0)
    mass(sc, -7.0, 2.0, 0, 14.0, 0.45, 1.12, BRK, sw=1.6, top=True,
         tmat=CONC, arris=False)
    sc.line((-7.0, 2.0, 1.12), (7.0, 2.0, 1.12),
            mix(shade(CONC, Z), (255, 255, 255), 0.3), sw=2.2, bias=0.1)
    ctx = C(sc)
    vdot(sc, -2.4, 13.5, 0.26, 0.26, (250, 248, 242))
    bicycle(ctx, 2.6, 16.0, col=RED)
    bicycle(ctx, 4.4, 16.8, col=TEAL)
    chalk(sc, -6.0, 14.5, 2.4, 1.5)
    house(sc, PNK, -1.5, yoff=26.0)
    washline(sc, 7.6, 23.0)
    vdot(sc, -9.5, 10.5, 2.5, 1.9, LEAF2)
    vdot(sc, -7.9, 10.8, 1.6, 1.2, mix(LEAF2, LEAF, 0.5))
    mass(sc, -8.8, 10.2, 0, 0.26, 0.26, 1.9, mix(TIMD, (90, 70, 50), 0.3),
         sw=1.2, top=False, arris=False)
    tree(sc, -14.0, 19.0, s=1.3)
    return sc, (0, 0, 1.6), (0.3, 16.0, 0.45), 1320, 0.53


def f_cafe():
    """stopped at the notice board; the green waits beyond"""
    sc = Scene()
    grass(sc, -4.0, 60.0, x0=-45.0, x1=45.0)
    flags(sc, -1.0, 2.2, x0=-25.0, x1=12.0)
    parishboard(sc, -1.8, 3.0)
    wornpath(sc, 0.8, 3.5, 2.5, 22.0, w=1.1)
    oak(sc, 4.5, 24.0, s=1.5)
    ctx = C(sc)
    bench(ctx, 0.5, 20.0)
    def bak(cctx):
        fascia_sign(cctx, "BAKERY", MUS, letters=INK)
        halo(cctx, cctx["gwc"], cctx["gwv"], cctx["gww"], cctx["gwh"])
    house(sc, MUS, -16.0, yoff=20.0, glass=GLSI, deco=bak)
    house(sc, OLV, -28.0, yoff=23.0)
    blob(sc, 8.0, 14.0, 0.8, 0.7, LEAF2)
    return sc, (0.6, 0.0, 1.55), (-0.5, 18.0, 1.4), 1300, 0.54


def f_tide():
    """just after the tide -- the crossing settles"""
    sc = Scene()
    flags(sc, -3.0, 4.2, x0=-45.0, x1=30.0)
    tarmac(sc, 4.2, 9.8, x0=-45.0, x1=30.0)
    flags(sc, 9.8, 14.5, x0=-45.0, x1=30.0)
    grass(sc, 14.5, 50.0, x0=-45.0, x1=30.0)
    zebra(sc, -4.2, 4.4, 9.6, w=5.6)
    belisha(sc, 1.05, 3.2)
    ctx = C(sc)
    bicycle(ctx, -3.4, 14.5, col=OLV)
    bicycle(ctx, -1.6, 15.1, col=RED)
    vdot(sc, -5.6, 14.0, 0.24, 0.24, (250, 248, 242))
    chalk(sc, -7.4, 14.6, 2.6, 1.6)
    house(sc, RED, -13.5, yoff=19.0)
    house(sc, GRN, 2.5, yoff=21.0)
    return sc, (0, 0, 1.5), (-1.4, 18.0, 1.0), 1320, 0.54


def f_square():
    """the square to yourself; the pub's lamps just on"""
    sc = Scene()
    brickpav(sc, -4.0, 55.0, x0=-40.0, x1=45.0,
             col=mix(PAVB, FLAG, 0.42), j=mix(PAVBJ, FLAGJ, 0.4))
    chalk(sc, -1.8, 5.0, 2.6, 1.6)
    def pub(ctx):
        fascia_sign(ctx, "THE HOME END", GRN, ww=ctx["gww"] + 0.55, letters=MUS)
        hangingsign(ctx, GRN, MUS)
        halo(ctx, ctx["gwc"], ctx["gwv"], ctx["gww"], ctx["gwh"])
        porchlight(ctx)
    house(sc, GRN, 4.4, yoff=20.0, glass=EVE, deco=pub)
    barrel(sc, 0.4, 17.6)
    barrel(sc, 1.9, 16.9)
    ctx = C(sc)
    postbox(ctx, -3.4, 12.0)
    lamppost(ctx, -6.5, 14.0, glow=True)
    house(sc, RED, 16.0, yoff=24.0, glass=EVE)
    house(sc, NVY, -19.0, yoff=26.0, glass=EVE)
    return sc, (0, 0, 1.55), (1.2, 22.0, 1.5), 1300, 0.54


def f_home():
    """two floodlights above the rooftops, walking home"""
    sc = Scene()
    grass(sc, -4.0, 70.0, x0=-45.0, x1=-2.5)
    tarmac(sc, -4.0, 70.0, x0=-2.5, x1=1.5)
    flags(sc, -4.0, 70.0, x0=1.5, x1=4.5)
    grass(sc, -4.0, 70.0, x0=4.5, x1=45.0)
    floodlights(sc, (7.5, 12.5), y=58.0, h=13.5)
    house(sc, TEAL, 10.5, yoff=17.0, glass=EVE)
    house(sc, NVY, 10.0, yoff=33.0, glass=EVE)
    house(sc, OLV, 9.5, yoff=48.0, glass=EVE)
    lowwall(sc, -8.5, 7.0, 5.5, h=0.6)
    blob(sc, -9.6, 8.0, 0.8, 0.7, LEAF2)
    tree(sc, -6.5, 24.0, s=1.35)
    ctx = C(sc)
    lamppost(ctx, 2.6, 16.0, glow=True)
    lamppost(ctx, 3.0, 34.0, glow=True)
    return sc, (0, 0, 1.55), (1.5, 32.0, 1.1), 1300, 0.54


def f_gate():
    """the gate, last light -- the day lets you go"""
    sc = Scene()
    grass(sc, -4.0, 60.0, x0=-45.0, x1=45.0)
    flags(sc, 7.0, 10.0, x0=-30.0, x1=35.0)
    tarmac(sc, 10.0, 15.5, x0=-30.0, x1=35.0)
    lowwall(sc, -5.5, 5.0, 7.0, h=0.62)
    gf = Face(sc, (-1.2, 4.98, 0), X, Z, NY, ref=(0.0, 4.98, 0.6))
    for i in range(5):
        gf.rect(0.06 + i * 0.40, 0.04, 0.27, 0.80 - 0.10 * abs(i - 2), GRN,
                sw=1.1, rad=0.05)
    def home(ctx):
        porchlight(ctx, glow=True)
        doormat(ctx)
        windowbox(ctx, 1.15, ctx["bv"] - 0.55, 1.7, [RED, MUS])
    house(sc, GRN, -9.5, yoff=8.0, glass=EVE, deco=home)
    ctx = C(sc)
    lamppost(ctx, 5.0, 13.0, glow=True)
    house(sc, NVY, 12.5, yoff=24.0, glass=EVE)
    oak(sc, 1.5, 28.0, s=1.5, scarves=False)
    wornpath(sc, 0.2, 6.0, 1.2, 24.0, w=1.05)
    floodlights(sc, (11.0, 15.5), y=48.0, h=12.5)
    tree(sc, -10.0, 17.0, s=1.25)
    return sc, (0.4, -0.4, 1.5), (-1.0, 18.0, 1.3), 1300, 0.55


SKIES = [
    ((205, 224, 238), (255, 248, 233)),
    ((201, 222, 236), (252, 247, 234)),
    ((198, 222, 238), (247, 246, 238)),
    ((196, 220, 236), (248, 245, 235)),
    ((199, 216, 233), (250, 240, 224)),
    ((188, 200, 224), (253, 227, 195)),
    ((178, 190, 218), (250, 220, 186)),
    ((152, 165, 198), (244, 205, 168)),
]

BUMPS = [
    [(90, 26), (60, 18), (120, 30), (80, 22), (150, 26), (110, 20), (140, 28), (160, 24)],
    [(120, 22), (90, 28), (140, 20), (100, 26), (160, 24), (120, 20), (140, 26)],
    [(100, 24), (140, 30), (80, 20), (120, 26), (150, 22), (110, 28), (130, 20)],
    [(110, 26), (80, 20), (130, 28), (100, 22), (150, 26), (120, 30), (140, 22)],
    [(90, 22), (130, 28), (100, 20), (150, 26), (110, 24), (140, 20), (120, 28)],
    [(120, 26), (90, 20), (140, 28), (110, 22), (130, 26), (100, 20), (150, 24)],
    [(100, 24), (130, 20), (90, 26), (140, 22), (120, 28), (110, 20), (150, 26)],
    [(110, 22), (140, 28), (100, 24), (130, 20), (120, 26), (150, 22), (90, 26)],
]

FRAMES = [f_oak, f_ginnel, f_bridge, f_cafe, f_tide, f_square, f_home, f_gate]
LIGHTS = {6: [(0.28, 42), (0.46, 36)], 7: [(0.86, 34)]}

parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (W, H, W, H))
parts.append('<rect width="%d" height="%d" fill="#f4f2ed"/>' % (W, H))
parts.append('<text x="%d" y="42" font-family="Helvetica,Arial,sans-serif" '
             'font-size="15" font-weight="700" letter-spacing="3" '
             'fill="#8d887b">DISTRICT 01</text>' % MG)

DEFS = ['<defs>']
body = []

for i, fn in enumerate(FRAMES):
    c, r = i % 2, i // 2
    fx = MG + c * (FW + GUT)
    fy = 64 + r * (FH + GUT)
    top, bot = SKIES[i]
    DEFS.append('<linearGradient id="sky%d" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
                '</linearGradient>' % (i, hexc(top), hexc(bot)))
    DEFS.append('<clipPath id="clip%d"><rect x="%.1f" y="%.1f" width="%.1f" '
                'height="%.1f" rx="6"/></clipPath>' % (i, fx, fy, FW, FH))
    sc, cam, tgt, SCALE, vfrac = fn()
    az, el = aim(cam, tgt)
    svgkit.set_persp(cam[0], cam[1], cam[2], az, el)
    sc2, camx, tgtx, SCALEx, vfx = fn()          # rebuild under perspective
    ox = fx + 0.5 * FW
    oy = fy + vfrac * FH
    horizon = oy - SCALE * math.tan(math.radians(el))
    hazec = mix(mix(bot, (150, 160, 178), 0.38), (255, 255, 255), 0.18)
    body.append('<g clip-path="url(#clip%d)">' % i)
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#sky%d)"/>'
                % (fx, fy, FW, FH, i))
    # skyline
    y0 = horizon
    p = 'M %.1f,%.1f ' % (fx, y0 + 10)
    xcur = fx
    for (w_, h_) in BUMPS[i]:
        p += 'L %.1f,%.1f L %.1f,%.1f L %.1f,%.1f ' % (
            xcur, y0 - h_ * 0.35, xcur + w_ * 0.5, y0 - h_, xcur + w_, y0 - h_ * 0.35)
        xcur += w_
    p += 'L %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z' % (xcur, y0 + 10, fx + FW, fy + FH, fx, fy + FH)
    body.append('<path d="%s" fill="%s"/>' % (p, hexc(hazec)))
    for (lxf, lh) in LIGHTS.get(i, []):
        lx = fx + lxf * FW
        body.append('<rect x="%.1f" y="%.1f" width="3.2" height="%.1f" fill="%s"/>'
                    % (lx, y0 - lh, lh, hexc(mul(hazec, 0.86))))
        body.append('<rect x="%.1f" y="%.1f" width="15" height="8" rx="2" fill="%s"/>'
                    % (lx - 6, y0 - lh - 7, hexc(mul(hazec, 0.80))))
    body.append(sc2.emit(ox, oy, SCALE))
    body.append('</g>')
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
                'fill="none" stroke="#dcd7cb" stroke-width="1.2"/>' % (fx, fy, FW, FH))

DEFS.append('</defs>')
parts.append("".join(DEFS))
parts.append("".join(body))
parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
