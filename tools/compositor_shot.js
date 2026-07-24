#!/usr/bin/env node
// ERA — headless screenshot / sequence harness for web/compositor.js.
// Serves web/ over http and drives the compositor with Playwright + the
// pre-installed Chromium, using the page's debug hooks (window.__ready,
// __seek(frame), __draw(), __state, __view, __s2w). Used to VERIFY compositor
// changes (e.g. the owl flight) without a real browser.
//
//   node tools/compositor_shot.js [frame] [owlSeconds] [out.png]
//   node tools/compositor_shot.js --seq [frame] [t0] [t1] [n] [outdir]
//
// `owlSeconds` pins state.anim (the real-time clock the owl flies on) so a
// specific soar phase can be captured deterministically.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.join(__dirname, '..', 'web');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg' };
function chromePath() {
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  const hit = cp.execSync(`ls -d ${base}/chromium-*/chrome-linux/chrome 2>/dev/null | head -1`).toString().trim();
  return hit || undefined;   // fall back to Playwright's own resolution
}
const server = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/compositor.html';
  fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; }
    r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(d); });
});
(async () => {
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;
  const b = await chromium.launch({ executablePath: chromePath() });
  const pg = await b.newPage({ viewport: { width: 1280, height: 840 } });
  pg.on('pageerror', e => console.log('PAGE-EXC:', e.message));
  await pg.goto(`http://localhost:${port}/compositor.html`);
  await pg.waitForFunction('window.__ready === true', { timeout: 15000 });
  const a = process.argv.slice(2);
  const pin = async t => pg.evaluate(tt => { try { Object.defineProperty(window.__state, 'anim', { value: tt, writable: true, configurable: true }); } catch (e) { window.__state.anim = tt; } window.__draw(); }, t);
  if (a[0] === '--seq') {
    const frame = +(a[1] || 150), t0 = +(a[2] || 18), t1 = +(a[3] || 56), n = +(a[4] || 30), dir = a[5] || '/tmp/owlseq';
    fs.mkdirSync(dir, { recursive: true });
    await pg.evaluate(fr => { window.__seek(fr); window.__state.playing = false; }, frame);
    for (let i = 0; i < n; i++) { await pin(t0 + (t1 - t0) * i / (n - 1));
      await pg.screenshot({ path: `${dir}/f${String(i).padStart(2, '0')}.png` }); }
    console.log('SEQ', n, '->', dir);
  } else {
    const frame = +(a[0] || 144), t = +(a[1] || 30), out = a[2] || '/tmp/plate_owl.png';
    await pg.evaluate(fr => { window.__seek(fr); window.__state.playing = false; }, frame);
    await pin(t); await pg.waitForTimeout(300); await pin(t);
    await pg.screenshot({ path: out });
    console.log('SHOT frame', frame, 'owlSec', t, '->', out);
  }
  await b.close(); server.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
