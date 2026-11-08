import json,sys,struct,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
root=Path('D:/work/doudizhu-image');batch=root/'designs/ui/modes'
source=Path(sys.argv[1]);output=batch/'27-tournament-detail-v2.png'
if output.exists():raise SystemExit('Refusing overwrite')
shutil.copy2(source,output)
data=output.read_bytes();w,h=struct.unpack('>II',data[16:24]);sha=hashlib.sha256(data).hexdigest()
old=batch/'27-tournament-detail-v1.png'
refs=[]
for name,role in [('designs/ui/modes/27-tournament-detail-v1.png','编辑目标：赛事详情原稿，只改10级到1级'),('references/style/01-mail-event.png','主风格参考'),('references/style/team-ui-v2.png','主风格参考')]:
 refs.append({'file':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest(),'role':role})
record={'file':str(output.relative_to(root)).replace(chr(92),'/'),'sha256':sha,'generatedAt':datetime.now(timezone.utc).isoformat(),'width':w,'height':h,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','operation':'AI-precise-local-edit','configSnapshot':json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[str(root/r['file']) for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实元数据','evidence':{'receipt':'designs/ui/modes/27-tournament-detail-v2.receipt.json','receiptSha256':hashlib.sha256((batch/'27-tournament-detail-v2.receipt.json').read_bytes()).hexdigest(),'returnedSourceFile':str(source),'toolReturnKeys':['image_url','output_hint']},'prompt':'prompts/modes/27-tournament-detail-v2.txt','references':refs,'editTarget':{'file':'designs/ui/modes/27-tournament-detail-v1.png','sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'generation':'designs/ui/modes/27-tournament-detail-v1.generation.json'},'review':{'status':'design_ready_user_review','userApproved':False,'notes':'已实际看26赛事卡与27v1，再查看生成结果。报名条件从等级达到10级改为等级达到1级，与26青云入门赛门槛一致；当前等级28级、20:00、三轮赛、前三奖励与布局视觉保持。','editAcceptance':'target-copy-corrected-and-visual-invariants-preserved','renderedStates':['可报名']}}
(batch/'27-tournament-detail-v2.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
statespath=batch/'27-tournament-detail.states.json';st=json.loads(statespath.read_text(encoding='utf-8'))
st['primaryArtwork']=record['file']
for s in st['states']:
 if s.get('renderedIn')=='designs/ui/modes/27-tournament-detail-v1.png':s['renderedIn']=record['file']
 if s.get('composition'):s['composition']['sourceArtwork']=record['file']
statespath.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
auditpath=batch/'audit-existing.json';audit=json.loads(auditpath.read_text(encoding='utf-8'))
for p in audit['pages']:
 if p['id']=='27-tournament-detail':
  p.update({'file':record['file'],'sha256':sha,'width':w,'height':h,'generation':'designs/ui/modes/27-tournament-detail-v2.generation.json','receipt':'designs/ui/modes/27-tournament-detail-v2.receipt.json','prompt':record['prompt'],'visualReview':record['review'],'copyConsistency':'门槛1级已通过内置image_gen精确编辑统一，与26页一致。'})
for issue in audit['issues']:
 if issue['id']=='27-tournament-detail':
  issue['currentRasterExample']='v2报名门槛已改为1级，与26一致'
  issue['resolutionStatus']='fixed-in-v2'
  issue['resolution']='已通过内置image_gen局部编辑10→1并实际看图，v2为选用稿；原生动态文案仍绑定同一tournamentId。'
audit['recordedAt']=datetime.now(timezone.utc).isoformat()
auditpath.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':record['file'],'width':w,'height':h,'sha256':sha,'adoptedIn':'audit-existing.json'},ensure_ascii=False))

