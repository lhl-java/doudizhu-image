// Actual Chrome wall-clock playback evidence. No virtual clock, seek, or source mutation.
// Usage: node tools/browser_motion_audit.cjs [--only=regression|actors|costumes|fx]
// Optional env: PLAYWRIGHT_MODULE, CHROME_EXECUTABLE, ART_PREVIEW_URL.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const output = path.join(root, '.work/browser-motion-audit');
// Keep the optional recording toolchain inside this repository as well.
process.env.PLAYWRIGHT_BROWSERS_PATH ||= path.join(output, 'toolchain');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const entry = process.env.ART_PREVIEW_URL || 'http://127.0.0.1:8771/runtime/art-preview.html';
if (new URL(entry).hostname !== '127.0.0.1') throw new Error('Audit must use the project localhost preview.');
const only = process.argv.find(x => x.startsWith('--only='))?.slice(7);
const digest = b => crypto.createHash('sha256').update(b).digest('hex');
const readJson = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const write = (file, value) => fs.writeFileSync(path.join(output, file), JSON.stringify(value, null, 2) + '\n');
const I = readJson('assets/game/runtime-index.json');
const clips = readJson('assets/animations/characters/manifest.json').clips;
const actions = ['idle', 'think', 'play', 'win', 'lose'];
fs.mkdirSync(output, {recursive:true});
const sourceFiles = ['runtime/art-preview.js', 'runtime/art-preview.html', 'runtime/art-preview.css', 'runtime/state-art.css', 'runtime/screens.json', 'assets/game/runtime-index.json', 'assets/animations/characters/player.mjs', 'assets/animations/characters/manifest.json'];
const sourceSnapshot = () => sourceFiles.map(file => ({file, sha256:digest(fs.readFileSync(path.join(root,file)))}));
const startedInputs = sourceSnapshot();
let browser;
async function contextFor(id) {
  const dir = path.join(output,id);fs.mkdirSync(dir,{recursive:true});
  const context = await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,recordVideo:{dir,size:{width:960,height:600}}});
  await context.addInitScript(() => {
    window.__motionDraws = [];
    const drawImage = CanvasRenderingContext2D.prototype.drawImage;
    CanvasRenderingContext2D.prototype.drawImage = function(image,...args) {
      if (this.canvas.dataset.actor) window.__motionDraws.push({at:performance.now(),source:image.src || 'non-image',actor:this.canvas.dataset.actor});
      return drawImage.call(this,image,...args);
    };
  });
  const page = await context.newPage(), errors=[], responseJobs=[], inputs=new Map();
  page.on('pageerror',error=>errors.push(error.message));
  page.on('response',response=>{
    if (!response.url().startsWith(new URL(entry).origin)) return;
    responseJobs.push((async()=>{try{const body=await response.body();inputs.set(new URL(response.url()).pathname.slice(1),{sha256:digest(body),status:response.status()});}catch(error){errors.push('Response body: '+error.message);}})());
  });
  await page.goto(entry,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>window.ART_PREVIEW?.actorPlayer());
  await page.evaluate(()=>document.fonts.ready);
  return {context,page,errors,inputs,async finish(){
    await page.waitForLoadState('networkidle');
    await Promise.allSettled(responseJobs);
    const video=page.video();await context.close();
    const nativeVideo=await video.path(), target=path.join(dir,'playback.webm');
    if(nativeVideo!==target)fs.renameSync(nativeVideo,target);
    return {video:path.relative(root,target).replaceAll('\\','/'),videoBytes:fs.statSync(target).size,videoSha256:digest(fs.readFileSync(target)),browserErrors:errors,servedInputs:[...inputs].sort(([a],[b])=>a.localeCompare(b)).map(([file,value])=>({file,...value}))};
  }};
}
async function choosePage(page,id) {
  await page.locator(`[data-page="${id}"]`).evaluate(el=>el.click());
  await page.waitForFunction(id=>window.ART_PREVIEW.page()===id,id);
}
async function capture(page,id,label) {
  const file=path.join(output,id,label+'.png');
  await page.locator('#stage').screenshot({path:file,animations:'allow'});
  const bytes=fs.readFileSync(file);
  return {file:path.relative(root,file).replaceAll('\\','/'),bytes:bytes.length,sha256:digest(bytes)};
}
async function waitFrom(page,start,target) {
  const elapsed=await page.evaluate(start=>performance.now()-start,start);
  if(target>elapsed)await page.waitForTimeout(target-elapsed);
}
async function actorCase(actor,action,skin,group) {
  const id=[group,actor,skin||'base',action].join('-'), run=await contextFor(id), {page}=run;
  await page.selectOption('#actor',actor);
  await page.waitForFunction(actor=>window.ART_PREVIEW.actorPlayer()?.actor===actor,actor);
  if(skin) {
    await choosePage(page,'35-wardrobe');
    await page.waitForFunction(()=>window.ART_PREVIEW.actorPlayer()?.actor==='daotong');
    await page.locator(`[data-costume="${skin}"]`).evaluate(el=>el.click());
    await page.waitForFunction(skin=>window.ART_PREVIEW.actorPlayer()?.skin===skin,skin);
  }
  await page.selectOption('#action',action);
  await page.waitForFunction(()=>!!window.ART_PREVIEW.actorPlayer());
  const clip=readJson(clips.find(c=>c.actor===actor&&c.action===action).file);
  const start=await page.evaluate(action=>{window.__motionDraws=[];window.ART_PREVIEW.actorPlayer().play(action);return performance.now();},action);
  const samples=[],screens=[];
  const targets=[0,.2,.45,.7,.95,1.16].map(x=>x*clip.durationMs);
  for(let i=0;i<targets.length;i++) {
    await waitFrom(page,start,targets[i]);
    const sample=await page.evaluate(start=>{
      const canvas=document.querySelector('#canvas canvas[data-actor]');
      return {elapsedMs:performance.now()-start,actor:window.ART_PREVIEW.actorPlayer().actor,skin:window.ART_PREVIEW.actorPlayer().skin,png:canvas.toDataURL('image/png').split(',')[1],draws:window.__motionDraws.length,lastSource:window.__motionDraws.at(-1)?.source};
    },start);
    const png=Buffer.from(sample.png,'base64');delete sample.png;samples.push({...sample,canvasPngSha256:digest(png)});
    if([0,2,5].includes(i))screens.push(await capture(page,id,{0:'start',2:'middle',5:'end'}[i]));
  }
  const preTail=await page.evaluate(()=>window.__motionDraws.length);
  await page.waitForTimeout(140);
  const draws=await page.evaluate(()=>window.__motionDraws);
  const actorSources=[...new Set(draws.map(x=>new URL(x.source).pathname.slice(1)))];
  const poseExpected=['win','lose'].includes(action)?(skin&&skin!=='daotong_base'?`assets/characters/daotong/costumes/${skin.replace('daotong_','')}-poses/${action}.png`:`assets/characters/${actor}/${action}.png`):null;
  const checks={actualWallClockBeyondDuration:samples.at(-1).elapsedMs>=clip.durationMs,pixelChanges:new Set(samples.map(x=>x.canvasPngSha256)).size>1,realCanvasDraws:draws.length>5,expectedActor:samples.every(s=>s.actor===actor),expectedSkin:samples.every(s=>s.skin===(skin|| (actor==='daotong'?'daotong_base':actor))),ownIndependentPose:!poseExpected||actorSources.includes(poseExpected),loopContinuesOrOneShotStops:clip.loop?draws.length>preTail:draws.length===preTail};
  const result={id,group,actor,skin:skin||null,action,durationMs:clip.durationMs,loop:clip.loop,method:'Unmodified requestAnimationFrame and performance.now; public player.play; no seek or virtual time.',samples,drawCount:draws.length,firstDrawMs:draws[0]?.at-start,lastDrawMs:draws.at(-1)?.at-start,actorSources,poseExpected,screens,checks,...await run.finish()};
  result.passed=Object.values(checks).every(Boolean)&&!result.browserErrors.length;
  write(id+'/result.json',result);console.log(JSON.stringify({id,passed:result.passed,checks}));return result;
}
async function fxCase(fx) {
  const id='fx-'+fx.id,run=await contextFor(id),{page}=run;
  await page.evaluate(()=>window.ART_PREVIEW.actorPlayer().destroy());
  await page.selectOption('#fx',fx.id);await page.click('#playfx');
  await page.waitForFunction(id=>document.querySelector('#effectLayer .effect')?.alt===id,fx.id);
  await page.waitForFunction(()=>document.querySelector('#effectLayer .effect').complete);
  const start=await page.evaluate(()=>performance.now()),samples=[],screens=[];
  for(const [i,fraction] of [0,.2,.45,.7,.95,1.16].entries()) {
    await waitFrom(page,start,fx.durationMs*fraction);
    samples.push(await page.evaluate(start=>{
      const el=document.querySelector('#effectLayer .effect'),a=el?.getAnimations()[0],timing=a?.effect.getComputedTiming();
      return {elapsedMs:performance.now()-start,present:!!el,id:el?.alt||null,currentTimeMs:a?.currentTime??null,playState:a?.playState||null,progress:timing?.progress??null,currentIteration:timing?.currentIteration??null,transform:el?getComputedStyle(el).transform:null,opacity:el?getComputedStyle(el).opacity:null};
    },start));
    if([0,2,5].includes(i))screens.push(await capture(page,id,{0:'start',2:'middle',5:'end'}[i]));
  }
  const active=samples.filter(s=>s.present),tail=samples.at(-1);
  const checks={actualWallClockBeyondDuration:tail.elapsedMs>=fx.durationMs,progressChanges:new Set(active.map(s=>s.progress)).size>1,transformOrOpacityChanges:new Set(active.map(s=>s.transform+' '+s.opacity)).size>1,loopCrossesCycleOrOneShotRemoves:fx.loop?tail.present&&tail.currentIteration>=1&&!['finished','idle'].includes(tail.playState):!tail.present};
  const result={id,group:'fx',durationMs:fx.durationMs,loop:fx.loop,method:'Real Web Animations API progression and wall-clock screenshots; no animation time writes.',samples,screens,checks,...await run.finish()};result.passed=Object.values(checks).every(Boolean)&&!result.browserErrors.length;
  write(id+'/result.json',result);console.log(JSON.stringify({id,passed:result.passed,checks}));return result;
}
async function regression() {
  const id='fx-navigation-regression',run=await contextFor(id),{page}=run;
  await page.selectOption('#fx','turn-ring');await page.click('#playfx');await page.waitForSelector('#effectLayer .effect');
  const initial=await page.locator('#effectLayer .effect').count();await choosePage(page,'03-classic-select');await page.waitForTimeout(180);
  const afterNavigation=await page.locator('#effectLayer .effect').count();
  await page.route('**/assets/fx/turn-ring.timeline.json',async route=>{await new Promise(resolve=>setTimeout(resolve,350));await route.continue();});
  await page.click('#playfx');await choosePage(page,'04-stakes-select');await page.waitForTimeout(650);
  const afterPendingNavigation=await page.locator('#effectLayer .effect').count();
  // An older delayed request must not overwrite a newer effect.
  await page.selectOption('#fx','turn-ring');await page.click('#playfx');await page.selectOption('#fx','loading-ring');await page.click('#playfx');await page.waitForTimeout(650);
  const afterReplay=await page.locator('#effectLayer .effect').count(),latest=await page.locator('#effectLayer .effect').getAttribute('alt');
  const screens=[await capture(page,id,'latest-only')];await choosePage(page,'02-lobby');await page.waitForTimeout(400);
  const finalCount=await page.locator('#effectLayer .effect').count();screens.push(await capture(page,id,'cleared'));
  const checks={loopStarted:initial===1,renderClears:afterNavigation===0,pendingRenderCannotResurrect:afterPendingNavigation===0,newestPlayWins:afterReplay===1&&latest==='loading-ring',subsequentRenderClears:finalCount===0};
  const result={id,group:'regression',observations:{initial,afterNavigation,afterPendingNavigation,afterReplay,latest,finalCount},checks,screens,...await run.finish()};result.passed=Object.values(checks).every(Boolean)&&!result.browserErrors.length;write(id+'/result.json',result);console.log(JSON.stringify({id,passed:result.passed,checks}));return result;
}
(async()=>{
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const report={schemaVersion:1,createdAt:new Date().toISOString(),chrome:browser.version(),entry,viewport:{width:1440,height:900},videoSize:{width:960,height:600},description:'Rigid still-pose UI animation and FX playback; not AI video, skeletal animation, or target-client acceptance.',screenshotsAnimations:'allow',inputsAtStart:startedInputs,scriptSha256:digest(fs.readFileSync(__filename)),cases:[],limits:['Headless desktop Chrome evidence only; target client and human art approval remain external.','Motion checks show real clock progression and source selection. Final visual judgment requires viewing the recorded artifacts.','Video includes preview controls at reduced recording resolution; PNG screenshots preserve the stage at browser CSS pixel resolution.']};
  try {
    if(!only||only==='regression')report.cases.push(await regression());
    if(!only||only==='actors')for(const actor of ['daotong','taohua','hulu'])for(const action of actions)report.cases.push(await actorCase(actor,action,null,'actor'));
    if(!only||only==='costumes')for(const skin of I.costumes.map(c=>c.id))for(const action of actions)report.cases.push(await actorCase('daotong',action,skin,'costume'));
    if(!only||only==='fx')for(const fx of I.fx)report.cases.push(await fxCase(fx));
    report.inputsAtEnd=sourceSnapshot();report.changedInputFiles=report.inputsAtEnd.filter((row,i)=>row.sha256!==startedInputs[i].sha256).map(x=>x.file);
    report.passed=report.cases.every(x=>x.passed);report.counts={cases:report.cases.length,actorActions:report.cases.filter(x=>x.group==='actor').length,costumeActions:report.cases.filter(x=>x.group==='costume').length,fx:report.cases.filter(x=>x.group==='fx').length,regressions:report.cases.filter(x=>x.group==='regression').length};
    write(only?'report-'+only+'.json':'report.json',report);console.log(JSON.stringify({passed:report.passed,counts:report.counts,changedInputFiles:report.changedInputFiles}));if(!report.passed)process.exitCode=1;
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
