import sys, math
from svgkit import hexc
from era_lang import *
from concepts import CONCEPTS

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-lang-v2.svg"
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 21.0
VER = sys.argv[3] if len(sys.argv) > 3 else "VERSION 02"

COLS, ROWS = 4, 3
CW, CH = 502, 392
MX, TOP, BOT = 58, 186, 168
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
t(MX + 126, 80, "ARCHITECTURAL LANGUAGE", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "SHEET 01 &#183; TWELVE BUILDING CONCEPTS &#183; %s" % VER,
  15, TXT2, "700", ls=2.2)
t(MX, 150, "A modern English village, late 1970s / early 1980s. An exploration sheet — the vocabulary, "
           "not the buildings. Twelve deliberately divergent directions, one town.",
  15, TXT2, "400")
t(W - MX, 126, "PRODUCTION CONCEPT &#183; NOT FOR BUILD", 13, TXT2, "700",
  anchor="end", ls=2.2)
t(W - MX, 150, "three-quarter front view &#183; orthographic &#183; one light &#183; one eye height",
  13, TXT2, "400", anchor="end")

# scale bar — 10 m at sheet scale, alternating ticks
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
GY = 0.21955                                  # projected slope of a ground line

for i, (code, name, note, spec, fn) in enumerate(CONCEPTS):
    c, r = i % COLS, i // COLS
    cx = MX + c * CW
    cy = TOP + r * CH
    sc = fn()
    bx0, by0, bx1, by1 = sc.bounds()
    ox = cx + CW / 2 - (bx0 + bx1) / 2 * SCALE
    baseline = cy + CH - 106 - by1 * SCALE

    # projected ground datum, drawn under the form
    mid, half = (bx0 + bx1) / 2, (bx1 - bx0) / 2
    half = min(half + 0.22, 4.3)
    a, b = mid - half, mid + half
    parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                 'stroke-width="1.6" stroke-linecap="round"/>'
                 % (ox + a * SCALE, baseline + a * GY * SCALE,
                    ox + b * SCALE, baseline + b * GY * SCALE, DATUM))

    parts.append('<g>' + sc.emit(ox, baseline, SCALE) + '</g>')

    # label block
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
t(MX, fy + 2, "MATERIAL SET", 13, TXT, "700", ls=2.2)

SWATCH = [("brick", BRK), ("dark brick", BRK2), ("buff brick", BRK3),
          ("white render", RND), ("warm render", RND2), ("painted fascia", FAS),
          ("concrete", CONC), ("dark timber", TIMD), ("light timber", TIML),
          ("slate tile", TILG), ("clay tile", TILB), ("flat roof", FELT),
          ("glass", GLS)]
ACC = [("orange", ORG), ("mustard", MUS), ("olive", OLV), ("teal", TEAL),
       ("navy", NVY), ("green", GRN), ("red", RED)]

x = MX
for nm, col in SWATCH:
    parts.append('<rect x="%.0f" y="%.0f" width="30" height="30" rx="7" fill="%s" '
                 'stroke="%s" stroke-width="1"/>' % (x, fy + 16, hexc(col), RULE))
    t(x, fy + 62, nm, 11.5, TXT2, "400")
    x += 92

t(W - MX, fy + 2, "ACCENT SET &#183; ONE PER BUILDING", 13, TXT, "700", ls=2.2, anchor="end")
x = W - MX - 7 * 62 + 32
for nm, col in ACC:
    parts.append('<rect x="%.0f" y="%.0f" width="30" height="30" rx="7" fill="%s" '
                 'stroke="%s" stroke-width="1"/>' % (x, fy + 16, hexc(col), RULE))
    x += 62

t(MX, fy + 100, "RULES HELD ACROSS ALL TWELVE — matte only, no gloss; geometry carries the "
                "detail, textures stay flat; one brick, one render, one timber, one tile; "
                "a deep painted fascia wherever a roof stops; one accent colour per building, "
                "used once and used hard; soft corners everywhere; generous openings.",
  13.5, TXT2, "400")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
