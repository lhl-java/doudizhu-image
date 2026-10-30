"""Independent final runtime scene/FX file checks and documented visual findings."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
scenes=read('assets/scenes/scenes.json');fx=read('assets/fx/manifest.json')
rejected_moon='be626bb02972c8cc46d021ea824e23338834a6bb3a86331c0f45ae7df731903c'
scene_rows=[];scene_errors=[]
for entry in scenes['assets']:
    p=entry['file'];im=Image.open(ROOT/p);record=read(entry['record']);problems=[]
    if sha(p)!=record['sha256']:problems.append('record hash differs')
    if im.size!=(entry['width'],entry['height']):problems.append('manifest size differs')
    row=dict(id=entry['id'],file=p,sha256=sha(p),width=im.width,height=im.height,mode=im.mode)
    if entry['kind']=='foreground':
        a=np.array(im.getchannel('A'))
        edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
        row['alphaRange']=[int(a.min()),int(a.max())];row['edgeNonzero']=int((edge>0).sum())
        source=record['derivedFrom'][0]['file'];src=np.array(Image.open(ROOT/source).convert('RGBA'))
        expected=src.copy();expected[expected[:,:,3]<=4,3]=0
        actual=np.array(im)[64:-64,64:-64]
        # alpha_composite discards hidden RGB under zero alpha; only visible pixels are significant.
        visible=expected[:,:,3]>0
        row['visibleSourcePixels1to1']=bool(np.array_equal(actual[visible],expected[visible]))
        row['sourceAlpha1to1']=bool(np.array_equal(actual[:,:,3],expected[:,:,3]))
        if not(row['visibleSourcePixels1to1'] and row['sourceAlpha1to1']):problems.append('source 1:1 differs')
        if row['edgeNonzero'] or im.mode!='RGBA':problems.append('transparent outer edge invalid')
    if sha(p)==rejected_moon:problems.append('Moon upper-left rim has dark rectangular artifact; AI correction pending.')
    row['status']='needs_fix' if problems else 'passed_for_art_file_review';row['errors']=problems
    scene_errors += [dict(file=p,message=x) for x in problems];scene_rows.append(row)

fx_rows=[];fx_errors=[];frames_total=0
for entry in fx['assets']:
    problems=[];p=entry['file'];rec=read(entry['record']);im=Image.open(ROOT/p)
    if sha(p)!=rec['sha256']:problems.append('sprite record hash differs')
    if im.mode!='RGBA' or im.size!=(512,512):problems.append('sprite format invalid')
    a=np.array(im.getchannel('A'));edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    if (edge>0).any():problems.append('source outer alpha edge not empty')
    timeline=read(entry['timeline']);fm=read(entry['frames'])
    if len(fm['frames'])!=16:problems.append('expected 16 baked frames')
    if sha(fm['derivedFrom'][0]['file'])!=fm['derivedFrom'][0]['sha256']:problems.append('frame source hash differs')
    frame_rows=[]
    for f in fm['frames']:
        image=Image.open(ROOT/f['file']);arr=np.array(image.getchannel('A'))
        border=np.concatenate([arr[0],arr[-1],arr[:,0],arr[:,-1]])
        if sha(f['file'])!=f['sha256']:problems.append('frame hash differs '+f['file'])
        if image.size!=(384,384) or image.mode!='RGBA':problems.append('frame format differs '+f['file'])
        if (border>16).any():problems.append('frame edge clipped '+f['file'])
        yy,xx=np.where(arr>4);margin=int(min(xx.min(),yy.min(),383-xx.max(),383-yy.max())) if len(xx) else None
        frame_rows.append(dict(file=f['file'],sha256=f['sha256'],atMs=f['atMs'],durationMs=f['durationMs'],edgeAlphaAbove16=int((border>16).sum()),marginAlphaAbove4=margin))
        frames_total+=1
    times=[f['atMs'] for f in fm['frames']]
    if times[0]!=0 or any(b<=a for a,b in zip(times,times[1:])):problems.append('frame times invalid')
    interval_sum=sum(f['durationMs'] for f in fm['frames'])
    expected=timeline['durationMs']+(0 if timeline['loop'] else 1)
    if interval_sum!=expected:problems.append('playback sum differs; terminal transparent sentinel is 1ms on one-shot only')
    if timeline['loop'] and not timeline.get('stopEvent'):problems.append('loop stop event absent')
    if not timeline['loop'] and np.array(Image.open(ROOT/fm['frames'][-1]['file']).getchannel('A')).max()!=0:problems.append('one shot terminal frame not transparent')
    fx_errors += [dict(id=entry['id'],message=x) for x in problems]
    fx_rows.append(dict(id=entry['id'],file=p,sha256=sha(p),sourceAlphaEdgeNonzero=int((edge>0).sum()),frames=frame_rows,timelineDurationMs=timeline['durationMs'],bakedPlaybackDurationMs=interval_sum,terminalSentinelMs=0 if timeline['loop'] else 1,loop=timeline['loop'],errors=problems,status='needs_fix' if problems else 'passed_for_art_file_review'))

base=dict(schemaVersion=1,checkedAt=stamp,reviewMethod='File hashes, RGBA byte comparisons and offline image/contact-sheet inspection; not browser/device playback or engine import.',userApproved=False)
scene_report=dict(**base,status='needs_fix' if scene_errors else 'passed_for_art_file_review',counts=dict(backgrounds=3,transparentForegrounds=2),assets=scene_rows,errors=scene_errors,limits=['No collision/nav claim; backgrounds are scenery plates.','16:9 center-crop preserves visual center; runtime foreground must contain-fit.','Rejected moon image hash stays recorded even after corrected selection.'])
fx_report=dict(**base,status='needs_fix' if fx_errors else 'passed_for_art_file_review',counts=dict(effects=12,bakedFrames=frames_total),assets=fx_rows,errors=fx_errors,visualInspection=dict(staticContacts=['designs/runtime-scenes-20261026/fx-a-over-light.jpg','designs/runtime-scenes-20261026/fx-a-over-dark.jpg','designs/runtime-scenes-20261026/fx-b-over-light.jpg','designs/runtime-scenes-20261026/fx-b-over-dark.jpg'],frameContact='designs/runtime-scenes-20261026/fx-frame-contact.jpg',frameIndices=[1,5,9,13],notes='All12 independently isolated motifs visually inspected on light/dark; selected phases show coherent drift/fade/scale/rotation, no visible cut-off after deal-trail repair.'),knownSourceWarnings=read('designs/runtime-scenes-20261026/validation.json')['qaNotes'],limits=['Original sheet B failed fixed-grid cross-cell tests; all components retained by ownership separation. Raw source tests remain FAIL in their historical reports.','Faint detached alpha glow specks retained as authored glow; see exact raw/runtime QA warnings.','Frames are transform-derived from still art, not AI video or independently drawn phase animations.','One-shot PNG stream contains an explicit 1ms fully transparent terminal sentinel; its stream duration is timeline duration +1ms.','Screen blend requires engine/browser renderer to honor manifest blend semantics.'])
for p,r in [('assets/scenes/qa-report.json',scene_report),('assets/fx/qa-report.json',fx_report)]:
    (ROOT/p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(sceneStatus=scene_report['status'],fxStatus=fx_report['status'],sceneErrors=scene_errors,fxErrors=fx_errors,frames=frames_total),ensure_ascii=False))
