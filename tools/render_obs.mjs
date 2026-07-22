import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
p.on('pageerror', e => console.error('[pageerror]', String(e).slice(0, 400)));
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
await p.evaluate(() => {
  window.__seek(144);
  window.__state.showPins = true;
  window.__debugDraw({ paths: true, routes: [['loc_main_square', 'loc_stadium', '#ff2020'], ['loc_riverside', 'loc_cafe', '#ffe000']] });
});
await p.waitForTimeout(80);
await p.screenshot({ path: '/tmp/net_full.png' });
await p.screenshot({ path: '/tmp/net_stadium.png', clip: { x: 780, y: 300, width: 500, height: 280 } });
console.log('wrote net_full + net_stadium');
await b.close();
