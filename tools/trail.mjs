import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
const id = process.argv[2] || 'res_yusuf';
const t0 = Number(process.argv[3] || 108), t1 = Number(process.argv[4] || 116);
// sample rendered position + visibility finely
const samples = [];
for (let t = t0; t <= t1; t += 0.1) {
  const s = await p.evaluate(([t, id]) => {
    window.__seek(t);
    const lf = (window.__state.lastFigs || []).find(l => l.id === id);
    // also compute where placeEntity would put it (its route position), regardless of hide
    return lf ? { x: Math.round(lf.sx), y: Math.round(lf.sy), vis: 1 } : { vis: 0 };
  }, [t, id]);
  samples.push({ t: +t.toFixed(1), ...s });
}
const vis = samples.filter(s => s.vis).length;
console.log(id + ' t' + t0 + '-' + t1 + ': ' + vis + '/' + samples.length + ' frames visible');
// print visibility timeline compactly
console.log(samples.map(s => s.vis ? '#' : '.').join(''));
// draw the visible trail on the plate over paths
const pts = samples.filter(s => s.vis).map(s => [s.x, s.y]);
await p.evaluate(([id, pts, t]) => {
  window.__seek(t);
  window.__debugDraw({ paths: true, markers: pts.map((p, i) => ({ x: 0, y: 0, r: 0, c: 'rgb(0,0,0)' })) });
  // draw trail manually on canvas (screen coords already)
  const ctx = document.getElementById('c').getContext('2d');
  ctx.save(); ctx.strokeStyle = 'rgba(255,60,60,.95)'; ctx.lineWidth = 2; ctx.beginPath();
  pts.forEach((pt, i) => { i ? ctx.lineTo(pt[0], pt[1]) : ctx.moveTo(pt[0], pt[1]); }); ctx.stroke();
  ctx.fillStyle = '#ff0'; pts.forEach(pt => { ctx.beginPath(); ctx.arc(pt[0], pt[1], 2.5, 0, 7); ctx.fill(); });
  ctx.restore();
}, [id, pts, t0]);
await p.waitForTimeout(60);
await p.screenshot({ path: '/tmp/trail.png' });
console.log('wrote /tmp/trail.png (red = the path the resident actually renders along; green = your traced paths)');
await b.close();
