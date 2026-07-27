import sys
import math
import svgkit
from svgkit import Scene, Face, shade, mix, mul, X, Y, Z, NX, NY, hexc
from era_lang import *
from district_level import LEVEL

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-build-v1.svg"

W = 2124
MX = 58

PAPER = "#ffffff"
RULE = "#dcd8ce"
TXT = "#22242a"
TXT2 = "#7b7e87"
TXT3 = "#a3a6ae"

# plan palette (module families)
C_ROAD = "#d6d3cb"
C_FLAG = "#eae6dc"
C_BRICK = "#e0cfc2"
C_WORN = "#d9c9a8"
C_GRASS = "#dbe5c2"
C_FIELD = "#cfdcae"
C_WATER = "#b9d0de"
C_BLD = "#c97a5e"
C_KIT = "#a85a42"
C_LM = "#6e6a5e"
C_ADJ = "#c04a30"

ACC = {"GRN": "#2f7a52", "NVY": "#1c5488", "RED": "#da3a2c", "ORG": "#f2782c",
       "MUS": "#f8bc3a", "OLV": "#8a9c48", "TEAL": "#22949a", "PNK": "#e88a7c"}

parts = []


def t(x, y, s, size, col=TXT, w="400", anchor="start", ls=0.0):
    parts.append('<text x="%.1f" y="%.1f" font-family="Helvetica,Arial,sans-serif" '
                 'font-size="%.1f" font-weight="%s" letter-spacing="%.2f" fill="%s" '
                 'text-anchor="%s">%s</text>' % (x, y, size, w, ls, col, anchor, s))


def rule(x1, y, x2, col=RULE, sw=1.5):
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.2f"/>' % (x1, y, x2, y, col, sw))


# ---------------------------------------------------------------- plan
EX0, EY0, EX1, EY1 = LEVEL["meta"]["extent"]
PLX, PLY = MX, 210
PS = (2124 - 2 * MX - 640) / (EX1 - EX0)      # leave right column for text
PLW = (EX1 - EX0) * PS
PLH = (EY1 - EY0) * PS


def PX(mx):
    return PLX + (mx - EX0) * PS


def PY(my):
    return PLY + (EY1 - my) * PS


def prect(x0, y0, x1, y1, col, r=4, op=1.0, stroke=None):
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
                 'fill="%s" opacity="%.2f" %s/>'
                 % (PX(x0), PY(y1), (x1 - x0) * PS, (y1 - y0) * PS, r, col, op,
                    ('stroke="%s" stroke-width="1"' % stroke) if stroke else ''))


def pline(pts, col, sw=2.0, dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % (PX(x), PY(y)) for x, y in pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linecap="round" stroke-linejoin="round" %s/>'
                 % (d, col, sw, ('stroke-dasharray="%s"' % dash) if dash else ''))


def pdot(x, y, r, col, stroke=None):
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" %s/>'
                 % (PX(x), PY(y), r, col,
                    ('stroke="%s" stroke-width="1.4"' % stroke) if stroke else ''))


def plab(x, y, s, size=11, col=TXT2, w="700", anchor="middle", ls=1.0):
    t(PX(x), PY(y), s, size, col, w, anchor=anchor, ls=ls)


# ---------------------------------------------------------------- header
t(MX, 80, "ERA", 48, TXT, "700", ls=6)
t(MX + 126, 80, "DISTRICT 01 &#8212; BUILD v1", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "THE LEVEL &#183; LAYOUT FROM DATA &#183; MODULES &#183; BUILD ORDER &#183; VALIDATION &#183; DEFINITION OF DONE",
  15, TXT2, "700", ls=2.2)
t(MX, 150, "Phase 1 discovered ERA; this constructs it. The layout below is generated from "
           "district_level.py &#8212; the data IS the level; this drawing is derived. Canon: CD-024&#8211;027, no reopened decisions.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION PACKAGE &#183; TOWARD PLAYABLE ALPHA 1", 13, TXT2, "700", anchor="end", ls=2.2)
t(W - MX, 150, "full module catalogue, build order, risks and DoD: era/design/district-01-build-v1.md",
  13, TXT2, "400", anchor="end")

# plan card
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="#fbfaf7" '
             'stroke="%s" stroke-width="1.5"/>' % (PLX - 10, PLY - 10, PLW + 20, PLH + 20, RULE))

# terrain
prect(EX0, EY0, EX1, EY1, C_GRASS, r=8)
tr = LEVEL["terrain"]
prect(*tr["playing_field"], C_FIELD)
plab((tr["playing_field"][0] + tr["playing_field"][2]) / 2, tr["playing_field"][1] + 3,
     "PLAYING FIELD", 10.5, "#94a476")
prect(*tr["allotments"], C_FIELD)
plab((tr["allotments"][0] + tr["allotments"][2]) / 2, tr["allotments"][1] + 3,
     "ALLOTMENTS", 10.5, "#94a476")
prect(*tr["ground_apron"], "#d8d3c6", op=0.6)

# water + bridge
wpts = LEVEL["water"]["pts"]
pline(wpts, C_WATER, sw=LEVEL["water"]["w"] * PS)
br = LEVEL["landmarks"]["bridge"]
prect(br["x"] - 0.6, br["y"] - 3.4, br["x"] + br["w"] + 0.6, br["y"] + 3.4, C_BRICK, r=2,
      stroke=C_ADJ)
plab(br["x"] + 3, br["y"] - 6.5, "BRIDGE &#183; ADJ-1", 9.5, C_ADJ)

# roads
for r_ in LEVEL["roads"]:
    prect(r_["x0"], r_["y0"], r_["x1"], r_["y1"], C_ROAD, r=3)
for z in LEVEL["zebra"]:
    prect(z["x"] - 2.6, 15.0, z["x"] + 2.6, 21.5, "#f2f0e8", r=1)
    for (bx, by) in z["beacons"]:
        pdot(bx, by, 2.4, "#f2782c")

# paths + squares
for p in LEVEL["paths"]:
    if p["kind"] == "worn":
        pline(p["pts"], C_WORN, sw=5.5)
    else:
        prect(p["x0"], p["y0"], p["x1"], p["y1"],
              C_FLAG if p["kind"] == "flags" else C_BRICK, r=3)
sb = LEVEL["stall_bay"]
prect(*sb, "none", stroke="#b08a5a")
plab((sb[0] + sb[2]) / 2, sb[1] + 2, "STALL BAY (sim)", 9.5, "#b08a5a")

# plots
for p in LEVEL["plots"]:
    prect(p["x"], p["y"], p["x"] + 7.4, p["y"] + 6.2, C_BLD, r=2)
    prect(p["x"] + 7.38, p["y"] + 0.55, p["x"] + 10.43, p["y"] + 5.85, C_BLD, r=2, op=0.75)
    pdot(p["x"] + 5.3, p["y"] - 0.9, 2.6, ACC[p["accent"]])
    plab(p["x"] + 3.7, p["y"] + 2.2, p["id"], 9, "#f7ece5", "700")
    if p["kit"] != "home":
        plab(p["x"] + 3.7, p["y"] + 8.0, p["kit"].upper(), 10, "#7b4a36")

# landmarks
lm = LEVEL["landmarks"]
pdot(lm["oak"]["x"], lm["oak"]["y"], 13.5 * PS * 0.32, "#8aa668")
pdot(lm["oak"]["x"], lm["oak"]["y"], 4.4, "#5c4632")
plab(lm["oak"]["x"], lm["oak"]["y"] + 8.5, "THE OAK", 11, TXT)
pdot(lm["board"]["x"], lm["board"]["y"], 3.2, C_LM)
plab(lm["board"]["x"] - 1, lm["board"]["y"] - 5.5, "BOARD", 9.5, TXT2)
st = lm["stand"]
prect(st["x0"], st["y"], st["x0"] + st["w"], st["y"] + 4.0, "#b9917c", r=2)
plab(st["x0"] + st["w"] / 2, st["y"] + 6.5, "THE GROUND (edge only)", 10.5, "#8d8674")
for (fx, fy) in lm["floodlights"]:
    pdot(fx, fy, 3.0, "none", stroke="#8d8674")
    pline([(fx - 2, fy), (fx + 2, fy)], "#8d8674", 1.4)
for (tx, ty) in lm["turnstiles"]:
    prect(tx, ty, tx + 3.0, ty + 2.6, "#b9917c", r=1)

# furniture + veg
for f in LEVEL["furniture"]:
    col = C_ADJ if "note" in f and "ADJ" in f.get("note", "") else C_LM
    pdot(f["x"], f["y"], 2.2, col)
for v in LEVEL["veg"]:
    pdot(v["x"], v["y"], 4.6 if "tree" in v["m"] else 2.8, "#9ab873")

# routes (the canonical walk + matchday funnel), light overlay
pline([(-16, 18.2), (28, 18.2), (32, 18.2), (40, 22), (50, 28), (53.5, 29),
       (64, 24), (84, 25), (108, 22), (118, 24), (128, 26), (140.3, 30.5),
       (152, 46)], "#e07a30", 2.6, dash="9,7")
plab(-8, 21.5, "the walk", 10, "#e07a30", anchor="start")

# scale + grid ticks
for gx in range(0, 200, 20):
    if EX0 <= gx <= EX1:
        pline([(gx, EY0), (gx, EY0 + 1.6)], "#b9b4a6", 1.2)
        plab(gx, EY0 + 4.0, str(gx), 8.5, TXT3)
t(PX(EX0), PY(EY1) - 8, "grid 20 m &#183; plots P01&#8211;P15 &#183; accent dots = resident colour &#183; "
                        "red = camera-validation adjustments ADJ-1..4", 11, TXT3)

# ---------------------------------------------------------------- right column
RX = PLX + PLW + 36
t(RX, PLY + 6, "MODULES (digest &#8212; 9 families, 31 modules)", 13, TXT, "700", ls=1.6)
MOD = [
    ("TER 2", "terrain plate &#183; stream bed"),
    ("RD 4", "carriageway &#183; junction &#183; kerb &#183; zebra kit"),
    ("PTH 4", "flag pave &#183; brick pave &#183; worn decal &#183; patch"),
    ("BLD 3", "hero core (7.4&#215;6.2+annex) &#183; shop kit &#183; pub kit"),
    ("LM 5", "Oak (unique) &#183; board &#183; bridge &#183; stand edge &#183; mast"),
    ("ST 11", "shelter &#183; lamp &#183; belisha &#183; bench &#183; bollard &#183; bin &#183; pillar &#183; planter &#183; wall/gate &#183; hedge &#183; rail"),
    ("VEG 3", "street tree &#183; shrub &#183; canopy variants"),
    ("PRP 9", "trace props, sim-owned: bin-out &#183; paper &#183; milk &#183; washing &#183; bike &#183; ball &#183; chalk &#183; scarf &#183; boxes"),
    ("KIT dep", "all kits depend on BLD-A sockets; traces on anchors (86 in level)"),
]
yy = PLY + 28
for (a, b) in MOD:
    t(RX, yy, a, 12, TXT, "700")
    words = b.split()
    line, lines = "", []
    for wd in words:
        if len(line) + len(wd) > 52:
            lines.append(line); line = wd
        else:
            line = (line + " " + wd).strip()
    lines.append(line)
    for j, ln in enumerate(lines):
        t(RX + 64, yy, ln, 11.5, TXT2)
        yy += 16
    yy += 6

yy += 10
t(RX, yy, "BUILD ORDER (each step playable)", 13, TXT, "700", ls=1.6)
yy += 22
for i, s in enumerate(["terrain + stream", "roads + kerbs + zebra",
                       "paths + squares  &#8594; NAV LOOP WALKABLE",
                       "15 plots, hero cores  &#8594; MASSING PLAYABLE",
                       "shop / pub kits (identity)",
                       "landmarks: Oak &#183; board &#183; bridge &#183; stand edge",
                       "street furniture", "vegetation",
                       "care layer (Sheet 03, per resident)",
                       "trace anchors + evidence props (CD-025)",
                       "lighting states: morning / dusk / matchday",
                       "ambient: bakery, stream, distant ground"]):
    t(RX, yy, "%02d" % (i + 1), 11.5, TXT3, "700")
    t(RX + 30, yy, s, 11.5, TXT2)
    yy += 17

yy += 14
t(RX, yy, "RISKS (production only)", 13, TXT, "700", ls=1.6)
yy += 22
for s in ["one house core everywhere &#8212; Alpha 1 ships 3 roof/accent",
          "variants; Sheet-01 twelve ported before Alpha 2",
          "Oak is the hero asset: highest budget, wind, scarf states",
          "bicycle prop must be remodelled (fails at lens range)",
          "bridge is a matchday choke by design &#8212; cap crowd density",
          "NE quadrant thin &#8212; allotments assigned, no new places",
          "shared-surface square needs nav priority zones (sim)"]:
    t(RX, yy, s, 11.5, TXT2)
    yy += 16

yy += 14
t(RX, yy, "DEFINITION OF DONE &#8212; PLAYABLE ALPHA 1", 13, TXT, "700", ls=1.6)
yy += 22
for s in ["walk the canonical route, collision on, 3:20 at 1.4 m/s",
          "all nine places readable at eye level, no labels",
          "every place on &#8805;2 routes (Stadium Road: 1, by design)",
          "15 plots &#183; 3 visual variants &#183; 5 kits &#183; 86 trace anchors",
          "Empty Tuesday Test: Tue am / Tue pm / Sat screenshots",
          "distinguishable by a stranger (CD-025 pilot passes)",
          "10-minute watch yields &#8805;3 sim-authored moments",
          "lighting: morning / dusk / matchday states switch",
          "no white background reachable by any in-game camera"]:
    t(RX, yy, s, 11.5, TXT2)
    yy += 16

# ---------------------------------------------------------------- validation strip
VY = max(PLY + PLH + 46, 1175)
rule(MX, VY - 18, W - MX)
t(MX, VY + 2, "CAMERA VALIDATION &#8212; four stations on the walked routes (perspective, eye height); "
              "findings applied to the data as ADJ-1..4", 13, TXT, "700", ls=1.2)

from charm import hero
from walk import house
from lovable import base, blob, vdot, bench as _bench, halo, porchlight, fascia_sign, hangingsign
from streets import flags, brickpav, tarmac, grass, tree, hedgerow, bollard, belisha, zebra, busstop, shelter
from places import oak, wornpath, parishboard, floodlights, barrel, stream as _stream

C = lambda sc: {"sc": sc, "K": lambda c: c}
EVE = (246, 210, 130)


def v1():
    sc = Scene()
    grass(sc, -4, 60, x0=-45, x1=45)
    flags(sc, -2, 4, x0=-30, x1=20)
    zebra(sc, -3.5, 4.2, 9.2, w=5.2)
    belisha(sc, 1.2, 3.4)
    house(sc, MUS, -8.0, yoff=22.0, glass=GLSI,
          deco=lambda c2: fascia_sign(c2, "BAKERY", MUS, letters=INK))
    parishboard(sc, 3.5, 16.0)
    oak(sc, 9.0, 30.0, s=1.4)
    return sc, (0, 0, 1.55), (-1.0, 20.0, 1.4), 1300, 0.55


def v2():
    sc = Scene()
    grass(sc, -4, 60, x0=-45, x1=45)
    oak(sc, 2.0, 8.0, s=1.5)
    wornpath(sc, 0.5, 6.0, -1.0, 20.0, w=1.1)
    house(sc, ORG, -10.0, yoff=22.0, glass=GLSI,
          deco=lambda c2: fascia_sign(c2, "CAF&#201;", ORG))
    house(sc, NVY, 2.0, yoff=25.0)
    ctx = C(sc)
    _bench(ctx, -3.5, 9.0)
    return sc, (0, 0, 1.55), (-2.0, 20.0, 1.4), 1300, 0.55


def v3():
    sc = Scene()
    brickpav(sc, -4, 55, x0=-40, x1=45, col=mix((186, 118, 88), (223, 219, 209), 0.42),
             j=mix((158, 98, 74), (204, 199, 187), 0.4))
    shelter(sc, -7.5, 9.0)
    busstop(sc, -2.5, 9.4)
    def pub(c2):
        fascia_sign(c2, "THE HOME END", GRN, ww=c2["gww"] + 0.55, letters=MUS)
        hangingsign(c2, GRN, MUS)
    house(sc, GRN, 4.0, yoff=20.0, glass=EVE, deco=pub)
    barrel(sc, 2.6, 17.6)
    return sc, (0, 0, 1.55), (1.0, 20.0, 1.5), 1300, 0.55


def v4():
    sc = Scene()
    grass(sc, 8.5, 60, x0=-45, x1=45)
    _stream(sc, 2.6, 8.5, x0=-45, x1=45)
    mass(sc, -7.0, 2.0, 0, 14.0, 0.45, 1.12, BRK, sw=1.6, top=True, tmat=CONC,
         arris=False)
    floodlights(sc, (5.0, 11.0), y=34.0, h=13.0)
    hedgerow(sc, -14.0, 10.0, 10.0, h=0.85)
    wornpath(sc, 1.0, 9.5, 4.0, 26.0, w=1.6)
    return sc, (0, 0, 1.6), (2.0, 18.0, 0.8), 1300, 0.54


VAL = [
    ("R1 &#183; the walk, at the crossing", "PASS &#8212; beacon, board and Oak read in one glance; rhythm intact", v1),
    ("R2 &#183; school route, under the Oak", "PASS &#8212; bench and caf&#233; visible; ADJ-4 gives the north path a destination", v2),
    ("R3 &#183; matchday route, market square", "ADJ-2/3 &#8212; shelter shifted, bollards aligned; pub sign now clear from the flag", v3),
    ("R4 &#183; matchday route, the bridge", "ADJ-1 &#8212; bridge moved 2 m south; parapet and masts read from the pub corner", v4),
]

VFW = (W - 2 * MX - 3 * 20) / 4.0
VFH = 330
for i, (nm, verdict, fn) in enumerate(VAL):
    cx = MX + i * (VFW + 20)
    cy = VY + 18
    sc, cam, tgt, SCALE, vfrac = fn()
    dx, dy, dz = tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    az = math.degrees(math.atan2(-dx / L, dy / L))
    el = math.degrees(math.asin(-dz / L))
    svgkit.set_persp(cam[0], cam[1], cam[2], az, el)
    sc2, *_ = fn()
    SCALE2 = SCALE * VFW / 1010.0
    ox = cx + 0.5 * VFW
    oy = cy + vfrac * VFH
    parts.append('<clipPath id="vc%d"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5"/></clipPath>'
                 % (i, cx, cy, VFW, VFH))
    parts.append('<g clip-path="url(#vc%d)">' % i)
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e9eff3"/>' % (cx, cy, VFW, VFH))
    hz = oy - SCALE2 * math.tan(math.radians(el))
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dfe2e0"/>'
                 % (cx, hz - 14, VFW, cy + VFH - hz + 14))
    parts.append(sc2.emit(ox, oy, SCALE2))
    parts.append('</g>')
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="none" '
                 'stroke="#dcd7cb" stroke-width="1.2"/>' % (cx, cy, VFW, VFH))
    t(cx, cy + VFH + 20, nm, 12, TXT, "700")
    words = verdict.split()
    line, lines = "", []
    for wd in words:
        if len(line) + len(wd) > 58:
            lines.append(line); line = wd
        else:
            line = (line + " " + wd).strip()
    lines.append(line)
    for j, ln in enumerate(lines):
        t(cx, cy + VFH + 38 + j * 15, ln, 11, TXT2)

svgkit.set_view(34.0, 19.0)

H = int(VY + 18 + VFH + 96)
parts.insert(0, '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                'viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="%s"/>'
             % (W, H, W, H, W, H, PAPER))
parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
