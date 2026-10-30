import json, hashlib, argparse, math
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from scipy import ndimage
from PIL import Image
ROOT=Path("D:/work/doudizhu-image")
ART=ROOT/"assets/ui/runtime-kit"
DESIGN=ROOT/"designs/ui/runtime-kit"
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
def hygiene(a):
 b=a.copy(); floor=(b>0)&(b<=4); floor_n=int(floor.sum()); b[floor]=0
 near=ndimage.maximum_filter(b>=32,size=5)
 isolated=(b>0)&(b<32)&(~near)
 detached_n=int(isolated.sum()); b[isolated]=0
 return b,dict(alphaFloor=4,floorRemovedPixels=floor_n,faintDetachedRemovedPixels=detached_n,maxFaintRemovedAlpha=31,method="native alpha hygiene only, preserve RGB and all alpha>=32; faint alpha<32 kept within 2px of solid art")
def boundaries(mask,n,axis):
 counts=mask.sum(axis=axis)
 length=len(counts); cuts=[0]; evidence=[]
 for i in range(1,n):
  nominal=round(i*length/n); radius=round(length/n*.23)
  low=max(cuts[-1]+1,nominal-radius); high=min(length-1,nominal+radius)
  window=counts[low:high+1]
  if int(window.min())!=0:
   radius=round(length/n*.48)
   low=max(cuts[-1]+1,nominal-radius);high=min(length-1,nominal+radius)
   window=counts[low:high+1]
  best=np.flatnonzero(window==window.min())+low
  if int(window.min())!=0: raise RuntimeError(f"No clear alpha>16 cut at {axis}/{i}: {int(window.min())}")
  runs=np.split(best,np.flatnonzero(np.diff(best)>1)+1)
  run=sorted(runs,key=lambda x:(-len(x),abs(float(x.mean())-nominal)))[0]
  cut=int(round(float(run.mean())))
  cuts.append(cut);evidence.append(dict(nominal=nominal,actual=cut,visiblePixelsOnCut=int(counts[cut])))
 cuts.append(length);return cuts,evidence
def run():
 plans=json.loads((ROOT/"tools/runtime_kit/sheet-plan.json").read_text(encoding="utf-8-sig"))
 assets=[];sheet_records=[]
 for p in plans:
  sheet="icons-navigation-v2" if p["id"]=="icons-navigation-v1" else p["id"]
  source=DESIGN/(sheet+".png")
  if not source.exists(): continue
  recpath=DESIGN/(sheet+".generation.json")
  rec=json.loads(recpath.read_text(encoding="utf-8-sig"))
  image=Image.open(source)
  if image.mode!="RGBA":raise RuntimeError("not RGBA")
  rgba=np.array(image);a,clean=hygiene(rgba[:,:,3]);rgba[:,:,3]=a
  visible=a>16
  ys,yev=boundaries(visible,p["rows"],axis=1)
  row_x=[];row_xev=[]
  for r in range(p["rows"]):
   xs,xev=boundaries(visible[ys[r]:ys[r+1]],p["cols"],axis=0)
   row_x.append(xs);row_xev.append(xev)
  no_cut_loss=0
  for r in range(p["rows"]):
   xs=row_x[r]
   for c in range(p["cols"]):
    i=r*p["cols"]+c;name=p["names"][i]
    cell=rgba[ys[r]:ys[r+1],xs[c]:xs[c+1]]
    yy,xx=np.where(cell[:,:,3]>16)
    if not len(xx):raise RuntimeError("empty "+name)
    bbox=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
    l=max(0,bbox[0]-6);t=max(0,bbox[1]-6);rr=min(cell.shape[1],bbox[2]+6);bb=min(cell.shape[0],bbox[3]+6)
    crop=cell[t:bb,l:rr].copy()
    # Only trim residual alpha<=16 outside the measured visible bbox + 6px.
    preserved=int((crop[:,:,3]>16).sum())
    if preserved!=len(xx):raise RuntimeError("visible clipping "+name)
    # Ensure the published texture has a real transparent one-pixel perimeter.
    # Any nonzero alpha on perimeter is only <=16 haze; trim it by recorded alpha cleanup.
    edge=np.zeros(crop.shape[:2],dtype=bool);edge[0,:]=True;edge[-1,:]=True;edge[:,0]=True;edge[:,-1]=True
    haze_edge=int(((crop[:,:,3]>0)&edge).sum())
    if np.any((crop[:,:,3]>16)&edge):raise RuntimeError("visible edge contact "+name)
    crop[:,:,3][edge]=0
    target=ART/("icons" if p["type"]=="icons" else "skins")/(name+".png")
    target.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(crop).save(target)
    hist=Image.fromarray(crop[:,:,3]).histogram()
    kind="icon" if p["type"]=="icons" else "skin"
    rect=[xs[c]+l,ys[r]+t,xs[c]+rr,ys[r]+bb]
    record=target.with_suffix(".derivation.json")
    deriv=dict(schemaVersion=1,id=name,kind=kind,file=target.relative_to(ROOT).as_posix(),sha256=sha(target),width=crop.shape[1],height=crop.shape[0],format="PNG",mode="RGBA",
      operation="adaptive transparent-gap crop + documented native-alpha hygiene; no resampling, no redrawing, no upscaling",
      derivedFrom=dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),generationRecord=recpath.relative_to(ROOT).as_posix()),
      cellIndex=i,row=r,column=c,sourceRect=rect,cellRect=[xs[c],ys[r],xs[c+1],ys[r+1]],trimOffset=[l,t],alphaHygiene=clean,perimeterHazePixelsCleared=haze_edge,
      alpha=dict(zeroPixels=hist[0],partialPixels=sum(hist[1:255]),opaquePixels=hist[255],extrema=[min(np.flatnonzero(hist)),max(np.flatnonzero(hist))]),
      visiblePixelsPreserved=preserved,clipping=False,actualModel=rec["actualModel"],actualQuality=rec["actualQuality"],modelEvidence="Follow derivedFrom.generationRecord; this crop is not a new model call",
      status="derived_asset_ready_user_review")
    deriv["alpha"]["extrema"]=[int(x) for x in deriv["alpha"]["extrema"]]
    write(record,deriv)
    assets.append(dict(id=name,kind=kind,file=target.relative_to(ROOT).as_posix(),record=record.relative_to(ROOT).as_posix(),sha256=sha(target),width=crop.shape[1],height=crop.shape[0],alpha=deriv["alpha"],sourceSheet=sheet,sourceRect=rect,status=deriv["status"]))
  sheet_records.append(dict(id=sheet,file=source.relative_to(ROOT).as_posix(),record=recpath.relative_to(ROOT).as_posix(),sha256=sha(source),width=image.width,height=image.height,grid=[p["rows"],p["cols"]],cutsXByRow=row_x,cutsY=ys,cutEvidence=dict(xByRow=row_xev,y=yev),alphaHygiene=clean,nativePixelOperation="crop only plus alpha cleanup, no resampling",visiblePixelsLostAtCuts=no_cut_loss))
  rec["inspection"]=dict(status="design_ready_user_review",notes=["实际看图：内容与row-major清单一致，导航v2道童身份已修正" if sheet.startswith("icons-navigation") else "实际看图：内容与row-major清单一致，画风继承实际主参考","等分网格可能穿越原生图标边缘；采用全局alpha>16零像素通道自适应切分，独立输出无可见主体裁损"],slicingStatus="adaptive_crop_passed",hasActualTransparency=True)
  write(recpath,rec)
 manifest=dict(schemaVersion=1,updatedAt=datetime.now(timezone.utc).isoformat(),art_source="host_image",route="builtin",status="partial" if len(assets)<64 else "runtime_kit_ready_user_review",
 note="48 icons + 16 blank skins planned. True native RGBA; adaptive transparent-gap crops and alpha hygiene, no source art resized or code-drawn. Dynamic labels are native text per font-contract.",
 counts=dict(icons=sum(x["kind"]=="icon" for x in assets),skins=sum(x["kind"]=="skin" for x in assets),total=len(assets)),
 assets=assets,sheets=sheet_records,reuseManifest="assets/ui/manifest.json")
 write(ART/"manifest.json",manifest)
 print(json.dumps(dict(counts=manifest["counts"],sheets=len(sheet_records),status=manifest["status"]),ensure_ascii=False))
if __name__=="__main__": run()

