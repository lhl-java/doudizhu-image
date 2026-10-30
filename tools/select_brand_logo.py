"""Adopt the host-generated brand logo and export transparent, source-sized padding."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
out=root/'assets/brand/daoyou-qing-chupai';out.mkdir(parents=True,exist_ok=True)
source=Path(r'C:/Users/luyua/.codex/generated_images/01a17714-4402-7063-9782-93f78261cb48/exec-c577e426-e262-4e4f-9f05-afbc507dc232.png')
native=out/'logo-native-v1.png'
if native.exists():raise SystemExit('This version is already adopted; use a new version for new generation')
shutil.copy2(source,native)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(root).as_posix()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
refs=['references/style/01-mail-event.png','references/style/team-ui-v2.png','assets/brand/title.png']
prompt='prompts/brand/daoyou-logo-v1.txt';receipt=out/'logo-native-v1.receipt.json'
write(receipt,dict(tool='image_gen.imagegen',returnedKeys=['image_url','output_hint'],hostOutputFile=str(source),recordedAt=now,actualModel=None,actualQuality=None))
with Image.open(native) as im:
    im.load();size=im.size;mode=im.mode;alpha=im.getchannel('A');extrema=alpha.getextrema()
    significant=alpha.point(lambda v:255 if v>16 else 0).getbbox()
    if mode!='RGBA' or extrema!=(0,255):raise ValueError('Native output is not real transparent RGBA')
    # Preserve every returned source pixel; add safety canvas only, no resampling/repainting.
    padded=Image.new('RGBA',(im.width+128,im.height+128),(0,0,0,0));padded.paste(im,(64,64))
    final=out/'logo-v1.png';padded.save(final,optimize=True)
    web=out/'logo-1024.png';height=round(padded.height*1024/padded.width)
    padded.resize((1024,height),Image.Resampling.LANCZOS).save(web,optimize=True)
native_rec=native.with_suffix('.generation.json')
write(native_rec,dict(schemaVersion=1,file=rel(native),sha256=sha(native),generatedAt=now,generatedAtEvidence='time recorded after host return; not model internal timestamp',width=size[0],height=size[1],format='PNG',pixelMode=mode,alphaExtrema=extrema,significantAlphaBBox=significant,nativeResolution=dict(width=size[0],height=size[1]),tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=True,referenced_image_paths=[str(root/f) for f in refs]),actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未披露／无可核实元数据；配置目标不是实际锁定API分支和质量证据',prompt=prompt,promptSha256=sha(root/prompt),references=[dict(file=f,sha256=sha(root/f),role='primary style reference' if i<2 else 'existing genre-title finish reference') for i,f in enumerate(refs)],evidence=dict(receipt=rel(receipt),hostOutputFile=str(source)),operation='byte-identical-copy-no-resize',visualQA=dict(status='passed_for_brand_art_review',mainText='道友请出牌',subtitle='斗地主',observations=['已实际查看宿主返回成图；五字主名及三字副标完整可读；葫芦、太极、云纹、流苏与纸牌采用既有玉绿/米白/暖金画法。','Native canvas has alpha=1 at some boundary pixels; final runtime export adds64px fully transparent padding on all sides without changing the artwork.','Decorative card fan is a logo motif, not a gameplay hand or dealt-card state.'],userApproved=False)))
for target,operation,parent,parent_record in [(final,'Add64px transparent border on all four sides; paste exact native RGBA pixels 1:1; no resize or repaint.',native,native_rec),(web,'Uniform Lanczos downscale of padded logo to1024px width; no repaint or new image generation.',final,final.with_suffix('.derivation.json'))]:
    with Image.open(target) as im:w,h=im.size
    write(target.with_suffix('.derivation.json'),dict(file=rel(target),sha256=sha(target),width=w,height=h,format='PNG',pixelMode='RGBA',route='derived',operation=operation,noUpscale=True,derivedFrom=[dict(file=rel(parent),sha256=sha(parent),record=rel(parent_record))]))
brand=dict(schemaVersion=1,name='道友请出牌',subtitle='斗地主',genre='斗地主',displayName='道友请出牌·斗地主',slogan='三位道友，一桌好牌。',selectedAt=now,namingBasis='User asked the assistant to settle the name and make the logo; selected to match original Daoist chibi characters and Doudizhu play.',logo=rel(final),logoRecord=rel(final.with_suffix('.derivation.json')),logoNative=rel(native),logoWeb=rel(web),prompt=prompt)
write(root/'config/brand.json',brand)
manifest=json.loads((root/'assets/brand/manifest.json').read_text(encoding='utf-8-sig'))
for a in manifest['assets']:
    if a['id']=='title':
        a.update(file=rel(final),record=rel(final.with_suffix('.derivation.json')),width=padded.width,height=padded.height,sha256=sha(final))
manifest['branding']='config/brand.json';write(root/'assets/brand/manifest.json',manifest)
new=dict(id='title',file=rel(final),record=rel(final.with_suffix('.derivation.json')),kind='title',width=padded.width,height=padded.height,format='PNG',pixelMode='RGBA',alphaExtrema=[0,255],sha256=sha(final))
game=json.loads((root/'assets/game/manifest.json').read_text(encoding='utf-8-sig'))
game['assets']=[new if a['kind']=='title' else a for a in game['assets']];game['branding']='config/brand.json';game['updatedAt']=now
write(root/'assets/game/manifest.json',game)
index=json.loads((root/'assets/game/runtime-index.json').read_text(encoding='utf-8-sig'))
index['brand']['title']=rel(final);index['branding']=brand;index['previewAssets']=[new if a['kind']=='title' else a for a in index['previewAssets']]
write(root/'assets/game/runtime-index.json',index)
copy=json.loads((root/'runtime/copy.zh-CN.json').read_text(encoding='utf-8-sig'));copy['brand']=brand;write(root/'runtime/copy.zh-CN.json',copy)
write(out/'manifest.json',dict(branding='config/brand.json',assets=[dict(role=role,file=rel(p),record=rel(p.with_suffix('.generation.json' if p==native else '.derivation.json')),sha256=sha(p)) for role,p in [('native',native),('runtime',final),('web',web)]]))
print(json.dumps(dict(name=brand['name'],native=rel(native),nativeSize=size,runtime=rel(final),runtimeSize=list(padded.size),web=rel(web)),ensure_ascii=False))
