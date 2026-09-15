const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url))throw Error('Local preview required');
let browser;const results=[],errors=[];
(async()=>{
 await fs.mkdir(out,{recursive:true});browser=await chromium.launch({channel:'chrome',headless:true});
 const p=await browser.newPage({viewport:{width:1906,height:1272}});p.on('pageerror',e=>errors.push(e.message));
 await p.route('**/js/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:'window.qaMaps={};const qaFactory=L.map;L.map=function(id,opts){const m=qaFactory(id,opts);qaMaps[id]=m;return m;};\n'+await response.text()});});
 await p.goto(url,{waitUntil:'networkidle'});await p.locator('#mainNav [data-tab="tab-forecast"]').click();
 const settle=()=>p.waitForFunction(()=>document.getElementById('tab-forecast').getAttribute('aria-busy')==='false');await settle();
 if(!await p.locator('#regionSearchInput').isVisible())await p.locator('#btnToggleAnalysisPanel').click();
 await p.locator('#regionSearchInput').fill('Rhein-Kreis Neuss');await p.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:'Rhein-Kreis Neuss'}).first().click();await settle();
 for(const scenario of ['2019_BASE','2040_P1']){
  await p.locator('#selectScenario').selectOption(scenario);await settle();await p.waitForTimeout(400);
  const result=await p.evaluate(()=>{
   const m=qaMaps.forecastLeafletMap;let region,route,point;const routes=[];
   m.eachLayer(layer=>{
    const tip=layer.getTooltip?.();if(!tip)return;
    const html=tip.getContent();if(layer.wbpExport?.code==='DEA1D')region=html;
    if(tip.options.className==='forecast-relation-leaflet-tooltip'){
     routes.push(html);
     if(html.includes('Rotterdam')&&layer.getLatLngs){route=html;const coords=layer.getLatLngs();const a=m.latLngToContainerPoint(coords[0]),b=m.latLngToContainerPoint(coords[1]),r=m.getContainer().getBoundingClientRect();point={x:r.left+(a.x+b.x)/2,y:r.top+(a.y+b.y)/2};}
    }
   });return{region,route,routes,point};
  });
  assert.ok(result.region.includes('Δ'));assert.match(result.region,/#16a34a|#dc2626/);
  assert.match(result.region,/Kombinierter Verkehr/);assert.match(result.route,/Kombinierter Verkehr/);assert.ok(result.route);assert.match(result.route,/Δ/);assert.match(result.route,/#16a34a/);assert.match(result.route,/6,2 %/);
  for(const html of result.routes)assert.ok(html.includes(scenario==='2019_BASE'?'bis 2040':'gegenüber 2019'));
  await p.mouse.move(result.point.x,result.point.y);await p.waitForTimeout(400);
  const tip=p.locator('#forecastLeafletMap .forecast-relation-leaflet-tooltip:visible');await tip.waitFor();assert.match(await tip.innerText(),/6,2 %/);
  await p.screenshot({path:path.join(out,`route-${scenario}.png`)});results.push({scenario,...result});
 }

 // Exercise actual sticky mouse moves at the western map edge, then each corner.
 await p.mouse.move(0,0);

 const target=await p.evaluate(()=>{const m=qaMaps.forecastLeafletMap;let result;m.eachLayer(l=>{if(l.wbpExport?.name?.includes('Bitburg')){window.qaEdgeLayer=l;const q=m.latLngToContainerPoint(l.getBounds().getCenter()),r=m.getContainer().getBoundingClientRect();result={x:r.left+q.x,y:r.top+q.y,name:l.wbpExport.name};}});return result;});
 assert.ok(target);
 await p.mouse.move(target.x,target.y);await p.waitForTimeout(400);
 await p.mouse.move(target.x+2,target.y+2);await p.waitForTimeout(100);
 const check=async()=>p.evaluate(()=>{const m=qaMaps.forecastLeafletMap,r=m.getContainer().getBoundingClientRect(),t=m.getContainer().querySelector('.forecast-region-leaflet-tooltip'),b=t?.getBoundingClientRect();return b?{left:b.left,top:b.top,right:b.right,bottom:b.bottom,map:{left:r.left,top:r.top,right:r.right,bottom:r.bottom},text:t.textContent}:null;});
 const assertFit=b=>{assert.ok(b);assert.ok(b.left>=b.map.left+7,JSON.stringify(b));assert.ok(b.right<=b.map.right-7,JSON.stringify(b));assert.ok(b.top>=b.map.top+7,JSON.stringify(b));assert.ok(b.bottom<=b.map.bottom-7,JSON.stringify(b));assert.match(b.text,/Kombinierter Verkehr/);};
 const edge=await check();assertFit(edge);results.push({edge});await p.screenshot({path:path.join(out,'bitburg-hover.png')});
 for(const [x,y] of [[12,12],[-12,12],[12,-12],[-12,-12]]){
  await p.evaluate(({x,y})=>{const m=qaMaps.forecastLeafletMap,s=m.getSize(),q=L.point(x<0?s.x+x:x,y<0?s.y+y:y),latlng=m.containerPointToLatLng(q);qaEdgeLayer.openTooltip(latlng);qaEdgeLayer.getTooltip().setLatLng(latlng);qaEdgeLayer.fire('mousemove',{latlng,containerPoint:q});},{x,y});
  await p.waitForTimeout(100);assertFit(await check());
 }

 // Reproduce the user's selected Ortenaukreis with the settings collapsed.
 await p.setViewportSize({width:1906,height:1272});
 if(!await p.locator('#regionSearchInput').isVisible())await p.locator('#btnToggleAnalysisPanel').click();
 await p.locator('#regionSearchInput').fill('Ortenaukreis');await p.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:'Ortenaukreis'}).first().click();await settle();
 await p.locator('#btnToggleAnalysisPanel').click();await p.waitForTimeout(1000);
 const routePoint=await p.evaluate(()=>{const m=qaMaps.forecastLeafletMap;let q;m.eachLayer(l=>{if(l.getTooltip?.()?.getContent().includes('Rotterdam')&&l.getLatLngs){const coords=l.getLatLngs(),a=m.latLngToContainerPoint(coords[0]),b=m.latLngToContainerPoint(coords[1]),r=m.getContainer().getBoundingClientRect();q={x:r.left+(a.x+b.x)/2,y:r.top+(a.y+b.y)/2};}});return q;});
 assert.ok(routePoint);await p.mouse.move(routePoint.x,routePoint.y);await p.waitForTimeout(400);
 const ortenau=p.locator('#forecastLeafletMap .forecast-relation-leaflet-tooltip:visible');await ortenau.waitFor();await p.waitForTimeout(500);assert.ok(await ortenau.isVisible());assert.match(await ortenau.innerText(),/Ortenaukreis/);await p.screenshot({path:path.join(out,'ortenau-route.png')});
 // Check every route and region tooltip through Leaflet's position updates;
 // route paths may stop propagation before the map sees mousemove.
 for(const width of [1906,1440]) {
  await p.setViewportSize({width,height:1272});await p.waitForTimeout(250);
  const placements=await p.evaluate(()=>{
   const m=qaMaps.forecastLeafletMap,checks=[];
   m.eachLayer(l=>{const t=l.getTooltip?.();if(!t?.options.className?.startsWith('forecast-'))return;
    for(const [x,y] of [[10,10],[m.getSize().x-10,10],[10,m.getSize().y-10],[m.getSize().x-10,m.getSize().y-10]]){
     l.openTooltip(m.containerPointToLatLng([x,y]));t.setLatLng(m.containerPointToLatLng([x+1,y-1]));
     const e=t.getElement(),b=e.getBoundingClientRect(),r=m.getContainer().getBoundingClientRect();
     checks.push({kind:t.options.className,ok:b.left>=r.left+7&&b.right<=r.right-7&&b.top>=r.top+7&&b.bottom<=r.bottom-7,contentFits:e.firstElementChild.scrollWidth<=e.firstElementChild.clientWidth+2});l.closeTooltip();
    }
   });return checks;
  });
  assert.ok(placements.length>0);assert.ok(placements.every(v=>v.ok&&v.contentFits),JSON.stringify(placements.filter(v=>!v.ok||!v.contentFits).slice(0,3)));results.push({width,placements:placements.length});
 }
 await p.evaluate(()=>document.getElementById('modalLicenses').classList.add('active'));
 const legal=await p.locator('#modalLicenses').textContent();assert.doesNotMatch(legal,/Exportbibliotheken und ihre Lizenztexte|Berater für wissensbasierte/);assert.match(legal,/Urheberrecht und Nutzung des Tools/);
 assert.ok(await p.locator('#modalLicenses .source-tool-meta').nth(1).evaluate(e=>parseFloat(getComputedStyle(e).marginTop))>=12);
 await p.screenshot({path:path.join(out,'sources-dialog.png')});
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(out,'results.json'),JSON.stringify({results,errors},null,2));
 console.log('PASS: real route hover Rhine-Neuss–Rotterdam, 6.2%, both scenarios; Delta/colors on regions and all displayed connections.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>browser?.close());
