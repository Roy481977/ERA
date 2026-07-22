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
  window.__debugDraw({ obscured: false, routes: [['loc_riverside', 'loc_cafe', '#ffd000'], ['loc_main_square', 'loc_stadium', '#00e5ff'], ['loc_oakside', 'loc_bakery', '#ff3bd0'], ['loc_millers_row', 'loc_pub', '#7cff3b']] });
});
await p.waitForTimeout(80);
await p.screenshot({ path: '/tmp/routes_clean.png' });
// zoom center
await p.screenshot({ path: '/tmp/routes_center.png', clip: { x: 640, y: 300, width: 560, height: 320 } });
console.log('wrote routes_clean + routes_center');
await b.close();
