// ERA plate compositor — the living layer over plate-v1.
// Backdrop: the pre-graded plate. Living layer: residents/animals from the
// deterministic sim replay, positioned by a smooth world->plate mapping built
// from the plate-map pins, perspective-scaled and y-sorted.

const PLATE_W = 2048, PLATE_H = 2048;

// ===== Real-world scale & speeds (Roy's realism pass) ======================
// The built town spans ~1649 plate-px (measured across the place pixels). At a
// real town width of ~175 m that is ~9.4 px per metre. A sim tick is ultimately
// REAL TIME (Roy), so on-plate motion is paced in real seconds: a mover at v m/s
// covers v*PX_PER_M px per real second (state.anim, which runs continuously).
const TOWN_WIDTH_M = 175;                     // whole town ~150-200 m (Roy) -> use 175
const TOWN_PX = 1649;                         // measured px span of the town's places
const PX_PER_M = TOWN_PX / TOWN_WIDTH_M;      // ~9.42 px / metre
// A sim tick is ultimately REAL TIME (Roy), so motion is paced by a real-time
// clock (state.anim, seconds) at v*PX_PER_M px/sec — real speed on the plate,
// independent of the time-lapse pace slider.
const SPEED = {                               // real ground/air speeds, m/s
  walk: 1.35, hurry: 2.6, run: 4.5,           // people
  dog_amble: 1.0, fox_trot: 2.2, fox_run: 5.5,
  cat_walk: 1.0, cat_run: 4.0, hedgehog: 0.35,
  owl_soar: 5.0, crow_fly: 9.0, heron_fly: 9.0,
};
const pxPerSec = v => v * PX_PER_M;                  // px/sec on the plate at v m/s
// Ground movers (people, dog, fox, cats, hedgehog) are paced along their route at
// their own real speed, measured in sim-time (state.t, which respects pause and is
// deterministic). MOTION_TICK_S = how many seconds of motion one tick represents;
// it sets how much of each leg's window is spent walking vs. waiting at the far end.
// (Tunable — the RELATIVE speeds below stay correct regardless.)
const MOTION_TICK_S = 20;
function moverSpeed(e) {
  const id = e.id, sig = e.sig;
  if (id === 'ani_fox') return SPEED.fox_trot;
  if (id === 'ani_tabby' || id === 'ani_blackcat') return SPEED.cat_walk;
  if (id === 'ani_hedgehog') return SPEED.hedgehog;
  if (id === 'the_old_dog') return SPEED.dog_amble;
  if (id.startsWith('ani_')) return SPEED.walk;              // any other wildlife
  let v = SPEED.walk;                                        // people
  if (sig === 'skip') v = SPEED.hurry;                       // children bound along
  else if (sig === 'cane' || sig === 'limp' || sig === 'load') v *= 0.72;  // stiff / laden / elderly
  return v;
}

// ===== Owl flight (compositor sky atmosphere) ==============================
// Owl launches from its perch, soars a slow wide loop over the town, and lands.
// Real speed: paced by state.anim (real seconds) at owl_soar m/s -> px/sec, so the
// soar is a genuine ~5 m/s glide regardless of the playback pace. Compositor-side
// proof; the sim's Act::Fly will later choose real crossings between perches.
// Two perches: the clock tower (lore home, high) and a visible stadium-rim ledge
// so landings are seen. The owl alternates — leaves one, soars, lands on the other.
const OWL_PERCHES = [ { x: 855, y: 251 }, { x: 880, y: 780 } ];
// A slow, low hunting glide over the town — a wide flat loop over the pitch and
// square, low enough to read against the rooftops (and in the default framed view).
const OWL_LOOP  = { cx: 890, cy: 640, ax: 450, ay: 90 };
const OWL_FRAMES = { perch: 8, takeoff: 8, soar: 14, land: 8 };
const OWL_REST = 15, OWL_UP = 3.5, OWL_DN = 4.5;            // fixed launch/land/rest (s)
function owlLoopPt(s) { const a = -Math.PI / 2 + s * 2 * Math.PI;
  return { x: OWL_LOOP.cx + OWL_LOOP.ax * Math.cos(a),
           y: OWL_LOOP.cy + OWL_LOOP.ay * Math.sin(a) + 7 * Math.sin(s * 4 * Math.PI) }; }  // gentle bob
function owlSoarDur() { const a = OWL_LOOP.ax, b = OWL_LOOP.ay;
  const perim = Math.PI * (3 * (a + b) - Math.sqrt((3 * a + b) * (a + 3 * b)));
  return perim / pxPerSec(SPEED.owl_soar); }
function owlFlight(rt) {                                     // rt = real seconds
  const soarDur = owlSoarDur();
  const cycle = OWL_REST + OWL_UP + soarDur + OWL_DN;        // constant -> stable cycle index
  const ci = Math.floor(rt / cycle);
  const fromP = OWL_PERCHES[((ci % 2) + 2) % 2], toP = OWL_PERCHES[((ci + 1) % 2 + 2) % 2];
  const start = owlLoopPt(0), end = owlLoopPt(1);
  let u = rt - ci * cycle;
  if (u < OWL_REST) return { clip: 'perch', x: fromP.x, y: fromP.y, dir: 1 };
  u -= OWL_REST;
  if (u < OWL_UP) { const k = ease01(u / OWL_UP); return { clip: 'takeoff', aloft: true,
    x: lerp(fromP.x, start.x, k), y: lerp(fromP.y, start.y, k), dir: start.x >= fromP.x ? 1 : -1, bank: 0.25 * k }; }
  u -= OWL_UP;
  if (u < soarDur) { const s = u / soarDur; const p = owlLoopPt(s), p2 = owlLoopPt((s + 0.02) % 1);
    const dx = p2.x - p.x; return { clip: 'soar', aloft: true, x: p.x, y: p.y,
    dir: dx >= 0 ? 1 : -1, bank: 0.30 * Math.sin(s * 2 * Math.PI) }; }
  u -= soarDur;
  const k = ease01(u / OWL_DN); return { clip: 'land', aloft: true,
    x: lerp(end.x, toP.x, k), y: lerp(end.y, toP.y, k), dir: toP.x >= end.x ? 1 : -1, bank: 0.22 * (1 - k) };
}
function drawOwl() {
  if (!state.owl) return;
  const fs = owlFlight(state.anim || 0);
  const sheet = state.owl[fs.clip]; if (!sheet) return;
  const frames = OWL_FRAMES[fs.clip];
  const [sx, sy] = P2S(fs.x, fs.y);
  const cellW = sheet.width / frames, cellH = sheet.height;
  const rate = fs.clip === 'takeoff' ? 12 : fs.clip === 'soar' ? 10 : fs.clip === 'land' ? 9 : 4;  // sprite fps
  const fi = ((Math.floor((state.anim || 0) * rate) % frames) + frames) % frames;
  // stylised size (matches the plate's figurine scale, not literal 0.9 m), a
  // touch larger when aloft so the spread wings read; scaled by view + a gentle
  // perspective. Anchored at centre when flying, at the feet when perched.
  const skySc = 0.62 * view.s;
  const targetH = (fs.aloft ? 84 : 40) * (fs.aloft ? skySc : scaleAt(fs.y) * view.s);
  const dh = targetH, dw = targetH * (cellW / cellH);
  // soft ground shadow below the aloft owl — sells altitude. Falls down and a
  // little away from the upper-right sun; fainter/smaller the higher it flies.
  if (fs.aloft) {
    const drop = dh * 0.9;                         // screen px between bird and its shadow
    ctx.save();
    ctx.globalAlpha = 0.16;
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.ellipse(sx - drop * 0.18, sy + drop, dw * 0.32, dw * 0.11, 0, 0, 7);
    ctx.fill();
    ctx.restore();
  }
  ctx.save();
  ctx.translate(sx, sy);
  ctx.scale(fs.dir < 0 ? -1 : 1, 1);              // face travel
  if (fs.bank) ctx.rotate((fs.dir < 0 ? -1 : 1) * fs.bank);   // lean into the turn
  if (fs.aloft) ctx.drawImage(sheet, fi * cellW, 0, cellW, cellH, -dw / 2, -dh / 2, dw, dh);
  else ctx.drawImage(sheet, fi * cellW, 0, cellW, cellH, -dw / 2, -dh, dw, dh);   // feet on the perch
  ctx.restore();
}
const PLATE_IMG = 'assets/plate-v2.jpeg';

const state = {
  world: null, frames: [], map: null, anchors: [],
  t: 0, playing: true, M: 120, last: 0,   // M = game-seconds per real-second (1 = true real time)
  legT: {},                               // per-entity leg start (for real-speed pacing)
  selected: null, lastFigs: [], story: [], storyAt: -1,
  showPins: false, showNames: false,
  plate: null,
};

async function boot() {
  let replay, map, plate;
  if (window.__INLINE) {                       // self-contained build
    replay = window.__INLINE.replay;
    map = window.__INLINE.map;
    plate = await loadImg(window.__INLINE.plate);
    state.occluder = window.__INLINE.occluder ? await loadImg(window.__INLINE.occluder) : null;
    state.miloSheet = window.__INLINE.miloSheet ? await loadImg(window.__INLINE.miloSheet) : null;
  } else {                                      // served build
    [replay, map, plate] = await Promise.all([
      fetch('assets/replay.json').then(r => r.json()),
      fetch('assets/era-plate-map-v2.json').then(r => r.json()),
      loadImg(PLATE_IMG),
    ]);
    // plate-v2 uses per-house occluder polygons from the map (not the v1 mask png).
    state.occluder = null;
    state.miloSheet = await loadImg('milo/milo_walk_sheet.png').catch(() => null);
    state.owl = {
      perch:   await loadImg('owl/owl_perch_sheet.png').catch(() => null),
      takeoff: await loadImg('owl/owl_takeoff_sheet.png').catch(() => null),
      soar:    await loadImg('owl/owl_soar_sheet.png').catch(() => null),
      land:    await loadImg('owl/owl_land_sheet.png').catch(() => null),
    };
    if (!state.owl.soar) state.owl = null;
  }
  state.world = replay.world;
  state.frames = replay.frames;
  state.map = map;
  state.plate = plate;

  // roster: id -> {name, kind, color}; and place id -> name
  state.roster = {};
  for (const e of state.world.entities) state.roster[e.id] = e;
  state.locName = {};
  for (const l of state.world.locations) state.locName[l.id] = l.name;

  // indoor places: homes + workplaces that are inside. A settled resident here is
  // indoors, not standing on the roof — so we don't draw them (their window lights
  // up at night instead). Café/pub/square/market/riverside/ground stay visible.
  const INDOOR_WORK = ['loc_bakery', 'loc_club_shop', 'loc_corner_grocer', 'loc_club_offices', 'loc_museum', 'loc_school'];
  state.indoor = new Set([...state.world.locations.filter(l => l.home).map(l => l.id), ...INDOOR_WORK]);

  // obscured zones: polygons (plate px) the camera can't see past — anyone whose
  // feet fall inside is hidden. Authored in the plate-mapper's obscure tool.
  state.obscured = (map.obscured || []).map(z => z.pts || z);
  // moon-hide rooflines: the low moon is drawn BEHIND these, so it ducks behind the skyline.
  state.moonmask = (map.moonmask || []).map(z => z.pts || z).filter(z => z && z.length >= 3);
  // the stands are a solid structure: a real person WALKING the path behind them is
  // hidden by the terracing (only the seated fans show). Kept separate from obscured
  // so it applies to walkers only (settled spectators are placed in the stands).
  state.stands = (map.stands || []).map(z => z.pts || z).filter(z => z && z.length >= 3);

  // plate-space path network, so walkers follow the streets instead of straight
  // pin-to-pin lines (which cut across the river and buildings).
  // plate-v2 authors walkable PATHWAY AREAS (polygons) instead of line paths, so a
  // resident routes A->B across the painted ground (a nav-mesh), not along a rail.
  state.areaMode = !!(map.pathareas && map.pathareas.length);
  state.houses = (map.houses || []).map(z => z.pts || z).filter(z => z && z.length >= 3);
  state.pathareas = (map.pathareas || []).map(z => z.pts || z).filter(z => z && z.length >= 3);
  state.graph = state.areaMode ? buildAreaGraph(map) : buildPlateGraph(map);
  state.routeCache = {};
  // presence point per place: on the disc, pins sit ON the buildings, so anchor the
  // living layer to each place's ground doorstep (the path in front) instead of the
  // rooftop pin — residents then stand and start/finish on the walkable ground.
  state.ground = (state.areaMode && state.graph.ground) ? state.graph.ground : null;

  // anchors: world (x,y) from the replay's static locations <-> plate pixels. In area
  // mode these are the ground doorsteps (path in front of each building); otherwise the
  // raw pins. worldToPlate interpolates over them, so the whole living layer lands on
  // the walkable ground.
  const px = map.places;
  state.anchors = state.world.locations
    .filter(l => px[l.id])
    .map(l => { const g = state.ground && state.ground[l.id]; return { id: l.id, wx: l.x, wy: l.y, px: g ? g.x : px[l.id].x, py: g ? g.y : px[l.id].y }; });

  // house occluders (plate-v2): cut each house's own pixels out of the plate so a
  // resident walking BEHIND a house is covered by it (painter's algorithm, by depth).
  if (state.areaMode) buildHouseOccluder();
  // low fences (jump-over): flatten to segments so a route crossing one triggers a hop
  state.lowFences = [];
  for (const f of (map.fences || [])) if ((f.kind || 'low') !== 'wall') {
    const p = f.pts; for (let i = 1; i < p.length; i++) state.lowFences.push([p[i - 1][0], p[i - 1][1], p[i][0], p[i][1]]);
  }

  // river polyline (for animated shimmer) as an arc-length curve
  const rv = (map.paths || []).find(p => p.type === 'river');
  if (rv && rv.pts.length > 1) {
    const cum = [0]; for (let i = 1; i < rv.pts.length; i++) cum.push(cum[i - 1] + Math.hypot(rv.pts[i][0] - rv.pts[i - 1][0], rv.pts[i][1] - rv.pts[i - 1][1]));
    state.river = { pts: rv.pts, cum, len: cum[cum.length - 1] };
  }
  // water surface polygons (marked in the mapper) — ripple animates across them
  state.waterAreas = (map.water || []).map(z => z.pts || z);
  // drifting clouds (stable seeds; move with time)
  state.clouds = [];
  for (let i = 0; i < 5; i++) { const h = (i * 2654435761) >>> 0; state.clouds.push({ y: 40 + (h % 130), s: 26 + (h >> 4) % 34, sp: 3 + (h >> 8) % 5, ph: (h % 1000) / 1000, a: 0.05 + (h % 5) / 90 }); }

  // lamps: use the ones placed in the mapper if present; otherwise auto-place
  // (sample along streets/lanes + a few centre and back-of-town extras).
  if (map.lamps && map.lamps.length) {
    state.lamps = map.lamps.map(l => ({ x: l.x, y: l.y, kind: l.kind || 'light', small: !!l.small }));
  } else if (map.pathareas && map.pathareas.length) {
    state.lamps = [];   // plate-v2: no v1 auto-lamps (they'd land off-place); add lamps in the mapper
  } else {
    state.lamps = [];
    for (const p of (map.paths || [])) {
      if (p.type !== 'street' && p.type !== 'lane') continue;
      let acc = 0, next = 40;
      for (let i = 1; i < p.pts.length; i++) {
        const [ax, ay] = p.pts[i - 1], [bx, by] = p.pts[i];
        const segLen = Math.hypot(bx - ax, by - ay);
        if (segLen < 1e-3) continue;
        while (acc + segLen >= next) {
          const t = (next - acc) / segLen;
          state.lamps.push({ x: ax + (bx - ax) * t, y: ay + (by - ay) * t });
          next += 95;
        }
        acc += segLen;
      }
    }
    const CENTER = ['loc_main_square', 'loc_cafe', 'loc_pub', 'loc_bakery', 'loc_high_street',
      'loc_corner_grocer', 'loc_north_gate', 'loc_museum', 'loc_club_shop', 'loc_bridge'];
    for (const id of CENTER) {
      const p = map.places[id];
      if (p && p.x > 0 && p.x < PLATE_W) state.lamps.push({ x: p.x, y: p.y + 6 });
    }
    const EXTRA = [
      { x: 300, y: 240, small: true }, { x: 264, y: 244, small: true },
      { x: 905, y: 322 }, { x: 968, y: 326 }, { x: 1012, y: 340 }, { x: 878, y: 305 },
    ];
    for (const e of EXTRA) state.lamps.push(e);
    const inPitch = (x, y) => x > 990 && x < 1362 && y > 420 && y < 560;
    state.lamps = state.lamps.filter(L => !inPitch(L.x, L.y));
  }

  // stadium floodlights: four tall masts at the pitch corners, aimed into the pitch.
  // Use masts placed in the mapper if present, else these estimates (Roy can nudge).
  const discPlate = !!(map.pathareas && map.pathareas.length);
  state.floods = (map.floodlights && map.floodlights.length)
    ? map.floodlights.map(F => ({ x: F.x, y: F.y }))
    : discPlate ? [{ x: 600, y: 520 }, { x: 1080, y: 560 }, { x: 620, y: 700 }, { x: 1050, y: 720 }]  // plate-v2 bowl corners
    : [{ x: 1012, y: 430 }, { x: 1300, y: 452 }, { x: 1055, y: 512 }, { x: 1312, y: 504 }];
  state.floodAim = discPlate ? { x: 830, y: 620 } : { x: 1160, y: 470 };   // pitch centre

  // Game-night crowd: seats across the visible stands. On a match evening the terracing
  // fills with anonymous supporters (green & white) — a decorative crowd, not sim
  // residents. If Roy has outlined the stands in the mapper (map.stands polygons) the
  // seats are sampled inside those; otherwise a built-in estimate of the main + side
  // stand. Ordered by distance from the north gate so they populate from the entrance out.
  const gate = (map.places && map.places.loc_north_gate) || { x: 1070, y: 408 };
  const seats = [];
  const stands = (map.stands || []).map(z => z.pts || z);
  if (stands.length) {
    for (const poly of stands) {
      let minx = 1e9, miny = 1e9, maxx = -1e9, maxy = -1e9;
      for (const [px, py] of poly) { minx = Math.min(minx, px); miny = Math.min(miny, py); maxx = Math.max(maxx, px); maxy = Math.max(maxy, py); }
      for (let y = miny; y <= maxy; y += 6) for (let x = minx; x <= maxx; x += 8) {
        if (pointInPoly(x, y, poly)) seats.push({ x, y });
      }
    }
  } else {
    for (let row = 0; row < 6; row++) {               // main stand behind the pitch (tiered)
      const y = 376 + row * 6, x0 = 1046 + row * 4, x1 = 1298 - row * 2;
      for (let x = x0; x <= x1; x += 9) seats.push({ x, y });
    }
    for (let row = 0; row < 4; row++) {               // near side stand (left of the pitch)
      const x = 1036 - row * 6, y0 = 388 + row * 3, y1 = 424 - row * 2;
      for (let y = y0; y <= y1; y += 8) seats.push({ x, y });
    }
  }
  seats.sort((a, b) => ((a.x - gate.x) ** 2 + (a.y - gate.y) ** 2) - ((b.x - gate.x) ** 2 + (b.y - gate.y) ** 2));
  state.stadiumSeats = seats;

  sizeCanvas();
  window.addEventListener('resize', sizeCanvas);
  wireControls();
  // headless capture hooks
  window.__state = state; window.__draw = draw; window.__ready = true;
  window.__seek = (frame) => { state.playing = false; state.t = frame; draw(); };
  window.__getRoute = getRoute;
  window.__view = () => ({ s: view.s, ox: view.ox, oy: view.oy, z: zoom.z, cx: zoom.cx, cy: zoom.cy, cw: cnv.width, ch: cnv.height });
  window.__s2w = (sx, sy) => [ (sx - view.ox) / view.s, (sy - view.oy) / view.s ];
  window.__debugDraw = (arg) => { state.__dbg = Array.isArray(arg) ? { routes: arg } : arg; draw(); };
  requestAnimationFrame(loop);
}

function loadImg(src) {
  return new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
}

// --- smooth world -> plate mapping (Shepard / inverse-distance weighting) ---
// Passes exactly through every pin; blends smoothly between them. Off-frame
// places carry off-frame plate coords, so anyone walking there slides past the
// edge and out of view — exactly what we want.
function worldToPlate(wx, wy) {
  let sx = 0, sy = 0, sw = 0;
  for (const a of state.anchors) {
    const dx = wx - a.wx, dy = wy - a.wy;
    const d2 = dx * dx + dy * dy;
    if (d2 < 1e-6) return [a.px, a.py];
    const w = 1 / (d2 * d2);         // p = 4: tight, so pins dominate locally
    sx += a.px * w; sy += a.py * w; sw += w;
  }
  return [sx / sw, sy / sw];
}

// Entity -> plate pixel. While traveling, walk the street network leg-by-leg
// between adjacent place pins (no water-cutting); when settled, use the accurate
// near-pin IDW position (which preserves the sim's fine drift to benches/shade).
// Build a walkable graph in plate pixels: path polylines (streets/lanes/foot-
// paths, never the river) linked at junctions, with each place pin joined to its
// nearest path points. Routes computed on this follow the streets.
function buildPlateGraph(map) {
  const V = [], adj = [];
  const addV = (x, y) => { const i = V.length; V.push({ x, y }); adj.push([]); return i; };
  const link = (a, b) => {
    if (a === b) return; const w = Math.hypot(V[a].x - V[b].x, V[a].y - V[b].y);
    adj[a].push([b, w]); adj[b].push([a, w]);
  };
  const pathVerts = [], segs = [];                       // segs: consecutive path edges [a,b,pathIdx]
  const endpoints = [];                                   // {i,x,y,pathIdx} — first & last vertex of each path
  let pathIdx = -1;
  for (const p of (map.paths || [])) {
    if (p.type === 'river') continue;                    // river is not walkable
    pathIdx++;
    let prev = null; const verts = [];
    for (const [x, y] of p.pts) { const i = addV(x, y); pathVerts.push({ i, x, y }); verts.push({ i, x, y }); if (prev != null) { link(prev, i); segs.push([prev, i, pathIdx]); } prev = i; }
    if (verts.length) { endpoints.push(Object.assign({ pathIdx }, verts[0])); if (verts.length > 1) endpoints.push(Object.assign({ pathIdx }, verts[verts.length - 1])); }
  }
  // Make the paths one continuous web. (1) where two path segments actually CROSS,
  // drop a shared junction node at the crossing and wire it to both segments' ends, so
  // a route can turn from one path onto the other exactly at the intersection — all on
  // the drawn lines. (2) stitch path vertices that nearly touch (a small gap where Roy
  // meant two ways to meet).
  const segInt = (p1, p2, p3, p4) => {
    const d1x = p2.x - p1.x, d1y = p2.y - p1.y, d2x = p4.x - p3.x, d2y = p4.y - p3.y;
    const den = d1x * d2y - d1y * d2x; if (Math.abs(den) < 1e-9) return null;
    const t = ((p3.x - p1.x) * d2y - (p3.y - p1.y) * d2x) / den;
    const u = ((p3.x - p1.x) * d1y - (p3.y - p1.y) * d1x) / den;
    if (t <= 0.001 || t >= 0.999 || u <= 0.001 || u >= 0.999) return null;
    return { x: p1.x + t * d1x, y: p1.y + t * d1y };
  };
  for (let i = 0; i < segs.length; i++)
    for (let j = i + 1; j < segs.length; j++) {
      const [a1, b1] = segs[i], [a2, b2] = segs[j];
      if (a1 === a2 || a1 === b2 || b1 === a2 || b1 === b2) continue;   // already share a node
      const P = segInt(V[a1], V[b1], V[a2], V[b2]);
      if (P) { const vi = addV(P.x, P.y); link(vi, a1); link(vi, b1); link(vi, a2); link(vi, b2); }
    }
  // (3) T-junctions: where a path's ENDPOINT lands near a DIFFERENT path (one lane runs
  // into another), join it at the nearest point on that path. This closes the little gaps
  // that make a resident cut the corner — without laddering parallel lanes, because only
  // endpoints (not every mid-segment vertex) reach out.
  const ENDTH = 34;
  for (const ep of endpoints) {
    let best = ENDTH * ENDTH, foot = null, fa = -1, fb = -1;
    for (const [a, b, pi] of segs) {
      if (pi === ep.pathIdx) continue;                   // don't join a path to itself
      const ax = V[a].x, ay = V[a].y, bx = V[b].x, by = V[b].y, dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1;
      let t = ((ep.x - ax) * dx + (ep.y - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
      const fx = ax + t * dx, fy = ay + t * dy, d = (ep.x - fx) ** 2 + (ep.y - fy) ** 2;
      if (d < best) { best = d; foot = { x: fx, y: fy }; fa = a; fb = b; }
    }
    if (foot) { const vi = addV(foot.x, foot.y); link(vi, fa); link(vi, fb); link(vi, ep.i); }
  }
  const TH2 = 16 * 16;                                    // near-touch stitch (real intersections handled above)
  for (let a = 0; a < pathVerts.length; a++)
    for (let b = a + 1; b < pathVerts.length; b++) {
      const dx = pathVerts[a].x - pathVerts[b].x, dy = pathVerts[a].y - pathVerts[b].y;
      if (dx * dx + dy * dy <= TH2) link(pathVerts[a].i, pathVerts[b].i);
    }
  // nearest point on the path network to (x,y): project onto every path segment,
  // keep the closest foot. Returns {x,y,a,b} — the foot and the segment it lies on.
  const nearestOnPath = (x, y) => {
    let best = Infinity, res = null;
    for (const [a, b] of segs) {
      const ax = V[a].x, ay = V[a].y, bx = V[b].x, by = V[b].y;
      const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1;
      let t = ((x - ax) * dx + (y - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
      const fx = ax + t * dx, fy = ay + t * dy, d = (x - fx) ** 2 + (y - fy) ** 2;
      if (d < best) { best = d; res = { x: fx, y: fy, a, b }; }
    }
    return res;
  };
  const pinIdx = {};
  for (const [id, p] of Object.entries(map.places || {})) {
    // Places off the frame (the school, training ground, canal side, …) are real
    // destinations townsfolk walk out to. Anchor their ROUTE node at the frame edge
    // nearest their true spot so a journey there follows the streets to the edge and
    // then walks off-view — rather than snapping. (Their settled render still uses the
    // true off-frame coord, so they simply leave sight.)
    const cx = clamp(p.x, 6, PLATE_W - 6), cy = clamp(p.y, 6, PLATE_H - 6);
    const pi = addV(cx, cy); pinIdx[id] = pi;
    // Join the pin to the network at the NEAREST POINT ON A PATH (a short perpendicular
    // step onto the lane) rather than striking a straight line to a far vertex that
    // would cut across the buildings between them. Split the path segment at that foot
    // so travel then follows the traced ways only. Every place — the stadium included —
    // reaches the network through Roy's traced approach paths, never a straight stub.
    const f = nearestOnPath(cx, cy);
    if (f) { const fi = addV(f.x, f.y); link(fi, f.a); link(fi, f.b); link(pi, fi); }
  }
  return { V, adj, pinIdx };
}

// Build a walkable nav-mesh from PATHWAY AREAS (plate-v2). Sample a grid over the
// union of the pathway polygons, drop any node inside a house or the water, connect
// neighbours whose connecting step stays on the ground and crosses no wall, then hook
// each place pin onto the nearest walkable node. getRoute's Dijkstra runs on this
// unchanged — so a journey A->B threads the painted ground, avoiding houses and river.
function buildAreaGraph(map) {
  const areas = (map.pathareas || []).map(z => z.pts || z).filter(z => z && z.length >= 3);
  const houses = (map.houses || []).map(z => z.pts || z).filter(z => z && z.length >= 3);
  const waters = (map.water || []).map(z => z.pts || z).filter(z => z && z.length >= 3);
  const walls = [];
  for (const f of (map.fences || [])) if ((f.kind || 'low') === 'wall') {
    const p = f.pts; for (let i = 1; i < p.length; i++) walls.push([p[i - 1][0], p[i - 1][1], p[i][0], p[i][1]]);
  }
  const inAny = (x, y, polys) => { for (const p of polys) if (pointInPoly(x, y, p)) return true; return false; };
  const blocked = (x, y) => inAny(x, y, houses) || inAny(x, y, waters);
  const wallBlocked = (ax, ay, bx, by) => { for (const w of walls) if (segCross(ax, ay, bx, by, w[0], w[1], w[2], w[3])) return true; return false; };

  // Rasterise the walkable ground onto a fine grid, then DILATE it: the hand-drawn
  // pathway polygon pinches below grid width in places, breaking the network into
  // islands. Growing the raw mask by a few cells bridges those pinches (but never
  // into a house or the river, which we re-subtract), giving one connected ground.
  const S = 14, R = 3;                                       // cell size px, dilation radius (cells)
  let minx = Infinity, miny = Infinity, maxx = -Infinity, maxy = -Infinity;
  for (const a of areas) for (const [x, y] of a) { minx = Math.min(minx, x); miny = Math.min(miny, y); maxx = Math.max(maxx, x); maxy = Math.max(maxy, y); }
  minx -= (R + 1) * S; miny -= (R + 1) * S; maxx += (R + 1) * S; maxy += (R + 1) * S;
  const cols = Math.ceil((maxx - minx) / S) + 1, rows = Math.ceil((maxy - miny) / S) + 1;
  const cx = c => minx + c * S, cy = r => miny + r * S;
  const raw = new Uint8Array(cols * rows), walk = new Uint8Array(cols * rows);
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++)
    if (inAny(cx(c), cy(r), areas) && !blocked(cx(c), cy(r))) raw[r * cols + c] = 1;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    if (blocked(cx(c), cy(r))) continue;                     // never grow into a building/river
    let hit = 0;
    for (let dr = -R; dr <= R && !hit; dr++) for (let dc = -R; dc <= R; dc++) {
      const rr = r + dr, cc = c + dc; if (rr < 0 || rr >= rows || cc < 0 || cc >= cols) continue;
      if (raw[rr * cols + cc]) { hit = 1; break; }
    }
    if (hit) walk[r * cols + c] = 1;
  }

  const V = [], adj = [];
  const addV = (x, y) => { const i = V.length; V.push({ x, y }); adj.push([]); return i; };
  const link = (a, b) => { if (a === b) return; const w = Math.hypot(V[a].x - V[b].x, V[a].y - V[b].y); adj[a].push([b, w]); adj[b].push([a, w]); };
  const gi = new Int32Array(cols * rows).fill(-1);
  const at = (c, r) => (c >= 0 && c < cols && r >= 0 && r < rows) ? gi[r * cols + c] : -1;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) if (walk[r * cols + c]) gi[r * cols + c] = addV(cx(c), cy(r));
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const a = at(c, r); if (a < 0) continue;
    for (const [dc, dr] of [[1, 0], [0, 1], [1, 1], [1, -1]]) {
      const b = at(c + dc, r + dr); if (b < 0) continue;
      if (!wallBlocked(V[a].x, V[a].y, V[b].x, V[b].y)) link(a, b);
    }
  }
  // largest connected component — pins must attach to the main ground, not a stray islet
  const comp = new Int32Array(V.length).fill(-1); let nc = 0, mainC = 0, mainSz = -1;
  for (let i = 0; i < V.length; i++) {
    if (comp[i] >= 0) continue; const st = [i]; comp[i] = nc; let sz = 0;
    while (st.length) { const u = st.pop(); sz++; for (const [v] of adj[u]) if (comp[v] < 0) { comp[v] = nc; st.push(v); } }
    if (sz > mainSz) { mainSz = sz; mainC = nc; } nc++;
  }
  // hook each place pin to the nearest node in the main component (its doorstep onto
  // the ground). The doorstep is also the place's PRESENCE point: pins sit on the
  // building in the art, so a resident standing "at" a place stands on the path in
  // front of it, not on its roof. Homes are indoor (not drawn) so this is for the
  // visible places (plaza, café, the ground, riverside, the bridge…).
  // Each place's ROUTE + PRESENCE node is the walkable ground node nearest its DOOR
  // (Roy's marked entrance), not the rooftop pin — so residents arrive at, leave from,
  // and stand at the door on the path, never mid-wall or on the roof. Falls back to the
  // pin when no door is near.
  const doors = (map.doors || []);
  const pinIdx = {}, ground = {};
  for (const [id, p] of Object.entries(map.places || {})) {
    let tx = p.x, ty = p.y, bd = 150 * 150;                 // aim at the nearest door to the pin
    for (const d of doors) { const dd = (d.x - p.x) ** 2 + (d.y - p.y) ** 2; if (dd < bd) { bd = dd; tx = d.x; ty = d.y; } }
    let best = Infinity, bi = -1;                            // nearest walkable node to that door/pin
    for (let i = 0; i < V.length; i++) { if (comp[i] !== mainC) continue; const dd = (V[i].x - tx) ** 2 + (V[i].y - ty) ** 2; if (dd < best) { best = dd; bi = i; } }
    if (bi >= 0) { pinIdx[id] = bi; ground[id] = { x: V[bi].x, y: V[bi].y }; }
  }
  return { V, adj, pinIdx, comp, mainC, ground };
}

// Turn a raw polyline into a route {pts, cum, len}.
function polyRoute(pts) {
  const P = pts.map(([x, y]) => ({ x, y }));
  const cum = [0];
  for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + Math.hypot(P[i].x - P[i - 1].x, P[i].y - P[i - 1].y));
  return { pts: P, cum, len: cum[cum.length - 1], explicit: true };
}
// An explicitly traced A->B way: a path tagged with from/to place ids. This IS the
// route for that journey — followed exactly, no graph, no shortcuts. Reversed when
// the entity travels B->A.
function explicitPath(fromId, toId) {
  for (const p of (state.map.paths || [])) {
    if (p.type === 'river' || !p.from || !p.to || p.pts.length < 2) continue;
    if (p.from === fromId && p.to === toId) return polyRoute(p.pts);
    if (p.from === toId && p.to === fromId) return polyRoute(p.pts.slice().reverse());
  }
  return null;
}

// Route between two places: an explicit A->B traced way if one exists, otherwise the
// shortest route on the shared network (fallback for pairs Roy hasn't drawn yet).
function getRoute(fromId, toId) {
  const ck = fromId + '|' + toId;
  if (state.routeCache[ck] !== undefined) return state.routeCache[ck];
  const ex = explicitPath(fromId, toId);
  if (ex) { state.routeCache[ck] = addHops(ex); return state.routeCache[ck]; }
  const g = state.graph; if (!g) return (state.routeCache[ck] = null);
  const s = g.pinIdx[fromId], t = g.pinIdx[toId];
  if (s == null || t == null) return (state.routeCache[ck] = null);
  const n = g.V.length, dist = new Float64Array(n).fill(Infinity), prev = new Int32Array(n).fill(-1);
  const seen = new Uint8Array(n);
  dist[s] = 0;
  // simple O(n^2) Dijkstra (n is small)
  for (let k = 0; k < n; k++) {
    let u = -1, best = Infinity;
    for (let i = 0; i < n; i++) if (!seen[i] && dist[i] < best) { best = dist[i]; u = i; }
    if (u < 0 || u === t) break;
    seen[u] = 1;
    for (const [v, w] of g.adj[u]) if (dist[u] + w < dist[v]) { dist[v] = dist[u] + w; prev[v] = u; }
  }
  let route = null;
  if (dist[t] < Infinity) {
    let pts = []; for (let u = t; u !== -1; u = prev[u]) pts.push(g.V[u]); pts.reverse();
    if (state.areaMode) pts = chaikin(pts, 2);               // round the grid stair-steps into a natural line
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
    route = { pts, cum, len: cum[cum.length - 1] };
  }
  state.routeCache[ck] = addHops(route);
  return state.routeCache[ck];
}

// segment intersection point (or null) — for finding where a route crosses a fence
function segCross(ax, ay, bx, by, cx, cy, dx, dy) {
  const r1 = bx - ax, r2 = by - ay, s1 = dx - cx, s2 = dy - cy;
  const den = r1 * s2 - r2 * s1; if (Math.abs(den) < 1e-9) return null;
  const t = ((cx - ax) * s2 - (cy - ay) * s1) / den, u = ((cx - ax) * r2 - (cy - ay) * r1) / den;
  if (t < 0 || t > 1 || u < 0 || u > 1) return null;
  return [ax + t * r1, ay + t * r2];
}
// annotate a route with the points where it crosses a low fence (computed once, cached on the route)
function addHops(route) {
  if (!route || route.hopPts) return route;
  route.hopPts = [];
  const F = state.lowFences;
  if (F && F.length && route.pts && route.pts.length > 1)
    for (let i = 1; i < route.pts.length; i++) { const a = route.pts[i - 1], b = route.pts[i];
      for (const s of F) { const p = segCross(a.x, a.y, b.x, b.y, s[0], s[1], s[2], s[3]); if (p) route.hopPts.push(p); } }
  return route;
}
// Chaikin corner-cutting: smooths a polyline's stair-steps into a rounded line,
// keeping the endpoints. A couple of passes turns a grid route into a natural walk.
function chaikin(pts, iters) {
  let p = pts;
  for (let k = 0; k < iters; k++) {
    if (p.length < 3) break;
    const out = [p[0]];
    for (let i = 0; i < p.length - 1; i++) {
      const a = p[i], b = p[i + 1];
      out.push({ x: a.x * 0.75 + b.x * 0.25, y: a.y * 0.75 + b.y * 0.25 });
      out.push({ x: a.x * 0.25 + b.x * 0.75, y: a.y * 0.25 + b.y * 0.75 });
    }
    out.push(p[p.length - 1]);
    p = out;
  }
  return p;
}
function pointAlong(route, t) {
  const target = t * route.len, cum = route.cum, pts = route.pts;
  if (route.len < 1e-6) return [pts[0].x, pts[0].y];
  let i = 1; while (i < cum.length && cum[i] < target) i++;
  if (i >= pts.length) return [pts[pts.length - 1].x, pts[pts.length - 1].y];
  const seg = cum[i] - cum[i - 1] || 1, f = (target - cum[i - 1]) / seg;
  return [lerp(pts[i - 1].x, pts[i].x, f), lerp(pts[i - 1].y, pts[i].y, f)];
}

// Elevated perch points (plate px) — a bird lands UP here (a steeple, a rooftop),
// not on the ground like a pigeon. Keyed by entity id; extend as Roy sends the
// places each bird flies to. A bird with perches drifts between them over a day.
const PERCHES = {
  ani_owl: [{ x: 855, y: 251, name: 'the clock tower' }],
};
function perchFor(id, f) {
  const list = PERCHES[id]; if (!list || !list.length) return null;
  const drift = f ? (f.day | 0) * 2 + Math.floor((f.hour || 0) / 6) : 0;   // move a few times a day
  return list[(hashId(id) + drift) % list.length];
}

// Hand-placed rest spots (plate px), keyed by entity id then place id, so an animal
// beds down somewhere believable instead of dead-centre on a doorway pin. Add spots
// as Roy points out odd placements.
const SETTLE_SPOTS = {
  the_old_dog: {
    loc_riverside: [768, 590],   // curls up on the grass under the oak, off the quay/doors
  },
};

function placeEntity(e) {
  const P = state.map.places;
  if (e.moving && e.from && e.to && P[e.from] && P[e.to]) {
    const t = ease01(e.et || 0);            // accelerate out of a place, decelerate into the next
    const route = getRoute(e.from, e.to);
    const [jx, jy] = jitterPx(e.id, 2);
    if (route) { const [x, y] = pointAlong(route, t); return [x + jx, y + jy]; }
    const a = P[e.from], b = P[e.to];       // fallback: straight leg
    return [lerp(a.x, b.x, t) + jx, lerp(a.y, b.y, t) + jy];
  }
  // stadium: spectators/gatherers stand in the STANDS, not on the pitch. Only
  // the groundskeeper (tending the pitch) stays on the grass.
  if (!e.moving && e.place === 'loc_stadium' && !/pitch|grounds|mow|groundskeep/i.test(e.doing || '')) {
    const h = hashId(e.id);
    return [1020 + (h % 300), 388 + ((h >> 4) % 5) * 7];  // rows in the terracing
  }
  // animals settle at their place's ground spot (with a little jitter) rather than
  // a drifted world point that can land on a rooftop. A hand-placed rest spot
  // (plate px, per place) beds them down somewhere believable — a den on the grass,
  // not dead-centre on a doorway pin.
  if (!e.moving && (e.id === 'the_old_dog' || e.id.startsWith('ani_'))) {
    const spot = SETTLE_SPOTS[e.id] && SETTLE_SPOTS[e.id][e.place];
    if (spot) { const [jx, jy] = jitterPx(e.id, 2); return [spot[0] + jx, spot[1] + jy]; }
    if (P[e.place]) { const [jx, jy] = jitterPx(e.id, 3); return [P[e.place].x + jx, P[e.place].y + jy]; }
  }
  return worldToPlate(e.x, e.y);
}

// Keep a walker's FEET on the painted pathway: if the point has strayed off every
// pathway area (the nav-mesh is dilated for connectivity, so a route can clip a verge),
// pull it to the nearest point just inside the nearest pathway edge.
function clampToPath(px, py) {
  const areas = state.pathareas;
  if (!areas || !areas.length) return [px, py];
  for (const a of areas) if (pointInPoly(px, py, a)) return [px, py];   // already on a path
  let best = Infinity, fx = px, fy = py;
  for (const a of areas) for (let i = 0, j = a.length - 1; i < a.length; j = i++) {
    const ax = a[j][0], ay = a[j][1], bx = a[i][0], by = a[i][1], dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1;
    let t = ((px - ax) * dx + (py - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
    const cx = ax + t * dx, cy = ay + t * dy, d = (px - cx) ** 2 + (py - cy) ** 2;
    if (d < best) { best = d; fx = cx; fy = cy; }
  }
  return [fx, fy];
}

// small stable per-id pixel offset so figures sharing a spot don't perfectly stack
function jitterPx(id, r) {
  let h = 2166136261;
  for (let i = 0; i < id.length; i++) { h ^= id.charCodeAt(i); h = Math.imul(h, 16777619); }
  const a = (h % 360) * Math.PI / 180;
  return [Math.cos(a) * r, Math.sin(a) * r];
}

// perspective scale from plate y: further back (smaller y) => smaller figures
function scaleAt(py) {
  if (PLATE_H > 1200) {                                      // plate-v2 disc (2048): town spans ~py 420..1440
    const t = clamp((py - 420) / (1440 - 420), 0, 1);
    return lerp(0.9, 2.1, t);
  }
  const t = clamp((py - 230) / (700 - 230), 0, 1);
  return lerp(0.55, 1.35, t);
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const PSCALE = 1.7;   // people read too small against the disc — scale residents up ~70%

// --- motion-quality helpers (presence & individuality pass) ---
const ease01 = (t) => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };   // smoothstep: accel out of a place, decel into the next
// A stable per-resident "how they move" profile, derived from the id hash — so two
// people walking the same way never look like copies. All gentle multipliers.
function idTraits(id) {
  const h = hashId(id);
  const b = (n, lo, hi) => lo + (((h >> n) & 15) / 15) * (hi - lo);
  return {
    gait:    b(0, 0.82, 1.20),   // step rate
    stride:  b(4, 0.80, 1.22),   // step length
    bob:     b(8, 0.75, 1.25),   // vertical bounce
    upright: b(12, -0.5, 0.9),   // posture bias: <0 stoop, >0 tall
    swing:   b(16, 0.70, 1.30),  // arm swing amplitude
    idle:    b(20, 0.80, 1.25),  // idle fidget rate
    phase:   ((h >> 6) % 628) / 100,  // personal gait phase so steps aren't in lockstep
  };
}
// Eased facing: a continuous per-id value in [-1,1] that chases the target sign, so
// the left/right flip reads as a turn instead of an instant mirror.
function easeFace(id, target) {
  const m = (state.face || (state.face = {}));
  const cur = m[id] != null ? m[id] : target;
  m[id] = cur + (target - cur) * Math.min(1, (state.dt || 0.016) * 9);
  return m[id];
}

// --- canvas / layout ---
let cnv, ctx, view = { s: 1, ox: 0, oy: 0 };
let fit = { s: 1, ox: 0, oy: 0 };                          // plate-fit transform (no zoom)
const DISC = PLATE_H > 1200;                               // plate-v2 floating disc
const ZHOME = DISC ? 2.4 : 1;                              // start zoomed IN on the action (not the far whole-disc)
const ZCLOSE = DISC ? 5.5 : 2.6;                           // double-click close-up
const ZMAX = DISC ? 9 : 5;
let zoom = { z: ZHOME, cx: DISC ? 950 : PLATE_W / 2, cy: DISC ? 940 : PLATE_H / 2 };  // z + focus point (drag to pan, wheel to zoom)
let camDrag = null, suppressClick = false;
function sizeCanvas() {
  cnv = document.getElementById('c'); ctx = cnv.getContext('2d');
  const wrap = document.getElementById('stage');
  const cw = wrap.clientWidth, ch = wrap.clientHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  cnv.width = cw * dpr; cnv.height = ch * dpr;
  cnv.style.width = cw + 'px'; cnv.style.height = ch + 'px';
  // fit the plate into the stage (contain)
  const s = Math.min(cw / PLATE_W, ch / PLATE_H);
  fit.s = s * dpr;
  fit.ox = (cw * dpr - PLATE_W * fit.s) / 2;
  fit.oy = (ch * dpr - PLATE_H * fit.s) / 2;
  if (!cnv.__zoomBound) { cnv.__zoomBound = true;
    cnv.style.cursor = 'grab';
    cnv.addEventListener('dblclick', onDblClick);
    cnv.addEventListener('mousedown', onPanDown);
    window.addEventListener('mousemove', onPanMove);
    window.addEventListener('mouseup', onPanUp);
    cnv.addEventListener('wheel', onWheel, { passive: false }); }
  applyView();
}
// Compose the plate-fit with the current double-click zoom. The focus point stays
// centred; the plate is kept covering the view (no panning past the edges); z==1
// returns exactly the fit. Everything downstream reads view.s/ox/oy + P2S, so the
// whole living layer (figures, lights, weather, pins) zooms with it for free.
function applyView() {
  view.s = fit.s * zoom.z;
  view.ox = cnv.width / 2 - zoom.cx * view.s;
  view.oy = cnv.height / 2 - zoom.cy * view.s;
  if (PLATE_W * view.s <= cnv.width) view.ox = (cnv.width - PLATE_W * view.s) / 2;
  else view.ox = clamp(view.ox, cnv.width - PLATE_W * view.s, 0);
  if (PLATE_H * view.s <= cnv.height) view.oy = (cnv.height - PLATE_H * view.s) / 2;
  else view.oy = clamp(view.oy, cnv.height - PLATE_H * view.s, 0);
}
// Double-click toggles between the home view and a close-up centred where you clicked.
function onDblClick(e) {
  const rect = cnv.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (cnv.width / rect.width);
  const my = (e.clientY - rect.top) * (cnv.height / rect.height);
  if (zoom.z > ZHOME + 0.4) { zoom.z = ZHOME; }                         // pull back to home
  else { zoom.z = ZCLOSE; zoom.cx = (mx - view.ox) / view.s; zoom.cy = (my - view.oy) / view.s; }  // dive in
  cnv.style.cursor = 'grab'; applyView(); draw();
}
// Drag the plate to move around (pan). A drag suppresses the click-to-inspect.
function onPanDown(e) {
  const rect = cnv.getBoundingClientRect();
  camDrag = { x: e.clientX, y: e.clientY, cx: zoom.cx, cy: zoom.cy, sx: cnv.width / rect.width, sy: cnv.height / rect.height, moved: false };
}
function onPanMove(e) {
  if (!camDrag) return;
  const dx = (e.clientX - camDrag.x) * camDrag.sx, dy = (e.clientY - camDrag.y) * camDrag.sy;
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) camDrag.moved = true;
  if (camDrag.moved) { cnv.style.cursor = 'grabbing'; zoom.cx = camDrag.cx - dx / view.s; zoom.cy = camDrag.cy - dy / view.s; applyView(); draw(); }
}
function onPanUp() { if (!camDrag) return; if (camDrag.moved) suppressClick = true; camDrag = null; cnv.style.cursor = 'grab'; }
// Wheel zooms toward the cursor.
function onWheel(e) {
  e.preventDefault();
  const rect = cnv.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (cnv.width / rect.width), my = (e.clientY - rect.top) * (cnv.height / rect.height);
  const wx = (mx - view.ox) / view.s, wy = (my - view.oy) / view.s;
  zoom.z = clamp(zoom.z * (e.deltaY < 0 ? 1.12 : 1 / 1.12), 1, ZMAX);
  view.s = fit.s * zoom.z;                                              // new scale, then keep the cursor's world point fixed
  zoom.cx = wx - (mx - cnv.width / 2) / view.s; zoom.cy = wy - (my - cnv.height / 2) / view.s;
  applyView(); draw();
}
const P2S = (x, y) => [view.ox + x * view.s, view.oy + y * view.s];

// --- draw ---
function draw() {
  if (!cnv || cnv.width < 1 || cnv.height < 1 || !(view.s > 0)) return;   // no drawable surface yet
  const fi = Math.floor(state.t);
  const f = state.frames[fi];
  if (!f) return;
  const frac = state.t - fi;                                  // sub-tick progress
  const fB = state.frames[(fi + 1) % state.frames.length] || f;
  const nextById = {};
  for (const e of fB.entities) nextById[e.id] = e;
  const fP = state.frames[(fi - 1 + state.frames.length) % state.frames.length] || f;
  const prevById = {}; for (const e of fP.entities) prevById[e.id] = e;
  // social arrangement: the sim marks who's talking to whom (mutual `partner`) but often
  // stacks the pair on one spot. Place mutual conversation partners a step apart and turn
  // them to FACE each other, so their gestures read as a real exchange, not two blobs.
  const byId = {}; for (const e of f.entities) byId[e.id] = e;
  const pairPose = {};   // id -> {px,py,hd}
  for (const e of f.entities) {
    const p = e.partner && byId[e.partner];
    if (!p || p.partner !== e.id || e.id > p.id) continue;   // mutual, handle each pair once
    if (e.moving || p.moving || pairPose[e.id]) continue;    // settled conversation only
    const [ax, ay] = placeEntity(e), [bx, by] = placeEntity(p);
    const cx = (ax + bx) / 2, cy = (ay + by) / 2;
    const ang = (hashId(e.id + p.id) % 360) * Math.PI / 180;
    const d = 8, ox = Math.cos(ang) * d, oy = Math.sin(ang) * d * 0.4;   // flatten y for perspective
    pairPose[e.id] = { px: cx - ox, py: cy - oy, hd: (ox >= 0) ? Math.PI : 0 };   // face toward partner
    pairPose[p.id] = { px: cx + ox, py: cy + oy, hd: (ox >= 0) ? 0 : Math.PI };
  }
  ctx.clearRect(0, 0, cnv.width, cnv.height);
  // backdrop
  ctx.drawImage(state.plate, view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s);

  const night = nightFactor(f.hour, f.minute);
  const lit = lampsOn(f.hour, f.minute);
  const wx = weatherOf(f);                                     // today's sky, drives the weather layer

  const flood = floodOn(f);
  drawSky(night, wx);
  drawWater(night);
  drawLampPosts(lit);
  drawFloodPosts(flood);
  drawStadiumCrowd(f);   // game-night supporters filling the stands

  // living layer on the lit plate: map every entity, y-sort, draw back-to-front
  const figs = [];
  for (const e of f.entities) {
    // the owl is drawn by drawOwl() as a real-speed sky element (perch + flight),
    // not as a procedural ground figure.
    if (e.id === 'ani_owl' && state.owl) continue;
    const meta = state.roster[e.id] || { color: '#eee', kind: 'resident', name: e.id };
    const eN = nextById[e.id];                                 // next tick's state, for continuous motion
    // A "hop": the sim records some journeys (notably the dog & wildlife) as an
    // instantaneous change of place rather than a moving leg. Walk them along the
    // real street/path network between the two places so nothing teleports or
    // slides across a roof.
    const hop = !!(eN && frac > 0 && !e.moving && e.place && eN.place && e.place !== eN.place);
    const hopRoute = hop ? getRoute(e.place, eN.place) : null;
    // On a real travel leg (from/to set) the entity IS walking, even on the one
    // tick its instantaneous speed reads ~0 (leg start) — so the legs never freeze
    // mid-journey. Otherwise fall back to the speed test / a network hop.
    const onLeg = e.moving && e.from && e.to;
    let walking = (e.moving && ((e.spd || 0) > 0.03 || onLeg)) || (hop && hopRoute && hopRoute.len > 4);
    // Physical presence: instead of blinking out on arrival, a resident holds at the
    // doorway for a beat and fades under the building's occlusion (and reverses on exit).
    if ((meta.kind === 'resident' || meta.kind === 'dog') && !walking && state.indoor.has(e.place)) {
      const was = prevById[e.id];
      if (was && was.place === e.place && !was.moving) continue;   // fully inside — off the rooftops
      const dp = state.map.places[e.place], df = 1 - frac;          // just arrived: linger + fade at the door
      if (!dp || df <= 0.03) continue;
      const a = occlusionAlpha(dp.x, dp.y) * df;
      if (a > 0.02) figs.push({ e, meta, px: dp.x, py: dp.y, walking: false, hd: null, alpha: a });
      continue;
    }
    let [px, py] = placeEntity(e); let hd = null;
    // a bird at rest perches UP on a steeple/rooftop, not the ground like a pigeon
    const perched = !walking && !!PERCHES[e.id];
    if (perched) { const per = perchFor(e.id, f); if (per) { px = per.x; py = per.y; } }
    const conv = !walking && pairPose[e.id];                   // arranged conversation position
    if (conv) { px = conv.px; py = conv.py; hd = conv.hd; }
    else if (!perched && eN && frac > 0) {
      // On a real travel leg, follow the TRACED ROUTE continuously within the tick,
      // so the figure traces the curved street — not a straight chord between two
      // sparse per-tick samples (which, with few ticks per leg, read as a bee-line
      // through walls and fences). Applies to the dog, every animal, and residents.
      const legRoute = (e.moving && e.from && e.to) ? getRoute(e.from, e.to) : null;
      if (legRoute) {
        // Real-speed pacing: walk the route at the mover's own m/s (sim-time), then
        // hold at the destination until the schedule starts the next leg. Replaces
        // the old "stretch et across the whole leg window" (which was too slow).
        const key = e.from + '>' + e.to;
        let lt = state.legT[e.id];
        if (!lt || lt.key !== key) lt = state.legT[e.id] = { key, start: state.t };
        const travelled = Math.max(0, (state.t - lt.start)) * MOTION_TICK_S * moverSpeed(e) * PX_PER_M;
        const prog = clamp(travelled / Math.max(1, legRoute.len), 0, 1);
        const [jx, jy] = jitterPx(e.id, 2);
        const [rx, ry] = pointAlong(legRoute, prog);
        px = rx + jx; py = ry + jy;
        const [ax, ay] = pointAlong(legRoute, Math.min(1, prog + 0.02));            // face along the route
        hd = (ax - rx) >= 0 ? 0 : Math.PI;
        if (prog >= 1) walking = false;                        // arrived — stand and wait
      } else if (hopRoute && hopRoute.len > 4) {                // glide along the network (a place hop)
        [px, py] = pointAlong(hopRoute, frac);
        const [ax, ay] = pointAlong(hopRoute, Math.min(1, frac + 0.03));
        hd = (ax - px) >= 0 ? 0 : Math.PI;
      } else {
        const [nx, ny] = placeEntity(eN);
        if (Math.hypot(nx - px, ny - py) < 130) { px += (nx - px) * frac; py += (ny - py) * frac; }
      }
    }
    if (px < -40 || px > PLATE_W + 40 || py < -40 || py > PLATE_H + 40) continue; // off-frame
    let alpha = occlusionAlpha(px, py);     // soft fade behind buildings instead of a hard blink
    if (walking) alpha *= standsAlpha(px, py);   // a real person walking behind the stands is hidden by them (fans are seated, not walking)
    const wasX = prevById[e.id];            // emerging from a doorway: fade in over the first step out
    if (walking && wasX && !wasX.moving && wasX.place !== e.place && state.indoor.has(wasX.place)) alpha *= ease01(frac);
    if (alpha <= 0.02) continue;            // fully behind a building — skip
    // hop over a low fence: a vertical lift as the mover passes a fence crossing on its route
    let fenceHop = 0;
    if (walking && e.moving && e.from && e.to) {
      const r = getRoute(e.from, e.to);
      if (r && r.hopPts && r.hopPts.length) {
        const HOPR = 15;                                  // px around the crossing over which the hop rises & falls
        for (const hp of r.hopPts) { const d = Math.hypot(px - hp[0], py - hp[1]); if (d < HOPR) fenceHop = Math.max(fenceHop, Math.cos(Math.PI / 2 * d / HOPR)); }
        if (fenceHop > 0) { let A = meta.kind !== 'resident' ? 5.5 : 3.2;  // cats & the dog spring higher than people
          const s = e.sig; if (s === 'load' || s === 'cane' || s === 'limp') A *= 0.35;   // laden / stiff / elderly step over, barely a hop
          else if (s === 'skip') A *= 1.4;                                  // children bound over
          fenceHop *= A; }
      }
    }
    // keep people (and the dog) with their feet on the painted pathways; wild animals roam freely
    if (meta.kind === 'resident' || e.id === 'the_old_dog') { const [cx, cy] = clampToPath(px, py); px = cx; py = cy; }
    figs.push({ e, meta, px, py, walking, hd, alpha, hop: fenceHop });
  }
  figs.sort((a, b) => a.py - b.py);
  // remember screen positions for click-to-inspect
  state.lastFigs = figs.map(fig => { const [sx, sy] = P2S(fig.px, fig.py); return { id: fig.e.id, sx, sy, px: fig.px, py: fig.py, walking: fig.walking, sc: scaleAt(fig.py) * view.s }; });
  // selection ring under the chosen resident
  if (state.selected) {
    const lf = state.lastFigs.find(l => l.id === state.selected);
    if (lf) { ctx.strokeStyle = 'rgba(255,215,90,.95)'; ctx.lineWidth = Math.max(1.5, 1.6 * lf.sc); ctx.beginPath(); ctx.ellipse(lf.sx, lf.sy, 8 * lf.sc, 3 * lf.sc, 0, 0, 7); ctx.stroke(); }
  }
  // Depth draw: figures and house-occluders sorted together by their near (bottom)
  // edge. A figure behind a house is drawn before that house's silhouette and so is
  // covered by it; a figure in front is drawn after and stays visible.
  const items = figs.map(fig => ({ py: fig.py, fig }));
  if (state.houseMeta && state.houseMeta.length) for (const hm of state.houseMeta) items.push({ py: hm.frontY, hm });
  items.sort((a, b) => a.py - b.py);
  for (const it of items) {
    if (it.hm) { blitHouse(it.hm); continue; }
    const fig = it.fig; ctx.globalAlpha = fig.alpha != null ? fig.alpha : 1;
    if (fig.e.id === 'res_milo' && state.miloSheet) drawMiloSprite(fig);
    else drawFigure(fig, f);
    ctx.globalAlpha = 1;
  }

  drawOwl();   // the owl: perched on the clock tower, or soaring its slow sky loop

  // foreground occluder: front greenery over the living layer (2.5D depth).
  if (state.occluder) ctx.drawImage(state.occluder, view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s);

  drawWeatherGrade(wx, night);   // grey overcast wash + wet-street sheen over the whole scene

  // night lighting: multiply a warm light map over the whole composed scene, so
  // lamps and lit windows genuinely illuminate the buildings, ground and people
  // around them — everything else falls into real darkness.
  if (night > 0) applyLightMap(night, lit, f);
  drawMoon(night, f);      // the large slow moon, bright over the darkened sky (before rain)
  drawFloodBeams(flood);   // beam shafts + head flares over the lit scene
  drawFestival(festivalOn(f), f);   // strung lanterns + music over the square
  drawPrecip(wx, night);   // rain streaks / snow, wind-angled, over everything

  if (state.showPins) drawPins();
  drawHUD(f);
  if (state.__dbg) drawDebugOverlay(state.__dbg);
}
function drawDebugOverlay(routes) {
  const g = state.graph; if (!g) return;
  if (routes.markers) {   // {x,y,r,c} diagnostic dots
    ctx.save(); ctx.lineWidth = 2;
    for (const mk of routes.markers) { const [x, y] = P2S(mk.x, mk.y); ctx.strokeStyle = mk.c; ctx.fillStyle = mk.c.replace(')', ',.25)').replace('rgb', 'rgba'); ctx.beginPath(); ctx.arc(x, y, mk.r || 7, 0, 7); ctx.stroke(); }
    ctx.restore();
  }
  if (routes.paths) {   // raw traced path polylines in green — compare against the cyan graph
    ctx.save(); ctx.strokeStyle = 'rgba(40,255,90,.9)'; ctx.lineWidth = 3;
    for (const p of (state.map.paths || [])) { if (p.type === 'river') continue; ctx.beginPath(); p.pts.forEach((pt, i) => { const [x, y] = P2S(pt[0], pt[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.stroke(); }
    ctx.restore();
  }
  if (routes.obscured) {
    ctx.save(); ctx.fillStyle = 'rgba(255,40,40,.28)'; ctx.strokeStyle = 'rgba(255,60,60,.7)'; ctx.lineWidth = 1;
    for (const o of (state.map.obscured || [])) { const pts = o.pts || o; ctx.beginPath(); pts.forEach((p, i) => { const [x, y] = P2S(p[0], p[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath(); ctx.fill(); ctx.stroke(); }
    ctx.restore();
  }
  ctx.save();
  ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(80,200,255,.35)';
  for (let a = 0; a < g.adj.length; a++) for (const [b] of g.adj[a]) if (b > a) {
    const [ax, ay] = P2S(g.V[a].x, g.V[a].y), [bx, by] = P2S(g.V[b].x, g.V[b].y);
    ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
  }
  ctx.fillStyle = 'rgba(80,200,255,.7)';
  for (const v of g.V) { const [x, y] = P2S(v.x, v.y); ctx.fillRect(x - 1.5, y - 1.5, 3, 3); }
  for (const [fromId, toId, col] of (routes.routes || [])) {
    const r = getRoute(fromId, toId); if (!r) continue;
    ctx.strokeStyle = col || '#ff3b3b'; ctx.lineWidth = 3;
    ctx.beginPath();
    r.pts.forEach((p, i) => { const [x, y] = P2S(p.x, p.y); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
    ctx.stroke();
  }
  ctx.restore();
}

// Read the deterministic sky for this frame into a small render struct.
// grey = how heavily to wash the scene toward overcast; rain/snow/fog are flags.
function weatherOf(f) {
  const w = (f && f.weather) || {};
  const sky = w.sky || 'clear';
  const grey = ({ clear: 0, fair: 0.06, cloudy: 0.34, overcast: 0.62, rain: 0.56, snow: 0.40, fog: 0.52 })[sky] || 0;
  return {
    sky, grey,
    rain: sky === 'rain' ? 1 : 0,
    snow: sky === 'snow' ? 1 : 0,
    fog: sky === 'fog' ? 1 : 0,
    wet: !!w.wet, windy: !!w.windy,
  };
}

// Drifting clouds over the plate's sky band. On grey days the puffs turn denser,
// slatier and more numerous so the sky itself reads overcast, not just the ground.
// The large slow moon — ERA grew under two moons (seen, never said; residents never
// react). v1: one pale-cool moon with a warm-rimmed glow, hanging low over the
// stadium and drifting slowly across the night, its spot seeded per night. Drawn
// AFTER the night light-map so it reads bright against the dark sky, before rain.
// Build a foreground occluder from the house polygons: the plate's own pixels kept
// only inside each house footprint, transparent elsewhere. Drawn back-to-front,
// interleaved with the figures by depth, it re-covers anyone standing behind it.
function buildHouseOccluder() {
  state.houseOcc = null; state.houseMeta = [];
  if (!state.houses || !state.houses.length || !state.plate) return;
  const oc = document.createElement('canvas'); oc.width = PLATE_W; oc.height = PLATE_H;
  const g = oc.getContext('2d');
  g.drawImage(state.plate, 0, 0, PLATE_W, PLATE_H);
  g.globalCompositeOperation = 'destination-in';           // keep plate pixels only inside the houses
  g.fillStyle = '#fff';
  for (const poly of state.houses) { g.beginPath(); poly.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.fill(); }
  state.houseOcc = oc;
  state.houseMeta = state.houses.map(poly => {
    let minx = 1e9, miny = 1e9, maxx = -1e9, maxy = -1e9;
    for (const [x, y] of poly) { minx = Math.min(minx, x); miny = Math.min(miny, y); maxx = Math.max(maxx, x); maxy = Math.max(maxy, y); }
    return { minx, miny, maxx, maxy, frontY: maxy };         // frontY = the house's near (bottom) edge
  });
}
// Blit one house's silhouette (its own plate pixels) over whatever's been drawn so far.
function blitHouse(hm) {
  if (!state.houseOcc) return;
  const w = hm.maxx - hm.minx, h = hm.maxy - hm.miny;
  ctx.drawImage(state.houseOcc, hm.minx, hm.miny, w, h,
    view.ox + hm.minx * view.s, view.oy + hm.miny * view.s, w * view.s, h * view.s);
}

function drawMoon(night, f) {
  if (night < 0.04) return;
  const day = (f.day | 0), h = (f.hour || 0) + (f.minute || 0) / 60;
  const s = ((day * 2654435761) >>> 0);
  const disc = PLATE_H > 1200;                              // plate-v2: over the disc's stadium
  const bx = disc ? 830 : 1200, by = disc ? 250 : 150;     // base position (over the ground)
  const mx = bx + (s % 100) - 50 + (h - 12) * 0.8;         // ±50px per night, a slow nightly drift
  const my = by + ((s >> 8) % 24) - (h - 21) * 0.35;      // large & a bit low
  const [sx, sy] = P2S(mx, my);
  const r = (disc ? 66 : 44) * view.s;
  const a = clamp(night, 0, 1);
  // clip the moon to everything EXCEPT the buildings/rooflines, so it ducks behind the
  // skyline. The moon is sky — always behind the town — so houses occlude it as well as
  // any explicit moon-hide rooflines (a tower, a tree not marked as a house).
  const occ = [...(state.houses || []), ...(state.moonmask || [])];
  ctx.save();
  if (occ.length) {
    ctx.beginPath(); ctx.rect(0, 0, cnv.width, cnv.height);
    for (const poly of occ) { poly.forEach((p, i) => { const [x, y] = P2S(p[0], p[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath(); }
    ctx.clip('evenodd');
  }
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const halo = (rad, col) => { const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rad); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(sx, sy, rad, 0, 7); ctx.fill(); };
  halo(r * 3.1, `rgba(190,208,234,${0.085 * a})`);          // broad cool halo
  halo(r * 1.75, `rgba(206,221,240,${0.20 * a})`);          // mid glow
  // face — pale cool disc, soft-edged (matte, not photoreal)
  { const g = ctx.createRadialGradient(sx - r * 0.22, sy - r * 0.22, 0, sx, sy, r);
    g.addColorStop(0, `rgba(236,241,249,${0.96 * a})`); g.addColorStop(0.72, `rgba(222,230,242,${0.82 * a})`); g.addColorStop(1, 'rgba(208,219,236,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(sx, sy, r, 0, 7); ctx.fill(); }
  // a faint warm rim so it still belongs to the warm district
  { const g = ctx.createRadialGradient(sx, sy, r * 0.78, sx, sy, r * 1.06);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.72, `rgba(255,224,180,${0.11 * a})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(sx, sy, r * 1.06, 0, 7); ctx.fill(); }
  ctx.restore();
  // faint maria — a hint of clay texture on the face
  ctx.save(); ctx.globalAlpha = 0.09 * a; ctx.fillStyle = 'rgba(150,166,192,1)';
  ctx.beginPath(); ctx.ellipse(sx - r * 0.26, sy - r * 0.14, r * 0.26, r * 0.2, 0.4, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.ellipse(sx + r * 0.22, sy + r * 0.24, r * 0.18, r * 0.15, -0.3, 0, 7); ctx.fill();
  ctx.restore();
  ctx.restore();   // moon-mask clip
}

function drawSky(night, wx) {
  if (!state.clouds) return;
  const grey = wx ? wx.grey : 0;
  const span = PLATE_W + 240;
  ctx.save(); ctx.globalCompositeOperation = grey > 0.25 ? 'source-over' : 'lighter';
  const T = state.anim || 0;
  // grey days: blanket the sky band with extra slate puffs riding lower and wider
  const passes = grey > 0.25 ? 2 : 1;
  const tint = grey > 0.25 ? [176, 182, 190] : [255, 255, 255];   // slate vs bright cloud
  for (let p = 0; p < passes; p++) {
    for (const c of state.clouds) {
      const drift = T * c.sp * 2.2 + p * 137;
      const x = ((c.ph * span + drift) % span) - 120;
      const yOff = p * 34 + grey * 26;                              // spread the cover down over the band
      const [sx, sy] = P2S(x, c.y + yOff); const r = Math.max(1, c.s * view.s) * (1 + grey * 0.8);
      const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, r * 2);
      const a = (c.a + grey * 0.10) * (1 - 0.7 * night);
      g.addColorStop(0, `rgba(${tint[0]},${tint[1]},${tint[2]},${a})`); g.addColorStop(1, `rgba(${tint[0]},${tint[1]},${tint[2]},0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.ellipse(sx, sy, r * 2, r * 0.9, 0, 0, 7); ctx.fill();
      ctx.beginPath(); ctx.ellipse(sx + r * 0.7, sy + r * 0.2, r * 1.2, r * 0.7, 0, 0, 7); ctx.fill();
    }
  }
  ctx.restore();
}

// Overcast wash + wet-street sheen over the fully composed scene. The grey grade
// is atmospheric (kept light so figures still read); the sheen only shows when wet.
function drawWeatherGrade(wx, night) {
  if (!wx) return;
  const X = view.ox, Y = view.oy, W = PLATE_W * view.s, H = PLATE_H * view.s;
  const day = 1 - 0.6 * night;
  if (wx.grey > 0.02) {
    // 1) drain the baked sunshine out of the scene, proportional to how grey the day is
    ctx.save();
    ctx.globalCompositeOperation = 'saturation';
    ctx.globalAlpha = Math.min(0.85, wx.grey * 0.9) * day;
    ctx.fillStyle = 'rgb(128,128,128)'; ctx.fillRect(X, Y, W, H);
    ctx.restore();
    // 2) cool grey overcast wash — heavier at the sky, lifting toward the ground
    ctx.save();
    const grad = ctx.createLinearGradient(0, Y, 0, Y + H);
    grad.addColorStop(0, `rgba(146,154,166,${0.36 * wx.grey * day})`);
    grad.addColorStop(1, `rgba(150,158,168,${0.16 * wx.grey * day})`);
    ctx.fillStyle = grad; ctx.fillRect(X, Y, W, H);
    ctx.restore();
  }
  if (wx.fog) {   // drifting low fog banks across the lower half
    const T = state.anim || 0;
    ctx.save();
    for (let i = 0; i < 3; i++) {
      const yy = Y + H * (0.55 + i * 0.14);
      const off = ((T * (6 + i * 3)) % (W + 300)) - 150;
      const g = ctx.createRadialGradient(X + off, yy, 0, X + off, yy, W * 0.42);
      g.addColorStop(0, `rgba(210,214,220,${0.16 * day})`); g.addColorStop(1, 'rgba(210,214,220,0)');
      ctx.fillStyle = g; ctx.fillRect(X, yy - H * 0.2, W, H * 0.4);
    }
    ctx.restore();
  }
  if (wx.wet) {   // cool reflective sheen on the lower ground — the streets are wet
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const grad = ctx.createLinearGradient(0, Y + H * 0.52, 0, Y + H);
    grad.addColorStop(0, 'rgba(126,156,182,0)'); grad.addColorStop(1, `rgba(134,166,192,${0.11 * day})`);
    ctx.fillStyle = grad; ctx.fillRect(X, Y + H * 0.52, W, H * 0.48);
    ctx.restore();
  }
}

// Precipitation over the whole viewport: parallel rain streaks (steeper when windy)
// or drifting snow. Recycled deterministic particles scrolled by the ambient clock.
function drawPrecip(wx, night) {
  if (!wx || (!wx.rain && !wx.snow)) return;
  const T = state.anim || 0, s = view.s, W = cnv.width, H = cnv.height;
  ctx.save();
  if (wx.rain) {
    const N = 260, slant = wx.windy ? 0.52 : 0.22, len = 14 * s;
    const fall = (wx.windy ? 640 : 520) * s, span = H + 60;
    ctx.lineCap = 'round';
    ctx.strokeStyle = `rgba(214,226,238,${(0.42 - 0.14 * night)})`;
    ctx.lineWidth = Math.max(0.7, 0.95 * s);
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const h = (i * 2654435761) >>> 0;
      const x = (h % 100000) / 100000 * (W + 260) - 130;
      const speed = fall * (0.78 + (h >> 5 & 255) / 255 * 0.5);
      const y = (((h >> 13 & 8191) / 8191) * span + T * speed) % span - 30;
      ctx.moveTo(x, y); ctx.lineTo(x - len * slant, y - len);
    }
    ctx.stroke();
  }
  if (wx.snow) {
    const N = 150, fall = 66 * s, span = H + 40, drift = wx.windy ? 2 : 1;
    ctx.fillStyle = `rgba(248,250,255,${0.9 - 0.35 * night})`;
    for (let i = 0; i < N; i++) {
      const h = (i * 2654435761) >>> 0;
      const x0 = (h % 100000) / 100000 * (W + 80) - 40;
      const speed = fall * (0.6 + (h >> 6 & 255) / 255 * 0.7);
      const y = (((h >> 13 & 8191) / 8191) * span + T * speed) % span - 20;
      const dx = Math.sin(T * 0.6 + (h & 63)) * 10 * s * drift;
      const r = (0.9 + (h & 3) * 0.4) * s;
      ctx.beginPath(); ctx.arc(x0 + dx, y, r, 0, 7); ctx.fill();
    }
  }
  ctx.restore();
}

// Animated river. If a water *area* is marked (mapper Water tool), ripple across
// the whole surface; otherwise fall back to shimmer streaks along the centerline.
function drawWater(night) {
  const T = state.anim || 0;
  if (state.waterAreas && state.waterAreas.length) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const a = 0.30 * (1 - 0.6 * night);                    // lighter overall
    for (const poly of state.waterAreas) {
      if (poly.length < 3) continue;
      ctx.save();
      ctx.beginPath();
      let minx = 1e9, miny = 1e9, maxx = -1e9, maxy = -1e9;
      poly.forEach((pt, i) => { const [x, y] = P2S(pt[0], pt[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); minx = Math.min(minx, x); miny = Math.min(miny, y); maxx = Math.max(maxx, x); maxy = Math.max(maxy, y); });
      ctx.closePath(); ctx.clip();
      const w = maxx - minx, h = maxy - miny;
      // scrolling ripple bands, drifting downstream (downward) — soft and faint
      const N = 7;
      for (let i = 0; i < N; i++) {
        const yy = miny + (((i / N) + T * 0.05) % 1) * (h + 24) - 12;
        const bh = 5 * view.s;
        const g = ctx.createLinearGradient(0, yy - bh, 0, yy + bh);
        g.addColorStop(0, 'rgba(196,238,244,0)'); g.addColorStop(0.5, `rgba(206,242,248,${a * 0.26})`); g.addColorStop(1, 'rgba(196,238,244,0)');
        ctx.fillStyle = g; ctx.fillRect(minx - 4, yy - bh, w + 8, bh * 2);
      }
      // drifting sparkle caustics — fewer, dimmer
      for (let k = 0; k < 9; k++) {
        const hx = (k * 2654435761) >>> 0;
        const sx = minx + (hx % 1000) / 1000 * w;
        const sy = miny + (((hx >> 10) % 1000) / 1000 + T * 0.08) % 1 * h;
        const rr = (1.1 + (hx % 3) * 0.5) * view.s;
        ctx.fillStyle = `rgba(220,246,250,${a * 0.32})`;
        ctx.beginPath(); ctx.ellipse(sx, sy, rr * 1.6, rr * 0.7, 0, 0, 7); ctx.fill();
      }
      // very little foam: a handful of tiny soft-white crests riding the ripple lines,
      // drifting downstream and gently blinking in and out so it never reads as spray
      const FOAM = 5;
      for (let k = 0; k < FOAM; k++) {
        const hx = ((k + 1) * 40503 * 2654435761) >>> 0;
        const fx = minx + (hx % 997) / 997 * w;
        const phase = ((hx >> 9) % 1000) / 1000;
        const fy = miny + ((phase + T * 0.05) % 1) * h;                 // rides with the bands
        const blink = Math.max(0, Math.sin((T * 0.5 + phase * 6.28)));  // fades in/out
        if (blink < 0.15) continue;
        const fr = (0.8 + (hx % 2) * 0.5) * view.s;
        ctx.fillStyle = `rgba(248,253,255,${0.16 * blink * (1 - 0.7 * night)})`;
        ctx.beginPath(); ctx.ellipse(fx, fy, fr * 1.5, fr * 0.6, 0, 0, 7); ctx.fill();
      }
      ctx.restore();
    }
    ctx.restore();
    return;
  }
  const r = state.river; if (!r) return;
  const at = t => { const target = t * r.len; let i = 1; while (i < r.cum.length && r.cum[i] < target) i++; if (i >= r.pts.length) i = r.pts.length - 1; const seg = r.cum[i] - r.cum[i - 1] || 1, f = (target - r.cum[i - 1]) / seg; const a = r.pts[i - 1], b = r.pts[i]; return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2(b[1] - a[1], b[0] - a[0])]; };
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const K = 12, alpha = 0.55 * (1 - 0.6 * night);
  for (let k = 0; k < K; k++) {
    const t = ((T * 0.07 + k / K) % 1);
    const [wx, wy, ang] = at(t); const [sx, sy] = P2S(wx, wy); const sc = scaleAt(wy) * view.s;
    const fade = Math.sin(t * Math.PI);   // dim at the ends of the run
    ctx.save(); ctx.translate(sx, sy); ctx.rotate(ang);
    const g = ctx.createLinearGradient(-8 * sc, 0, 8 * sc, 0);
    g.addColorStop(0, 'rgba(180,235,240,0)'); g.addColorStop(0.5, `rgba(200,240,245,${alpha * fade})`); g.addColorStop(1, 'rgba(180,235,240,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 0, 8 * sc, 1.5 * sc, 0, 0, 7); ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}

function drawPins() {
  for (const a of state.anchors) {
    if (a.px < 0 || a.px > PLATE_W) continue;
    const [x, y] = P2S(a.px, a.py);
    ctx.fillStyle = 'rgba(255,90,90,.9)';
    ctx.beginPath(); ctx.arc(x, y, 4, 0, 7); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.font = `${11 * (view.s)}px system-ui`;
    ctx.fillText(a.id.replace('loc_', ''), x + 6, y + 3);
  }
}

const SKINS = ['#e8b98f', '#d59a6e', '#c68a5c', '#f0c9a3', '#a9744e', '#8a5a3a'];
const HAIRS = ['#2c2016', '#4a2f1c', '#6b4a2a', '#8a6a3a', '#3a3a40', '#d8d2c8'];
function hashId(id) { let h = 2166136261; for (let i = 0; i < id.length; i++) { h ^= id.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const skinOf = id => SKINS[hashId(id) % SKINS.length];
const hairOf = id => HAIRS[(hashId(id) >> 3) % HAIRS.length];

// A resident's visible role right now, from what they're doing / where they are.
// Drives work clothing (apron, cap, jacket) so people read at a glance.
function roleOf(e) {
  const d = (e.doing || '').toLowerCase(), p = e.place;
  if (/bread|bakery|bakes|loaf|bun/.test(d) || p === 'loc_bakery') return 'baker';
  if (/grocer|groceries|greengroc/.test(d) || p === 'loc_corner_grocer') return 'grocer';
  if (/coach|training|groundskeep|grounds|pitch|mows|the old oak/.test(d) || p === 'loc_training_ground') return 'keeper';
  if (/ledger|club-office|club office|admin/.test(d) || p === 'loc_club_offices') return 'clerk';
  if (/kit|club shop/.test(d) || p === 'loc_club_shop') return 'shop';
  return null;
}

// Milo rendered as a real clay sprite (Meshy 3D -> plate-camera walk sheet) instead
// of the procedural figure. Walk cycle when moving; a near-still frame when settled.
// Anchored at the feet, scaled to the same on-screen height as the procedural adult
// (~20*sc), occlusion-faded via the caller's globalAlpha, flipped to face travel.
const MILO_FRAMES = 16;
function drawMiloSprite(fig) {
  const [x, y] = P2S(fig.px, fig.py);
  const sc = scaleAt(fig.py) * view.s;
  const sheet = state.miloSheet;
  const cellW = sheet.width / MILO_FRAMES, cellH = sheet.height;
  const moving = fig.walking;
  const idx = moving ? ((Math.floor(state.t * 8) % MILO_FRAMES) + MILO_FRAMES) % MILO_FRAMES : 3;
  const targetH = 23 * sc * PSCALE;                 // match the procedural adult's height
  const dh = targetH, dw = targetH * (cellW / cellH);
  const hd = fig.hd != null ? fig.hd : (fig.e.h || 0);
  const faceS = easeFace(fig.e.id, Math.cos(hd) >= 0 ? 1 : -1) >= 0 ? 1 : -1;  // eased turn to face travel
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(faceS, 1);
  ctx.drawImage(sheet, idx * cellW, 0, cellW, cellH, -dw / 2, -dh, dw, dh);
  ctx.restore();
}

function drawFigure(fig, f) {
  const { e, meta } = fig;
  let [x, y] = P2S(fig.px, fig.py);
  const sc = scaleAt(fig.py) * view.s;
  if (meta.kind !== 'resident') { drawAnimal(fig, f, x, y, sc); return; }
  const hopY = (fig.hop || 0) * sc; const groundY = y; y -= hopY;   // airborne over a low fence; shadow stays on the ground

  const col = meta.color || '#c9cad3';
  const hs = hashId(e.id);
  const k = e.child ? 0.74 : 1.0;
  const U = sc * k * PSCALE;
  const hd = fig.hd != null ? fig.hd : (e.h || 0);
  const faceS = easeFace(e.id, Math.cos(hd) >= 0 ? 1 : -1) >= 0 ? 1 : -1;   // eased turn, not an instant mirror
  const ph = (hs % 628) / 100;
  const tr = idTraits(e.id);                 // this resident's individual way of moving
  // behaviour → motion parameters (all straight from the deterministic stream)
  const spd = e.spd || 0;
  const sig = e.sig || 'none';               // a memorable physical signature (limp / cane / …)
  const vigor = clamp(((e.energy != null ? e.energy : 0.8) - 0.4) / 0.6, 0, 1);   // tired … lively
  const cheer = clamp(e.mood != null ? e.mood : 0.6, 0, 1);                        // low … bright mood
  const openness = clamp(((e.soc != null ? e.soc : 0) + 1) / 4, 0, 1);            // introvert … extrovert
  const pose = e.pose || 'stand';
  const sit = pose === 'sit' || pose === 'lie';
  const working = pose === 'work', talking = pose === 'talk', playing = pose === 'play', dancing = pose === 'dance';
  const dancePh = dancing ? state.t * 3.6 + ph : 0;
  const worn = e.worn || [];
  const gest = e.gest || 'none';
  const ink = 'rgba(30,22,16,.6)';
  const role = roleOf(e);

  const moving = fig.walking != null ? fig.walking : (e.moving && (e.spd || 0) > 0.05);
  const gaitRate = (3.0 + spd * 2.4 + vigor * 0.7) * tr.gait * (sig === 'skip' ? 1.5 : 1);      // hurry & vigour quicken the step; a child's skip is quicker still
  const wph = moving ? Math.sin(state.t * gaitRate + ph) : 0;
  const strideAmp = (0.55 + spd * 1.0 + vigor * 0.25) * tr.stride * (sig === 'cane' ? 0.6 : sig === 'load' ? 0.8 : 1);  // stride length (a cane / a load shortens it)
  const workPhase = working ? Math.sin(state.t * 2.6 + ph) : 0;                    // rhythmic task
  const playHop = playing ? Math.abs(Math.sin(state.t * 3.2 + ph)) : 0;           // child's hop

  // proportions — broader shoulders than hips
  const legH = (sit ? 2.4 : 5.4) * U, torsoH = (sit ? 6 : 8) * U;
  const shoulderW = 7 * U, hipW = 5.4 * U, headR = 3.0 * U * (e.child ? 1.2 : 1);
  const slump = (((1 - vigor) * 0.6 + (1 - cheer) * 0.35) - tr.upright * 0.5 + (sig === 'cane' ? 1.4 : sig === 'load' ? 1.1 : 0)) * U;   // tired/low-mood shoulders drop; a cane or a heavy load bends the back into a stoop
  const idle = moving ? 0 : Math.sin(state.t * (1.1 + vigor * 0.9) * tr.idle + ph);
  const sway = moving ? 0 : Math.sin(state.t * 0.9 + (hs % 314) / 100) * (0.32 + openness * 0.4) * U;
  const bob = moving ? Math.abs(wph) * (0.55 + vigor * 0.5) * U * tr.bob * (sig === 'skip' ? 1.9 : sig === 'load' ? 0.5 : 1)
    : (playing ? playHop * 1.7 * U : dancing ? (0.4 + Math.abs(Math.sin(dancePh))) * 1.2 * U : idle * 0.22 * U);
  const lean = working ? faceS * 0.9 * U : 0;                                     // stoop over the work
  const danceSway = dancing ? Math.sin(dancePh * 0.5) * 1.7 * U : 0;              // hips side to side
  // a limp hitches the body down each time the stiff leg takes the weight
  const limpHitch = (sig === 'limp' && moving) ? Math.max(0, Math.sin(state.t * gaitRate + ph)) * 0.9 * U : 0;
  const hipY = y - legH + bob + limpHitch, shoulderY = hipY - torsoH + slump;
  const nod = gest === 'nod' ? Math.abs(Math.sin(state.t * 3.2 + ph)) * 0.7 * U : 0;      // agreeing
  const glance = gest === 'glance' ? Math.sin(state.t * 1.3 + ph) * 0.9 * U : 0;          // looking about
  const headDroop = (1 - cheer) * 0.5 * U;                                        // low mood: head dips
  const headCY = shoulderY - headR * 1.05 + idle * 0.15 * U + nod + headDroop;
  x += sway + lean + danceSway;
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';

  // ground shadow — stays on the ground and shrinks while the figure is airborne
  { const sh = 1 - Math.min(1, hopY / (7 * U)) * 0.5;
    ctx.fillStyle = `rgba(0,0,0,${0.2 * sh})`;
    ctx.beginPath(); ctx.ellipse(x, groundY, 7 * U * sh, 2.6 * U * sh, 0, 0, 7); ctx.fill(); }

  // legs — opposite swing; role-tinted trousers
  const trouser = role === 'keeper' ? '#3f4a37' : role === 'clerk' ? '#33384a' : shade(col, 0.6);
  ctx.strokeStyle = trouser; ctx.lineWidth = 2.3 * U;
  const hipL = x - hipW * 0.28, hipR = x + hipW * 0.28;
  if (sit) {
    ctx.beginPath(); ctx.moveTo(x, hipY); ctx.lineTo(x + faceS * 3.6 * U, hipY + 0.4 * U); ctx.stroke();
  } else {
    const st = moving ? wph * strideAmp * 2.7 * U : (playing ? Math.sin(state.t * 3.2 + ph) * 1.5 * U : dancing ? Math.sin(dancePh) * 1.7 * U : 0.8 * U);
    const stiff = sig === 'limp' ? 0.4 : 1;   // the limped leg barely swings — a stiff, dragged step
    ctx.beginPath(); ctx.moveTo(hipL, hipY); ctx.lineTo(hipL + st * faceS, y + bob); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(hipR, hipY); ctx.lineTo(hipR - st * faceS * stiff, y + bob); ctx.stroke();
  }
  // a cane: a stick from the forward hand down to the ground ahead, taking weight
  if (sig === 'cane' && !sit) {
    ctx.strokeStyle = '#6b5330'; ctx.lineWidth = 1.4 * U; ctx.lineCap = 'round';
    const handY = shoulderY + 2.4 * U;
    ctx.beginPath(); ctx.moveTo(x + faceS * 2.4 * U, handY); ctx.lineTo(x + faceS * 4.4 * U, y); ctx.stroke();
  }

  // torso — clay-shaded trapezoid, colour = identity
  const g = ctx.createLinearGradient(0, shoulderY, 0, hipY);
  g.addColorStop(0, shade(col, 1.14)); g.addColorStop(1, shade(col, 0.84));
  ctx.fillStyle = g;
  const torsoPath = () => {
    ctx.beginPath();
    ctx.moveTo(x - shoulderW / 2 + U, shoulderY);
    ctx.lineTo(x + shoulderW / 2 - U, shoulderY);
    ctx.quadraticCurveTo(x + shoulderW / 2, shoulderY, x + shoulderW / 2 - 0.4 * U, shoulderY + 1.6 * U);
    ctx.lineTo(x + hipW / 2, hipY);
    ctx.lineTo(x - hipW / 2, hipY);
    ctx.lineTo(x - shoulderW / 2 + 0.4 * U, shoulderY + 1.6 * U);
    ctx.quadraticCurveTo(x - shoulderW / 2, shoulderY, x - shoulderW / 2 + U, shoulderY);
    ctx.closePath();
  };
  torsoPath(); ctx.fill();
  ctx.lineWidth = Math.max(0.5, 0.7 * U); ctx.strokeStyle = ink; ctx.stroke();

  // work jacket (clerk) / coat overlay (worn) darkens the torso
  if (role === 'clerk') { ctx.fillStyle = 'rgba(40,46,66,.55)'; torsoPath(); ctx.fill(); }
  if (worn.includes('coat')) { ctx.fillStyle = 'rgba(60,50,40,.5)'; torsoPath(); ctx.fill(); }

  // apron (baker / grocer / shop) — lighter block over the lower front, with straps
  if (role === 'baker' || role === 'grocer' || role === 'shop') {
    const apron = role === 'baker' ? 'rgba(246,243,236,.94)' : role === 'grocer' ? 'rgba(122,96,60,.92)' : 'rgba(198,204,214,.92)';
    const aTop = shoulderY + torsoH * 0.4;
    ctx.fillStyle = apron; roundRect(x - hipW * 0.42, aTop, hipW * 0.84, hipY - aTop + 0.5 * U, 1.1 * U); ctx.fill();
    ctx.strokeStyle = apron; ctx.lineWidth = 0.9 * U;
    ctx.beginPath(); ctx.moveTo(x - hipW * 0.26, aTop); ctx.lineTo(x - hipW * 0.12, shoulderY + 1.4 * U);
    ctx.moveTo(x + hipW * 0.26, aTop); ctx.lineTo(x + hipW * 0.12, shoulderY + 1.4 * U); ctx.stroke();
  }

  // carried signatures — a porter's load, a busker's instrument, a florist's blooms
  if (sig === 'load') {                                     // a crate/sack on the back
    const bw = 6.2 * U, bh = 5.4 * U, bx = x - faceS * 2.6 * U - bw / 2, by = shoulderY - 1.4 * U;
    ctx.fillStyle = '#8a6a44'; ctx.strokeStyle = ink; ctx.lineWidth = 0.6 * U;
    roundRect(bx, by, bw, bh, 1 * U); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = 'rgba(40,30,20,.5)'; ctx.lineWidth = 0.5 * U;                 // strap
    ctx.beginPath(); ctx.moveTo(x - faceS * 0.6 * U, shoulderY); ctx.lineTo(bx + bw * 0.5, by + 1 * U); ctx.stroke();
  }
  if (sig === 'instrument') {                               // a slim case slung at the trailing side
    ctx.save(); ctx.translate(x - faceS * 3.3 * U, shoulderY + 3.2 * U); ctx.rotate(faceS * 0.5);
    ctx.fillStyle = '#8a5a2a'; ctx.strokeStyle = ink; ctx.lineWidth = 0.5 * U;
    ctx.beginPath(); ctx.ellipse(0, 0, 1.7 * U, 4.4 * U, 0, 0, 7); ctx.fill(); ctx.stroke();
    ctx.restore();
  }
  if (sig === 'flowers') {                                  // an armful of blooms at the chest
    const cx2 = x + faceS * 1.4 * U, cy2 = shoulderY + 3.4 * U;
    ctx.strokeStyle = '#3f6b3a'; ctx.lineWidth = 0.8 * U;
    ctx.beginPath(); ctx.moveTo(cx2, cy2 + 2 * U); ctx.lineTo(cx2, cy2 - 1.4 * U); ctx.stroke();
    for (const [dx, dy, c] of [[-1.2, -1.4, '#e2637a'], [1.2, -1.6, '#f2c14e'], [0, -2.6, '#d98cc0'], [-1.7, -0.1, '#e88a3a']])
      { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(cx2 + dx * U, cy2 + dy * U, 1.15 * U, 0, 7); ctx.fill(); }
  }

  // arms — behaviour-driven: work at a surface, play arms-up, or swing/gesture
  ctx.strokeStyle = shade(col, 0.98); ctx.lineWidth = 2.0 * U;
  const armY = shoulderY + 1.7 * U;
  const shL = x - shoulderW * 0.42, shR = x + shoulderW * 0.42;
  if (working) {
    // both hands out front at the counter/task, moving with the rhythm
    const wx = faceS * (2.6 + Math.abs(workPhase) * 0.7) * U, wy = armY + (2.4 + workPhase * 0.9) * U;
    ctx.beginPath(); ctx.moveTo(shL, armY); ctx.lineTo(x + wx - 0.7 * U, wy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(shR, armY); ctx.lineTo(x + wx + 0.7 * U, wy); ctx.stroke();
  } else if (playing) {
    const pw = Math.sin(state.t * 3.2 + ph) * 1.5 * U;                            // arms up, waving with the hop
    ctx.beginPath(); ctx.moveTo(shL, armY); ctx.lineTo(shL - 1.3 * U + pw, armY - 2.7 * U); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(shR, armY); ctx.lineTo(shR + 1.3 * U - pw, armY - 2.7 * U); ctx.stroke();
  } else if (dancing) {
    const d1 = Math.sin(dancePh) * 1.7 * U, d2 = Math.sin(dancePh + Math.PI) * 1.7 * U;   // arms up, alternating
    ctx.beginPath(); ctx.moveTo(shL, armY); ctx.lineTo(shL - 1.4 * U + d1, armY - 2.9 * U - Math.abs(d1) * 0.6); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(shR, armY); ctx.lineTo(shR + 1.4 * U + d2, armY - 2.9 * U - Math.abs(d2) * 0.6); ctx.stroke();
  } else {
    const aSwing = moving ? wph * strideAmp * 1.8 * U * tr.swing : 0;
    const rest = moving ? 0 : (0.6 + openness * 0.9) * U;                          // open posture = arms held out
    ctx.beginPath(); ctx.moveTo(shL, armY); ctx.lineTo(shL - aSwing * faceS - rest, armY + 3.4 * U); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(shR, armY);
    if (gest === 'gesture' || gest === 'laugh' || (talking && gest !== 'none')) {
      const gm = Math.sin(state.t * 4 + ph) * 0.6;                                // hand moves while making a point
      ctx.lineTo(shR + faceS * (1.4 + openness) * U, armY - (2.5 + gm) * U);
    } else ctx.lineTo(shR + aSwing * faceS + rest, armY + 3.4 * U);
    ctx.stroke();
  }

  // scarf
  if (worn.includes('club_scarf') || worn.includes('scarf')) {
    ctx.strokeStyle = '#c9463d'; ctx.lineWidth = 1.7 * U;
    ctx.beginPath(); ctx.moveTo(x - 2 * U, shoulderY + 0.6 * U); ctx.lineTo(x + 2 * U, shoulderY + 0.6 * U); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + 0.8 * U, shoulderY + 0.6 * U); ctx.lineTo(x + 1.5 * U * faceS, shoulderY + 3 * U); ctx.stroke();
  }

  // head + hair + a hint of a face on the facing side (glance shifts it side to side)
  const hcx = x + faceS * 0.4 * U + glance;
  ctx.fillStyle = skinOf(e.id);
  ctx.beginPath(); ctx.arc(hcx, headCY, headR, 0, 7); ctx.fill();
  ctx.lineWidth = Math.max(0.5, 0.7 * U); ctx.strokeStyle = ink; ctx.stroke();
  ctx.fillStyle = hairOf(e.id);
  ctx.beginPath(); ctx.arc(hcx, headCY - headR * 0.24, headR * 0.96, Math.PI * 1.02, Math.PI * 2.08); ctx.fill();
  // face: a soft lit cheek + a brow dot, toward the direction faced
  ctx.fillStyle = 'rgba(255,252,245,.12)';
  ctx.beginPath(); ctx.ellipse(hcx + faceS * headR * 0.34, headCY + headR * 0.12, headR * 0.5, headR * 0.62, 0, 0, 7); ctx.fill();
  ctx.fillStyle = 'rgba(40,28,20,.5)';
  ctx.beginPath(); ctx.arc(hcx + faceS * headR * 0.5, headCY - headR * 0.02, Math.max(0.5, 0.4 * U), 0, 7); ctx.fill();

  // role headwear
  if (role === 'baker') {
    ctx.fillStyle = 'rgba(248,246,240,.96)';
    ctx.beginPath(); ctx.ellipse(hcx, headCY - headR * 0.7, headR * 1.05, headR * 0.85, 0, Math.PI, 0); ctx.fill();
    ctx.beginPath(); ctx.ellipse(hcx, headCY - headR * 0.55, headR * 1.15, headR * 0.3, 0, 0, 7); ctx.fill();
  } else if (role === 'keeper') {
    ctx.fillStyle = '#2f3a2a';
    ctx.beginPath(); ctx.ellipse(hcx, headCY - headR * 0.5, headR * 1.15, headR * 0.55, 0, Math.PI, 0); ctx.fill();
    ctx.beginPath(); ctx.ellipse(hcx + faceS * headR * 0.85, headCY - headR * 0.45, headR * 0.7, headR * 0.28, 0, 0, 7); ctx.fill();
  }
  // worn hats
  if (worn.includes('sunhat')) {
    ctx.fillStyle = '#e6d49a';
    ctx.beginPath(); ctx.ellipse(hcx, headCY - headR * 0.45, headR * 1.6, headR * 0.55, 0, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.ellipse(hcx, headCY - headR * 0.8, headR * 0.75, headR * 0.55, 0, Math.PI, 0); ctx.fill();
  }
  // out in the rain: raise an umbrella (from the sim's `worn`, or simply because it's wet outdoors)
  const rainingOut = !!(f && f.weather && f.weather.wet) && !sit;
  if (worn.includes('umbrella') || rainingOut) {
    ctx.fillStyle = 'rgba(45,65,95,.92)';
    ctx.beginPath(); ctx.ellipse(x, headCY - headR * 2.6, 6.5 * U, 2.6 * U, 0, Math.PI, 0); ctx.fill();
    ctx.strokeStyle = 'rgba(45,65,95,.92)'; ctx.lineWidth = 0.8 * U;
    ctx.beginPath(); ctx.moveTo(x, headCY - headR * 2.6); ctx.lineTo(x, headCY + headR * 0.5); ctx.stroke();
  }
  if (gest === 'laugh') { ctx.fillStyle = 'rgba(255,240,180,.95)'; ctx.beginPath(); ctx.arc(x + faceS * 3 * U, headCY - 2 * U, 1.3 * U, 0, 7); ctx.fill(); }

  if (state.showNames) {
    ctx.font = `${Math.max(9, 9 * U)}px system-ui`; ctx.fillStyle = 'rgba(255,255,255,.92)';
    ctx.textAlign = 'center'; ctx.fillText(meta.name, x, headCY - headR - 4 * U); ctx.textAlign = 'left';
  }
}

function drawAnimal(fig, f, x, y, sc) {
  const { e, meta } = fig; const col = meta.color || '#b98a5a'; const k = sc * 1.25; const kind = meta.kind;
  const hopY = (fig.hop || 0) * sc; const groundY = y; y -= hopY;   // airborne over a low fence; shadow stays down
  const trot = fig.walking ? state.t * 5.5 + (hashId(e.id) % 628) / 100 : null;   // leg-swing phase while walking
  const legSwing = (i) => trot != null ? Math.sin(trot + i * 1.7) * 1.7 * k : 0;
  const faceS = Math.cos(fig.hd || 0) >= 0 ? 1 : -1;   // which way the animal faces (head toward travel)
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  { const sh = 1 - Math.min(1, hopY / (6 * k)) * 0.5;
    ctx.fillStyle = `rgba(0,0,0,${0.16 * sh})`; ctx.beginPath(); ctx.ellipse(x, groundY, 5 * k * sh, 1.8 * k * sh, 0, 0, 7); ctx.fill(); }

  if (kind === 'cat') {
    ctx.strokeStyle = shade(col, 0.75); ctx.lineWidth = 1.1 * k;
    [-2, -0.5, 0.5, 2].forEach((dx, i) => { ctx.beginPath(); ctx.moveTo(x + dx * k, y - 2.4 * k); ctx.lineTo(x + dx * k + legSwing(i), y); ctx.stroke(); });
    ctx.fillStyle = col; roundRect(x - 3.2 * k, y - 5 * k, 6.4 * k, 2.9 * k, 1.5 * k); ctx.fill();
    ctx.beginPath(); ctx.arc(x + 3.4 * k, y - 5.4 * k, 1.7 * k, 0, 7); ctx.fill();
    // ears
    ctx.beginPath(); ctx.moveTo(x + 2.7 * k, y - 6.6 * k); ctx.lineTo(x + 3.1 * k, y - 7.6 * k); ctx.lineTo(x + 3.7 * k, y - 6.7 * k); ctx.fill();
    ctx.beginPath(); ctx.moveTo(x + 3.6 * k, y - 6.7 * k); ctx.lineTo(x + 4.1 * k, y - 7.6 * k); ctx.lineTo(x + 4.5 * k, y - 6.5 * k); ctx.fill();
    // upright curling tail
    ctx.strokeStyle = col; ctx.lineWidth = 1.3 * k;
    ctx.beginPath(); ctx.moveTo(x - 3.2 * k, y - 4 * k); ctx.quadraticCurveTo(x - 5.6 * k, y - 5 * k, x - 4.8 * k, y - 7.4 * k); ctx.stroke();
    return;
  }
  if (kind === 'dog' || kind === 'fox') {
    const fox = kind === 'fox', fs = faceS, old = e.id === 'the_old_dog';
    const dark = shade(col, 0.72), belly = shade(col, fox ? 1.35 : 1.18);
    const wag = fig.walking ? Math.sin(state.t * 7) * 0.9 * k : Math.sin(state.t * 1.6) * 0.4 * k;
    // far legs (behind the body) darker, near legs lighter — a little depth
    const leg = (dx, i, cc) => { const bx = x + dx * k * fs, sw = legSwing(i); ctx.strokeStyle = cc; ctx.lineWidth = 1.5 * k;
      ctx.beginPath(); ctx.moveTo(bx, y - 3.3 * k); ctx.quadraticCurveTo(bx + sw * 0.5, y - 1.5 * k, bx + sw, y); ctx.stroke(); };
    leg(-2.4, 1, dark); leg(2.7, 3, dark);                    // far pair
    // tail (bushy for the fox), gently wagging
    ctx.strokeStyle = fox ? col : dark; ctx.lineWidth = (fox ? 3.0 : 1.7) * k;
    const tx = x - 4.2 * k * fs, ty = y - 4.9 * k;
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.quadraticCurveTo(tx - 3.0 * k * fs, ty - (fox ? 1.6 : 3.0) * k + wag, tx - 3.4 * k * fs, ty - (fox ? 3.4 : 4.4) * k + wag); ctx.stroke();
    if (fox) { ctx.strokeStyle = 'rgba(245,244,240,.92)'; ctx.lineWidth = 1.7 * k; ctx.beginPath(); ctx.moveTo(tx - 3.1 * k * fs, ty - 2.6 * k + wag); ctx.lineTo(tx - 3.5 * k * fs, ty - 3.6 * k + wag); ctx.stroke(); }
    // body — a rounded torso with a chest bump toward the head; old dog dips at the back
    ctx.fillStyle = col;
    ctx.beginPath(); ctx.ellipse(x - 0.4 * k * fs, y - (old ? 4.6 : 5.0) * k, 4.7 * k, 2.9 * k, old ? 0.05 * fs : -0.05 * fs, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x + 3.1 * k * fs, y - 5.4 * k, 2.5 * k, 2.7 * k, 0, 0, 7); ctx.fill();   // shoulder/chest
    // belly highlight
    ctx.fillStyle = belly; ctx.globalAlpha = 0.55; ctx.beginPath(); ctx.ellipse(x + 0.4 * k * fs, y - 3.5 * k, 3.8 * k, 1.3 * k, 0, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
    // near legs on top
    leg(-1.0, 0, col); leg(1.3, 2, col);
    // head
    const hx = x + 4.7 * k * fs, hy = y - 6.6 * k;
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(hx, hy, 2.3 * k, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.ellipse(hx + 1.9 * k * fs, hy + 0.7 * k, 1.6 * k, 1.05 * k, 0.1 * fs, 0, 7); ctx.fill();   // snout
    if (old) { ctx.fillStyle = 'rgba(214,209,201,.65)'; ctx.beginPath(); ctx.ellipse(hx + 2.0 * k * fs, hy + 0.8 * k, 1.7 * k, 1.0 * k, 0.1 * fs, 0, 7); ctx.fill(); }   // grey muzzle
    // ears
    if (fox) { ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(hx - 0.5 * k * fs, hy - 1.4 * k); ctx.lineTo(hx - 0.1 * k * fs, hy - 3.7 * k); ctx.lineTo(hx + 1.5 * k * fs, hy - 1.7 * k); ctx.closePath(); ctx.fill();
      ctx.fillStyle = dark; ctx.beginPath(); ctx.moveTo(hx + 0.3 * k * fs, hy - 1.7 * k); ctx.lineTo(hx + 0.6 * k * fs, hy - 3.2 * k); ctx.lineTo(hx + 1.4 * k * fs, hy - 1.8 * k); ctx.closePath(); ctx.fill(); }
    else { ctx.fillStyle = dark; ctx.beginPath(); ctx.ellipse(hx - 1.1 * k * fs, hy - 0.1 * k, 1.05 * k, 2.1 * k, -0.35 * fs, 0, 7); ctx.fill(); }   // floppy ear
    // nose + eye
    ctx.fillStyle = '#2a2320'; ctx.beginPath(); ctx.arc(hx + 3.2 * k * fs, hy + 0.5 * k, 0.62 * k, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.arc(hx + 0.9 * k * fs, hy - 0.5 * k, 0.5 * k, 0, 7); ctx.fill();
    return;
  } else if (kind === 'heron') {
    ctx.strokeStyle = '#b9c0c5'; ctx.lineWidth = 1.1 * k;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - 6 * k); ctx.stroke();
    ctx.fillStyle = '#e2e6e9'; ctx.beginPath(); ctx.ellipse(x, y - 8.2 * k, 2.2 * k, 3.3 * k, 0, 0, 7); ctx.fill();
    ctx.strokeStyle = '#e2e6e9'; ctx.lineWidth = 1.0 * k; ctx.beginPath(); ctx.moveTo(x, y - 10.5 * k); ctx.lineTo(x + 1.6 * k, y - 13.5 * k); ctx.stroke();
    ctx.strokeStyle = '#e0b040'; ctx.beginPath(); ctx.moveTo(x + 1.6 * k, y - 13.5 * k); ctx.lineTo(x + 4.2 * k, y - 13 * k); ctx.stroke();
  } else if (kind === 'hedgehog') {
    ctx.fillStyle = '#7a5a3a'; ctx.beginPath(); ctx.ellipse(x, y - 2 * k, 3.6 * k, 2.4 * k, 0, 0, 7); ctx.fill();
    ctx.strokeStyle = '#4f381f'; ctx.lineWidth = 0.8 * k;
    for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.moveTo(x + i * 1.2 * k, y - 3.4 * k); ctx.lineTo(x + i * 1.2 * k - 0.6 * k, y - 5.4 * k); ctx.stroke(); }
  } else { // birds / owl
    if (e.moving) { ctx.strokeStyle = col; ctx.lineWidth = 1.1 * k; ctx.beginPath(); ctx.moveTo(x - 3 * k, y - 3.5 * k); ctx.lineTo(x, y - 2 * k); ctx.lineTo(x + 3 * k, y - 3.5 * k); ctx.stroke(); }
    else { ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(x, y - 2 * k, 2.3 * k, 1.6 * k, 0, 0, 7); ctx.fill(); }
  }
}

function roundRect(x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

// 0 = full day, 1 = deep night, ramped through dawn/dusk (drives sky darkness).
function nightFactor(hour, minute) {
  const h = hour + minute / 60;
  if (h >= 7 && h < 17) return 0;
  if (h >= 5 && h < 7) return clamp(1 - (h - 5) / 2, 0, 1);     // dawn fade out
  if (h >= 17 && h < 20.5) return clamp((h - 17) / 3.5, 0, 1);  // dusk fade in
  return 1;                                                     // night
}

// Street/window lights on their own switch: ON at 19:20, fully OUT by ~5:05, with a
// short ramp so they fade rather than snap. The morning fade is pulled earlier (and
// eased) so nothing lingers lit once it reads as morning. Independent of sky darkness.
function lampsOn(hour, minute) {
  const h = hour + minute / 60;
  if (h >= 19 + 20 / 60 && h < 19 + 40 / 60) return (h - (19 + 20 / 60)) / (20 / 60); // ramp up 19:20→19:40
  if (h >= 19 + 40 / 60 || h < 4 + 40 / 60) return 1;                                  // full on overnight until 4:40
  if (h >= 4 + 40 / 60 && h < 5 + 5 / 60) { const u = (h - (4 + 40 / 60)) / (25 / 60); return (1 - u) * (1 - u); } // ease out 4:40→5:05
  return 0;                                                                             // day, off
}

// Stadium floodlights: on for one evening in the loop (a matchday preview) — day 1,
// 19:00→21:00 with a short ramp each end. When the sim emits real matchdays this hooks
// to that flag instead of a fixed evening. Returns 0..1.
function floodOn(f) {
  if (f.day !== 1) return 0;
  const h = f.hour + f.minute / 60, on = 19, off = 21, ramp = 1 / 6;   // 10-min ramps
  if (h < on || h >= off) return 0;
  if (h < on + ramp) return (h - on) / ramp;
  if (h > off - ramp) return (off - h) / ramp;
  return 1;
}
// The physical masts: a tall pole with a lamp panel angled toward the pitch. The bright
// pitch wash itself comes from applyLightMap; this is the fixture + its glowing head.
function drawFloodPosts(on) {
  const floods = state.floods, aim = state.floodAim; if (!floods) return;
  for (const F of floods) {
    const [x, y] = P2S(F.x, F.y), sc = scaleAt(F.y) * view.s;
    const mastH = 52 * sc, hx = x, hy = y - mastH;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'rgba(38,40,46,0.9)'; ctx.lineWidth = Math.max(1, 1.8 * sc);
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(hx, hy); ctx.stroke();          // mast
    // lamp panel at the top, tilted a touch toward the pitch centre
    const dir = Math.atan2(aim.y - F.y, aim.x - F.x);
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(Math.sin(dir) * 0.25);
    const pw = 9 * sc, ph = 4.5 * sc;
    ctx.fillStyle = on > 0.1 ? `rgba(236,244,255,${0.55 + 0.45 * on})` : 'rgba(58,62,68,0.92)';
    ctx.strokeStyle = 'rgba(26,28,32,0.85)'; ctx.lineWidth = Math.max(0.5, 0.6 * sc);
    roundRect(-pw / 2, -ph, pw, ph, 1 * sc); ctx.fill(); ctx.stroke();
    if (on > 0.1) {                                                              // individual bulbs glowing
      ctx.fillStyle = `rgba(255,255,246,${on})`;
      for (let i = 0; i < 4; i++) for (let j = 0; j < 2; j++) {
        ctx.beginPath(); ctx.arc(-pw / 2 + (i + 0.5) * pw / 4, -ph + (j + 0.5) * ph / 2, 0.7 * sc, 0, 7); ctx.fill();
      }
    }
    ctx.restore();
  }
}
// Visible beam shafts + a cool glow spilling from each mast onto the pitch (additive,
// drawn over the night light map so the pitch reads brightly floodlit).
function drawFloodBeams(on) {
  const floods = state.floods, aim = state.floodAim; if (!floods || on <= 0) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const [ax, ay] = P2S(aim.x, aim.y);
  for (const F of floods) {
    const sc = scaleAt(F.y) * view.s, [x, y] = P2S(F.x, F.y), hy = y - 52 * sc;
    const dx = ax - x, dy = ay - hy, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
    const spread = 26 * sc;
    const g = ctx.createLinearGradient(x, hy, ax, ay);
    g.addColorStop(0, `rgba(220,236,255,${0.16 * on})`); g.addColorStop(1, 'rgba(210,228,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(x, hy); ctx.lineTo(ax + nx * spread, ay + ny * spread); ctx.lineTo(ax - nx * spread, ay - ny * spread); ctx.closePath(); ctx.fill();
    ctx.fillStyle = `rgba(255,255,250,${0.9 * on})`;                              // bright head flare
    ctx.beginPath(); ctx.arc(x, hy, 1.8 * sc, 0, 7); ctx.fill();
  }
  ctx.restore();
}

// Game-night crowd fill: on the match evening (the floodlight night) the stands fill
// from ~18:25, are full through the game, and clear after. Returns 0..1 (how full).
function gameCrowdFill(f) {
  if (f.day !== 1) return 0;                          // the floodlight/match night
  const h = f.hour + f.minute / 60;
  const arrive = 18 + 25 / 60, full = 19 + 40 / 60, gameEnd = 21, clear = 21 + 40 / 60;
  if (h < arrive || h >= clear) return 0;
  if (h < full) return (h - arrive) / (full - arrive);   // filling from the north gate
  if (h < gameEnd) return 1;                             // packed for the match
  return 1 - (h - gameEnd) / (clear - gameEnd);          // drifting out after
}
// Draw the anonymous supporters in the stands — the same little clay build as the
// residents (torso + head), just faceless and in club green or white. The number varies
// per match (seeded 40–180); they fill nearest the north gate first.
const SPEC_SKIN = ['#e3b78e', '#cda079', '#b98c66', '#9a734f', '#7f5c3d'];
function drawStadiumCrowd(f) {
  const fill = gameCrowdFill(f); if (fill <= 0 || !state.stadiumSeats) return;
  const target = 40 + (hashId('gamecrowd|' + f.day) % 141);   // 40..180 this match
  const n = Math.min(Math.floor(target * fill), state.stadiumSeats.length);
  const ink = 'rgba(30,22,16,.5)';
  ctx.save(); ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const s = state.stadiumSeats[i], hgt = hashId('seat|' + i);
    const jx = ((hgt % 7) - 3) * 0.5, jy = (((hgt >> 3) % 5) - 2) * 0.4;   // break the grid a touch
    const [x, y] = P2S(s.x + jx, s.y + jy), sc = scaleAt(s.y) * view.s, U = sc * 0.7;
    const col = (hgt % 2) === 0 ? '#2e8442' : '#e9ede7';                    // club green / white
    const hipY = y, shoulderY = y - 4 * U, headCY = shoulderY - 2.2 * U;
    // torso — clay trapezoid, shaded like a resident
    const g = ctx.createLinearGradient(0, shoulderY, 0, hipY);
    g.addColorStop(0, shade(col, 1.12)); g.addColorStop(1, shade(col, 0.82));
    ctx.fillStyle = g;
    const sw = 3.4 * U, hw = 2.7 * U;
    ctx.beginPath();
    ctx.moveTo(x - sw / 2, shoulderY); ctx.lineTo(x + sw / 2, shoulderY);
    ctx.lineTo(x + hw / 2, hipY); ctx.lineTo(x - hw / 2, hipY); ctx.closePath(); ctx.fill();
    ctx.lineWidth = Math.max(0.4, 0.5 * U); ctx.strokeStyle = ink; ctx.stroke();
    // head
    ctx.fillStyle = SPEC_SKIN[hgt % SPEC_SKIN.length];
    ctx.beginPath(); ctx.arc(x, headCY, 1.6 * U, 0, 7); ctx.fill();
    ctx.lineWidth = Math.max(0.3, 0.4 * U); ctx.strokeStyle = ink; ctx.stroke();
  }
  ctx.restore();
}

// Monday-night town festival: the square is lit warm and festive for the gathering
// (19:00→22:00), matched to the sim's festival window. Returns 0..1.
function festivalOn(f) {
  if (f.weekday !== 'Mon') return 0;
  const h = f.hour + f.minute / 60, on = 19, off = 22, ramp = 1 / 6;
  if (h < on || h >= off) return 0;
  if (h < on + ramp) return (h - on) / ramp;
  if (h > off - ramp) return (off - h) / ramp;
  return 1;
}
// A festive canopy over the square: strings of little coloured lanterns strung above the
// crowd, drawn over the lit scene (additive), plus a few musical notes drifting up.
function drawFestival(on, f) {
  if (on <= 0) return;
  const sq = state.map.places && state.map.places.loc_main_square; if (!sq) return;
  const [cx, cy] = P2S(sq.x, sq.y), sc = scaleAt(sq.y) * view.s, T = state.anim || 0;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const cols = ['255,120,90', '255,210,110', '120,200,255', '150,255,150', '255,150,220'];
  // three strung lines of bulbs arcing over the square
  for (let s = 0; s < 3; s++) {
    const span = (70 + s * 18) * sc, x0 = cx - span, x1 = cx + span, yTop = cy - (34 + s * 8) * sc, sag = (10 + s * 3) * sc;
    const N = 10 + s * 2;
    for (let i = 0; i <= N; i++) {
      const u = i / N, bx = x0 + (x1 - x0) * u, by = yTop + Math.sin(u * Math.PI) * -sag + Math.sin(u * Math.PI) * sag * 2;
      const twinkle = 0.55 + 0.45 * Math.sin(T * 2.5 + i * 1.3 + s);
      const c = cols[(i + s) % cols.length];
      ctx.fillStyle = `rgba(${c},${on * twinkle * 0.9})`;
      ctx.beginPath(); ctx.arc(bx, by, 1.5 * sc, 0, 7); ctx.fill();
    }
  }
  // a few musical notes drifting up over the crowd
  ctx.strokeStyle = `rgba(255,246,220,${on * 0.7})`; ctx.fillStyle = `rgba(255,246,220,${on * 0.7})`;
  ctx.lineWidth = Math.max(0.6, 0.8 * sc);
  for (let k = 0; k < 5; k++) {
    const hx = ((k + 1) * 2654435761) >>> 0;
    const rise = ((hx % 1000) / 1000 + T * 0.06) % 1;
    const nx = cx + ((hx >> 10) % 160 - 80) * sc * 0.9, ny = cy - 20 * sc - rise * 46 * sc;
    const a = on * (1 - rise) * 0.8;
    ctx.globalAlpha = a;
    ctx.beginPath(); ctx.arc(nx, ny, 1.2 * sc, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.moveTo(nx + 1.1 * sc, ny); ctx.lineTo(nx + 1.1 * sc, ny - 4 * sc); ctx.stroke();
    ctx.globalAlpha = 1;
  }
  ctx.restore();
}

// A resident whose feet fall inside an obscured region (a passage the camera
// can't see past, marked in the plate-mapper) is hidden.
function obscured(px, py) {
  const zs = state.obscured;
  if (!zs || !zs.length) return false;
  for (const poly of zs) if (pointInPoly(px, py, poly)) return true;
  return false;
}
// Soft occlusion: instead of a hard on/off at the obscured-zone edge (which makes
// walkers blink and reads as jumpy, fragmented motion), return an opacity that fades
// across a ~20px band around the edge. A resident stays fully visible on the open
// street, dissolves smoothly as it steps behind a building, and fades back in on the
// far side — natural depth, no flicker. 1 = fully visible, 0 = hidden.
const OCC_FADE = 12;
const OCC_EDGE = 2.5;   // px past the occluder edge over which a figure vanishes — a hard hide, just anti-aliased
function occlusionAlpha(px, py) {
  const zs = state.obscured;
  if (!zs || !zs.length) return 1;
  let inside = false, mind = Infinity;
  for (const poly of zs) {
    if (pointInPoly(px, py, poly)) inside = true;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const ax = poly[j][0], ay = poly[j][1], bx = poly[i][0], by = poly[i][1];
      const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1;
      let t = ((px - ax) * dx + (py - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
      const d = Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
      if (d < mind) mind = d;
    }
  }
  // An object passing behind a wall should DISAPPEAR behind it, not dissolve: full
  // opacity out in the open, then hidden once its feet cross the edge (a ~1px lip
  // only to avoid a jagged pop). No long approach-fade.
  if (!inside) return 1;
  return clamp(1 - mind / OCC_EDGE, 0, 1);
}
// A walker whose feet fall behind the stands is hidden by the terracing (soft edge).
// Outside the stands: fully visible. Seated fans are settled (not walkers) so this
// never touches them.
function standsAlpha(px, py) {
  const zs = state.stands;
  if (!zs || !zs.length) return 1;
  let inside = false, mind = Infinity;
  for (const poly of zs) {
    if (pointInPoly(px, py, poly)) inside = true;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const ax = poly[j][0], ay = poly[j][1], bx = poly[i][0], by = poly[i][1];
      const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1;
      let t = ((px - ax) * dx + (py - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
      const d = Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
      if (d < mind) mind = d;
    }
  }
  if (!inside) return 1;
  return clamp(1 - mind / OCC_EDGE, 0, 1);   // hidden behind the stands, not a soft fade
}
function pointInPoly(x, y, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1];
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}

// Visible lamp posts: a slim post with a lantern head, standing in the scene.
// Faint by day, with the lantern lit warm at night. The light pools themselves
// come from applyLightMap; this is the physical fixture.
function drawLampPosts(lit) {
  for (const L of state.lamps) {
    if ((L.kind || 'light') === 'lantern') continue;   // lanterns have no visible fixture — ever (only their light shows, at night)
    if (L.x < 0 || L.x > PLATE_W) continue;
    if (obscured(L.x, L.y)) continue;   // behind a building: hide the post (light still spills in applyLightMap)
    const [x, y] = P2S(L.x, L.y);
    const sc = scaleAt(L.y) * view.s;
    const ph = (L.small ? 10 : 14) * sc, hx = x, hy = y - ph;
    ctx.lineCap = 'round';
    // post
    ctx.strokeStyle = 'rgba(40,42,38,0.65)';
    ctx.lineWidth = Math.max(0.8, 1.3 * sc);
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(hx, hy + 1.5 * sc); ctx.stroke();
    // lantern head — lit warm only when the lamps are on
    ctx.fillStyle = lit > 0.12 ? `rgba(255,224,150,${0.6 + 0.4 * lit})` : 'rgba(58,58,52,0.85)';
    ctx.strokeStyle = 'rgba(30,30,26,0.7)'; ctx.lineWidth = Math.max(0.5, 0.6 * sc);
    ctx.beginPath(); ctx.arc(hx, hy, (L.small ? 1.5 : 1.9) * sc, 0, 7); ctx.fill(); ctx.stroke();
  }
}

// Real night lighting. Build a warm light map (dark ambient floor + additive
// warm pools at every lamp and lit window) in an offscreen canvas, then MULTIPLY
// it over the whole composed scene — so lamps and windows actually illuminate
// the buildings, ground and people near them, and unlit areas fall dark.
function applyLightMap(n, lit, f) {
  const R = Math.ceil(PLATE_W * view.s), H = Math.ceil(PLATE_H * view.s);
  if (R < 1 || H < 1) return;                                // stage has no size yet (loading/resize) — nothing to light
  let lc = state.lc;
  if (!lc) lc = state.lc = document.createElement('canvas');
  if (lc.width !== R || lc.height !== H) { lc.width = R; lc.height = H; }
  const g = lc.getContext('2d');
  g.globalCompositeOperation = 'source-over';
  // ambient floor: how dark the unlit night gets (deep blue), eased through dusk
  g.fillStyle = `rgb(${Math.round(lerp(255, 18, n))},${Math.round(lerp(255, 26, n))},${Math.round(lerp(255, 54, n))})`;
  g.fillRect(0, 0, R, H);
  g.globalCompositeOperation = 'lighter';
  n = lit;  // light sources follow the on/off switch, not the sky
  const lamp = (lx, ly, rad, c0, c1) => {
    if (!isFinite(lx) || !isFinite(ly) || !isFinite(rad) || rad <= 0) return;
    const rg = g.createRadialGradient(lx, ly, 0, lx, ly, rad);
    rg.addColorStop(0, c0); rg.addColorStop(0.62, c1); rg.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = rg; g.beginPath(); g.arc(lx, ly, rad, 0, 7); g.fill();
  };
  // Lamp glow (lanterns + street lights) goes onto its OWN layer so we can then
  // ERASE the house silhouettes from it — a building blocks the light, it doesn't
  // pass through. (Window/floodlight glows stay on the main map: a window lights its
  // own house.) The lamp sits hidden behind a house; only its spill on open ground shows.
  let gc = state.gc; if (!gc) gc = state.gc = document.createElement('canvas');
  if (gc.width !== R || gc.height !== H) { gc.width = R; gc.height = H; }
  const gg = gc.getContext('2d');
  gg.clearRect(0, 0, R, H);
  gg.globalCompositeOperation = 'lighter';
  const glow = (lx, ly, rad, c0, c1) => {
    if (!isFinite(lx) || !isFinite(ly) || !isFinite(rad) || rad <= 0) return;
    const rg = gg.createRadialGradient(lx, ly, 0, lx, ly, rad);
    rg.addColorStop(0, c0); rg.addColorStop(0.62, c1); rg.addColorStop(1, 'rgba(0,0,0,0)');
    gg.fillStyle = rg; gg.beginPath(); gg.arc(lx, ly, rad, 0, 7); gg.fill();
  };
  // A building blocks only what is BEHIND it, never what is between it and the camera.
  // So interleave lamp glows and house silhouettes by depth (near-edge y), back to
  // front: a house erases glow from lamps drawn before it (deeper/behind), and lamps
  // drawn after it (in front) light freely — including onto that house's near face.
  // A house is keyed by its BACK edge (min y): only lamps deeper than that — genuinely
  // behind the building — are erased. Lamps in front of or beside it (including the
  // ones on the path/plaza at its foot) are drawn after, so they light its near face
  // and base. The building stays lit and blocks only what's truly behind it.
  const glowItems = [];
  for (const L of state.lamps) if (L.x >= 0 && L.x <= PLATE_W) glowItems.push({ py: L.y, lamp: L });
  for (const poly of (state.houses || [])) { let my = 1e9; for (const p of poly) my = Math.min(my, p[1]); glowItems.push({ py: my, house: poly }); }
  glowItems.sort((a, b) => a.py - b.py);
  for (const it of glowItems) {
    if (it.house) {
      gg.globalCompositeOperation = 'destination-out'; gg.fillStyle = '#000';
      gg.beginPath(); it.house.forEach((p, i) => { const x = p[0] * view.s, y = p[1] * view.s; i ? gg.lineTo(x, y) : gg.moveTo(x, y); }); gg.closePath(); gg.fill();
      gg.globalCompositeOperation = 'lighter';
      continue;
    }
    const L = it.lamp, sc = scaleAt(L.y) * view.s, lantern = (L.kind || 'light') === 'lantern';
    const lx = L.x * view.s, ly = L.y * view.s - (lantern ? 0 : 14) * sc;
    if (lantern) {   // softer, warmer, a closer reach
      glow(lx, ly, 82 * sc, `rgba(255,168,96,${0.36 * n})`, `rgba(255,146,78,${0.14 * n})`);
      glow(lx, ly, 34 * sc, `rgba(255,190,120,${0.72 * n})`, `rgba(255,164,92,${0.30 * n})`);
    } else {
      glow(lx, ly, 108 * sc, `rgba(255,186,116,${0.44 * n})`, `rgba(255,166,96,${0.17 * n})`);
      glow(lx, ly, 46 * sc, `rgba(255,202,142,${0.85 * n})`, `rgba(255,180,108,${0.34 * n})`);
    }
  }
  g.drawImage(gc, 0, 0);   // composite the depth-occluded lamp glow onto the light map
  for (const [pid, cnt] of Object.entries(f.occupancy || {})) {
    if (!cnt || !state.indoor.has(pid) || !state.map.places[pid]) continue;
    const p = state.map.places[pid]; if (p.x < 0 || p.x > PLATE_W) continue;
    const lx = p.x * view.s, ly = (p.y - 5) * view.s, sc = scaleAt(p.y) * view.s;
    const rc = (22 + Math.min(cnt, 5) * 5) * sc;
    lamp(lx, ly, rc * 2.6, `rgba(255,178,108,${0.4 * n})`, `rgba(255,160,90,${0.16 * n})`); // wide halo
    lamp(lx, ly, rc, `rgba(255,192,120,${0.8 * n})`, `rgba(255,170,100,${0.32 * n})`);       // core
  }
  // stadium floodlights: a strong, cool-white wash over the whole pitch when they're on
  const flood = floodOn(f);
  if (flood > 0 && state.floods) {
    const aim = state.floodAim, asc = scaleAt(aim.y) * view.s;
    for (const F of state.floods) {                       // a pool from each mast into its quadrant
      const cx = lerp(F.x, aim.x, 0.5) * view.s, cy = lerp(F.y, aim.y, 0.5) * view.s, sc = scaleAt(F.y) * view.s;
      lamp(cx, cy, 150 * sc, `rgba(226,238,255,${0.62 * flood})`, `rgba(206,224,255,${0.3 * flood})`);
    }
    lamp(aim.x * view.s, aim.y * view.s, 250 * asc, `rgba(230,240,255,${0.5 * flood})`, `rgba(210,226,255,${0.22 * flood})`); // whole-pitch wash
  }
  // Monday festival: a strong warm-gold wash over the square for the gathering
  const fest = festivalOn(f), sq = state.map.places && state.map.places.loc_main_square;
  if (fest > 0 && sq && sq.x > 0 && sq.x < PLATE_W) {
    const sc = scaleAt(sq.y) * view.s, lx = sq.x * view.s, ly = (sq.y - 4) * view.s;
    lamp(lx, ly, 200 * sc, `rgba(255,196,120,${0.6 * fest})`, `rgba(255,168,96,${0.28 * fest})`);   // warm crowd wash
    lamp(lx, ly, 95 * sc, `rgba(255,214,150,${0.85 * fest})`, `rgba(255,188,120,${0.4 * fest})`);    // brighter core
  }
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.drawImage(lc, view.ox, view.oy);
  ctx.restore();
  // bright bulb cores + window squares on top (additive) so the sources sparkle
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const L of state.lamps) {
    if ((L.kind || 'light') === 'lantern') continue;   // a lantern's SOURCE is never seen (only its spill, from the light-map above) — it sits hidden behind houses
    if (L.x < 0 || L.x > PLATE_W) continue;
    if (obscured(L.x, L.y)) continue;   // behind a wall: hide the visible source too, not just the post — you don't see a light through a wall (its spill in the light-map above still lights the surroundings)
    const [x, y] = P2S(L.x, L.y); const sc = scaleAt(L.y) * view.s;
    ctx.fillStyle = `rgba(255,240,206,${0.8 * n})`;
    ctx.beginPath(); ctx.arc(x, y - 14 * sc, 1.5 * sc, 0, 7); ctx.fill();  // the lit lamp head
  }
  ctx.restore();
}

function shade(hex, f) {
  const c = hex.replace('#', '');
  if (c.length !== 6) return hex;
  let r = parseInt(c.slice(0, 2), 16), g = parseInt(c.slice(2, 4), 16), b = parseInt(c.slice(4, 6), 16);
  r = clamp(Math.round(r * f), 0, 255); g = clamp(Math.round(g * f), 0, 255); b = clamp(Math.round(b * f), 0, 255);
  return `rgb(${r},${g},${b})`;
}

// --- HUD ---
function drawHUD(f) {
  const el = document.getElementById('clock');
  const mm = String(f.minute).padStart(2, '0');
  const busiest = f.busiest ? `busiest: ${f.busiest.name} (${f.busiest.count})` : '';
  el.innerHTML = `<b>${f.weekday}</b> · day ${f.day} · ${String(f.hour).padStart(2,'0')}:${mm}
    <span class="dim">· ${f.season} · ${f.weather.phrase}</span>`;
  document.getElementById('sub').textContent = busiest;
  updateStory(f);
  updateInspector(f);
}

// Replace loc_ ids and route arrows in sim text with friendly place names.
function prettify(text) {
  return text.replace(/loc_[a-z_]+/g, id => state.locName[id] || id)
    .replace(/\s*->\s*/g, ' → ');
}

// --- the town's unfolding story: a rolling feed of what's happening ---
function updateStory(f) {
  const fi = Math.floor(state.t);
  if (fi === state.storyAt) return;
  const back = state.storyAt >= 0 && fi < state.storyAt; // looped/scrubbed back
  state.storyAt = fi;
  if (back) state.story = [];
  const hm = `${String(f.hour).padStart(2, '0')}:${String(f.minute).padStart(2, '0')}`;
  for (const ev of (f.events || [])) {
    const actor = Array.isArray(ev) ? ev[0] : ev.actor;
    const text = Array.isArray(ev) ? ev[1] : ev.text;
    if (!text) continue;
    const who = actor && !text.startsWith(actor) ? actor + ' ' : '';
    state.story.push({ text: prettify((who + text).replace(/\s*—\s*at .*$/, '')), hm });
  }
  if (!f.events || !f.events.length) for (const c of (f.callouts || []).slice(0, 1)) state.story.push({ text: prettify(c.text), hm });
  if (state.story.length > 60) state.story = state.story.slice(-60);
  const near = document.getElementById('near');
  near.innerHTML = state.story.slice(-7).map(s => `<div class="cal"><span class="t">${s.hm}</span> ${s.text}</div>`).join('');
  near.scrollTop = near.scrollHeight;
}

// --- click-to-inspect: who is this person, and their life right now ---
function moodWord(m) { return m > 0.5 ? 'bright' : m > 0.15 ? 'content' : m > -0.15 ? 'even' : m > -0.5 ? 'low' : 'downcast'; }
function socWord(s) { return s >= 2 ? 'outgoing' : s === 1 ? 'sociable' : s === 0 ? 'even-keeled' : s === -1 ? 'reserved' : 'solitary'; }

function updateInspector(f) {
  const panel = document.getElementById('inspector');
  if (!state.selected) { panel.classList.add('hidden'); return; }
  const e = f.entities.find(x => x.id === state.selected);
  const meta = state.roster[state.selected];
  if (!e || !meta) { panel.classList.add('hidden'); return; }
  panel.classList.remove('hidden');
  const isRes = meta.kind === 'resident';
  const bar = (v, col) => `<span class="bar"><i style="width:${Math.round(clamp(v, 0, 1) * 100)}%;background:${col}"></i></span>`;
  const bonds = (f.bonds || []).filter(b => b.a === state.selected || b.b === state.selected)
    .map(b => ({ who: b.a === state.selected ? b.b : b.a, aff: b.affinity, place: b.place }))
    .sort((x, y) => y.aff - x.aff).slice(0, 4);
  const nameOf = id => (state.roster[id] || {}).name || id;
  let html = `<div class="ihead"><span class="dot" style="background:${meta.color}"></span><b>${meta.name}</b>
    <button id="iclose">✕</button></div>`;
  if (isRes) {
    html += `<div class="irow">${socWord(e.soc)}${e.child ? ' · a child' : ''}</div>
      <div class="idoing">${e.doing || '—'}</div>
      <div class="imeta">at <b>${state.locName[e.place] || e.place}</b>${e.partner ? ` · with <b>${nameOf(e.partner)}</b>` : ''}</div>
      <div class="istat">mood <span>${moodWord(e.mood)}</span> ${bar((e.mood + 1) / 2, '#e8b93a')}</div>
      <div class="istat">energy ${bar(e.energy, '#5fb0e8')}</div>`;
    if (e.worn && e.worn.length) html += `<div class="iworn">wearing: ${e.worn.join(', ').replace(/_/g, ' ')}</div>`;
    if (bonds.length) html += `<div class="ibonds"><div class="lbl">knows</div>${bonds.map(b => `<div class="bond" data-id="${b.who}">${nameOf(b.who)} <span class="aff">${'♥'.repeat(clamp(Math.round(b.aff / 2), 1, 5))}</span></div>`).join('')}</div>`;
  } else {
    html += `<div class="irow">${meta.kind}</div><div class="idoing">${e.doing || 'about the district'}</div>
      <div class="imeta">at <b>${state.locName[e.place] || e.place}</b></div>`;
  }
  panel.innerHTML = html;
  document.getElementById('iclose').onclick = () => { state.selected = null; draw(); };
  panel.querySelectorAll('.bond').forEach(el => el.onclick = () => { state.selected = el.dataset.id; draw(); });
}

// --- playback loop ---
function loop(ts) {
  if (!state.last) state.last = ts;
  const dt = Math.min((ts - state.last) / 1000, 0.25); state.last = ts;
  state.dt = dt;                          // for per-resident easing (turning, gait)
  state.anim = (state.anim || 0) + dt;   // real-time clock for ambient effects (water, sky) — runs even when paused
  if (state.playing) {
    // one tick = 300 game-seconds; advance the world by M game-seconds per real second
    state.t += dt * state.M / 300;
    if (state.t >= state.frames.length) state.t -= state.frames.length;  // seamless loop
    document.getElementById('scrub').value = Math.floor(state.t);
  }
  draw();
  requestAnimationFrame(loop);
}

function speedLabel(M) {
  if (M <= 1) return 'live · real time';
  if (M < 60) return `${M}× · ${M}s world/s`;
  return `${M}× · ${Math.round(M / 60)} min world/s`;
}

function wireControls() {
  const scrub = document.getElementById('scrub');
  scrub.max = state.frames.length - 1;
  scrub.addEventListener('input', () => { state.t = +scrub.value; state.playing = false; playBtn.textContent = '▶'; });
  const playBtn = document.getElementById('play');
  playBtn.addEventListener('click', () => { state.playing = !state.playing; playBtn.textContent = state.playing ? '❚❚' : '▶'; state.last = 0; });
  const STOPS = [1, 15, 60, 120, 300, 900, 1800];
  const speed = document.getElementById('speed');
  speed.min = 0; speed.max = STOPS.length - 1; speed.step = 1; speed.value = STOPS.indexOf(state.M);
  const applySpeed = () => { state.M = STOPS[+speed.value]; document.getElementById('speedv').textContent = speedLabel(state.M); };
  speed.addEventListener('input', applySpeed); applySpeed();
  document.getElementById('pins').addEventListener('change', e => state.showPins = e.target.checked);
  document.getElementById('names').addEventListener('change', e => state.showNames = e.target.checked);
  window.playBtn = playBtn;

  // click a figure to inspect them
  cnv.addEventListener('click', e => {
    if (suppressClick) { suppressClick = false; return; }   // this "click" was the end of a pan-drag
    const f = cnv.width / cnv.clientWidth;   // CSS px -> canvas px
    const cx = e.offsetX * f, cy = e.offsetY * f;
    let best = null, bd = Infinity;
    for (const lf of state.lastFigs) {
      const hy = lf.sy - 11 * lf.sc;          // aim at the body, not the feet
      const d = Math.hypot(cx - lf.sx, cy - hy);
      const r = Math.max(16 * f, 18 * lf.sc);
      if (d < r && d < bd) { bd = d; best = lf.id; }
    }
    state.selected = best;    // click empty space to deselect
    draw();
  });
}

boot();
