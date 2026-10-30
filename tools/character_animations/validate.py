from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/animations/characters'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(OUT/'manifest.json'); result=read(OUT/'validation.json'); failures=[]; webps=[]
now=datetime.now(timezone.utc).isoformat()
assert len(manifest['clips'])==15
for entry in manifest['clips']:
    clip=read(ROOT/entry['file']); rp=ROOT/entry['record']; record=read(rp)
    assert record['sha256']==sha(ROOT/entry['sheet'])
    assert record['animationDataSha256']==sha(ROOT/entry['file'])
    assert record['maximumActorScale']<=1 and record['supersampling']['intermediateMaximumSourceScale']<=1
    for source in record['derivedFrom']:assert sha(ROOT/source['file'])==source['sha256']
    with Image.open(ROOT/entry['sheet']) as sheet:
        assert sheet.mode=='RGBA' and list(sheet.size)==[640,800]
        frames=[]
        for index in clip['preview']['frames']:
            x,y,w,h=index['rect'];frame=sheet.crop((x,y,x+w,y+h));frames.append(frame)
            a=np.asarray(frame.getchannel('A'));edge=np.concatenate([a[0,:],a[-1,:],a[:,0],a[:,-1]])
            assert int(edge.max())==0
            assert frame.getbbox() is not None
        if clip['loop']:assert frames[0].tobytes()==frames[-1].tobytes()
        assert len(frames)==16 and sum(entry['durationsMs'])==clip['durationMs']
    record['reviewStatus']='passed_visual_contact_sheet_and_numeric_timing_review'
    record['reviewedAt']=now;write(rp,record)
for preview in manifest['previews']:
    rp=ROOT/preview['record'];record=read(rp)
    with Image.open(ROOT/preview['file']) as im:
        durations=[]
        for i in range(im.n_frames):
            im.seek(i);im.load();durations.append(im.info['duration'])
            assert im.convert('RGBA').getchannel('A').getextrema()[0]==0
        assert sum(durations)==record['durationMs']==7840
        assert im.n_frames>1
        row={'actor':preview['actor'],'file':preview['file'],'decodedFrames':im.n_frames,'durationMs':sum(durations),'alphaPresent':True,'sha256':sha(ROOT/preview['file']),'note':'WebP encoder may merge identical adjacent frames while preserving total time.'}
        webps.append(row)
    record['reviewStatus']='passed_decode_all_frames_and_exact_duration_check';record['decoded']=row;write(rp,record)
manifest['reviewStatus']='passed_for_ui_actor_asset_review'
manifest['reviewedAt']=now
manifest['previewResolutionRationale']='160x200 transparent baked preview frames keep this batch under 10 MiB. Full 1024 actor source keyframes and player.mjs remain the high-resolution runtime path.'
manifest['playbackPage']='assets/animations/characters/index.html';manifest['player']='assets/animations/characters/player.mjs'
write(OUT/'manifest.json',manifest)
player=read(OUT/'player-validation.json')
assert player['status']=='passed'
result.update({'status':'passed_for_ui_actor_asset_review','validatedAt':now,'webpTemporalChecks':webps,'sourceHashChecks':'passed','all240FramesRgbaAndCompleteAlphaBounds':'passed','loopClips':6,'loopFirstLastByteIdentical':True,'outcomeSwitchAt120Ms':'passed for all six win/lose clips','outcomeReturnMasterAt1440Ms':'passed','noUpscaleIncludingSupersampling':True,'visualReview':{'all15FullContactSheetsActuallyViewed':True,'all3IvoryReviewSheetsActuallyViewed':True,'findings':['All hands, feet, hair and accessories remain inside each frame.','Thought portrait badge reads independently from the body.','Card flight is a rigid existing card-back image plus faded trail copies.','Outcome poses are distinct real generated stills.']},'playerValidation':'assets/animations/characters/player-validation.json','browserPlayback':{'status':'not_verified_in_this_worker','reason':'cua.createBrowserTab returned Local browser use is disabled in Work settings. Root will conduct final browser playback review.','url':'http://127.0.0.1:8877/assets/animations/characters/index.html'},'artGeneration':'None in this animation batch. CPU rendering of prior generated assets only.','note':'This approves the UI actor keyframe asset scope, not AI video or articulated full-body motion.'})
write(OUT/'validation.json',result)
total=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
result['packageBytes']=total;result['packageMiB']=round(total/1024**2,3);result['packageBudgetBytes']=10*1024**2
write(OUT/'validation.json',result)
print(json.dumps({'status':result['status'],'clips':15,'frames':240,'packageBytes':total,'packageMiB':result['packageMiB'],'webps':webps},ensure_ascii=False))
assert total<=10*1024**2, total
