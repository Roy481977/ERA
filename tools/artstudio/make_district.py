import sys
import svgkit
from svgkit import hexc, proj
from era_lang import *
from district01 import build, LABELS

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-district01-built.svg"
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

svgkit.set_view(34.0, 19.0)              # the production camera

W = 2124
MX = 58
TOP = 196

PAPER = "#ffffff"
RULE = "#dcd8ce"
TXT = "#22242a"
TXT2 = "#7b7e87"
TXT3 = "#a3a6ae"

sc = build()
bx0, by0, bx1, by1 = sc.bounds()
RW = (bx1 - bx0) * SCALE
RH = (by1 - by0) * SCALE
OX = MX + (W - 2 * MX - RW) / 2 - bx0 * SCALE
OY = TOP + 40 - by0 * SCALE

TSY = TOP + 40 + RH + 96                 # time strip y
H = int(TSY + 214 + 150)

parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (W, H, W, H))
parts.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER))


def t(x, y, s, size, col=TXT, w="400", anchor="start", ls=0.0):
    parts.append('<text x="%.1f" y="%.1f" font-family="Helvetica,Arial,sans-serif" '
                 'font-size="%.1f" font-weight="%s" letter-spacing="%.2f" fill="%s" '
                 'text-anchor="%s">%s</text>' % (x, y, size, w, ls, col, anchor, s))


def rule(x1, y, x2, col=RULE, sw=1.5):
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.2f"/>' % (x1, y, x2, y, col, sw))


# ---------------------------------------------------------------- header
t(MX, 80, "ERA", 48, TXT, "700", ls=6)
t(MX + 126, 80, "DISTRICT 01, BUILT", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "THE WEAVE, PROVEN SPATIALLY &#183; ONE CONTINUOUS PLACE &#183; SATURDAY 13:40",
  15, TXT2, "700", ls=2.2)
t(MX, 150, "Not an exploration sheet. One worldspace: the daily line (crossing &#183; bakery square &#183; green &#183; "
           "high street &#183; market) and the weekly line (homes &#183; Oak &#183; bridge &#183; ground), crossing at the Oak.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION BOARD &#183; CD-027 RATIFIED", 13, TXT2, "700", anchor="end", ls=2.2)
t(W - MX, 150, "every discovery from Sheets 01&#8211;06 present and load-bearing &#183; no people, life implied",
  13, TXT2, "400", anchor="end")

# ---------------------------------------------------------------- render
parts.append('<g>' + sc.emit(OX, OY, SCALE) + '</g>')

# labels from world anchors
for (wx, wy, wz, lab, dx, dy) in LABELS:
    px, py = proj((wx, wy, wz))
    sx, sy = OX + px * SCALE + dx, OY + py * SCALE + dy
    ax, ay = OX + px * SCALE, OY + py * SCALE
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#b3aea0" '
                 'stroke-width="1.1"/>' % (ax, ay, sx, sy - 4))
    parts.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="#8d8674"/>' % (ax, ay))
    t(sx, sy, lab, 12.5, "#5f5a4e", "700", anchor="middle", ls=1.6)

# ground line
rule(MX, TOP + 40 + RH + 40, W - MX)

# ---------------------------------------------------------------- time strip
t(MX, TSY, "COMPOSED IN TIME &#8212; the same places, different owners", 14, TXT, "700", ls=2.2)
t(W - MX, TSY, "movement answers WHERE people meet &#183; time answers WHEN &#183; together: the rhythm", 12.5,
  TXT3, "400", anchor="end")
CELLS = [
    ("06:30", "THE BAKERY STEP", "Hana&#8217;s queue; the step is warm before the town wakes"),
    ("09:00", "THE GREEN", "prams and benches; the Oak belongs to the slow hours"),
    ("12:30", "MARKET SQUARE", "Friday&#8217;s flowers, Saturday&#8217;s folding stalls"),
    ("15:30", "THE CROSSING", "the school tide; the whole town yields twice a day"),
    ("18:30", "THE PUB DOOR", "barrels out, lantern on; the day is discussed"),
    ("SAT 14:45", "STADIUM ROAD", "the procession; the quietest street&#8217;s loudest hour"),
]
cw = (W - 2 * MX - 5 * 18) / 6.0
for i, (tm, pl, who) in enumerate(CELLS):
    cx = MX + i * (cw + 18)
    cy = TSY + 22
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="118" rx="9" '
                 'fill="#fbfaf7" stroke="%s" stroke-width="1.3"/>' % (cx, cy, cw, RULE))
    t(cx + 16, cy + 34, tm, 19, (lambda c: "#e07a30" if "SAT" not in tm else "#2f7a52")(tm),
      "700", ls=1.0)
    t(cx + 16, cy + 58, pl, 13.5, TXT, "700", ls=1.0)
    words = who.split()
    line, lines = "", []
    for wd in words:
        if len(line) + len(wd) > 34:
            lines.append(line); line = wd
        else:
            line = (line + " " + wd).strip()
    lines.append(line)
    yy = cy + 78
    for ln in lines:
        t(cx + 16, yy, ln, 11.5, TXT2, "400")
        yy += 15

# ---------------------------------------------------------------- footer
fy = TSY + 22 + 118 + 44
rule(MX, fy - 20, W - MX)
t(MX, fy + 4, "THE TEN-MINUTE TEST", 13, TXT, "700", ls=2.2)
t(MX, fy + 26, "Walk it west to east: your gate &#8594; the crossing &#8594; the warm step &#8594; the board&#8217;s news &#8594; "
               "under the Oak &#8594; the awnings &#8594; the square &#8594; the pub corner &#8594; over the bridge with everyone else. "
               "Compression and release the whole way; the ground earned, never given.",
  13.5, TXT2, "400")
t(W - MX, fy + 4, "THE LANGUAGE WORKS WHEN IT BECOMES A PLACE", 13, TXT, "700", ls=2.2, anchor="end")
t(W - MX, fy + 26, "next: residents &#8212; the town is ready to be lived in", 12.5, TXT3, "400", anchor="end")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H, "render", int(RW), "x", int(RH))
