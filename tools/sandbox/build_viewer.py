"""
build_viewer — export one deterministic simulated year as a replayable,
self-contained HTML viewer (Phase 8: the Living Town).

The engine stays canonical: this runs the world once, then flattens the
record into compact JSON injected into viewer_template.html. The viewer
REPLAYS the year — which, in a deterministic world, IS watching the
simulation live. Nothing here is authored; every panel in the viewer
draws on the same record the historian reads.
"""
import json
import importlib
from world.engine import build_world
from world import behaviour
from world.historian import _idx, place_identity

dd = importlib.import_module("district01_data").DISTRICT
W = build_world(dd)
behaviour.run(W)
ix = _idx(W)
clock = W.clock
fb = W.football
st = W.state
h = W.rng.h

# ---------------------------------------------------------------- places
place_ids = sorted(W.places)
pcode = {pid: chr(65 + i) for i, pid in enumerate(place_ids)}
places_out = {}
for pid, pl in W.places.items():
    places_out[pid] = {
        "x": pl.loc[0] if pl.loc else None, "y": pl.loc[1] if pl.loc else None,
        "caps": sorted(pl.sat), "cover": pl.cover, "quiet": pl.quiet,
        "open": sorted(pl.open), "days": (sorted(pl.days) if pl.days is not None else None),
        "match_only": pl.matchday_only, "pub_": pl.public and bool(pl.sat),
    }

# ---------------------------------------------------------------- residents
res_out = []
for r in W.residents:
    res_out.append({
        "n": r["n"], "age": r["age"], "home": r["home"], "hh": str(r["hh"]),
        "child": bool(r.get("child")), "occ": r["occ"],
        "sup": ("season ticket" in r.get("poss", []) or r["tr"]["foot"] > 0.55),
        "arr": r.get("arrives", 0),
        # behavioural seeds — never displayed; they only make different people
        "tr": {k: round(r["tr"][k], 3) for k in ("soc", "rout", "out", "temper")},
    })

# per-resident per-day slot strings ('.'=home, '~'=not arrived, A..=places)
by_rd = {r["n"]: [["~" if day < r.get("arrives", 0) else "." for _ in range(7)]
                  for day in range(clock.ndays)] for r in W.residents}
for (day, s, n, p, why, iu, wx) in st["visits"]:
    by_rd[n][day][s] = "." if p == "home" else pcode[p]
pos_out = {n: ["".join(dayrow) for dayrow in rows] for n, rows in by_rd.items()}

# ---------------------------------------------------------------- fixtures
fixtures = []
for w in range(clock.weeks):
    res = fb.results.get(w)
    if not res:
        fixtures.append(None)
        continue
    gf, ga = res["score"]
    goals = sorted((1 + h("gmin", w, g) % 90) for g in range(gf))
    fixtures.append({"opp": res["opp"], "venue": res["venue"],
                     "result": res["result"], "gf": gf, "ga": ga,
                     "goals": goals})

# ---------------------------------------------------------------- events (curated)
events = []
for (dy, kind, pay) in st["eventlog"]:
    if kind == "arrival":
        events.append({"d": dy, "k": "arrive", "t": f"{pay['who']} moves in — a new face in town"})
    elif kind == "retirement":
        events.append({"d": dy, "k": "retire", "t": f"{pay['who']} retires after years as {pay['was']}"})
    elif kind == "borrow":
        events.append({"d": dy, "k": "borrow", "t": f"{pay['who']} borrows from {pay['lender']}"})
for (dy, a, b, k, pl) in st["argulog"]:
    if k == "argument":
        events.append({"d": dy, "k": "argue", "t": f"words between {a} and {b} at the {pl}"})
    else:
        events.append({"d": dy, "k": "peace", "t": f"{a} and {b} make peace at the {pl}"})
for r in W.residents:
    for dy, txt in r["log"]:
        if txt == "birthday":
            events.append({"d": dy, "k": "bday", "t": f"{r['n']}'s birthday"})
        elif "season ticket" in txt:
            events.append({"d": dy, "k": "ticket", "t": f"{r['n']} buys a season ticket"})
        elif txt.startswith("joined"):
            events.append({"d": dy, "k": "join", "t": f"{r['n']} {txt}"})
events.sort(key=lambda e: (e["d"], e["k"], e["t"]))

# first-recognition events for newcomers only (the viewer's "Roy recognises Bill")
recog = []
for r in W.residents:
    if not r.get("arrives"):
        continue
    for o, rl in r["rel"].items():
        if "named" in rl:
            recog.append({"d": rl["named"], "a": r["n"], "b": o})
recog.sort(key=lambda e: (e["d"], e["a"], e["b"]))

# ---------------------------------------------------------------- place stats
pstats = {}
for pid in place_ids:
    if not (W.places[pid].public and W.places[pid].sat):
        continue
    ident = place_identity(W, ix, pid)
    if not ident:
        continue
    tot, tags, regs = ident
    met = sum(1 for r in W.residents for o, rl in r["rel"].items()
              if rl["met"] and rl["met"][1] == pid and r["n"] < o)
    args = sum(1 for (dy, a, b, k, pl) in st["argulog"] if pl == pid and k == "argument")
    peace = sum(1 for (dy, a, b, k, pl) in st["argulog"] if pl == pid and k == "resolved")
    pstats[pid] = {"visits": tot, "tags": tags, "regulars": regs.split(", "),
                   "met": met, "args": args, "peace": peace}

# ---------------------------------------------------------------- intents
intents = [{"n": n, "kind": k, "tg": tg, "note": note, "b": b, "e": e, "st": stt}
           for (n, k, tg, note, b, e, stt) in st["intentlog"]]
for r in W.residents:
    for it in r["intents"]:
        if it["state"] == "open":
            intents.append({"n": r["n"], "kind": it["kind"], "tg": it["target"],
                            "note": it["note"], "b": it["born"],
                            "e": clock.ndays, "st": "open"})

# ---------------------------------------------------------------- level geometry
LV = dd["level"]
level = {
    "terrain": {k: list(v) for k, v in LV["terrain"].items() if k != "base"},
    "water": {"pts": [list(p) for p in LV["water"]["pts"]], "w": LV["water"]["w"]},
    "roads": [[r["x0"], r["y0"], r["x1"], r["y1"]] for r in LV["roads"]],
    "paths": [({"k": p["kind"], "r": [p["x0"], p["y0"], p["x1"], p["y1"]]}
               if "x0" in p else
               {"k": p["kind"], "pts": [list(q) for q in p["pts"]]})
              for p in LV["paths"]],
    "plots": [{"id": p["id"], "x": p["x"], "y": p["y"]} for p in LV["plots"]],
    "oak": [LV["landmarks"]["oak"]["x"], LV["landmarks"]["oak"]["y"]],
    "bridge": [LV["landmarks"]["bridge"]["x"], LV["landmarks"]["bridge"]["y"], LV["landmarks"]["bridge"]["w"]],
    "stand": [LV["landmarks"]["stand"]["x0"], LV["landmarks"]["stand"]["y"],
              LV["landmarks"]["stand"]["w"], LV["landmarks"]["stand"]["h"]],
    "floodlights": [list(p) for p in LV["landmarks"]["floodlights"]],
    "veg": [[v["x"], v["y"], 1 if "tree" in v["m"] else 0] for v in LV["veg"]],
    "stall": list(LV["stall_bay"]),
}
plot_loc = {k: list(v) for k, v in dd["plot_loc"].items()}
plot_loc["P12"] = plot_loc.get("P12", [104.0, 30.0])

# ------------------------------------------------------- walk graph
# nodes on road/path centrelines; junctions auto-stitched; every place and
# plot gets a door edge to its nearest network node. The Human Layer routes
# along this instead of teleporting across the green.
segs = []
for r in LV["roads"]:
    cy = (r["y0"] + r["y1"]) / 2
    segs.append(((r["x0"], cy), (r["x1"], cy)))
for p in LV["paths"]:
    if "x0" in p:
        segs.append((((p["x0"] + 0), (p["y0"] + p["y1"]) / 2 if abs(p["y1"] - p["y0"]) < 3 else p["y0"]),
                     ((p["x1"]), (p["y0"] + p["y1"]) / 2 if abs(p["y1"] - p["y0"]) < 3 else p["y1"])))
    else:
        pts = p["pts"]
        for a, b in zip(pts, pts[1:]):
            segs.append((tuple(a), tuple(b)))
# the road to the match: market -> bridge -> turnstiles
segs += [((108.0, 18.2), (117.0, 20.0)), ((117.0, 20.0), (128.0, 24.0)),
         ((128.0, 24.0), (137.4, 27.2)), ((137.4, 27.2), (146.0, 40.0)),
         ((146.0, 40.0), (152.0, 47.6)),
         ((-8.0, 15.0), (-8.0, 26.0)), ((20.0, 42.5), (20.0, 30.0))]
nodes, edges = [], []


def _nid(pt):
    for i, q in enumerate(nodes):
        if abs(q[0] - pt[0]) < 3.2 and abs(q[1] - pt[1]) < 3.2:
            return i
    nodes.append([round(pt[0], 1), round(pt[1], 1)])
    return len(nodes) - 1


for a, b in segs:
    ia, ib = _nid(a), _nid(b)
    if ia != ib:
        edges.append([ia, ib])
# stitch any two nodes that nearly touch
for i in range(len(nodes)):
    for j in range(i + 1, len(nodes)):
        dx = nodes[i][0] - nodes[j][0]
        dy = nodes[i][1] - nodes[j][1]
        if dx * dx + dy * dy < 49 and [i, j] not in edges and [j, i] not in edges:
            edges.append([i, j])
doors = {}
for pid in place_ids:
    pl = W.places[pid]
    if pl.loc:
        doors[pid] = min(range(len(nodes)),
                         key=lambda i: (nodes[i][0] - pl.loc[0]) ** 2 + (nodes[i][1] - pl.loc[1]) ** 2)
for plot, loc in plot_loc.items():
    doors["@" + plot] = min(range(len(nodes)),
                            key=lambda i: (nodes[i][0] - loc[0]) ** 2 + (nodes[i][1] - loc[1]) ** 2)
graph = {"nodes": nodes, "edges": edges, "doors": doors}

DATA = {
    "meta": {"name": dd["name"], "seed": dd["seed"], "weeks": clock.weeks,
             "club": fb.name},
    "cal": {"mname": clock.mname, "mstart": clock.mstart,
            "holidays": sorted(clock.holidays), "family": clock.family_day,
            "breaks": [list(b) for b in clock.breaks]},
    "wx": "".join({"rain": "r", "wind": "w", "dry": "d"}[W.weather.at(dy)]
                  for dy in range(clock.ndays)),
    "placeIds": place_ids,
    "places": places_out,
    "residents": res_out,
    "pos": pos_out,
    "fixtures": fixtures,
    "events": events,
    "recog": recog,
    "pstats": pstats,
    "intents": intents,
    "level": level,
    "plotLoc": plot_loc,
    "graph": graph,
}

payload = json.dumps(DATA, separators=(",", ":"))
tpl = open("viewer_template.html").read()
out = tpl.replace("/*__DATA__*/null", payload)
open("era-living-town.html", "w").write(out)
print(f"era-living-town.html written: {len(out)//1024} KB "
      f"(data {len(payload)//1024} KB, {len(events)} events, {len(recog)} recognitions)")
