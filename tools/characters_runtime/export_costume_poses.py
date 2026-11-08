"""Export independent costume victory/defeat stills, anchored to each skin master."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2]
read=lambda p:json.loads((root/p).read_text(encoding='utf-8-sig'))
write=lambda p,d:(root/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
def bbox(im):return im.getchannel('A').point(lambda v:255 if v>=16 else 0).getbbox()
manifest=read('assets/characters/manifest.json');dt=manifest['characters'][0];assets=[]
contact=Image.new('RGB',(1500,1200),'#eae3d3');draw=ImageDraw.Draw(contact)
for i,skin in enumerate(['spring','ink','moon','snow','festival']):
    masterfile=f'assets/characters/daotong/costumes/{skin}.png';master=Image.open(root/masterfile).convert('RGBA');mb=bbox(master);height=mb[3]-mb[1]
    mapping={'master':masterfile}
    for j,pose in enumerate(['win','lose']):
        source=f'designs/characters/costume-poses-20261029/{skin}-{pose}-v1.png';im=Image.open(root/source).convert('RGBA');bb=bbox(im)
        scale=min(1.,height/(bb[3]-bb[1]),880/(bb[2]-bb[0]));crop=(max(0,bb[0]-6),max(0,bb[1]-6),min(im.width,bb[2]+6),min(im.height,bb[3]+6))
        piece=im.crop(crop).convert('RGBa');piece=piece.resize((round(piece.width*scale),round(piece.height*scale)),Image.Resampling.LANCZOS).convert('RGBA')
        origin=[(bb[0]+bb[2])/2,bb[3]];offset=[round(512-(origin[0]-crop[0])*scale),round(920-(origin[1]-crop[1])*scale)]
        result=Image.new('RGBA',(1024,1024));result.alpha_composite(piece,offset)
        file=f'assets/characters/daotong/costumes/{skin}-poses/{pose}.png';(root/file).parent.mkdir(parents=True,exist_ok=True);result.save(root/file)
        a=result.getchannel('A');edge=max(a.crop(q).getextrema()[1] for q in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)])
        if edge:raise ValueError('Export perimeter not clear: '+file)
        record=file.replace('.png','.derivation.json')
        rec=dict(id=f'daotong_{skin}_{pose}',kind='costume_pose',file=file,record=record,width=1024,height=1024,anchor=[512,920],sha256=sha(file),route='derived',noUpscale=True,fixedScale=scale,sourceRect=list(crop),sourceAnchor=origin,offset=offset,registration='match the skin-master significant body height; feet anchored at512,920; per-source uniform downscale only',operation='significant-alpha crop plus6px, premultiplied-alpha Lanczos downscale, foot-anchor registration; independent generated pose still',derivedFrom=[dict(file=source,sha256=sha(source),record=source.replace('.png','.generation.json'))],alphaExtrema=list(a.getextrema()),edgeAlphaMax=edge,status='exported_needs_visual_review',recordedAt=datetime.now(timezone.utc).isoformat())
        write(record,rec);assets.append(rec);mapping[pose]=file
    for c in dt['costumes']:
        if c['id']=='daotong_'+skin:c['poses']=mapping;c['poseRecords']={p:f.replace('.png','.derivation.json') for p,f in mapping.items()};c['animationPolicy']='Resolve master/win/lose to this costume own independent PNGs; timeline is 2D pose-switch motion, not articulated animation.'
    for j,pose in enumerate(['master','win','lose']):
        image=Image.open(root/mapping[pose]).convert('RGBA');image.thumbnail((280,340),Image.Resampling.LANCZOS)
        # Two backgrounds expose white fringes and transparency residue at display size.
        for side,color in enumerate(['#f7f0df','#17392f']):
            x=i*300;y=side*600+j*190
            tile=Image.new('RGBA',(300,190),color);image=Image.open(root/mapping[pose]).convert('RGBA');image.thumbnail((180,180),Image.Resampling.LANCZOS);tile.alpha_composite(image,((300-image.width)//2,190-image.height));contact.paste(tile.convert('RGB'),(x,y));draw.text((x+5,y+5),skin+' '+pose,fill='#887d60')
write('assets/characters/manifest.json',manifest);character=read('assets/characters/daotong/character.json');character['costumes']=dt['costumes'];write('assets/characters/daotong/character.json',character)
write('assets/characters/costume-poses.json',dict(schemaVersion=1,status='exported_needs_visual_review',assets=assets,counts=dict(costumes=5,independentPoses=10),animationKind='independent still poses plus 2D keyframes',wholeGameArtComplete=False))
contact.save(root/'.work/costume-pose-contact.png')
print(json.dumps(dict(exported=len(assets),costumes=5,contact='.work/costume-pose-contact.png')))
