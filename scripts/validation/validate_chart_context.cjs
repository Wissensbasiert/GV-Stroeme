/** Local regression of chart-specific headings, regional KV and delayed loading. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const fs = require('node:fs/promises'), path = require('node:path'), assert = require('node:assert/strict');
const url = process.argv[2], out = path.resolve(process.argv[3]);
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/$/.test(url || '')) throw Error('Local preview required');
let browser;
const results = [], errors = [];
(async () => {
  await fs.mkdir(out, {recursive:true});
  browser = await chromium.launch({channel:'chrome', headless:true});
  const page = await browser.newPage({viewport:{width:1600,height:1000}});
  page.on('pageerror', error => errors.push(error.message));
  await page.route('**/js/app.js*', async route => {
    const response = await route.fetch();
    await route.fulfill({response, body:(await response.text()).replace('function setModuleLoadingState(', 'window.qaLoading = setModuleLoadingState;\n  function setModuleLoadingState(')});
  });
  await page.goto(url, {waitUntil:'networkidle'});
  const settle = key => page.waitForFunction(key => document.getElementById('tab-'+key)?.getAttribute('aria-busy') === 'false', key, {timeout:60000});
  const tab = async key => {await page.locator(`#mainNav [data-tab="tab-${key}"]`).click(); await settle(key);};
  const heading = async id => {
    await page.locator('#enlarge-'+id).click();
    await page.locator('#modalChartLarge.active').waitFor();
    await page.waitForTimeout(350);
    const text = await page.locator('#largeChartContext').textContent();
    assert.doesNotMatch(text, /Diagrammwerte|Güterfilter nicht anwendbar|Top 10|Binnenverkehr ein$/);
    results.push({id,context:text});
    await page.screenshot({path:path.join(out,`${results.length}-${id}.png`)});
    await page.keyboard.press('Escape');
    return text;
  };
  await settle('overview');
  assert.match(await heading('chartModalSplit'), /Verkehrsaufkommen/);
  for (const key of ['overview','road','rail','iww','maritime','airfreight','forecast','intermodal']) {
    await tab(key);
    for (const id of await page.locator('.tab-pane.active canvas').evaluateAll(nodes=>nodes.map(n=>n.id).filter(id=>id.startsWith('chart')))) {
      if (await page.locator('#enlarge-'+id).isEnabled()) await heading(id);
    }
    for (const toggle of await page.locator('.tab-pane.active .toggle-group:has([data-view="trend"])').evaluateAll(nodes=>nodes.map(n=>n.id).filter(Boolean))) {
      await page.locator(`#${toggle} [data-view="trend"]`).click();
      for (const id of await page.locator(`#${toggle}`).locator('xpath=ancestor::div[contains(concat(" ",normalize-space(@class)," ")," card ")][1]').locator('canvas').evaluateAll(nodes=>nodes.map(n=>n.id).filter(id=>id.startsWith('chart')))) {
        if (await page.locator('#enlarge-'+id).isEnabled()) assert.match(await heading(id), /20\d\d–20\d\d/);
      }
      await page.locator(`#${toggle} [data-view="snapshot"]`).click();
    }
  }
  const values = () => page.evaluate(()=>['chartKvRailUnits','chartKvIwwUnits'].map(id=>Chart.getChart(document.getElementById(id)).data.datasets[0].data));
  const national = await values();
  if (!await page.locator('#regionSearchInput').isVisible()) await page.locator('#btnToggleAnalysisPanel').click();
  await page.locator('#regionSearchInput').fill('Bremen');
  await page.locator('#regionAutocompleteList .autocomplete-item').filter({hasText:'Bremen, Kreisfreie Stadt'}).first().click();
  await settle('intermodal');
  const regional = await values();
  for(let i=0;i<2;i++) assert.notDeepEqual(regional[i],national[i]);
  const data = JSON.parse(await fs.readFile(path.resolve(__dirname,'../../data/processed/web_intermodal.json'),'utf8'));
  const year = await page.locator('#selectYear').inputValue();
  const rail = data.scoped_metrics_by_year[year].DE501.rail;
  const sum = category => ['outbound','inbound','binnen'].reduce((v,d)=>v+(rail[category][d]?.tonnes||0),0);
  assert.ok(Math.abs(regional[0][0]-100*sum('containers_and_swap_bodies')/sum('intermodal_load_units'))<1e-9);
  await heading('chartKvRailUnits');
  await page.locator('#selectDirection').selectOption('balance'); await settle('intermodal');
  assert.ok((await values())[0].every(Number.isFinite));
  assert.match(await heading('chartKvRailUnits'),/Saldo/);
  await page.locator('#toggleIntermodalRailStructure [data-view="trend"]').click();
  assert.match(await heading('chartKvRailUnits'),/20\d\d–20\d\d/);
  await page.locator('#selectDirection').selectOption('all');
  await tab('maritime');
  assert.equal(await page.locator('#kpiMrtmTeuTitle').textContent(),'Containerumschlag');
  await tab('forecast');
  await page.locator('#selectForecastChart2View').selectOption('kv');
  assert.doesNotMatch(await heading('chartForecastCommodityKv'),/Tonnen|Versand|Empfang/);
  // Controlled timings exercise the real loading helper without a network dependency.
  const overlay = page.locator('#tab-forecast .module-loading-overlay');
  await page.evaluate(()=>window.qaLoading('tab-forecast',true));
  await page.waitForTimeout(1100); assert.equal(await overlay.isVisible(),false);
  await page.evaluate(()=>window.qaLoading('tab-forecast',false));
  await page.waitForTimeout(1600); assert.equal(await overlay.isVisible(),false);
  await page.evaluate(()=>window.qaLoading('tab-forecast',true));
  await page.waitForTimeout(1700); assert.equal(await overlay.isVisible(),true);
  await page.screenshot({path:path.join(out,'loading-after-1500ms.png')});
  await page.evaluate(()=>window.qaLoading('tab-forecast',false));
  assert.equal(await overlay.isVisible(),false);
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(out,'results.json'),JSON.stringify({results,regional,national,errors,loading:'1100 ms hidden; cancelled timer hidden; 1700 ms visible; completion hidden'},null,2));
  console.log(`PASS: ${results.length} chart views, regional KV values, signed balances, loading threshold and cancellation.`);
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>browser?.close());
