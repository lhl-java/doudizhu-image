import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path("D:/work/doudizhu-image")
OUT=ROOT/"assets/ui/runtime-kit"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=read(OUT/"manifest.json");existing=read(ROOT/"assets/ui/manifest.json")
controls=[x for x in existing["assets"] if x["file"].startswith("assets/ui/controls/")]
assets=manifest["assets"]+[{**x,"id":Path(x["file"]).stem,"kind":"existing_control","record":x["file"].replace(".png",".derivation.json")} for x in controls]
metrics=[]
fixed_ids={"window-normal","window-wide","dialog","tooltip","portrait-normal","portrait-selected","rarity-common","rarity-rare","rarity-legendary","red-dot","item-locked","avatar-frame","close","title-primary","title-secondary","checkbox-on","checkbox-off","toggle-on","toggle-off","slider","progress","scrollbar"}
for a in assets:
 name=a["id"];w=a["width"];h=a["height"];kind=a["kind"]
 fixed=(kind=="icon" or name in fixed_ids)
 nine=None
 if not fixed:
  x=max(8,min(round(w*.18),round(w*.29) if "primary" in name or "secondary" in name else 64))
  y=max(8,min(round(h*.22),64))
  nine={"left":x,"top":y,"right":x,"bottom":y,"units":"source_texels","centerRegion":[x,y,w-x,h-y]}
 padding=[24,18,24,18] if kind!="icon" else [0,0,0,0]
 target=[80,80] if kind=="icon" else [w,h]
 minimum=[64,64] if kind=="icon" else [max(48,round(w*.65)),max(48,round(h*.65))]
 if nine:minimum=[2*nine["left"]+24,2*nine["top"]+24]
 if name=="red-dot":target=[20,20];minimum=[12,12];padding=[0]*4
 if name.startswith("rarity"):target=[48,48];minimum=[32,32];padding=[0]*4
 if name.startswith("portrait") or name=="avatar-frame":target=[144,144];minimum=[72,72];padding=[round(w*.16),round(h*.16),round(w*.16),round(h*.16)]
 metrics.append({"id":name,"key":kind+"/"+name,"kind":kind,"file":a["file"],"nativeSize":[w,h],"resizeMode":"uniform_contain" if fixed else "nine_slice","nineSliceInsets":nine,"padding":{"left":padding[0],"top":padding[1],"right":padding[2],"bottom":padding[3],"units":"reference_canvas_logical_px"},"minimumLogicalSize":minimum,"recommendedLogicalSize":target,
 "hitbox":{"mode":"rect","minimumLogicalSize":[88,88] if kind=="icon" else [max(88,minimum[0]),max(56,minimum[1])],"alphaHitTest":False,"note":"pointer/touch hitbox is logical UI geometry; do not shrink to decorative alpha outline"},
 "constraints":"Keep aspect; no nine-slice for symbols/medallions/avatars/tassels/tooltips. For arbitrary aspect body panels use existing controls/panel.png and separate title/ornaments." if fixed else "Preserve corner texels with nine-slice; native text separate; do not stretch entire bitmap.",
 "qualityLimit":"Native source dimensions recorded; scaling in engine is rendering only, never a claim of new detail."})
write(OUT/"control-metrics.json",{"schemaVersion":1,"referenceCanvas":[2560,1080],"units":{"source":"texture texels","layout":"logical pixels at reference canvas; global viewport scale applied once"},"status":"runtime_art_contract_user_review","nineSlicePolicy":"Insets are conservative proposed source-space contract for engine validation, not claimed measured runtime success; inspect at minimum and wide sizes.","assets":metrics})
font={"schemaVersion":1,"downloadedFonts":[],"bundledFonts":[],"encoding":"UTF-8","writingDirection":"ltr","language":"zh-CN","stacks":{"body":["Microsoft YaHei","PingFang SC","Noto Sans CJK SC","sans-serif"],"heading":["KaiTi","STKaiti","Noto Serif CJK SC","serif"],"numeric":["Microsoft YaHei","Noto Sans","sans-serif"]},"styleTokens":{
 "screenTitle":{"stack":"heading","size":56,"lineHeight":1.15,"weight":700,"color":"#FFF6DB"},
 "panelTitle":{"stack":"heading","size":36,"lineHeight":1.2,"weight":700,"color":"#173F32"},
 "body":{"stack":"body","size":28,"lineHeight":1.45,"weight":400,"color":"#173F32"},
 "secondary":{"stack":"body","size":24,"lineHeight":1.35,"weight":400,"color":"#675B43"},
 "button":{"stack":"body","size":30,"lineHeight":1.2,"weight":600,"color":"#FFF6DB"},
 "buttonSecondary":{"stack":"body","size":30,"lineHeight":1.2,"weight":600,"color":"#173F32"},
 "numeric":{"stack":"numeric","size":30,"lineHeight":1.2,"weight":600,"color":"#173F32"},
 "warning":{"stack":"body","size":24,"lineHeight":1.35,"weight":500,"color":"#A9442C"}},
 "units":"logical pixels on 2560x1080 canvas","textSeparation":"UI labels, dynamic numbers, prices, names, dates and errors are native text. Icon and skin PNGs contain no textual labels.",
 "fallbackPolicy":"Resolve first installed CJK font in stack; if unavailable, show missing font diagnostic and use OS CJK fallback. Do not download fonts silently.",
 "layoutRules":{"wrap":"body paragraphs may wrap by grapheme; buttons single line; tooltip wraps","overflow":"measure actual selected font; ellipsis with full-text tooltip for list names; never crop price/score/status","minimumBodyLogicalPx":24,"buttonAutoFit":"never reduce below24; expand button or shorten product-approved text","numeralPolicy":"tabular figures where available; keep separators and signs explicit","localization":"remeasure text bounds after locale change","license":"No third-party font files shipped; confirm font licensing if bundling later"},
 "validationRequired":["Installed font resolution per target OS","CJK/Latin/numeral glyph coverage","No overflow at 2560x1080 and minimum supported viewport","Contrast of ivory on jade and jade on ivory"]}
write(OUT/"font-contract.json",font)
index={(a["kind"],a["id"]):a for a in manifest["assets"]}
pages=read(ROOT/"docs/UI_SCOPE.json")["pages"];pageicons=read(ROOT/"tools/runtime_kit/page-icons.json")
def asset(name,fallback=None):
 for kind in ["skin","icon"]:
  if (kind,name) in index:return index[kind,name]["file"]
 return fallback
mapping=[]
for page in pages:
 pid=page["id"];batch=page["batch"];table=batch=="table" or pid in ["31-puzzle-play","56-offline"]
 frame=asset("window-wide" if table else "window-normal","assets/ui/controls/panel.png")
 icons=[{"id":i,"file":asset(i),"record":index["icon",i]["record"]} for i in pageicons[pid]]
 roles=["dao-child","peach-cultivator","gourd-elder"] if pid in ["02-lobby","09-room-waiting","11-deal-bid","12-rob-landlord","13-double","14-play-turn","15-follow-pass","16-trustee","17-reconnect","18-round-win","19-round-loss","20-room-summary","33-character-select","34-character-detail","35-wardrobe","40-player-profile","41-friends"] else []
 mapping.append({"pageId":pid,"title":page["title"],"designReference":page.get("output"),"stateSpec":page.get("stateSpec"),"artBindings":{"frame":frame,"dialog":asset("dialog","assets/ui/controls/panel.png"),"title":"assets/ui/controls/title-primary.png","closeIcon":asset("close"),"primaryButton":"assets/ui/controls/primary-normal.png","primaryDisabled":"assets/ui/controls/primary-disabled.png","secondaryButton":"assets/ui/controls/secondary-normal.png","tabSelected":"assets/ui/controls/tab-selected.png","tabNormal":"assets/ui/controls/tab-normal.png","input":"assets/ui/controls/input-normal.png","icons":icons,"listRow":asset("list-row-normal","assets/ui/controls/panel.png"),"listRowSelected":asset("list-row-selected","assets/ui/controls/panel.png"),"itemSlot":asset("item-normal","assets/ui/controls/panel.png"),"avatarFrame":asset("portrait-normal","assets/ui/controls/avatar-frame.png")},
 "externalArt":{"background":{"logicalId":"background.table-garden" if table else "background.ui-garden","status":"awaiting_coordinator_binding"},"characters":[{"logicalId":"character."+r+".idle","status":"awaiting_coordinator_binding"} for r in roles],"deckManifest":"assets/ui/manifest.json" if table or pid in ["03-classic-select","48-help-rules","52-card-and-effects"] else None},
 "fontContract":"assets/ui/runtime-kit/font-contract.json","metricsContract":"assets/ui/runtime-kit/control-metrics.json","scope":"runtime artwork bindings; layout/runtime behavior separately validated; background/actor logical IDs intentionally pending root coordination"})
write(OUT/"mapping.json",{"schemaVersion":1,"pageCount":len(mapping),"referenceCanvas":[2560,1080],"status":"ui_art_bound_external_art_pending","pages":mapping})
print(json.dumps({"metrics":len(metrics),"mappedPages":len(mapping),"icons":manifest["counts"]["icons"],"skins":manifest["counts"]["skins"]}))

