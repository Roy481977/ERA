// ERA — plate BLOCKOUT renderer (CD-008 step 3). Builds the town's massing from
// the locked design/bible/world-coords.json: winding road ribbons along the real
// path curves, clay building blocks (signature places + terraced rows fronting the
// lanes), the river, the square + clock tower, and the Ground with its stand.
//
// A BLOCKOUT: correct massing + curves + a locked camera, rendered as a colour
// pass and a linear-depth pass. The clay skin comes afterwards from the Krea
// depth-locked style pass, so buildings here are simple clay boxes, not models.
// Driven headlessly by tools/render_plate3d.mjs.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const QS = new URLSearchParams(location.search);
const qf = (k, d) => { const v = parseFloat(QS.get(k)); return Number.isFinite(v) ? v : d; };

// ---- world units (wu) -> scene ----
const SC = 0.06;                 // scene units per wu
const CX = 1348, CZ = 606;       // bible-region centre (wu)
const w2s = (x, y) => [(x - CX) * SC, (y - CZ) * SC];
const WU = SC;

const WALL = [0xf1e7d2, 0xe9d3b8, 0xd9e2d0, 0xe6d0b8, 0xefe3cc, 0xe3d3c0, 0xdfe6ea, 0xecdcc4];
const ROOF = [0xc65a3a, 0xcf6838, 0xbe5533, 0xd6743f, 0xc2603a, 0x9aa0a6];
function hash(s) { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }

let renderer, scene, camera, composer, sun, hemi, amb, skyDome;
let COORDS;
const town = new THREE.Group();
const $ = id => document.getElementById(id);

function clayMat(color, rough = 0.95) { return new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0 }); }
function box(w, h, d, color) {
  const r = Math.max(0.03, Math.min(w, h, d) * 0.16);
  return new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 2, r), clayMat(color));
}
function ribbon(pts, width, y, color, rough = 1) {
  const n = pts.length; if (n < 2) return null;
  const pos = [], nrm = [], idx = [];
  for (let i = 0; i < n; i++) {
    const p = pts[i], a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
    let dx = b[0] - a[0], dz = b[1] - a[1]; const L = Math.hypot(dx, dz) || 1; dx /= L; dz /= L;
    const px = -dz, pz = dx;
    pos.push(p[0] + px * width / 2, y, p[1] + pz * width / 2);
    pos.push(p[0] - px * width / 2, y, p[1] - pz * width / 2);
    nrm.push(0, 1, 0, 0, 1, 0);
  }
  for (let i = 0; i < n - 1; i++) { const a = i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
  g.setIndex(idx);
  const m = new THREE.Mesh(g, clayMat(color, rough)); m.receiveShadow = true; return m;
}
const scenePath = p => p.pts.map(([x, y]) => w2s(x, y));
function segLen(pts) { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; }
function* along(pts, step) {
  let carry = 0;
  for (let i = 1; i < pts.length; i++) {
    const [ax, az] = pts[i - 1], [bx, bz] = pts[i];
    let dx = bx - ax, dz = bz - az; const L = Math.hypot(dx, dz) || 1e-6; dx /= L; dz /= L;
    let t = step - carry;
    while (t <= L) { yield { x: ax + dx * t, z: az + dz * t, dirx: dx, dirz: dz }; t += step; }
    carry = (carry + L) % step;
  }
}
const near = (x, z, list, d) => list.some(([lx, lz]) => Math.hypot(lx - x, lz - z) < d);

function buildGround(sx, sz) {
  const wall = box(9.6, 0.9, 6.4, 0xcaa07a); wall.position.set(sx, 0.45, sz); town.add(wall);
  const pitch = new THREE.Mesh(new THREE.BoxGeometry(8.6, 0.2, 5.6), clayMat(0x5fbf4a)); pitch.position.set(sx, 0.95, sz); town.add(pitch);
  const stand = box(9.0, 2.6, 2.0, 0xbfc4c8); stand.position.set(sx, 1.6, sz - 3.6); town.add(stand);
  const roof = box(9.6, 0.4, 2.5, 0xdfe4e8); roof.position.set(sx, 3.1, sz - 3.6); town.add(roof);
  for (const ox of [-4.4, 4.4]) { const fl = box(0.3, 6, 0.3, 0x3a3d42); fl.position.set(sx + ox, 3, sz - 4.6); town.add(fl); }
}
function buildTower(sx, sz) {
  const t = box(1.0, 4.2, 1.0, 0xe8dcc0); t.position.set(sx, 2.1, sz); town.add(t);
  const cap = new THREE.Mesh(new THREE.ConeGeometry(0.9, 1.2, 4), clayMat(0x4a5568)); cap.rotation.y = Math.PI / 4; cap.position.set(sx, 4.7, sz); town.add(cap);
}

function build() {
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(240, 240), clayMat(0x9ec06a, 1));
  ground.rotation.x = -Math.PI / 2; ground.position.y = -0.02; ground.receiveShadow = true; town.add(ground);

  const roads = [...COORDS.nav_paths, ...COORDS.dressing_paths].filter(p => p.pts);
  const placePts = COORDS.places.map(pl => w2s(...pl.world));
  const riverScene = [];

  // one river only — Roy's drawn nav river (p22), not the older traced dressing one
  for (const p of COORDS.nav_paths) if (p.type === 'river') { const sp = scenePath(p); riverScene.push(...sp); town.add(ribbon(sp, 40 * WU, 0.02, 0x3fb6cf, 0.4)); }
  for (const p of roads) {
    if (['river', 'rail', 'park'].includes(p.type)) continue;
    const sp = scenePath(p), w = p.type === 'lane' ? 30 : 46;
    town.add(ribbon(sp, (w + 20) * WU, 0.04, 0xcfc7b0));
    town.add(ribbon(sp, w * WU, 0.06, 0x55585e));
  }
  for (const p of roads) {
    if (p.type === 'park') town.add(ribbon(scenePath(p), 14 * WU, 0.05, 0xccc0a0));
    if (p.type === 'rail') town.add(ribbon(scenePath(p), 16 * WU, 0.03, 0x8a8f96));
  }

  const sig = new Set();
  for (const pl of COORDS.places) {
    const [sx, sz] = w2s(...pl.world);
    if (pl.name === 'The Ground' || pl.role === 'sim:loc_stadium') { buildGround(sx, sz); sig.add(pl.n); }
    else if (pl.name === 'Clock Tower') { buildTower(sx, sz); sig.add(pl.n); }
  }
  const ring = COORDS.dressing_paths.find(p => p.id === 'square_ring');
  if (ring && ring.circle) {
    const [cx, cz] = w2s(...ring.circle.c), rr = ring.circle.rx * WU;
    const plaza = new THREE.Mesh(new THREE.CylinderGeometry(rr + 1.2, rr + 1.2, 0.12, 40), clayMat(0xd9d0bb)); plaza.position.set(cx, 0.07, cz); town.add(plaza);
    const isle = new THREE.Mesh(new THREE.CylinderGeometry(rr * 0.42, rr * 0.42, 0.22, 28), clayMat(0x86bf3a)); isle.position.set(cx, 0.14, cz); town.add(isle);
  }

  const built = [];
  for (const pl of COORDS.places) {
    if (sig.has(pl.n)) continue;
    const role = pl.role || '';
    if (role === 'dressing' || role.startsWith('dressing')) continue;
    const [sx, sz] = w2s(...pl.world);
    const big = /club|museum|pub|caf|bakery|grocer/i.test(pl.name);
    const h = (big ? 3.2 : 2.6) + (hash(pl.name) % 5) * 0.2;
    const wdt = big ? 3.4 : 2.8, dep = big ? 3.0 : 2.6;
    const b = box(wdt, h, dep, WALL[hash(pl.name) % WALL.length]); b.position.set(sx, h / 2, sz); town.add(b);
    const roof = box(wdt + 0.5, 0.6, dep + 0.5, ROOF[hash(pl.name + 'r') % ROOF.length]); roof.position.set(sx, h + 0.3, sz); town.add(roof);
    built.push([sx, sz]);
  }

  let seed = 1337; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const avoid = [...placePts, ...built];
  for (const p of roads) {
    if (['river', 'rail', 'park'].includes(p.type)) continue;
    const sp = scenePath(p); if (segLen(sp) < 4) continue;
    const halfRoad = (p.type === 'lane' ? 30 : 46) * WU / 2;
    for (const s of along(sp, 3.0)) {
      for (const side of [1, -1]) {
        const off = halfRoad + 2.4;
        const hx = s.x + (-s.dirz) * off * side, hz = s.z + (s.dirx) * off * side;
        if (near(hx, hz, avoid, 3.2) || near(hx, hz, riverScene, 2.2)) continue;
        if (rnd() < 0.25) continue;
        const h = 2.2 + rnd() * 1.4, wdt = 2.4 + rnd() * 0.5, ang = Math.atan2(s.dirx, s.dirz);
        const b = box(wdt, h, 2.6, WALL[(seed >>> 3) % WALL.length]); b.position.set(hx, h / 2, hz); b.rotation.y = ang; town.add(b);
        const roof = box(wdt + 0.4, 0.5, 3.0, ROOF[(seed >>> 6) % ROOF.length]); roof.position.set(hx, h + 0.25, hz); roof.rotation.y = ang; town.add(roof);
        avoid.push([hx, hz]);
      }
    }
  }

  for (const x of (COORDS.crossings || [])) {
    const [cx, cz] = w2s(...x.world);
    for (let k = -2; k <= 2; k++) { const bar = box(0.4, 0.02, 1.4, 0xf2efe6); bar.position.set(cx + k * 0.45, 0.09, cz); town.add(bar); }
  }

  town.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  scene.add(town);
}

async function main() {
  COORDS = await (await fetch('./world-coords.json')).json();
  const RW = qf('w', 2640), RH = qf('h', 1200);   // 2.2:1 wide plate
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(RW, RH);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  $('app').appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe0ea);
  scene.fog = new THREE.Fog(0xcfe4ec, 60, 220);
  // THE LOCKED PLATE CAMERA (CD-008, Roy 2026-07-21): composition "C" — the Ground
  // cropped on the right, town winding to the left, river through the foreground.
  camera = new THREE.PerspectiveCamera(qf('fov', 52), RW / RH, 0.5, 700);
  camera.position.set(qf('cx', 15), qf('cy', 11), qf('cz', 26));
  camera.lookAt(qf('tx', 0), qf('ty', 1.5), qf('tz', -10));

  hemi = new THREE.HemisphereLight(0xcfe4ec, 0x6a5a3a, 0.9); scene.add(hemi);
  amb = new THREE.AmbientLight(0xbfae90, 0.35); scene.add(amb);
  sun = new THREE.DirectionalLight(0xfff0d2, 1.35); sun.position.set(30, 44, 26); scene.add(sun);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004;
  { const c = sun.shadow.camera; c.left = -70; c.right = 70; c.top = 70; c.bottom = -70; c.near = 1; c.far = 240; }

  { const cv = document.createElement('canvas'); cv.width = 8; cv.height = 128; const g = cv.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, '#1f74d0'); gr.addColorStop(0.55, '#68a8e0'); gr.addColorStop(1, '#cfe9f5'); g.fillStyle = gr; g.fillRect(0, 0, 8, 128);
    skyDome = new THREE.Mesh(new THREE.SphereGeometry(340, 24, 16), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(cv), side: THREE.BackSide, fog: false })); scene.add(skyDome); }

  build();

  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new OutputPass());

  const depthMat = new THREE.ShaderMaterial({
    uniforms: { uNear: { value: qf('dnear', 8) }, uFar: { value: qf('dfar', 150) } },
    vertexShader: 'varying float vD; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vD=-mv.z; gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'varying float vD; uniform float uNear; uniform float uFar; void main(){ float d=clamp((vD-uNear)/(uFar-uNear),0.0,1.0); gl_FragColor=vec4(vec3(1.0-d),1.0); }',
  });
  window.__renderColor = () => composer.render();
  window.__renderDepth = () => { skyDome.visible = false; scene.overrideMaterial = depthMat; scene.fog = null; scene.background = new THREE.Color(0); renderer.render(scene, camera); };

  composer.render();
  const l = $('loading'); if (l) l.remove();
  window.__plateReady = true;
}
main().catch(e => { const l = $('loading'); if (l) l.textContent = 'error: ' + e; console.error(e); });
