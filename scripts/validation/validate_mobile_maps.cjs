/** Mobile map overlays, menu hit testing, credits and legend touch controls. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
if(!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/$/.test(url||''))throw Error('Local URL required');
let browser;const results=[],errors=[];
const pass=(name,detail)=>{results.push({name,detail,status:'passed'});console.log('PASS',name)};
(async()=>{
 await fs.mkdir(out,{recursive:true});
 browser=await chromium.launch({channel:'chrome',headless:false,args:['--window-position=-32000,-32000']});
 let p=await browser.newPage({viewport:{width:1479,height:912}});p.on('pageerror',e=>errors.push(e.message));
 await p.goto(url,{waitUntil:'networkidle'});await p.waitForTimeout(700);
 const desktop=await p.evaluate(()=>['.module-layout-grid','.bottom-split-charts-row','#overviewChoroplethLegend','#chartModalSplit','#chartCommodity'].map(s=>{const n=document.querySelector(s),r=n.getBoundingClientRect();return{s,x:r.x,y:r.y,w:r.width,h:r.height}}));
 assert.equal(await p.locator('.main-content').evaluate(n=>getComputedStyle(n).isolation),'auto');
 assert.equal(await p.locator('#overviewChoroplethLegend .legend-title').isVisible(),true);
 assert.equal(await p.locator('#overviewChoroplethLegend .btn-legend-toggle').evaluate(n=>getComputedStyle(n).backgroundImage),'none');
 if(process.argv[4]){const before=JSON.parse(await fs.readFile(process.argv[4],'utf8'));assert.deepEqual(desktop,before);pass('Desktop bounds exactly match the pre-change view',desktop)}
 await p.screenshot({path:path.join(out,'01-desktop.jpg'),type:'jpeg',quality:85});await p.close();
 p=await browser.newPage({viewport:{width:393,height:852},isMobile:true,hasTouch:true});p.on('pageerror',e=>errors.push(e.message));
 await p.goto(url,{waitUntil:'networkidle'});
 const shot=async name=>{await p.waitForTimeout(250);await p.screenshot({path:path.join(out,name+'.jpg'),type:'jpeg',quality:85})};
 const checkMap=async key=>{
  const pane=p.locator('#tab-'+key),legend=pane.locator('.choropleth-legend'),btn=legend.locator('.btn-legend-toggle');
  await p.waitForFunction(key=>document.getElementById('tab-'+key)?.getAttribute('aria-busy')==='false',key,{timeout:60000});
  await legend.scrollIntoViewIfNeeded();await p.waitForTimeout(350);
  assert.equal(await btn.getAttribute('aria-expanded'),'false');
  assert.equal(await legend.locator('.legend-title').isVisible(),false);
  const size=await btn.boundingBox();assert.ok(size.width>=44&&size.height>=44);
  const inspect=()=>pane.evaluate(n=>{const l=n.querySelector('.choropleth-legend'),a=n.querySelector('.leaflet-control-attribution'),f=l.closest('.map-container-leaflet');const lr=l.getBoundingClientRect(),ar=a.getBoundingClientRect(),fr=f.getBoundingClientRect();return{legend:lr.toJSON(),credits:ar.toJSON(),frame:fr.toJSON(),gap:ar.top-lr.bottom,creditText:a.textContent}});
  let geometry=await inspect();assert.ok(geometry.gap>=7,JSON.stringify(geometry));
  if(key==='overview'||key==='toll')await shot('02-'+key+'-symbol');
  await btn.tap();await p.waitForTimeout(300);
  assert.equal(await btn.getAttribute('aria-expanded'),'true');assert.equal(await legend.locator('.legend-title').isVisible(),true);
  geometry=await inspect();assert.ok(geometry.gap>=7,JSON.stringify(geometry));assert.ok(geometry.legend.top>=geometry.frame.top,JSON.stringify(geometry));assert.ok(geometry.credits.right<=geometry.frame.right,JSON.stringify(geometry));
  if(key==='overview'||key==='toll')await shot('03-'+key+'-legende');
  await btn.tap();await p.waitForTimeout(300);assert.equal(await btn.getAttribute('aria-expanded'),'false');
  await p.locator('#btnMobileModule').tap();await p.waitForTimeout(250);
  // Reproduce Leaflet's raised control layer while its information bubble is open.
  await pane.locator('.leaflet-container').evaluate(n=>n.classList.add('wbp-tooltip-open'));
  const occlusion=await pane.evaluate(n=>{const z=n.querySelector('.leaflet-control-zoom'),m=document.getElementById('mobileModuleMenu'),zr=z.getBoundingClientRect(),mr=m.getBoundingClientRect();const left=Math.max(zr.left,mr.left),right=Math.min(zr.right,mr.right),top=Math.max(zr.top,mr.top),bottom=Math.min(zr.bottom,mr.bottom);return{overlap:right>left&&bottom>top,menuOnTop:right>left&&bottom>top?m.contains(document.elementFromPoint((left+right)/2,(top+bottom)/2)):null}});
  if(occlusion.overlap)assert.equal(occlusion.menuOnTop,true);
  if(key==='overview'){assert.equal(occlusion.overlap,true);await shot('04-menue-ueber-zoom')}
  await pane.locator('.leaflet-container').evaluate(n=>n.classList.remove('wbp-tooltip-open'));
  await p.locator('#btnMobileModule').tap();
  pass('Mobile menu, legend and credits: '+key,{geometry,occlusion});
 };
 for(const key of ['overview','road','rail','iww','maritime','airfreight','intermodal','forecast','toll']){
  if(key!=='overview'){await p.locator('#btnMobileModule').tap();await p.locator(`#mobileModuleMenu [data-tab="tab-${key}"]`).tap()}
  await checkMap(key);
 }
 // Narrower devices and longer toll credits must still leave a real gap.
 for(const width of [320,430,768]){
  await p.setViewportSize({width,height:852});await checkMap('toll');assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);pass('No horizontal overflow at '+width);
 }
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(out,'mobile-map-results.json'),JSON.stringify({results,errors},null,2));
})().catch(async e=>{console.error(e);await fs.mkdir(out,{recursive:true});await fs.writeFile(path.join(out,'mobile-map-failure.json'),JSON.stringify({error:e.stack,results,errors},null,2));process.exitCode=1}).finally(async()=>browser?.close());
