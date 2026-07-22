import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
p.on('pageerror', e => console.error('[pageerror]', String(e).slice(0, 300)));
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
for (const t of [96, 144, 191.5, 216, 264]) {
  const r = await p.evaluate((t) => {
    window.__seek(t);
    const f = window.__state.frames[Math.floor(t)];
    const total = f.entities.length;
    const vis = (window.__state.lastFigs || []).length;
    const dog = (window.__state.lastFigs || []).some(l => l.id === 'the_old_dog');
    return { total, vis, dogVisible: dog };
  }, t);
  console.log('t' + t, 'entities=' + r.total, 'visible=' + r.vis, 'dogVisible=' + r.dogVisible);
}
await p.evaluate(() => window.__seek(144));
await p.waitForTimeout(60);
await p.screenshot({ path: '/tmp/hide_144.png' });
await p.evaluate(() => window.__seek(191.5));
await p.waitForTimeout(60);
await p.screenshot({ path: '/tmp/hide_191.png', clip: { x: 760, y: 300, width: 460, height: 260 } });
console.log('shots written');
await b.close();
