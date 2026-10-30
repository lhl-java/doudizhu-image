from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--file',required=True);p.add_argument('--source',required=True);p.add_argument('--prompt',required=True);p.add_argument('--transparent',action='store_true');p.add_argument('--receipt',required=True);args=p.parse_args()
target=root/args.file;target.parent.mkdir(parents=True,exist_ok=True)
source=Path(args.source)
if target.exists():
    if target.read_bytes()!=source.read_bytes() or target.with_suffix('.generation.json').exists():raise SystemExit('Target exists with existing record or different bytes: '+str(target))
else:shutil.copy2(source,target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(target) as im:im.verify()
with Image.open(target) as im:width,height,mode=im.width,im.height,im.mode;alpha=im.getextrema()[-1] if 'A' in im.getbands() else None
refs=['references/style/01-mail-event.png','references/style/team-ui-v2.png','designs/characters/characters-trio-v1.png']
record=dict(file=args.file,sha256=sha(target),generatedAt=datetime.now(timezone.utc).isoformat(),generatedAtEvidence='time recorded after tool return, not service internal timestamp',width=width,height=height,format='PNG',pixelMode=mode,alphaExtrema=alpha,tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=args.transparent,referenced_image_paths=[str(root/r) for r in refs]),actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未披露／无可核实元数据',prompt=args.prompt,promptSha256=sha(root/args.prompt),references=[dict(file=r,sha256=sha(root/r),role='actually attached style/identity reference') for r in refs],evidence=dict(hostOutputFile=str(source),receipt=args.receipt),nativeResolution=dict(width=width,height=height),operation='byte-identical-copy-no-resize',visualQA=dict(status='pending_visual_review',findings=[]))
target.with_suffix('.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['file','width','height','pixelMode','alphaExtrema','sha256']},ensure_ascii=False))

