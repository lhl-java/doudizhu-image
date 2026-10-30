from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil
from PIL import Image

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--source', required=True)
parser.add_argument('--transparent', action='store_true')
parser.add_argument('--include-characters', action='store_true')
args = parser.parse_args()
scope = json.loads((root / 'docs/UI_SCOPE.json').read_text(encoding='utf-8-sig'))
page = next(p for p in scope['pages'] if p['id'] == args.id)
source = Path(args.source)
target = root / page['output']
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    raise SystemExit('Target already exists; choose a new version instead of overwriting.')
shutil.copy2(source, target)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(target) as im:
    im.verify()
with Image.open(target) as im:
    width, height, fmt, mode = im.width, im.height, im.format, im.mode
    alpha = im.getextrema()[-1] if 'A' in im.getbands() else None
config = json.loads((root / 'config/image-generation.json').read_text(encoding='utf-8-sig'))
prompt = f"prompts/{page['batch']}/{args.id}-v1.txt"
refs = [dict(file=f'references/style/{name}', sha256=sha(root / 'references/style' / name), role='user-confirmed-primary-style') for name in ['01-mail-event.png', 'team-ui-v2.png']]
if args.include_characters:
    refs.append(dict(file='designs/characters/characters-trio-v1.png',sha256=sha(root/'designs/characters/characters-trio-v1.png'),role='current-three-character-identities'))
record = dict(file=page['output'], sha256=sha(target), generatedAt=datetime.now(timezone.utc).isoformat(), generatedAtEvidence='recorded after tool completion; service internal timestamp not disclosed', width=width, height=height, format=fmt, nativeResolution=dict(width=width,height=height), exportOperation='byte-identical-copy-no-resize', tool='image_gen.imagegen', route='builtin', configSnapshot=config, submittedParameters=dict(model=None, quality=None, transparent_background=args.transparent, referenced_image_paths=[str(root / r['file']) for r in refs]), actualModel=None, actualQuality=None, unverifiedReason='宿主管理，工具未披露／无可核实元数据', evidence=dict(hostOutputFile=str(source), toolReceipt=str(target.with_suffix('.receipt.json').relative_to(root))), prompt=prompt, references=refs, pixelMode=mode, alphaExtrema=alpha, status='design_ready_user_review', visualQA=dict(status='pending', findings=[]))
(root / page['generation']).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(file=page['output'],width=width,height=height,mode=mode,alphaExtrema=alpha,sha256=record['sha256']),ensure_ascii=False))

