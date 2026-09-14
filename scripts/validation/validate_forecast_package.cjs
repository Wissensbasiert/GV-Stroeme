/** Execute the real forecast loader against only the files of a delivery package. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const sourceRoot = path.resolve(__dirname, '../..');
const publicRoot = path.resolve(process.argv[2]);
const output = process.argv[3];
const requests = [];
const errors = [];
const context = vm.createContext({
  console: {error: (...args) => errors.push(args.map(String).join(' '))},
  AbortController, setTimeout, clearTimeout,
  state: {region: 'DEA1D'}, forecastData: null, centroidsVp2040: null,
  crosswalkSpatialVp: null, crosswalkNstVp: null, nutsToVpCell: {}, vpCellToNuts: {},
  fetch: async url => {
    const relative = String(url).split('?')[0];
    const target = path.resolve(publicRoot, relative);
    assert.ok(target.startsWith(publicRoot + path.sep));
    const present = fs.existsSync(target);
    requests.push({path: relative, status: present ? 200 : 404});
    return {ok: present, status: present ? 200 : 404, json: async () => JSON.parse(fs.readFileSync(target, 'utf8'))};
  }
});
vm.runInContext(fs.readFileSync(path.join(sourceRoot, 'js/shared/data-access.js'), 'utf8'), context);
(async () => {
  const passed = await context.ensureModuleData('forecast');
  const report = {passed, public_root: publicRoot, region: 'DEA1D', requests, errors, external_calls: 0};
  if (passed) {
    assert.ok(context.forecastData.scenarios['2040_P1'].regions['DEA1D'].relations_overall);
    assert.ok(Array.isArray(context.crosswalkSpatialVp));
    assert.ok(Array.isArray(context.crosswalkNstVp));
    assert.ok(requests.some(request => request.path === 'data/processed/delivery/forecast/DEA1D.json'));
  }
  if (output) fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify(report));
  process.exitCode = passed ? 0 : 1;
})().catch(error => {console.error(error); process.exitCode = 1;});
