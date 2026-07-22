// ERA plate compositor — the living layer over plate-v1.
// Backdrop: the pre-graded plate. Living layer: residents/animals from the
// deterministic sim replay, positioned by a smooth world->plate mapping built
// from the plate-map pins, perspective-scaled and y-sorted.

const PLATE_W = 1376, PLATE_H = 768;
const PLATE_IMG = 'assets/plate-v1-graded.jpeg';

const state = {
  world: null, frames: [], map: null, anchors: [],
  t: 0, playing: true, speed: 6, last: 0, acc: 0,
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

  // night/day tint overlay
  const tint = skyTint(f.hour, f.minute);
  if (tint) {
    ctx.fillStyle = tint;
    ctx.fillRect(view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s);
  }

  if (state.showPins) drawPins();

  // living layer: map every entity, y-sort, draw back-to-front
  const figs = [];
  for (const e of f.entities) {
    const meta = state.roster[e.id] || { color: '#eee', kind: 'resident', name: e.id };
    const [px, py] = placeEntity(e);
    if (px < -40 || px > PLATE_W + 40 || py < -40 || py > PLATE_H + 40) continue; // off-frame
    figs.push({ e, meta, px, py });
  }
  figs.sort((a, b) => a.py - b.py);
  for (const fig of figs) drawFigure(fig, f);

  // foreground occluder: front greenery drawn over the living layer, so figures
  // by the banks read as *behind* the front bushes (the 2.5D depth cue).
  if (state.occluder) {
    ctx.drawImage(state.occluder, view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s);
    if (tint) { ctx.save(); ctx.globalCompositeOperation = 'source-atop'; ctx.fillStyle = tint; ctx.fillRect(view.ox, view.oy, PLATE_W * view.s, PLATE_H * view.s); ctx.restore(); }
  }

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

function drawFigure(fig, f) {
  const { e, meta } = fig;
  const [x, y] = P2S(fig.px, fig.py);
  const sc = scaleAt(fig.py) * view.s;
  const isAnimal = meta.kind !== 'resident';
  const col = meta.color || '#ddd';

  // soft ground shadow
  ctx.fillStyle = 'rgba(0,0,0,.22)';
  ctx.beginPath(); ctx.ellipse(x, y, 7 * sc, 3 * sc, 0, 0, 7); ctx.fill();

  if (isAnimal) {
    // small low mark for dog/birds
    ctx.fillStyle = col;
    ctx.beginPath(); ctx.ellipse(x, y - 3 * sc, 5 * sc, 3 * sc, 0, 0, 7); ctx.fill();
  } else {
    // a small standing figure: body + head, colour = identity
    const bodyH = 16 * sc, bodyW = 7 * sc, headR = 4.2 * sc;
    ctx.fillStyle = col;
    roundRect(x - bodyW / 2, y - bodyH, bodyW, bodyH - headR, 3 * sc);
    ctx.fill();
    ctx.beginPath(); ctx.arc(x, y - bodyH - headR * 0.2, headR, 0, 7);
    ctx.fillStyle = shade(col, 1.12); ctx.fill();
    // subtle outline for legibility on busy plate
    ctx.lineWidth = Math.max(0.6, 0.8 * sc); ctx.strokeStyle = 'rgba(20,16,12,.55)';
    ctx.beginPath(); ctx.arc(x, y - bodyH - headR * 0.2, headR, 0, 7); ctx.stroke();
    // gesture spark
    if (e.gest && e.gest !== 'none' && e.gest !== 'idle') {
      ctx.fillStyle = 'rgba(255,240,180,.9)';
      ctx.beginPath(); ctx.arc(x + bodyW * 0.7, y - bodyH - headR, 1.6 * sc, 0, 7); ctx.fill();
    }
  }
  if (state.showNames && !isAnimal) {
    ctx.font = `${Math.max(9, 9 * sc)}px system-ui`;
    ctx.fillStyle = 'rgba(255,255,255,.92)';
    ctx.textAlign = 'center';
    ctx.fillText(meta.name, x, y - 20 * sc - 6);
    ctx.textAlign = 'left';
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

// day/night wash. Returns a fillStyle or null (full day).
function skyTint(hour, minute) {
  const h = hour + minute / 60;
  if (h >= 7 && h < 17) return null;                       // day
  if (h >= 5 && h < 7) return `rgba(255,150,90,${lerp(0.28, 0, (h - 5) / 2)})`;   // dawn
  if (h >= 17 && h < 20) return `rgba(40,50,110,${lerp(0, 0.30, (h - 17) / 3)})`; // dusk
  return 'rgba(18,24,64,.42)';                             // night
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
  const dt = (ts - state.last) / 1000; state.last = ts;
  if (state.playing) {
    state.t += dt * state.speed;
    if (state.t >= state.frames.length) state.t = 0;
    document.getElementById('scrub').value = Math.floor(state.t);
  }
  draw();
  requestAnimationFrame(loop);
}

function wireControls() {
  const scrub = document.getElementById('scrub');
  scrub.max = state.frames.length - 1;
  scrub.addEventListener('input', () => { state.t = +scrub.value; state.playing = false; playBtn.textContent = '▶'; });
  const playBtn = document.getElementById('play');
  playBtn.addEventListener('click', () => { state.playing = !state.playing; playBtn.textContent = state.playing ? '❚❚' : '▶'; state.last = 0; });
  document.getElementById('speed').addEventListener('input', e => { state.speed = +e.target.value; document.getElementById('speedv').textContent = state.speed + '×'; });
  document.getElementById('pins').addEventListener('change', e => state.showPins = e.target.checked);
  document.getElementById('names').addEventListener('change', e => state.showNames = e.target.checked);
  window.playBtn = playBtn;
}

boot();
