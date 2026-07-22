import fs from 'fs';
const m = JSON.parse(fs.readFileSync('web/assets/era-plate-map.json', 'utf8'));
const obs = m.obscured || [];
function pip(x, y, poly) { let ins = false, j = poly.length - 1; for (let i = 0; i < poly.length; i++) { const xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1]; if (((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) ins = !ins; j = i; } return ins; }
function inObs(x, y) { for (const o of obs) { const pts = o.pts || o; if (pip(x, y, pts)) return true; } return false; }
// each PATH polyline: how much of it lies inside a building zone?
m.paths.forEach((p, idx) => {
  if (p.type === 'river') return;
  let hits = 0, tot = 0;
  const pts = p.pts;
  for (let i = 1; i < pts.length; i++) { const [x0, y0] = pts[i - 1], [x1, y1] = pts[i]; const seg = Math.hypot(x1 - x0, y1 - y0), N = Math.max(2, Math.round(seg / 6)); for (let k = 0; k <= N; k++) { const t = k / N, x = x0 + (x1 - x0) * t, y = y0 + (y1 - y0) * t; tot++; if (inObs(x, y)) hits++; } }
  console.log('path ' + idx + ' (' + (p.type || 'path') + ', ' + pts.length + 'pts): ' + hits + '/' + tot + ' in building ' + (hits / tot * 100).toFixed(0) + '%');
});
// each PIN: nearest path vertex distance, and does the straight stub cross a building?
const pathVerts = [];
m.paths.forEach(p => { if (p.type === 'river') return; p.pts.forEach(([x, y]) => pathVerts.push([x, y])); });
console.log('\npin -> nearest-path-vertex stub, building crossing:');
for (const [id, p] of Object.entries(m.places)) {
  if (p.x < 0 || p.x > 1376) continue;
  let best = 1e9, bv = null;
  for (const v of pathVerts) { const d = (v[0] - p.x) ** 2 + (v[1] - p.y) ** 2; if (d < best) { best = d; bv = v; } }
  let hits = 0, N = 14; for (let k = 0; k <= N; k++) { const t = k / N, x = p.x + (bv[0] - p.x) * t, y = p.y + (bv[1] - p.y) * t; if (inObs(x, y)) hits++; }
  console.log('  ' + id.replace('loc_', '').padEnd(16), 'stub ' + Math.sqrt(best).toFixed(0) + 'px', hits > 0 ? ('CROSSES building ' + hits + '/15') : 'clear');
}
