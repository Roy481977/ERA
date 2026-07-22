import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1376, height: 800 } });
const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('console',m=>{ if(m.type()==='error') errs.push('console:'+m.text()); });
await p.goto('http://127.0.0.1:8399/compositor.html', { waitUntil: 'domcontentloaded' });
await p.waitForFunction('window.__ready===true', null, { timeout: 60000 });
// report weather at sampled frames straight from the loaded replay
const info = await p.evaluate(()=>{
  const fr=window.__state.frames; const s=(i)=>{const w=fr[i].weather||{};return {day:fr[i].day,hour:fr[i].hour,sky:w.sky,wet:w.wet,windy:w.windy};};
  return {n:fr.length, festival:s(239), game:s(527), rainday:s(731), raineve:s(815)};
});
console.log('frames',info.n);
console.log('festival(239)',JSON.stringify(info.festival));
console.log('game(527)   ',JSON.stringify(info.game));
console.log('rainday(731)',JSON.stringify(info.rainday));
console.log('raineve(815)',JSON.stringify(info.raineve));
const shots = [['festival-fair',239],['gamenight-cloudy',527],['rain-midday',731],['rain-evening',815]];
for (const [tag,fr] of shots){
  await p.evaluate((fr)=>{ window.__state.anim=6.0; window.__seek(fr); }, fr);
  await p.waitForTimeout(80);
  await p.screenshot({ path:`/tmp/real-${tag}.png` });
}
console.log('errors:', errs.length ? errs.slice(0,8) : 'NONE');
await b.close();
