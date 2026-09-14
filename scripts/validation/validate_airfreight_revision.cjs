/** Real browser acceptance for the reviewed Eurostat airport revision. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
if(!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/$/.test(url||''))throw Error('Local URL required');
(async()=>{
  await fs.mkdir(out,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(url,{waitUntil:'networkidle'});
    await page.locator('#mainNav [data-tab="tab-airfreight"]').click();
    await page.waitForFunction(()=>document.getElementById('tab-airfreight').getAttribute('aria-busy')==='false');
    if(!await page.locator('#selectAirfreightAirport').isVisible())await page.locator('#btnToggleAnalysisPanel').click();
    await page.locator('#selectAirfreightMetric').selectOption('flights');
    await page.locator('#selectYear').selectOption('2025');
    await page.locator('#selectAirfreightAirport').selectOption('EDDP');
    assert.equal(await page.locator('#airfreightNationalValue').innerText(),'48.657 Flüge');
    assert.match(await page.locator('#airfreightYoYValue').innerText(),/-2,6/);
    assert.doesNotMatch(await page.locator('#airfreightNationalSub').innerText(),/nicht belastbar/);
    await page.screenshot({path:path.join(out,'leipzig-2025.png'),fullPage:true});
    await page.locator('#selectAirfreightAirport').selectOption('EDDF');
    assert.equal(await page.locator('#airfreightNationalValue').innerText(),'24.210 Flüge');
    await page.locator('#selectYear').selectOption('2024');
    assert.equal(await page.locator('#airfreightNationalValue').innerText(),'23.743 Flüge');
    assert.deepEqual(errors,[]);
    await fs.writeFile(path.join(out,'validation.json'),JSON.stringify({passed:true,checks:['Leipzig 2025','Vorjahresvergleich','keine Sperrmeldung','Frankfurt 2025','Frankfurt 2024','keine JavaScript-Fehler']},null,2));
    console.log('PASS: corrected 2025 airport values in the real browser; 2024 regression.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
