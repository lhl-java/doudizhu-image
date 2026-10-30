from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--id',required=True);ap.add_argument('--source',required=True);ap.add_argument('--refs',nargs='+',required=True);args=ap.parse_args()
id=args.id;target=root/'designs/characters/runtime-20261026'/f'{id}.png'
target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():raise SystemExit('Refuse overwrite '+str(target))
shutil.copy2(args.source,target)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with Image.open(target) as im:
    im.verify()
with Image.open(target) as im:
    w,h=im.size;mode=im.mode
    alpha=im.getchannel('A') if 'A' in im.getbands() else None
    extrema=alpha.getextrema() if alpha else None
    bbox=alpha.getbbox() if alpha else None
    border=0
    if alpha:
        import numpy as np
        a=np.array(alpha)
        border=int((a[0]>0).sum()+(a[-1]>0).sum()+(a[:,0]>0).sum()+(a[:,-1]>0).sum())
refs=[dict(file=Path(p).relative_to(root).as_posix(),sha256=sha(p),role='primary confirmed style or selected character identity/pose') for p in args.refs]
record=dict(file=target.relative_to(root).as_posix(),sha256=sha(target),generatedAt=datetime.now(timezone.utc).isoformat(),generatedAtEvidence='timestamp recorded immediately after host output adoption, not internal model clock',width=w,height=h,format='PNG',pixelMode=mode,tool='image_gen.imagegen',route='builtin',art_source='host_image',configSnapshot=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=True,referenced_image_paths=args.refs),actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未披露／无可核实元数据',prompt=f'prompts/characters-runtime/{id}.txt',references=refs,evidence=dict(hostOutputFile=args.source,receipt=target.with_suffix('.receipt.json').relative_to(root).as_posix()),transparency=dict(hasAlpha=alpha is not None,alphaExtrema=extrema,nonTransparentBounds=bbox,borderPixelsWithAlpha=border),nativeResolution=dict(width=w,height=h),exportOperation='byte-identical-copy-no-resize',status='needs_visual_review')
target.with_suffix('.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['file','sha256','width','height','transparency']},ensure_ascii=False))

