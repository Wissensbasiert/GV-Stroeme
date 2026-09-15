const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url))throw Error('Local preview required');
let browser;const results=[],errors=[];
(async()=>{
 await fs.mkdir(out,{recursive:true});browser=await chromium.launch({channel:'chrome',headless:true});
 const p=await browser.newPage({viewport:{width:2119,height:1272}});p.on('pageerror',e=>errors.push(e.message));
 await p.route('**/js/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:'window.qaMaps={};const qaMapFactory=L.map;L.map=function(id,options){const map=qaMapFactory(id,options);window.qaMaps[id]=map;return map;};\n'+await response.text()});});
 await p.goto(url,{waitUntil:'networkidle'});
 await p.locator('#mainNav [data-tab="tab-airfreight"]').click();
 await p.waitForFunction(()=>document.getElementById('tab-airfreight').getAttribute('aria-busy')==='false');
 if(!await p.locator('#selectTopX').isVisible())await p.locator('#btnToggleAnalysisPanel').click();
 await p.locator('#selectTopX').selectOption('20');
 assert.equal(await p.locator('#airfreightAirportCount').textContent(),'18');
 assert.doesNotMatch(await p.locator('#airfreightAirportCountSub').textContent(),/Nullwerte/);
 for(const name of ['Bremen','Paderborn/Lippstadt','Erfurt-Weimar','Hamburg']){
  const target=await p.evaluate(name=>{
   const c=Chart.getChart(document.getElementById('chartAirfreightAirports')),i=c.data.labels.indexOf(name);if(i<0)throw Error(name);
   const r=c.canvas.getBoundingClientRect(),y=r.top+c.scales.y.getPixelForValue(i);
   let mapValue;
   qaMaps.airfreightLeafletMap.eachLayer(layer=>{if(layer.wbpExport?.name===name){const n=document.createElement('div');n.innerHTML=layer.getTooltip().getContent();mapValue=n.querySelector('.map-tooltip-value').textContent;}});
   return{x:r.left+c.chartArea.right-10,y,axisX:r.left+c.scales.y.right-10,mapValue};
  },name);
  assert.ok(target.mapValue,name);
  await p.mouse.move(target.x,target.y);
  const tip=p.locator('#chart-hover-tooltip-chartAirfreightAirports.is-visible');await tip.waitFor();
  const text=await tip.innerText();assert.ok(text.includes(name),text);assert.ok(text.includes(target.mapValue),text);
  await p.mouse.move(target.axisX,target.y);
  const axis=p.locator('#chart-axis-label-tooltip-chartAirfreightAirports.is-visible');await axis.waitFor();assert.equal(await axis.textContent(),name);
  results.push({name,text,mapValue:target.mapValue});
 }
 await p.mouse.move(0,0);await p.screenshot({path:path.join(out,'airports-18.png')});
 await p.locator('#enlarge-chartAirfreightAirports').click();await p.waitForTimeout(350);
 const point=await p.evaluate(()=>{const c=Chart.getChart(document.getElementById('largeChartCanvas')),i=c.data.labels.indexOf('Bremen'),r=c.canvas.getBoundingClientRect();return{x:r.left+c.chartArea.right-10,y:r.top+c.scales.y.getPixelForValue(i)};});
 await p.mouse.move(point.x,point.y);await p.waitForTimeout(200);
 const large=await p.evaluate(()=>{const t=Chart.getChart(document.getElementById('largeChartCanvas')).tooltip;return{title:t.title,body:t.body};});
 assert.equal(large.title[0],'Bremen');assert.ok(JSON.stringify(large.body).includes(results[0].mapValue));
 await p.screenshot({path:path.join(out,'bremen-large-hover.png')});await p.keyboard.press('Escape');
 await p.locator('#mainNav [data-tab="tab-forecast"]').click();await p.waitForFunction(()=>document.getElementById('tab-forecast').getAttribute('aria-busy')==='false');
 await p.locator('#selectMetric').selectOption('tkm');
 const data=JSON.parse(await fs.readFile(path.resolve(__dirname,'../../data/processed/web_forecast_core.json'),'utf8'));
 for(const scenario of ['2019_BASE','2040_P1']){
  await p.locator('#selectScenario').selectOption(scenario);
  await p.waitForFunction(()=>document.getElementById('tab-forecast').getAttribute('aria-busy')==='false');
  await p.waitForTimeout(500);
  const tip=await p.evaluate(()=>{
   let result;qaMaps.forecastLeafletMap.eachLayer(layer=>{if(layer.wbpExport?.name==='Teltow-Fläming'){const q=qaMaps.forecastLeafletMap.latLngToContainerPoint(layer.getBounds().getCenter()),r=qaMaps.forecastLeafletMap.getContainer().getBoundingClientRect();result={code:layer.wbpExport.code,html:layer.getTooltip().getContent(),x:r.left+q.x,y:r.top+q.y};}});return result;
  });
  assert.ok(tip);assert.match(tip.html,/Kombinierter Verkehr/);assert.doesNotMatch(tip.html,/Modal Split|Netto-Saldo/);assert.match(tip.html,/Versand \+ Empfang \+ Binnenverkehr/);
  assert.ok(tip.html.includes(scenario==='2019_BASE'?'Erwartete Veränderung bis 2040':'Veränderung gegenüber 2019'));
  const base=data.scenarios['2019_BASE'].regions[tip.code].directions_tkm.all,future=data.scenarios['2040_P1'].regions[tip.code].directions_tkm.all;
  assert.ok(tip.html.includes(((future-base)/base*100).toLocaleString('de-DE',{maximumFractionDigits:1})+' %'));
  await p.mouse.move(tip.x,tip.y);await p.waitForTimeout(350);
  assert.ok((await p.locator('#forecastLeafletMap .leaflet-tooltip:visible').innerText()).includes('Teltow-Fläming'));
  results.push({scenario,...tip});await p.screenshot({path:path.join(out,`forecast-${scenario}.png`)});
 }
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(out,'results.json'),JSON.stringify({results,large,errors},null,2));
 console.log('PASS: 18 active airports, four small-bar/axis hover pairs with map-identical values, enlarged hover, 2019/2040 forecast comparison.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>browser?.close());
