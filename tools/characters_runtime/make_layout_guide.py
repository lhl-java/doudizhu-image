from PIL import Image,ImageDraw
from pathlib import Path
p=Path(r'D:/work/doudizhu-image/tools/characters_runtime/expression-layout-guide.png')
im=Image.new('RGB',(1600,800),(245,245,245));d=ImageDraw.Draw(im)
for row in range(2):
 for col in range(4):
  x=col*400;y=row*400
  d.rectangle((x,y,x+399,y+399),outline=(170,170,170),width=3)
  d.rectangle((x+70,y+60,x+330,y+340),outline=(15,155,75),width=5)
im.save(p)
print(p)

