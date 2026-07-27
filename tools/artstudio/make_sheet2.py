import sys
from era_lang import *
from svgkit import hexc
from stylize import PASSES

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-style-v1.svg"
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 19.5
VER = sys.argv[3] if len(sys.argv) > 3 else "VERSION 01"

COLS, ROWS = 4, 3
CW, CH = 502, 392
MX, TOP, BOT = 58, 186, 150
W = MX * 2 + CW * COLS
H = TOP + CH * ROWS + BOT

PAPER = "#ffffff"
RULE = "#dcd8ce"
DATUM = "#ddd8cc"
TXT = "#22242a"
TXT2 = "#7b7e87"
TXT3 = "#a3a6ae"

parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (W, H, W, H))
parts.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER))


def t(x, y, s, size, col=TXT, w="400", anchor="start", ls=0.0,
      fam="Helvetica,Arial,sans-serif"):
    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%.1f" '
                 'font-weight="%s" letter-spacing="%.2f" fill="%s" text-anchor="%s">%s</text>'
                 % (x, y, fam, size, w, ls, col, anchor, s))


def rule(x1, y, x2, col=RULE, sw=1.5):
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.2f"/>' % (x1, y, x2, y, col, sw))


# ---------------------------------------------------------------- header
t(MX, 80, "ERA", 48, TXT, "700", ls=6)
t(MX + 126, 80, "FINDING THE VOICE", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "SHEET 02 &#183; TWELVE STYLIZATION PASSES &#183; %s" % VER,
  15, TXT2, "700", ls=2.2)
t(MX, 150, "One architecture, twelve treatments. Sheet 01 found the era; this sheet hunts the voice. "
           "The building never changes &#8212; only the charm does.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION CONCEPT &#183; NOT FOR BUILD", 13, TXT2, "700",
  anchor="end", ls=2.2)
t(W - MX, 150, "row 1 isolates the axes &#183; row 2 climbs the ladder &#183; row 3 changes the kind of play",
  13, TXT2, "400", anchor="end")

# scale bar
sb_x = W - MX - 10 * SCALE
sb_y = 74
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="8" fill="none" stroke="%s" '
             'stroke-width="1.2"/>' % (sb_x, sb_y, 10 * SCALE, TXT3))
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="8" fill="%s"/>'
             % (sb_x, sb_y, 5 * SCALE, "#e6e2d8"))
for k, lab in ((0, "0"), (5, "5"), (10, "10 m")):
    t(sb_x + k * SCALE, sb_y - 8, lab, 11.5, TXT3, "700",
      anchor="middle" if k < 10 else "end", ls=0.8)

# ---------------------------------------------------------------- tiles
from charm import hero
GY = 0.21955

for i, (code, name, note, spec, prm) in enumerate(PASSES):
    c, r = i % COLS, i // COLS
    cx = MX + c * CW
    cy = TOP + r * CH
    sc = hero(prm)
    bx0, by0, bx1, by1 = sc.bounds()
    ox = cx + CW / 2 - (bx0 + bx1) / 2 * SCALE
    baseline = cy + CH - 106 - by1 * SCALE

    mid, half = (bx0 + bx1) / 2, (bx1 - bx0) / 2
    half = min(half + 0.22, 4.3)
    a, b = mid - half, mid + half
    parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                 'stroke-width="1.6" stroke-linecap="round"/>'
                 % (ox + a * SCALE, baseline + a * GY * SCALE,
                    ox + b * SCALE, baseline + b * GY * SCALE, DATUM))

    parts.append('<g>' + sc.emit(ox, baseline, SCALE) + '</g>')

    lx = cx + 28
    ly = cy + CH - 62
    rule(lx, ly - 28, cx + CW - 28)
    t(lx, ly, code, 17, TXT, "700", ls=1.6)
    t(lx + 58, ly, name, 17, TXT, "400", ls=0.6)
    t(lx, ly + 21, note, 13.5, TXT2, "400")
    t(lx, ly + 40, spec, 12, TXT3, "400", ls=0.4)

# ---------------------------------------------------------------- footer
fy = TOP + CH * ROWS + 40
rule(MX, fy - 24, W - MX)
t(MX, fy + 2, "THE AXES", 13, TXT, "700", ls=2.2)
t(MX, fy + 24, "proportion &#183; roof generosity &#183; opening size &#183; entrance friendliness &#183; "
               "colour spend &#183; softness of edge &#183; orthogonal perfection",
  13.5, TXT2, "400")
t(MX, fy + 58, "LEAD&#8217;S READ &#8212; the voice lives between S-06 and S-07, carried by S-09&#8217;s hand: "
               "charm in the +20/+30 band, with the wobble&#8217;s built-by-hands imperfection on top. "
               "S-08 proves the ceiling; S-10 and S-12 are lovely but belong to different games.",
  13.5, "#22242a", "400")
t(W - MX, fy + 2, "SHEET 01 FOUND THE ERA &#183; SHEET 02 HUNTS THE VOICE", 13, TXT, "700",
  ls=2.2, anchor="end")
t(W - MX, fy + 24, "the winning voice is then verified across all twelve buildings of Sheet 01 "
                   "before anything locks", 12.5, TXT3, "400", anchor="end")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
