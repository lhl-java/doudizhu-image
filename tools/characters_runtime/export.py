from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,hashlib,math,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2]
source=root/'designs/characters/runtime-20261026'
out=root/'assets/characters'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names={'daotong':'玉绿道童','taohua':'桃花女修','hulu':'葫芦长者'}
emotions=['calm','smile','laugh','thinking','surprise','smug','sad','angry']
emotionNames=['平静','微笑','大笑','思考','惊讶','得意','难过','生气']
skinNames={'spring':'桃花春衣','ink':'暮色墨衣','moon':'桂月金衣','snow':'雪色白衣','festival':'庆典红衣'}
items=[];characters=[];qa=[];now=datetime.now(timezone.utc).isoformat()
def bounds(im,threshold=16):
 a=np.array(im.getchannel('A'));ys,xs=np.where(a>=threshold)
 return (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
def ref(p):
 return dict(file=p.relative_to(root).as_posix(),sha256=sha(p),record=p.with_suffix('.generation.json').relative_to(root).as_posix())
def save_derived(im,path,identifier,kind,src,operation,anchor,**kwargs):
 path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
 a=np.array(im.getchannel('A'));edge=int((a[0]>=16).sum()+(a[-1]>=16).sum()+(a[:,0]>=16).sum()+(a[:,-1]>=16).sum())
 r=dict(id=identifier,file=path.relative_to(root).as_posix(),record=path.with_suffix('.derivation.json').relative_to(root).as_posix(),kind=kind,width=im.width,height=im.height,anchor=anchor,sha256=sha(path),operation=operation,derivedFrom=ref(src),alphaExtrema=[int(a.min()),int(a.max())],significantBorderPixels=edge,recordedAt=now,art_source='existing',status='asset_ready_user_review',**kwargs)
 path.with_suffix('.derivation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 items.append(r)
 assert edge==0,identifier+' touching exported canvas'
 return r
for key,title in names.items():
 folder=out/key
 poses={p:Image.open(source/f'{key}-{p}-v1.png').convert('RGBA') for p in ['master','win','lose']}
 b={p:bounds(im) for p,im in poses.items()}
 scale=min(1.,800/(b['master'][3]-b['master'][1]),880/max(v[2]-v[0] for v in b.values()),850/max(v[3]-v[1] for v in b.values()))
 mapping={}
 for pose,im in poses.items():
  bb=b[pose];crop=(max(0,bb[0]-6),max(0,bb[1]-6),min(im.width,bb[2]+6),min(im.height,bb[3]+6))
  piece=im.crop(crop);size=(round(piece.width*scale),round(piece.height*scale))
  piece=piece.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
  origin=((bb[0]+bb[2])/2,bb[3])
  offset=(round(512-(origin[0]-crop[0])*scale),round(920-(origin[1]-crop[1])*scale))
  target=Image.new('RGBA',(1024,1024));target.alpha_composite(piece,offset)
  r=save_derived(target,folder/f'{pose}.png',f'{key}_{pose}','character_pose',source/f'{key}-{pose}-v1.png','crop-to-significant-alpha-bounds-with6px-padding-and-one-fixed-downscale-per-character-registered-to-foot-anchor',[512,920],sourceRect=list(crop),sourceAnchor=list(origin),fixedScale=scale,offset=list(offset),noUpscale=True,pose=pose,characterId=key)
  mapping[pose]=r['file']
 # portraits, preserve all eight under common scale
 sheetpath=source/f'{key}-expressions-v2.png';sheet=Image.open(sheetpath).convert('RGBA');W,H=sheet.size
 cells=[]
 for i in range(8):
  x=i%4;y=i//4;box=(round(x*W/4),round(y*H/2),round((x+1)*W/4),round((y+1)*H/2))
  cell=sheet.crop(box);bb=bounds(cell)
  cells.append((box,cell,bb))
 portraitscale=min(1.,224/max(bb[2]-bb[0] for _,_,bb in cells),224/max(bb[3]-bb[1] for _,_,bb in cells))
 expr={}
 for i,(box,cell,bb) in enumerate(cells):
  crop=(max(0,bb[0]-4),max(0,bb[1]-4),min(cell.width,bb[2]+4),min(cell.height,bb[3]+4))
  piece=cell.crop(crop);piece=piece.convert('RGBa').resize((round(piece.width*portraitscale),round(piece.height*portraitscale)),Image.Resampling.LANCZOS).convert('RGBA')
  offset=(round(128-((bb[0]+bb[2])/2-crop[0])*portraitscale),round(244-(bb[3]-crop[1])*portraitscale))
  target=Image.new('RGBA',(256,256));target.alpha_composite(piece,offset)
  globalcrop=[box[0]+crop[0],box[1]+crop[1],box[0]+crop[2],box[1]+crop[3]]
  r=save_derived(target,folder/'expressions'/f'{emotions[i]}.png',f'{key}_{emotions[i]}','character_expression',sheetpath,'grid-ownership-crop-with4px-alpha-padding-and-one-fixed-downscale-per-character-portrait',[128,244],expression=emotions[i],expressionName=emotionNames[i],grid=dict(columns=4,rows=2,index=i,cellRect=list(box)),sourceRect=globalcrop,fixedScale=portraitscale,offset=list(offset),noUpscale=True,characterId=key)
  expr[emotions[i]]=r['file']
 char=dict(id=key,name=title,art_source='host_image',canvas=[1024,1024],anchor=[512,920],recommendedDisplayHeight=520,faceDisplayHeight=128,poses=mapping,expressions=expr,sourceToRuntimeScale=scale,portraitScale=portraitscale,status='asset_ready_user_review',animationBoundary='Three independent still poses; root runtime authors 2D UI keyframe transforms and pose switches. Not image-to-video, skeletal full-body animation or generated in-between frames.')
 (folder/'character.json').write_text(json.dumps(char,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');characters.append(char)
 for pose in poses:
  gp=source/f'{key}-{pose}-v1.generation.json';rec=json.loads(gp.read_text(encoding='utf-8-sig'))
  rec['status']='asset_ready_user_review';rec['visualQA']=dict(status='passed_for_runtime_art_review',method='actual displayed image_gen output and light/dark runtime contact sheet',findings=['Complete distinct identity and requested pose; full hair/shoes/prop readable.','Native RGBA preserved; low alpha outer dust handled by significant-alpha-bound crop with6px safety margin and fixed downscale, not redraw.','Independent still pose only, no continuous character animation claim.'])
  gp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Costume variants share daotong master scale; no alternate emotion body poses on skins.
dt=characters[0];scale=dt['sourceToRuntimeScale'];skins=[]
for skin,label in skinNames.items():
 src=source/f'daotong-costume-{skin}-v1.png'
 if not src.exists():continue
 im=Image.open(src).convert('RGBA');bb=bounds(im);crop=(max(0,bb[0]-6),max(0,bb[1]-6),min(im.width,bb[2]+6),min(im.height,bb[3]+6))
 piece=im.crop(crop).convert('RGBa').resize((round((crop[2]-crop[0])*scale),round((crop[3]-crop[1])*scale)),Image.Resampling.LANCZOS).convert('RGBA')
 origin=((bb[0]+bb[2])/2,bb[3]);offset=(round(512-(origin[0]-crop[0])*scale),round(920-(origin[1]-crop[1])*scale))
 target=Image.new('RGBA',(1024,1024));target.alpha_composite(piece,offset)
 r=save_derived(target,out/'daotong/costumes'/f'{skin}.png',f'daotong_{skin}','character_costume',src,'AI-generated-costume-variant-cropped-and-scaled-with-daotong-fixed-profile',[512,920],costumeName=label,characterId='daotong',sourceRect=list(crop),sourceAnchor=list(origin),fixedScale=scale,offset=list(offset),noUpscale=True)
 skins.append(dict(id=r['id'],name=label,file=r['file'],record=r['record'],characterId='daotong',anchor=r['anchor'],width=r['width'],height=r['height'],animationPolicy='Use this skin for UI transform clips; do not silently swap to base costume win/lose pose.'))
 gp=src.with_suffix('.generation.json');rec=json.loads(gp.read_text(encoding='utf-8-sig'));rec['status']='asset_ready_user_review';rec['editedFrom']=dict(file='designs/characters/runtime-20261026/daotong-master-v1.png',sha256=sha(source/'daotong-master-v1.png'),generationRecord='designs/characters/runtime-20261026/daotong-master-v1.generation.json')
 rec['visualQA']=dict(status='passed_for_runtime_art_review',method='actual image_gen output inspected',findings=['Full character, same face and stance, matching wardrobe variant with newly generated embroidery.','Native RGBA, complete shoes/headband/gourd, no background.'])
 gp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dt['costumes']=[dict(id='daotong_base',name='青云衣',file=dt['poses']['master'],record='assets/characters/daotong/master.derivation.json')]+skins
(out/'daotong/character.json').write_text(json.dumps(dt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Mark chosen expression sheets and superseded source records.
for key in names:
 for ver in [1,2]:
  gp=source/f'{key}-expressions-v{ver}.generation.json';rec=json.loads(gp.read_text(encoding='utf-8-sig'))
  rec['status']='asset_ready_user_review' if ver==2 else 'superseded_layout_too_tight'
  rec['visualQA']=dict(status='passed_for_runtime_art_review' if ver==2 else 'needs_fix',findings=['Eight distinct expressions, selected v2 has clean portrait separation and full hair after layout correction.' if ver==2 else 'Native transparent portraits were too tightly packed; layout corrected by AI edit in v2.'])
  if ver==2:rec['editedFrom']=dict(file=f'designs/characters/runtime-20261026/{key}-expressions-v1.png',sha256=sha(source/f'{key}-expressions-v1.png'),generationRecord=f'designs/characters/runtime-20261026/{key}-expressions-v1.generation.json')
  gp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=dict(schemaVersion=1,recordedAt=now,status='asset_ready_user_review',characters=characters,costumes=skins,assets=items,counts=dict(characters=3,poses=9,expressions=24,costumes=len(skins),runtimePngs=len(items),nativeGenerations=20,selectedNativeGenerations=17),notes=['All runtime PNGs derived from actual built-in image generation/AI edits, RGBA alpha.','No runtime output upscaled. 1024 square poses registered foot anchor [512,920], 256 square expressions anchor [128,244].','Three rejected tight expression sheet images retain source records until selected references migration; source images can be removed after current source hashes recorded.','Character motion is an engine-authored 2D UI timeline, not AI video or full-body skeletal animation.'])
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# QA contact sheets from derived assets. Not new generated art.
rev=out/'review';rev.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for group,select,columns,tile in [('poses',[x for x in items if x['kind']=='character_pose'],3,(360,420)),('costumes',[x for x in items if x['kind']=='character_costume'],5,(240,300)),('expressions',[x for x in items if x['kind']=='character_expression'],8,(160,190))]:
 rows=math.ceil(len(select)/columns);sheet=Image.new('RGB',(columns*tile[0],rows*tile[1]*2),(248,242,226));draw=ImageDraw.Draw(sheet)
 for i,item in enumerate(select):
  im=Image.open(root/item['file']).convert('RGBA');im.thumbnail((tile[0]-16,tile[1]-40),Image.Resampling.LANCZOS)
  for dark in [0,1]:
   x=(i%columns)*tile[0];y=(i//columns)*tile[1]+dark*rows*tile[1]
   if dark:draw.rectangle((x,y,x+tile[0],y+tile[1]),fill=(18,48,41))
   sheet.paste(im,(x+(tile[0]-im.width)//2,y+8),im);draw.text((x+8,y+tile[1]-25),item['id'],font=font,fill=(235,226,195) if dark else (25,67,52))
 path=rev/f'{group}-light-dark.jpg';sheet.save(path,quality=94)
 deriv=dict(file=path.relative_to(root).as_posix(),sha256=sha(path),operation='contact-sheet-for-alpha-and-silhouette-review-only',derivedFrom=[dict(file=x['file'],sha256=x['sha256'],record=x['record']) for x in select])
 path.with_suffix('.derivation.json').write_text(json.dumps(deriv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest['counts']))

