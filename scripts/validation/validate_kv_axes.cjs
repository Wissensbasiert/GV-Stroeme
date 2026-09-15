const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url))throw Error('Local preview required');
let browser;const results=[],errors=[];
(async()=>{
 await fs.mkdir(out,{recursive:true});browser=await chromium.launch({channel:'chrome',headless:true});
 const p=await browser.newPage({viewport:{width:2119,height:1272}});p.on('pageerror',e=>errors.push(e.message));
 await p.goto(url,{waitUntil:'networkidle'});
 assert.equal(await p.locator('#kpiTotalTonnes').textContent(),'3.839 Mio. t');
 await p.screenshot({path:path.join(out,'overview-kpi.png')});
 await p.locator('#mainNav [data-tab="tab-intermodal"]').click();
 await p.waitForFunction(()=>document.getElementById('tab-intermodal').getAttribute('aria-busy')==='false');
 if(!await p.locator('#regionSearchInput').isVisible())await p.locator('#btnToggleAnalysisPanel').click();
 await p.locator('#regionSearchInput').fill('Köln');await p.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:'Köln, Kreisfreie Stadt'}).first().click();
 await p.locator('#selectYear').selectOption('2025');
 for(const metric of ['tkm','tonnes']){
  await p.locator('#selectMetric').selectOption(metric);
  for(const direction of ['balance','all','inbound','outbound']){
   await p.locator('#selectDirection').selectOption(direction);
   for(const view of ['snapshot','trend']){
    for(const mode of ['Rail','Iww'])await p.locator(`#toggleIntermodal${mode}Structure [data-view="${view}"]`).click();
    await p.waitForTimeout(300);
    const scales=await p.evaluate(view=>['chartKvRailUnits','chartKvIwwUnits'].map(id=>{
     const c=Chart.getChart(document.getElementById(id)),s=c.scales[view==='trend'?'y':'x'];
     return{id,values:s.ticks.map(t=>t.value),labels:s.ticks.map(t=>t.label)};
    }),view);
    for(const s of scales){assert.equal(new Set(s.labels).size,s.labels.length,JSON.stringify(s));assert.ok(s.values.some(v=>v!==0));}
    results.push({metric,direction,view,scales});
    if(metric==='tkm'&&['balance','all'].includes(direction)&&view==='trend'){
     await p.screenshot({path:path.join(out,`koeln-${direction}.png`)});
     await p.locator('#enlarge-chartKvIwwUnits').click();await p.waitForTimeout(350);
     const labels=await p.evaluate(()=>Chart.getChart(document.getElementById('largeChartCanvas')).scales.y.ticks.map(t=>t.label));
     assert.equal(new Set(labels).size,labels.length);
     await p.screenshot({path:path.join(out,`koeln-${direction}-large.png`)});await p.keyboard.press('Escape');
    }
   }
  }
 }
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(out,'results.json'),JSON.stringify({results,errors},null,2));
 console.log('PASS: 32 KV axes, Cologne 2025, both metrics, four directions, Status/Dynamik, enlarged axes and national KPI.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>browser?.close());
