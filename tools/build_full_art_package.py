from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((root/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read('assets/ui/manifest.json');kit=read('assets/ui/runtime-kit/manifest.json');chars=read('assets/characters/manifest.json');scenes=read('assets/scenes/scenes.json');fx=read('assets/fx/manifest.json');anims=read('assets/animations/characters/manifest.json')
controls={Path(a['file']).stem:a['file'] for a in old['assets'] if a['file'].startswith('assets/ui/controls/')}
cards={Path(a['file']).stem:a['file'] for a in old['assets'] if a['file'].startswith('assets/ui/cards/')}
icons={a['id']:a['file'] for a in kit['assets'] if a['kind']=='icon'};skins={a['id']:a['file'] for a in kit['assets'] if a['kind']=='skin'}
actors={c['id']:dict(name=c['name'],**c['poses'],expressions=c['expressions'],anchor=c['anchor']) for c in chars['characters']}
costumes=next(c['costumes'] for c in chars['characters'] if c['id']=='daotong')
registry={}
def add(file,kind,id=None,record=None):
    if file in registry:return
    path=root/file
    if not path.exists():raise ValueError('Asset absent '+file)
    if not record:
        options=[path.with_suffix('.derivation.json'),path.with_suffix('.generation.json'),Path(str(path)+'.generation.json')]
        candidate=next((p for p in options if p.exists()),None)
        record=candidate.relative_to(root).as_posix() if candidate else None
    if not record:raise ValueError('Asset record absent '+file)
    with Image.open(path) as im:
        width,height,fmt=im.width,im.height,im.format
        mode=im.mode;alpha=im.getextrema()[-1] if 'A' in im.getbands() else None
    rec=read(record)
    if rec.get('sha256') and rec['sha256'].lower()!=sha(path):raise ValueError('Record hash differs '+file)
    registry[file]=dict(id=id or file.replace('assets/','').replace('/','.'),file=file,record=record,kind=kind,width=width,height=height,format=fmt,pixelMode=mode,alphaExtrema=alpha,sha256=sha(path))
for a in old['assets']:add(a['file'],'ui-'+Path(a['file']).parts[2],record=a['file'].replace('.png','.derivation.json'))
for a in kit['assets']:add(a['file'],a['kind'],a['id'],a['record'])
for c in chars['characters']:
    for pose,file in c['poses'].items():add(file,'actor',c['id']+'_'+pose)
    for emotion,file in c['expressions'].items():add(file,'portrait',c['id']+'_'+emotion)
    for skin in c.get('costumes',[]):add(skin['file'],'costume',skin['id'],skin['record'])
    for skin in c.get('costumes',[]):
        for pose,file in skin.get('poses',{}).items():
            if pose!='master':add(file,'costume-pose',skin['id']+'_'+pose,skin['poseRecords'][pose])
for a in scenes['assets']:add(a['file'],a['kind'],a['id'],a['record'])
effects=fx.get('effects',fx.get('assets',[]))
for a in effects:add(a['file'],'fx',a['id'],a['record'])
for manifest in ['assets/brand/manifest.json','assets/events/manifest.json']:
    for a in read(manifest)['assets']:add(a['file'],a['kind'],a['id'],a['record'])
for a in anims['clips']:add(a['sheet'],'actor-preview-sheet','animation-preview.'+a['id'],a['record'])
metrics=read('assets/ui/runtime-kit/control-metrics.json')['assets']
index=dict(schemaVersion=1,scenes={a['logicalId']:a['file'] for a in scenes['assets'] if a['kind']=='background'},tables={a['logicalId']:a['file'] for a in scenes['assets'] if a['kind']=='foreground'},actors=actors,costumes=costumes,controls=controls,cards=cards,icons=icons,skins=skins,metrics=metrics,brand={a['id']:a['file'] for a in read('assets/brand/manifest.json')['assets']},events={a['id']:a['file'] for a in read('assets/events/manifest.json')['assets']},fx=effects,animations=anims['clips'],assetCount=len(registry),previewAssets=list(registry.values()))
out=root/'assets/game';out.mkdir(parents=True,exist_ok=True)
index['branding']=read('config/brand.json')
(out/'runtime-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Pack reusable UI, portraits and FX at 1:1 source resolution, 4px gutters, no rotation.
packable=[a for a in registry.values() if a['kind'] not in ['actor','costume','costume-pose','background','foreground','title','app-icon','event-banner','actor-preview-sheet']]
packable.sort(key=lambda a:(-a['height'],-a['width'],a['file']))
limit=4096;gap=4;pages=[];current=[];x=y=rowh=gap
for a in packable:
    w,h=a['width'],a['height']
    if w+gap*2>limit or h+gap*2>limit:raise ValueError('Sprite too large '+a['file'])
    if x+w+gap>limit:x=gap;y+=rowh+gap;rowh=0
    if y+h+gap>limit:pages.append(current);current=[];x=y=gap;rowh=0
    current.append((a,x,y));x+=w+gap;rowh=max(rowh,h)
if current:pages.append(current)
atlasdir=out/'atlases';atlasdir.mkdir(exist_ok=True)
textures=[];frames=[]
for pi,entries in enumerate(pages):
    maxx=max(x+a['width']+gap for a,x,y in entries);maxy=max(y+a['height']+gap for a,x,y in entries)
    w=min(limit,2**(maxx-1).bit_length());h=min(limit,2**(maxy-1).bit_length())
    atlas=Image.new('RGBA',(w,h),(0,0,0,0))
    for a,x,y in entries:
        im=Image.open(root/a['file']).convert('RGBA');atlas.paste(im,(x,y))
        frames.append(dict(id=a['id'],source=a['file'],sourceSha256=a['sha256'],texture=pi,rect=[x,y,a['width'],a['height']],rotated=False,trimmed=False,sourceSize=[a['width'],a['height']],pivot=[.5,.5]))
        if atlas.crop((x,y,x+a['width'],y+a['height'])).tobytes()!=im.tobytes():raise ValueError('Pack pixels changed '+a['file'])
    file=atlasdir/f'atlas-{pi:02}.png';atlas.save(file,optimize=True)
    tex=dict(file=file.relative_to(root).as_posix(),width=w,height=h,sha256=sha(file))
    textures.append(tex)
    file.with_suffix('.derivation.json').write_text(json.dumps(dict(**tex,operation='RGBA sprite packing at source1:1; no resize, no rotation, 4px transparent gutters',derivedFrom=[dict(file=a['file'],sha256=a['sha256'],record=a['record']) for a,x,y in entries]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
atlas_manifest=dict(schemaVersion=1,textures=textures,frames=frames,coordinateSystem='top-left pixels, straight RGBA alpha, source-sized sprites',gutter=gap,scale=1)
(out/'atlas.json').write_text(json.dumps(atlas_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Godot4 AtlasTexture resources can be imported directly; anchors and nine-slice live in common JSON.
gdir=out/'godot';gdir.mkdir(exist_ok=True)
for i,f in enumerate(frames):
    tex=textures[f['texture']]['file'];r=f['rect']
    tres=f'[gd_resource type="AtlasTexture" load_steps=2 format=3]\n\n[ext_resource type="Texture2D" path="res://{tex}" id="1"]\n\n[resource]\natlas = ExtResource("1")\nregion = Rect2({r[0]}, {r[1]}, {r[2]}, {r[3]})\nfilter_clip = true\n'
    (gdir/f'sprite-{i:03}.tres').write_text(tres,encoding='utf-8')
manifest=dict(schemaVersion=1,updatedAt=datetime.now(timezone.utc).isoformat(),scope='three-character 2D Doudizhu game art; full-body video, sound/voice, server and game logic are not included',assets=list(registry.values()),counts=dict(Counter(a['kind'] for a in registry.values())),total=len(registry),atlas='assets/game/atlas.json',runtimeIndex='assets/game/runtime-index.json',screens='runtime/screens.json',locale='runtime/copy.zh-CN.json',controlMetrics='assets/ui/runtime-kit/control-metrics.json',fontContract='assets/ui/runtime-kit/font-contract.json',characterAnimations='assets/animations/characters/manifest.json',fx='assets/fx/manifest.json')
manifest['branding']='config/brand.json'
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Resolve the UI worker's external art logical IDs without rewriting its historical source mappings.
mapping=read('assets/ui/runtime-kit/mapping.json')
(out/'resolved-screen-art.json').write_text(json.dumps(dict(source='assets/ui/runtime-kit/mapping.json',sourceSha256=sha(root/'assets/ui/runtime-kit/mapping.json'),backgroundLogicalIds=index['scenes'],tableLogicalIds=index['tables'],actorLogicalIds=actors,resolution='all files exist and are indexed',screenBindings='runtime/screens.json'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(assets=len(registry),atlasTextures=len(textures),atlasSprites=len(frames),counts=manifest['counts']),ensure_ascii=False))

