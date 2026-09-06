/** Mobile presentation tabs: preserved filters, real controls, map state and desktop geometry. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
if(!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/$/.test(url||''))throw Error('Local URL required');
let browser;const results=[],errors=[];const pass=(name,detail)=>{results.push({name,detail,status:'passed'});console.log('PASS',name)};
(async()=>{
 await fs.mkdir(out,{recursive:true});browser=await chromium.launch({channel:'chrome',headless:false,args:['--window-position=-32000,-32000']});
 let p=await browser.newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto(url,{waitUntil:'networkidle'});
 const baseline=process.argv[4]?JSON.parse(await fs.readFile(process.argv[4],'utf8')):null;
 const modules=['overview','road','rail','iww','maritime','airfreight','intermodal','forecast','toll'];
 for(const [width,height] of [[1479,912],[2119,1272]]){
  await p.setViewportSize({width,height});
  for(const key of modules){
   await p.locator(`#mainNav [data-tab="tab-${key}"]`).click();await p.waitForFunction(key=>document.getElementById('tab-'+key).getAttribute('aria-busy')==='false',key,{timeout:60000});await p.waitForTimeout(500);
   const boxes=await p.evaluate(()=>[...document.querySelectorAll('.tab-pane.active .module-layout-grid,.tab-pane.active .card,.tab-pane.active canvas')].map(n=>{const r=n.getBoundingClientRect();return{cl:n.className,x:r.x,y:r.y,w:r.width,h:r.height}}));
   if(baseline){const expected=baseline[width+'-'+key];assert.equal(boxes.length,expected.length);boxes.forEach((box,i)=>{for(const field of ['x','y','w','h'])assert.ok(Math.abs(box[field]-expected[i][field])<=1,JSON.stringify({width,key,i,field,before:expected[i][field],after:box[field]}))})}
   assert.equal(await p.locator('.tab-pane.active .mobile-analysis-navigation').isHidden(),true);
   for(const view of ['map','relations','charts'])assert.equal(await p.locator(`.tab-pane.active [data-mobile-view-panel="${view}"]`).isVisible(),true);
   pass('Desktop unchanged: '+width+' '+key);
  }
 }
 await p.close();p=await browser.newPage({viewport:{width:393,height:852},hasTouch:true,isMobile:true});p.on('pageerror',e=>errors.push(e.message));
 await p.route('**/js/app.js*',async route=>{const r=await route.fetch();await route.fulfill({response:r,body:`(()=>{window.qaMaps={};const original=L.map;L.map=function(id,options){const map=original(id,options);qaMaps[id]=map;return map;};})();\n`+await r.text()})});
 await p.goto(url,{waitUntil:'networkidle'});
 const pane=()=>p.locator('.tab-pane.active');
 const settle=async key=>{await p.waitForFunction(key=>document.getElementById('tab-'+key).getAttribute('aria-busy')==='false',key,{timeout:60000});await p.waitForTimeout(400)};
 const tab=async key=>{await p.locator('#btnMobileModule').tap();await p.locator(`#mobileModuleMenu [data-tab="tab-${key}"]`).tap();await settle(key)};
 const view=async name=>{await pane().locator(`.mobile-analysis-tabs [data-view="${name}"]`).tap();await p.waitForTimeout(350)};
 const checkView=async name=>{for(const key of ['map','relations','charts']){assert.equal(await pane().locator(`[data-mobile-view-panel="${key}"]`).isVisible(),key===name);assert.equal(await pane().locator(`[data-mobile-view-panel="${key}"]`).evaluate(n=>n.inert),key!==name)}assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)};
 const shot=async name=>{await pane().locator('.mobile-analysis-navigation').scrollIntoViewIfNeeded();await p.waitForTimeout(1100);await p.screenshot({path:path.join(out,name+'.jpg'),type:'jpeg',quality:85})};
 for(const key of modules){
  if(key!=='overview')await tab(key);else await settle(key);
  const hint=await pane().locator('.mobile-analysis-hint').innerText();assert.match(hint,/Aktuell → Raum & Zeit/);assert.doesNotMatch(hint,/Aktuelle Einstellungen/);
  for(const name of ['map','relations','charts']){await view(name);await checkView(name)}
  const charts=await pane().locator('[data-mobile-view-panel="charts"] canvas').evaluateAll(nodes=>nodes.map(n=>({id:n.id,w:Chart.getChart(n)?.width,h:Chart.getChart(n)?.height})));
  assert.ok(charts.every(c=>c.w>=200&&c.h>=180),JSON.stringify({key,charts}));
  await pane().locator('.mobile-analysis-settings').tap();
  const target=key==='airfreight'?'selectAirfreightAirport':key==='maritime'?'selectMaritimePort':key==='toll'?'tollMunicipalitySearchInput':'regionSearchInput';
  assert.equal(await p.evaluate(()=>document.activeElement.id),target);assert.equal(await p.locator('#analysisPanelBody').isVisible(),true);
  await p.locator('#btnToggleAnalysisPanel').tap();await view('map');
  if(key==='overview')await shot('01-karte-ohne-auswahl');
  pass('Three mobile views and correct settings link: '+key,charts);
 }
 await tab('overview');await pane().locator('.mobile-analysis-settings').tap();await p.locator('#regionSearchInput').fill('Duisburg');await p.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:'Duisburg'}).first().tap();await settle('overview');
 assert.match(await pane().locator('.mobile-analysis-title').innerText(),/Duisburg/);await checkView('map');
 await p.locator('#btnToggleAnalysisPanel').tap();await pane().locator('.mobile-analysis-relations').tap();await checkView('relations');
 assert.match(await p.locator('#tableTopRelationsBody').innerText(),/\d/);await shot('02-relationen-duisburg');
 const region=await p.locator('#summaryRegion').innerText();await view('charts');assert.equal(await p.locator('#summaryRegion').innerText(),region);
 // Open settings from a non-map view; changing the year must not change the view.
 await pane().locator('.mobile-analysis-settings').tap();await p.locator('#selectYear').selectOption('2023');await settle('overview');await checkView('charts');assert.equal(await p.locator('#summaryRegion').innerText(),region);await p.locator('#btnToggleAnalysisPanel').tap();await shot('03-diagramme-duisburg');
 await view('map');await p.locator('#btnExportModal').tap();await p.locator('#modalExport.active').waitFor();assert.equal(await p.locator('#exportChartSelect option').count(),2);await p.keyboard.press('Escape');pass('Region/year preserved and exports retain both charts from the map view');
 // A real map tap selects Berlin without forcing the relations view.
 await pane().locator('[data-mobile-view-panel="map"]').scrollIntoViewIfNeeded();
 await p.evaluate(()=>{qaMaps.overviewLeafletMap.setView([52.52,13.405],8,{animate:false});});await p.waitForTimeout(400);
 const pt=await p.evaluate(()=>{const m=qaMaps.overviewLeafletMap,q=m.latLngToContainerPoint([52.52,13.405]),r=m.getContainer().getBoundingClientRect();return{x:r.left+q.x,y:r.top+q.y}});await p.touchscreen.tap(pt.x,pt.y);await settle('overview');assert.match(await pane().locator('.mobile-analysis-title').innerText(),/Berlin/);await checkView('map');
 const camera=await p.evaluate(()=>{const m=qaMaps.overviewLeafletMap;return{lat:m.getCenter().lat,lng:m.getCenter().lng,zoom:m.getZoom()}});await view('relations');await view('charts');await view('map');const restored=await p.evaluate(()=>{const m=qaMaps.overviewLeafletMap;return{lat:m.getCenter().lat,lng:m.getCenter().lng,zoom:m.getZoom()}});assert.deepEqual(restored,camera);pass('Map selection does not navigate; view switches retain map center and zoom');
 await pane().locator('.mobile-analysis-settings').tap();await p.locator('#btnClearRegion').tap();await settle('overview');await p.locator('#btnToggleAnalysisPanel').tap();assert.match(await pane().locator('.mobile-analysis-title').innerText(),/Deutschland aktiv/);assert.equal(await pane().locator('.mobile-analysis-relations').isHidden(),true);pass('Clear selection restores the mobile instructions');
 await pane().locator('.mobile-analysis-tabs [data-view="map"]').focus();await p.keyboard.press('ArrowRight');await checkView('relations');await p.keyboard.press('End');await checkView('charts');pass('Keyboard tab navigation');
 for(const width of [320,430,768,900]){await p.setViewportSize({width,height:852});for(const name of ['map','relations','charts']){await view(name);await checkView(name)}pass('Responsive views at '+width)}
 await p.setViewportSize({width:1479,height:912});await p.waitForTimeout(500);assert.equal(await pane().locator('.mobile-analysis-navigation').isHidden(),true);for(const name of ['map','relations','charts']){const panel=pane().locator(`[data-mobile-view-panel="${name}"]`);assert.equal(await panel.isVisible(),true);assert.equal(await panel.evaluate(n=>n.inert),false)}pass('Resizing to desktop restores all panels');
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(out,'mobile-views-results.json'),JSON.stringify({results,errors},null,2));
})().catch(async e=>{console.error(e);await fs.mkdir(out,{recursive:true});await fs.writeFile(path.join(out,'mobile-views-failure.json'),JSON.stringify({error:e.stack,results,errors},null,2));process.exitCode=1}).finally(async()=>browser?.close());
