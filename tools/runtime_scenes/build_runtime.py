import json,hashlib,datetime,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import numpy as np
from scipy import ndimage
ROOT=Path("D:/work/doudizhu-image")
OUT=ROOT/"designs/runtime-scenes-20261026"
FX=ROOT/"assets/fx";SCENES=ROOT/"assets/scenes"
FX.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT)).replace("\\","/")
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
def alpha_qa(im):
 a=np.array(im.getchannel("A"));mask=a>16
 edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
 yy,xx=np.where(mask)
 return {"mode":im.mode,"alphaMin":int(a.min()),"alphaMax":int(a.max()),"transparentPixels":int((a==0).sum()),"softAlphaPixels":int(((a>0)&(a<255)).sum()),"edgeVisiblePixelsAbove16":int((edge>16).sum()),"bboxVisibleAbove16":[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None,"status":"passed" if len(xx) and (edge>16).sum()==0 and (a==0).any() else "needs_fix"}
def source_entry(p,role,record=None):return {"file":rel(p),"sha256":sha(p),"record":record or (rel(p)+".generation.json"),"role":role}
def derived_record(path,source,operation,extra=None):
 im=Image.open(path)
 data={"schemaVersion":1,"file":rel(path),"sha256":sha(path),"width":im.width,"height":im.height,"format":"PNG","createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"route":"derived","art_source":"existing","tool":"Pillow/NumPy/SciPy deterministic asset processing","operation":operation,"actualModel":None,"actualQuality":None,"modelEvidence":"Follow derivedFrom source generation record; processing is not new AI generation","derivedFrom":source,"alphaQA":alpha_qa(im.convert("RGBA")),"visualReview":{"status":"pending_visual_review","note":""}}
 if extra:data.update(extra)
 write(str(path)+".generation.json",data)
 return data
# Foregrounds: drop imperceptible alpha floor only, preserve source detail 1:1, transparent padding.
scene_entries=[]
for name,logical,kind in [("courtyard-lobby","lobby","background"),("courtyard-day","day","background"),("courtyard-moon","night","background"),("jade-table","jade","foreground"),("peach-table","peach","foreground")]:
 p=SCENES/("courtyard-moon-v2.png" if name=="courtyard-moon" else name+".png");im=Image.open(p);rec=read(str(p)+".generation.json")
 if kind=="foreground":
  a=np.array(im.convert("RGBA"));a[a[:,:,3]<=4,3]=0
  padded=Image.new("RGBA",(im.width+128,im.height+128),(0,0,0,0));padded.alpha_composite(Image.fromarray(a),(64,64))
  target=SCENES/(name+"-runtime.png");padded.save(target)
  rec=derived_record(target,[source_entry(p,"original native RGBA foreground")],"alpha-floor<=4 to zero; 64px transparent canvas padding on all sides; original artwork pixels kept 1:1, no resize",{"nativeArtworkResolution":{"width":im.width,"height":im.height},"canvasPadding":[64,64,64,64]})
  p=target;im=padded
 anchor={"x":.5,"y":.82 if kind=="foreground" else .5}
 scene_entries.append({"id":name,"logicalId":logical,"file":rel(p),"record":rel(p)+".generation.json","width":im.width,"height":im.height,"kind":kind,"anchor":anchor,"layer":"table" if kind=="foreground" else "background","z":20 if kind=="foreground" else 0,"status":"pending_visual_review","fit":"contain" if kind=="foreground" else "cover","safeAreaNormalized":{"left":.2,"top":.27,"right":.8,"bottom":.68} if kind=="foreground" else {"left":.14,"top":.08,"right":.86,"bottom":.92}})
scene_manifest={"schemaVersion":1,"logicalViewport":{"width":2560,"height":1080},"sceneMode":"baked_scene_mode","art_source":"host_image","assets":scene_entries,"scenes":[{"id":"lobby","background":"courtyard-lobby","table":None},{"id":"day","background":"courtyard-day","table":"jade-table"},{"id":"night","background":"courtyard-moon","table":"peach-table"}],"cropPolicy":{"2.37:1":"background centered cover, foreground contain-fit; native source retained","16:9":"center-crop background to 1.7778; preserve x .14-.86; foreground always contain-fit and reposition anchor, never crop table silhouette","ui":"separate native layers, no UI/people/text baked into these assets"},"runtimePlacement":{"background":{"x":.5,"y":.5,"anchor":[.5,.5],"z":0},"table":{"x":.5,"y":.90,"anchor":[.5,.82],"maxWidth":.96,"maxHeight":.68,"z":20}},"note":"Source artwork is not a walkable map; no collision/nav claim. Runtime scaling changes display size, not source native detail."}
write(SCENES/"scenes.json",scene_manifest)
# 12 FX: keep all connected components; ownership follows cell containing most visible pixels.
groups=[("a",["deal-trail","play-glow","bomb-burst","rocket-trail","spring-petals","counter-spring-leaves"]),("b",["win-gold","lose-cloud","rank-up","reward-sparkle","turn-ring","loading-ring"])]
timelines=read(ROOT/"tools/runtime_scenes/timelines.json")
fx_entries=[];ownership_reports=[]
review=Image.new("RGBA",(1536,1024),(0,0,0,0))
for sheet_letter,names in groups:
 sheet_path=OUT/("fx-sheet-"+sheet_letter+".png");im=Image.open(sheet_path).convert("RGBA");arr=np.array(im);a=arr[:,:,3]
 labels,n=ndimage.label(a>16,np.ones((3,3)))
 owner_by_label=np.zeros(n+1,dtype=np.int16)-1
 for label in range(1,n+1):
  yy,xx=np.where(labels==label);cells=(yy//512)*3+(xx//512);owner_by_label[label]=int(np.bincount(cells,minlength=6).argmax())
 seed_owner=owner_by_label[labels]
 # Low-alpha halo belongs to nearest visible component, never a full-sheet opaque matte.
 _,nearest=ndimage.distance_transform_edt(labels==0,return_indices=True)
 nearest_owner=seed_owner[nearest[0],nearest[1]]
 for idx,name in enumerate(names):
  mask=(seed_owner==idx)|((a>4)&(a<=16)&(nearest_owner==idx))
  owned=arr.copy();owned[:,:,3]=np.where(mask,a,0).astype(np.uint8)
  owned[owned[:,:,3]<=4,3]=0
  owned_im=Image.fromarray(owned)
  box=owned_im.getbbox()
  if not box:raise RuntimeError("empty FX "+name)
  crop=owned_im.crop(box)
  # Maximum art 340px on 512px source canvas gives >15% safe frame at source output.
  scale=min(1.0,340/max(crop.size));size=(max(1,round(crop.width*scale)),max(1,round(crop.height*scale)))
  small=crop.resize(size,Image.Resampling.LANCZOS)
  pix=np.array(small);pix[pix[:,:,3]<=4,3]=0;small=Image.fromarray(pix)
  canvas=Image.new("RGBA",(512,512),(0,0,0,0));canvas.alpha_composite(small,((512-small.width)//2,(512-small.height)//2))
  path=FX/(name+".png");canvas.save(path)
  deriv=derived_record(path,[source_entry(sheet_path,"generated transparent FX sheet")],"all visible connected components assigned by majority cell; alpha 5..16 halo assigned to nearest owned component; alpha<=4 cleared; ownership crop; uniform downscale only; center on 512 transparent safe canvas",{"sourceCell":{"row":idx//3,"col":idx%3,"nominalBox":[(idx%3)*512,(idx//3)*512,(idx%3+1)*512,(idx//3+1)*512]},"ownedCropBox":list(box),"uniformScale":scale,"noLargestComponentFiltering":True})
  ownership_reports.append({"id":name,"sheet":rel(sheet_path),"nominalCell":idx,"ownedBBox":list(box),"scale":scale,"alphaQA":deriv["alphaQA"],"componentsKept":int((owner_by_label==idx).sum())})
  clip=timelines[name]
  clip.update({"id":name,"file":rel(path),"record":rel(path)+".generation.json","width":512,"height":512,"kind":"fx","anchor":{"x":.5,"y":.5},"z":80,"sourceNativeCell":{"width":512,"height":512},"staticSource":True,"animationSource":"runtime transforms of generated static illustration, not AI video","maxDisplaySize":384})
  write(FX/(name+".timeline.json"),clip)
  # Actual baked frame animation from same illustration; fixed 384 canvas and center anchor.
  frame_dir=FX/"frames"/name;frame_dir.mkdir(parents=True,exist_ok=True)
  duration=clip["durationMs"];frame_count=16;sample_times=[round(duration*i/(frame_count if clip["loop"] else frame_count-1)) for i in range(frame_count)]
  def at(t):
   keys=clip["keyframes"]
   for left,right in zip(keys,keys[1:]):
    if t<=right["atMs"]:
     q=(t-left["atMs"])/(right["atMs"]-left["atMs"])
     return {k:left[k]+(right[k]-left[k])*q for k in ["alpha","scale","x","y","rotation"]}
   return keys[-1]
  frames=[]
  base_sprite_size=220 if name=="deal-trail" else 300
  for frame_idx,t in enumerate(sample_times):
   pose=at(t);sprite=canvas.resize((round(base_sprite_size*pose["scale"]),round(base_sprite_size*pose["scale"])),Image.Resampling.LANCZOS)
   sprite=sprite.rotate(-pose["rotation"],resample=Image.Resampling.BICUBIC,expand=True)
   data=np.array(sprite);data[:,:,3]=np.rint(data[:,:,3].astype(float)*pose["alpha"]).clip(0,255).astype(np.uint8);sprite=Image.fromarray(data)
   frame=Image.new("RGBA",(384,384),(0,0,0,0))
   x=round(192+pose["x"]*384-sprite.width/2);y=round(192+pose["y"]*384-sprite.height/2)
   frame.alpha_composite(sprite,(x,y))
   fpath=frame_dir/(f"{frame_idx:03d}.png");frame.save(fpath)
   next_t=sample_times[frame_idx+1] if frame_idx+1<frame_count else duration
   frames.append({"file":rel(fpath),"sha256":sha(fpath),"atMs":t,"durationMs":max(1,next_t-t) if frame_idx+1<frame_count else (max(1,duration//frame_count) if clip["loop"] else 1),"width":384,"height":384,"transform":pose})
  frame_manifest={"schemaVersion":1,"id":name,"kind":"derived_spriteframes","route":"derived","operation":"translate/rotate/scale/alpha generated static illustration onto fixed384RGBA canvas, no invented paint details","baseSpriteSize":base_sprite_size,"derivedFrom":[source_entry(path,"runtime FX static sprite",rel(path)+".generation.json")],"timeline":rel(FX/(name+".timeline.json")),"durationMs":duration,"loop":clip["loop"],"blend":clip["blend"],"event":clip["event"],"anchor":{"x":.5,"y":.5},"frames":frames}
  write(frame_dir/"frames.json",frame_manifest)
  entry={k:clip[k] for k in ["id","file","record","width","height","kind","anchor","z","blend","event","durationMs","loop"]}
  entry.update({"timeline":rel(FX/(name+".timeline.json")),"frames":rel(frame_dir/"frames.json"),"status":"pending_visual_review","animationKind":"derived_transform_spriteframes"})
  fx_entries.append(entry)
  # Each sheet preview independent to preserve exact 3x2 source index.
  if sheet_letter=="a":review.alpha_composite(canvas,((idx%3)*512,(idx//3)*512))
 packed=Image.new("RGBA",(1536,1024),(0,0,0,0))
 for idx,name in enumerate(names):packed.alpha_composite(Image.open(FX/(name+".png")).convert("RGBA"),((idx%3)*512,(idx//3)*512))
 packed.save(OUT/("fx-sheet-"+sheet_letter+"-runtime.png"))
fx_manifest={"schemaVersion":1,"logicalViewport":{"width":2560,"height":1080},"assets":fx_entries,"effects":fx_entries,"animationSemantics":{"translationUnit":"fraction of baked384 frame","interpolation":"linear","scale":"uniform","rotation":"clockwise degrees","blend":"normal maps source-over, screen maps screen; renderer must honor blend","events":"trigger only on game-state event; looping animations stop on stopEvent","native_vs_derived":"Two AI-generated source sheets; 12 ownership-sliced runtime sprites; 192 transform-derived frames; no AI video."},"sourceSheets":[{"file":rel(OUT/("fx-sheet-"+letter+".png")),"record":rel(OUT/("fx-sheet-"+letter+".png.generation.json")),"runtimePacked":rel(OUT/("fx-sheet-"+letter+"-runtime.png"))} for letter,_ in groups],"rawQALimit":"A original WARN safe_frame/faint_specks; B original FAIL cross_cell_components/cross_cell_visible, WARN boundary_band/safe_frame/faint_specks. Runtime ownership slicing keeps all components and separates subjects; original reports retained. Final alpha/safety QC is separate."}
write(FX/"manifest.json",fx_manifest);write(OUT/"ownership-qa.json",ownership_reports)
# QA composite contact sheets over real light/dark grounds; previews only.
for letter,names in groups:
 for bg_name,bg in [("light",(242,237,220,255)),("dark",(27,48,42,255))]:
  contact=Image.new("RGBA",(1536,1024),bg)
  for idx,name in enumerate(names):contact.alpha_composite(Image.open(FX/(name+".png")),((idx%3)*512,(idx//3)*512))
  contact.convert("RGB").save(OUT/(f"fx-{letter}-over-{bg_name}.jpg"),quality=92)
# Scene alpha review plates.
for name in ["jade-table","peach-table"]:
 table=Image.open(SCENES/(name+"-runtime.png")).convert("RGBA")
 for bg_name,bg in [("light",(242,237,220,255)),("dark",(27,48,42,255))]:
  ground=Image.new("RGBA",table.size,bg);ground.alpha_composite(table);ground.convert("RGB").save(OUT/(name+"-over-"+bg_name+".jpg"),quality=92)
print(json.dumps({"scenes":5,"fx":len(fx_entries),"frames":len(fx_entries)*16,"sourceSheets":2,"ownershipComponentsRetained":sum(x["componentsKept"] for x in ownership_reports)},ensure_ascii=False))

