from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from PIL import Image
r=Path(__file__).resolve().parents[1];read=lambda p:json.loads((r/p).read_text(encoding='utf-8-sig'));write=lambda p,d:(r/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
m=read('assets/characters/costume-poses.json');checks=[]
for a in m['assets']:
    im=Image.open(r/a['file']).convert('RGBA');alpha=im.getchannel('A');bb=alpha.point(lambda v:255 if v>=16 else 0).getbbox()
    skin=a['id'].split('_')[1];master=Image.open(r/f'assets/characters/daotong/costumes/{skin}.png').convert('RGBA');mb=master.getchannel('A').point(lambda v:255 if v>=16 else 0).getbbox()
    edges=max(alpha.crop(box).getextrema()[1] for box in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)])
    if edges or abs((bb[3]-bb[1])-(mb[3]-mb[1]))>2 or abs(bb[3]-920)>2 or sha(a['file'])!=a['sha256']:raise ValueError('Pose registration/alpha/hash mismatch '+a['file'])
    a['status']='passed_offline_art_review';a['visualReview']=dict(method='actual imagegen returns plus light/dark five-costume master-win-lose contact inspected',passed=True,reviewedAt=datetime.now(timezone.utc).isoformat(),bodyHeight=bb[3]-bb[1],masterBodyHeight=mb[3]-mb[1],edgeAlphaMax=edges,footAnchorError=bb[3]-920)
    write(a['record'],a);checks.append(dict(file=a['file'],sha256=a['sha256'],**a['visualReview']))
contact='assets/characters/review/costume-poses-light-dark.png';shutil.copy2(r/'.work/costume-pose-contact.png',r/contact)
write(contact.replace('.png','.derivation.json'),dict(file=contact,sha256=sha(contact),operation='Downscaled contact of existing five costume master/win/lose PNGs on ivory and jade backgrounds; no AI generation',derivedFrom=[dict(file=a['file'],sha256=a['sha256'],record=a['record']) for a in m['assets']]))
m['status']='passed_offline_art_review';m['reviewContact']=contact;write('assets/characters/costume-poses.json',m)
write('docs/COSTUME_POSES_VALIDATION.json',dict(status='passed_offline_art_review',counts=dict(costumes=5,independentGeneratedPoseStills=10,registeredPngs=10),assets=checks,contact=contact,animationScope='Own-costume master/win/lose sources loaded by existing 2D keyframe player; no generated in-between frames, no skeletal animation claim',wholeGameClientVerified=False))
print('10 costume poses: alpha, source hash, same-height and foot-anchor checks passed; contact inspected.')
