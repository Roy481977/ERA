#!/usr/bin/env node
// Headless capture of the ERA plate compositor at chosen replay frames.
// Serve web/ first:  python3 -m http.server 8321 --directory web
// Usage: node tools/render_compositor.mjs out_prefix 84 132 210
import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');

const [prefix = 'comp', ...frames] = process.argv.slice(2);
const PORT = process.env.PORT || 8322;
const W = 1376, H = 800;
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', e => console.error('[pageerror]', String(e).slice(0, 500)));
await page.goto(`http://127.0.0.1:${PORT}/compositor.html`, { waitUntil: 'domcontentloaded' });
await page.waitForFunction('window.__ready === true', null, { timeout: 60000 });
for (const f of (frames.length ? frames : [84])) {
  await page.evaluate((n) => window.__seek(n), Number(f));
  await page.waitForTimeout(150);
  await page.screenshot({ path: `${prefix}_f${f}.png` });
  console.log('wrote', `${prefix}_f${f}.png`);
}
await browser.close();
