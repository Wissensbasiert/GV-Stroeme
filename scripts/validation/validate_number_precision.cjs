const fs = require('node:fs'), vm = require('node:vm'), path = require('node:path'), assert = require('node:assert/strict');
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../../js/shared/numbers.js'),'utf8'), context);
for (const [value, expected] of [[3839.24,'3.839'],[337.52,'338'],[100,'100'],[42.56,'42,6'],[1.38,'1,4'],[0.0741,'0,074'],[-0.00231,'-0,0023'],[0,'0'],[null,'--'],[Infinity,'--']]) assert.equal(context.formatKpiNumber(value),expected);
for(const values of [[0,.02,.04,.06],[-.06,-.04,-.02,0,.02],[-.5,-.25,0,.25,.5],[0,1e-7,2e-7],[0,100,200]]) {
  const ticks = values.map(value=>({value}));
  const labels = values.map((value,i)=>context.formatChartAxisTick(value,i,ticks));
  assert.equal(new Set(labels).size,values.length);
  for(let i=0;i<values.length;i++) assert.ok(Math.abs(Number(labels[i].replaceAll('.','').replace(',','.'))-values[i])<1e-12);
}
assert.notEqual(context.formatKpiNumber(1e-12),'0');
console.log('PASS: KPI thresholds, small/signed/missing values and distinct accurate fractional axis labels.');
