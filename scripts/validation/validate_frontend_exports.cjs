/** Browser acceptance for enlarged charts, scoped exports and prior-year Toll hovers. */
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const url=process.argv[2],out=path.resolve(process.argv[3]||'C:/tmp/gueterstroeme-exports-qa');
if(!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/$/.test(url||''))throw Error('Local preview URL required');
let browser;const results=[],errors=[];const pass=(name,detail='')=>{results.push({name,status:'passed',detail});console.log('PASS',name,detail)};
(async()=>{
 await fs.mkdir(out,{recursive:true});browser=await chromium.launch({channel:'chrome',headless:false,args:['--window-position=-32000,-32000']});
 const context=await browser.newContext({viewport:{width:1600,height:1000},acceptDownloads:true});const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/js/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:`(()=>{window.qaMaps={};const factory=L.map;L.map=function(id,options){const map=factory(id,options);window.qaMaps[id]=map;return map;};})();\n`+await response.text()});});
 const settle=async key=>page.waitForFunction(id=>document.getElementById('tab-'+id)?.getAttribute('aria-busy')==='false',key,{timeout:60000});
 const tab=async key=>{await page.locator(`#mainNav [data-tab="tab-${key}"]`).click();await settle(key)};
 const shot=async name=>{await page.waitForTimeout(350);await page.screenshot({path:path.join(out,name+'.jpg'),type:'jpeg',quality:80})};
 const download=async(button,name)=>{const event=page.waitForEvent('download');await page.locator(button).click();await(await event).saveAs(path.join(out,name));};
 await page.goto(url,{waitUntil:'networkidle'});await settle('overview');
 assert.equal(await page.locator('#overviewLeafletMap').getAttribute('data-viewport-ready'),'true');
 const start=await page.evaluate(()=>{const m=qaMaps.overviewLeafletMap;return {zoom:m.getZoom(),center:m.getCenter(),bounds:m.getBounds()}});assert.ok(start.zoom>5);pass('Germany viewport ready on first display',JSON.stringify(start));
 await page.locator('#btnAiModal').click();assert.equal(await page.locator('[data-ai-question]').count(),5);
 for(const example of await page.locator('[data-ai-question]').all()){const question=await example.getAttribute('data-ai-question');if(!await example.isVisible())await page.locator('#aiExamplesToggle').click();await example.click();assert.equal(await page.locator('#aiQuestionInput').inputValue(),question)}
 await page.locator('#aiExamplesToggle').click();await shot('01-fuenf-ki-fragen');await page.keyboard.press('Escape');pass('All five example questions populate the input');
 const order=await page.evaluate(()=>['btnLicensesModal','btnExportModal','btnAiModal'].map(id=>document.getElementById(id).getBoundingClientRect().left));assert.ok(order[0]<order[1]&&order[1]<order[2]);
 await page.locator('#btnExportModal').click();assert.equal(await page.locator('#exportGeo').isDisabled(),true);await download('#exportExcel','uebersicht.xlsx');await shot('02-export');await page.keyboard.press('Escape');pass('Header order, Excel download, national GeoPackage blocked');
 if(!await page.locator('#regionSearchInput').isVisible())await page.locator('#btnToggleAnalysisPanel').click();await page.locator('#regionSearchInput').fill('Duisburg');await page.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:'Duisburg'}).first().click();await settle('overview');
 for(const key of ['overview','road','rail','iww','intermodal','maritime','airfreight','forecast']){
  await tab(key);
  const buttons=page.locator('.tab-pane.active .btn-chart-enlarge');let count=0;
  for(let i=0;i<await buttons.count();i++){
   const button=buttons.nth(i);if(!await button.isEnabled())continue;
   const id=(await button.getAttribute('id')).replace('enlarge-','');
   const expected=await page.evaluate(id=>{const c=Chart.getChart(id);return JSON.stringify({labels:c.data.labels,data:c.data.datasets.map(d=>d.data)})},id);
   await button.click();await page.waitForTimeout(100);
   assert.equal(await page.evaluate(()=>{const c=Chart.getChart('largeChartCanvas');return JSON.stringify({labels:c.data.labels,data:c.data.datasets.map(d=>d.data)})}),expected);
   const bounds=await page.locator('#largeChartCanvas').boundingBox();assert.ok(bounds.width>1000&&bounds.height>=400,JSON.stringify(bounds));
   if(key==='overview'&&i===0){await shot('03-diagramm-gross');await download('#largeChartPng','modal-split.png');}
   await page.keyboard.press('Escape');assert.equal(await button.evaluate(n=>n===document.activeElement),true);count++;
  }
  assert.ok(count>0,key);pass('Enlarged charts preserve data and return focus: '+key,String(count));
 }
 await tab('rail');await page.locator('#selectRailNstLevel').selectOption('20');await page.locator('.tab-pane.active .btn-chart-enlarge').first().click();assert.equal(await page.evaluate(()=>Chart.getChart('largeChartCanvas').options.scales.x.ticks.display),true);await shot('04-zwanzig-guetergruppen');await page.keyboard.press('Escape');
 await tab('airfreight');await page.locator('#selectAirfreightAirport').selectOption('EDDF');await page.locator('#btnExportModal').click();await download('#exportExcel','luftfracht-frankfurt.xlsx');await page.keyboard.press('Escape');
 await tab('overview');await page.waitForTimeout(350);await page.evaluate(()=>{qaMaps.overviewLeafletMap.setView([51.2,6.8],9,{animate:false});});await page.locator('#btnExportModal').click();assert.equal(await page.locator('#exportGeo').isEnabled(),true,await page.locator('#exportGeoScope').innerText());await download('#exportGeo','kartenausschnitt.gpkg');await page.keyboard.press('Escape');pass('Regional GeoPackage and selected-airport Excel downloaded');
 await page.setViewportSize({width:1366,height:768});await page.locator('.tab-pane.active .btn-chart-enlarge').first().click();assert.ok((await page.locator('#largeChartCanvas').boundingBox()).width>1000);await shot('05-laptop-gross');await page.keyboard.press('Escape');
 await page.setViewportSize({width:390,height:844});assert.equal(await page.locator('.tab-pane.active .btn-chart-enlarge').first().isVisible(),false);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.locator('#btnExportModal').click();await shot('06-mobil-export');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.keyboard.press('Escape');pass('Laptop enlarged chart, mobile actions hidden and export usable');
 await page.setViewportSize({width:1600,height:1000});
 // Isolated published-API-shaped fixture makes missing and zero prior values repeatable.
 const calls=[];let failPrior=false;
 await page.route('https://webgis.toll-collect.de/**/query?*',async route=>{
  const u=new URL(route.request().url()),where=u.searchParams.get('where')||'';
  if(u.searchParams.get('returnDistinctValues')==='true')return route.fulfill({json:{features:['2026-07','2025-07','2024-06'].map(m=>({attributes:{monat:Date.parse(m+'-01T00:00:00Z')}}))}});
  const month=/DATE '(\d{4}-\d{2})/.exec(where)?.[1];if(!month)return route.continue();calls.push(month);
  if(failPrior&&month==='2025-07')return route.fulfill({status:503,body:'Unavailable'});
  const direction=where.includes('richtung = 1')?1:0;
  const municipality=/ags_(?:start|ziel) = '([^']+)'/.exec(where)?.[1];
  const partners=month==='2025-07'?[['05113000','Essen',400],['05114000','Krefeld',0]]:[['05113000','Essen',600],['05114000','Krefeld',10],['05116000','Mönchengladbach',30]];
  const features=partners.map(([ags,name,trips],i)=>({type:'Feature',properties:{richtung:direction,monat:Date.parse(month+'-01T00:00:00Z'),ags_start:direction?ags:municipality,ags_ziel:direction?municipality:ags,name_start:direction?name:'Duisburg',name_ziel:direction?'Duisburg':name,anzahl_befahrungen:trips,fahrleistung_km:trips*10,distanz_km_mittelw:10,zeit_min_mittelw:20},geometry:{type:'Polygon',coordinates:[[[6.8+i*.1,51.3],[6.87+i*.1,51.3],[6.87+i*.1,51.37],[6.8+i*.1,51.37],[6.8+i*.1,51.3]]]}}));
  await route.fulfill({json:{type:'FeatureCollection',features,exceededTransferLimit:false}});
 });
 await tab('toll');if(!await page.locator('#tollMunicipalitySearchInput').isVisible())await page.locator('#btnToggleAnalysisPanel').click();await page.locator('#tollMunicipalitySearchInput').fill('Duisburg');await page.locator('#tollMunicipalityAutocompleteList .autocomplete-item').filter({hasText:'Duisburg'}).first().click();await settle('toll');await page.waitForFunction(()=>document.getElementById('tollComparisonNotice').textContent.includes('Werte in den'));
 // Request the same content function used by both municipality and connection hover controllers.
 const hover=async ags=>page.evaluate(ags=>{const m=qaMaps.tollLeafletMap;let found; m.eachLayer(layer=>{if(layer.feature?.properties?.tollRow?.partnerAgs===ags)found=layer});if(!found)throw Error('Partner not found');found.fire('mouseover',{latlng:found.getBounds().getCenter()});},ags);
 await hover('05113000');await page.waitForTimeout(850);let tooltip=await page.locator('.leaflet-tooltip').allTextContents();assert.match(tooltip.join(' '),/↗ \+200/);assert.equal(await page.locator('#tollComparisonNotice').isHidden(),true);assert.match(tooltip.join(' '),/50(?:,0)? %/);await shot('07-maut-vorjahr');
 await hover('05114000');await page.waitForTimeout(850);tooltip=await page.locator('.leaflet-tooltip').allTextContents();assert.match(tooltip.join(' '),/nicht berechenbar/);
 await hover('05116000');await page.waitForTimeout(850);tooltip=await page.locator('.leaflet-tooltip').allTextContents();assert.match(tooltip.join(' '),/Kein vergleichbarer/);
 await page.mouse.move(0,0);await page.waitForTimeout(400);await page.locator('#enlarge-chartTollDistanceClasses').click();await page.locator('#modalChartLarge.active').waitFor();assert.match(await page.locator('#largeChartContext').innerText(),/Anteil der Mautfahrten nach mittlerer Distanz/);await page.keyboard.press('Escape');
 await page.locator('#selectTollMonth').selectOption('2024-06');await settle('toll');assert.equal(await page.locator('#tollComparisonNotice').isHidden(),true);assert.match(await page.locator('#tollComparisonNotice').textContent(),/nicht verfügbar/);await hover('05113000');await page.waitForTimeout(500);assert.match((await page.locator('.leaflet-tooltip').allTextContents()).join(' '),/Juli 2026/);
 const requestsBefore=calls.length;await page.locator('#selectTollMonth').selectOption('2026-07');await settle('toll');await page.waitForTimeout(150);assert.equal(calls.length,requestsBefore);pass('Toll prior-year values, zero denominator, absent partner/month and scoped cache');
 failPrior=true;await page.locator('#selectTollDirection').selectOption('inbound');await settle('toll');await page.waitForFunction(()=>document.getElementById('tollComparisonNotice').textContent.includes('konnte nicht geladen'));assert.match(await page.locator('#tableTollRelationsBody').innerText(),/600/);failPrior=false;await page.locator('#tollComparisonNotice button').click();await page.waitForFunction(()=>document.getElementById('tollComparisonNotice').textContent.includes('Werte in den'));pass('Failed prior-year request keeps current data and retries successfully');
 assert.deepEqual(errors,[]);pass('No uncaught browser errors');
 await fs.writeFile(path.join(out,'browser-results.json'),JSON.stringify({results,errors},null,2));
})().catch(async e=>{console.error(e);try{await fs.writeFile(path.join(out,'browser-failure.json'),JSON.stringify({error:e.stack,results,errors},null,2))}catch{}process.exitCode=1}).finally(async()=>{await browser?.close()});
