#!/usr/bin/env node
// ERA plate control-rig renderer (CD-008). Headless Chromium opens
// web/plate3d.html?<params>, waits for the rig, and captures the colour
// blockout and the depth pass as PNGs. Run a local server on web/ first:
//   python3 -m http.server 8321 --directory web
// Usage:
//   node tools/render_plate.mjs out_prefix "w=1920&h=1200&cx=6&cy=46&cz=132&tx=-2&ty=4&tz=-20&fov=30"
import { chromium } from 'playwright';

const [prefix = 'plate', params = ''] = process.argv.slice(2);
const url = `http://127.0.0.1:8321/plate3d.html?${params}`;
const m = /w=(\d+)/.exec(params), mh = /h=(\d+)/.exec(params);
const W = m ? +m[1] : 1920, H = mh ? +mh[1] : 1200;

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',   // preinstalled build (env-pinned)
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: Math.min(W, 8192), height: Math.min(H, 8192) } });
page.on('console', msg => { const t = msg.text(); if (!/three\.module/.test(t)) console.log('[page]', t.slice(0, 300)); });
page.on('pageerror', e => console.error('[pageerror]', String(e).slice(0, 500)));

console.log('opening', url);
await page.goto(url, { waitUntil: 'domcontentloaded' });
await page.waitForFunction('window.__plateReady === true', null, { timeout: 240000 });
const canvas = page.locator('#app canvas');
await canvas.screenshot({ path: `${prefix}_color.png` });
console.log('wrote', `${prefix}_color.png`);
await page.evaluate('window.__renderDepth()');
await canvas.screenshot({ path: `${prefix}_depth.png` });
console.log('wrote', `${prefix}_depth.png`);
await browser.close();
