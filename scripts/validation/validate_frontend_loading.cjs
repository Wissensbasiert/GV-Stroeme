/** Behavioral regression checks for shared browser data access and unit formatting. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const context = vm.createContext({ console, AbortController, setTimeout, clearTimeout });
vm.runInContext(fs.readFileSync(path.join(root, 'js/shared/numbers.js'), 'utf8') + '\n' + fs.readFileSync(path.join(root, 'js/shared/data-access.js'), 'utf8'), context);
const { requestDataOnce, fetchJson, formatFixedUnitValue, formatDeNum } = context;
(async () => {
  let attempts = 0;
  const intermittent = () => { if (++attempts === 1) throw new Error('temporary outage'); return 42; };
  await assert.rejects(requestDataOnce('transient', intermittent), /temporary/);
  assert.equal(await requestDataOnce('transient', intermittent), 42);
  assert.equal(await requestDataOnce('transient', intermittent), 42);
  assert.equal(attempts, 2, 'Failed loads must retry; successful loads must stay cached');
  let concurrentCalls = 0;
  const [first, second] = await Promise.all([
    requestDataOnce('shared', async () => { concurrentCalls++; await new Promise(r => setTimeout(r, 5)); return 'ready'; }),
    requestDataOnce('shared', () => { throw new Error('duplicate request'); })
  ]);
  assert.equal(first, second); assert.equal(concurrentCalls, 1);
  context.fetch = async () => ({ ok: false, status: 503 });
  await assert.rejects(fetchJson('/unavailable'), /HTTP 503/);
  context.fetch = async () => ({ ok: true, json: async () => { throw new SyntaxError('Invalid JSON'); } });
  await assert.rejects(fetchJson('/invalid'), /Invalid JSON/);
  let aborted = false;
  context.fetch = (_url, options) => new Promise((_resolve, reject) => {
    const abort = () => { aborted = true; reject(new Error('aborted')); };
    if (options.signal.aborted) abort(); else options.signal.addEventListener('abort', abort);
  });
  await assert.rejects(fetchJson('/stalled', null, { timeoutMs: 10 }), /aborted/);
  assert.equal(aborted, true, 'A stalled request must end');
  const controller = new AbortController();
  const superseded = fetchJson('/superseded', null, { signal: controller.signal });
  controller.abort();
  await assert.rejects(superseded, /aborted/);
  assert.equal(formatFixedUnitValue(215169.2), '215.169,2');
  assert.equal(formatFixedUnitValue(215.2), '215,2');
  assert.equal(formatFixedUnitValue(-215169.2, { signed: true }), '-215.169,2');
  assert.equal(formatFixedUnitValue(215169.2, { divisor: 1000, signed: true }), '+215,2');
  assert.equal(formatFixedUnitValue(23743, { decimals: 0 }), '23.743');
  for (const value of [null, undefined, NaN, Infinity]) assert.equal(formatFixedUnitValue(value), '--');
  assert.equal(formatDeNum(Infinity), '--');
  console.log('PASS: retry after failure, shared concurrent requests, HTTP/JSON errors, timeouts, cancellation and fixed table units.');
})().catch(error => { console.error(error); process.exitCode = 1; });
