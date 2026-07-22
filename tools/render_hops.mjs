import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT=process.env.PORT||8399;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']});
const p=await b.newPage({viewport:{width:1376,height:800}});
p.on('pageerror',e=>console.error('[pageerror]',String(e).slice(0,400)));
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`,{waitUntil:'domcontentloaded'});
await p.waitForFunction('window.__ready===true',null,{timeout:60000});
const shots=[
  ['dog_hop', 71.3, [['loc_riverside','loc_cafe','#ff3b3b']]],
  ['fox_hop', 3.4, [['loc_oakside','loc_main_square','#00ff6a']]],
];
for(const [name,t,routes] of shots){
  await p.evaluate(([t,routes])=>{window.__seek(t); window.__state.showPins=true; window.__debugDraw(routes);}, [t,routes]);
  await p.waitForTimeout(60);
  await p.screenshot({path:`/tmp/${name}.png`});
  console.log('wrote',name,'at t',t);
}
await b.close();
