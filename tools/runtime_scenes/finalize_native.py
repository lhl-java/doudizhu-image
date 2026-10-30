import json,sys,hashlib,datetime
from pathlib import Path
from PIL import Image
import numpy as np
root=Path("D:/work/doudizhu-image")
plan=json.loads((root/"tools/runtime_scenes/production-plan.json").read_text(encoding="utf-8-sig"))
asset_id,source_path,receipt_path=sys.argv[1:4]
item=next(x for x in plan["items"] if x["id"]==asset_id)
source=Path(source_path);target=root/item["file"];target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():raise RuntimeError(f"target exists: {target}")
target.write_bytes(source.read_bytes())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=json.loads(Path(receipt_path).read_text(encoding="utf-8-sig"))
im=Image.open(target);rgba=im.convert("RGBA");arr=np.array(rgba);alpha=arr[:,:,3]
bbox=rgba.getbbox()
edge=np.concatenate((alpha[0,:],alpha[-1,:],alpha[:,0],alpha[:,-1]))
qa={"mode":im.mode,"width":im.width,"height":im.height,"alphaMin":int(alpha.min()),"alphaMax":int(alpha.max()),"transparentPixelFraction":float((alpha==0).mean()),"softAlphaPixelFraction":float(((alpha>0)&(alpha<255)).mean()),"opaquePixelFraction":float((alpha==255).mean()),"visibleBBox":list(bbox) if bbox else None,"edgeVisiblePixelCount":int((edge>8).sum()),"expectedTransparent":item["transparent"],"isRealRGBAWithTransparency":im.mode=="RGBA" and bool((alpha==0).any())}
qa["status"]="passed" if (not item["transparent"] or qa["isRealRGBAWithTransparency"]) else "needs_fix"
record={"schemaVersion":1,"file":item["file"],"sha256":sha(target),"generatedAt":receipt["finished"]["current_time"],"generatedAtEvidence":"host tool return completion UTC proxy, not model internal timestamp","recordedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"width":im.width,"height":im.height,"format":"PNG","nativeResolution":{"width":im.width,"height":im.height},"exportOperation":"byte-identical-copy-no-resize","tool":"image_gen.imagegen","route":"builtin","art_source":"host_image","kind":item["kind"],"configSnapshot":json.loads((root/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":item["transparent"],"referenced_image_paths":plan["refs"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露／无可核实元数据；配置目标不是实际分支和质量证据","prompt":item["prompt"],"promptSha256":sha(root/item["prompt"]),"references":[{"file":str(Path(p).relative_to(root)).replace("\\","/"),"sha256":sha(p),"role":"actual reference input, first two primary style authority"} for p in plan["refs"]],"evidence":{"receipt":str(Path(receipt_path).relative_to(root)).replace("\\","/"),"hostOutputFile":str(source),"toolReturnedKeys":receipt["keys"]},"alphaQA":qa,"visualReview":{"status":"pending_visual_review","note":""}}
(root/item["record"]).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"id":asset_id,"file":item["file"],"width":im.width,"height":im.height,"alphaQA":qa},ensure_ascii=False))

