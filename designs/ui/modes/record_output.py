import json,sys,hashlib,struct,shutil
from pathlib import Path
from datetime import datetime,timezone
root=Path('D:/work/doudizhu-image')
identifier,source,rendered,qa=sys.argv[1:5]
scope=json.loads((root/'docs/UI_SCOPE.json').read_text(encoding='utf-8-sig'))
page=next(p for p in scope['pages'] if p['id']==identifier)
output=root/page['output']; output.parent.mkdir(parents=True,exist_ok=True)
if output.exists():
 if hashlib.sha256(output.read_bytes()).hexdigest()!=hashlib.sha256(Path(source).read_bytes()).hexdigest(): raise SystemExit('Refusing to overwrite '+str(output))
else: shutil.copy2(source,output)
data=output.read_bytes()
if data[:8]!=bytes.fromhex('89504e470d0a1a0a'): raise SystemExit('Not PNG')
w,h=struct.unpack('>II',data[16:24]); sha=hashlib.sha256(data).hexdigest()
config=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig'))
receipt=output.with_suffix('.receipt.json')
refs=[]
for name,role in [('references/style/01-mail-event.png','主风格：配色材质控件'),('references/style/team-ui-v2.png','主风格：布局留白层级'),('designs/characters/characters-trio-v1.png','同源角色身份设定')]:
 refs.append({'file':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest(),'role':role})
record={'file':page['output'],'sha256':sha,'generatedAt':datetime.now(timezone.utc).isoformat(),'width':w,'height':h,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[str(root/r['file']) for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实元数据','evidence':{'receipt':str(receipt.relative_to(root)).replace('\\\\','/'),'returnedSourceFile':source,'toolReturnKeys':['image_url','output_hint'],'imagePayloadOmitted':'原生PNG已保存并计算哈希，避免重复base64'},'prompt':'prompts/modes/'+identifier+'-v1.txt','references':refs,'review':{'status':'design_ready_user_review','notes':qa,'renderedStates':rendered.split('|'),'userApproved':False}}
(root/page['generation']).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
shared=['designs/ui/components/50-shared-dialogs-v1.png','designs/ui/components/51-common-components-v1.png']
state={'id':identifier,'title':page['title'],'primaryArtwork':page['output'],'controls':page['controls'],'states':[],'dynamicText':'昵称、积分、时间、价格、进度及规则由客户端与服务端原生文字提供；图内均为美术示意。','sharedDependencies':shared,'notes':'未另画的状态明确specified_only；公共状态依赖尚待协调者核验，不冒称已经完成。'}
for s in page['requiredStates']:
 state['states'].append({'name':s,'coverage':'rendered' if s in rendered.split('|') else 'specified_only','renderedIn':page['output'] if s in rendered.split('|') else None,'interaction':{'可领':'点击领取，处理中禁用，成功后已领取，失败保留资格','可领取':'点击领取，处理中禁用，成功后已领取，失败保留资格','未拥有':'显示获取入口，使用按钮禁用并说明未拥有','未解锁':'显示解锁条件，使用按钮禁用','锁定':'显示解锁条件且阻止进入','条件不足':'显示缺失条件，报名禁用','未达':'奖励节点禁用，提示所需积分','未开始':'显示开始时间，进入操作禁用','已报名':'允许查看报名信息与取消规则','已拥有':'可预览与使用，禁用重复购买','售罄':'购买禁用并显示售罄','赛季结束':'匹配入口禁用，显示赛季结算与新赛季时间','失败':'显示重试并保留返回关卡入口','全部完成':'下一关替换为返回关卡','无可行出牌':'出牌禁用，显示提示与重来','已领取':'领取禁用，显示已领取','无奖励':'奖励区空态说明，保留返回','淘汰':'终止下一轮等待并给出结果入口','取消':'取消候场并返回赛事大厅'}.get(s,'按该状态更新文案、选中标记、按钮可用性与反馈，保留返回入口。')})
(root/page['stateSpec']).write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
readme=['# 模式、角色与商城 UI 批次','','状态为首版待用户确认；逐页来源、原生尺寸和实际型号证据见对应 generation.json。','','| 页面 | 原生尺寸 | 状态 | 记录 | 状态说明 |','|---|---|---|---|---|']
for p in scope['pages']:
 if p['batch']!='modes':continue
 rec=root/p['generation']
 if rec.exists():
  obj=json.loads(rec.read_text(encoding='utf-8-sig')); readme.append('| ['+p['title']+']('+Path(p['output']).name+') | '+str(obj['width'])+'×'+str(obj['height'])+' | design_ready_user_review | [记录]('+Path(p['generation']).name+') | [状态]('+Path(p['stateSpec']).name+') |')
 else: readme.append('| '+p['title']+' | — | pending | — | — |')
(root/'designs/ui/modes/README.md').write_text(chr(10).join(readme)+chr(10),encoding='utf-8')
print(json.dumps({'id':identifier,'file':str(output),'width':w,'height':h,'sha256':sha},ensure_ascii=False))

