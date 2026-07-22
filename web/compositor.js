// ERA plate compositor — the living layer over plate-v1.
// Backdrop: the pre-graded plate. Living layer: residents/animals from the
// deterministic sim replay, positioned by a smooth world->plate mapping built
// from the plate-map pins, perspective-scaled and y-sorted.

const PLATE_W = 1376, PLATE_H = 768;
const PLATE_IMG = 'assets/plate-v1-graded.jpeg';

const state = {
  world: null, frames: [], map: null, anchors: [],
  t: 0, playing: true, M: 120, last: 0,   // M = game-seconds per real-second (1 = true real time)
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
  } else {                                      // served build
    [replay, map, plate] = await Promise.all([
      fetch('assets/replay.json').then(r => r.json()),
      fetch('assets/era-plate-map.json').then(r => r.json()),
      loadImg(PLATE_IMG),
    ]);
    state.occluder = await loadImg('assets/occluder.png').catch(() => null);
  }
  state.world = replay.world;
  state.frames = replay.frames;
  state.map = map;
  state.plate = plate;

  // anchors: world (x,y) from the replay's static locations  <->  plate pixels
  // from the plate-map. Both keyed by loc id, all 23 places.
  const px = map.places;
  state.anchors = state.world.locations
    .filter(l => px[l.id])
    .map(l => ({ id: l.id, wx: l.x, wy: l.y, px: px[l.id].x, py: px[l.id].y }));

  // roster: id -> {name, kind, color}
  state.roster = {};
  for (const e of state.world.entities) state.roster[e.id] = e;

  // indoor places: homes + workplaces that are inside. A settled resident here is
  // indoors, not standing on the roof — so we don't draw them (their window lights
  // up at night instead). Café/pub/square/market/riverside/ground stay visible.
  const INDOOR_WORK = ['loc_bakery', 'loc_club_shop', 'loc_corner_grocer', 'loc_club_offices', 'loc_museum', 'loc_school'];
  state.indoor = new Set([...state.world.locations.filter(l => l.home).map(l => l.id), ...INDOOR_WORK]);

  // obscured zones: polygons (plate px) the camera can't see past — anyone whose
  // feet fall inside is hidden. Authored in the plate-mapper's obscure tool.
  state.obscured = (map.obscured || []).map(z => z.pts || z);

  // streetlamps: drop a lamp every ~95px along the streets and lanes
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
  // extra lamps around the town centre — the heart wants more light
  const CENTER = ['loc_main_square', 'loc_cafe', 'loc_pub', 'loc_bakery', 'loc_high_street',
    'loc_corner_grocer', 'loc_north_gate', 'loc_museum', 'loc_club_shop', 'loc_bridge'];
  for (const id of CENTER) {
    const p = map.places[id];
    if (p && p.x > 0 && p.x < PLATE_W) state.lamps.push({ x: p.x, y: p.y + 6, center: true });
  }

  sizeCanvas();
  window.addEventListener('resize', sizeCanvas);
  wireControls();
  // headless capture hooks
  window.__state = state; window.__draw = draw; window.__ready = true;
  window.__seek = (frame) => { state.playing = false; state.t = frame; draw(); };
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
function placeEntity(e) {
  const P = state.map.places;
  if (e.moving && e.from && e.to && P[e.from] && P[e.to]) {
    const a = P[e.from], b = P[e.to], t = clamp(e.et || 0, 0, 1);
    const [jx, jy] = jitterPx(e.id, 2);
    return [lerp(a.x, b.x, t) + jx, lerp(a.y, b.y, t) + jy];
  }
  // stadium: spectators/gatherers stand in the STANDS, not on the pitch. Only
  // the groundskeeper (tending the pitch) stays on the grass.
  if (!e.moving && e.place === 'loc_stadium' && !/pitch|grounds|mow|groundskeep/i.test(e.doing || '')) {
    const h = hashId(e.id);
    return [1020 + (h % 300), 388 + ((h >> 4) % 5) * 7];  // rows in the terracing
  }
  return worldToPlate(e.x, e.y);
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
  const t = clamp((py - 230) / (700 - 230), 0, 1);
  return lerp(0.55, 1.35, t);
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;

// --- canvas / layout ---
let cnv, ctx, view = { s: 1, ox: 0, oy: 0 };
function sizeCanvas() {
  cnv = document.getElementById('c'); ctx = cnv.getContext('2d');
  const wrap = document.getElementById('stage');
  const cw = wrap.clientWidth, ch = wrap.clientHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  cnv.width = cw * dpr; cnv.height = ch * dpr;
  cnv.style.width = cw + 'px'; cnv.style.height = ch + 'px';
  // fit the plate into the stage (contain)
  const s = Math.min(cw / PLATE_W, ch / PLATE_H);
  view.s = s * dpr;
  view.ox = (cw * dpr - PLATE_W * view.s) / 2;
  view.oy = (ch * dpr - PLATE_H * view.s) / 2;
}
const P2S = (x, y) => [view.ox + x * view.s, view.oy + y * view.s];

// --- draw ---
function draw() {
  const f = state.frames[Math.floor(state.t)];
  if (!f) return;
  ctx.clearRect(0, 0, cnv.width, cnv.height);
  // backdrop
  ctx.drawImage(state.plate, view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s);

  const night = nightFactor(f.hour, f.minute);

  drawLampPosts(night);

  // living layer on the lit plate: map every entity, y-sort, draw back-to-front
  const figs = [];
  for (const e of f.entities) {
    const meta = state.roster[e.id] || { color: '#eee', kind: 'resident', name: e.id };
    if (meta.kind === 'resident' && !e.moving && state.indoor.has(e.place)) continue; // indoors
    const [px, py] = placeEntity(e);
    if (px < -40 || px > PLATE_W + 40 || py < -40 || py > PLATE_H + 40) continue; // off-frame
    if (obscured(px, py)) continue; // behind a building the camera can't see past
    figs.push({ e, meta, px, py });
  }
  figs.sort((a, b) => a.py - b.py);
  for (const fig of figs) drawFigure(fig, f);

  // foreground occluder: front greenery over the living layer (2.5D depth).
  if (state.occluder) ctx.drawImage(state.occluder, view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s);

  // night lighting: multiply a warm light map over the whole composed scene, so
  // lamps and lit windows genuinely illuminate the buildings, ground and people
  // around them — everything else falls into real darkness.
  if (night > 0) applyLightMap(night, f);

  if (state.showPins) drawPins();
  drawHUD(f);
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

function drawFigure(fig, f) {
  const { e, meta } = fig;
  let [x, y] = P2S(fig.px, fig.py);
  const sc = scaleAt(fig.py) * view.s;
  if (meta.kind !== 'resident') { drawAnimal(fig, f, x, y, sc); return; }

  const col = meta.color || '#c9cad3';
  const hs = hashId(e.id);
  const k = e.child ? 0.74 : 1.0;
  const U = sc * k;
  const hd = e.h || 0;
  const faceS = Math.cos(hd) >= 0 ? 1 : -1;
  const moving = e.moving && (e.spd || 0) > 0.05;
  const wph = moving ? Math.sin(state.t * 3.4 + (hs % 628) / 100) : 0;
  const pose = e.pose || 'stand';
  const sit = pose === 'sit' || pose === 'lie';
  const worn = e.worn || [];
  const gest = e.gest || 'none';
  const ink = 'rgba(30,22,16,.6)';

  // ground shadow
  ctx.fillStyle = 'rgba(0,0,0,.20)';
  ctx.beginPath(); ctx.ellipse(x, y, 7 * U, 2.6 * U, 0, 0, 7); ctx.fill();

  const legH = (sit ? 2.2 : 5) * U, torsoH = (sit ? 6 : 8) * U, torsoW = 6 * U;
  const headR = 3.2 * U * (e.child ? 1.14 : 1);
  // idle life: a slow breathing bob + faint sway when standing about
  const idle = moving ? 0 : Math.sin(state.t * 1.5 + (hs % 628) / 100);
  const sway = moving ? 0 : Math.sin(state.t * 0.9 + (hs % 314) / 100) * 0.5 * U;
  const bob = moving ? Math.abs(wph) * 0.6 * U : idle * 0.25 * U;
  const hipY = y - legH + bob, shoulderY = hipY - torsoH, headCY = shoulderY - headR * 0.9 + idle * 0.15 * U;
  x += sway;
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';

  // legs
  ctx.strokeStyle = shade(col, 0.7); ctx.lineWidth = 2.2 * U;
  if (sit) {
    ctx.beginPath(); ctx.moveTo(x, hipY); ctx.lineTo(x + faceS * 3.4 * U, hipY + 0.4 * U); ctx.stroke();
  } else {
    const stride = moving ? wph * 2.6 * U : 1.0 * U;
    ctx.beginPath(); ctx.moveTo(x, hipY); ctx.lineTo(x + stride * faceS, y + bob); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x, hipY); ctx.lineTo(x - stride * faceS, y + bob); ctx.stroke();
  }

  // torso — clay-shaded capsule, colour = identity
  const g = ctx.createLinearGradient(0, shoulderY, 0, hipY);
  g.addColorStop(0, shade(col, 1.12)); g.addColorStop(1, shade(col, 0.85));
  ctx.fillStyle = g;
  roundRect(x - torsoW / 2, shoulderY, torsoW, torsoH + (sit ? 0 : U), 3 * U); ctx.fill();
  ctx.lineWidth = Math.max(0.5, 0.7 * U); ctx.strokeStyle = ink; ctx.stroke();

  // arms (front arm raises on a gesture)
  ctx.strokeStyle = shade(col, 0.95); ctx.lineWidth = 2.0 * U;
  const armY = shoulderY + 2.2 * U, raise = (gest === 'gesture' || gest === 'laugh');
  ctx.beginPath(); ctx.moveTo(x - torsoW * 0.35, armY);
  ctx.lineTo(x - torsoW * 0.35 - faceS * (moving ? -wph * 1.6 * U : 1.1 * U), armY + (sit ? 2 : 3.2) * U); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x + torsoW * 0.35, armY);
  if (raise) ctx.lineTo(x + torsoW * 0.35 + faceS * 1.6 * U, armY - 3.2 * U);
  else ctx.lineTo(x + torsoW * 0.35 + faceS * (moving ? wph * 1.6 * U : 1.1 * U), armY + (sit ? 2 : 3.2) * U);
  ctx.stroke();

  // coat overlay (worn)
  if (worn.includes('coat')) {
    ctx.fillStyle = 'rgba(60,50,40,.5)';
    roundRect(x - torsoW / 2, shoulderY + 1 * U, torsoW, torsoH, 3 * U); ctx.fill();
  }
  // scarf
  if (worn.includes('club_scarf') || worn.includes('scarf')) {
    ctx.strokeStyle = '#c9463d'; ctx.lineWidth = 1.7 * U;
    ctx.beginPath(); ctx.moveTo(x - 2 * U, shoulderY + 0.6 * U); ctx.lineTo(x + 2 * U, shoulderY + 0.6 * U); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + 0.8 * U, shoulderY + 0.6 * U); ctx.lineTo(x + 1.5 * U * faceS, shoulderY + 3 * U); ctx.stroke();
  }

  // head + hair
  ctx.fillStyle = skinOf(e.id);
  ctx.beginPath(); ctx.arc(x + faceS * 0.4 * U, headCY, headR, 0, 7); ctx.fill();
  ctx.lineWidth = Math.max(0.5, 0.7 * U); ctx.strokeStyle = ink; ctx.stroke();
  ctx.fillStyle = hairOf(e.id);
  ctx.beginPath(); ctx.arc(x + faceS * 0.4 * U, headCY - headR * 0.22, headR * 0.94, Math.PI * 1.04, Math.PI * 2.06); ctx.fill();

  // hats / umbrella
  if (worn.includes('sunhat')) {
    ctx.fillStyle = '#e6d49a';
    ctx.beginPath(); ctx.ellipse(x + faceS * 0.4 * U, headCY - headR * 0.45, headR * 1.6, headR * 0.55, 0, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x + faceS * 0.4 * U, headCY - headR * 0.8, headR * 0.75, headR * 0.55, 0, Math.PI, 0); ctx.fill();
  }
  if (worn.includes('umbrella')) {
    ctx.fillStyle = 'rgba(45,65,95,.92)';
    ctx.beginPath(); ctx.ellipse(x, headCY - headR * 2.6, 6.5 * U, 2.6 * U, 0, Math.PI, 0); ctx.fill();
    ctx.strokeStyle = 'rgba(45,65,95,.92)'; ctx.lineWidth = 0.8 * U;
    ctx.beginPath(); ctx.moveTo(x, headCY - headR * 2.6); ctx.lineTo(x, headCY + headR * 0.5); ctx.stroke();
  }
  // laugh spark
  if (gest === 'laugh') { ctx.fillStyle = 'rgba(255,240,180,.95)'; ctx.beginPath(); ctx.arc(x + faceS * 3 * U, headCY - 2 * U, 1.3 * U, 0, 7); ctx.fill(); }

  if (state.showNames) {
    ctx.font = `${Math.max(9, 9 * U)}px system-ui`; ctx.fillStyle = 'rgba(255,255,255,.92)';
    ctx.textAlign = 'center'; ctx.fillText(meta.name, x, headCY - headR - 4 * U); ctx.textAlign = 'left';
  }
}

function drawAnimal(fig, f, x, y, sc) {
  const { e, meta } = fig; const col = meta.color || '#b98a5a'; const k = sc * 1.25; const kind = meta.kind;
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.fillStyle = 'rgba(0,0,0,.16)'; ctx.beginPath(); ctx.ellipse(x, y, 5 * k, 1.8 * k, 0, 0, 7); ctx.fill();

  if (kind === 'cat') {
    ctx.strokeStyle = shade(col, 0.75); ctx.lineWidth = 1.1 * k;
    for (const dx of [-2, -0.5, 0.5, 2]) { ctx.beginPath(); ctx.moveTo(x + dx * k, y - 2.4 * k); ctx.lineTo(x + dx * k, y); ctx.stroke(); }
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
    ctx.strokeStyle = shade(col, 0.7); ctx.lineWidth = 1.3 * k;
    for (const dx of [-2.5, -1, 1, 2.5]) { ctx.beginPath(); ctx.moveTo(x + dx * k, y - 3 * k); ctx.lineTo(x + dx * k, y); ctx.stroke(); }
    ctx.fillStyle = col; roundRect(x - 4 * k, y - 6 * k, 8 * k, 3.4 * k, 1.7 * k); ctx.fill();
    ctx.beginPath(); ctx.arc(x + 4.2 * k, y - 6.2 * k, 2 * k, 0, 7); ctx.fill();
    ctx.strokeStyle = col; ctx.lineWidth = 1.3 * k;
    ctx.beginPath(); ctx.moveTo(x - 4 * k, y - 5.5 * k); ctx.lineTo(x - 6.4 * k, y - (kind === 'fox' ? 6 : 7.6) * k); ctx.stroke();
    if (kind === 'fox') { ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x + 3.5 * k, y - 7.6 * k); ctx.lineTo(x + 4.2 * k, y - 9.2 * k); ctx.lineTo(x + 4.9 * k, y - 7.6 * k); ctx.fill(); }
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

// 0 = full day, 1 = deep night, ramped through dawn/dusk.
function nightFactor(hour, minute) {
  const h = hour + minute / 60;
  if (h >= 7 && h < 17) return 0;
  if (h >= 5 && h < 7) return clamp(1 - (h - 5) / 2, 0, 1);     // dawn fade out
  if (h >= 17 && h < 20.5) return clamp((h - 17) / 3.5, 0, 1);  // dusk fade in
  return 1;                                                     // night
}

// A resident whose feet fall inside an obscured region (a passage the camera
// can't see past, marked in the plate-mapper) is hidden.
function obscured(px, py) {
  const zs = state.obscured;
  if (!zs || !zs.length) return false;
  for (const poly of zs) if (pointInPoly(px, py, poly)) return true;
  return false;
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
function drawLampPosts(night) {
  for (const L of state.lamps) {
    if (L.x < 0 || L.x > PLATE_W) continue;
    const [x, y] = P2S(L.x, L.y);
    const sc = scaleAt(L.y) * view.s;
    const ph = 14 * sc, hx = x, hy = y - ph;
    ctx.lineCap = 'round';
    // post
    ctx.strokeStyle = `rgba(38,40,36,${0.5 + 0.35 * night})`;
    ctx.lineWidth = Math.max(0.8, 1.3 * sc);
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(hx, hy + 1.5 * sc); ctx.stroke();
    // lantern head
    ctx.fillStyle = night > 0.15 ? `rgba(255,224,150,${0.6 + 0.4 * night})` : 'rgba(60,60,54,0.8)';
    ctx.strokeStyle = 'rgba(30,30,26,0.7)'; ctx.lineWidth = Math.max(0.5, 0.6 * sc);
    ctx.beginPath(); ctx.arc(hx, hy, 1.9 * sc, 0, 7); ctx.fill(); ctx.stroke();
  }
}

// Real night lighting. Build a warm light map (dark ambient floor + additive
// warm pools at every lamp and lit window) in an offscreen canvas, then MULTIPLY
// it over the whole composed scene — so lamps and windows actually illuminate
// the buildings, ground and people near them, and unlit areas fall dark.
function applyLightMap(n, f) {
  const R = Math.ceil(PLATE_W * view.s), H = Math.ceil(PLATE_H * view.s);
  let lc = state.lc;
  if (!lc) lc = state.lc = document.createElement('canvas');
  if (lc.width !== R || lc.height !== H) { lc.width = R; lc.height = H; }
  const g = lc.getContext('2d');
  g.globalCompositeOperation = 'source-over';
  // ambient floor: how dark the unlit night gets (deep blue), eased through dusk
  g.fillStyle = `rgb(${Math.round(lerp(255, 18, n))},${Math.round(lerp(255, 26, n))},${Math.round(lerp(255, 54, n))})`;
  g.fillRect(0, 0, R, H);
  g.globalCompositeOperation = 'lighter';
  const lamp = (lx, ly, rad, c0, c1) => {
    if (!isFinite(lx) || !isFinite(ly) || !isFinite(rad) || rad <= 0) return;
    const rg = g.createRadialGradient(lx, ly, 0, lx, ly, rad);
    rg.addColorStop(0, c0); rg.addColorStop(0.62, c1); rg.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = rg; g.beginPath(); g.arc(lx, ly, rad, 0, 7); g.fill();
  };
  for (const L of state.lamps) {
    if (L.x < 0 || L.x > PLATE_W) continue;
    const sc = scaleAt(L.y) * view.s;
    const lx = L.x * view.s, ly = L.y * view.s - 14 * sc;   // pool centred at the lantern head
    lamp(lx, ly, 108 * sc, `rgba(255,186,116,${0.44 * n})`, `rgba(255,166,96,${0.17 * n})`); // wide soft spill
    lamp(lx, ly, 46 * sc, `rgba(255,202,142,${0.85 * n})`, `rgba(255,180,108,${0.34 * n})`); // brighter core
  }
  for (const [pid, cnt] of Object.entries(f.occupancy || {})) {
    if (!cnt || !state.indoor.has(pid) || !state.map.places[pid]) continue;
    const p = state.map.places[pid]; if (p.x < 0 || p.x > PLATE_W) continue;
    const lx = p.x * view.s, ly = (p.y - 5) * view.s, sc = scaleAt(p.y) * view.s;
    const rc = (22 + Math.min(cnt, 5) * 5) * sc;
    lamp(lx, ly, rc * 2.6, `rgba(255,178,108,${0.4 * n})`, `rgba(255,160,90,${0.16 * n})`); // wide halo
    lamp(lx, ly, rc, `rgba(255,192,120,${0.8 * n})`, `rgba(255,170,100,${0.32 * n})`);       // core
  }
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.drawImage(lc, view.ox, view.oy);
  ctx.restore();
  // bright bulb cores + window squares on top (additive) so the sources sparkle
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const L of state.lamps) {
    if (L.x < 0 || L.x > PLATE_W) continue;
    const [x, y] = P2S(L.x, L.y); const sc = scaleAt(L.y) * view.s;
    ctx.fillStyle = `rgba(255,240,206,${0.8 * n})`;
    ctx.beginPath(); ctx.arc(x, y - 14 * sc, 1.5 * sc, 0, 7); ctx.fill();  // glow at the lantern head
  }
  for (const [pid, cnt] of Object.entries(f.occupancy || {})) {
    if (!cnt || !state.indoor.has(pid) || !state.map.places[pid]) continue;
    const p = state.map.places[pid]; if (p.x < 0 || p.x > PLATE_W) continue;
    const [x, y] = P2S(p.x, p.y - 5); const sc = scaleAt(p.y) * view.s;
    ctx.fillStyle = `rgba(255,226,164,${0.95 * n})`;
    for (let i = 0; i < Math.min(cnt, 3); i++) ctx.fillRect(x - 3 * sc + i * 3 * sc, y, 1.5 * sc, 1.5 * sc);
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
  const near = document.getElementById('near');
  // a couple of live callouts for texture
  near.innerHTML = (f.callouts || []).slice(0, 3)
    .map(c => `<div class="cal">${c.text}</div>`).join('');
}

// --- playback loop ---
function loop(ts) {
  if (!state.last) state.last = ts;
  const dt = Math.min((ts - state.last) / 1000, 0.25); state.last = ts;
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
}

boot();
