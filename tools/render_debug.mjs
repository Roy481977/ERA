import { createRequire } from 'module';
const require = createRequire('/home/claude/plate_tools/');
const { chromium } = require('playwright');
const PORT = process.env.PORT || 8399;
const W=1376,H=800;
const browser = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium',
  args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox','--no-sandbox']});
const page = await browser.newPage({ viewport:{width:W,height:H}});
page.on('pageerror',e=>console.error('[pageerror]',String(e).slice(0,400)));
await page.goto(`http://127.0.0.1:${PORT}/compositor.html`,{waitUntil:'domcontentloaded'});
await page.waitForFunction('window.__ready===true',null,{timeout:60000});
await page.evaluate((n)=>window.__seek(n), 84);
// dog teleport legs + fox leg
const routes=[
  ['loc_riverside','loc_cafe','#ff3b3b'],
  ['loc_cafe','loc_main_square','#ff8c00'],
  ['loc_main_square','loc_stadium','#ffd000'],
  ['loc_oakside','loc_main_square','#00ff6a'],
];
await page.evaluate((r)=>window.__debugDraw(r), routes);
await page.screenshot({path:'/tmp/dbg_graph.png'});
console.log('wrote /tmp/dbg_graph.png');
await browser.close();
