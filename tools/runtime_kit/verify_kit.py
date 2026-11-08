import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path("D:/work/doudizhu-image");KIT=ROOT/"assets/ui/runtime-kit";DES=ROOT/"designs/ui/runtime-kit"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
m=read(KIT/"manifest.json");checks=[];errors=[]
for a in m["assets"]:
 p=ROOT/a["file"];im=Image.open(p);alpha=np.asarray(im.getchannel("A")) if im.mode=="RGBA" else None
 record=read(ROOT/a["record"])
 perimeter=np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]) if alpha is not None else np.array([255])
 source=ROOT/record["derivedFrom"]["file"]
 result={"id":a["id"],"kind":a["kind"],"file":a["file"],"hashMatches":sha(p)==a["sha256"]==record["sha256"],"sourceHashMatches":sha(source)==record["derivedFrom"]["sha256"],"RGBA":im.mode=="RGBA","hasTransparentPixels":bool((alpha==0).any()) if alpha is not None else False,"hasVisiblePixels":bool((alpha>16).any()) if alpha is not None else False,"transparentPerimeter":bool((perimeter==0).all()),"sourceNativeCropPreserved":record["visiblePixelsPreserved"],"resized":False,"size":[im.width,im.height]}
 if a["id"].startswith("portrait"):
  result["centerAlpha"]=int(alpha[im.height//2,im.width//2])
  result["centerTransparent"]=result["centerAlpha"]==0
  if not result["centerTransparent"]: errors.append(a["id"]+": center not transparent")
 if not all(result[k] for k in ["hashMatches","sourceHashMatches","RGBA","hasTransparentPixels","hasVisiblePixels","transparentPerimeter"]):errors.append(a["id"])
 checks.append(result)
# Actual-size light/dark composites; labels are preview text only, never in runtime PNGs.
try:font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",16)
except:font=ImageFont.load_default()
previews=[]
for group in ["icons-navigation-v2","icons-gameplay-v1","icons-resources-v1","skins-windows-v1","skins-slots-v1"]:
 items=[a for a in m["assets"] if a["sourceSheet"]==group]
 cols=4 if group.startswith("icons") or group=="skins-slots-v1" else 2
 rows=(len(items)+cols-1)//cols
 cw=max(a["width"] for a in items)+18
 ch=max(a["height"] for a in items)+42
 panels=[]
 for bg in ["#F8F0DD","#173F32"]:
  canvas=Image.new("RGBA",(cols*cw,rows*ch),bg)
  dr=ImageDraw.Draw(canvas)
  for i,a in enumerate(items):
   im=Image.open(ROOT/a["file"]).convert("RGBA")
   x=(i%cols)*cw+(cw-im.width)//2;y=(i//cols)*ch+6
   canvas.alpha_composite(im,(x,y))
   dr.text(((i%cols)*cw+8,(i//cols)*ch+ch-26),a["id"],fill="#173F32" if bg=="#F8F0DD" else "#FFF6DB",font=font)
  panels.append(canvas)
 board=Image.new("RGBA",(panels[0].width*2,panels[0].height))
 board.alpha_composite(panels[0]);board.alpha_composite(panels[1],(panels[0].width,0))
 out=DES/(group+"-alpha-review.png");board.convert("RGB").save(out)
 previews.append({"file":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"operation":"native-size compositing of runtime assets over ivory and jade backgrounds for review; no source art resized","sourceAssets":[a["file"] for a in items]})
metrics=read(KIT/"control-metrics.json")
for c in metrics["assets"]:
 if c["nineSliceInsets"]:
  n=c["nineSliceInsets"];w,h=c["nativeSize"]
  if n["left"]+n["right"]>=w or n["top"]+n["bottom"]>=h:errors.append("invalid nine-slice "+c["id"])
mapping=read(KIT/"mapping.json")
mappingMissing=[]
for p in mapping["pages"]:
 b=p["artBindings"]
 for k,v in b.items():
  if isinstance(v,str) and not (ROOT/v).is_file():mappingMissing.append([p["pageId"],k,v])
  if k=="icons":
   for i in v:
    if not(ROOT/i["file"]).is_file():mappingMissing.append([p["pageId"],"icon",i["file"]])
errors+=["binding "+str(x) for x in mappingMissing]
result={"schemaVersion":1,"verifiedAt":datetime.now(timezone.utc).isoformat(),"status":"passed" if not errors else "failed","counts":m["counts"],"checks":checks,"metricsCount":len(metrics["assets"]),"pageBindingCount":len(mapping["pages"]),"mappingFilePathsVerified":not mappingMissing,"previews":previews,"errors":errors,
"rawNominalGridCaveat":"Native image generator does not respect uniform mathematical grid. Raw navigation-v1 sheet_qc FAIL cross_cell_components=7 threshold0; cross_cell_visible=7 threshold0; boundary_band WARN2805 threshold0; safe_frame WARN16 threshold0; faint_specks WARN floor88850 detached25. Navigation-v1 also had wrong character identity and is not selected. Selected navigation-v2 corrects identity; all selected sheets use measured transparent-gap adaptive row/column ownership cuts, not nominal grid. Actual final crops pass transparent perimeter and preserve all pixels alpha>16; no main component/largest filter.",
"alphaHygiene":"All source RGB retained. Source alpha<=4 cleared; detached alpha<32 not within2px of alpha>=32 cleared. Perimeter faint residual<=16 cleared. Counts in per-asset derivation and sheet manifest. No keying, painted checkerboard or upscaling.",
"environmentCaveat":"forge_doctor python.path WARN: other Python on PATH; tools explicitly use isolated Python3.12. API routes unavailable and not used. Host image generation is actual route.",
"limits":["Metrics are proposed art geometry, require engine layout and hitbox validation at min/wide sizes","Scene and character logical IDs in mapping await coordinator binding","No claim of game client/server integration"]}
write(KIT/"qa-report.json",result)
write(DES/"alpha-review.derivation.json",{"schemaVersion":1,"previews":previews,"notGeneration":True})
print(json.dumps({"status":result["status"],"counts":result["counts"],"checked":len(checks),"errors":errors,"previews":len(previews),"metrics":len(metrics["assets"]),"mappedPages":len(mapping["pages"])}))

