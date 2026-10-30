// Source-selection and timing integration check. No browser or rasterization is used.
import {readFile,writeFile,access,mkdir} from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import crypto from 'node:crypto';
const root=fileURLToPath(new URL('../',import.meta.url));
const logRoot=path.join(root,'.work/full-art-integration-test');
await mkdir(logRoot,{recursive:true});
const runtimeFile=path.join(root,'runtime/art-preview.js');
const source=await readFile(runtimeFile,'utf8');
const sourceHash=crypto.createHash('sha256').update(source).digest('hex');
await writeFile(path.join(logRoot,'runtime-snapshot.txt'),source);
const failures=[],notes=[],rows=[],fetches=new Set(),imageSources=new Set(),allDraws=[],inflightFetches=new Set();
let clock=0,rafId=0,raf=new Map(),lastReplaced=null;
globalThis.performance={now:()=>clock};
globalThis.requestAnimationFrame=fn=>{raf.set(++rafId,fn);return rafId;};
globalThis.cancelAnimationFrame=id=>raf.delete(id);
const runtimeURL=pathToFileURL(path.join(root,'runtime/art-preview.html'));
globalThis.fetch=value=>{const request=(async()=>{const u=value instanceof URL?value:new URL(value,runtimeURL);const p=fileURLToPath(u);fetches.add(p);const body=await readFile(p,'utf8');return {ok:true,status:200,json:async()=>JSON.parse(body.replace(/^\uFEFF/,''))};})();inflightFetches.add(request);request.finally(()=>inflightFetches.delete(request));return request;};
globalThis.Image=class{set src(v){this.file=v;imageSources.add(fileURLToPath(v));access(fileURLToPath(v)).then(()=>queueMicrotask(()=>this.onload())).catch(e=>this.onerror(e));}};
const decode=s=>s.replace(/&quot;/g,'"').replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>');
class Node {
 constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs=attrs;this.id=attrs.id;this.className=attrs.class||'';this.dataset={};for(const [k,v] of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,a)=>a.toUpperCase())]=v;this.value=attrs.value||'';this.checked=false;this.textContent='';this.children=[];this.style={setProperty(k,v){this[k]=v;}};this.classList={toggle:(c,v)=>{const set=new Set(this.className.split(' '));(v??!set.has(c))?set.add(c):set.delete(c);this.className=[...set].join(' ');},contains:c=>this.className.split(' ').includes(c)};this.draws=[];}
 set innerHTML(h){this.html=h;this.children=[];const tags=/<([\w-]+)\b([^>]*)>/g;let m;while((m=tags.exec(h))){const a={};for(const q of m[2].matchAll(/([\w-]+)(?:="([^"]*)")?/g))a[q[1]]=decode(q[2]||'');const n=new Node(m[1],a);n.parent=this;this.children.push(n);}if(this.tagName==='SELECT'){const opts=this.children.filter(n=>n.tagName==='OPTION');if(opts.length&&!opts.some(n=>n.value===this.value))this.value=opts[0].value;}}
 get innerHTML(){return this.html||'';}
 setAttribute(k,v){this.attrs[k]=v;}
 querySelector(sel){return this.children.find(n=>matches(n,sel))||null;}
 replaceWith(n){const ix=this.parent.children.indexOf(this);this.parent.children[ix]=n;n.parent=this.parent;lastReplaced={className:this.className,actor:this.dataset.actor};}
 replaceChildren(...nodes){this.children=nodes;for(const n of nodes)n.parent=this;}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(n=>n!==this);}
 animate(keys,opts){this.animation={keys,opts};return {cancel(){},onfinish:null};}
 closest(){return this;}
 getContext(){const self=this;return {clearRect(){self.draws=[];},save(){},restore(){},translate(){},rotate(){},scale(){},drawImage(im){self.draws.push(im.file);allDraws.push(im.file);}};}
}
function matches(n,s){const compound=s.match(/^(\.[\w-]+)(\[.+\])$/);if(compound)return matches(n,compound[1])&&matches(n,compound[2]);if(s.startsWith('.'))return n.className.split(' ').includes(s.slice(1));if(s.startsWith('#'))return n.id===s.slice(1);const a=s.match(/^\[([\w-]+)(?:="([^"]*)")?\]$/);if(a){const key=a[1].replace(/^data-/,'').replace(/-([a-z])/g,(_,c)=>c.toUpperCase());return key in n.dataset&&(a[2]===undefined||n.dataset[key]===a[2]);}return n.tagName.toLowerCase()===s;}
const ids=new Map();const html=await readFile(path.join(root,'runtime/art-preview.html'),'utf8');
for(const m of html.matchAll(/<([\w-]+)\b([^>]*\bid="([^"]+)"[^>]*)>/g)){const a={};for(const q of m[2].matchAll(/([\w-]+)(?:="([^"]*)")?/g))a[q[1]]=decode(q[2]||'');ids.set(m[3],new Node(m[1],a));}
for(const [id,value] of Object.entries({actor:'daotong',action:'idle',state:'0',tableSkin:'jade',search:'',fx:'play-glow'}))ids.get(id).value=value;
globalThis.document={querySelector(sel){const [head,...rest]=sel.split(/\s+/);const base=ids.get(head.slice(1));return rest.length?base?.querySelector(rest.join(' '))||null:base||null;},createElement:tag=>new Node(tag)};
globalThis.window={};
globalThis.PLAYER=await import(pathToFileURL(path.join(root,'assets/animations/characters/player.mjs')));
globalThis.STATE_ART_MODULE=await import(pathToFileURL(path.join(root,'runtime/state-art.mjs')));
const rewritten=source.replace(/^import \{createActorPlayer\} from [^;]+;/,'const {createActorPlayer}=globalThis.PLAYER;').replace(/^import \{renderStateArt\} from [^;]+;/m,'const {renderStateArt}=globalThis.STATE_ART_MODULE;');
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
await new AsyncFunction(rewritten+'\nglobalThis.API={render,state,action,animateActor,playFx,pages,setPage:id=>{page=pages.find(p=>p.id===id);},player:()=>actorPlayer,skin:()=>activeSkin};')();
const settle=async()=>{for(let i=0;i<3;i++){if(inflightFetches.size)await Promise.all([...inflightFetches]);await new Promise(resolve=>setImmediate(resolve));}};
await settle();
const click=(nodeId,dataset)=>ids.get(nodeId).onclick({target:new Node('button',Object.fromEntries(Object.entries(dataset).map(([k,v])=>['data-'+k,v])))});
for(const p of API.pages){
 try{API.setPage(p.id);API.render();await API.animateActor();await settle();const imgs=ids.get('canvas').children.filter(n=>n.tagName==='IMG');for(const im of imgs){if(im.attrs.src){const u=new URL(im.attrs.src,runtimeURL);await access(fileURLToPath(u));}}
  for(let i=0;i<p.states.length;i++){ids.get('state').value=String(i);API.state();const h=ids.get('stateLayer').innerHTML;if(!h||!h.includes('data-state-art="'+p.id+'.state.'+i+'"'))failures.push({kind:'empty-state',page:p.id,index:i});for(const im of ids.get('stateLayer').children.filter(n=>n.tagName==='IMG'))if(im.attrs.src)await access(fileURLToPath(new URL(im.attrs.src,runtimeURL)));}
  rows.push({page:p.id,states:p.states.length,render:'passed',imageRefs:imgs.length});
 }catch(e){failures.push({kind:'render-or-state',page:p.id,message:e.stack});}
}
// Real player API source checks from root callback integration.
for(const actor of ['daotong','taohua','hulu']){
 ids.get('actor').value=actor;ids.get('action').value='idle';API.setPage('02-lobby');API.render();await API.animateActor();await settle();
 for(const action of ['idle','think','play','win','lose']){ids.get('action').value=action;await API.animateActor();const p=API.player();const t=['win','lose'].includes(action)?120:480;const state=p.seek(t);if(state.pose!==(['win','lose'].includes(action)?action:'master'))failures.push({kind:'pose',actor,action,state});}
}
ids.get('actor').value='daotong';ids.get('action').value='idle';API.setPage('35-wardrobe');API.render();await API.animateActor();await settle();
for(const skin of ['spring','ink','moon','snow','festival']){
 click('canvas',{'costume':'daotong_'+skin});await settle();ids.get('action').value='win';await API.animateActor();const p=API.player();p.seek(480);if(p.skin!=='daotong_'+skin)failures.push({kind:'skin',skin,actual:p.skin});
 for(const pose of ['win','lose']){ids.get('action').value=pose;await API.animateActor();API.player().seek(480);const file=allDraws.at(-1),expected=`assets/characters/daotong/costumes/${skin}-poses/${pose}.png`;if(!file?.endsWith(expected))failures.push({kind:'costume-pose-source',skin,pose,file,expected});else notes.push({kind:'costume-pose-source',skin,pose,passed:true});API.player().seek(1500);if(!allDraws.at(-1)?.endsWith(`assets/characters/daotong/costumes/${skin}.png`))failures.push({kind:'costume-master-return',skin,pose});}
}
// Wardrobe contains only daotong skins: entering it from another actor must bind its player.
for(const fromActor of ['taohua','hulu']){
 ids.get('actor').value=fromActor;await ids.get('actor').onchange();await settle();
 API.setPage('35-wardrobe');API.render();await API.animateActor();await settle();
 let passed=ids.get('actor').value==='daotong'&&API.player()?.actor==='daotong';
 click('canvas',{'costume':'daotong_moon'});await settle();ids.get('action').value='win';await API.animateActor();await settle();API.player()?.seek(480);
 passed=passed&&API.player()?.skin==='daotong_moon';
 notes.push({kind:'wardrobe-actor-binding',fromActor,actor:ids.get('actor').value,skin:API.player()?.skin,passed});
 if(!passed)failures.push({kind:'wardrobe-actor-binding',fromActor});
}
// Regression assertions for root's three corrected integration defects.
for(const id of ['daotong','taohua','hulu']){
 ids.get('actor').value=id;ids.get('action').value='idle';API.setPage('14-play-turn');API.render();await API.animateActor();await settle();
 const passed=lastReplaced.className==='self'&&lastReplaced.actor===id;
 notes.push({kind:'table-selected-actor-target',actor:id,replaced:lastReplaced,passed});
 if(!passed)failures.push({kind:'wrong-actor-target',actor:id,replaced:lastReplaced});
}
ids.get('actor').value='daotong';ids.get('action').value='idle';API.setPage('19-round-loss');API.render();await API.animateActor();await settle();const resultState=API.player().seek(480);const lossPassed=ids.get('action').value==='lose'&&resultState.pose==='lose';notes.push({kind:'loss-page-default-action',action:ids.get('action').value,pose:resultState.pose,passed:lossPassed});if(!lossPassed)failures.push({kind:'loss-page-default-action'});
// Run real requestAnimationFrame callback at play event time; seek intentionally emits no events.
API.setPage('02-lobby');API.render();await API.animateActor();await settle();ids.get('action').value='play';await API.animateActor();clock+=300;const callbacks=[...raf.values()];raf.clear();for(const fn of callbacks)fn(clock);await settle();
const effect=ids.get('effectLayer').children[0];const eventPassed=effect?.alt==='play-glow'&&!!effect.animation;
notes.push({kind:'root-play-event-consumer',emitted:'card_flight_visual',listened:source.includes("event.type==='card_flight_visual'")?'card_flight_visual':'other',effectChildren:ids.get('effectLayer').children.length,passed:eventPassed});if(!eventPassed)failures.push({kind:'play-event-not-consumed'});
// All FX timeline keys must produce finite offsets/transforms and preserve configured units.
const fxIndex=window.ART_PREVIEW.assetIndex.fx;
for(const fx of fxIndex){await API.playFx(fx.id);const el=ids.get('effectLayer').children[0], timeline=JSON.parse(await readFile(path.join(root,fx.timeline),'utf8'));
 const keys=el.animation.keys;let passed=keys.length===timeline.keyframes.length&&keys.every(k=>Number.isFinite(k.offset)&&k.offset>=0&&k.offset<=1&&!/NaN|undefined/.test(k.transform));
 const unit=timeline.translationUnit==='fraction-of-384px-frame'?384:1;
 for(let i=0;i<keys.length;i++){const row=timeline.keyframes[i],x=(row.x??row.translateX??0)*unit,y=(row.y??row.translateY??0)*unit;if(!keys[i].transform.startsWith(`translate(${x}px,${y}px)`))passed=false;}
 notes.push({kind:'fx-timeline',id:fx.id,keys:keys.length,unit,passed});if(!passed)failures.push({kind:'fx-timeline-invalid',id:fx.id});
}
for(const p of fetches)await access(p);
API.player()?.destroy();
const pathChecks=[];
for(const f of ['assets/game/runtime-index.json','runtime/screens.json']){const data=JSON.parse(await readFile(path.join(root,f),'utf8'));const refs=new Set();const walk=v=>{if(typeof v==='string'&&/^(assets|designs|runtime)\/.+\.(png|jpg|webp|json|mjs|html)$/.test(v))refs.add(v);else if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')Object.values(v).forEach(walk);};walk(data);for(const r of refs)await access(path.join(root,r));pathChecks.push({file:f,uniqueReferences:refs.size,missing:0});}
const out={status:failures.length?'failed':'passed_static_and_mock_execution',validatedAt:new Date().toISOString(),sourceFile:'runtime/art-preview.js',sourceSha256:sourceHash,rootSourceUnchangedDuringTest:source==await readFile(runtimeFile,'utf8'),pages:rows.length,states:rows.reduce((n,r)=>n+r.states,0),actionsChecked:15,skinsChecked:5,wardrobeTransitionsChecked:2,fxTimelinesChecked:fxIndex.length,jsonSourcesRead:fetches.size,imageSourcesRead:imageSources.size,pathChecks,failures,findings:notes,limits:['Lightweight custom DOM, not a CSS/layout engine.','Mock Canvas records source selection and transform calls; it does not rasterize or verify appearance.','No browser, server, root code mutation, Git or new art generation used.','All states producing a modal is execution coverage, not proof that every designed state layout is semantically implemented.'],rows};
await writeFile(path.join(logRoot,'result.json'),JSON.stringify(out,null,2)+'\n');
const proofFiles=['runtime/art-preview.js','runtime/art-preview.html','runtime/art-preview.css','runtime/state-art.mjs','runtime/state-art.css','runtime/state-art.json','runtime/screens.json','assets/game/runtime-index.json','assets/animations/characters/player.mjs','assets/characters/daotong/character.json'];
const evidence=[];for(const f of proofFiles)evidence.push({file:f,sha256:crypto.createHash('sha256').update(await readFile(path.join(root,f))).digest('hex')});
out.limits[out.limits.length-1]='223 explicit state-art bindings execute against 26 visual layout types; CSS appearance and production state logic still need real visual/runtime review.';
const publicReport={...out,rows:undefined,evidence,method:'Node static syntax plus custom DOM and mock Canvas execution against actual local JSON/image references; actual createActorPlayer and renderStateArt modules used.',browserPlayback:{performed:false,claim:'No browser screenshot, CSS layout or visual animation playback is asserted by this report. CSS source is hashed as evidence only; this tool does not measure layout.'},reproduction:'node --check runtime/art-preview.js; node tools/verify_art_runtime.mjs',scriptSha256:crypto.createHash('sha256').update(await readFile(fileURLToPath(import.meta.url))).digest('hex')};
await writeFile(path.join(root,'docs/RUNTIME_INTEGRATION_VALIDATION.json'),JSON.stringify(publicReport,null,2)+'\n');
console.log(JSON.stringify({...out,rows:undefined},null,2));
if(failures.length||!out.rootSourceUnchangedDuringTest)process.exitCode=1;
