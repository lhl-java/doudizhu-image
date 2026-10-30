"""Rebake one FX transform stream with a fixed safe display size; preserve the art."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fm_path=ROOT/'assets/fx/frames/deal-trail/frames.json'
fm=read(fm_path)
source=ROOT/fm['derivedFrom'][0]['file']
assert sha(source)==fm['derivedFrom'][0]['sha256']
original=Image.open(source).convert('RGBA')

def compose(base,pose):
    size=round(base*pose['scale'])
    sprite=original.resize((size,size),Image.Resampling.LANCZOS)
    sprite=sprite.rotate(-pose['rotation'],resample=Image.Resampling.BICUBIC,expand=True)
    data=np.array(sprite)
    data[:,:,3]=np.rint(data[:,:,3].astype(float)*pose['alpha']).clip(0,255).astype(np.uint8)
    sprite=Image.fromarray(data)
    frame=Image.new('RGBA',(384,384),(0,0,0,0))
    frame.alpha_composite(sprite,(round(192+pose['x']*384-sprite.width/2),round(192+pose['y']*384-sprite.height/2)))
    return frame

# Pick a single scale for the entire clip, preserving its trajectory and temporal proportions.
for base in range(300,159,-4):
    images=[compose(base,f['transform']) for f in fm['frames']]
    good=True
    for image in images:
        a=np.array(image.getchannel('A'))
        yy,xx=np.where(a>4)
        if len(xx) and (min(xx.min(),yy.min(),383-xx.max(),383-yy.max())<8):
            good=False;break
    if good:break
else:raise RuntimeError('Unable to fit FX stream')

for f,image in zip(fm['frames'],images):
    target=ROOT/f['file'];image.save(target)
    f['sha256']=sha(target)
fm['baseSpriteSize']=base
fm['operation']='Uniformly fit the complete deal-trail transform stream at fixed base sprite size '+str(base)+'px on a 384px RGBA canvas; same trajectory, timing, alpha and rotation; downscale only, no new art.'
fm['safetyCorrection']={'checkedAt':datetime.now(timezone.utc).isoformat(),'previousBaseSpriteSize':300,'reason':'Previous stream had 129 edge pixels with alpha>16 across 16 frames. Fixed one clip-wide source display size, with >=8px alpha>4 safety margin in every nonempty frame.','timelineTransformsUnchanged':True,'sourceUnchanged':True,'alphaThreshold':4,'minimumMarginPx':8}
fm_path.write_text(json.dumps(fm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'id':fm['id'],'baseSpriteSize':base,'frames':len(images),'status':'repaired'},ensure_ascii=False))
