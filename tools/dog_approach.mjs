import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
// dog main_square->stadium spans tick 191->192. sample fine.
let line = [];
for (let t = 191.0; t <= 192.01; t += 0.1) {
  const r = await p.evaluate((t) => { window.__seek(t); const lf = (window.__state.lastFigs || []).find(l => l.id === 'the_old_dog'); return lf ? { x: Math.round(lf.sx), y: Math.round(lf.sy) } : null; }, t);
  line.push('t' + t.toFixed(1) + (r ? ' vis(' + r.x + ',' + r.y + ')' : ' HIDDEN'));
}
console.log(line.join('\n'));
// route it takes
const rt = await p.evaluate(() => { const r = window.__getRoute('loc_main_square', 'loc_stadium'); return r ? r.pts.map(p => [Math.round(p.x), Math.round(p.y)]) : null; });
console.log('\nmain_square->stadium route:', JSON.stringify(rt));
await b.close();
