"""CPU-render existing transparent UI actor art; no image model or new artwork."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/animations/characters'
OUT.mkdir(parents=True, exist_ok=True)
W, H, BASE = 160, 200, 0.17
PIVOT = [512, 920]
SCREEN = [80, 180]
ACTORS = ['daotong', 'taohua', 'hulu']
ACTIONS = ['idle', 'think', 'play', 'win', 'lose']
NOW = datetime.now(timezone.utc).isoformat()

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def src(p):
    path = ROOT/p
    with Image.open(path) as im: size=list(im.size)
    return {'file':p, 'sha256':sha(path), 'width':size[0], 'height':size[1], 'record':p.replace('.png','.derivation.json')}

def k(at, pose='master', x=0,y=0,sx=1,sy=1,deg=0,hud=0):
    return {'atMs':at,'pose':pose,'x':x,'y':y,'scaleX':sx,'scaleY':sy,'rotationDeg':deg,'hudOpacity':hud}

def spec(action):
    if action=='idle':
        times=list(range(0,1600,100)); end=1600
        keys=[k(0),k(800,y=-5,sx=1.004,sy=1.012),k(1500),k(end)]
        events=[{'atMs':0,'type':'ui_idle_begin','visualOnly':True}]
        description='Whole-actor breathing only, at most 1.2% scale and 5/1024 canvas units vertical displacement.'
    elif action=='think':
        times=list(range(0,1920,120)); end=1920
        keys=[k(0),k(240,x=-3,deg=-1.2,hud=1),k(840,x=-5,y=-2,deg=-2,hud=1),k(1440,x=-3,deg=-1,hud=1),k(1800),k(end)]
        events=[{'atMs':0,'type':'thought_hud_fade_in','durationMs':240,'visualOnly':True}, {'atMs':240,'type':'thought_hud_show','visualOnly':True,'role':'thinking portrait HUD badge; separate from actor anatomy'}, {'atMs':1440,'type':'thought_hud_fade_out','durationMs':360,'visualOnly':True}, {'atMs':1800,'type':'thought_hud_hidden','visualOnly':True}]
        description='Whole-actor tilt and separate framed thinking portrait HUD; no replacement head or articulated limb animation.'
    elif action=='play':
        times=list(range(0,960,60)); end=960
        keys=[k(0),k(120,x=7,deg=1.5),k(240,x=22,y=-4,sx=1.012,sy=1.006,deg=-3),k(480,x=12,deg=-1.5),k(720),k(end)]
        events=[{'atMs':240,'type':'card_flight_visual','visualOnly':True,'logicalCommitAuthority':'gameplay-controller','source':'assets/ui/cards-source/back-jade.png','durationMs':420,'coordinateSpace':'actor-canvas-1024','quadraticBezier':[[640,560],[800,350],[900,440]],'rotationDegrees':[-18,12],'trail':{'source':'same card image','samplesBehindMs':[36,72],'opacity':[0.2,0.08]},'semantics':'Anonymous card back illustrates play feedback. It does not choose cards, consume a hand, resolve a turn or send a gameplay command.'}, {'atMs':720,'type':'ui_play_recovered','visualOnly':True}]
        description='Whole-actor lean and existing card-back visual flight/trail; hands remain part of a rigid still.'
    else:
        times=[0,120,200,300,400,500,600,700,800,900,1000,1100,1200,1320,1440,1560]; end=1680
        if action=='win':
            keys=[k(0),k(120,pose='win'),k(400,pose='win',y=-7,sx=1.008,sy=1.015,deg=-1),k(1080,pose='win'),k(1320,pose='win'),k(1440),k(end)]
        else:
            keys=[k(0),k(120,pose='lose'),k(520,pose='lose',y=5,sy=.99,deg=1.4),k(1140,pose='lose'),k(1320,pose='lose'),k(1440),k(end)]
        events=[{'atMs':120,'type':'pose_switch','pose':action,'visualOnly':True,'semantics':'Replace the full still with this actor\'s real generated outcome pose.'}, {'atMs':200,'type':f'ui_{action}_cue','visualOnly':True,'semantics':'Optional presentation/audio cue; no gameplay result is determined here.'}, {'atMs':1440,'type':'pose_switch','pose':'master','visualOnly':True,'semantics':'Return to neutral whole-actor still.'}, {'atMs':end,'type':'clip_complete','next':'idle','visualOnly':True}]
        description=f'Real independently generated {action} still switches at 120 ms, holds, then returns to master at 1440 ms.'
    return times,end,keys,events,description

def state_at(keys,t):
    left=keys[0]; right=keys[-1]
    for row in keys:
        if row['atMs']<=t: left=row
        if row['atMs']>t:
            right=row; break
    span=right['atMs']-left['atMs']
    u=0 if span<=0 else max(0,min(1,(t-left['atMs'])/span))
    u=u*u*(3-2*u)
    state={'pose':left['pose']}
    for key in ['x','y','scaleX','scaleY','rotationDeg','hudOpacity']:
        state[key]=left[key]+(right[key]-left[key])*u
    return state

def affine_actor(im,state):
    # Supersample only within the source's existing resolution, then use a true
    # premultiplied LANCZOS downsample. Direct tiny affine sampling aliases art.
    ss=4
    r=math.radians(state['rotationDeg']); c,s=math.cos(r),math.sin(r)
    mat=np.array([[c*state['scaleX'],-s*state['scaleY']],[s*state['scaleX'],c*state['scaleY']]])*BASE*ss
    origin=np.array(SCREEN)*ss+np.array([state['x'],state['y']])*BASE*ss-mat@np.array(PIVOT)
    inv=np.linalg.inv(mat); offset=-inv@origin
    coeff=(float(inv[0,0]),float(inv[0,1]),float(offset[0]),float(inv[1,0]),float(inv[1,1]),float(offset[1]))
    high=im.convert('RGBa').transform((W*ss,H*ss),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
    return high.resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')

def resize(im,size): return im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
def opacity(im,alpha):
    im=im.copy(); im.putalpha(im.getchannel('A').point(lambda a:round(a*alpha))); return im
def card_layer(card,p,alpha):
    x=(1-p)**2*640+2*(1-p)*p*800+p*p*900
    y=(1-p)**2*560+2*(1-p)*p*350+p*p*440
    size=(15,19)
    im=resize(card,size).convert('RGBa').rotate(-18+30*p,Image.Resampling.BICUBIC,expand=True).convert('RGBA')
    im=opacity(im,alpha)
    return im,(round(SCREEN[0]+(x-512)*BASE-im.width/2),round(SCREEN[1]+(y-920)*BASE-im.height/2))

def render(actor,action,t,keys,images):
    state=state_at(keys,t)
    frame=affine_actor(images[state['pose']],state)
    if action=='think' and state['hudOpacity']>0:
        # Reuse two real source bitmaps as a portrait badge. No drawn bubble art.
        hud=Image.new('RGBA',(44,44))
        portrait=resize(images['thinking'],(36,36)); hud.alpha_composite(portrait,(4,3))
        border=resize(images['avatar-frame'],(44,38)); hud.alpha_composite(border,(0,2))
        frame.alpha_composite(opacity(hud,state['hudOpacity']),(113,8))
    if action=='play' and 240<=t<660:
        for lag,alpha in [(72,.08),(36,.2),(0,1)]:
            p=(t-240-lag)/420
            if p>=0:
                piece,point=card_layer(images['card'],p,alpha*((1-p)/.2 if p>.8 else 1))
                frame.alpha_composite(piece,point)
    return frame,state

def bbox_info(im):
    a=np.asarray(im.getchannel('A')); ys,xs=np.where(a>0)
    edge=np.concatenate([a[0,:],a[-1,:],a[:,0],a[:,-1]])
    return {'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'alphaExtrema':[int(a.min()),int(a.max())],'borderAlphaNonzero':int(np.count_nonzero(edge))}

all_clips=[]; qa=[]; engine=[]; actor_preview=[]; reviews=[]
frame_texture=Image.open(ROOT/'assets/ui/controls/avatar-frame.png').convert('RGBA')
card_texture=Image.open(ROOT/'assets/ui/cards-source/back-jade.png').convert('RGBA')
for actor in ACTORS:
    images={pose:Image.open(ROOT/f'assets/characters/{actor}/{pose}.png').convert('RGBA') for pose in ['master','win','lose']}
    images['thinking']=Image.open(ROOT/f'assets/characters/{actor}/expressions/thinking.png').convert('RGBA')
    images['avatar-frame']=frame_texture; images['card']=card_texture
    combo_frames=[]; combo_durations=[]; combo_segments=[]; combo_clock=0
    actor_review=Image.new('RGB',(W*4,H*5),(247,241,223))
    for action in ACTIONS:
        ident=f'{actor}_{action}'; times,end,keys,events,description=spec(action)
        durations=[b-a for a,b in zip(times,times[1:]+[end])]
        loop=action in ['idle','think']
        sources=[src(f'assets/characters/{actor}/{pose}.png') for pose in (['master',action] if action in ['win','lose'] else ['master'])]
        if action=='think': sources += [src(f'assets/characters/{actor}/expressions/thinking.png'),src('assets/ui/controls/avatar-frame.png')]
        if action=='play': sources += [src('assets/ui/cards-source/back-jade.png')]
        frames=[]; frame_records=[]
        for i,t in enumerate(times):
            im,state=render(actor,action,t,keys,images); info=bbox_info(im)
            assert info['borderAlphaNonzero']==0,(ident,i,info)
            frames.append(im)
            frame_records.append({'index':i,'atMs':t,'durationMs':durations[i],'rect':[(i%4)*W,(i//4)*H,W,H],'pose':state['pose'],'state':state,**info})
        if loop: assert frames[0].tobytes()==frames[-1].tobytes(),ident
        sheet=Image.new('RGBA',(W*4,H*4))
        for i,im in enumerate(frames): sheet.alpha_composite(im,((i%4)*W,(i//4)*H))
        sp=OUT/f'{ident}.png'; sheet.save(sp,optimize=True,compress_level=9)
        cp=OUT/f'{ident}.json'; rp=OUT/f'{ident}.derivation.json'
        clip={'schema':'doudizhu.ui-actor-keyframes.v1','id':ident,'actor':actor,'action':action,'description':description,'art_source':'existing','rendering':'CPU affine rendering of already generated transparent stills; not imagegen, AI video, skeletal animation or new limb frames','durationMs':end,'loop':loop,'keyframes':keys,'interpolation':{'numeric':'smoothstep between adjacent keys','pose':'step at key time','angles':'clockwise degrees in screen coordinates'},'pivot':{'sourceCanvas':[1024,1024],'sourcePoint':PIVOT,'units':'source canvas pixels','normalized':[.5,920/1024]},'preview':{'sheet':rel(sp),'frameSize':[W,H],'columns':4,'rows':4,'baseScale':BASE,'pivot':SCREEN,'frames':frame_records},'events':events,'eventPolicy':'Events are presentation cues only. Server/gameplay controller owns card selection, turn commit and win/loss results. In a loop, emit events once per cycle; on seek emit none unless explicitly requested.','hud':{'coordinateSpace':'preview pixels','rect':[113,8,44,44],'sourcePortrait':f'assets/characters/{actor}/expressions/thinking.png','sourceFrame':'assets/ui/controls/avatar-frame.png','role':'separate framed thinking HUD badge; not a body pose','highResolutionPosition':{'coordinateSpace':'320x400 presentation','rect':[226,16,88,88]}} if action=='think' else None,'skinPolicy':{'baseActor':actor,'supportedCostumes':['daotong_base','daotong_spring','daotong_ink','daotong_moon','daotong_snow','daotong_festival'] if actor=='daotong' else [],'timelineReusable':True,'forAlternateCostume':'Resolve all pose names to the selected skin file and apply the same transform; do not switch win/lose to base costume. Keep thinking portrait HUD hidden for alternate costumes unless a matching portrait exists. The baked sheets show the base costume only.','requiresNewBakedSheets':False},'sources':sources,'status':'asset_ready_user_review'}
        write(cp,clip)
        record={'file':rel(sp),'sha256':sha(sp),'width':sheet.width,'height':sheet.height,'format':'PNG','pixelMode':'RGBA','createdAt':NOW,'operation':'CPU affine transform and premultiplied LANCZOS downsampling of existing images into sixteen transparent frames; 4x4 packing; no new art drawn','art_source':'existing','sourceImageGeneration':False,'derivedFrom':sources,'sourceToPreviewBaseScale':BASE,'maximumActorScale':max(max(s['state']['scaleX'],s['state']['scaleY']) for s in frame_records)*BASE,'supersampling':{'factor':4,'intermediateMaximumSourceScale':max(max(s['state']['scaleX'],s['state']['scaleY']) for s in frame_records)*BASE*4,'filter':'premultiplied affine BICUBIC then LANCZOS downsample; intermediate resolution remains below source'},'noUpscale':True,'animationData':rel(cp),'animationDataSha256':sha(cp),'frameIndex':frame_records,'loopEndpointByteIdentical':frames[0].tobytes()==frames[-1].tobytes() if loop else None,'reviewStatus':'pending_visual_review'}
        write(rp,record)
        entry={'id':ident,'actor':actor,'action':action,'file':rel(cp),'sheet':rel(sp),'frameSize':[W,H],'frames':16,'durationsMs':durations,'durationMs':end,'loop':loop,'record':rel(rp)}
        all_clips.append(entry)
        engine.append({**entry,'pivot':SCREEN,'frameIndex':[{'rect':r['rect'],'durationMs':r['durationMs'],'pose':r['pose']} for r in frame_records],'events':events,'keyframes':keys})
        qa.append({'id':ident,'frameCount':16,'durationSumMs':sum(durations),'durationMatches':sum(durations)==end,'allRgba':True,'allBordersClear':all(r['borderAlphaNonzero']==0 for r in frame_records),'firstLastLoopEqual':record['loopEndpointByteIdentical'],'posesAt120And1440':{'120':state_at(keys,120)['pose'],'1440':state_at(keys,1440)['pose']} if action in ['win','lose'] else None,'maximumSourceScale':record['maximumActorScale'],'maxIdleScaleDelta':max(abs(s['state']['scaleY']-1) for s in frame_records) if action=='idle' else None,'sheetBytes':sp.stat().st_size})
        combo_segments.append({'action':action,'startMs':combo_clock,'durationMs':end,'clip':rel(cp)})
        combo_clock+=end; combo_frames+=frames; combo_durations+=durations
        # Four timestamps from each clip form one compact QA review per actor.
        row=ACTIONS.index(action)
        for column,i in enumerate([0,4,8,15]):
            actor_review.paste(frames[i],(column*W,row*H),frames[i])
            ImageDraw.Draw(actor_review).text((column*W+4,row*H+4),f'{action} {times[i]}ms',fill=(23,61,49))
        print(json.dumps({'clip':ident,'sheetBytes':sp.stat().st_size}),flush=True)
    webp=OUT/f'{actor}-all-actions.webp'
    combo_frames[0].save(webp,format='WEBP',save_all=True,append_images=combo_frames[1:],duration=combo_durations,loop=0,quality=65,method=6,exact=True)
    write(OUT/f'{actor}-all-actions.derivation.json',{'file':rel(webp),'sha256':sha(webp),'format':'animated WebP','frameSize':[W,H],'requestedFrameCount':80,'durationMs':sum(combo_durations),'requestedDurationsMs':combo_durations,'segments':combo_segments,'operation':'Lossy quality65 animated preview of CPU-rendered existing-art frames; alpha retained; PNG sheets are authoritative','derivedFrom':[{'file':e['sheet'],'sha256':sha(ROOT/e['sheet'])} for e in all_clips if e['actor']==actor],'createdAt':NOW,'reviewStatus':'pending_temporal_check'})
    actor_preview.append({'actor':actor,'file':rel(webp),'record':rel(OUT/f'{actor}-all-actions.derivation.json'),'segments':combo_segments})
    review=OUT/f'{actor}.review.jpg'; actor_review.save(review,quality=82,optimize=True)
    write(OUT/f'{actor}.review.derivation.json',{'file':rel(review),'sha256':sha(review),'operation':'QA contact sheet: four selected frames per action over ivory with timing labels; not game artwork','derivedFrom':[{'file':e['sheet'],'sha256':sha(ROOT/e['sheet'])} for e in all_clips if e['actor']==actor],'createdAt':NOW})
    reviews.append(rel(review))

write(OUT/'engine.json',{'schema':'doudizhu.engine-atlas-animations.v1','frameCoordinates':'top-left integer pixel rectangle [x,y,width,height]','rendering':'Draw one atlas rectangle at its native preview size or smaller; apply pivot [80,180]. Runtime may instead evaluate source timeline against full-size transparent actor stills for high-resolution presentation.','timing':'Advance frame only after durationMs; one-shots end on final master frame and next idle; loops wrap modulo duration.','clips':engine})
manifest={'schema':'doudizhu.ui-actor-animation-manifest.v1','createdAt':NOW,'status':'asset_ready_user_review','art_source':'existing','rendering':'CPU rendering of already generated assets, no imagegen, no video generation, no articulated body motion','clips':all_clips,'previews':actor_preview,'engine':'assets/animations/characters/engine.json','sourcesManifest':'assets/characters/manifest.json','skinPolicy':'Five alternate daotong skins reuse transform keys but always resolve pose to their own skin file; suppress unmatched thought portrait HUD. No duplicate skin sheets are required.','reviews':reviews}
write(OUT/'manifest.json',manifest)
write(OUT/'validation.json',{'status':'pending_visual_review','createdAt':NOW,'clipCount':len(all_clips),'frameCount':len(all_clips)*16,'frameSize':[W,H],'clips':qa,'note':'Numerical QA does not approve animation appearance; each contact sheet and temporal behavior must be reviewed.'})
print(json.dumps({'clips':len(all_clips),'sheetBytes':sum(q['sheetBytes'] for q in qa),'totalBytes':sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())}),flush=True)
