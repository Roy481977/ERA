import sys, math

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/era_art/era-composition.svg"

W = 2124
MX = 58
TOP = 186
TCW, TCH = 670, 596            # tile pitch (diagram 330 + text)
DGW, DGH = 640, 318            # diagram card
ROWS, COLS = 3, 3
MTX_H = 250
VER_H = 210
H = TOP + ROWS * TCH + MTX_H + VER_H + 40

PAPER = "#ffffff"
RULE = "#dcd8ce"
TXT = "#22242a"
TXT2 = "#7b7e87"
TXT3 = "#a3a6ae"

# diagram palette
HOUS = "#d9a58c"
HOUS2 = "#c98f74"
OAKC = "#7a9758"
MKTC = "#e07a30"
BAKC = "#e8b53c"
PUBC = "#2f7a52"
SCHC = "#4a7fb5"
GNDC = "#8d8674"
BUSC = "#3aa0a6"
FLOW_D = "#e07a30"             # daily errands
FLOW_K = "#3aa0a6"             # the school tide
FLOW_M = "#2f7a52"             # matchday
QUIET = "#eef0f4"
WATER = "#b9d0de"

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
t(MX + 126, 80, "TOWN COMPOSITION", 48, TXT, "300", ls=2.4)
rule(MX, 100, W - MX)
t(MX, 126, "THE SOCIAL STRUCTURE &#183; NINE COMPOSITIONS &#183; ONE CANON", 15, TXT2, "700", ls=2.2)
t(MX, 150, "Not assets, not environments &#8212; the shape of everyday life. Each diagram is a topology of "
           "encounters: where routines cross, friendships become accidents waiting to happen.",
  15, TXT2, "400")
t(W - MX, 126, "DESIGN STUDY &#183; NOT A MASTERPLAN", 13, TXT2, "700", anchor="end", ls=2.2)
_lx = W - MX - 560
t(_lx - 12, 150, "flows:", 13, TXT2, "400", anchor="end")
for (_c, _n, _dash) in ((FLOW_D, "daily errands", None),
                        (FLOW_K, "school tide", "3,6"), (FLOW_M, "matchday", None)):
    parts.append('<line x1="%.1f" y1="145.5" x2="%.1f" y2="145.5" stroke="%s" '
                 'stroke-width="4" stroke-linecap="round" %s/>'
                 % (_lx, _lx + 34, _c, ('stroke-dasharray="%s"' % _dash) if _dash else ''))
    t(_lx + 42, 150, _n, 13, _c, "700")
    _lx += 42 + len(_n) * 7.2 + 26
t(_lx, 150, "grey wash = quiet", 13, TXT3, "400")

# ---------------------------------------------------------------- diagram kit
class DG:
    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy
        self.sx = DGW / 100.0
        self.sy = (DGH - 16) / 52.0

    def P(self, x, y):
        return (self.ox + x * self.sx, self.oy + 8 + y * self.sy)

    def card(self):
        parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="10" '
                     'fill="#fbfaf7" stroke="%s" stroke-width="1.4"/>'
                     % (self.ox, self.oy, DGW, DGH, RULE))

    def wash(self, x, y, w, h, col=QUIET, op=1.0, r=14):
        X0, Y0 = self.P(x, y)
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
                     'fill="%s" opacity="%.2f"/>' % (X0, Y0, w * self.sx,
                                                     h * self.sy, r, col, op))

    def houses(self, pts, s=7):
        for (x, y) in pts:
            X0, Y0 = self.P(x, y)
            parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2" '
                         'fill="%s"/>' % (X0 - s / 2, Y0 - s / 2, s, s, HOUS))

    def cluster(self, cx, cy, n, rad):
        pts = []
        for i in range(n):
            a = i * 2.399963
            r = rad * math.sqrt((i + 0.7) / n)
            pts.append((cx + r * math.cos(a) * 1.6, cy + r * math.sin(a)))
        self.houses(pts)

    def node(self, x, y, kind, lab=None, big=False):
        X0, Y0 = self.P(x, y)
        r = 11 if big else 8
        if kind == "OAK":
            parts.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" opacity="0.3"/>'
                         % (X0, Y0, r + 7, OAKC))
            parts.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (X0, Y0, r, OAKC))
        elif kind == "MKT":
            parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="3" fill="%s"/>'
                         % (X0 - r, Y0 - r, 2 * r, 2 * r, MKTC))
        elif kind == "GND":
            parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="3" fill="none" '
                         'stroke="%s" stroke-width="3"/>' % (X0 - r - 4, Y0 - r + 2,
                                                             2 * r + 8, 2 * r - 4, GNDC))
            parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="2"/>' % (X0 - r + 1, Y0 - r - 4, X0 - r + 1, Y0 - r + 2, GNDC))
            parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="2"/>' % (X0 + r - 1, Y0 - r - 4, X0 + r - 1, Y0 - r + 2, GNDC))
        else:
            col = {"BAK": BAKC, "PUB": PUBC, "SCH": SCHC, "BUS": BUSC}[kind]
            parts.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (X0, Y0, r - 1, col))
        if lab:
            t(X0, Y0 - r - 5, lab, 10.5, TXT2, "700", anchor="middle", ls=0.8)

    def flow(self, pts, col, sw=4.5, op=0.75, dash=None, arrow=True):
        d = "M " + " L ".join("%.1f,%.1f" % self.P(x, y) for (x, y) in pts)
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                     'stroke-linecap="round" stroke-linejoin="round" opacity="%.2f" %s/>'
                     % (d, col, sw, op, ('stroke-dasharray="%s"' % dash) if dash else ''))
        if arrow and len(pts) >= 2:
            (x1, y1), (x2, y2) = self.P(*pts[-2]), self.P(*pts[-1])
            a = math.atan2(y2 - y1, x2 - x1)
            for da in (2.6, -2.6):
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                             'stroke-width="%.1f" stroke-linecap="round" opacity="%.2f"/>'
                             % (x2, y2, x2 - 10 * math.cos(a + da),
                                y2 - 10 * math.sin(a + da), col, sw, op))

    def water(self, pts, w=9):
        d = "M " + " L ".join("%.1f,%.1f" % self.P(x, y) for (x, y) in pts)
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                     'stroke-linecap="round" opacity="0.85"/>' % (d, WATER, w))


# ---------------------------------------------------------------- compositions
def c1(d):
    d.wash(2, 2, 22, 48); d.wash(76, 2, 22, 48)
    d.cluster(22, 14, 8, 9); d.cluster(22, 40, 8, 9)
    d.cluster(78, 14, 8, 9); d.cluster(78, 40, 8, 9)
    d.cluster(50, 6, 6, 8); d.cluster(50, 47, 6, 8)
    d.node(50, 26, "OAK"); d.node(45, 22, "MKT"); d.node(55, 22, "BAK")
    d.node(45, 30, "PUB"); d.node(55, 30, "SCH")
    d.node(88, 44, "GND", "GROUND")
    for (hx, hy) in ((22, 14), (22, 40), (78, 14), (50, 6), (50, 47)):
        d.flow([(hx, hy), (50, 26)], FLOW_D, 3.4)
    d.flow([(50, 28), (70, 38), (86, 43)], FLOW_M, 6, 0.5)


def c2(d):
    d.wash(2, 2, 96, 12); d.wash(2, 40, 96, 10)
    for x in range(10, 92, 9):
        d.houses([(x, 14), (x + 4, 38)])
    d.node(12, 26, "SCH", "SCHOOL"); d.node(30, 26, "BAK")
    d.node(48, 26, "MKT", "MARKET"); d.node(62, 26, "OAK", "OAK")
    d.node(72, 26, "PUB"); d.node(90, 26, "GND", "GROUND")
    d.flow([(8, 26), (44, 26)], FLOW_D, 5)
    d.flow([(54, 26), (86, 26)], FLOW_M, 5, 0.55)
    d.flow([(14, 22), (46, 22)], FLOW_K, 3, dash="2,6")


def c3(d):
    n = 10
    ring = [(50 + 30 * math.cos(i * 2 * math.pi / 40),
             26 + 19 * math.sin(i * 2 * math.pi / 40)) for i in range(41)]
    d.flow(ring, FLOW_D, 4.5, 0.55, arrow=False)
    d.node(50, 26, "OAK", "OAK")
    d.node(20, 26, "MKT"); d.node(80, 26, "PUB"); d.node(50, 7, "SCH")
    d.node(50, 45, "BAK"); d.node(74, 9, "GND", "GROUND")
    for i in range(8):
        a = i * math.pi / 4
        d.cluster(50 + 40 * math.cos(a), 26 + 25 * math.sin(a), 4, 5)
    d.flow([(35, 15), (50, 26)], FLOW_K, 3, dash="2,6")
    d.flow([(66, 17), (73, 11)], FLOW_M, 5, 0.5)


def c4(d):
    d.water([(62, 0), (60, 14), (63, 30), (61, 52)])
    d.wash(70, 2, 28, 20)
    d.cluster(22, 12, 8, 9); d.cluster(20, 38, 9, 10); d.cluster(42, 44, 6, 7)
    d.node(38, 24, "OAK", "OAK"); d.node(30, 20, "MKT"); d.node(46, 19, "BAK")
    d.node(45, 29, "PUB"); d.node(24, 27, "SCH")
    d.node(84, 38, "GND", "GROUND")
    d.flow([(20, 30), (34, 25)], FLOW_D, 4)
    d.flow([(44, 40), (39, 28)], FLOW_D, 3.2)
    d.flow([(40, 26), (61, 26), (78, 34)], FLOW_M, 7, 0.55)
    t(*(lambda p: (p[0], p[1]))(d.P(61, 24)), "", 1)
    t(d.P(61, 22)[0], d.P(61, 22)[1], "the bridge", 10.5, "#5b7c96", "700",
      anchor="middle")


def c5(d):
    d.wash(2, 2, 96, 9); d.wash(2, 44, 96, 7)
    d.cluster(18, 10, 7, 8); d.cluster(80, 10, 7, 8)
    d.cluster(18, 44, 7, 8); d.cluster(80, 44, 7, 8)
    d.node(30, 26, "MKT", "MARKET"); d.node(24, 21, "BAK"); d.node(36, 21, "BUS")
    d.node(70, 26, "OAK", "OAK"); d.node(64, 31, "PUB"); d.node(22, 32, "SCH")
    d.node(90, 15, "GND", "GROUND")
    d.flow([(34, 26), (66, 26)], FLOW_D, 5.5)
    d.flow([(66, 24), (36, 24)], FLOW_D, 3.2)
    d.flow([(72, 24), (87, 17)], FLOW_M, 6, 0.55)
    d.flow([(24, 30), (30, 27)], FLOW_K, 3, dash="2,6")


def c6(d):
    d.node(50, 26, "GND", "GROUND");
    ring = [(50 + 26 * math.cos(i * math.pi / 20),
             26 + 17 * math.sin(i * math.pi / 20)) for i in range(41)]
    d.flow(ring, FLOW_D, 4, 0.5, arrow=False)
    d.node(24, 26, "MKT"); d.node(76, 26, "PUB"); d.node(50, 9, "BAK")
    d.node(50, 43, "SCH"); d.node(32, 12, "OAK")
    for i in range(8):
        a = i * math.pi / 4
        d.cluster(50 + 38 * math.cos(a), 26 + 24 * math.sin(a), 4, 5)
    t(d.P(50, 30)[0], d.P(50, 30)[1], "empty 13 days of 14", 10.5, "#a09a8a",
      "700", anchor="middle")


def c7(d):
    d.cluster(16, 12, 9, 9); d.node(16, 19, "BAK")
    d.cluster(16, 42, 9, 9); d.node(21, 36, "SCH")
    d.cluster(52, 46, 9, 9); d.node(46, 40, "PUB")
    d.node(48, 22, "OAK", "SHARED GREEN"); d.node(56, 18, "MKT")
    d.node(84, 30, "GND", "GROUND")
    d.flow([(20, 14), (44, 21)], FLOW_D, 3.2)
    d.flow([(20, 40), (44, 24)], FLOW_D, 3.2)
    d.flow([(52, 42), (50, 27)], FLOW_D, 3.2)
    d.flow([(52, 23), (80, 29)], FLOW_M, 5.5, 0.55)
    d.flow([(20, 38), (24, 20)], FLOW_K, 3, dash="2,6")


def c8(d):
    d.wash(2, 2, 96, 10); d.wash(2, 42, 96, 8)
    for x in range(14, 88, 10):
        d.houses([(x, 14), (x + 5, 40)])
    d.node(10, 26, "SCH", "SCHOOL"); d.node(38, 26, "MKT"); d.node(44, 21, "BAK")
    d.node(58, 26, "OAK", "OAK"); d.node(64, 31, "PUB")
    d.node(90, 26, "GND", "GROUND")
    d.flow([(12, 23), (36, 23)], FLOW_K, 5, dash="3,7")
    d.flow([(36, 23), (12, 23)], FLOW_K, 2.4, dash="2,8")
    d.flow([(30, 29), (55, 29)], FLOW_D, 4)
    d.flow([(60, 25), (86, 25)], FLOW_M, 5.5, 0.5)
    t(d.P(23, 18)[0], d.P(23, 18)[1], "the tide, twice a day", 10.5, BUSC,
      "700", anchor="middle")


def c9(d):
    d.wash(2, 2, 20, 48); d.wash(80, 2, 18, 48)
    d.water([(70, 0), (68, 16), (71, 34), (69, 52)])
    d.cluster(14, 12, 6, 7); d.cluster(12, 38, 7, 8); d.cluster(38, 8, 6, 7)
    d.cluster(36, 46, 6, 7); d.cluster(88, 10, 5, 6)
    d.node(10, 26, "SCH", "SCHOOL"); d.node(30, 26, "BAK")
    d.node(44, 26, "MKT", "MARKET"); d.node(52, 20, "BUS")
    d.node(57, 27, "OAK"); d.node(62, 31, "PUB")
    t(d.P(57, 34)[0], d.P(57, 34)[1] + 10, "OAK &#183; THE CROSSING", 10.5,
      TXT2, "700", anchor="middle", ls=0.8)
    d.node(88, 42, "GND", "GROUND")
    d.flow([(8, 26), (43, 26)], FLOW_D, 5)                      # daily line
    d.flow([(12, 24), (40, 24)], FLOW_K, 3, dash="2,6")         # school tide
    d.flow([(38, 8), (52, 18), (56, 24)], FLOW_D, 3.2)
    d.flow([(36, 44), (52, 33), (56, 28)], FLOW_D, 3.2)
    d.flow([(58, 27), (70, 33), (84, 40)], FLOW_M, 6.5, 0.55)   # weekly line
    t(d.P(75, 42)[0], d.P(75, 42)[1], "the bridge", 10.5, "#5b7c96", "700",
      anchor="middle")


COMPS = [
    ("T1", "THE SINGLE HEART", "everything meets in one square", c1,
     "everyone crosses everyone, daily; the town has one unmistakable stage",
     "no gradient &#8212; the centre exhausts itself, the edges die; quiet is accidental, not designed",
     "public stories only: markets, announcements, spectacles &#8212; intimacy has nowhere to happen"),
    ("T2", "THE STRING", "one street carries the whole town", c2,
     "maximum repeated encounters &#8212; the same faces at the same times, every day",
     "no shortcuts, no discovery, no second route; the ends are exile; one blockage stops the town",
     "routine stories: the commuter who nods, the timed hellos &#8212; warm but monotone"),
    ("T3", "THE RING", "an orbit with the green at its centre", c3,
     "no dead ends; two directions mean chance meetings; the centre is always near",
     "all places equal &#8594; no heart, no climax; compression never happens; navigation is ambiguous",
     "coincidence stories &#8212; but few anchored memories; nowhere is THE place"),
    ("T4", "TWO SHORES", "the ground across the water, one bridge", c4,
     "matchday becomes pilgrimage; the bridge funnels the whole town into one shared moment",
     "the ground is exiled on the thirteen quiet days; the river cuts more than it joins",
     "ritual stories: the crossing, the bridge meeting, the returning crowd at dusk"),
    ("T5", "TWIN CENTRES", "market at one end, Oak at the other", c5,
     "busy and quiet built in; walking has direction; District 01 is this structure",
     "two hearts can split loyalty; the connecting street must never fail or both centres do",
     "contrast stories: commerce vs. calm, the walk between moods"),
    ("T6", "STADIUM AT THE HEART", "the town orbits the ground", c6,
     "football permeates &#8212; literally; matchday is effortless",
     "violates the brief: the ground dominates and lies empty 13 days of 14; a dead heart most of the time",
     "football stories only &#8212; the town has no life to return to on Sunday"),
    ("T7", "THE CONSTELLATION", "three hamlets, one shared green", c7,
     "neighbourhood identity &#8212; each hamlet its own anchor; natural rivalries (street teams!)",
     "cross-town encounters are rare; friends happen within hamlets, strangers stay strangers",
     "belonging and rivalry stories: our end, their end, the derby inside the town"),
    ("T8", "THE SCHOOL AXIS", "the children&#8217;s tide crosses everyone", c8,
     "generations overlap by design &#8212; the school run crosses the shopping run twice daily",
     "the rhythm collapses in holidays; adults without children orbit outside it",
     "growing-up stories: the walk that shortens as you age, teachers met in the market"),
    ("T9", "THE WEAVE", "two lines of different frequency, crossing at the Oak", c9,
     "the daily line (school&#8211;bakery&#8211;market) crosses the weekly line (homes&#8211;Oak&#8211;bridge&#8211;ground) "
     "at one point &#8212; everyone meets everyone, at different cadences; quiet edges survive",
     "the crossing must be sized with care &#8212; too small congests, too large dissipates",
     "every kind: routine on the daily line, ritual on the weekly, and their collisions at the Oak"),
]

for i, (code, name, thesis, fn, s, wk, st) in enumerate(COMPS):
    c, r = i % COLS, i // COLS
    ox = MX + c * (TCW + 10) if False else MX + c * ((W - 2 * MX - 2 * 30) // 3 + 30)
    ox = MX + c * (DGW + 44)
    oy = TOP + r * TCH
    d = DG(ox, oy)
    d.card()
    fn(d)
    ly = oy + DGH + 30
    t(ox, ly, code, 17, TXT, "700", ls=1.6)
    t(ox + 52, ly, name, 17, TXT, "400", ls=0.8)
    t(ox, ly + 21, thesis, 13, TXT2, "700")

    def wrap(s0, width=86):
        words = s0.split()
        line, lines = "", []
        for wd in words:
            if len(line) + len(wd) > width:
                lines.append(line); line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        return lines

    yy = ly + 42
    for pre, col, body in (("+", "#2f7a52", s), ("&#8722;", "#b0442c", wk),
                           ("&#9656;", TXT3, st)):
        for j, ln in enumerate(wrap(body)):
            t(ox + (0 if j == 0 else 16), yy, ("%s  " % pre if j == 0 else "") + ln,
              12.5, col if j == 0 else TXT2, "400")
            yy += 17
    del wrap

# ---------------------------------------------------------------- matrix
my0 = TOP + ROWS * TCH + 26
rule(MX, my0 - 14, W - MX)
t(MX, my0 + 6, "AGAINST THE NINE QUESTIONS (condensed to five)", 14, TXT, "700", ls=2.2)
CRIT = ["everyone meets", "repeated encounters", "quiet AND busy",
        "football permeates, gently", "one emotional heart"]
SCORES = {  # 2 = strong, 1 = partial, 0 = fails
    "T1": (2, 2, 0, 1, 2), "T2": (2, 2, 1, 1, 1), "T3": (1, 1, 1, 1, 0),
    "T4": (1, 1, 2, 2, 1), "T5": (2, 2, 2, 1, 1), "T6": (2, 1, 0, 0, 0),
    "T7": (0, 2, 2, 1, 1), "T8": (1, 2, 1, 1, 1), "T9": (2, 2, 2, 2, 2),
}
cx0 = MX + 240
for j, cr in enumerate(CRIT):
    t(cx0 + j * 300 + 40, my0 + 34, cr, 12.5, TXT2, "700", ls=0.6)
for i, (code, name, *_rest) in enumerate(COMPS):
    ry = my0 + 58 + i * 17.5
    t(MX, ry, "%s  %s" % (code, name), 12, TXT if code == "T9" else TXT2,
      "700" if code == "T9" else "400", ls=0.4)
    for j in range(5):
        sc = SCORES[code][j]
        col = "#2f7a52" if sc == 2 else ("#d9a53c" if sc == 1 else "#c04a30")
        fill = col if sc > 0 else "none"
        parts.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="%s" '
                     'stroke-width="1.6" %s/>' % (cx0 + j * 300 + 40 + 30, ry - 4,
                                                  fill if sc > 0 else "none", col,
                                                  'opacity="0.55"' if sc == 1 else ''))

# ---------------------------------------------------------------- verdict
vy0 = my0 + 58 + 9 * 17.5 + 26
rule(MX, vy0 - 14, W - MX)
t(MX, vy0 + 8, "THE VERDICT", 13, TXT, "700", ls=2.2)
t(W - MX, vy0 + 8, "DISTRICT 01 IS THE WEAVE&#8217;S CROSSING, ZOOMED IN", 13, TXT, "700",
  ls=2.2, anchor="end")
t(MX, vy0 + 32, "CANONICAL &#8212; <tspan font-weight=\"700\">T9 THE WEAVE</tspan>: a daily line (school &#183; bakery &#183; market) and a weekly line "
               "(homes &#183; Oak &#183; bridge &#183; ground) crossing at ONE point &#8212; the Oak, the pub on its corner, quiet lanes ringing the edges.",
  13.5, TXT2, "400")
t(MX, vy0 + 52, "The ground sits across the water at the weekly line&#8217;s end &#8212; floodlights and sound, never dominance &#8212; "
               "and on matchday the bridge turns the whole town into one procession (T4&#8217;s gift).",
  13.5, TXT2, "400")
t(MX, vy0 + 78, "WHY IT SUPPORTS THE SIMULATION &#8212; encounters are made by routines of DIFFERENT FREQUENCY sharing one node: "
               "daily crosses weekly crosses seasonal at the Oak, so familiar strangers are manufactured by geometry (Recognition, CD-003),",
  13.5, TXT2, "400")
t(MX, vy0 + 98, "friendships become accidents of repetition (CD-001), quiet edges give dyads somewhere to become stories, and the school "
               "tide guarantees the generations collide twice a day. Deterministic tides make watchable crowds (CD-006).",
  13.5, TXT2, "400")
t(MX, vy0 + 124, "REJECTED FOR THE RECORD &#8212; T6 (stadium at the heart) fails the brief outright: a dead centre 13 days of 14. "
                "T3 (the ring) has no heart at all. Both kept on the board so they are never re-argued.",
  13.5, TXT2, "400")

parts.append('</svg>')
open(OUT, "w").write("\n".join(parts))
print("wrote", OUT, W, "x", H)
