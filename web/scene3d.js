// ERA — the town in true 3D perspective. The same deterministic Rust engine
// (compiled to WASM) ticks here; this renderer observes its behaviour stream and
// draws the town with a real perspective camera — so distance is real: far things
// are smaller and hazed into a genuine horizon, exactly the natural view. The
// simulation is untouched; only the camera changed from the flat isometric slice.
//
// Placeholder blocks and figures — this proves the perspective view and the
// pipeline. Real 3D/rigged assets (Blender → glTF, or billboards) come later.

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import init, { WasmEngine } from './pkg/era_first_breath.js';

const S = 0.12, CX = 500 * S, CZ = 430 * S;           // world→scene scale + centre
const w2s = (x, y) => [x * S - CX, y * S - CZ];        // (world x,y) → scene (X,Z)

// ---- day/night lighting keyframes (hour → colours & intensities) ----
const LKF = [
  { h: 0, sky: 0x0e1732, sun: 0x24345e, sunI: 0.05, hemi: 0.18, amb: 0x0a1330 },
  { h: 6, sky: 0xe7b088, sun: 0xffd9a0, sunI: 0.55, hemi: 0.5, amb: 0x40384e },
  { h: 12, sky: 0xbfe0ea, sun: 0xfff6e0, sunI: 1.15, hemi: 0.95, amb: 0x9fb8c0 },
  { h: 18, sky: 0xe89055, sun: 0xff9a55, sunI: 0.6, hemi: 0.55, amb: 0x6a5a6a },
  { h: 20.5, sky: 0x3f3766, sun: 0x3a3a6a, sunI: 0.12, hemi: 0.22, amb: 0x241f40 },
  { h: 24, sky: 0x0e1732, sun: 0x24345e, sunI: 0.05, hemi: 0.18, amb: 0x0a1330 },
];
function lerpColor(a, b, f) { return new THREE.Color(a).lerp(new THREE.Color(b), f); }
function lightingAt(t) {
  let a = LKF[0], b = LKF[LKF.length - 1];
  for (let i = 0; i < LKF.length - 1; i++) if (t >= LKF[i].h && t <= LKF[i + 1].h) { a = LKF[i]; b = LKF[i + 1]; break; }
  const f = (t - a.h) / Math.max(0.001, b.h - a.h);
  return { sky: lerpColor(a.sky, b.sky, f), sun: lerpColor(a.sun, b.sun, f), sunI: a.sunI + (b.sunI - a.sunI) * f, hemi: a.hemi + (b.hemi - a.hemi) * f, amb: lerpColor(a.amb, b.amb, f) };
}

// ---- greater-town fabric (mirrors the slice's layout, in world coords) ----
const EX0 = -260, EX1 = 1260, EY0 = -170, EY1 = 1010, GAP = 190;
const RIVER = [[735, 150], [565, 300], [470, 470], [430, 600], [300, 760], [110, 905]];
// clay-diorama palette (Roy's reference): cream walls, terracotta roofs.
const wallPal = [0xf1e7d2, 0xefe3cc, 0xeaddc3, 0xf3ecdb, 0xe7dcc6];
const roofPal = [0xd9743f, 0xcf6838, 0xc65a3a, 0xdc8a4a, 0xcb6a3c];

let renderer, scene, camera, sun, hemi, amb, cloudGroup, composer, bokeh;
let eng, WORLD, prev = null, cur = null;
const ROSTER = {}, people = {}, lastPos = {};
let playing = true, speed = 1, acc = 0, last = null, tms = 0;
const BASE_TPS = 7 / 6;
const orbit = { az: 0.7, pol: 1.12, rad: 60, tx: 0, ty: 4, tz: 0 };   // close & low — the hero fills the frame

const $ = id => document.getElementById(id);
const pad = n => String(n).padStart(2, '0');
const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : s);

function box(w, h, d, color) {
  const r = Math.max(0.05, Math.min(w, h, d) * 0.16);          // soft clay edges
  return new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 2, r), new THREE.MeshStandardMaterial({ color, roughness: 0.92, metalness: 0 }));
}
function near(x, y, list, d) { return list.some(([nx, ny]) => Math.hypot(nx - x, ny - y) < d); }

function buildTown() {
  const town = new THREE.Group();
  const nodes = WORLD.locations.map(l => [l.x, l.y]);

  // ground
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(900, 900), new THREE.MeshStandardMaterial({ color: 0x8fae52, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; town.add(ground);

  buildStreets(town);   // roads with sidewalks, markings, trees, lamps and cars

  // river — a low blue ribbon of segments
  for (let i = 0; i < RIVER.length - 1; i++) {
    const [x1, y1] = w2s(...RIVER[i]), [x2, y2] = w2s(...RIVER[i + 1]);
    const mx = (x1 + x2) / 2, mz = (y1 + y2) / 2, len = Math.hypot(x2 - x1, y2 - y1);
    const r = box(len + 3, 0.2, 4.2, 0x3fc6d0); r.position.set(mx, 0.1, mz);
    r.rotation.y = -Math.atan2(y2 - y1, x2 - x1); town.add(r);
  }

  // filler blocks (skip near the real places and the river)
  let s = 987654321; const rnd = () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
  for (let x = EX0 + GAP * 0.5; x < EX1; x += GAP) for (let y = EY0 + GAP * 0.5; y < EY1; y += GAP) {
    const n = 1 + Math.floor(rnd() * 3);
    for (let k = 0; k < n; k++) {
      const bx = x + (rnd() - 0.5) * GAP * 0.6, by = y + (rnd() - 0.5) * GAP * 0.6;
      if (near(bx, by, nodes, 120) || near(bx, by, RIVER, 95)) continue;
      const h = 1.6 + rnd() * 5.5, [sx, sz] = w2s(bx, by);
      const b = box(2 + rnd() * 1.6, h, 2 + rnd() * 1.6, wallPal[(s >>> 3) % wallPal.length]); b.position.set(sx, h / 2, sz); town.add(b);
      const roof = box(2.3, 0.5, 2.3, roofPal[(s >>> 7) % roofPal.length]); roof.position.set(sx, h + 0.25, sz); town.add(roof);
    }
  }

  // the twelve real places — distinct landmarks
  WORLD.locations.forEach(l => {
    const [sx, sz] = w2s(l.x, l.y);
    if (l.id === 'loc_main_square') {
      const plaza = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 0.2, 40), new THREE.MeshLambertMaterial({ color: 0xd8d2c4 })); plaza.position.set(sx, 0.1, sz); town.add(plaza);
      const isle = new THREE.Mesh(new THREE.CylinderGeometry(2, 2, 0.25, 24), new THREE.MeshLambertMaterial({ color: 0x9aa86a })); isle.position.set(sx, 0.15, sz); town.add(isle);
      const mon = box(0.5, 4, 0.5, 0xe8e2d4); mon.position.set(sx, 2, sz); town.add(mon);
    } else if (l.id === 'loc_stadium') {
      const stands = new THREE.Mesh(new THREE.CylinderGeometry(8, 9, 3.2, 36, 1, true), new THREE.MeshLambertMaterial({ color: 0x9aa0a6, side: THREE.DoubleSide })); stands.position.set(sx, 1.6, sz); town.add(stands);
      const pitch = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 0.2, 36), new THREE.MeshLambertMaterial({ color: 0x57ab46 })); pitch.position.set(sx, 0.15, sz); town.add(pitch);
    } else if (/oak/.test(l.id)) {
      const trunk = box(0.5, 2, 0.5, 0x7a5a3a); trunk.position.set(sx, 1, sz); town.add(trunk);
      const crown = new THREE.Mesh(new THREE.SphereGeometry(2.4, 12, 10), new THREE.MeshLambertMaterial({ color: 0x3f8a30 })); crown.position.set(sx, 3.2, sz); town.add(crown);
    } else if (l.id === 'loc_bridge' || l.id === 'loc_riverside') {
      const b = box(3.5, 0.4, 3.5, 0xcbb98f); b.position.set(sx, 0.3, sz); town.add(b);
    } else {
      const h = l.home ? 3 : 5;
      const b = box(3.2, h, 3.2, l.home ? 0xece0c4 : 0xeef0ee); b.position.set(sx, h / 2, sz); town.add(b);
      const roof = box(3.6, 0.6, 3.6, l.home ? 0xc65a3a : 0xb5613f); roof.position.set(sx, h + 0.3, sz); town.add(roof);
    }
  });
  town.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });   // soft clay shadows
  scene.add(town);
}

function streetTree(x, z) {
  const g = new THREE.Group();
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.17, 1.4, 6), new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 1 })); tr.position.y = 0.7; g.add(tr);
  const cr = new THREE.Mesh(new THREE.SphereGeometry(0.95, 10, 8), new THREE.MeshStandardMaterial({ color: 0x7fae3a, roughness: 1 })); cr.position.y = 2.0; cr.scale.y = 1.15; g.add(cr);
  g.position.set(x, 0, z); return g;
}
function lamp(x, z) {
  const g = new THREE.Group();
  const p = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 2.3, 6), new THREE.MeshStandardMaterial({ color: 0x2a2a2e })); p.position.y = 1.15; g.add(p);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 6), new THREE.MeshStandardMaterial({ color: 0xffd27a, emissive: 0xffb347, emissiveIntensity: 0.8 })); head.position.y = 2.3; g.add(head);
  g.position.set(x, 0, z); return g;
}
function car(x, z, ang, color) { const b = box(1.7, 0.55, 0.85, color); b.position.set(x, 0.35, z); b.rotation.y = ang; return b; }

function buildStreets(town) {
  const roadMat = new THREE.MeshStandardMaterial({ color: 0x41454b, roughness: 1 });
  const walkMat = new THREE.MeshStandardMaterial({ color: 0xd8d0be, roughness: 1 });
  const lineMat = new THREE.MeshStandardMaterial({ color: 0xe8e2d0, roughness: 1 });
  const carCols = [0xd1495b, 0xe0a24a, 0x3d84a8, 0xeeeeee, 0x33363a, 0x5fa85a, 0xe8c34a];
  const lines = [];
  for (let x = EX0; x <= EX1; x += GAP) lines.push([x, EY0, x, EY1]);
  for (let y = EY0; y <= EY1; y += GAP) lines.push([EX0, y, EX1, y]);
  let cs = 42; const rnd = () => { cs = (Math.imul(cs, 1664525) + 1013904223) >>> 0; return cs / 4294967296; };
  lines.forEach(([x1, y1, x2, y2]) => {
    const [ax, az] = w2s(x1, y1), [bx, bz] = w2s(x2, y2);
    const mx = (ax + bx) / 2, mz = (az + bz) / 2, len = Math.hypot(bx - ax, bz - az), ang = -Math.atan2(bz - az, bx - ax);
    const dirx = (bx - ax) / len, dirz = (bz - az) / len, px_ = -dirz, pz_ = dirx;
    const walk = new THREE.Mesh(new THREE.BoxGeometry(len, 0.12, 4.6), walkMat); walk.position.set(mx, 0.06, mz); walk.rotation.y = ang; town.add(walk);
    const road = new THREE.Mesh(new THREE.BoxGeometry(len, 0.14, 2.7), roadMat); road.position.set(mx, 0.08, mz); road.rotation.y = ang; town.add(road);
    const n = Math.max(1, Math.floor(len / 3));                       // dashed centreline
    for (let i = 0; i < n; i++) { const t = (i + 0.5) / n, cx = ax + (bx - ax) * t, cz = az + (bz - az) * t; const d = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.02, 0.14), lineMat); d.position.set(cx, 0.17, cz); d.rotation.y = ang; town.add(d); }
    for (let d = 9; d < len - 9; d += 15) {                            // trees & lamps along the kerb
      const side = rnd() < 0.5 ? 1 : -1, wx = ax + dirx * d + px_ * 2.8 * side, wz = az + dirz * d + pz_ * 2.8 * side;
      town.add(rnd() < 0.55 ? streetTree(wx, wz) : lamp(wx, wz));
    }
    for (let c = 0; c < 2; c++) { const d = 9 + rnd() * (len - 18); town.add(car(ax + dirx * d + px_ * 0.65, az + dirz * d + pz_ * 0.65, ang, carCols[(cs >>> 3) % carCols.length])); }
  });
}

function makePerson(e) {
  const g = new THREE.Group();
  const col = new THREE.Color(e.color || '#888888');
  const kind = e.kind;
  if (kind === 'resident') {
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.44, 1.3, 10), new THREE.MeshLambertMaterial({ color: col })); body.position.y = 0.65; g.add(body);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 12, 10), new THREE.MeshLambertMaterial({ color: 0xdcae82 })); head.position.y = 1.55; g.add(head);
  } else if (kind === 'dog') {
    const b = box(1.1, 0.5, 0.5, col); b.position.y = 0.3; g.add(b);
    const h = new THREE.Mesh(new THREE.SphereGeometry(0.32, 10, 8), new THREE.MeshLambertMaterial({ color: col })); h.position.set(0.55, 0.5, 0); g.add(h);
  } else {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), new THREE.MeshLambertMaterial({ color: col })); b.position.y = 0.3; g.add(b);
  }
  scene.add(g); return g;
}

function updateCamera() {
  const { az, pol, rad, tx, ty, tz } = orbit;
  camera.position.set(tx + rad * Math.sin(pol) * Math.sin(az), ty + rad * Math.cos(pol), tz + rad * Math.sin(pol) * Math.cos(az));
  camera.lookAt(tx, ty, tz);
}

function lerpEntities(a, b, f) {
  const m = {}; b.entities.forEach(e => m[e.id] = e);
  return a.entities.map(e => { const o = m[e.id] || e; return { ...e, x: e.x + (o.x - e.x) * f, y: e.y + (o.y - e.y) * f }; });
}

function frame(ts) {
  if (last === null) last = ts; const dt = Math.min(0.05, (ts - last) / 1000); last = ts; tms = ts;
  if (playing) { acc += dt * BASE_TPS * speed; let g = 0; while (acc >= 1 && g < 240) { eng.tick(); prev = cur; cur = JSON.parse(eng.snapshot_json()); acc -= 1; g++; } }
  const f = playing ? Math.min(acc, 1) : 0;
  const ents = lerpEntities(prev, cur, f);

  // lighting by the clock
  const L = lightingAt((cur.hour + cur.minute / 60) % 24);
  scene.background = L.sky; scene.fog.color = L.sky;
  hemi.color = L.sky; hemi.intensity = L.hemi; amb.color = L.amb; sun.color = L.sun; sun.intensity = L.sunI;
  const sa = ((cur.hour + cur.minute / 60) / 24) * Math.PI * 2;
  sun.position.set(Math.cos(sa) * 80, Math.max(6, Math.sin(sa) * 80), 40);

  // people
  ents.forEach(e => {
    let g = people[e.id]; if (!g) { g = people[e.id] = makePerson(ROSTER[e.id] || { color: '#888', kind: 'resident' }); }
    const [X, Z] = w2s(e.x, e.y);
    const lp = lastPos[e.id];
    let bob = 0;
    if (lp) { const dx = X - lp[0], dz = Z - lp[1]; if (dx * dx + dz * dz > 1e-5) g.rotation.y = Math.atan2(dx, dz); if (e.pose === 'walk') bob = Math.abs(Math.sin(ts / 130 + e.x)) * 0.12; }
    lastPos[e.id] = [X, Z];
    g.position.set(X, bob, Z);
  });

  // clouds drift
  if (cloudGroup) cloudGroup.position.x = ((ts / 1000 * 1.2) % 120) - 60;

  if (cur.tick !== frame._t) { renderHud(cur); frame._t = cur.tick; }
  if (bokeh) bokeh.uniforms['focus'].value = orbit.rad;   // keep focus on the hero (camera→target)
  composer.render();
  requestAnimationFrame(frame);
}

function renderHud(fr) {
  $('hh').textContent = pad(fr.hour) + ':' + pad(fr.minute);
  $('wd').textContent = fr.weekday; $('day').textContent = fr.day;
  if (fr.weather) $('wx').textContent = `${fr.season} · ${cap(fr.weather.sky)}`;
}

async function main() {
  await init();
  eng = new WasmEngine(0);
  WORLD = JSON.parse(eng.world_json());
  WORLD.entities.forEach(e => ROSTER[e.id] = e);
  cur = JSON.parse(eng.snapshot_json()); prev = cur;

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  $('app').appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe0ea);
  scene.fog = new THREE.Fog(0xbfe0ea, 55, 240);          // depth haze → the horizon
  camera = new THREE.PerspectiveCamera(33, window.innerWidth / window.innerHeight, 0.5, 800);

  hemi = new THREE.HemisphereLight(0xbfe0ea, 0x6a5a3a, 0.9); scene.add(hemi);
  amb = new THREE.AmbientLight(0xbfae90, 0.35); scene.add(amb);
  sun = new THREE.DirectionalLight(0xfff0d2, 1.15); sun.position.set(60, 80, 40); scene.add(sun);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004;
  { const c = sun.shadow.camera; c.left = -75; c.right = 75; c.top = 75; c.bottom = -75; c.near = 1; c.far = 320; }

  buildTown();

  // a few soft clouds high up
  cloudGroup = new THREE.Group();
  for (let i = 0; i < 7; i++) {
    const c = new THREE.Mesh(new THREE.SphereGeometry(4 + Math.random() * 4, 8, 6), new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.75 }));
    c.position.set(-60 + i * 22, 34 + (i % 3) * 5, -40 - (i % 4) * 18); c.scale.y = 0.5; cloudGroup.add(c);
  }
  scene.add(cloudGroup);

  // macro depth of field — the hero sharp, the rest melting to blur (tilt-shift).
  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  bokeh = new BokehPass(scene, camera, { focus: orbit.rad, aperture: 0.0016, maxblur: 0.012 });
  composer.addPass(bokeh);
  composer.addPass(new OutputPass());

  updateCamera();
  bindControls();
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer && composer.setSize(window.innerWidth, window.innerHeight);
  });
  $('loading').remove();
  renderHud(cur);
  requestAnimationFrame(frame);
}

function bindControls() {
  const el = renderer.domElement; let dragging = false, lx = 0, ly = 0;
  el.addEventListener('pointerdown', e => { dragging = true; lx = e.clientX; ly = e.clientY; });
  window.addEventListener('pointerup', () => dragging = false);
  window.addEventListener('pointermove', e => { if (!dragging) return; orbit.az -= (e.clientX - lx) * 0.005; orbit.pol = Math.max(0.35, Math.min(1.4, orbit.pol - (e.clientY - ly) * 0.004)); lx = e.clientX; ly = e.clientY; updateCamera(); });
  el.addEventListener('wheel', e => { e.preventDefault(); orbit.rad = Math.max(35, Math.min(240, orbit.rad * (1 + Math.sign(e.deltaY) * 0.08))); updateCamera(); }, { passive: false });
  $('play').onclick = e => { playing = !playing; e.target.textContent = playing ? 'Pause' : 'Play'; };
  document.querySelectorAll('[data-mul]').forEach(b => b.onclick = () => { speed = +b.dataset.mul; document.querySelectorAll('[data-mul]').forEach(x => x.classList.toggle('on', x === b)); });
}

main().catch(err => { const l = $('loading'); if (l) l.textContent = 'Failed to start: ' + err; console.error(err); });
