import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
import fs from 'fs';
const PORT = process.env.PORT || 8399;
const m = JSON.parse(fs.readFileSync('web/assets/era-plate-map.json', 'utf8'));
// distance from point to a polyline
function distToPolys(x, y) {
  let best = Infinity;
  for (const p of m.paths) { if (p.type === 'river') continue; const pts = p.pts; for (let i = 1; i < pts.length; i++) { const ax = pts[i - 1][0], ay = pts[i - 1][1], bx = pts[i][0], by = pts[i][1]; const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1; let t = ((x - ax) * dx + (y - ay) * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t; const fx = ax + t * dx, fy = ay + t * dy; const d = Math.hypot(x - fx, y - fy); if (d < best) best = d; } }
  return best;
}
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
const legs = await p.evaluate(() => {
  const fr = window.__state.frames, set = new Set(), out = [];
  const push = (a, b) => { const k = a + '|' + b; if (a && b && a !== b && !set.has(k)) { set.add(k); out.push([a, b]); } };
  for (let i = 0; i < fr.length; i++) { const f = fr[i], g = fr[(i + 1) % fr.length]; const nb = {}; for (const e of g.entities) nb[e.id] = e; for (const e of f.entities) { if (e.moving && e.from && e.to) push(e.from, e.to); const eN = nb[e.id]; if (eN && !e.moving && e.place && eN.place && e.place !== eN.place) push(e.place, eN.place); } }
  return out;
});
const TOL = 10; // px: within this of a traced path counts as "on path"
let worst = [];
for (const [f, t] of legs) {
  const r = await p.evaluate(([f, t]) => { const r = window.__getRoute(f, t); return r ? r.pts.map(p => [p.x, p.y]) : null; }, [f, t]);
  if (!r) continue;
  let onLen = 0, offLen = 0;
  for (let i = 1; i < r.length; i++) { const [x0, y0] = r[i - 1], [x1, y1] = r[i]; const seg = Math.hypot(x1 - x0, y1 - y0), N = Math.max(2, Math.round(seg / 5)); for (let k = 1; k <= N; k++) { const t0 = (k - 1) / N, t1 = k / N; const mx = x0 + (x1 - x0) * (t0 + t1) / 2, my = y0 + (y1 - y0) * (t0 + t1) / 2; const dl = seg / N; if (distToPolys(mx, my) <= TOL) onLen += dl; else offLen += dl; } }
  const pct = offLen / (onLen + offLen) * 100;
  worst.push({ leg: f.replace('loc_', '') + '->' + t.replace('loc_', ''), off: Math.round(offLen), pct: pct.toFixed(0) });
}
worst.sort((a, b) => b.off - a.off);
const bad = worst.filter(w => w.off > 15);
console.log('legs with >15px off-path travel (' + bad.length + ' of ' + worst.length + '):');
for (const w of bad.slice(0, 20)) console.log('  ' + w.leg.padEnd(34), w.off + 'px off (' + w.pct + '%)');
await b.close();
