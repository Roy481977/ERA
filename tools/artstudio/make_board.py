import sys
import svgkit
from era_lang import *
from svgkit import hexc
from district_views import VIEWS, build_view

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-district-01.svg"
VER = sys.argv[3] if len(sys.argv) > 3 else "BOARD 01"

W, H = 2124, 2640
MX = 58

PAPER = "#ffffff"
RULE = "#dcd8ce"
TXT = "#22242a"
TXT2 = "#7b7e87"
TXT3 = "#a3a6ae"

# plan palette
P_GREEN = "#cfdcae"
P_GREEN2 = "#c2d29e"
P_PAVE = "#eae6dc"
P_BRICKP = "#e0cfc2"
P_ROAD = "#d9d6cf"
P_FOOT = "#c97a5e"
P_FOOT2 = "#b96e54"
P_WORN = "#d9c9a8"
P_OAK = "#8aa668"
ROUTE = "#e07a30"
SIGHT = "#3c6ea5"
GATH = "#e8a13c"

parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (W, H, W, H))
parts.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER))


def t(x, y, s, size, col=TXT, w="400", anchor="start", ls=0.0, opac=1.0):
    parts.append('<text x="%.1f" y="%.1f" font-family="Helvetica,Arial,sans-serif" '
                 'font-size="%.1f" font-weight="%s" letter-spacing="%.2f" fill="%s" '
                 'text-anchor="%s" opacity="%.2f">%s</text>'
                 % (x, y, size, w, ls, col, anchor, opac, s))


def rule(x1, y, x2, col=RULE, sw=1.5):
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.2f"/>' % (x1, y, x2, y, col, sw))


# ---------------------------------------------------------------- header
t(MX, 80, "ERA", 48, TXT, "700", ls=6)
t(MX + 126, 80, "DISTRICT 01 &#8212; THE HEART", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "ONE COMPLETE DISTRICT &#183; PLAN, ROUTES, SIGHTLINES, FOUR VIEWS &#183; %s" % VER,
  15, TXT2, "700", ls=2.2)
t(MX, 150, "Not a concept sheet. The proof: every discovery from Sheets 01&#8211;06 living together in one "
           "believable place. Spaces lead; buildings follow; the ground is always hinted, never dominant.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION BOARD &#183; NOT FOR BUILD", 13, TXT2, "700", anchor="end", ls=2.2)
t(W - MX, 150, "plan 1:1250-ish &#183; views at the resident&#8217;s eye height (34/6.5) from the marked cones",
  13, TXT2, "400", anchor="end")

# ================================================================ PLAN
PLX, PLY = MX, 210            # plan origin on board
PS = 5.55                     # px per metre
PLW_M, PLH_M = 240.0, 146.0


def PX(mx):
    return PLX + mx * PS


def PY(my):
    return PLY + (PLH_M - my) * PS


def prect(x, y, w, h, col, r=6, stroke=None, sw=1.2, op=1.0):
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" '
                 'fill="%s" %s opacity="%.2f"/>'
                 % (PX(x), PY(y + h), w * PS, h * PS, r, col,
                    ('stroke="%s" stroke-width="%.1f"' % (stroke, sw)) if stroke else '',
                    op))


def ppoly(pts, col, stroke=None, sw=1.2, op=1.0, r=0):
    d = "M " + " L ".join("%.1f,%.1f" % (PX(x), PY(y)) for x, y in pts) + " Z"
    parts.append('<path d="%s" fill="%s" %s opacity="%.2f" stroke-linejoin="round"/>'
                 % (d, col, ('stroke="%s" stroke-width="%.1f"' % (stroke, sw)) if stroke else '', op))


def pline(pts, col, sw=2.0, dash=None, op=1.0, arrow=False):
    d = "M " + " L ".join("%.1f,%.1f" % (PX(x), PY(y)) for x, y in pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linecap="round" stroke-linejoin="round" %s opacity="%.2f"/>'
                 % (d, col, sw, ('stroke-dasharray="%s"' % dash) if dash else '', op))
    if arrow:
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        import math as _m
        a = _m.atan2(PY(y2) - PY(y1), PX(x2) - PX(x1))
        for da in (2.6, -2.6):
            parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="%.1f" stroke-linecap="round"/>'
                         % (PX(x2), PY(y2), PX(x2) - 9 * _m.cos(a + da),
                            PY(y2) - 9 * _m.sin(a + da), col, sw))


def pdot(x, y, r, col, op=1.0, stroke=None):
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f" %s/>'
                 % (PX(x), PY(y), r, col, op,
                    ('stroke="%s" stroke-width="1.2"' % stroke) if stroke else ''))


def plab(x, y, s, size=13, col=TXT, w="700", anchor="middle", ls=1.2):
    t(PX(x), PY(y), s, size, col, w, anchor=anchor, ls=ls)


# plan card
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="#fbfaf7" '
             'stroke="%s" stroke-width="1.5"/>' % (PLX - 10, PLY - 10, PLW_M * PS + 20,
                                                   PLH_M * PS + 20, RULE))

# --- ground: greens
ppoly([(88, 50), (140, 48), (146, 74), (140, 106), (94, 108), (86, 78)], P_GREEN)
prect(4, 116, 76, 26, P_GREEN, op=0.55)                    # back gardens north
prect(4, 6, 100, 22, P_GREEN, op=0.55)                     # south fields
prect(180, 108, 60, 34, P_GREEN, op=0.7)                   # towards the ground
# stadium corner, mostly off-board
ppoly([(214, 118), (240, 114), (240, 142), (210, 142)], "#d8d3c6", stroke="#b9b2a2", sw=2)
plab(228, 126, "THE GROUND", 12, "#8d8674", "700")
plab(228, 122, "(beyond the board)", 10.5, "#a49d8b", "400")

# --- paved squares
prect(58, 66, 30, 30, P_PAVE, r=10)                        # bakery square
prect(172, 56, 34, 38, P_BRICKP, r=10)                     # market square
prect(134, 70, 40, 8, P_BRICKP, r=4, op=0.9)               # high street walk
# roads
prect(4, 60, 56, 6, P_ROAD, r=3)                           # west lane
ppoly([(58, 62), (88, 66), (88, 72), (58, 68)], P_ROAD)    # approach
prect(134, 62, 40, 7, P_ROAD, r=3)                         # high street carriageway
ppoly([(196, 94), (204, 94), (226, 116), (218, 120)], P_WORN)  # stadium road (worn)
# worn paths across the green
pline([(88, 76), (104, 78), (112, 79)], P_WORN, sw=7, op=0.9)
pline([(112, 79), (128, 78), (134, 75)], P_WORN, sw=7, op=0.9)
pline([(112, 79), (120, 92), (128, 100)], P_WORN, sw=5, op=0.7)

# --- footprints (buildings define the spaces)
def houses_row(x0, y, n, w=9, d=7, gap=3.5, col=P_FOOT):
    for i in range(n):
        prect(x0 + i * (w + gap), y, w, d, col, r=3)

houses_row(6, 68, 4)                                        # west lane north side
houses_row(10, 50, 4)                                       # west lane south side
prect(60, 96, 20, 10, P_FOOT2, r=3)                         # BAKERY
houses_row(34, 96, 2, w=10)
prect(90, 96, 12, 8, P_FOOT, r=3)
prect(58, 46, 12, 9, P_FOOT, r=3)                           # square south
prect(74, 46, 12, 9, P_FOOT, r=3)
prect(136, 80, 16, 9, P_FOOT2, r=3)                         # STORES
prect(156, 80, 16, 9, P_FOOT, r=3)                          # post office
prect(138, 52, 15, 9, P_FOOT2, r=3)                         # CAFÉ
prect(158, 52, 12, 9, P_FOOT, r=3)
prect(206, 72, 13, 20, P_FOOT2, r=3)                        # PUB
prect(176, 40, 14, 9, P_FOOT, r=3)                          # by the bus stop
houses_row(104, 108, 3, w=10)                               # green, north edge
houses_row(100, 40, 2, w=10)                                # green, south edge

# --- the Oak
pdot(112, 79, 15.5 * PS * 0.32, P_OAK, op=0.25)
pdot(112, 79, 11.8 * PS * 0.32, P_OAK, op=0.85)
pdot(112, 79, 8.0 * PS * 0.32, "#7a9758", op=0.9)
pdot(112, 79, 5.2, "#5c4632")

# --- gathering places (warm nodes)
for (gx, gy) in ((71, 95.2), (109, 75.5), (145, 61.5), (188, 74), (206.5, 80),
                 (186, 57.5), (89, 81)):
    pdot(gx, gy, 9, GATH, op=0.28)
    pdot(gx, gy, 3.4, GATH)

# --- the walk (Sheet 06 made spatial)
pline([(6, 63), (52, 63), (66, 70), (72, 80), (88, 79), (112, 79),
       (134, 74.5), (172, 74.5), (188, 76), (197, 93), (222, 115)],
      ROUTE, sw=3.4, dash="10,7", arrow=True)
for (wx, wy, lab) in ((10, 63, "0:00"), (44, 63, "0:30"), (70, 82, "1:00"),
                      (112, 81.5, "1:30"), (152, 76.5, "2:20"), (188, 78, "2:45"),
                      (204, 100, "3:05"), (219, 111, "3:20")):
    pdot(wx, wy, 3.0, ROUTE)
    plab(wx, wy + 3.4, lab, 10.5, ROUTE, "700")

# --- sightlines
pline([(89, 81), (105, 79.6)], SIGHT, sw=1.8, dash="3,5", arrow=True)     # S1 board->oak
pline([(140, 74.5), (222, 116)], SIGHT, sw=1.8, dash="3,5", arrow=True)   # S2 street->floodlight
pline([(186, 58.5), (205, 78)], SIGHT, sw=1.8, dash="3,5", arrow=True)    # S3 bus->pub sign
pline([(112, 79), (90, 80.5)], SIGHT, sw=1.8, dash="3,5", arrow=True)     # S4 oak->square
for (sx, sy, lab) in ((96, 82.5, "S1"), (180, 96, "S2"), (194, 66, "S3"),
                      (101, 76.2, "S4")):
    plab(sx, sy, lab, 11, SIGHT, "700")

# --- compression / release markers
for (cx, cy) in ((66, 71), (134, 74.5), (197, 95)):
    plab(cx, cy - 3.4, "&#187;&#187;", 15, "#b05c2c", "700")
for (rx, ry) in ((72, 82.5), (112, 86), (188, 80)):
    pdot(rx, ry, 7.5, "none", stroke="#b05c2c")

# --- camera cones for the four views
import math as _m
def cone(x, y, ang_deg, lab):
    a = _m.radians(ang_deg)
    for da in (-0.35, 0.35):
        pline([(x, y), (x + 10 * _m.cos(a + da), y + 10 * _m.sin(a + da))],
              "#8a8f98", sw=1.6)
    pdot(x, y, 3.2, "#565b64")
    plab(x - 2.2, y - 4.6, lab, 11.5, "#565b64", "700")

cone(64, 76, -10, "V1")
cone(136, 72, 4, "V2")
cone(176, 70, -18, "V3")
cone(200, 97, 42, "V4")

# --- labels
plab(73, 88.5, "BAKERY SQUARE", 13)
plab(70, 105.5, "BAKERY", 11, "#7b4a36", "700")
plab(113, 95, "THE OLD OAK GREEN", 13)
plab(154, 75.8, "HIGH STREET", 12.5)
plab(145.5, 55.5, "CAF&#201;", 11, "#7b4a36", "700")
plab(144, 83.5, "STORES", 11, "#7b4a36", "700")
plab(163.5, 83.5, "POST", 11, "#7b4a36", "700")
plab(189, 51, "BUS STOP", 11.5)
plab(188, 67, "MARKET SQUARE", 13)
plab(212.5, 81.5, "PUB", 11, "#7b4a36", "700")
plab(215, 105.5, "STADIUM ROAD", 12.5)
plab(89, 84.5, "NOTICE BOARD", 10.5, TXT2)
plab(30, 59, "RESIDENTIAL LANES", 11.5, TXT2)
plab(42, 128, "ALLOTMENTS &#38; GARDENS", 10.5, "#94a476", "700")
plab(54, 16, "PLAYING FIELD", 10.5, "#94a476", "700")

# north arrow + scale
parts.append('<g transform="translate(%.1f,%.1f)">' % (PX(8), PY(138)))
parts.append('<line x1="0" y1="16" x2="0" y2="-14" stroke="#565b64" stroke-width="2"/>'
             '<path d="M 0,-14 L -6,-2 L 6,-2 Z" fill="#565b64"/></g>')
t(PX(8), PY(131), "N", 13, "#565b64", "700", anchor="middle")
sbx, sby = PX(150), PY(140)
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="7" fill="none" stroke="%s" '
             'stroke-width="1.2"/>' % (sbx, sby, 40 * PS, TXT3))
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="7" fill="#e6e2d8"/>'
             % (sbx, sby, 20 * PS))
t(sbx, sby - 6, "0", 11, TXT3, "700")
t(sbx + 20 * PS, sby - 6, "20", 11, TXT3, "700", anchor="middle")
t(sbx + 40 * PS, sby - 6, "40 m", 11, TXT3, "700", anchor="end")

# legend
ly0 = PY(10)
lx0 = PX(108)
t(lx0, ly0, "&#8212;&#8212; the walk (times from Sheet 06)", 12, ROUTE, "700")
t(lx0 + 250, ly0, "&#8211;&#8211;&#8594; sightline", 12, SIGHT, "700")
t(lx0 + 380, ly0, "&#9679; gathering place", 12, GATH, "700")
t(lx0 + 540, ly0, "&#187;&#187; compression &#183; &#9675; release", 12, "#b05c2c", "700")

# ================================================================ NOTES
NX_ = PX(240) + 40
NY0 = 240
t(NX_, NY0 - 26, "WHY EACH SPACE EXISTS", 14, TXT, "700", ls=2.2)
rule(NX_, NY0 - 12, W - MX)
notes = [
    ("BAKERY SQUARE", "Mornings need a destination. The square is exactly the "
     "size of a queue that wants to talk; the road steps aside for it."),
    ("THE NOTICE BOARD", "Stands at the square&#8217;s exit, not its centre &#8212; news "
     "travels on the way to somewhere. It heralds the green (hinge from Sheet 06)."),
    ("THE OLD OAK GREEN", "The green was here first; every street bends around "
     "it, which is why every sightline finds it. The district&#8217;s breath and its "
     "emotional centre (Sheet 05)."),
    ("HIGH STREET", "Compression by consent: shops need each other, so awnings "
     "nearly touch and both accents arrive at once. One floodlight sits in the "
     "gap between buildings &#8212; the town&#8217;s quietest promise (S2)."),
    ("THE CAF&#201;", "South side, terrace facing the green: coffee watches the "
     "town go by. The chair is the point; the coffee is the excuse."),
    ("MARKET SQUARE", "The widest floor in town, deliberately empty six days a "
     "week so that Friday feels like an event and every other day belongs to "
     "the kids."),
    ("THE PUB", "One building, two duties: its front door faces the market "
     "square (Friday), its gable faces Stadium Road (Saturday). THE HOME END "
     "serves both without moving."),
    ("THE BUS STOP", "On the square&#8217;s edge, not in a lay-by &#8212; arrival lands in "
     "the middle of life. The first thing a visitor sees is the market, the "
     "pub, and the Oak beyond."),
    ("STADIUM ROAD", "Deliberately the plainest street in the district: hedges, "
     "a rail, two scarves. The quietest street carries the loudest hour, and "
     "absence carries the anticipation."),
]
ny = NY0 + 10
for (nm, txtn) in notes:
    t(NX_, ny, nm, 13.5, TXT, "700", ls=1.0)
    # wrap at ~66 chars
    words = txtn.split()
    line, lines = "", []
    for wd in words:
        if len(line) + len(wd) > 64:
            lines.append(line)
            line = wd
        else:
            line = (line + " " + wd).strip()
    lines.append(line)
    yy = ny + 19
    for ln in lines:
        t(NX_, yy, ln, 12.5, TXT2, "400")
        yy += 17
    ny = yy + 14

# ================================================================ VIEWS
svgkit.set_view(34.0, 6.5)
VSCALE = 14.2
VY0 = 1120
VCW, VCH = (W - MX * 2 - 30) / 2.0, 470
for i in range(4):
    code, name, note, fn = VIEWS[i]
    c, r = i % 2, i // 2
    cx = MX + c * (VCW + 30)
    cy = VY0 + r * (VCH + 26)
    sc = build_view(i)
    bx0, by0, bx1, by1 = sc.bounds()
    ox = cx + VCW / 2 - (bx0 + bx1) / 2 * VSCALE
    baseline = cy + VCH - 92 - by1 * VSCALE
    parts.append('<g>' + sc.emit(ox, baseline, VSCALE) + '</g>')
    lx = cx + 8
    ly = cy + VCH - 48
    rule(lx, ly - 22, cx + VCW - 8)
    t(lx, ly, code, 16, TXT, "700", ls=1.4)
    t(lx + 46, ly, name, 16, TXT, "400", ls=0.8)
    t(lx, ly + 20, note, 12.5, TXT2, "400")

# ================================================================ footer
fy = VY0 + 2 * (VCH + 26) + 28
rule(MX, fy - 20, W - MX)
t(MX, fy + 4, "THE PROOF", 13, TXT, "700", ls=2.2)
t(MX, fy + 26, "Every discovery is load-bearing &#8212; Sheet 01 frames every space &#183; Sheet 02&#8217;s voice is every "
               "building &#183; Sheet 03&#8217;s care dresses bakery, caf&#233; and pub &#183; Sheet 04 paves the ground &#183; "
               "Sheet 05&#8217;s places are the rooms &#183; Sheet 06&#8217;s rhythm strings them.",
  13.5, TXT2, "400")
t(MX, fy + 48, "COMPRESSION &#8594; RELEASE, CONTINUOUS &#8212; lane &#187; bakery square &#9675; &#187; green (widest) &#9675; "
               "&#187; high street (tightest) &#187; market &#9675; &#187; stadium road &#8212; and the ground is never seen whole: "
               "one floodlight in a gap (S2), two over the hedge (V4), sound before sight on matchday.",
  13.5, TXT2, "400")
t(W - MX, fy + 4, "SHEETS 01&#8211;06 PROVED THE WORDS &#183; DISTRICT 01 PROVES THE SENTENCE", 13, TXT, "700",
  ls=2.2, anchor="end")
t(W - MX, fy + 26, "next: residents walk it &#8212; the watchability test, in place", 12.5, TXT3, "400",
  anchor="end")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
