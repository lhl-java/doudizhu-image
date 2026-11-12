// Browser regressions for clipped controls, scroll reachability and table art interactions.
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'..');
const {chromium}=require(process.env.AUDIT_PLAYWRIGHT_PATH||'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out=path.join(ROOT,'.work/browser-layout-regression');
const checks=[],errors=[];const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
async function main(){
 await fs.mkdir(out,{recursive:true});
 const browser=await chromium.launch({executablePath:process.env.AUDIT_CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const p=await browser.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>errors.push(String(e)));
 const check=(name,pass,detail)=>checks.push({name,pass,detail});
 const go=async id=>{await p.locator(`[data-page="${id}"]`).evaluate(el=>el.click());await p.evaluate(async()=>{await Promise.all([...document.querySelectorAll('#stage img')].map(im=>im.decode().catch(()=>{})))});await p.waitForTimeout(80)};
 await p.goto('http://127.0.0.1:8771/runtime/art-preview.html');
 await p.waitForFunction(()=>window.ART_PREVIEW?.actorPlayer());
 for(const width of [1920,1280])for(const aspect of ['wide','standard']){
  await p.setViewportSize({width,height:1080});await p.selectOption('#aspect',aspect);
  const prefix=`${width}-${aspect}`;
  for(const id of ['08-join-room','30-puzzle-select','35-wardrobe','47-settings','48-help-rules','55-card-counter','05-matchmaking','27-tournament-detail']){
   await go(id);
   const bounds=await p.locator('.panel').evaluateAll(panels=>panels.map(el=>{
    const r=el.getBoundingClientRect(),s=getComputedStyle(el),box={left:r.left+parseFloat(s.borderLeftWidth),right:r.right-parseFloat(s.borderRightWidth),top:r.top+parseFloat(s.borderTopWidth),bottom:r.bottom-parseFloat(s.borderBottomWidth)};
    return {scrollX:el.scrollWidth-el.clientWidth,scrollY:el.scrollHeight-el.clientHeight,children:[...el.children].map(c=>{const b=c.getBoundingClientRect();return {name:c.className,inside:b.left>=box.left-2&&b.right<=box.right+2&&b.top>=box.top-2&&b.bottom<=box.bottom+2}})};
   }));
   check(`${prefix}/${id}/panel-contained`,bounds.every(b=>b.scrollX<=2&&b.scrollY<=2&&b.children.every(c=>c.inside)),bounds);
   for(const scroller of await p.locator('.panel .rows').all()){
    const r=await scroller.evaluate(el=>{el.scrollTop=el.scrollHeight;const r=el.getBoundingClientRect(),last=el.lastElementChild?.getBoundingClientRect();return {last:el.lastElementChild?.textContent,scrollTop:el.scrollTop,reachable:!last||(last.bottom<=r.bottom+2&&last.top>=r.top-2)}});
    check(`${prefix}/${id}/last-row-reachable`,r.reachable,r);
   }
   if(id==='08-join-room'){
    const r=await p.locator('.keys').evaluate(el=>{const r=el.getBoundingClientRect();return [...el.children].map(c=>{const b=c.getBoundingClientRect();return {key:c.textContent,inside:b.left>=r.left-1&&b.right<=r.right+1&&b.top>=r.top-1&&b.bottom<=r.bottom+1}})});
    check(`${prefix}/all-twelve-keys`,r.length===12&&r.every(c=>c.inside),r);
    await p.locator('[data-key="1"]').click();await p.locator('[data-key="0"]').click();await p.locator('[data-key="删除"]').click();
    check(`${prefix}/keypad-input`,await p.locator('#roomcode').inputValue()==='1');
   }
   await p.locator('#stage').screenshot({path:path.join(out,`${prefix}--${id}.png`),animations:'allow'});
  }
 }
 await p.setViewportSize({width:1920,height:1080});
 for(const aspect of ['wide','standard'])for(const scene of ['day','night'])for(const skin of ['jade','peach']){
  await go('14-play-turn');await p.selectOption('#aspect',aspect);await p.selectOption('#tableScene',scene);await p.selectOption('#tableSkin',skin);
  await p.waitForFunction(()=>window.ART_PREVIEW.actorPlayer());
  // Cards overlap by design; click the exposed index strip, as a player would.
  await p.locator('[data-card="0"]').click({position:{x:5,y:15}});
  check(`${aspect}/${scene}/${skin}/selection`,await p.locator('.card.picked').count()===1&&!(await p.locator('[data-action="出牌"]').isDisabled()));
  await p.locator('#stage').screenshot({path:path.join(out,`table-${aspect}-${scene}-${skin}.png`),animations:'allow'});
  await p.locator('[data-action="出牌"]').click();
  check(`${aspect}/${scene}/${skin}/submit`,await p.locator('[data-card]').count()===19&&await p.locator('[data-action="出牌"]').isDisabled());
 }
 const sourceEvidence=[];for(const file of ['runtime/art-preview.js','runtime/art-preview.css','tools/browser_layout_regression.cjs'])sourceEvidence.push({file,sha256:hash(await fs.readFile(path.join(ROOT,file)))});
 const report={schemaVersion:1,createdAt:new Date().toISOString(),browser:browser.version(),viewportWidths:[1920,1280],aspects:['wide','standard'],checks,errors,sourceEvidence,status:checks.every(c=>c.pass)&&!errors.length?'passed_browser_regressions':'failed'};
 await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,checks:checks.length,failures:checks.filter(c=>!c.pass),errors}));await browser.close();
 if(report.status==='failed')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exit(1)});
