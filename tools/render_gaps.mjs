import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
import fs from 'fs';
const PORT = process.env.PORT || 8399;
const m = JSON.parse(fs.readFileSync('web/assets/era-plate-map.json', 'utf8'));
// gather segments tagged by path index
const segs = [];
m.paths.forEach((p, pi) => { if (p.type === 'river') return; for (let i = 1; i < p.pts.length; i++) segs.push({ pi, a: p.pts[i - 1], b: p.pts[i] }); });
function segInt(p1, p2, p3, p4) {
  const d1x = p2[0] - p1[0], d1y = p2[1] - p1[1], d2x = p4[0] - p3[0], d2y = p4[1] - p3[1];
  const den = d1x * d2y - d1y * d2x; if (Math.abs(den) < 1e-9) return null;
  const t = ((p3[0] - p1[0]) * d2y - (p3[1] - p1[1]) * d2x) / den;
  const u = ((p3[0] - p1[0]) * d1y - (p3[1] - p1[1]) * d1x) / den;
  if (t <= 0.001 || t >= 0.999 || u <= 0.001 || u >= 0.999) return null;
  return [p1[0] + t * d1x, p1[1] + t * d1y];
}
function segDist(A, B, C, D) { // min distance + closest midpoint between two segments
  const clampT = (P, Q, X) => { const dx = Q[0] - P[0], dy = Q[1] - P[1], L2 = dx * dx + dy * dy || 1; let t = ((X[0] - P[0]) * dx + (X[1] - P[1]) * dy) / L2; return t < 0 ? 0 : t > 1 ? 1 : t; };
  let best = Infinity, pt = null;
  for (const [P, Q, X] of [[A, B, C], [A, B, D], [C, D, A], [C, D, B]]) { const t = clampT(P, Q, X); const fx = P[0] + t * (Q[0] - P[0]), fy = P[1] + t * (Q[1] - P[1]); const d = Math.hypot(fx - X[0], fy - X[1]); if (d < best) { best = d; pt = [(fx + X[0]) / 2, (fy + X[1]) / 2]; } }
  return { d: best, pt };
}
const intersections = [], gaps = [];
for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length; j++) {
  if (segs[i].pi === segs[j].pi) continue;         // only between different paths
  const P = segInt(segs[i].a, segs[i].b, segs[j].a, segs[j].b);
  if (P) { intersections.push(P); continue; }
  const g = segDist(segs[i].a, segs[i].b, segs[j].a, segs[j].b);
  if (g.d > 16 && g.d < 48) gaps.push({ pt: g.pt, d: Math.round(g.d), pis: [segs[i].pi, segs[j].pi] });
}
// dedupe gaps by proximity
const gdedup = [];
for (const g of gaps) { if (!gdedup.some(h => Math.hypot(h.pt[0] - g.pt[0], h.pt[1] - g.pt[1]) < 25)) gdedup.push(g); }
console.log('true intersections (auto-joined):', intersections.length);
console.log('near-miss GAPS (paths close but NOT joined — likely corner-cuts):', gdedup.length);
for (const g of gdedup.sort((a, b) => a.d - b.d)) console.log('  (' + Math.round(g.pt[0]) + ',' + Math.round(g.pt[1]) + ')  ' + g.d + 'px apart  between path#' + g.pis[0] + ' & #' + g.pis[1]);
const markers = intersections.map(p => ({ x: p[0], y: p[1], r: 6, c: 'rgb(60,140,255)' })).concat(gdedup.map(g => ({ x: g.pt[0], y: g.pt[1], r: 11, c: 'rgb(255,40,40)' })));
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
await p.evaluate((markers) => { window.__seek(144); window.__debugDraw({ paths: true, markers }); }, markers);
await p.waitForTimeout(80);
await p.screenshot({ path: '/tmp/gaps.png' });
console.log('wrote /tmp/gaps.png (blue=joined crossings, red=unjoined gaps)');
await b.close();
