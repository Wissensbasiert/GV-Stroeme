const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const state={forecastScenario:'2040_P1',direction:'all',selectedGroup:'ALL'};
const data=JSON.parse(fs.readFileSync(path.join(root,'data/processed/web_forecast_core.json'),'utf8'));
const c=vm.createContext({state,forecastData:data});
for(const file of ['js/shared/numbers.js','js/modules/forecast.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),c);
let checks=0;
for(const metric of ['tonnes','tkm'])for(const direction of ['all','outbound','inbound','balance'])for(const group of ['ALL','1','4'])for(const scenario of ['2019_BASE','2040_P1']){
 Object.assign(state,{direction,selectedGroup:group,forecastScenario:scenario});
 const id='DE40H',field=group==='ALL'?`directions_${metric}`:`groups_7_${metric}`;
 const read=s=>group==='ALL'?data.scenarios[s].regions[id][field][direction]:data.scenarios[s].regions[id][field][direction][group];
 const base=read('2019_BASE'),future=read('2040_P1'),html=c.getForecastHoverComparison(id,metric==='tkm');
 assert.ok(html.includes(scenario==='2019_BASE'?'Erwartete Veränderung bis 2040':'Veränderung gegenüber 2019'));
 if(direction==='balance')assert.doesNotMatch(html,/%/);
 else if(base>0)assert.ok(html.includes(((future-base)/base*100).toLocaleString('de-DE',{maximumFractionDigits:1})+' %'));
 checks++;
}
Object.assign(state,{direction:'all',selectedGroup:'ALL'});
assert.match(c.getForecastHoverComparison('missing',false),/nicht verfügbar/);
data.scenarios['2019_BASE'].regions.test={directions_tonnes:{all:0}};
data.scenarios['2040_P1'].regions.test={directions_tonnes:{all:10}};
assert.match(c.getForecastHoverComparison('test',false),/nicht berechenbar/);
data.scenarios['2040_P1'].regions.test.directions_tonnes.all=0;
assert.match(c.getForecastHoverComparison('test',false),/0 %/);
console.log(`PASS: ${checks} forecast comparisons by metric/direction/goods/scenario, missing regions and zero baseline.`);

const detail=JSON.parse(fs.readFileSync(path.join(root,'data/processed/delivery/forecast/DEA1D.json'),'utf8'));
for(const scenario of Object.keys(detail))Object.assign(data.scenarios[scenario].regions.DEA1D,detail[scenario]);
state.region='DEA1D';state.selectedGroup='ALL';state.direction='all';
for(const scenario of ['2019_BASE','2040_P1']){
 state.forecastScenario=scenario;
 for(const metric of ['tonnes','tkm']){
  const html=c.getForecastRelationHoverComparison('3160166',metric==='tkm');
  const a=detail['2019_BASE'].relations_overall.all.find(r=>r.partner_id==='3160166')[metric];
  const b=detail['2040_P1'].relations_overall.all.find(r=>r.partner_id==='3160166')[metric];
  assert.ok(html.includes(((b-a)/a*100).toLocaleString('de-DE',{maximumFractionDigits:1})+' %'));
  assert.match(html,/Δ/);assert.match(html,/#16a34a/);
 }
}
assert.match(c.formatForecastHoverChange(100,80,false),/#dc2626/);
assert.match(c.formatForecastHoverChange(100,100,false),/#64748b/);
assert.match(c.getForecastRelationHoverComparison('missing',false),/nicht verfügbar/);
state.direction='balance';
assert.doesNotMatch(c.getForecastRelationHoverComparison('3160166',false),/%/);
assert.match(c.getForecastRelationHoverComparison('missing',false),/nicht verfügbar/);
console.log('PASS: Rhine-Neuss/Rotterdam route comparisons in both scenarios/metrics, red/green/neutral, missing and balance cases.');
