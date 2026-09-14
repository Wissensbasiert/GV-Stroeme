/** Missing-value and ranking rules for the airport-specific KPI row. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),elements=new Map();
const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',innerHTML:''});return elements.get(id)};
const state={year:'2024',direction:'all',airfreightMetric:'tonnes',selectedAirport:'A'};
const c=vm.createContext({console,state,setText:(id,value)=>{element(id).textContent=String(value)},document:{getElementById:element},airfreightData:{metadata:{availableAirportYears:[2023,2024],availableAirportFlightYears:[2023,2024]},airports:{A:{name:'Testflughafen',country:'DE'}},airportValues:{2024:{A:{tonnes:{all:100,inbound:40,outbound:60}}},2023:{A:{tonnes:{all:0,inbound:0,outbound:0}}}},national:{2024:{tonnes:{all:900}}}}});
for(const file of ['js/shared/numbers.js','js/modules/airfreight.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),c);
assert.equal(c.getAirfreightValue({tonnes:{outbound:10,inbound:null}},'tonnes','balance'),null);
assert.equal(c.getAirfreightValue({tonnes:{outbound:null,inbound:10}},'tonnes','balance'),null);
assert.equal(c.getAirfreightValue({tonnes:{outbound:0,inbound:0}},'tonnes','balance'),0);
const entries=[{code:'B',value:200},{code:'A',value:100},{code:'C',value:100}];c.renderAirfreightKpis(entries);
assert.equal(element('airfreightAirportCount').textContent,'25 %','Airport denominator must be 400, not national 900');
assert.equal(element('airfreightTop3Share').textContent,'2 von 3','Tied airports share rank');
assert.equal(element('airfreightYoYValue').innerHTML,'--');assert.match(element('airfreightYoYSub').textContent,/nicht berechenbar/);
state.year='2025';c.renderAirfreightKpis([]);assert.equal(element('airfreightNationalValue').textContent,'--');assert.equal(element('airfreightAirportCount').textContent,'--');assert.equal(element('airfreightTop3Share').textContent,'--');c.ensureAirfreightAirportSelection([]);assert.equal(state.selectedAirport,'A');
state.year='2024';c.airfreightData.airportValues['2023'].A.tonnes.all=null;c.renderAirfreightKpis(entries);assert.equal(element('airfreightYoYValue').innerHTML,'--');assert.match(element('airfreightYoYSub').textContent,/Kein Vergleichswert/);
console.log('PASS: airport denominator, ties, zero baseline, incomplete balance, missing year and retained selection.');

// The reviewed source revision also reaches the actual dashboard KPI functions.
c.airfreightData=JSON.parse(fs.readFileSync(path.join(root,'data/processed/web_airfreight.json'),'utf8'));
state.year='2025';state.airfreightMetric='flights';state.direction='all';state.selectedAirport='EDDP';
assert.equal(c.isAirfreightAirportMetricYearAvailable(),true);
c.renderAirfreightKpis(c.getAirfreightAirportEntries());
assert.equal(element('airfreightNationalValue').textContent,'48.657 Flüge');
assert.match(element('airfreightYoYValue').innerHTML,/-2,6/);
assert.equal(c.getAirfreightRelations().length,0);
console.log('PASS: corrected 2025 Leipzig flights, prior-year comparison and no fabricated 2025 relations.');
