import json
from pathlib import Path
root=Path('D:/work/doudizhu-image')
rules=json.loads((root/'prompts/modes/state_rules.json').read_text(encoding='utf-8'))
assets=[str(p.relative_to(root)).replace(chr(92),'/') for p in (root/'assets/ui/controls').glob('*.png')]
for path in (root/'designs/ui/modes').glob('*.states.json'):
 obj=json.loads(path.read_text(encoding='utf-8')); per=rules[obj['id']]
 obj['sharedDependencies']=['assets/ui/controls/panel.png','assets/ui/controls/title-primary.png','assets/ui/controls/primary-normal.png','assets/ui/controls/primary-disabled.png','assets/ui/controls/secondary-normal.png','assets/ui/controls/secondary-disabled.png','assets/ui/controls/tab-selected.png','assets/ui/controls/tab-normal.png']
 obj['notes']='主状态由独立成图体现；可复用控件的变体列出具体素材与原生文案。涉及独立胜负/赛季结束/晋级等主场景变化而未另画者保留specified_only，不冒充已生成。'
 for state in obj['states']:
  detail,label=per[state['name']];state['interaction']=detail;state['nativeCopy']=[label]
  state['controls']=[{'file':'assets/ui/controls/primary-disabled.png' if any(k in state['name'] for k in ['未达','未解锁','售罄','已领取','已使用','使用中','锁定','条件不足']) else 'assets/ui/controls/primary-normal.png','nativeText':label},{'file':'assets/ui/controls/secondary-normal.png','nativeText':'返回'}]
  if state['coverage']!='rendered' and state['name'] not in ['掉星','赛季结束','晋级','淘汰','取消','失败','全部完成','无奖励']:
   state['coverage']='shared_component';state['composition']='使用本页同源面板与列明控件；动态标题、数据、状态标记和按钮标签为原生文字；隐藏本页不适用的主状态内容。'
  state['assetFilesVerified']=all((root/c['file']).is_file() for c in state['controls'])
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
print('Updated concrete state copy and shared controls for modes pages.')

