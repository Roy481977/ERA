import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
p.on('pageerror', e => console.error('[pageerror]', String(e).slice(0, 400)));
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
// sample the dog's screen pos across two hops; also grab zoomed shots
async function shot(t, name, clip) {
  const pos = await p.evaluate((t) => { window.__seek(t); const lf = (window.__state.lastFigs || []).find(l => l.id === 'the_old_dog'); return lf ? { x: Math.round(lf.sx), y: Math.round(lf.sy) } : null; }, t);
  await p.waitForTimeout(40);
  await p.screenshot({ path: name, clip });
  return pos;
}
// riverside->cafe (tick72). sample & one zoom around the mid
for (const t of [71.2, 71.5, 71.8]) console.log('riv->cafe t' + t, JSON.stringify(await p.evaluate((t) => { window.__seek(t); const lf = (window.__state.lastFigs || []).find(l => l.id === 'the_old_dog'); return lf ? { x: Math.round(lf.sx), y: Math.round(lf.sy) } : null; }, t)));
await shot(71.5, '/tmp/dogwalk_riv.png', { x: 640, y: 340, width: 420, height: 300 });
// main_square->stadium (tick192)
for (const t of [191.2, 191.5, 191.8]) console.log('sq->stad t' + t, JSON.stringify(await p.evaluate((t) => { window.__seek(t); const lf = (window.__state.lastFigs || []).find(l => l.id === 'the_old_dog'); return lf ? { x: Math.round(lf.sx), y: Math.round(lf.sy) } : null; }, t)));
await shot(191.5, '/tmp/dogwalk_sq.png', { x: 760, y: 300, width: 460, height: 260 });
console.log('done');
await b.close();
