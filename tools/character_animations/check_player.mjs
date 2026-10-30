// Deterministic Canvas draw-call smoke check, not a browser playback claim.
import {readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=new URL('../../',import.meta.url);
globalThis.fetch=async input=>({json:async()=>JSON.parse(await readFile(fileURLToPath(input),'utf8'))});
globalThis.Image=class {set src(v){this.file=v;queueMicrotask(()=>this.onload());}};
globalThis.requestAnimationFrame=()=>1;globalThis.cancelAnimationFrame=()=>{};
const drawCalls=[];
const ctx={clearRect(){},save(){},restore(){},translate(){},rotate(){},scale(){},drawImage(im){drawCalls.push(im.file);}};
const canvas={getContext:()=>ctx};
const {createActorPlayer}=await import('../../assets/animations/characters/player.mjs');
const rows=[];
for(const actor of ['daotong','taohua','hulu']) {
 const p=await createActorPlayer(canvas,{actor});
 for(const action of ['idle','think','play','win','lose']) {
  p.play(action);drawCalls.length=0;const at=action==='win'||action==='lose'?120:480;
  const state=p.seek(at);const expected=(action==='win'||action==='lose')?action:'master';
  if(state.pose!==expected)throw Error(`${actor}/${action} wrong pose`);
  if(!drawCalls[0].endsWith(`/assets/characters/${actor}/${expected}.png`))throw Error('Wrong image source');
  rows.push({actor,action,atMs:at,pose:state.pose,drawCalls:drawCalls.length,status:'passed'});
 }
 if(actor==='daotong')for(const skin of ['spring','ink','moon','snow','festival']) {
  await p.setSkin('daotong_'+skin);
  for(const action of ['win','lose','think']) {p.play(action);drawCalls.length=0;p.seek(480);
   if(!drawCalls[0].endsWith(`/assets/characters/daotong/costumes/${skin}.png`))throw Error('Skin swapped to base pose');
   if(action==='think'&&drawCalls.length!==1)throw Error('Unmatched thought HUD should be hidden');
  }
  rows.push({actor,skin,status:'passed_no_base_pose_swap_and_no_unmatched_hud'});
 }
 p.destroy();
}
const result={status:'passed',kind:'Node mock Canvas source-selection and time-sampling smoke check; no browser rendering assertion',rows};
await writeFile(new URL('assets/animations/characters/player-validation.json',root),JSON.stringify(result,null,2)+'\n','utf8');
console.log(JSON.stringify({status:result.status,checked:rows.length}));
