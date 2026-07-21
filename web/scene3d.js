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
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// The WASM engine is imported dynamically in main() — plate mode renders the
// static world (world.json) and never loads the sim at all.

const S = 0.12, CX = 500 * S, CZ = 430 * S;           // world→scene scale + centre
const w2s = (x, y) => [x * S - CX, y * S - CZ];        // (world x,y) → scene (X,Z)

// ---- day/night lighting keyframes (hour → colours & intensities) ----
// summer-ish day: dawn ~5:20, dusk ~19:20, bright at noon.
const LKF = [
  { h: 0, sky: 0x0e1732, sun: 0x24345e, sunI: 0.05, hemi: 0.18, amb: 0x0a1330 },
  { h: 4.6, sky: 0x1b2a4c, sun: 0x2a3a66, sunI: 0.06, hemi: 0.22, amb: 0x14203c },
  { h: 5.4, sky: 0xe7b088, sun: 0xffd9a0, sunI: 0.42, hemi: 0.46, amb: 0x40384e },
  { h: 8, sky: 0xbfe0ea, sun: 0xfff0d2, sunI: 1.0, hemi: 0.82, amb: 0x9fb8c0 },
  { h: 12, sky: 0xc2e8f0, sun: 0xfff6e0, sunI: 1.3, hemi: 0.98, amb: 0xc2d2d6 },
  { h: 17, sky: 0xc2e2ea, sun: 0xffe8bc, sunI: 1.02, hemi: 0.82, amb: 0x9fb8c0 },
  { h: 19.3, sky: 0xe89055, sun: 0xff9a55, sunI: 0.42, hemi: 0.46, amb: 0x6a5a6a },
  { h: 21, sky: 0x2c2850, sun: 0x2c2c5e, sunI: 0.09, hemi: 0.22, amb: 0x1a1836 },
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
// clay-diorama palette — colourful facades for a vibrant town, terracotta roofs.
const wallPal = [0xf1e7d2, 0xd7e3d0, 0xd9e6ee, 0xf2e2c2, 0xe9d3d0, 0xefe3cc, 0xcfe0d6, 0xe6d0b8, 0xd4dfe8];
const roofPal = [0xd9743f, 0xcf6838, 0xc65a3a, 0xdc8a4a, 0xcb6a3c, 0x566270];
function hashId(s) { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }

let renderer, scene, camera, sun, hemi, amb, cloudGroup, composer, bokeh;
let eng, WORLD, prev = null, cur = null;
const ROSTER = {}, people = {}, lastPos = {}, lampFx = [];
let lampLights = 0, skyDome;
let playing = true, speed = 1, acc = 0, last = null, tms = 0;
const BASE_TPS = 7 / 6;
// A semi-fixed camera: a set overview (stadium large on the right, ~75% in frame),
// that eases in to a resident when you click them, and back out when you click away.
const OVERVIEW = { pos: [3, 20, 24], tgt: [-4, 4, -12] };
let camPos, camTgt, wantPos, wantTgt, focusId = null;
const TEX = {};

const $ = id => document.getElementById(id);
const pad = n => String(n).padStart(2, '0');
const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : s);

// ---- plate mode (CD-008): offline control-rig renders for the master plate ----
// ?plate=1 turns the scene into a still-image rig: fixed daylight, a camera set
// from URL params, no DOF/HUD/sim loop, café GLB from local assets, and two
// passes — the colour blockout and a linear depth map (for depth-ControlNet and
// runtime sprite occlusion). Driven headlessly; see tools/render_plate.mjs.
const QS = new URLSearchParams(location.search);
const PLATE = QS.has('plate');
const qf = (k, d) => { const v = parseFloat(QS.get(k)); return Number.isFinite(v) ? v : d; };

function box(w, h, d, color, tex) {
  const r = Math.max(0.05, Math.min(w, h, d) * 0.16);          // soft clay edges
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.92, metalness: 0 });
  if (tex) mat.map = tex;
  return new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 2, r), mat);
}

// simple procedural textures (canvas) so the map isn't flat colour.
function makeTex(px, draw, repeat) {
  const cv = document.createElement('canvas'); cv.width = cv.height = px; draw(cv.getContext('2d'), px);
  const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; if (repeat) t.repeat.set(repeat, repeat); t.anisotropy = 4; return t;
}
function buildTextures() {
  TEX.grass = makeTex(64, (c, n) => { c.fillStyle = '#82ba36'; c.fillRect(0, 0, n, n); for (let i = 0; i < 900; i++) { const g = 120 + Math.random() * 70 | 0; c.fillStyle = `rgba(${50 + Math.random() * 40 | 0},${g},${40 + Math.random() * 30 | 0},0.5)`; c.fillRect(Math.random() * n, Math.random() * n, 1.6, 1.6); } }, 90);
  TEX.asphalt = makeTex(64, (c, n) => { c.fillStyle = '#3b3f45'; c.fillRect(0, 0, n, n); for (let i = 0; i < 600; i++) { const v = 40 + Math.random() * 40 | 0; c.fillStyle = `rgba(${v},${v},${v + 4},0.4)`; c.fillRect(Math.random() * n, Math.random() * n, 1, 1); } }, 3);
  TEX.cobble = makeTex(64, (c, n) => { c.fillStyle = '#cfc7b2'; c.fillRect(0, 0, n, n); c.strokeStyle = 'rgba(120,110,90,0.5)'; for (let y = 0; y < n; y += 8) for (let x = 0; x < n; x += 8) c.strokeRect(x + (y / 8 % 2 ? 4 : 0), y, 8, 8); }, 2);
  TEX.plaster = makeTex(64, (c, n) => { c.fillStyle = '#f1e7d2'; c.fillRect(0, 0, n, n); for (let i = 0; i < 260; i++) { c.fillStyle = 'rgba(198,182,150,0.22)'; c.fillRect(Math.random() * n, Math.random() * n, 2, 2); } }, 1);
  TEX.tile = makeTex(64, (c, n) => { c.fillStyle = '#c8623c'; c.fillRect(0, 0, n, n); c.strokeStyle = 'rgba(120,50,30,0.5)'; c.lineWidth = 1; for (let y = 5; y < n; y += 6) { c.beginPath(); c.moveTo(0, y); c.lineTo(n, y); c.stroke(); } for (let x = 0; x < n; x += 10) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, n); c.strokeStyle = 'rgba(120,50,30,0.25)'; c.stroke(); } }, 1);
}
function near(x, y, list, d) { return list.some(([nx, ny]) => Math.hypot(nx - x, ny - y) < d); }

// ---- bespoke landmark builders (item: buildings that are what they are) ----
function umbrella3d(x, z, col) {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.2, 6), new THREE.MeshStandardMaterial({ color: 0x555555 })); pole.position.y = 0.6; g.add(pole);
  const top = new THREE.Mesh(new THREE.ConeGeometry(0.9, 0.45, 10), new THREE.MeshStandardMaterial({ color: col, roughness: 0.9 })); top.position.y = 1.35; g.add(top);
  g.position.set(x, 0, z); return g;
}
function table3d(x, z) { const t = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.5, 10), new THREE.MeshStandardMaterial({ color: 0xe8e2d0 })); t.position.set(x, 0.25, z); return t; }
function bench3d(x, z) { return box(1.2, 0.3, 0.4, 0x9a7a4a).translateY(0.25).translateX(x).translateZ(z); }
function floodlight(x, z) {
  const g = new THREE.Group();
  const p = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 7.5, 6), new THREE.MeshStandardMaterial({ color: 0x3a3d42 })); p.position.y = 3.75; g.add(p);
  const em = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.5, 0.12), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff3d0, emissiveIntensity: 0.9 })); em.position.set(0, 7.4, 0.2); g.add(em);
  g.position.set(x, 0, z); return g;
}
function cafeBuilding(sx, sz, town) {
  const b = box(3.6, 4, 3.4, 0xefe3cc, TEX.plaster); b.position.set(sx, 2, sz); town.add(b);
  const roof = box(4, 0.7, 3.8, 0xd9743f, TEX.tile); roof.position.set(sx, 4.35, sz); town.add(roof);
  const aw = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.16, 1.5), new THREE.MeshStandardMaterial({ color: 0x3fa9b0 })); aw.position.set(sx, 1.7, sz + 2.2); aw.rotation.x = -0.35; town.add(aw);
  for (let i = 0; i < 3; i++) { const ux = sx - 1.4 + i * 1.4, uz = sz + 3.4; town.add(umbrella3d(ux, uz, [0xd1495b, 0xe0a24a, 0x3d84a8][i])); town.add(table3d(ux, uz)); }
}
function museumBuilding(sx, sz, town) {
  const b = box(4.4, 3.4, 3.4, 0xeef0ee, TEX.plaster); b.position.set(sx, 1.7, sz); town.add(b);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(3.4, 1.5, 4), new THREE.MeshStandardMaterial({ color: 0x9aa0a6 })); roof.rotation.y = Math.PI / 4; roof.position.set(sx, 4.1, sz); town.add(roof);
  for (let i = 0; i < 5; i++) { const col = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 3, 10), new THREE.MeshStandardMaterial({ color: 0xf1ece0 })); col.position.set(sx - 1.7 + i * 0.85, 1.5, sz + 1.9); town.add(col); }
}

// ---- real AI-generated 3D assets (Meshy → glTF), style-gated ----
// Each place id can point at a glTF/GLB. It is auto-normalised: measured, scaled
// to a target footprint (scene units), rotated, and dropped onto the ground at the
// place's coords. If the file is missing/broken we fall back to the procedural
// builder, so the town always renders. This is the harness for Path B — the look
// moves from placeholder primitives to sculpted clay assets one landmark at a time.
const gltfLoader = new GLTFLoader();
const ASSETS = {
  // footprint target ~7.5 scene units (café + its terrace); face the street (+Z).
  // Served from the repo via jsDelivr (CORS-ok), pinned to the asset's commit so
  // the deploy needs no workflow change to ship the GLB. Same-origin ./assets/
  // also works once pages.yml copies web/assets.
  loc_cafe: { file: 'https://cdn.jsdelivr.net/gh/Roy481977/ERA@cb9df13b31f8d26c6070edad5c54c56dc1d90b10/web/assets/cafe.glb', target: 7.5, rotY: Math.PI, yOffset: 0 },
};
function loadAsset(spec, sx, sz, town, fallback) {
  let settled = false;
  window.__pendingAssets = (window.__pendingAssets || 0) + 1;
  gltfLoader.load(spec.file, gltf => {
    settled = true;
    window.__pendingAssets--;
    const m = gltf.scene;
    m.rotation.y = spec.rotY || 0;
    let bb = new THREE.Box3().setFromObject(m), size = new THREE.Vector3(); bb.getSize(size);
    const s = spec.target / Math.max(size.x, size.z, 0.001); m.scale.setScalar(s);
    bb = new THREE.Box3().setFromObject(m);
    const c = new THREE.Vector3(); bb.getCenter(c);
    m.position.set(sx - c.x, (spec.yOffset || 0) - bb.min.y, sz - c.z);
    m.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; if (o.material) { o.material.metalness = 0; if (o.material.roughness !== undefined) o.material.roughness = Math.max(0.7, o.material.roughness); } } });
    town.add(m);
  }, undefined, err => { if (!settled) { settled = true; window.__pendingAssets--; console.warn('asset load failed, using placeholder:', spec.file, err); fallback(); } });
}

function buildTown() {
  const town = new THREE.Group();
  const nodes = WORLD.locations.map(l => [l.x, l.y]);

  // ground
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(900, 900), new THREE.MeshStandardMaterial({ color: 0xffffff, map: TEX.grass, roughness: 1 }));
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
      const b = box(2 + rnd() * 1.6, h, 2 + rnd() * 1.6, wallPal[(s >>> 3) % wallPal.length], TEX.plaster); b.position.set(sx, h / 2, sz); town.add(b);
      const roof = box(2.3, 0.5, 2.3, roofPal[(s >>> 7) % roofPal.length], TEX.tile); roof.position.set(sx, h + 0.25, sz); town.add(roof);
    }
  }

  // plate mode: the world must recede into real distance — a far ring of fabric
  // (blocks, roofs, trees) beyond the core town, and soft hills on the horizon.
  if (PLATE) {
    let fs = 24681357; const frnd = () => { fs = (Math.imul(fs, 1664525) + 1013904223) >>> 0; return fs / 4294967296; };
    for (let x = EX0 - 900; x < EX1 + 900; x += GAP * 1.35) for (let y = EY0 - 1100; y < EY1 + 500; y += GAP * 1.35) {
      if (x > EX0 - 40 && x < EX1 + 40 && y > EY0 - 40 && y < EY1 + 40) continue;   // core handled above
      const n = 1 + Math.floor(frnd() * 3);
      for (let k = 0; k < n; k++) {
        const bx = x + (frnd() - 0.5) * GAP, by = y + (frnd() - 0.5) * GAP;
        const h = 1.6 + frnd() * 4.5, [sx, sz] = w2s(bx, by);
        const b = box(2 + frnd() * 1.8, h, 2 + frnd() * 1.8, wallPal[(fs >>> 3) % wallPal.length], TEX.plaster); b.position.set(sx, h / 2, sz); town.add(b);
        const roof = box(2.4, 0.5, 2.4, roofPal[(fs >>> 7) % roofPal.length], TEX.tile); roof.position.set(sx, h + 0.25, sz); town.add(roof);
        if (frnd() < 0.5) town.add(streetTree(sx + 2.4, sz + 1.2));
      }
    }
    for (let i = 0; i < 7; i++) {                                   // horizon hills
      const [hx, hz] = w2s(-700 + i * 420 + (i % 2) * 140, -1150 - (i % 3) * 260);
      const hill = new THREE.Mesh(new THREE.SphereGeometry(30 + (i % 3) * 14, 20, 12),
        new THREE.MeshStandardMaterial({ color: [0x8fb956, 0x7fae4e, 0x9cc161][i % 3], roughness: 1 }));
      hill.scale.y = 0.16; hill.position.set(hx, 0, hz); town.add(hill);
    }
  }

  // the twelve real places — distinct landmarks
  WORLD.locations.forEach(l => {
    const [sx, sz] = w2s(l.x, l.y);
    if (l.id === 'loc_main_square') {                                 // the city circle — plaza, monument, fountain, café seating
      const plaza = new THREE.Mesh(new THREE.CylinderGeometry(6.5, 6.5, 0.2, 44), new THREE.MeshStandardMaterial({ color: 0xffffff, map: TEX.cobble })); plaza.position.set(sx, 0.12, sz); town.add(plaza);
      const isle = new THREE.Mesh(new THREE.CylinderGeometry(2.3, 2.3, 0.3, 26), new THREE.MeshStandardMaterial({ color: 0x86bf3a })); isle.position.set(sx, 0.18, sz); town.add(isle);
      const mon = box(0.5, 4, 0.5, 0xe8e2d4); mon.position.set(sx, 2, sz); town.add(mon);
      const basin = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.5, 20), new THREE.MeshStandardMaterial({ color: 0xd8d2c4 })); basin.position.set(sx + 4.2, 0.25, sz + 3.6); town.add(basin);
      const wat = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 0.12, 20), new THREE.MeshStandardMaterial({ color: 0x3fc6d0 })); wat.position.set(sx + 4.2, 0.5, sz + 3.6); town.add(wat);
      for (let i = 0; i < 3; i++) { town.add(umbrella3d(sx - 4 + i * 1.7, sz + 4.6, [0xd1495b, 0xe0a24a, 0x3d84a8][i])); town.add(table3d(sx - 4 + i * 1.7, sz + 4.6)); }
      town.add(bench3d(sx - 5.4, sz)); town.add(bench3d(sx + 5.4, sz));
    } else if (l.id === 'loc_stadium') {                              // stadium — stands, pitch, roof ring, floodlights
      const stands = new THREE.Mesh(new THREE.CylinderGeometry(11, 12.5, 3.8, 44, 1, true), new THREE.MeshStandardMaterial({ color: 0x9aa0a6, side: THREE.DoubleSide })); stands.position.set(sx, 1.9, sz); town.add(stands);
      const inner = new THREE.Mesh(new THREE.CylinderGeometry(9.2, 9.6, 3.6, 44, 1, true), new THREE.MeshStandardMaterial({ color: 0xb04a4a, side: THREE.DoubleSide })); inner.position.set(sx, 1.9, sz); town.add(inner);
      const pitch = new THREE.Mesh(new THREE.CylinderGeometry(8.5, 8.5, 0.2, 44), new THREE.MeshStandardMaterial({ color: 0x5fbf4a })); pitch.position.set(sx, 0.16, sz); town.add(pitch);
      const roof = new THREE.Mesh(new THREE.TorusGeometry(11.8, 0.8, 8, 44), new THREE.MeshStandardMaterial({ color: 0xdfe4e8 })); roof.rotation.x = Math.PI / 2; roof.position.set(sx, 3.9, sz); town.add(roof);
      for (const [ox, oz] of [[8.5, 8.5], [-8.5, 8.5], [8.5, -8.5], [-8.5, -8.5]]) town.add(floodlight(sx + ox, sz + oz));
    } else if (/oak/.test(l.id)) {
      const trunk = box(0.5, 2, 0.5, 0x7a5a3a); trunk.position.set(sx, 1, sz); town.add(trunk);
      const crown = new THREE.Mesh(new THREE.SphereGeometry(2.6, 12, 10), new THREE.MeshStandardMaterial({ color: 0x3f9a30 })); crown.position.set(sx, 3.3, sz); town.add(crown);
    } else if (l.id === 'loc_bridge' || l.id === 'loc_riverside') {
      const b = box(3.5, 0.4, 3.5, 0xcbb98f); b.position.set(sx, 0.3, sz); town.add(b);
    } else if (l.id === 'loc_cafe') {
      if (ASSETS[l.id]) loadAsset(ASSETS[l.id], sx, sz, town, () => cafeBuilding(sx, sz, town));
      else cafeBuilding(sx, sz, town);
    }
    else if (l.id === 'loc_museum') { museumBuilding(sx, sz, town); }
    else {
      const h = l.home ? 3 : 5;
      const wc = wallPal[hashId(l.id) % wallPal.length];
      const b = box(3.2, h, 3.2, wc, TEX.plaster); b.position.set(sx, h / 2, sz); town.add(b);
      const roof = box(3.6, 0.6, 3.6, l.home ? 0xc65a3a : 0xb5613f, TEX.tile); roof.position.set(sx, h + 0.3, sz); town.add(roof);
      if (l.id === 'loc_pub') { const s = box(0.9, 0.55, 0.12, 0x7a3a2a); s.position.set(sx + 1.85, 2.4, sz); town.add(s); }
      if (l.id === 'loc_bakery') { const ch = box(0.42, 1.3, 0.42, 0xb5613f); ch.position.set(sx + 1, h + 0.9, sz + 1); town.add(ch); }
    }
  });
  town.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });   // soft clay shadows
  scene.add(town);
}

function streetTree(x, z) {
  const g = new THREE.Group();
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.17, 1.4, 6), new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 1 })); tr.position.y = 0.7; g.add(tr);
  const cr = new THREE.Mesh(new THREE.SphereGeometry(0.95, 10, 8), new THREE.MeshStandardMaterial({ color: 0x72c233, roughness: 1 })); cr.position.y = 2.0; cr.scale.y = 1.15; g.add(cr);
  g.position.set(x, 0, z); return g;
}
function lamp(x, z) {
  const g = new THREE.Group();
  const p = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 2.3, 6), new THREE.MeshStandardMaterial({ color: 0x2a2a2e })); p.position.y = 1.15; g.add(p);
  const headMat = new THREE.MeshStandardMaterial({ color: 0xffe0a0, emissive: 0xffb347, emissiveIntensity: 0.05 });
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 6), headMat); head.position.y = 2.3; g.add(head);
  const halo = new THREE.Mesh(new THREE.SphereGeometry(0.5, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffcf6a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); halo.position.y = 2.3; g.add(halo);
  const pool = new THREE.Mesh(new THREE.CircleGeometry(2.4, 20), new THREE.MeshBasicMaterial({ color: 0xffcf6a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); pool.rotation.x = -Math.PI / 2; pool.position.y = 0.06; g.add(pool);
  const fx = { head: headMat, halo: halo.material, pool: pool.material };
  if (lampLights < 24) { const pl = new THREE.PointLight(0xffcf6a, 0, 12, 2); pl.position.y = 2.3; g.add(pl); fx.light = pl; lampLights++; }   // a capped number cast real light
  lampFx.push(fx);
  g.position.set(x, 0, z); return g;
}
function car(x, z, ang, color) { const b = box(1.7, 0.55, 0.85, color); b.position.set(x, 0.35, z); b.rotation.y = ang; return b; }

function buildStreets(town) {
  const roadMat = new THREE.MeshStandardMaterial({ color: 0xffffff, map: TEX.asphalt, roughness: 1 });
  const walkMat = new THREE.MeshStandardMaterial({ color: 0xffffff, map: TEX.cobble, roughness: 1 });
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
  g.userData.id = e.id;
  scene.add(g); return g;
}

// Semi-fixed camera: hold the overview; when a resident is focused, ease in close
// on them; ease back to the overview when focus clears.
function easeCamera(dt) {
  if (focusId && people[focusId]) {
    const p = people[focusId].position;
    wantTgt.set(p.x, p.y + 1, p.z);
    wantPos.set(p.x + 5, p.y + 8, p.z + 12);
  } else {
    wantPos.set(OVERVIEW.pos[0], OVERVIEW.pos[1], OVERVIEW.pos[2]);
    wantTgt.set(OVERVIEW.tgt[0], OVERVIEW.tgt[1], OVERVIEW.tgt[2]);
  }
  const k = Math.min(1, dt * 2.4);
  camPos.lerp(wantPos, k); camTgt.lerp(wantTgt, k);
  camera.position.copy(camPos); camera.lookAt(camTgt);
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

  // lighting by the clock — sun peaks at noon, low at dawn/dusk
  const hourf = cur.hour + cur.minute / 60;
  const L = lightingAt(hourf % 24);
  scene.background = L.sky; scene.fog.color = L.sky;
  if (skyDome) { const dayF = Math.min(1, L.sunI / 1.0); skyDome.material.color.setRGB(0.05 + dayF * 0.95, 0.09 + dayF * 0.91, 0.18 + dayF * 0.82); }
  hemi.color = L.sky; hemi.intensity = L.hemi; amb.color = L.amb; sun.color = L.sun; sun.intensity = L.sunI;
  const solar = (hourf - 6) / 12, alt = Math.sin(Math.PI * Math.max(0, Math.min(1, solar)));
  sun.position.set((solar - 0.5) * 150, Math.max(5, alt * 95), 45);

  // street lights switch on as the sun drops — head glows, a halo blooms, a warm
  // pool falls on the pavement, and a capped few cast real light. Off by day.
  const nightF = Math.max(0, Math.min(1, (0.5 - L.sunI) / 0.45));
  for (const f of lampFx) { f.head.emissiveIntensity = 0.05 + nightF * 1.7; f.halo.opacity = nightF * 0.5; f.pool.opacity = nightF * 0.34; if (f.light) f.light.intensity = nightF * 3.2; }

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

  easeCamera(dt);
  if (skyDome) skyDome.position.copy(camera.position);   // keep the sky centred on us
  if (cur.tick !== frame._t) { renderHud(cur); frame._t = cur.tick; }
  if (bokeh) bokeh.uniforms['focus'].value = camPos.distanceTo(camTgt);
  composer.render();
  requestAnimationFrame(frame);
}

function renderHud(fr) {
  $('hh').textContent = pad(fr.hour) + ':' + pad(fr.minute);
  $('wd').textContent = fr.weekday; $('day').textContent = fr.day;
  if (fr.weather) $('wx').textContent = `${fr.season} · ${cap(fr.weather.sky)}`;
}

async function main() {
  if (PLATE) {
    WORLD = await (await fetch('./world.json')).json();      // static stage; no sim
    ASSETS.loc_cafe.file = './assets/cafe.glb';              // local GLB for the rig
  } else {
    const { default: init, WasmEngine } = await import('./pkg/era_first_breath.js');
    await init();
    eng = new WasmEngine(0);
    WORLD = JSON.parse(eng.world_json());
    cur = JSON.parse(eng.snapshot_json()); prev = cur;
  }
  WORLD.entities.forEach(e => ROSTER[e.id] = e);

  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: PLATE });
  renderer.setPixelRatio(PLATE ? 1 : (window.devicePixelRatio || 1));
  const RW = PLATE ? qf('w', 1920) : window.innerWidth, RH = PLATE ? qf('h', 1200) : window.innerHeight;
  renderer.setSize(RW, RH);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  $('app').appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x2f8fe0);
  scene.fog = new THREE.Fog(0xbfe0ea, 150, 660);          // only a light haze far out
  camera = new THREE.PerspectiveCamera(qf('fov', PLATE ? 38 : 34), RW / RH, 0.5, 900);
  buildTextures();
  // a rich vibrant sky — deep blue at the zenith, light near the horizon
  { const cv = document.createElement('canvas'); cv.width = 8; cv.height = 128; const g = cv.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, '#1466c8'); gr.addColorStop(0.5, '#4ea3e6'); gr.addColorStop(1, '#cfe9f5'); g.fillStyle = gr; g.fillRect(0, 0, 8, 128);
    skyDome = new THREE.Mesh(new THREE.SphereGeometry(430, 24, 16), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(cv), side: THREE.BackSide, fog: false, depthWrite: false })); scene.add(skyDome); }

  hemi = new THREE.HemisphereLight(0xbfe0ea, 0x6a5a3a, 0.98); scene.add(hemi);
  amb = new THREE.AmbientLight(0xbfae90, 0.38); scene.add(amb);
  sun = new THREE.DirectionalLight(0xfff0d2, 1.28); sun.position.set(60, 80, 40); scene.add(sun);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004;
  { const c = sun.shadow.camera; const e = PLATE ? 115 : 75; c.left = -e; c.right = e; c.top = e; c.bottom = -e; c.near = 1; c.far = PLATE ? 500 : 320; }

  buildTown();

  // big fluffy cumulus clouds (clusters of puffs), like the reference sky
  cloudGroup = new THREE.Group();
  for (let i = 0; i < 9; i++) {
    const cl = new THREE.Group(), puffs = 3 + (i % 3);
    for (let p = 0; p < puffs; p++) { const r = 8 + Math.random() * 7; const s = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 })); s.position.set((p - puffs / 2) * 7, Math.random() * 4, Math.random() * 6); s.scale.y = 0.6; cl.add(s); }
    cl.position.set(-95 + i * 26, 48 + (i % 3) * 8, -60 - (i % 4) * 22); cloudGroup.add(cl);
  }
  scene.add(cloudGroup);

  if (PLATE) { setupPlate(); $('loading').remove(); return; }   // still-image rig; no loop

  // macro depth of field — the hero sharp, the rest melting to blur (tilt-shift).
  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  bokeh = new BokehPass(scene, camera, { focus: 40, aperture: 0.0004, maxblur: 0.004 });   // only far distance softens
  composer.addPass(bokeh);
  composer.addPass(new OutputPass());

  camPos = new THREE.Vector3(...OVERVIEW.pos); camTgt = new THREE.Vector3(...OVERVIEW.tgt);
  wantPos = camPos.clone(); wantTgt = camTgt.clone();
  camera.position.copy(camPos); camera.lookAt(camTgt);
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

// The plate rig: fixed daylight, a parameterised still camera, two passes.
// Colour pass renders on load; __renderDepth() switches the scene to a linear
// depth material (near = white, far = black — disparity style for ControlNet
// and for runtime occlusion) and re-renders. __plateReady flags completion.
function setupPlate() {
  // THE CANONICAL PLATE CAMERA (CD-008, locked by Roy 2026-07-21): "W2" —
  // cinematic wide, whole district in frame, stadium right-of-center, café +
  // square + river midground, horizon hills, sky ~28%. Aspect 2.4:1. Every
  // sprite projects through this camera; change only with a new plate.
  const hour = qf('hour', 10.5);
  camera.position.set(qf('cx', -4), qf('cy', 24), qf('cz', 85));
  camera.lookAt(qf('tx', -14), qf('ty', 1), qf('tz', -26));

  const L = lightingAt(hour);                                 // fixed golden daylight
  scene.background = L.sky; scene.fog.color = L.sky;
  hemi.color = L.sky; hemi.intensity = L.hemi; amb.color = L.amb; sun.color = L.sun; sun.intensity = L.sunI;
  const solar = (hour - 6) / 12, alt = Math.sin(Math.PI * Math.max(0, Math.min(1, solar)));
  sun.position.set((solar - 0.5) * 150, Math.max(5, alt * 95), 45);
  skyDome.position.copy(camera.position);
  if (cloudGroup) cloudGroup.visible = false;   // the image model paints the cumulus

  const depthMat = new THREE.ShaderMaterial({
    uniforms: { uNear: { value: qf('dnear', 4) }, uFar: { value: qf('dfar', 300) } },
    vertexShader: 'varying float vD; void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }',
    fragmentShader: 'varying float vD; uniform float uNear; uniform float uFar; void main(){ float d = clamp((vD - uNear) / (uFar - uNear), 0.0, 1.0); gl_FragColor = vec4(vec3(1.0 - d), 1.0); }',
  });
  window.__renderColor = () => renderer.render(scene, camera);
  window.__renderDepth = () => {
    skyDome.visible = false; if (cloudGroup) cloudGroup.visible = false;
    scene.traverse(o => { if (o.isMesh && o.material && (o.material.transparent || o.material.blending === THREE.AdditiveBlending)) o.visible = false; });
    scene.overrideMaterial = depthMat; scene.fog = null; scene.background = new THREE.Color(0x000000);
    renderer.render(scene, camera);
  };
  (async () => {                                              // wait for the GLB, then render
    const t0 = Date.now();
    while ((window.__pendingAssets || 0) > 0 && Date.now() - t0 < 45000) await new Promise(r => setTimeout(r, 200));
    renderer.render(scene, camera);
    window.__plateReady = true;
  })();
}

function bindControls() {
  const el = renderer.domElement, ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  // click a resident to zoom in on them; click empty space to return to the overview.
  el.addEventListener('click', ev => {
    ndc.x = (ev.clientX / window.innerWidth) * 2 - 1; ndc.y = -(ev.clientY / window.innerHeight) * 2 + 1;
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(Object.values(people), true);
    let id = null; if (hits.length) { let o = hits[0].object; while (o && o.userData.id === undefined) o = o.parent; id = o ? o.userData.id : null; }
    focusId = id;
    const sel = document.getElementById('wx'); if (id && ROSTER[id]) { /* keep hud simple */ }
  });
  $('play').onclick = e => { playing = !playing; e.target.textContent = playing ? 'Pause' : 'Play'; };
  document.querySelectorAll('[data-mul]').forEach(b => b.onclick = () => { speed = +b.dataset.mul; document.querySelectorAll('[data-mul]').forEach(x => x.classList.toggle('on', x === b)); });
}

main().catch(err => { const l = $('loading'); if (l) l.textContent = 'Failed to start: ' + err; console.error(err); });
