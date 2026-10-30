// Existing-art UI actor player. Canvas transforms rigid stills; no video/rig claim.
const projectRoot = new URL('../../../', import.meta.url);
const images = new Map();
async function bitmap(file) {
  if (!images.has(file)) images.set(file, new Promise((resolve,reject) => {
    const im = new Image(); im.onload=()=>resolve(im); im.onerror=reject;
    im.src=new URL(file,projectRoot).href;
  }));
  return images.get(file);
}
export function sampleKeys(keys,t) {
  let a=keys[0],b=keys.at(-1);
  for (const k of keys) {if(k.atMs<=t)a=k;else {b=k;break;}}
  let u=b.atMs===a.atMs?0:Math.max(0,Math.min(1,(t-a.atMs)/(b.atMs-a.atMs)));
  u=u*u*(3-2*u); const out={pose:a.pose};
  for(const k of ['x','y','scaleX','scaleY','rotationDeg','hudOpacity'])out[k]=a[k]+(b[k]-a[k])*u;
  return out;
}
export async function createActorPlayer(canvas,{actor='daotong',onEvent=()=>{},skin='daotong_base'}={}) {
  const manifest=await fetch(new URL('manifest.json',import.meta.url)).then(r=>r.json());
  const character=await fetch(new URL(`assets/characters/${actor}/character.json`,projectRoot)).then(r=>r.json());
  const clips=new Map(await Promise.all(manifest.clips.filter(c=>c.actor===actor).map(async e=>[e.action,await fetch(new URL(e.file,projectRoot)).then(r=>r.json())])));
  const sourceImages={}; for(const [pose,file] of Object.entries(character.poses))sourceImages[pose]=await bitmap(file);
  const thought=await bitmap(character.expressions.thinking),ring=await bitmap('assets/ui/controls/avatar-frame.png'),card=await bitmap('assets/ui/cards-source/back-jade.png');
  let selectedSkin=skin,skinImage=null,skinPoses={},skinTicket=0,clip=clips.get('idle'),started=performance.now(),previous=-1,cycle=0,playing=true,handle;
  const ctx=canvas.getContext('2d'); canvas.width=320;canvas.height=400;
  ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
  async function setSkin(id) {
    const ticket=++skinTicket;
    const found=character.costumes?.find(c=>c.id===id);
    if(id!=='daotong_base'&&found) {
      const pairs=await Promise.all(Object.entries(found.poses||{master:found.file}).map(async([pose,file])=>[pose,await bitmap(file)]));
      if(ticket!==skinTicket)return;
      skinPoses=Object.fromEntries(pairs);skinImage=skinPoses.master;selectedSkin=id;
    }
    else {skinImage=null;skinPoses={};selectedSkin=actor==='daotong'?'daotong_base':actor;}
  }
  await setSkin(skin);
  function cardAt(progress,alpha) {
    if(progress<0||progress>=1)return;
    const u=1-progress,x=u*u*640+2*u*progress*800+progress*progress*900;
    const y=u*u*560+2*u*progress*350+progress*progress*440;
    ctx.save();ctx.globalAlpha=alpha*(progress>.8?(1-progress)/.2:1);
    ctx.translate(160+(x-512)*.34,360+(y-920)*.34);
    ctx.rotate((-18+30*progress)*Math.PI/180);ctx.drawImage(card,-15,-19,30,38);ctx.restore();
  }
  function render(t) {
    const state=sampleKeys(clip.keyframes,t);ctx.clearRect(0,0,320,400);
    ctx.save();ctx.translate(160+state.x*.34,360+state.y*.34);
    ctx.rotate(state.rotationDeg*Math.PI/180);ctx.scale(.34*state.scaleX,.34*state.scaleY);
    ctx.drawImage(skinImage?(skinPoses[state.pose]||skinImage):sourceImages[state.pose],-512,-920);ctx.restore();
    if(clip.action==='think'&&state.hudOpacity>0&&!skinImage) {
      ctx.save();ctx.globalAlpha=state.hudOpacity;
      ctx.drawImage(thought,234,22,72,72);ctx.drawImage(ring,226,20,88,75);ctx.restore();
    }
    if(clip.action==='play'&&t>=240&&t<660) {
      cardAt((t-312)/420,.08);cardAt((t-276)/420,.2);cardAt((t-240)/420,1);
    }
    return state;
  }
  function emitBetween(from,to) {for(const event of clip.events)if(event.atMs>from&&event.atMs<=to)onEvent({...event,clipId:clip.id,cycle});}
  function tick(now) {
    if(playing) {
      let elapsed=now-started;
      if(clip.loop) {
        const nextCycle=Math.floor(elapsed/clip.durationMs);
        if(nextCycle!==cycle) {emitBetween(previous,clip.durationMs);cycle=nextCycle;previous=-1;}
        elapsed%=clip.durationMs;
      } else elapsed=Math.min(clip.durationMs,elapsed);
      emitBetween(previous,elapsed);previous=elapsed;render(elapsed);
      if(!clip.loop&&elapsed===clip.durationMs)playing=false;
    }
    handle=requestAnimationFrame(tick);
  }
  handle=requestAnimationFrame(tick);
  return {play(action) {if(!clips.has(action))throw new Error(`Unknown action ${action}`);clip=clips.get(action);started=performance.now();previous=-1;cycle=0;playing=true;},seek(ms) {playing=false;return render(Math.max(0,Math.min(clip.durationMs,ms)));},setSkin,destroy(){cancelAnimationFrame(handle);},get actor(){return actor;},get skin(){return selectedSkin;}};
}
