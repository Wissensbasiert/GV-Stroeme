// Render a saved, verified answer through the dashboard's actual chat client.
// Usage: node script.cjs <local portal release> <saved answer.json> <new output>
const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH || 'C:/tmp/kita_playwright_qa/node_modules/playwright');
const release=path.resolve(process.argv[2]),fixturePath=path.resolve(process.argv[3]),output=path.resolve(process.argv[4]);
let server,browser;
(async()=>{
  const fixture=JSON.parse(await fs.readFile(fixturePath,'utf8'));
  const css=await fs.readFile(path.resolve(__dirname,'../../css/style.css'));
  await fs.mkdir(output,{recursive:true});
  server=http.createServer(async(req,res)=>{
    try{
      const route=new URL(req.url,'http://localhost').pathname;
      res.setHeader('Content-Type','application/json; charset=utf-8');
      if(route.endsWith('/quota'))return res.end(JSON.stringify({plan:'premium',limit:50,used:0,reserved:0,remaining:50,month:'2026-09',csrf_token:'local-fixture'}));
      if(route.endsWith('/analysis')){
        let body='';for await(const chunk of req)body+=chunk;
        assert.equal(JSON.parse(body).question,fixture.question);
        return res.end(JSON.stringify(fixture.result));
      }
      const base=path.join(release,'alwaysdata_portal');
      const target=route==='/tools/gueterstroeme'?path.join(base,'gueterstroeme_dashboard/index.html'):path.resolve(base,'.'+decodeURIComponent(route));
      if(!target.startsWith(base+path.sep)){res.writeHead(403).end();return;}
      const types={'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css','.json':'application/json','.geojson':'application/json','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2'};
      res.setHeader('Content-Type',types[path.extname(target)] || 'application/octet-stream');
      res.end(target.endsWith(path.join('css','style.css'))?css:await fs.readFile(target));
    }catch{res.writeHead(404).end();}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin='http://127.0.0.1:'+server.address().port;
  browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  await page.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  await page.goto(origin+'/tools/gueterstroeme');
  await page.locator('#btnAiModal').click();
  await page.locator('#aiQuestionInput').fill(fixture.question);
  await page.locator('#aiQuestionForm button').click();
  const details=page.locator('#aiConversation details.ki-answer-table');
  await details.waitFor();
  assert.equal(await details.getAttribute('open'),null);
  assert.equal(await page.locator('#aiConversation .ki-message-assistant .ki-message-content > p').count(),fixture.result.answer.paragraphs.length);
  assert.equal(await page.locator('#aiConversation .ki-message-assistant .ki-message-content > p + p').first().evaluate(el=>parseFloat(getComputedStyle(el).marginTop)),12);
  assert.match(await page.locator('#aiConversation').innerText(),/110\.050 Tonnen/);
  assert.doesNotMatch(await page.locator('#aiConversation').innerText(),/49,93/);
  for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
    await page.setViewportSize(viewport);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.locator('.ki-modal-dialog').screenshot({path:path.join(output,'antwort-'+viewport.width+'.png')});
  }
  await page.setViewportSize({width:1440,height:1000});
  await details.locator('summary').click();
  assert.equal(await details.locator('tbody tr').count(),5);
  assert.match(await details.innerText(),/55\.106/);
  assert.match(await details.innerText(),/Kein eigener Eintrag/);
  await fs.writeFile(path.join(output,'report.json'),JSON.stringify({passed:true,fixture:fixturePath,release,current_css_sha256:crypto.createHash('sha256').update(css).digest('hex'),external_model_calls:0,customer_quota_writes:0,
    checks:['question submitted through actual client','requested endpoints visible','no substitute rate','details initially collapsed','all five original years expandable','desktop and mobile without page overflow']},null,2)+'\n');
  console.log('Browserprüfung bestanden: aktuelle gespeicherte Antwort, Desktop und Mobilansicht.');
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(async()=>{await browser?.close();if(server){server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}});
