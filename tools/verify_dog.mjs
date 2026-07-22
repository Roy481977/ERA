import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT=process.env.PORT||8399;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']});
const p=await b.newPage({viewport:{width:1376,height:800}});
p.on('pageerror',e=>console.error('[pageerror]',String(e).slice(0,400)));
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`,{waitUntil:'domcontentloaded'});
await p.waitForFunction('window.__ready===true',null,{timeout:60000});
// sample dog rendered pos across the main_square->stadium hop (tick 191->192)
for(const t of [191.1,191.4,191.7,191.95]){
  const info=await p.evaluate((t)=>{
    window.__seek(t);
    const lf=(window.__state.lastFigs||[]).find(l=>l.id==='the_old_dog');
    return lf?{sx:Math.round(lf.sx),sy:Math.round(lf.sy)}:null;
  }, t);
  console.log('t',t,'dog screen',JSON.stringify(info));
}
// render one with route overlay + crop near dog path
await p.evaluate((t)=>{window.__seek(t); window.__state.showPins=true; window.__debugDraw([['loc_main_square','loc_stadium','#ff3b3b']]);}, 191.5);
await p.waitForTimeout(60);
await p.screenshot({path:'/tmp/dog_day.png'});
console.log('wrote dog_day');
await b.close();
