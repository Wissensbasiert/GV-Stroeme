/** Derive browser delivery partitions without changing source values or aggregation rules.
 * Run: node scripts/frontend/build_delivery_data.cjs [--kind summary|forecast|all] [--check]
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const processed = path.join(root, 'data/processed');
const args = process.argv.slice(2);
const check = args.includes('--check');
const kind = args.includes('--kind') ? args[args.indexOf('--kind') + 1] : 'all';
if (!['summary', 'forecast', 'all'].includes(kind)) throw new Error('Unknown delivery kind');
const summaryFields = ['by_mode_divisions', 'by_mode_divisions_tkm', 'divisions_20_tonnes', 'divisions_20_tkm'];
const forecastFields = ['relations_overall', 'by_group_relations'];
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const read = file => JSON.parse(fs.readFileSync(path.join(processed, file), 'utf8'));
let count = 0;
function emit(file, data) {
  const content = JSON.stringify(data);
  const destination = path.join(processed, file);
  if (check) {
    assert.equal(fs.readFileSync(destination, 'utf8'), content, `Stale or incomplete delivery file: ${file}`);
  } else if (!fs.existsSync(destination) || fs.readFileSync(destination, 'utf8') !== content) {
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, content, 'utf8');
  }
  count++;
  return { bytes: Buffer.byteLength(content), sha256: hash(content) };
}
function split(record, fields) {
  const detail = {}, core = {};
  for (const [key, value] of Object.entries(record)) (fields.includes(key) ? detail : core)[key] = value;
  // Equality includes string IDs, nulls, every numeric value and all dimensions.
  assert.deepEqual({ ...core, ...detail }, record);
  return [core, detail];
}
function sourceFingerprint(files) {
  return Object.fromEntries(files.map(file => [file, hash(fs.readFileSync(path.join(processed, file)))]));
}
if (kind === 'all' || kind === 'summary') {
  const source = read('web_summary_by_region.json');
  const nationalSource = fs.readFileSync(path.join(root, 'js/shared/national-summary.js'), 'utf8');
  const compute = vm.runInNewContext(`${nationalSource}\ncomputeNationalSummaries;`);
  const national = compute(source, read('national_benchmarks.json'));
  const regions = {}, files = {};
  for (const [id, years] of Object.entries(source)) {
    assert.match(id, /^[A-Za-z0-9_-]+$/);
    regions[id] = {};
    const detail = {};
    for (const [year, record] of Object.entries(years)) [regions[id][year], detail[year]] = split(record, summaryFields);
    files[`delivery/summary/${id}.json`] = emit(`delivery/summary/${id}.json`, detail);
  }
  files['web_summary_core.json'] = emit('web_summary_core.json', { format: 1, national, regions });
  emit('delivery/summary-manifest.json', { format: 1, sources: sourceFingerprint(['web_summary_by_region.json', 'national_benchmarks.json']), aggregationSha256: hash(nationalSource), files });
  console.log(`Summary core: ${files['web_summary_core.json'].bytes} bytes; ${Object.keys(regions).length} regional detail files`);
}
if (kind === 'all' || kind === 'forecast') {
  const source = read('web_forecast_2040.json');
  const core = { ...source, scenarios: {} }, regions = {}, files = {};
  for (const [scenarioId, scenario] of Object.entries(source.scenarios)) {
    core.scenarios[scenarioId] = { ...scenario, regions: {} };
    for (const [id, record] of Object.entries(scenario.regions)) {
      assert.match(id, /^[A-Za-z0-9_-]+$/);
      const [main, detail] = split(record, forecastFields);
      core.scenarios[scenarioId].regions[id] = main;
      (regions[id] ||= {})[scenarioId] = detail;
    }
  }
  for (const [id, detail] of Object.entries(regions)) files[`delivery/forecast/${id}.json`] = emit(`delivery/forecast/${id}.json`, detail);
  files['web_forecast_core.json'] = emit('web_forecast_core.json', core);
  emit('delivery/forecast-manifest.json', { format: 1, sources: sourceFingerprint(['web_forecast_2040.json']), files });
  console.log(`Forecast core: ${files['web_forecast_core.json'].bytes} bytes; ${Object.keys(regions).length} regional detail files`);
}
console.log(`${check ? 'Verified' : 'Built'} ${count} delivery files; canonical data unchanged.`);
