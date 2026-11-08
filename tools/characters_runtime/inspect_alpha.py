from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
root=Path(r'D:/work/doudizhu-image')
src=root/'designs/characters/runtime-20261026'
rows=[]
for p in src.glob('*.png'):
 im=Image.open(p).convert('RGBA');a=np.array(im.getchannel('A'))
 vals={}
 for t in [1,16,64,128,240]:
  ys,xs=np.where(a>=t)
  vals[t]=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 rows.append(dict(file=p.name,boundsByThreshold=vals,borderAbove128=int((a[0]>=128).sum()+(a[-1]>=128).sum()+(a[:,0]>=128).sum()+(a[:,-1]>=128).sum())))
print(json.dumps(rows,ensure_ascii=False))
p=src/'taohua-expressions-v2.png';im=Image.open(p).convert('RGBA')
canvas=Image.new('RGB',(1774,1774),(248,242,226));canvas.paste(im,(0,0),im)
dark=Image.new('RGB',im.size,(20,48,42));dark.paste(im,(0,0),im);canvas.paste(dark,(0,887))
out=root/'assets/characters/review/expressions-alpha-review.jpg';out.parent.mkdir(parents=True,exist_ok=True);canvas.save(out,quality=93)

