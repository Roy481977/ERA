import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
import fs from 'fs';
const PORT=process.env.PORT||8399;
const m=JSON.parse(fs.readFileSync('web/assets/era-plate-map.json','utf8'));
const wpts=(m.water[0].pts||m.water[0]);
function pip(x,y,poly){let ins=false,j=poly.length-1;for(let i=0;i<poly.length;i++){const xi=poly[i][0],yi=poly[i][1],xj=poly[j][0],yj=poly[j][1];if(((yi>y)!=(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi))ins=!ins;j=i;}return ins;}
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']});
const p=await b.newPage({viewport:{width:1376,height:800}});
await p.goto(`http://127.0.0.1:${PORT}/compositor.html`,{waitUntil:'domcontentloaded'});
await p.waitForFunction('window.__ready===true',null,{timeout:60000});
// collect all unique (from,to) legs that entities actually traverse (moving legs + hops)
const legs=await p.evaluate(()=>{
  const fr=window.__state.frames, set=new Set(), out=[];
  const push=(a,b)=>{const k=a+'|'+b;if(a&&b&&a!==b&&!set.has(k)){set.add(k);out.push([a,b]);}};
  for(let i=0;i<fr.length;i++){const f=fr[i],g=fr[(i+1)%fr.length];const nb={};for(const e of g.entities)nb[e.id]=e;
    for(const e of f.entities){ if(e.moving&&e.from&&e.to)push(e.from,e.to); const eN=nb[e.id]; if(eN&&!e.moving&&e.place&&eN.place&&e.place!==eN.place)push(e.place,eN.place); }}
  return out;
});
const results=[];
for(const [f,t] of legs){
  const r=await p.evaluate(([f,t])=>{const r=window.__getRoute(f,t);return r?r.pts.map(p=>[p.x,p.y]):null;},[f,t]);
  if(!r){results.push([f,t,'NO_ROUTE',0]);continue;}
  // sample along polyline, count water hits
  let hits=0,samples=0;
  for(let i=1;i<r.length;i++){const [x0,y0]=r[i-1],[x1,y1]=r[i];const seg=Math.hypot(x1-x0,y1-y0),N=Math.max(2,Math.round(seg/8));for(let k=0;k<=N;k++){const tt=k/N,x=x0+(x1-x0)*tt,y=y0+(y1-y0)*tt;samples++;if(pip(x,y,wpts))hits++;}}
  results.push([f,t,r.length+'pts',hits,samples]);
}
const noroute=results.filter(r=>r[2]==='NO_ROUTE');
const water=results.filter(r=>r[3]>0);
console.log('total legs',results.length,'| no-route',noroute.length,'| cross-water',water.length);
for(const r of noroute)console.log('  NO ROUTE',r[0],'->',r[1]);
for(const r of water.sort((a,b)=>b[3]-a[3]))console.log('  WATER',r[0].replace('loc_',''),'->',r[1].replace('loc_',''),r[3]+'/'+r[4],'samples in water');
await b.close();
