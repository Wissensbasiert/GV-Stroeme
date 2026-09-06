/** Chart layout acceptance: meaningful plot height, header action, NST resize and keyboard legend. */
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const url = process.argv[2], out = path.resolve(process.argv[3]);
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/$/.test(url || '')) throw Error('Local URL required');
let browser;
const results = [], errors = [];
const pass = (name, detail) => { results.push({name, detail, status:'passed'}); console.log('PASS', name, JSON.stringify(detail || '')); };
(async () => {
  await fs.mkdir(out, {recursive:true});
  browser = await chromium.launch({channel:'chrome',headless:false,args:['--window-position=-32000,-32000']});
  const p = await browser.newPage({viewport:{width:2119,height:1272}});
  p.on('pageerror', e => errors.push(e.message));
  const settle = async key => { await p.waitForFunction(key => document.getElementById('tab-'+key)?.getAttribute('aria-busy') === 'false', key, {timeout:60000}); await p.waitForTimeout(350); };
  const tab = async key => { await p.locator(`#mainNav [data-tab="tab-${key}"]`).click(); await settle(key); };
  const shot = async name => { await p.waitForTimeout(1100); return p.screenshot({path:path.join(out,name+'.jpg'),type:'jpeg',quality:85}); };
  const metrics = id => p.evaluate(id => {
    const c = Chart.getChart(id), w = c.canvas.closest('.chart-canvas-wrap');
    return {height:c.height, plot:c.chartArea.height, wrap:w.clientHeight, legend:!!w.querySelector('.chart-scroll-legend'), plotWrapper:!!w.querySelector('.chart-plot-content'), scroll:!!w.querySelector('.chart-scroll-content')};
  }, id);
  await p.goto(url, {waitUntil:'networkidle'}); await settle('overview');
  let buttonCount = 0;
  for (const key of ['overview','road','rail','iww','maritime','airfreight','intermodal','forecast','toll']) {
    await tab(key);
    const buttons = p.locator('.tab-pane.active .btn-chart-enlarge');
    for (let i=0;i<await buttons.count();i++) {
      const button = buttons.nth(i);
      console.log('CHECK', key, i);
      assert.equal(await button.isEnabled(), true);
      assert.equal(await button.getAttribute('title'), null);
      assert.equal(await button.evaluate(n=>n.closest('.card').scrollLeft),0);
      assert.equal(await button.getAttribute('aria-label'), 'Diagramm vergrößern');
      assert.ok(await button.evaluate(n => {const h=n.closest('.card-header'),r=n.getBoundingClientRect(),q=h?.getBoundingClientRect();return q&&r.top>=q.top&&r.bottom<=q.bottom&&r.right<=q.right}));
      await button.scrollIntoViewIfNeeded(); await p.waitForTimeout(150);
      await p.mouse.move(0,0); await button.hover(); await p.locator('#chartExpandHint').waitFor({state:'visible'});
      assert.equal(await p.locator('#chartExpandHint').evaluate(n=>getComputedStyle(n).backgroundColor), 'rgb(255, 255, 255)');
      if (key==='overview' && i===1) await shot('01-heller-hinweis-kopfzeile');
      await button.click(); await p.locator('#modalChartLarge.active').waitFor();
      assert.equal(await p.locator('#chartExpandHint').isHidden(), true);
      assert.ok(await p.evaluate(()=>Chart.getChart('largeChartCanvas').height>300));
      await p.keyboard.press('Escape');
      assert.equal(await button.evaluate(n=>document.activeElement===n), true);
      await p.keyboard.press('Escape');
      assert.equal(await p.locator('#chartExpandHint').isHidden(), true);
      buttonCount++;
    }
  }
  assert.equal(buttonCount, 12); pass('All 12 header actions, white hover, popup and focus return');
  await tab('overview');
  for (const [width,height] of [[2119,1272],[1479,912],[1366,768],[1200,800],[390,844]]) {
    await p.setViewportSize({width,height});
    for (const mode of ['snapshot','trend']) {
      await p.locator(`#toggleCommodityGroup [data-view="${mode}"]`).click();
      await p.locator(`#toggleModalSplitGroup [data-view="${mode}"]`).click();
      await p.waitForTimeout(400);
      const goods = await metrics('chartCommodity'), modal = await metrics('chartModalSplit');
      assert.ok(goods.plot >= 130, JSON.stringify({width,mode,goods}));
      assert.ok(modal.plot >= 130, JSON.stringify({width,mode,modal}));
      assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      if (mode==='trend') {
        const legend = p.locator('#chartCommodity-legend');
        assert.equal(await legend.locator('button').count(),7);
        const item = legend.locator('button').first();
        await item.focus(); await p.keyboard.press('Enter');
        assert.equal(await p.evaluate(()=>Chart.getChart('chartCommodity').isDatasetVisible(0)),false);
        if (width>767) {
          await p.locator('#enlarge-chartCommodity').click(); await p.locator('#modalChartLarge.active').waitFor();
          assert.equal(await p.evaluate(()=>Chart.getChart('largeChartCanvas').isDatasetVisible(0)),false);
          assert.equal(await p.evaluate(()=>Chart.getChart('largeChartCanvas').options.plugins.legend.display),true);
          await p.keyboard.press('Escape');
        }
        await item.click(); assert.equal(await item.getAttribute('aria-pressed'),'true');
        await legend.locator('button').last().scrollIntoViewIfNeeded();
        assert.equal(await legend.locator('button').last().isVisible(),true);
        await legend.evaluate(n=>{n.scrollTop=0});
        await p.locator('#chartCommodity').scrollIntoViewIfNeeded();
        await p.mouse.move(0,0);
        await shot(`02-dynamik-${width}`);
      }
      pass(`Readable overview ${width}x${height} ${mode}`,{goods,modal});
    }
    if (width<768) assert.equal(await p.locator('#enlarge-chartCommodity').isHidden(),true);
  }
  // Return to an ordinary desktop navigation after the mobile menu takes over.
  await p.setViewportSize({width:2119,height:1272});
  for (const [width,height] of [[2119,1272],[1479,912],[1366,768]]) {
    await p.setViewportSize({width,height});
    for (const [key,label] of [['rail','Rail'],['iww','Iww'],['maritime','Maritime']]) {
      await tab(key);
      for (const mode of ['snapshot','trend']) {
        await p.locator(`#toggle${label}CommodityGroup [data-view="${mode}"]`).click();
        await p.locator(`#select${label}NstLevel`).selectOption('7'); await p.waitForTimeout(400);
        const id = `chart${label}Commodity`, before = await metrics(id);
        assert.ok(before.plot>=130,JSON.stringify({width,key,mode,before}));
        for (let n=0;n<2;n++) {
          await p.locator(`#select${label}NstLevel`).selectOption('20'); await p.waitForTimeout(350);
          const detailed = await metrics(id);
          assert.equal(mode==='snapshot'?detailed.scroll:detailed.legend,true);
          await p.locator(`#select${label}NstLevel`).selectOption('7'); await p.waitForTimeout(350);
          const after = await metrics(id);
          assert.ok(Math.abs(after.height-before.height)<=2,JSON.stringify({id,mode,before,after}));
          assert.equal(after.plotWrapper,false); assert.equal(after.scroll,false);
        }
        pass(`NST 7-20-7 ${key} ${mode} ${width}`,before);
        if (key==='rail' && mode==='trend') await shot(`03-schiene-nach-wechsel-${width}`);
      }
    }
  }
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(out,'chart-layout-results.json'),JSON.stringify({results,errors},null,2));
})().catch(async error=>{console.error(error);await fs.mkdir(out,{recursive:true});await fs.writeFile(path.join(out,'chart-layout-failure.json'),JSON.stringify({error:error.stack,results,errors},null,2));process.exitCode=1}).finally(async()=>browser?.close());
