import sys
import svgkit
from era_lang import *
from svgkit import hexc
from walkframes import FRAMES

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-walking-the-town.svg"

W = 2124
MX = 58
COLS, ROWS = 4, 5
CW = (W - 2 * MX - 3 * 26) / 4.0
CH = 372
TOP = 150
H = int(TOP + ROWS * (CH + 22) + 190)

PAPER = "#ffffff"
RULE = "#e4e0d6"
TXT = "#22242a"
TXT2 = "#7b7e87"
TXT3 = "#a9a69c"

parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (W, H, W, H))
parts.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER))


def t(x, y, s, size, col=TXT, w="400", anchor="start", ls=0.0):
    parts.append('<text x="%.1f" y="%.1f" font-family="Helvetica,Arial,sans-serif" '
                 'font-size="%.1f" font-weight="%s" letter-spacing="%.2f" fill="%s" '
                 'text-anchor="%s">%s</text>' % (x, y, size, w, ls, col, anchor, s))


def rule(x1, y, x2, col=RULE, sw=1.2):
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.2f"/>' % (x1, y, x2, y, col, sw))


# ------------------------------------------------------- quiet header
t(MX, 78, "DISTRICT 01", 30, TXT, "700", ls=4)
t(MX + 240, 78, "walking the town", 30, TXT2, "300", ls=1.5)
t(W - MX, 78, "one Tuesday, 07:52 &#8211; 17:48", 14, TXT3, "400", anchor="end")
rule(MX, 98, W - MX)

# ------------------------------------------------------- frames
for i, (tm, note, az, el, scale, fn) in enumerate(FRAMES):
    c, r = i % COLS, i // COLS
    cx = MX + c * (CW + 26)
    cy = TOP + r * (CH + 22)
    svgkit.set_view(az, el)
    sc = fn()
    bx0, by0, bx1, by1 = sc.bounds()
    rw = (bx1 - bx0) * scale
    s = scale
    if rw > CW - 8:
        s = scale * (CW - 8) / rw
    ox = cx + CW / 2 - (bx0 + bx1) / 2 * s
    baseline = cy + CH - 46 - by1 * s
    parts.append('<g>' + sc.emit(ox, baseline, s) + '</g>')
    rule(cx, cy + CH - 26, cx + CW)
    t(cx, cy + CH - 8, tm, 13, TXT3, "700", ls=1.4)
    if note:
        t(cx + CW, cy + CH - 8, note, 12.5, TXT3, "400", anchor="end")

# ------------------------------------------------------- afterword
fy = TOP + ROWS * (CH + 22) + 26
rule(MX, fy - 12, W - MX)
t(MX, fy + 12, "WHERE IT BECOMES MEMORABLE", 12.5, TXT, "700", ls=2.0)
t(MX, fy + 34, "08:07, the warm step &#8212; the first time the town gives you something without being asked. "
               "08:20, the bench &#8212; the first time you stop for no reason, which is the moment a place becomes yours. "
               "17:48, the gate &#8212; the bin is in, the paper is gone, the light is on: the town kept living while you wandered.",
  13, TXT2, "400")
t(MX, fy + 64, "STILL ARTIFICIAL", 12.5, TXT, "700", ls=2.0)
t(MX, fy + 86, "the market shelter (arrives too complete, nothing worn); the pub barrels (set-dressed, not left); "
               "the lane&#8217;s rails (too regular &#8212; hands would have bent one). Each needs the sim&#8217;s handwriting, not mine.",
  13, TXT2, "400")
t(W - MX, fy + 64, "WHERE IT DISAPPEARS INTO EVERYDAY LIFE", 12.5, TXT, "700", ls=2.0, anchor="end")
t(W - MX, fy + 86, "the crossing &#183; the washing &#183; the worn grass &#183; the chalk &#183; the board&#8217;s papers &#183; the empty Tuesday square",
  13, TXT2, "400", anchor="end")
t(W - MX, fy + 112, "would someone walk it when they don&#8217;t have to?", 13, TXT3, "400", anchor="end")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
