import json, hashlib, re, shutil, argparse
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path("D:/work/doudizhu-image")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(sheet):
 d=ROOT/"designs/ui/runtime-kit"
 receipt=json.loads((d/(sheet+".receipt.json")).read_text(encoding="utf-8-sig"))
 m=re.search(r"as (.+?\.png) by default\.", receipt["output_hint"])
 if not m: raise RuntimeError("Native output path not disclosed")
 source=Path(m.group(1))
 target=d/(sheet+".png")
 if target.exists(): raise RuntimeError("Refusing overwrite")
 shutil.copyfile(source,target)
 im=Image.open(target)
 if im.mode!="RGBA": raise RuntimeError("Native image is not RGBA")
 alpha=im.getchannel("A")
 hist=alpha.histogram()
 rec=dict(schemaVersion=1,file=target.relative_to(ROOT).as_posix(),sha256=sha(target),generatedAt=receipt["recordedAt"],
 generatedAtEvidence="UTC recorded immediately after tool return, proxy completion time",width=im.width,height=im.height,format="PNG",art_source="host_image",
 tool="image_gen.imagegen",route="builtin",configSnapshot=json.loads((ROOT/"config/image-generation.json").read_text(encoding="utf-8-sig")),
 submittedParameters={"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":receipt["submittedArguments"]["referenced_image_paths"]},
 actualModel=receipt.get("actualModel"),actualQuality=receipt.get("actualQuality"),
 unverifiedReason="宿主管理，工具未披露／无可核实元数据；配置目标不等于显式锁定分支或max",
 prompt="prompts/runtime-kit/"+sheet+".txt",promptSha256=sha(ROOT/("prompts/runtime-kit/"+sheet+".txt")),
 references=[{"file":str(Path(p).relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"role":"actual attached approved style reference"} for p in receipt["submittedArguments"]["referenced_image_paths"]],
 nativeResolution=[im.width,im.height],exportOperation="byte-identical copy; no resize/redraw",alpha={"mode":im.mode,"extrema":list(alpha.getextrema()),"zeroPixels":hist[0],"partialPixels":sum(hist[1:255]),"opaquePixels":hist[255]},
 evidence={"receipt":str((d/(sheet+".receipt.json")).relative_to(ROOT)).replace("\\","/"),"sourcePath":str(source),"toolReturnKeys":receipt["toolReturnKeys"]},
 inspection={"status":"awaiting_visual_review","notes":[]})
 (d/(sheet+".generation.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"id":sheet,"width":im.width,"height":im.height,"alpha":rec["alpha"]},ensure_ascii=False))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("sheet");a=p.parse_args();run(a.sheet)

