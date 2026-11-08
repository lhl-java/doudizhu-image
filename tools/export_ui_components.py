from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
out=root/'assets/ui'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
atlas51='designs/ui/components/51-common-components-v1.png'
atlas52='designs/ui/components/52-card-and-effects-v1.png'
rows=[]
for group,source,items in [
('controls',atlas51,[
('primary-normal',(0,0,363,190)),('primary-highlight',(363,0,735,190)),('primary-pressed',(735,0,1084,190)),('primary-disabled',(1084,0,1448,190)),
('secondary-normal',(0,190,363,331)),('secondary-highlight',(363,190,735,331)),('secondary-pressed',(735,190,1084,331)),('secondary-disabled',(1084,190,1448,331)),
('title-primary',(0,331,480,500)),('title-secondary',(480,331,880,500)),('tab-selected',(880,331,1148,500)),('tab-normal',(1148,331,1448,500)),
('checkbox-off',(80,500,320,657)),('checkbox-on',(425,500,682,657)),('toggle-on',(747,500,1046,657)),('toggle-off',(1076,500,1448,657)),
('input-normal',(0,657,370,790)),('input-focus',(370,657,735,790)),('progress',(735,657,1080,790)),('slider',(1080,657,1448,790)),
('panel',(0,790,594,1086)),('close',(594,790,878,1086)),('scrollbar',(890,790,1025,1086)),('avatar-frame',(1085,790,1448,1086))]),
('cards-source',atlas52,[
('card-blank',(155,0,385,282)),('ace-spades',(461,0,694,283)),('ace-hearts',(764,0,994,283)),('ace-clubs',(1062,0,1297,283)),
('ace-diamonds',(155,279,385,565)),('joker-small',(461,279,694,565)),('joker-big',(764,279,994,565)),('back-jade',(1062,279,1297,565)),
('back-ivory',(155,565,385,850)),('landlord',(392,575,737,825)),('farmer',(737,575,1058,825)),('selection',(1063,562,1298,851)),
('bomb',(105,847,410,1086)),('rocket',(410,847,724,1086)),('spring',(725,847,1036,1086)),('counter-spring',(1036,847,1345,1086))])]:
    im=Image.open(root/source).convert('RGBA')
    dest=out/group;dest.mkdir(parents=True,exist_ok=True)
    source_record=source.replace('.png','.generation.json')
    for name,rect in items:
        piece=im.crop(rect)
        bbox=piece.getbbox()
        if bbox:piece=piece.crop(bbox)
        path=dest/(name+'.png');piece.save(path)
        info=dict(file=path.relative_to(root).as_posix(),sha256=sha(path),width=piece.width,height=piece.height,format='PNG',operation='crop-only-preserve-source-RGBA-no-resize',cropRect=list(rect),trimRect=list(bbox) if bbox else None,derivedFrom=dict(file=source,sha256=sha(root/source),generationRecord=source_record),actualModel=None,actualQuality=None,modelEvidence='Follow derivedFrom generationRecord; do not treat crop as new generation.',status='derived_asset_ready_user_review')
        path.with_suffix('.derivation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        rows.append(info)
# Exact ranks and suit typography are native text laid over the generated blank card skin.
deck=out/'cards';deck.mkdir(exist_ok=True)
basepath=out/'cards-source/card-blank.png'
base=Image.open(basepath).convert('RGBA');w,h=base.size
rankfont=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',max(22,w//7))
suitfont=ImageFont.truetype('C:/Windows/Fonts/seguisym.ttf',max(22,w//7))
centerfont=ImageFont.truetype('C:/Windows/Fonts/seguisym.ttf',max(54,w//3))
largefont=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',max(58,w//3))
suits=[('spades','♠',(24,39,33,255)),('hearts','♥',(173,43,32,255)),('clubs','♣',(24,39,33,255)),('diamonds','♦',(173,43,32,255))]
for suit,symbol,color in suits:
    for rank in ['A','2','3','4','5','6','7','8','9','10','J','Q','K']:
        card=base.copy()
        layer=Image.new('RGBA',(w,h));d=ImageDraw.Draw(layer)
        d.text((w*.19,h*.14),rank,font=rankfont,fill=color,anchor='mm')
        d.text((w*.19,h*.26),symbol,font=suitfont,fill=color,anchor='mm')
        corner=layer.copy()
        card.alpha_composite(corner);card.alpha_composite(corner.rotate(180))
        d2=ImageDraw.Draw(card)
        if rank in ['J','Q','K']:
            d2.text((w/2,h*.45),rank,font=largefont,fill=color,anchor='mm')
            d2.text((w/2,h*.68),symbol,font=suitfont,fill=color,anchor='mm')
        else:
            d2.text((w/2,h*.52),symbol,font=centerfont,fill=color,anchor='mm')
        path=deck/f'{suit}-{rank}.png';card.save(path)
        info=dict(file=path.relative_to(root).as_posix(),sha256=sha(path),width=w,height=h,rank=rank,suit=suit,symbol=symbol,operation='native-typeset-rank-and-suit-over-generated-blank-card-no-resize',derivedFrom=dict(file=basepath.relative_to(root).as_posix(),sha256=sha(basepath),record=basepath.with_suffix('.derivation.json').relative_to(root).as_posix()),actualModel=None,actualQuality=None,status='derived_asset_ready_user_review')
        path.with_suffix('.derivation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        rows.append(info)
for key in ['small','big']:
    source=out/f'cards-source/joker-{key}.png'
    im=Image.open(source).convert('RGBA')
    path=deck/f'joker-{key}.png';im.save(path)
    info=dict(file=path.relative_to(root).as_posix(),sha256=sha(path),width=im.width,height=im.height,rank='JOKER',suit=key,operation='copy-of-cropped-generated-joker',derivedFrom=dict(file=source.relative_to(root).as_posix(),sha256=sha(source),record=source.with_suffix('.derivation.json').relative_to(root).as_posix()),status='derived_asset_ready_user_review')
    path.with_suffix('.derivation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');rows.append(info)
manifest=dict(recordedAt=datetime.now(timezone.utc).isoformat(),note='Native art crops plus native text-derived cards. No generated image was upscaled. Cards use one original generated blank face with deterministic correct ranks and suits; not 54 independent AI images.',counts=dict(controls=24,sourceCardsAndEffects=16,deck=54,total=len(rows)),assets=rows)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# A contact sheet only for reviewing derived assets; not a new generated image.
thumbs=[]
for row in rows:
    if row['file'].startswith('assets/ui/cards/'):
        im=Image.open(root/row['file']).convert('RGBA');im.thumbnail((112,156))
        thumbs.append((row['file'],im))
sheet=Image.new('RGB',(9*132,6*190),(248,244,232));d=ImageDraw.Draw(sheet)
label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
for i,(name,im) in enumerate(thumbs):
    x=(i%9)*132;y=(i//9)*190;sheet.paste(im,(x+10,y+8),im);d.text((x+4,y+165),Path(name).stem,font=label,fill=(28,62,46))
preview=out/'deck-review.jpg';sheet.save(preview,quality=92)
print(json.dumps(manifest['counts']))

