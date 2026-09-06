/** Chrome regression audit. Dependencies stay outside the project.
 * PLAYWRIGHT_MODULE_PATH points to an existing external Playwright installation.
 * Usage: node scripts/validation/validate_frontend_browser.cjs URL OUTPUT_DIRECTORY
 */
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const url = process.argv[2];
const output = path.resolve(process.argv[3] || 'C:/tmp/gueterstroeme-browser-qa');
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/?$/.test(url || '')) throw new Error('A local preview URL is required');
const results = [], pageErrors = [];
const record = (name, detail = '') => { results.push({ name, status: 'passed', detail }); console.log('PASS', name, detail); };
let browser;
(async () => {
  await fs.mkdir(output, { recursive: true });
  browser = await chromium.launch({ channel: 'chrome', headless: process.env.QA_HEADLESS === '1', args: process.env.QA_HEADLESS === '1' ? [] : ['--window-position=-32000,-32000'] });
  const context = await browser.newContext({ viewport: { width: 1600, height: 950 } });
  const createPage = async () => {
    const page = await context.newPage();
    page.on('pageerror', error => pageErrors.push(error.message));
    return page;
  };
  const settle = async (page, tab) => {
    await page.waitForFunction(id => {
      const pane = document.getElementById(`tab-${id}`);
      return pane?.getAttribute('aria-busy') === 'false' && pane.dataset.loadError !== 'true';
    }, tab, { timeout: 45000 });
  };
  const tab = async (page, name) => {
    await page.locator(`#mainNav [data-tab="tab-${name}"]`).click();
    await settle(page, name);
  };
  const region = async (page, name, wait = true) => {
    if (!await page.locator('#regionSearchInput').isVisible()) await page.locator('#btnToggleAnalysisPanel').click();
    await page.locator('#regionSearchInput').fill(name);
    await page.locator('#regionAutocompleteList .autocomplete-item').filter({ hasText: name }).first().click();
    if (wait) await page.waitForFunction(() => document.querySelector('.tab-pane.active')?.getAttribute('aria-busy') === 'false');
  };
  const shot = async (page, name) => {
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(output, `${name}.jpg`), type: 'jpeg', quality: 80 });
  };
  const page = await createPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await settle(page, 'overview');
  assert.match(await page.locator('#tab-overview').innerText(), /3\.839,24 Mio\. t/);
  await region(page, 'Duisburg');
  assert.match(await page.locator('#tab-overview').innerText(), /108,22 Mio\. t/);
  record('National and Duisburg baseline values');
  for (const name of ['road', 'rail', 'iww', 'intermodal', 'maritime']) await tab(page, name);
  record('Road, rail, inland waterways, intermodal and maritime navigation');
  await tab(page, 'forecast');
  const forecast = await page.locator('#tab-forecast').innerText();
  assert.match(forecast, /103,87 Mio\. t/); assert.match(forecast, /19\.588,9/);
  await shot(page, '01-prognose-duisburg');
  await page.locator('#selectScenario').selectOption('2019_BASE');
  assert.match(await page.locator('#tab-forecast').innerText(), /2019/);
  await page.locator('#selectScenario').selectOption('2040_P1');
  await page.locator('#selectMetric').selectOption('tkm');
  assert.match(await page.locator('#tab-forecast').innerText(), /tkm/);
  await page.locator('#selectMetric').selectOption('tonnes');
  await page.locator('#selectGlobalGroup').selectOption('1');
  assert.doesNotMatch(await page.locator('#tab-forecast').innerText(), /Fachdaten konnten nicht/);
  await page.locator('#selectGlobalGroup').selectOption('ALL');
  record('Forecast partitions, both scenarios, tkm and goods filter');
  await tab(page, 'airfreight');
  await page.locator('#selectAirfreightAirport').selectOption('EDDF');
  assert.match(await page.locator('#tab-airfreight').innerText(), /215\.169,2/);
  await shot(page, '02-luftfracht-feste-einheit');
  await page.locator('#selectDirection').selectOption('balance');
  await shot(page, '03-luftfracht-salden');
  await page.locator('#selectDirection').selectOption('all');
  record('Airfreight table in tonnes and historical balances');
  for (const [button, modal] of [['btnSteckbriefModal', 'modalSteckbrief'], ['btnHelpModal', 'modalHelp'], ['btnLicensesModal', 'modalLicenses'], ['brandLogoBtn', 'modalLicenses'], ['btnAiModal', 'modalAi']]) {
    await page.locator(`#${button}`).click();
    await page.locator(`#${modal}.active`).waitFor();
    if (modal === 'modalSteckbrief') {
      await page.locator('#steckbriefModalBody .steckbrief-report').waitFor({ timeout: 45000 });
      assert.match(await page.locator('#steckbriefModalBody').innerText(), /108,2 Mio\. t/);
      await shot(page, '04-steckbrief');
    }
    await page.locator(`#${modal} .modal-close`).focus();
    await page.keyboard.press('Shift+Tab');
    assert.equal(await page.evaluate(id => document.getElementById(id).contains(document.activeElement), modal), true);
    for (let i = 0; i < 12; i++) {
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(id => document.getElementById(id).contains(document.activeElement), modal), true);
    }
    await page.keyboard.press('Escape');
    assert.equal(await page.evaluate(() => document.activeElement.id), button);
  }
  record('Five dialog openers: focus trap, Escape and focus return');
  await tab(page, 'toll');
  await page.waitForFunction(() => {
    const select = document.getElementById('selectTollMonth');
    return select && (!select.disabled || select.textContent.includes('nicht verfügbar'));
  }, null, { timeout: 45000 });
  const monthsLoaded = await page.locator('#selectTollMonth').isEnabled();
  if (monthsLoaded) {
    await page.locator('#tollMunicipalitySearchInput').fill('Duisburg');
    await page.locator('#tollMunicipalityAutocompleteList .autocomplete-item').filter({ hasText: 'Duisburg' }).first().click();
    await page.waitForFunction(() => document.getElementById('tab-toll')?.getAttribute('aria-busy') === 'false', null, { timeout: 60000 });
    const text = await page.locator('#tableTollRelationsBody').innerText();
    if (/Keine Live-Daten|nicht erreichbar/.test(text)) results.push({ name: 'Toll live relations', status: 'external-unavailable', detail: text.slice(0,200) });
    else { assert.match(text, /\d/); record('Toll live months and Duisburg relations', (await page.locator('#selectTollMonth').inputValue())); }
  } else results.push({ name: 'Toll live months', status: 'external-unavailable' });
  await shot(page, '05-maut-live');
  // Verify the actual browser transfer, not merely filenames in source code.
  const downloads = await page.evaluate(() => performance.getEntriesByType('resource').filter(r => r.name.includes('/data/processed/')).map(r => ({ file: r.name.split('/data/processed/')[1], bytes: r.decodedBodySize })));
  assert.equal(downloads.some(r => /web_forecast_2040\.json|web_summary_by_region\.json/.test(r.file)), false);
  assert.ok(downloads.some(r => r.file === 'delivery/forecast/DEA12.json'));
  record('Browser loads compact core and only selected regional forecast details');
  await tab(page, 'airfreight');
  for (const [width, height, name] of [[1366,768,'06-laptop'],[390,844,'07-mobil']]) {
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(700);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await shot(page, name);
  }
  record('Laptop and mobile without horizontal page overflow');
  // A fresh page exercises real failure/retry paths without a warm in-memory cache.
  const recovery = await createPage();
  let summaryAttempts = 0;
  await recovery.route('**/web_summary_core.json', route => ++summaryAttempts === 1 ? route.abort() : route.continue());
  await recovery.goto(url, { waitUntil: 'networkidle' });
  await recovery.locator('#tab-overview[data-load-error="true"] .data-retry-button').waitFor();
  await shot(recovery, '08-startfehler-wiederholen');
  await recovery.locator('#tab-overview .data-retry-button').click();
  await settle(recovery, 'overview');
  assert.equal(summaryAttempts, 2);
  assert.match(await recovery.locator('#tab-overview').innerText(), /3\.839,24 Mio\. t/);
  record('Initial summary failure recovers without page reload');
  let regionAttempts = 0;
  await recovery.route('**/delivery/summary/DEA12.json', route => ++regionAttempts === 1 ? route.abort() : route.continue());
  await region(recovery, 'Duisburg');
  await recovery.locator('#tab-overview[data-load-error="true"] .data-retry-button').click();
  await settle(recovery, 'overview');
  assert.equal(regionAttempts, 2);
  assert.match(await recovery.locator('#tab-overview').innerText(), /108,22 Mio\. t/);
  record('Regional summary failure recovers');
  let airAttempts = 0;
  await recovery.route('**/web_airfreight.json*', route => ++airAttempts === 1 ? route.abort() : route.continue());
  await recovery.locator('#mainNav [data-tab="tab-airfreight"]').click();
  await recovery.locator('#tab-airfreight[data-load-error="true"] .data-retry-button').click();
  await settle(recovery, 'airfreight');
  assert.equal(airAttempts, 2); record('Deferred module failure recovers');
  let forecastAttempts = 0, forecastRegionAttempts = 0;
  await recovery.route('**/web_forecast_core.json', route => ++forecastAttempts === 1 ? route.abort() : route.continue());
  await recovery.route('**/delivery/forecast/DEA12.json', route => ++forecastRegionAttempts === 1 ? route.abort() : route.continue());
  await recovery.locator('#mainNav [data-tab="tab-forecast"]').click();
  await recovery.locator('#tab-forecast[data-load-error="true"] .data-retry-button').click();
  await recovery.locator('#tab-forecast[data-load-error="true"] .data-retry-button').click();
  await settle(recovery, 'forecast');
  assert.equal(forecastAttempts, 2); assert.equal(forecastRegionAttempts, 2);
  assert.match(await recovery.locator('#tab-forecast').innerText(), /19\.588,9/);
  record('Forecast core and relation-partition failures recover independently');
  // The public API also offers an explicit retry for months and relation requests.
  let tollMonthAttempts = 0, tollRelationAttempts = 0;
  await recovery.route('**/mautdaten_bund_monat_sz/FeatureServer/0/query?*', route => {
    const query = new URL(route.request().url()).searchParams;
    if (query.get('outFields') === 'monat' && ++tollMonthAttempts === 1) return route.abort();
    if (query.get('f') === 'geojson' && ++tollRelationAttempts === 1) return route.abort();
    return route.continue();
  });
  await tab(recovery, 'toll');
  await recovery.locator('#btnRetryToll').waitFor({ state: 'visible' });
  await recovery.locator('#btnRetryToll').click();
  await recovery.waitForFunction(() => !document.getElementById('selectTollMonth').disabled, null, { timeout: 45000 });
  await recovery.locator('#tollMunicipalitySearchInput').fill('Duisburg');
  await recovery.locator('#tollMunicipalityAutocompleteList .autocomplete-item').filter({ hasText: 'Duisburg' }).first().click();
  await recovery.locator('#btnRetryToll').waitFor({ state: 'visible' });
  await recovery.locator('#btnRetryToll').click();
  await settle(recovery, 'toll');
  await recovery.waitForFunction(() => document.getElementById('tableTollRelationsBody').querySelectorAll('tr').length > 1, null, { timeout: 45000 });
  assert.equal(tollMonthAttempts, 2); assert.ok(tollRelationAttempts >= 2);
  assert.equal(await recovery.locator('#btnRetryToll').isVisible(), false);
  record('Toll month and relation failures recover through the visible retry action');
  await tab(recovery, 'overview');
  await recovery.route('**/nuts3_de_2016_display.geojson', async route => { const response = await route.fetch(); await new Promise(r=>setTimeout(r,800)); await route.fulfill({response}); });
  await recovery.locator('#selectYear').selectOption('2016');
  await recovery.locator('#selectYear').selectOption('2024');
  await settle(recovery, 'overview');
  await recovery.waitForTimeout(1000);
  assert.match(await recovery.locator('#tab-overview').innerText(), /\(2024\)/);
  assert.equal(await recovery.locator('#selectYear').inputValue(), '2024');
  record('Latest year wins when older geometry finishes later');
  await recovery.route('**/delivery/summary/DE600.json', async route => { await new Promise(r=>setTimeout(r,800)); await route.abort(); });
  await region(recovery, 'Hamburg', false);
  await region(recovery, 'Berlin', false);
  await settle(recovery, 'overview');
  await recovery.waitForTimeout(1100);
  assert.match(await recovery.locator('#regionSearchInput').inputValue(), /Berlin/);
  assert.equal(await recovery.locator('#tab-overview').getAttribute('data-load-error'), null);
  record('A late failure from an older region cannot replace the latest selection');
  assert.deepEqual(pageErrors, []);
  record('No JavaScript runtime errors');
  await fs.writeFile(path.join(output, 'browser-results.json'), JSON.stringify({ results, downloads, pageErrors }, null, 2), 'utf8');
})().catch(async error => {
  console.error(error);
  await fs.mkdir(output, { recursive: true });
  await fs.writeFile(path.join(output, 'browser-results.json'), JSON.stringify({ results, pageErrors, failure: error.stack }, null, 2), 'utf8');
  process.exitCode = 1;
}).finally(async () => { await browser?.close(); });
