import sys
from era_lang import *
from svgkit import hexc
from places import PLACES as STREETS
from places import build_place as build_street

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-place-v1.svg"
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 13.2
VER = sys.argv[3] if len(sys.argv) > 3 else "VERSION 01"

COLS, ROWS = 4, 3
CW, CH = 502, 424
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
t(MX + 126, 80, "PLACES YOU REMEMBER", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "SHEET 05 &#183; TWELVE PLACES &#183; %s" % VER,
  15, TXT2, "700", ls=2.2)
t(MX, 150, "Not landmarks &#8212; gathering points. After twenty years here you would say &#8220;meet me there&#8221; "
           "with no address. Twelve places, one question each: why do people naturally stop here?",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION CONCEPT &#183; NOT FOR BUILD", 13, TXT2, "700",
  anchor="end", ls=2.2)
t(W - MX, 150, "same camera &#183; locked architecture, voice, care and street language &#183; no people, life implied",
  13, TXT2, "400", anchor="end")

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
for i in range(12):
    code, name, q, spec, fn = STREETS[i]
    c, r = i % COLS, i // COLS
    cx = MX + c * CW
    cy = TOP + r * CH
    sc = build_street(i)
    bx0, by0, bx1, by1 = sc.bounds()
    ox = cx + CW / 2 - (bx0 + bx1) / 2 * SCALE
    baseline = cy + CH - 104 - by1 * SCALE
    parts.append('<g>' + sc.emit(ox, baseline, SCALE) + '</g>')

    lx = cx + 28
    ly = cy + CH - 60
    rule(lx, ly - 26, cx + CW - 28)
    t(lx, ly, code, 17, TXT, "700", ls=1.6)
    t(lx + 62, ly, name, 17, TXT, "400", ls=0.6)
    t(lx, ly + 21, "Q &#183; %s" % q, 13.5, TXT2, "400")
    t(lx, ly + 40, spec, 12, TXT3, "400", ls=0.4)

# ---------------------------------------------------------------- footer
fy = TOP + CH * ROWS + 40
rule(MX, fy - 24, W - MX)
t(MX, fy + 2, "THE PLACE RULES", 13, TXT, "700", ls=2.2)
t(MX, fy + 24, "human scale; no monuments, no spectacle; every place is caused by everyday life; "
               "the ground remembers &#8212; worn paths are the town&#8217;s handwriting; football stays on the horizon.",
  13.5, TXT2, "400")
t(W - MX, fy + 2, "SHEET 04 GAVE IT GROUND &#183; SHEET 05 GIVES IT MEMORY", 13, TXT, "700",
  ls=2.2, anchor="end")
t(W - MX, fy + 24, "&#8220;let&#8217;s meet there&#8221; &#8212; and nobody asks where", 12.5, TXT3, "400",
  anchor="end")
t(MX, fy + 60, "LEAD&#8217;S VERDICT &#8212; strongest three: <tspan font-weight=\"700\">PL-01 THE BAKERY STEP</tspan> "
               "(ritual &#8212; the day starts here, and the body remembers warmth and bread) &#183; "
               "<tspan font-weight=\"700\">PL-08 THE SMALL BRIDGE</tspan> (licensed idleness &#8212; the only place where stopping needs no excuse) &#183; "
               "<tspan font-weight=\"700\">PL-02 THE OLD OAK</tspan> (the only monument ERA allows: one that grew).",
  13.5, TXT, "400")
t(MX, fy + 82, "RECOMMENDED &#8212; <tspan font-weight=\"700\" fill=\"#22242a\">THE OLD OAK</tspan> as the emotional centre of every ERA town: "
               "it precedes the town; football touches it without owning it (scarves after wins); grief and celebration share it; "
               "and its meaning accumulates physically &#8212; the slowest clock of evidence-of-life.",
  13.5, TXT2, "400")
t(MX, fy + 104, "WHY PEOPLE RETURN &#8212; each place pays in a different currency: bread for the body, idleness with permission, "
                "memory for belonging. None was designed to be beautiful; all were caused by life &#8212; which is why they become beautiful.",
  13.5, TXT2, "400")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
