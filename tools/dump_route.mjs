import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT=process.env.PORT||8399;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']});
const p=await b.newPage({viewport:{width:1376,height:800}});
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`,{waitUntil:'domcontentloaded'});
await p.waitForFunction('window.__ready===true',null,{timeout:60000});
const legs=[['loc_main_square','loc_stadium'],['loc_oakside','loc_main_square'],['loc_riverside','loc_cafe'],['loc_north_gate','loc_stadium']];
for(const [f,t] of legs){
  const r=await p.evaluate(([f,t])=>{const r=window.__getRoute(f,t);return r?{n:r.pts.length,len:Math.round(r.len),pts:r.pts.map(p=>[Math.round(p.x),Math.round(p.y)])}:null;},[f,t]);
  console.log(f+'->'+t+':',r?('len='+r.len+' '+JSON.stringify(r.pts)):'NO ROUTE');
}
await b.close();
