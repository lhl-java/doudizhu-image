"""Downscale the final original app icon without repainting or upscaling."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
root=Path(__file__).resolve().parents[1]
source='assets/brand/app-icon.png';p=root/source
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
image=Image.open(p).convert('RGB');out=root/'assets/brand/exports';out.mkdir(exist_ok=True)
entries=[]
for n in [1024,512,192,180,128,96,64,48,32]:
    if n>min(image.size):raise ValueError('No upscaling')
    f=out/f'app-icon-{n}.png';image.resize((n,n),Image.Resampling.LANCZOS).save(f,optimize=True)
    record=f.with_suffix('.derivation.json')
    data=dict(file=f.relative_to(root).as_posix(),width=n,height=n,sha256=sha(f),route='derived',operation='Uniform Lanczos downscale of final square icon; no repainting, no AI generation, no upscaling.',derivedFrom=[dict(file=source,sha256=sha(p),record='assets/brand/app-icon.generation.json')])
    record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    entries.append(dict(**data,record=record.relative_to(root).as_posix()))
manifest=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),source=source,exports=entries,note='Generic square PNG exports. Platform signing, store listings, screenshots, and adaptive launcher layer configuration are application release integration.')
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Exported 9 source-derived square app icons, 32–1024px.')
