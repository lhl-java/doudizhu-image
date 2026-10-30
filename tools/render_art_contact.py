"""Compose existing final PNGs for offline visual inspection; not a browser screenshot."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/integration'
OUT.mkdir(parents=True, exist_ok=True)
I = json.loads((ROOT/'assets/game/runtime-index.json').read_text(encoding='utf-8'))
BRAND = json.loads((ROOT/'config/brand.json').read_text(encoding='utf-8'))
W, H = 1932, 815
sources = {}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(file):
    p = ROOT/file
    sources[file] = sha(p)
    return Image.open(p).convert('RGBA')
def font(n, title=False):
    return ImageFont.truetype('C:/Windows/Fonts/simkai.ttf' if title else 'C:/Windows/Fonts/msyh.ttc', n)
def text(im, xy, s, n=27, fill='#234f40', anchor='mm', title=False):
    ImageDraw.Draw(im).text(xy, s, font=font(n,title), fill=fill, anchor=anchor)
def put(im, file, box):
    p = load(file)
    # Display is a downscale only; this composition adds no generated detail.
    size=(min(box[2],p.width),min(box[3],p.height))
    p=ImageOps.contain(p,size,Image.Resampling.LANCZOS)
    im.alpha_composite(p,(round(box[0]+(box[2]-p.width)/2),round(box[1]+(box[3]-p.height)/2)))
def patch(im,file,box,insets=(64,64,64,64)):
    p=load(file);x,y,w,h=box;l,t,r,b=insets
    sx=[0,l,p.width-r,p.width];sy=[0,t,p.height-b,p.height]
    edge_scale=min(.65,(w-2)/(l+r),(h-2)/(t+b))
    dl,dt,dr,db=[max(1,int(v*edge_scale)) for v in (l,t,r,b)]
    dx=[x,x+dl,x+w-dr,x+w];dy=[y,y+dt,y+h-db,y+h]
    for j in range(3):
        for k in range(3):
            tile=p.crop((sx[k],sy[j],sx[k+1],sy[j+1]))
            tile=tile.resize((dx[k+1]-dx[k],dy[j+1]-dy[j]),Image.Resampling.LANCZOS)
            im.alpha_composite(tile,(dx[k],dy[j]))
def button(im,label,box,secondary=False):
    patch(im,I['controls']['secondary-normal' if secondary else 'primary-normal'],box,(65,40,65,40))
    text(im,(box[0]+box[2]/2,box[1]+box[3]/2),label,28,'#234f40' if secondary else '#fff4d2',title=True)
def base(scene,title):
    im=ImageOps.fit(load(I['scenes'][scene]),(W,H),Image.Resampling.LANCZOS)
    patch(im,I['controls']['panel'],(22,16,1888,104))
    text(im,(W/2,65),title,41,title=True)
    text(im,(1645,66),'铜钱 12,800  ·  玉牌 120',26)
    button(im,'返回',(42,28,190,80),True)
    return im
def save(im,name,detail):
    p=OUT/(name+'.png');im.convert('RGB').save(p,optimize=True)
    rec=dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),width=W,height=H,
             operation='Offline Pillow composition of existing final art plus native Chinese text; downscaled sprites and nine-slice UI, no AI generation or browser rendering.',
             browserScreenshot=False,detail=detail,createdAt=datetime.now(timezone.utc).isoformat(),
             derivedFrom=[dict(file=k,sha256=v) for k,v in sorted(sources.items())])
    p.with_suffix('.derivation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sources.clear()

im=base('day','经典斗地主 · 青云场')
put(im,I['tables']['jade'],(125,220,1682,590))
put(im,I['actors']['taohua']['master'],(22,132,350,350))
put(im,I['actors']['hulu']['master'],(1560,132,350,350))
for x,name in [(30,'桃花女修 · 17张'),(1560,'葫芦长者 · 17张')]:
    patch(im,I['controls']['panel'],(x,408,330,80))
    text(im,(x+165,448),name,24)
for j,key in enumerate(['spades-A','hearts-K','diamonds-3']):
    put(im,I['cards'][key],(817+j*95,139,95,127))
text(im,(W/2,292),'底分 100    倍数 ×4',26)
put(im,I['actors']['daotong']['master'],(0,455,330,330))
put(im,'assets/ui/cards-source/landlord.png',(40,704,90,75))
text(im,(220,752),'青云小道',26)
keys=['spades-2','hearts-A','spades-A','hearts-K','spades-K','hearts-Q','clubs-Q','clubs-J','hearts-10','spades-9','hearts-9','clubs-8','spades-7','hearts-7','diamonds-7','clubs-6','spades-5']
for j,key in enumerate(keys):
    put(im,I['cards'][key],(365+j*75,578-(18 if j in [9,10] else 0),130,200))
for x,label,secondary in [(668,'不出',True),(912,'提示',True),(1156,'出牌',False)]:
    button(im,label,(x,461,224,90),secondary)
save(im,'table-day','Layering check: independent scenery, transparent table and three characters, exact card faces, native text and nine-slice controls.')

im=base('lobby',BRAND['name']+' · 欢迎道友')
put(im,I['brand']['title'],(90,140,620,240))
put(im,I['actors']['daotong']['master'],(45,315,650,480))
patch(im,I['controls']['panel'],(735,150,1135,605))
tiles=[('经典模式','classic'),('好友同玩','friend-room'),('排位赛','rank'),('赛事','tournament'),('残局挑战','puzzle'),('单机练习','practice'),('商城','shop'),('任务活动','events')]
for j,(label,key) in enumerate(tiles):
    x=800+(j%4)*255;y=195+(j//4)*250
    patch(im,I['skins']['item-normal'],(x,y,235,225))
    put(im,I['icons'][key],(x+52,y+25,130,130))
    text(im,(x+117,y+180),label,28,title=True)
save(im,'lobby','Layering check: original title, actor, eight independent mode icons, native labels and panel skins.')

im=base('lobby','角色装扮 · 青云小道')
put(im,I['costumes'][3]['file'],(20,142,600,620))
patch(im,I['controls']['panel'],(630,150,1250,605))
for j,c in enumerate(I['costumes']):
    x=690+(j%3)*380;y=190+(j//3)*255
    patch(im,I['skins']['item-selected' if j==3 else 'item-normal'],(x,y,345,242))
    put(im,c['file'],(x+60,y+3,225,190))
    text(im,(x+172,y+212),c['name'],23)
button(im,'使用装扮',(200,700,285,90))
save(im,'wardrobe','Layering check: one base and five independent costume images; this page does not imply alternate costumes have independently redrawn win/lose poses.')
print(json.dumps(dict(outputs=[p.name for p in sorted(OUT.glob('*.png'))],method='offline asset composition, not browser screenshot'),ensure_ascii=False))
