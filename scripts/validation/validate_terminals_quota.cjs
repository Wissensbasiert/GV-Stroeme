// Source fidelity and quota boundary checks; no browser or model needed.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const raw = read('data/raw/Intermodal/intermodal_terminals_europe.geojson');
const source = JSON.parse(raw.replace(/^\uFEFF/, ''));
const output = JSON.parse(read('data/processed/web_intermodal_terminals.geojson'));
const mapping = {
  'Schiene / Straße': 'Bimodales Terminal · Schiene / Straße',
  'Wasserstraße / Straße': 'Bimodales Terminal · Wasserstraße / Straße',
  Trimodal: 'Trimodales Terminal · Schiene / Wasserstraße / Straße'
};
const expected = source.features.filter(f => f.properties.iso2 === 'DE' && mapping[f.properties.kategorie]);
assert.deepEqual(output.metadata.country_filter, {field: 'iso2', value: 'DE'});
assert.equal(output.features.length, expected.length);
assert.equal(output.metadata.source_sha256, crypto.createHash('sha256').update(raw).digest('hex'));
output.features.forEach((f, i) => {
  assert.deepEqual(Object.keys(f.properties).sort(), ['function', 'name']);
  assert.equal(f.properties.name, expected[i].properties.name);
  assert.equal(f.properties.function, mapping[expected[i].properties.kategorie]);
  assert.deepEqual(f.geometry, expected[i].geometry);
  assert(!f.properties.name.includes('\uFFFD'));
});

const quotaCode = read('js/shared/ai-quota.js');
function quotaContext(stored = null, failStorage = false) {
  const elements = new Map();
  const context = vm.createContext({ Intl, Date, document: {
    getElementById(id) { if (!elements.has(id)) elements.set(id, {}); return elements.get(id); },
    querySelector() { return this.getElementById('submit'); }
  }, sessionStorage: {
    getItem() { if (failStorage) throw Error('blocked'); return stored; },
    setItem(key, value) { if (failStorage) throw Error('blocked'); stored = value; }
  } });
  vm.runInContext(quotaCode, context);
  return { context, elements, run: code => vm.runInContext(code, context) };
}
const q = quotaContext();
assert.equal(q.run('refreshAiPreviewQuota().used'), 0);
for (let i = 0; i < 50; i++) assert(q.run('consumeAiPreviewQuestion()'));
assert.equal(q.run('consumeAiPreviewQuestion()'), false);
assert.equal(q.elements.get('aiQuotaProgress').value, 50);
assert.equal(q.elements.get('submit').disabled, true);
assert.equal(q.run('currentAiQuotaMonth(new Date("2026-09-30T21:59:59Z"))'), '2026-09');
assert.equal(q.run('currentAiQuotaMonth(new Date("2026-09-30T22:00:00Z"))'), '2026-10');
q.run('aiPreviewQuota.month = "2026-01"');
assert.equal(q.run('refreshAiPreviewQuota().used'), 0);
assert.equal(q.elements.get('submit').disabled, false);
for (const bad of ['broken', 'null', '{}', '[]', '{"used":-1}', '{"used":51}']) {
  assert.equal(quotaContext(bad).run('readAiPreviewQuota().used'), 0);
}
const month = q.run('currentAiQuotaMonth()');
assert.equal(quotaContext(JSON.stringify({ month, used: 17 })).run('readAiPreviewQuota().used'), 17);
for (const used of [-1, 51, 1.5, '12']) {
  assert.equal(quotaContext(JSON.stringify({ month, used })).run('readAiPreviewQuota().used'), 0);
}
assert(quotaContext(null, true).run('consumeAiPreviewQuestion()'));
console.log(`PASS: ${expected.length} terminal records match source names, functions and coordinates; minimal fields and source hash verified. Quota limit, month boundary, stored counts and unavailable storage passed.`);
