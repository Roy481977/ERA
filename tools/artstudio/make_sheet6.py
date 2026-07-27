import sys
import svgkit
from era_lang import *
from svgkit import hexc
from walk import BEATS, build_beat

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-walk-v1.svg"
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
VER = sys.argv[3] if len(sys.argv) > 3 else "VERSION 01"

svgkit.set_view(34.0, 6.5)               # a resident's eyes, not a drone's

COLS, ROWS = 3, 3
CW, CH = 660, 430
MX, TOP, BOT = 58, 186, 196
W = MX * 2 + CW * COLS
H = TOP + CH * ROWS + BOT

PAPER = "#ffffff"
RULE = "#dcd8ce"
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
t(MX + 126, 80, "THE WALK THROUGH TOWN", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "SHEET 06 &#183; ONE JOURNEY, NINE BEATS &#183; %s" % VER, 15, TXT2, "700", ls=2.2)
t(MX, 150, "Home to the stadium at walking pace. The resident always walks left to right; every panel&#8217;s "
           "exit is the next panel&#8217;s entrance. Places are the protagonists &#8212; buildings frame, they never anchor.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION CONCEPT &#183; NOT FOR BUILD", 13, TXT2, "700", anchor="end", ls=2.2)
t(W - MX, 150, "ground-level camera (34/6.5) &#183; locked language throughout &#183; no people, life implied",
  13, TXT2, "400", anchor="end")

# ---------------------------------------------------------------- panels
for i in range(9):
    num, tm, name, beat, note, fn = BEATS[i]
    c, r = i % COLS, i // COLS
    cx = MX + c * CW
    cy = TOP + r * CH
    sc = build_beat(i)
    bx0, by0, bx1, by1 = sc.bounds()
    ox = cx + CW / 2 - (bx0 + bx1) / 2 * SCALE
    baseline = cy + CH - 108 - by1 * SCALE
    parts.append('<g>' + sc.emit(ox, baseline, SCALE) + '</g>')

    lx = cx + 26
    ly = cy + CH - 64
    rule(lx, ly - 26, cx + CW - 26)
    t(lx, ly, num, 19, TXT, "700", ls=1.0)
    t(lx + 30, ly, tm, 14, TXT3, "700", ls=1.2)
    t(lx + 84, ly, name, 17, TXT, "400", ls=0.8)
    t(cx + CW - 26, ly, beat.upper(), 13, TXT2, "700", anchor="end", ls=2.4)
    t(lx, ly + 21, note, 13.5, TXT2, "400")
    if i < 8:
        t(cx + CW - 26, ly + 21, "&#8594;", 17, TXT3, "700", anchor="end")

# ---------------------------------------------------------------- footer
fy = TOP + CH * ROWS + 40
rule(MX, fy - 24, W - MX)
t(MX, fy + 2, "THE RHYTHM", 13, TXT, "700", ls=2.2)
t(MX, fy + 24, "quiet &#8594; rhythm &#8594; warmth &#8594; breath &#8594; pause &#8594; colour &#8594; gathering &#8594; "
               "anticipation &#8594; arrival &#8212; compression before every release, and never two open beats in a row.",
  13.5, TXT2, "400")
t(W - MX, fy + 2, "SHEET 05 GAVE IT MEMORY &#183; SHEET 06 GIVES IT PACE", 13, TXT, "700",
  ls=2.2, anchor="end")
t(W - MX, fy + 24, "the player learns the town by walking it &#8212; nobody reads a map of home",
  12.5, TXT3, "400", anchor="end")
t(MX, fy + 60, "WHY IT HOLDS &#8212; enclosure and openness alternate on a 30&#8211;40 second cycle: street &#8594; bakery square "
               "(open) &#8594; oak (widest) &#8594; bridge (narrow) &#8594; high street (loudest) &#8594; market (social) &#8594; lane "
               "(quiet) &#8594; ground (release). The senses arrive before their sources &#8212; smell before the bakery, sound before the ground.",
  13.5, TXT, "400")
t(MX, fy + 82, "WEAK TRANSITIONS, NAMED &#8212; 5&#8594;6 (bridge to high street) turns without a hinge: insert the CORNER WALL "
               "(PL-03) as the pivot. 3&#8594;4 (bakery to oak) is abrupt: let the NOTICE BOARD (PL-09) herald the green at the "
               "square&#8217;s exit. Both are one-prop fixes, already in the vocabulary.",
  13.5, TXT2, "400")
t(MX, fy + 104, "CANONICAL WALK, RECOMMENDED &#8212; DOOR &#183; QUIET STREET &#183; BAKERY SQUARE &#183; OAK &#183; BRIDGE &#183; "
                "HIGH STREET &#183; MARKET &#183; LANE &#183; GROUND, with the two hinges above. Every ERA town keeps these nine beats "
                "and this order; the places themselves may differ town to town &#8212; the rhythm is the canon.",
  13.5, TXT2, "400")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
