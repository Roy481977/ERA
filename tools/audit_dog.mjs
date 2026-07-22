import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
import fs from 'fs';
const PORT = process.env.PORT || 8399;
const m = JSON.parse(fs.readFileSync('web/assets/era-plate-map.json', 'utf8'));
const obs = m.obscured || [];
function pip(x, y, poly) { let ins = false, j = poly.length - 1; for (let i = 0; i < poly.length; i++) { const xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1]; if (((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) ins = !ins; j = i; } return ins; }
function inObs(x, y) { for (const o of obs) { const pts = o.pts || o; if (pip(x, y, pts)) return true; } return false; }
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
const legs = [['loc_riverside', 'loc_cafe'], ['loc_cafe', 'loc_main_square'], ['loc_main_square', 'loc_stadium'], ['loc_stadium', 'loc_main_square'], ['loc_main_square', 'loc_bridge'], ['loc_bridge', 'loc_riverside']];
for (const [f, t] of legs) {
  const r = await p.evaluate(([f, t]) => { const r = window.__getRoute(f, t); return r ? r.pts.map(p => [Math.round(p.x), Math.round(p.y)]) : null; }, [f, t]);
  if (!r) { console.log(f, '->', t, 'NO ROUTE'); continue; }
  let hits = 0, tot = 0; const bad = [];
  for (let i = 1; i < r.length; i++) { const [x0, y0] = r[i - 1], [x1, y1] = r[i]; const seg = Math.hypot(x1 - x0, y1 - y0), N = Math.max(2, Math.round(seg / 6)); for (let k = 0; k <= N; k++) { const tt = k / N, x = x0 + (x1 - x0) * tt, y = y0 + (y1 - y0) * tt; tot++; if (inObs(x, y)) { hits++; if (bad.length < 4) bad.push([Math.round(x), Math.round(y)]); } } }
  console.log(f.replace('loc_', '') + ' -> ' + t.replace('loc_', '') + ':', r.length + 'pts', hits + '/' + tot + ' IN BUILDING', bad.length ? JSON.stringify(bad) : '');
}
await b.close();
