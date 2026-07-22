import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('console',m=>{ if(m.type()==='error') errs.push('console:'+m.text()); });
await p.goto('http://127.0.0.1:8399/compositor.html', { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
const cases = [
  ['rain', {sky:'rain',temp:'cool',wet:true,windy:true,phrase:'steady rain'}, 150],
  ['snow', {sky:'snow',temp:'cold',wet:true,windy:false,phrase:'falling snow'}, 150],
  ['overcast', {sky:'overcast',temp:'cool',wet:false,windy:false,phrase:'a low, heavy overcast'}, 150],
  ['fog', {sky:'fog',temp:'cold',wet:false,windy:false,phrase:'a still, cold fog'}, 80],
];
for (const [tag,wx,t] of cases) {
  await p.evaluate(({wx,t})=>{ for(const f of window.__state.frames){ f.weather=wx; } window.__state.anim=6.0; window.__seek(t); }, {wx,t});
  await p.waitForTimeout(60);
  await p.screenshot({ path:`/tmp/wx-${tag}.png` });
}
console.log('errors:', errs.length ? errs.slice(0,8) : 'NONE');
await b.close();
