// ERA — the prove-it slice. A PixiJS renderer that observes the *same* live
// behaviour stream as the top-down client (the Rust engine compiled to WASM,
// ticking here in the tab) and draws the town in the locked true-2:1 isometric,
// in the bright diorama palette, with residents whose temperament — sociability,
// mood, energy, straight from the simulation — shows in how they stand and move.
//
// Placeholder figures on purpose: this proves the pipeline and the "alive" read,
// not the final art. Real rigged assets (Spine/Rive) drop in later behind the
// same stream. See design/asset-design-model.md.

import init, { WasmEngine } from './pkg/era_first_breath.js';

// ------------------------------------------------------------------ iso maths
// True 2:1 isometric: a world step of +x goes screen (+1, +0.5); +y goes (-1, +0.5).
const TILE = 0.5;                 // world→screen horizontal scale before fit
function iso(x, y) { return [(x - y) * TILE, (x + y) * TILE * 0.5]; }

// ------------------------------------------------------------------- palette
const C = {
  sky: 0xa9d6e6,
  grassTop: 0x63b64d, grassBot: 0x4c9c39,
  path: 0xccc6b8, pathEdge: 0xb7b09e,
  padPublic: 0xece0c4, padHome: 0xd8c6a0, padOpen: 0xfff3d6,
  water: 0x3f9aa6,
  ink: 0x24371d, inkSoft: 0x4a5a44,
  open: 0x2f7d46, closed: 0x6d7a86, warm: 0xe0a24a,
};

// seasonal dressing — the ground, the foliage and a few extras change by season.
const SEASONS = {
  Summer: { grassTop: 0x63b64d, grassBot: 0x4c9c39, canopy: [0x3f8a30, 0x66bd53, 0x57ab46], bare: false, blossom: false, snow: false },
  Autumn: { grassTop: 0x9caa4a, grassBot: 0x84772f, canopy: [0xc4702f, 0xd8963a, 0xb5893a], bare: false, blossom: false, snow: false },
  Winter: { grassTop: 0xdbe4e6, grassBot: 0xbcc8ca, canopy: [0x8a9aa0, 0x9fb0b4, 0x7f9095], bare: true, blossom: false, snow: true },
  Spring: { grassTop: 0x74c25a, grassBot: 0x5aa842, canopy: [0x6fc253, 0x8ed06a, 0x57ab46], bare: false, blossom: true, snow: false },
};
let SEASON = SEASONS.Summer, lastSeason = 'Summer';

// ---------------------------------------------------------------- engine glue
let eng, WORLD, prev = null, cur = null;
const NODES = {}, ROSTER = {};
let playing = true, speed = 1, acc = 0, last = null, tms = 0;
const BASE_TPS = 7 / 6;           // ~1.17 five-minute ticks/sec (matches era.js)

const $ = id => document.getElementById(id);
const pad = n => String(n).padStart(2, '0');

// hover state
let hoverId = null;

// ------------------------------------------------------------------- fit view
let FIT = { s: 1, ox: 0, oy: 0 };
function computeFit(vw, vh) {
  let minx = Infinity, miny = Infinity, maxx = -Infinity, maxy = -Infinity;
  WORLD.locations.forEach(l => {
    const [ix, iy] = iso(l.x, l.y);
    minx = Math.min(minx, ix); maxx = Math.max(maxx, ix);
    miny = Math.min(miny, iy); maxy = Math.max(maxy, iy);
  });
  const pad = 120;
  // Pull the camera back a little (× 0.85) so the world reads as a small model on
  // a table, with air around it, rather than filling the frame.
  const s = Math.min((vw - pad * 2) / (maxx - minx), (vh - pad * 2) / (maxy - miny)) * 0.85;
  FIT.s = s;
  FIT.ox = vw / 2 - ((minx + maxx) / 2) * s;
  FIT.oy = vh / 2 - ((miny + maxy) / 2) * s + 10;
}
function project(x, y) { const [ix, iy] = iso(x, y); return [ix * FIT.s + FIT.ox, iy * FIT.s + FIT.oy]; }

// -------------------------------------------------------------- interpolation
function lerpEntities(a, b, f) {
  const bmap = {}; b.entities.forEach(e => bmap[e.id] = e);
  return a.entities.map(e => {
    const e2 = bmap[e.id] || e;
    return { ...e, x: e.x + (e2.x - e.x) * f, y: e.y + (e2.y - e.y) * f };
  });
}

// disposition helpers (default gracefully if an older engine build omits them)
const socOf = e => (typeof e.soc === 'number' ? e.soc : 0);
const moodOf = e => (typeof e.mood === 'number' ? e.mood : 0);
const energyOf = e => (typeof e.energy === 'number' ? e.energy : 1);
// readiness ~ the sim's social_readiness(): openness of body language
function readiness(e) { return socOf(e) + moodOf(e) * 3 + (energyOf(e) - 0.5) * 4; }
function seedOf(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return ((h >>> 0) % 1000) / 1000; }

// --------------------------------------------------------------------- Pixi
let app, gGround, gPaths, gPlaces, gActors, labelLayer, gWeather;
const labels = {};

async function main() {
  await init();
  eng = new WasmEngine(0);
  WORLD = JSON.parse(eng.world_json());
  WORLD.locations.forEach(l => NODES[l.id] = l);
  WORLD.entities.forEach(e => ROSTER[e.id] = e);
  cur = JSON.parse(eng.snapshot_json()); prev = cur;

  app = new PIXI.Application();
  await app.init({ background: C.sky, antialias: true, resizeTo: window, autoDensity: true,
    resolution: window.devicePixelRatio || 1 });
  $('stage').appendChild(app.canvas);

  gGround = new PIXI.Graphics();
  gPaths = new PIXI.Graphics();
  gPlaces = new PIXI.Graphics();
  gActors = new PIXI.Graphics();
  labelLayer = new PIXI.Container();
  gWeather = new PIXI.Graphics();          // veil + precipitation, on top of all
  app.stage.addChild(gGround, gPaths, gPlaces, gActors, labelLayer, gWeather);

  // a soft tilt-shift: blur the far and near thirds of the frame gently.
  applyTiltShift();

  SEASON = SEASONS[cur.season] || SEASON; lastSeason = cur.season;
  computeFit(window.innerWidth, window.innerHeight);
  drawStatic();
  window.addEventListener('resize', () => { computeFit(window.innerWidth, window.innerHeight); drawStatic(); });

  // pointer hover → nearest actor
  app.stage.eventMode = 'static';
  app.stage.hitArea = { contains: () => true };
  app.stage.on('pointermove', ev => {
    const mx = ev.global.x, my = ev.global.y;
    let best = null, bd = 26;
    (cur.entities).forEach(e => {
      const [sx, sy] = project(e.x, e.y);
      const d = Math.hypot(sx - mx, sy - my);
      if (d < bd) { bd = d; best = e.id; }
    });
    hoverId = best;
    const tip = $('tip');
    if (best && ROSTER[best] && ROSTER[best].kind === 'resident') {
      const e = cur.entities.find(x => x.id === best);
      tip.style.opacity = 1; tip.style.left = (mx + 14) + 'px'; tip.style.top = (my + 14) + 'px';
      tip.innerHTML = `<b>${ROSTER[best].name}</b> · sociability ${socOf(e)} · ` +
        `mood ${moodOf(e).toFixed(2)} · energy ${energyOf(e).toFixed(2)}<br>${e.doing}`;
    } else { tip.style.opacity = 0; }
  });

  // controls
  $('play').onclick = e => { playing = !playing; e.target.textContent = playing ? 'Pause' : 'Play'; };
  document.querySelectorAll('[data-mul]').forEach(b => b.onclick = () => {
    speed = +b.dataset.mul;
    document.querySelectorAll('[data-mul]').forEach(x => x.classList.toggle('on', x === b));
  });
  document.querySelector('[data-mul="1"]').classList.add('on');

  $('loading').remove();
  renderHud(cur);
  app.ticker.add(loop);
}

function applyTiltShift() {
  try {
    // A cheap evocation of tilt-shift: blur the ground plane faintly so the model
    // reads as "photographed small". (Depth-graded blur is a later refinement.)
    gGround.filters = [new PIXI.BlurFilter({ strength: 1.5, quality: 2 })];
  } catch (_) { /* filters optional */ }
}

// ------------------------------------------------------------- static layers
function drawStatic() {
  // ground: one big bright rhombus spanning the projected map, plus a subtle grid.
  gGround.clear();
  const corners = [iso(-40, -40), iso(1080, -40), iso(1080, 820), iso(-40, 820)]
    .map(([ix, iy]) => [ix * FIT.s + FIT.ox, iy * FIT.s + FIT.oy]);
  gGround.poly(corners.flat()).fill(SEASON.grassBot);
  // a lighter top sheen
  const sheen = [iso(-40, -40), iso(1080, -40), iso(560, 390)]
    .map(([ix, iy]) => [ix * FIT.s + FIT.ox, iy * FIT.s + FIT.oy]);
  gGround.poly(sheen.flat()).fill({ color: SEASON.grassTop, alpha: 0.5 });

  // paths: the nav edges as inlaid iso lines.
  gPaths.clear();
  WORLD.edges.forEach(([a, b]) => {
    const A = NODES[a], B = NODES[b]; if (!A || !B) return;
    const [x1, y1] = project(A.x, A.y), [x2, y2] = project(B.x, B.y);
    gPaths.moveTo(x1, y1).lineTo(x2, y2).stroke({ width: 7 * FIT.s + 3, color: C.path, alpha: 0.9, cap: 'round' });
  });

  // points of interest first (they sit around the buildings): benches, trees,
  // the fountain, the shade under the stadium's east wing — each with a little
  // volume, so the world has things in it, not just labelled dots.
  gPlaces.clear();
  labelLayer.removeChildren();
  (WORLD.pois || []).forEach(p => { const [cx, cy] = project(p.x, p.y); drawPoiProp(gPlaces, p.kind, cx, cy); });

  // buildings: proper isometric volumes (walls + roof), sorted back-to-front.
  const locs = WORLD.locations.slice().sort((a, b) => (a.x + a.y) - (b.x + b.y));
  locs.forEach(l => {
    const [cx, cy] = project(l.x, l.y);
    const isWater = /river|bridge/.test(l.id);
    const isOak = /oak/.test(l.id);
    if (isWater) {
      const r = 22 * FIT.s + 8;
      gPlaces.poly([cx, cy - r * 0.5, cx + r, cy, cx, cy + r * 0.5, cx - r, cy]).fill(C.water);
      gPlaces.poly([cx, cy - r * 0.5, cx + r, cy, cx, cy + r * 0.5, cx - r, cy]).fill({ color: 0x8fd8e0, alpha: 0.25 });
    } else if (isOak) {
      tree(gPlaces, cx, cy, 26 * FIT.s + 12);
    } else {
      const w = (l.home ? 15 : 24) * FIT.s + 7;
      const h = (l.home ? 20 : 30) * FIT.s + 9;
      const walls = l.home ? 0xece0c4 : 0xeef0ee;
      const roof = l.home ? 0xc65a3a : (/stadium/.test(l.id) ? 0x566270 : 0xb5613f);
      isoBuilding(gPlaces, cx, cy, w, w * 0.55, h, walls, roof);
    }
    const t = new PIXI.Text({ text: l.name, style: { fontFamily: 'system-ui', fontSize: 11,
      fill: 0x2f4a2a, fontWeight: '500' } });
    t.anchor.set(0.5, 0); t.x = cx; t.y = cy + 14 * FIT.s + 4; t.alpha = 0.85;
    labelLayer.addChild(t);
  });
}

// an isometric cuboid: bottom diamond at (cx,cy), raised by h, two front faces + top.
function isoPrism(g, cx, cy, rx, ry, h, colTop, colL, colR) {
  g.poly([cx - rx, cy, cx, cy + ry, cx, cy + ry - h, cx - rx, cy - h]).fill(colL);      // left front
  g.poly([cx + rx, cy, cx, cy + ry, cx, cy + ry - h, cx + rx, cy - h]).fill(colR);      // right front
  g.poly([cx, cy - ry - h, cx + rx, cy - h, cx, cy + ry - h, cx - rx, cy - h]).fill(colTop); // top
}
function isoBuilding(g, cx, cy, rx, ry, h, walls, roof) {
  const wl = shade(walls, -0.14), wr = shade(walls, 0.06);
  // walls
  g.poly([cx - rx, cy, cx, cy + ry, cx, cy + ry - h, cx - rx, cy - h]).fill(wl);
  g.poly([cx + rx, cy, cx, cy + ry, cx, cy + ry - h, cx + rx, cy - h]).fill(wr);
  // roof: a raised pyramid-ish cap over the top diamond
  const rh = h * 0.5;
  g.poly([cx - rx, cy - h, cx, cy + ry - h, cx, cy + ry - h - rh, cx - rx, cy - h - rh]).fill(shade(roof, -0.1));
  g.poly([cx + rx, cy - h, cx, cy + ry - h, cx, cy + ry - h - rh, cx + rx, cy - h - rh]).fill(shade(roof, 0.05));
  g.poly([cx, cy - ry - h - rh, cx + rx, cy - h - rh, cx, cy + ry - h - rh, cx - rx, cy - h - rh]).fill(roof);
}

function tree(g, cx, cy, r) {
  g.rect(cx - r * 0.08, cy - r * 0.5, r * 0.16, r * 0.5).fill(0x7a5a3a);
  if (SEASON.bare) {
    g.moveTo(cx, cy - r * 0.2).lineTo(cx - r * 0.3, cy - r * 0.72).stroke({ width: 2, color: 0x6a4a33 });
    g.moveTo(cx, cy - r * 0.3).lineTo(cx + r * 0.28, cy - r * 0.76).stroke({ width: 2, color: 0x6a4a33 });
    g.ellipse(cx, cy - r * 0.55, r * 0.5, r * 0.34).fill({ color: 0xeef2f4, alpha: 0.5 }); // dusting of snow
    return;
  }
  g.ellipse(cx, cy - r * 0.55, r * 0.7, r * 0.5).fill(SEASON.canopy[0]);
  g.ellipse(cx - r * 0.22, cy - r * 0.75, r * 0.42, r * 0.34).fill(SEASON.canopy[1]);
  g.ellipse(cx + r * 0.2, cy - r * 0.68, r * 0.36, r * 0.3).fill(SEASON.canopy[2]);
  if (SEASON.blossom) { for (let i = 0; i < 6; i++) { const a = i * 1.05; g.circle(cx + Math.cos(a) * r * 0.5, cy - r * 0.6 + Math.sin(a) * r * 0.3, r * 0.06).fill(0xf2b8d0); } }
  if (SEASON.snow) { g.ellipse(cx, cy - r * 0.82, r * 0.5, r * 0.18).fill({ color: 0xffffff, alpha: 0.6 }); }
}

function drawPoiProp(g, kind, cx, cy) {
  const s = FIT.s;
  if (kind === 'tree') { tree(g, cx, cy, 16 * s + 8); return; }
  if (kind === 'bench') { isoPrism(g, cx, cy, 9 * s + 4, 5 * s + 2, 4 * s + 2, 0xb5834a, 0x8a5f34, 0xa5763f); return; }
  if (kind === 'fountain') {
    isoPrism(g, cx, cy, 8 * s + 4, 4 * s + 2, 4 * s + 2, 0xd8d2c4, 0xb7b09e, 0xc9c2b2);
    g.ellipse(cx, cy - 4 * s - 2, 6 * s + 3, 3 * s + 1.5).fill(0x5fc0cc); return;
  }
  if (kind === 'stall') {
    isoPrism(g, cx, cy, 9 * s + 4, 5 * s + 2, 5 * s + 3, 0xc65a3a, 0x9c4630, 0xb5533a);
    g.poly([cx - 11 * s - 4, cy - 5 * s - 3, cx, cy - 9 * s - 5, cx + 11 * s + 4, cy - 5 * s - 3]).fill({ color: 0xeef0ee, alpha: 0.9 }); return;
  }
  if (kind === 'wing') { isoPrism(g, cx, cy, 14 * s + 6, 7 * s + 3, 3 * s + 2, 0x6d7a86, 0x4c5661, 0x5c6773); return; }
  if (kind === 'den') { g.ellipse(cx, cy, 9 * s + 4, 5 * s + 2).fill(0x4a3f34); g.ellipse(cx, cy - 1, 6 * s + 2, 3 * s + 1).fill(0x2f281f); return; }
  if (kind === 'verge') { g.ellipse(cx, cy, 12 * s + 5, 5 * s + 2).fill(0x66bd53); return; }
  // nook / default: a small doorway block
  isoPrism(g, cx, cy, 6 * s + 3, 3 * s + 1.5, 5 * s + 3, 0xd8c6a0, 0xb49a70, 0xc7b487);
}

// shade a colour toward black (t<0) or white (t>0)
function shade(c, t) {
  const r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
  const to = t < 0 ? 0 : 255, k = Math.abs(t);
  return ((r + (to - r) * k) << 16 | (g + (to - g) * k) << 8 | (b + (to - b) * k)) & 0xffffff;
}

// ------------------------------------------------------------------- actors
function drawActors(ents) {
  gActors.clear();
  // conversation partners drawn as a soft link, first
  const handled = new Set();
  ents.forEach(e => {
    if (e.pose === 'talk' && e.partner && !handled.has(e.id)) {
      const p = ents.find(o => o.id === e.partner);
      if (p) {
        const [ax, ay] = project(e.x, e.y), [bx, by] = project(p.x, p.y);
        gActors.moveTo(ax, ay - 10).lineTo(bx, by - 10)
          .stroke({ width: 2, color: 0xffffff, alpha: 0.5 });
        const mx = (ax + bx) / 2, my = (ay + by) / 2 - 16;
        const t = (tms / 320) % 3;
        for (let i = 0; i < 3; i++) {
          const pp = (t + i) % 3;
          gActors.circle(mx + (i - 1) * 3, my - pp * 3, 1.4).fill({ color: 0xfff3d6, alpha: 0.35 + 0.25 * (2 - pp) });
        }
        handled.add(e.id); handled.add(p.id);
      }
    }
  });

  // depth sort: nearer (greater x+y) draws later / on top
  const order = ents.map((e, i) => i).sort((a, b) => (ents[a].x + ents[a].y) - (ents[b].x + ents[b].y));
  order.forEach(i => drawFigure(ents[i]));
}

function drawFigure(e) {
  const meta = ROSTER[e.id] || { color: '#888', kind: 'resident', name: e.id };
  const kind = meta.kind;
  const [x, y0] = project(e.x, e.y);
  const T = tms / 1000, sd = seedOf(e.id);
  const isRes = kind === 'resident';
  const dog = kind === 'dog';
  const small = kind === 'fox' || kind === 'cat' || kind === 'hedgehog';
  const bird = kind === 'crow' || kind === 'owl' || kind === 'heron';

  // base figure metrics
  let bodyH = isRes ? 22 : dog ? 11 : small ? 9 : 8;
  let bodyW = isRes ? 12 : dog ? 16 : 11;
  bodyH *= FIT.s * 1.1 + 0.55; bodyW *= FIT.s * 1.1 + 0.55;

  // --- disposition shapes the body (residents) ---
  let headDrop = 0, lean = 0, widen = 1, bounceScale = 1, tint = null;
  if (isRes) {
    const rd = readiness(e);                     // ~ -7..8
    const openness = Math.max(-1, Math.min(1, rd / 6));
    headDrop = openness < 0 ? -openness * bodyH * 0.16 : -openness * bodyH * 0.05; // low mood → head down
    widen = 1 + openness * 0.16;                 // open stance vs closed
    bounceScale = 0.55 + energyOf(e) * 0.9;      // energy → springier gait
    // mood tints the body subtly warm (up) or cool (down)
    const m = moodOf(e);
    tint = m >= 0 ? mix(hex(meta.color), 0xffe6b0, m * 0.28) : mix(hex(meta.color), 0x6d7a86, -m * 0.30);
  }
  const col = tint != null ? tint : hex(meta.color);

  // --- per-pose motion (behaviour → body) ---
  let dx = 0, dy = 0, hb = 0;
  if (e.pose === 'walk') { const b = Math.sin(T * 9 + sd * 6) * (0.7 + (e.spd || 0.3) * 2.5) * bounceScale; hb = -Math.abs(b) * 1.1; dx = b * 0.2; }
  else if (e.pose === 'talk') { lean += Math.sin(T * 2.2 + sd * 6) * 1.4; if (e.gest === 'laugh') hb = -Math.abs(Math.sin(T * 11)) * 2.2; }
  else if (e.pose === 'work') { const w = Math.sin(T * 3 + sd * 6); dx = w * 2.0; }
  else if (e.pose === 'sit') { dy = bodyH * 0.28; bodyH *= 0.7; }
  else if (e.pose === 'stand' || e.pose === 'alert') { dx = Math.sin(T * 0.8 + sd) * 1.1 * bounceScale; hb = Math.sin(T * 1.4 + sd) * 0.8; }
  else if (e.pose === 'forage' || e.pose === 'sniff') { dy = Math.abs(Math.sin(T * 3.2 + sd * 6)) * 2.2; }
  else if (e.pose === 'play') { dx = (Math.sin(T * 2.1 + sd * 6) + Math.sin(T * 3.7 + sd * 3)) * 6; dy = -(Math.abs(Math.sin(T * 3.1 + sd))) * 6; }
  else if (e.pose === 'lie' || e.pose === 'perch') { bodyH *= 0.5; }

  const px = x + dx, base = y0 + dy;

  // shadow
  gActors.ellipse(px, base + 1, bodyW * 0.7 * widen, bodyW * 0.32).fill({ color: 0x1a3a12, alpha: 0.18 });

  // hover ring
  if (e.id === hoverId) gActors.circle(px, base - bodyH * 0.5, Math.max(bodyW, bodyH) * 0.8).stroke({ width: 2, color: 0xffffff, alpha: 0.9 });

  if (bird) {
    // little wing chevron
    gActors.moveTo(px - 6, base).lineTo(px, base - 5).lineTo(px + 6, base).stroke({ width: 2.4, color: col });
  } else if (dog || small) {
    // low rounded body + head
    gActors.roundRect(px - bodyW * 0.5, base - bodyH * 0.9 + hb, bodyW, bodyH * 0.8, bodyH * 0.3).fill(col);
    gActors.circle(px + Math.cos(e.h) * bodyW * 0.5, base - bodyH * 0.9 + hb, bodyH * 0.35).fill(col);
  } else {
    // resident: body capsule + head, posture from disposition
    const topY = base - bodyH + hb;
    gActors.roundRect(px - bodyW * 0.5 * widen, topY + bodyH * 0.32, bodyW * widen, bodyH * 0.68, bodyW * 0.42).fill(col);
    // head
    const hx = px + lean * 0.6, hy = topY + headDrop + bodyH * 0.16;
    gActors.circle(hx, hy, bodyW * 0.42).fill(mix(col, 0xffffff, 0.06));
    // facing nub
    gActors.circle(hx + Math.cos(e.h) * bodyW * 0.5, hy + Math.sin(e.h) * bodyW * 0.28, 1.8).fill({ color: 0xffffff, alpha: 0.85 });
    // what they've got on — the possessions layer (coat, scarf, hat, umbrella…)
    const worn = e.worn || [];
    if (worn.length) {
      const neckY = hy + bodyW * 0.5;
      if (worn.includes('coat')) gActors.roundRect(px - bodyW * 0.5 * widen, topY + bodyH * 0.34, bodyW * widen, bodyH * 0.44, bodyW * 0.34).fill(shade(col, -0.2));
      if (worn.includes('club_scarf')) gActors.rect(hx - bodyW * 0.4, neckY, bodyW * 0.8, 2.6).fill(0xd1495b);
      else if (worn.includes('scarf')) gActors.rect(hx - bodyW * 0.4, neckY, bodyW * 0.8, 2.6).fill(hex(meta.color));
      if (worn.includes('sunhat')) gActors.ellipse(hx, hy - bodyW * 0.36, bodyW * 0.58, bodyW * 0.2).fill(0xe8d9a0);
      else if (worn.includes('cap')) gActors.ellipse(hx, hy - bodyW * 0.34, bodyW * 0.46, bodyW * 0.2).fill(0x5a7d86);
      if (worn.includes('umbrella')) { gActors.rect(hx - 0.6, hy - bodyW * 1.05, 1.2, bodyW * 0.95).fill(0x555555); gActors.ellipse(hx, hy - bodyW * 1.05, bodyW * 0.85, bodyW * 0.34).fill(0x3d84a8); }
      if (worn.includes('basket') || worn.includes('satchel')) gActors.circle(px + bodyW * 0.55 * widen, base - bodyH * 0.42, 2.6).fill(0xb5834a);
      if (worn.includes('flower')) gActors.circle(hx + bodyW * 0.42, hy, 1.8).fill(0xe36a9a);
    }
    // gesture spark
    if (e.pose === 'talk') gActors.arc(hx, hy - bodyW * 0.7, 3 + Math.sin(T * 4 + sd * 6) * 1.3, Math.PI * 0.1, Math.PI * 0.9).stroke({ width: 1.4, color: 0xffe6b0, alpha: 0.9 });
  }

  // name label for residents (persistent Text object, positioned each frame)
  if (isRes) {
    let t = labels[e.id];
    if (!t) { t = new PIXI.Text({ text: meta.name, style: { fontFamily: 'system-ui', fontSize: 10.5, fill: 0x22371a } }); t.anchor.set(0.5, 1); labelLayer.addChild(t); labels[e.id] = t; }
    t.x = px; t.y = base - bodyH - 6 + hb; t.alpha = 0.9;
  }
}

// tiny colour helpers
function hex(s) { return typeof s === 'number' ? s : parseInt(String(s).replace('#', ''), 16); }
function mix(a, b, t) {
  a = hex(a); b = hex(b); t = Math.max(0, Math.min(1, t));
  const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255;
  const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255;
  return ((ar + (br - ar) * t) << 16 | (ag + (bg - ag) * t) << 8 | (ab + (bb - ab) * t)) & 0xffffff;
}

// ----------------------------------------------------------------- weather
function drawWeather(fr) {
  gWeather.clear();
  const w = fr.weather || { sky: 'clear' }, sky = w.sky;
  const W = app.screen.width, H = app.screen.height;
  let veil = 0, veilColor = 0x3a4653;
  if (sky === 'cloudy') veil = 0.06;
  else if (sky === 'overcast') veil = 0.14;
  else if (sky === 'fog') { veil = 0.26; veilColor = 0xdfe6ea; }
  else if (sky === 'rain') veil = 0.18;
  else if (sky === 'snow') { veil = 0.12; veilColor = 0xeaf2f6; }
  if (veil > 0) gWeather.rect(0, 0, W, H).fill({ color: veilColor, alpha: veil });
  const t = tms / 1000;
  if (sky === 'rain') {
    for (let i = 0; i < 90; i++) { const x = (i * 137.5 + t * 620) % W; const y = (i * 89.3 + t * 900) % H; gWeather.moveTo(x, y).lineTo(x - 4, y + 12).stroke({ width: 1, color: 0xbfd8e8, alpha: 0.5 }); }
  } else if (sky === 'snow') {
    for (let i = 0; i < 70; i++) { const x = (i * 151.3 + Math.sin(t * 0.6 + i) * 22) % W; const y = (i * 73.1 + t * 90) % H; gWeather.circle(x, y, 1.7).fill({ color: 0xffffff, alpha: 0.85 }); }
  }
}

// --------------------------------------------------------------------- HUD
const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : s);
function renderHud(fr) {
  $('hh').textContent = pad(fr.hour) + ':' + pad(fr.minute);
  $('wd').textContent = fr.weekday;
  $('day').textContent = fr.day;
  $('phase').textContent = fr.phase;
  if (fr.weather) { const w = fr.weather; $('wx').textContent = `${fr.season} · ${cap(w.sky)}${w.windy ? ', windy' : ''} · ${w.temp}`; }
}

// -------------------------------------------------------------------- loop
let lastHudTick = -1;
function loop(ticker) {
  const now = ticker.lastTime !== undefined ? ticker.lastTime : performance.now();
  tms = now;
  if (last === null) last = now;
  const dt = (now - last) / 1000; last = now;
  if (playing) {
    acc += dt * BASE_TPS * speed;
    let guard = 0;
    while (acc >= 1 && guard < 240) { eng.tick(); prev = cur; cur = JSON.parse(eng.snapshot_json()); acc -= 1; guard++; }
  }
  const f = playing ? Math.min(acc, 1) : 0;
  const ents = lerpEntities(prev, cur, f);
  // re-dress the static scene when the season turns
  if (cur.season !== lastSeason) { SEASON = SEASONS[cur.season] || SEASON; lastSeason = cur.season; drawStatic(); }
  drawActors(ents);
  drawWeather(cur);
  if (cur.tick !== lastHudTick) { renderHud(cur); lastHudTick = cur.tick; }
}

main().catch(err => {
  const l = $('loading'); if (l) l.textContent = 'Failed to start: ' + err;
  console.error(err);
});
