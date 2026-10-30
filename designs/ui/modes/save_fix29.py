import json,sys,struct,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
root=Path('D:/work/doudizhu-image');batch=root/'designs/ui/modes';ident='29-tournament-result'
source=Path(sys.argv[1]);output=batch/(ident+'-v2.png')
if output.exists():raise SystemExit('Refusing overwrite')
shutil.copy2(source,output);data=output.read_bytes();w,h=struct.unpack('>II',data[16:24]);sha=hashlib.sha256(data).hexdigest()
old=batch/(ident+'-v1.png');record=json.loads((batch/(ident+'-v1.generation.json')).read_text(encoding='utf-8'))
refs=[]
for name,role in [('designs/ui/modes/'+ident+'-v1.png','编辑目标：只改总局数18到3'),('references/style/01-mail-event.png','主风格参考'),('references/style/team-ui-v2.png','主风格参考')]:
 refs.append({'file':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest(),'role':role})
record.update({'file':str(output.relative_to(root)).replace(chr(92),'/'),'sha256':sha,'generatedAt':datetime.now(timezone.utc).isoformat(),'width':w,'height':h,'format':'PNG','operation':'AI-precise-local-edit','configSnapshot':json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[str(root/r['file']) for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实元数据','evidence':{'receipt':'designs/ui/modes/'+ident+'-v2.receipt.json','receiptSha256':hashlib.sha256((batch/(ident+'-v2.receipt.json')).read_bytes()).hexdigest(),'returnedSourceFile':str(source),'toolReturnKeys':['image_url','output_hint']},'prompt':'prompts/modes/'+ident+'-v2.txt','references':refs,'editTarget':{'file':'designs/ui/modes/'+ident+'-v1.png','sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'generation':'designs/ui/modes/'+ident+'-v1.generation.json'},'review':{'status':'design_ready_user_review','userApproved':False,'notes':'已实际看图，右上我的成绩总局数18已改为3，与26青云入门赛3局、27三轮对局一致；排名3、三人2350/1920/1680积分、个人1680积分、奖励与布局视觉保持。','editAcceptance':'target-copy-corrected-and-visual-invariants-preserved','renderedStates':['可领取']}})
(batch/(ident+'-v2.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
statespath=batch/(ident+'.states.json');st=json.loads(statespath.read_text(encoding='utf-8'));st['primaryArtwork']=record['file']
for s in st['states']:
 if s.get('renderedIn')=='designs/ui/modes/'+ident+'-v1.png':s['renderedIn']=record['file']
 if s.get('composition'):s['composition']['sourceArtwork']=record['file']
statespath.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
auditpath=batch/'audit-existing.json';audit=json.loads(auditpath.read_text(encoding='utf-8'))
for p in audit['pages']:
 if p['id']==ident:p.update({'file':record['file'],'sha256':sha,'width':w,'height':h,'generation':'designs/ui/modes/'+ident+'-v2.generation.json','receipt':'designs/ui/modes/'+ident+'-v2.receipt.json','prompt':record['prompt'],'visualReview':record['review'],'copyConsistency':'总局数3已通过内置image_gen精确编辑统一，与26/27一致。'})
for issue in audit['issues']:
 if issue['id']==ident:issue.update({'currentRasterExample':'v2总局数已改为3，与26赛事卡3局及27三轮一致','resolutionStatus':'fixed-in-v2','resolution':'已通过内置image_gen局部编辑18→3并实际看图，v2为选用稿；实际游戏仍由同一赛事ID的回执驱动。'})
audit['recordedAt']=datetime.now(timezone.utc).isoformat()
audit['crossPageNumericCheck']={'eventId':'qingyun','26-entryLevel':1,'27-entryLevel':1,'26-games':3,'27-rounds':3,'29-totalGames':3,'27-currentPlayerLevel':28,'28-currentPlayerLevel':28,'29-scoreInRanking':1680,'29-scoreInMyResult':1680,'30-completedLevels':3,'30-currentLevel':4,'status':'same-event-key-values-consistent-after-v2-edits','remainingRequiredFixes':[],'reviewMethod':'每张选用稿生成时已实际看图；26/27修改前后与29修改前后再次实际查看；未变更图按已记录哈希复用原视觉检查。'}
auditpath.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':record['file'],'width':w,'height':h,'sha256':sha,'auditPages':len(audit['pages'])},ensure_ascii=False))

