from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
from PIL import Image
root=Path(__file__).resolve().parents[1]
arg=argparse.ArgumentParser();arg.add_argument('--skin',choices=['spring','ink','moon','snow','festival'],default='spring');arg.add_argument('--action',choices=['win','lose'],required=True);arg.add_argument('--source',required=True);args=arg.parse_args()
target=root/f'designs/characters/costume-poses-20261029/{args.skin}-{args.action}-v1.png';target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():raise SystemExit('Target already exists; no overwrite')
shutil.copy2(args.source,target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[f'assets/characters/daotong/costumes/{args.skin}.png',f'assets/characters/daotong/{args.action}.png','references/style/01-mail-event.png','references/style/team-ui-v2.png']
prompt=f'prompts/characters-runtime/{args.skin}-{args.action}-v1.txt'
with Image.open(target) as im:
    im.load();a=im.getchannel('A');w,h=im.size;b=a.point(lambda v:255 if v>16 else 0).getbbox();edge=max(a.crop(q).getextrema()[1] for q in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
    if im.mode!='RGBA' or a.getextrema()!=(0,255):raise ValueError('Expected true transparent RGBA')
rec=dict(file=target.relative_to(root).as_posix(),sha256=sha(target),generatedAt=datetime.now(timezone.utc).isoformat(),generatedAtEvidence='recorded after host return',width=w,height=h,format='PNG',pixelMode='RGBA',alphaExtrema=[0,255],significantAlphaBBox=b,edgeAlphaMax=edge,tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=True,referenced_image_paths=[str(root/p) for p in refs]),actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未披露／无可核实元数据',prompt=prompt,promptSha256=sha(root/prompt),references=[dict(file=p,sha256=sha(root/p),role=['costume identity master','base action pose','primary style','primary style'][i]) for i,p in enumerate(refs)],evidence=dict(hostOutputFile=args.source,toolReturnedKeys=['image_url','output_hint']),visualReview=dict(status='candidate_needs_runtime_registration_and_user_review',note='Independently generated full-body still; not continuous animation. Must check scale and transparent borders before runtime adoption.'))
target.with_suffix('.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:rec[k] for k in ['file','width','height','edgeAlphaMax','significantAlphaBBox','sha256']},ensure_ascii=False))
