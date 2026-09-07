/** Regional profile: source-backed narrative, Top 5, missing/zero forecast,
 * actual UI selection and PDF export. Dependencies/output stay outside the repo.
 * Usage: PLAYWRIGHT_MODULE_PATH=... node scripts/validation/validate_steckbrief.cjs URL OUTPUT
 */
const fs = require('node:fs/promises');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root = path.resolve(__dirname, '../..');
const url = process.argv[2];
const output = path.resolve(process.argv[3] || 'C:/tmp/gueterstroeme-steckbrief');
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/?$/.test(url || '')) throw Error('Local preview required');
const results = [], errors = [];
const record = (name,detail) => { results.push({name,detail,status:'passed'}); console.log('PASS',name); };
const read = async name => JSON.parse(await fs.readFile(path.join(root,'data/processed',name),'utf8'));
const fmt = value => new Intl.NumberFormat('de-DE',{minimumFractionDigits:0,maximumFractionDigits:1}).format(value);
let browser;
(async()=>{
 await fs.mkdir(output,{recursive:true});
 const source = await fs.readFile(path.join(root,'js/source/core-head.js'),'utf8');
 const fn = name => {const start=source.indexOf(`  function ${name}(`);assert.ok(start>=0);return source.slice(start,source.indexOf('\n  function ',start+5));};
 const forecast = await read('web_forecast_core.json');
 const summary = await read('web_summary_core.json');
 const sandbox = vm.createContext({forecastData:structuredClone(forecast)});
 vm.runInContext(fn('getProfileForecastOutlook'),sandbox);
 for(const [target,baseline,expected] of [[0,100,-100],[100,100,0],[120,100,20],[80,100,-20],[100,0,null],[null,100,null],[undefined,100,null]]){
  sandbox.forecastData={scenarios:{'2040_P1':{national:{total_tonnes:target}},'2019_BASE':{national:{total_tonnes:baseline}}}};
  assert.equal(vm.runInContext('getProfileForecastOutlook(null)?.totalChange ?? null',sandbox),expected);
 }
 record('Forecast growth, decline, unchanged, zero target and missing/zero baseline');
 // Check Top 5 independently of rendering, including aggregation of directions.
 const relationSandbox=vm.createContext({getRegionRelations:()=>({'2024':{outbound_overall:Array.from({length:7},(_,i)=>({dest_id:String(i),tonnes:i+1})),inbound_overall:[{origin_id:'0',tonnes:50}]}}),regionsData:{},forecastData:{scenarios:{'2040_P1':{regions:{test:{relations_overall:{all:Array.from({length:7},(_,i)=>({partner_id:String(i),tonnes:i+1}))}}}}}},fullCentroids:{},centroidsVp2040:{}});
 vm.runInContext(fn('getProfileRelations')+fn('getProfileForecastRelations'),relationSandbox);
 assert.equal(vm.runInContext("getProfileRelations('test','2024','Test').length",relationSandbox),5);
 assert.equal(vm.runInContext("getProfileRelations('test','2024','Test')[0].tonnes",relationSandbox),51);
 assert.equal(vm.runInContext("getProfileForecastRelations('test').length",relationSandbox),5);
 record('Top 5 sorted after inbound/outbound aggregation');
 const taxonomy=source.match(/  const NST_GROUPS_7 = (\{[\s\S]*?\n  \});/)[1];
 const wordingContext=vm.createContext({fmt:value=>fmt(value)+' %'});
 vm.runInContext(`const NST_GROUPS_7 = ${taxonomy};`+fn('getProfileDirectionalGoodsSentence'),wordingContext);
 const wording=groups=>{wordingContext.groups=groups;return vm.runInContext('getProfileDirectionalGoodsSentence(groups,fmt)',wordingContext);};
 assert.match(wording({outbound:{1:60,4:40},inbound:{1:80,4:20}}),/sowohl im Versand mit 60 % als auch im Empfang mit 80 %/);
 assert.match(wording({outbound:{1:40,4:60},inbound:{1:80,4:20}}),/Im Versand führt die Gütergruppe „Metalle und Metallerzeugnisse“ mit 60 %.*im Empfang die Gütergruppe „Erzeugnisse/);
 assert.match(wording({outbound:{1:50,4:50},inbound:{1:80,4:20}}),/zählt.*zu den größten/);
 assert.match(wording({outbound:{1:100}}),/für den Empfang liegt keine/);
 assert.match(wording({inbound:{4:100}}),/für den Versand liegt keine/);
 assert.match(wording({outbound:{1:0},inbound:{4:null}}),/keine auswertbare Güterstruktur/);
 assert.match(wording({}),/keine auswertbare Güterstruktur/);
 record('Wording handles identical/different groups, ties and missing/zero directions');

 browser=await chromium.launch({channel:'chrome',headless:false,args:['--window-position=-32000,-32000']});
 const context=await browser.newContext({viewport:{width:1479,height:912}});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url,{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelector('#tab-overview')?.getAttribute('aria-busy')==='false');
 const selectRegion=async name=>{
  if(!await page.locator('#regionSearchInput').isVisible())await page.locator('#btnToggleAnalysisPanel').click();
  await page.locator('#regionSearchInput').fill(name);
  await page.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:name}).first().click();
  await page.waitForFunction(()=>document.querySelector('#tab-overview')?.getAttribute('aria-busy')==='false');
 };
 const open=async()=>{await page.locator('#btnSteckbriefModal').click();await page.locator('#steckbriefModalBody .steckbrief-report').waitFor({timeout:45000});};
 const profiles=[];
 for(const [id,name] of [[null,'Deutschland'],['DEA12','Duisburg'],['DE300','Berlin'],['DEA31','Bottrop']]){
  if(id)await selectRegion(name);
  await open();
  const title=await page.locator('#steckbriefModalTitle').innerText();const year=title.match(/\d{4}$/)[0];
  const text=await page.locator('.steckbrief-summary').innerText();
  assert.equal(await page.locator('.steckbrief-summary p').count(),3);
  assert.match(text,/des Güteraufkommens/);assert.match(text,/größten Gütergruppen/);assert.match(text,/im Versand|Im Versand/);assert.doesNotMatch(text,/[()]/);assert.match(text,/2019/);assert.match(text,/2040/);
  const data=id?summary.regions[id][year]:summary.national[year];
  const modeSum=Object.values(data.modes_tonnes).reduce((a,b)=>a+b,0);
  for(const value of Object.values(data.modes_tonnes))assert.ok(text.includes(fmt(value/modeSum*100)+' %'));
  const groupEntries=Object.entries(data.groups_7_tonnes.all || data.groups_7_tonnes).filter(([,v])=>typeof v==='number').sort((a,b)=>b[1]-a[1]);
  const groupSum=groupEntries.reduce((a,[,v])=>a+v,0);
  for(const [,value]of groupEntries.slice(0,2))assert.ok(text.includes(fmt(value/groupSum*100)+' %'));
  const target=id?forecast.scenarios['2040_P1'].regions[id].directions_tonnes.all:forecast.scenarios['2040_P1'].national.total_tonnes;
  const base=id?forecast.scenarios['2019_BASE'].regions[id].directions_tonnes.all:forecast.scenarios['2019_BASE'].national.total_tonnes;
  assert.ok(text.includes(fmt(Math.abs((target-base)/base*100))+' %'), JSON.stringify({name,title,expected:(target-base)/base*100,text}));
  assert.match(text,target<base?/geringeres Güteraufkommen/:/höheres Güteraufkommen/);
  if(id){
   const tables=page.locator('.steckbrief-relation-table');assert.equal(await tables.count(),2);
   for(let i=0;i<2;i++)assert.equal(await tables.nth(i).locator('tbody tr').count(),5);
   assert.match(text,/Bundeswert/);assert.match(text,/bundesweit/);
   if(id==='DE300')assert.match(text,/die mengenstärkste Verkehrsbeziehung ist der Binnenverkehr in Berlin/i);
   if(id==='DEA12')assert.match(text,/Verkehrsbeziehung besteht mit Groot-Rijnmond/);
  }else{assert.doesNotMatch(text,/Bundeswert|bundesweit/);assert.equal(await page.locator('.steckbrief-relation-table').count(),0);}
  assert.doesNotMatch(text,/NaN|undefined|\uFFFD/);
  await page.screenshot({path:path.join(output,name+'.jpg'),type:'jpeg',quality:85});
  await page.pdf({path:path.join(output,name+'.pdf'),format:'A4',preferCSSPageSize:true,printBackground:true});
  profiles.push({id,name,year,text,tables:await page.locator('.steckbrief-relation-table').allInnerTexts()});
  record(name+' narrative values, relations and PDF');
  if(id==='DEA12'){
   await page.evaluate(()=>{window.__profilePrintCalls=0;window.print=()=>{window.__profilePrintCalls++;};});
   await page.locator('#btnPrintSteckbrief').click();assert.equal(await page.evaluate(()=>window.__profilePrintCalls),1);
   record('Visible PDF button calls browser print');
  }
  await page.keyboard.press('Escape');
 }
 // Global goods, direction and metric filters must not change the all-goods profile.
 const original=profiles.at(-1).text;
 if(!await page.locator('#selectMetric').isVisible())await page.locator('#btnToggleAnalysisPanel').click();
 await page.locator('#selectMetric').selectOption('tkm');await page.locator('#selectDirection').selectOption('outbound');await page.locator('#selectGlobalGroup').selectOption('1');
 await open();assert.equal(await page.locator('.steckbrief-summary').innerText(),original);await page.keyboard.press('Escape');
 record('Profile independent of module metric, direction and goods filters');
 await page.setViewportSize({width:390,height:844});await open();
 for(const width of [320,390]){
  await page.setViewportSize({width,height:844});
  const titleBox=await page.locator('#steckbriefModalTitle').boundingBox();
  const printBox=await page.locator('#btnPrintSteckbrief').boundingBox();
  assert.ok(titleBox.x+titleBox.width<=printBox.x-5,'Mobile title must not overlap print button');
  assert.equal(await page.locator('#steckbriefModalBody').evaluate(e=>e.scrollWidth>e.clientWidth+1),false);
 }
 record('Long mobile heading and print control do not overlap at 320/390px');
 await page.screenshot({path:path.join(output,'Mobil.jpg'),type:'jpeg',quality:85});
 const overflow=await page.locator('#steckbriefModalBody').evaluate(e=>e.scrollWidth>e.clientWidth+1);assert.equal(overflow,false);
 for(const table of await page.locator('.steckbrief-relation-table').all()){await table.scrollIntoViewIfNeeded();assert.equal(await table.locator('tbody tr').count(),5);}
 await page.locator('.steckbrief-sources').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'Mobil-Ende.jpg'),type:'jpeg',quality:85});
 await page.pdf({path:path.join(output,'Mobil.pdf'),format:'A4',preferCSSPageSize:true,printBackground:true});
 await page.keyboard.press('Escape');await page.setViewportSize({width:1479,height:912});await open();assert.equal(await page.locator('.steckbrief-summary').innerText(),original);
 record('Mobile scroll, both Top 5 lists, sources, PDF and return to desktop');
 assert.deepEqual(errors,[]);
 await fs.writeFile(path.join(output,'steckbrief-results.json'),JSON.stringify({results,errors,profiles},null,2),'utf8');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();});
