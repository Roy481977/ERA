import sys
from era_lang import *
from svgkit import hexc
from lovable import TREATMENTS, build_treatment

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-love-v1.svg"
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 19.5
VER = sys.argv[3] if len(sys.argv) > 3 else "VERSION 01"

COLS, ROWS = 4, 3
CW, CH = 502, 400
MX, TOP, BOT = 58, 186, 196
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
t(MX + 126, 80, "BECOMING LOVABLE", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "SHEET 03 &#183; TWELVE CHARACTER TREATMENTS &#183; %s" % VER,
  15, TXT2, "700", ls=2.2)
t(MX, 150, "The building is locked. Every tile is the same architecture receiving a different act of care "
           "&#8212; paint, plants, light, signage, furniture. Charm from care, not clutter.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION CONCEPT &#183; NOT FOR BUILD", 13, TXT2, "700",
  anchor="end", ls=2.2)
t(W - MX, 150, "massing, roofs, windows, proportions: unchanged in every tile",
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
GY = 0.21955

for i in range(12):
    code, name, note, spec, accent, glass, fn = TREATMENTS[i]
    c, r = i % COLS, i // COLS
    cx = MX + c * CW
    cy = TOP + r * CH
    sc = build_treatment(i)
    bx0, by0, bx1, by1 = sc.bounds()
    ox = cx + CW / 2 - (bx0 + bx1) / 2 * SCALE
    baseline = cy + CH - 106 - by1 * SCALE

    mid, half = (bx0 + bx1) / 2, (bx1 - bx0) / 2
    half = min(half + 0.22, 5.6)
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
t(MX, fy + 2, "THE TEST", 13, TXT, "700", ls=2.2)
t(MX, fy + 24, "&#8220;I&#8217;d love to live there&#8221; &#8212; not &#8220;that&#8217;s a cute stylized building.&#8221; "
               "Warmth, optimism and craftsmanship; never caricature.",
  13.5, TXT2, "400")
t(W - MX, fy + 2, "SHEET 02 FOUND THE VOICE &#183; SHEET 03 MAKES IT LOVABLE", 13, TXT, "700",
  ls=2.2, anchor="end")
t(W - MX, fy + 24, "every treatment is reversible dressing on the locked language &#8212; "
                   "nothing here touches the architecture", 12.5, TXT3, "400", anchor="end")
t(MX, fy + 60, "LEAD&#8217;S VERDICT &#8212; strongest three: <tspan font-weight=\"700\">L-02 THE FRONT DOOR</tspan> "
               "(love legible at the threshold; a kit every resident can vary) &#183; "
               "<tspan font-weight=\"700\">L-03 WINDOW BOXES</tspan> (colour with a reason; reads at any distance) &#183; "
               "<tspan font-weight=\"700\">L-06 CRAFT</tspan> (care in the fabric itself &#8212; gutters, courses, pots).",
  13.5, TXT, "400")
t(MX, fy + 82, "RECOMMENDED &#8212; <tspan font-weight=\"700\" fill=\"#22242a\">L-12 LIVED-IN</tspan>, which is exactly those three combined: "
               "the entrance kit on every home, boxes on one or two windows, the craft layer everywhere. "
               "Garden, street and shop kits deploy by context, not by default.",
  13.5, TXT2, "400")
t(MX, fy + 104, "WHY IT WORKS &#8212; every element is evidence of a caring hand rather than applied cuteness, and every one "
                "is a per-resident variable the simulation can own &#8212; so the town dresses itself differently on every street.",
  13.5, TXT2, "400")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
