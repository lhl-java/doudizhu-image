import json,hashlib,struct
from pathlib import Path
from datetime import datetime,timezone
root=Path('D:/work/doudizhu-image')
source=Path('C:/Users/luyua/.codex/generated_images/01a1772b-4166-7350-8473-50c63538bc86/exec-62c16b60-33b6-45b6-81a4-f45fc64766a3.png')
data=source.read_bytes()
w,h=struct.unpack('>II',data[16:24])
promptfile=root/'prompts/modes/31-puzzle-play-v1.txt'
refs=[]
for p,role in [('references/style/01-mail-event.png','主风格：配色材质'),('references/style/team-ui-v2.png','主风格：层级留白'),('designs/characters/characters-trio-v1.png','同源三角色设定')]:
 refs.append({'file':p,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest(),'role':role})
record={
'status':'original_inflight_unselected_source_only',
'file':str(source),'sha256':hashlib.sha256(data).hexdigest(),'width':w,'height':h,'format':'PNG',
'generatedAt':datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),
'generatedAtEvidence':'源PNG的文件修改时间；原调用已在分工切换前提交，等待单元会话未继承，无法取回原始工具结果对象。',
'tool':'image_gen.imagegen','route':'builtin',
'configSnapshot':json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),
'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[str(root/r['file']) for r in refs]},
'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露；原工具结果对象未继承。源文件路径、哈希与实际像素已恢复核对。',
'prompt':str(promptfile.relative_to(root)),'promptSha256':hashlib.sha256(promptfile.read_bytes()).hexdigest(),'actualPromptText':promptfile.read_text(encoding='utf-8'),
'references':refs,
'copyStatus':'未复制至designs/ui/modes/31-puzzle-play-v1.png，未覆盖接手工页面。',
'visualCheck':'已实际view_image。三席与8张手牌AAKK9876、中央QQ、6/5张余牌、目标和提示/重来/出牌清楚；作为在途候选待协调者决定，不能代表31页已采用。',
'captureNote':'仅保存来源文字记录，不包含base64或重复PNG。'}
directory=root/'designs/ui/modes/receipts';directory.mkdir(exist_ok=True)
(directory/'31-original-inflight-generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
receipt={'tool':'image_gen.imagegen','route':'builtin','sourceFile':str(source),'sourceSha256':record['sha256'],'record':'31-original-inflight-generation.json','originalToolReturnAvailable':False,'recovery':'本工原生成目录中30页之后唯一新增PNG；实际像素对应原已提交31页提示词。','actualModel':None,'actualQuality':None,'selection':'unselected; coordinator decides','sourceNotCopied':True}
(directory/'31-original-inflight-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'source':str(source),'width':w,'height':h,'sha256':record['sha256'],'textRecords':str(directory)},ensure_ascii=False))

