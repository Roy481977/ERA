import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
const t0 = Number(process.argv[2] || 140), t1 = Number(process.argv[3] || 149), step = Number(process.argv[4] || 0.15);
let n = 0;
for (let t = t0; t <= t1; t += step) {
  await p.evaluate((t) => window.__seek(t), t);
  await p.waitForTimeout(30);
  await p.screenshot({ path: `/tmp/gf_${String(n).padStart(3, '0')}.png`, clip: { x: 48, y: 40, width: 1280, height: 700 } });
  n++;
}
console.log('captured', n, 'frames');
await b.close();
