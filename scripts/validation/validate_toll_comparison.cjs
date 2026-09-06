/** Deterministic checks for monthly comparison, nulls, request scope and cache. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const c=vm.createContext({console,AbortController,DOMException,Map,Date,state:{tollMunicipality:'05112000',tollDirection:'both',tollMetric:'trips'},document:{getElementById:()=>null}});
for(const file of ['js/shared/numbers.js','js/shared/toll-comparison.js','js/modules/toll.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),c);
const run=code=>vm.runInContext(code,c);
const feature=(direction,trips,mileage=1000,distance=10)=>({properties:{richtung:direction,ags_start:'05112000',ags_ziel:'05112000',name_start:'Duisburg',name_ziel:'Duisburg',anzahl_befahrungen:trips,fahrleistung_km:mileage,distanz_km_mittelw:distance,zeit_min_mittelw:20},geometry:null});
(async()=>{
 assert.equal(c.previousTollYearMonth('2026-01'),'2025-01');
 assert.equal(c.latestTollComparableMonth(['2026-07','2026-06','2025-06']),'2026-06');
 assert.equal(c.latestTollComparableMonth(['2026-07','2025-07','2026-06','2025-06']),'2026-07');
 assert.equal(c.latestTollComparableMonth(['2026-07']),null);
 assert.equal(c.latestTollComparableMonth([]),null);
 assert.equal(c.compareTollValues(12,8).absolute,4);assert.equal(c.compareTollValues(12,8).percent,50);
 assert.equal(c.compareTollValues(0,8).percent,-100);assert.equal(c.compareTollValues(0,0).percent,null);assert.equal(c.compareTollValues(12,0).percent,null);
 for(const x of [null,undefined,NaN,Infinity]){assert.equal(c.compareTollValues(x,1),null);assert.equal(c.compareTollValues(1,x),null);}
 assert.equal(c.numericTollValue(null),null);assert.equal(c.numericTollValue(''),null);assert.equal(c.numericTollValue(0),0);
 let normalized=c.normalizeTollFeatures([feature(0,100),feature(1,100)],{municipality:'05112000',direction:'both'});assert.equal(normalized.length,1);assert.equal(normalized[0].trips,100,'Internal trips must be counted once');
 assert.equal(c.normalizeTollFeatures([feature(0,null)])[0].trips,null);assert.equal(c.normalizeTollFeatures([feature(0,1,null)])[0].mileage,null);
 run("tollComparison={status:'available',month:'2025-07',rows:new Map([['05113000',{trips:40}]])}");
 assert.match(c.buildTollComparisonTooltip({partnerAgs:'05113000',trips:60}),/↗/);
 assert.match(c.buildTollComparisonTooltip({partnerAgs:'05113000',trips:20}),/↘/);
 assert.match(c.buildTollComparisonTooltip({partnerAgs:'05113000',trips:40}),/→/);
 assert.equal(c.getTollComparisonForRow({partnerAgs:'05113000',trips:60}).absolute,20);assert.equal(c.getTollComparisonForRow({partnerAgs:'missing',trips:60}),null);
 let requests=0;c.fetchTollRelations=async scope=>{requests++;return [feature(0,scope.month==='2026-07'?60:40)]};
 const scope={municipality:'05112000',month:'2026-07',direction:'outbound'};
 const a=await c.getTollMonthlySnapshot(scope);const b=await c.getTollMonthlySnapshot(scope);assert.equal(requests,1);assert.equal(a,b);assert.equal(a.month,scope.month);assert.ok(a.fetchedAt);assert.equal(a.complete,true);
 await c.getTollMonthlySnapshot({...scope,month:'2025-07'});assert.equal(requests,2);
 c.fetchTollRelations=async()=>{throw new Error('outage')};await assert.rejects(c.getTollMonthlySnapshot({...scope,month:'2024-07'}));
 c.fetchTollRelations=async()=>[feature(0,2)];assert.equal((await c.getTollMonthlySnapshot({...scope,month:'2024-07'})).rows[0].trips,2);
 const controller=new AbortController();controller.abort();await assert.rejects(c.getTollMonthlySnapshot({...scope,month:'2023-07'},controller.signal),/Aborted/);
 run("tollAvailableMonths=['2026-07'];tollRequestSequence=5");await c.loadTollComparison(scope,5);assert.equal(run('tollComparison.status'),'unavailable');
 run("tollAvailableMonths=['2026-07','2025-07'];tollRequestSequence=6");await c.loadTollComparison(scope,6);assert.equal(run('tollComparison.status'),'available');
 console.log('PASS: exact prior month, missing/zero, absolute/percent, internal-trip deduplication, scoped cache/timestamp, failure retry and aborted loads.');
})().catch(e=>{console.error(e);process.exitCode=1});
