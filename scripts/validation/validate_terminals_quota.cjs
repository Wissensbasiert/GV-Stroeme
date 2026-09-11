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

// The former browser quota has been replaced by the guarded portal API.
assert(!read('scripts/frontend/build_frontend.py').includes('"ai-quota.js"'));
assert(read('scripts/frontend/build_frontend.py').includes('"ai-client.js"'));
console.log(`PASS: ${expected.length} terminal records match source; the delivery bundle uses the portal assistant client. Browser/HTTP behavior is checked separately.`);
