import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
import fs from 'fs';
const PORT = process.env.PORT || 8399;
const m = JSON.parse(fs.readFileSync('web/assets/era-plate-map.json', 'utf8'));
function distToPath(px, py) {
  let best = Infinity;
  for (const p of m.paths) { if (p.type === 'river') continue; const pts = p.pts; for (let i = 1; i < pts.length; i++) { const ax = pts[i - 1][0], ay = pts[i - 1][1], bx = pts[i][0], by = pts[i][1], dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1; let t = ((px - ax) * dx + (py - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t; const d = Math.hypot(px - (ax + t * dx), py - (ay + t * dy)); if (d < best) best = d; } }
  return best;
}
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
const TOL = 16;   // within this of a path = on the walkable ground
const off = [];
for (let t = 0; t < 288; t += 1.5) {   // one full day, sub-tick sampled
  const figs = await p.evaluate((t) => { window.__seek(t); return (window.__state.lastFigs || []).map(l => ({ id: l.id, px: l.px, py: l.py, w: l.walking })); }, t);
  for (const f of figs) {
    if (!f.px) continue;
    // only care about MOVING figures straying off the ground (settled-at-a-place is fine)
    if (!f.w) continue;
    const d = distToPath(f.px, f.py);
    if (d > TOL) off.push({ x: Math.round(f.px), y: Math.round(f.py), d: Math.round(d), id: f.id });
  }
}
// cluster off-path samples into hotspots
const spots = [];
for (const o of off) { let s = spots.find(h => Math.hypot(h.x - o.x, h.y - o.y) < 22); if (s) { s.n++; s.x = (s.x * (s.n - 1) + o.x) / s.n; s.y = (s.y * (s.n - 1) + o.y) / s.n; s.maxd = Math.max(s.maxd, o.d); } else spots.push({ x: o.x, y: o.y, n: 1, maxd: o.d }); }
spots.sort((a, b) => b.n - a.n);
console.log('off-path moving samples:', off.length, 'in', spots.length, 'hotspots (>16px from any path):');
for (const s of spots.filter(s => s.n >= 3)) console.log('  (' + Math.round(s.x) + ',' + Math.round(s.y) + ')  ' + s.n + ' samples, up to ' + s.maxd + 'px off');
// render the hotspots + path net
const markers = spots.filter(s => s.n >= 3).map(s => ({ x: s.x, y: s.y, r: Math.min(14, 4 + s.n / 6), c: 'rgb(255,40,40)' }));
await p.evaluate((markers) => { window.__seek(144); window.__debugDraw({ paths: true, markers }); }, markers);
await p.waitForTimeout(80);
await p.screenshot({ path: '/tmp/offpath.png' });
console.log('wrote /tmp/offpath.png (green = paths, red = where movers step off the ground)');
await b.close();
