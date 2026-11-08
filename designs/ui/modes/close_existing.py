import json,hashlib,struct
from pathlib import Path
from datetime import datetime,timezone
root=Path('D:/work/doudizhu-image'); batch=root/'designs/ui/modes'
copy=json.loads((batch/'native-copy-existing.json').read_text(encoding='utf-8'))
scope=json.loads((root/'docs/UI_SCOPE.json').read_text(encoding='utf-8-sig'))
pages={p['id']:p for p in scope['pages'] if p['id'] in copy}
shared=['assets/ui/controls/panel.png','assets/ui/controls/title-primary.png','assets/ui/controls/primary-normal.png','assets/ui/controls/primary-disabled.png','assets/ui/controls/secondary-normal.png','assets/ui/controls/secondary-disabled.png','assets/ui/controls/progress.png','assets/ui/controls/avatar-frame.png','assets/ui/controls/tab-selected.png','assets/ui/controls/tab-normal.png']
for f in shared:
 if not (root/f).is_file():raise SystemExit('Missing shared source '+f)
audit={'schemaVersion':1,'batch':'modes-existing-23-30','recordedAt':datetime.now(timezone.utc).isoformat(),'selectionBoundary':'仅23–30八张选用稿；不含31旧在途或31–36接手稿，不改全量scope与README。','pages':[],'issues':[],'stateMethod':'独立主图的状态标rendered；其他状态用实际存在的公共控件+具体原生标题/正文/按钮和交互说明标shared_component。这些不是新增AI整屏，也不是已渲染客户端截图。'}
for ident,statespec in copy.items():
 p=pages[ident]; stpath=root/p['stateSpec']
 st=json.loads(stpath.read_text(encoding='utf-8'))
 st['sharedDependencies']=shared
 st['notes']='选用主图为独立已生成画面；其他语义状态用下列真实公共素材与原生文字组装。shared_component表示完整组成设计，未冒称另有整屏生成图。接入时使用原画皮肤与动态区域，不把整屏PNG内示例数字作为业务真值。'
 st['dynamicCopySource']='designs/ui/modes/demo-data-contract-existing.json + 同tournamentId/seasonId/playerId的服务端回执'
 for state in st['states']:
  title,body,primary,secondary,behavior=statespec[state['name']]
  state['nativeCopy']=[title,body,primary,secondary]
  state['nativeText']={'title':title,'body':body,'primary':primary,'secondary':secondary}
  state['interaction']=behavior
  is_disabled=state['name'] in ['未达','已达','锁定','条件不足','已领取']
  state['controls']=[{'file':'assets/ui/controls/primary-disabled.png' if is_disabled else 'assets/ui/controls/primary-normal.png','nativeText':primary,'enabled':not is_disabled},{'file':'assets/ui/controls/secondary-normal.png','nativeText':secondary,'enabled':True}]
  if ident=='28-tournament-waiting' and state['name']=='候场':
   state['controls'][0]['role']='status';state['controls'][0]['enabled']=False;state['controls'][0]['nativeText']='保持在线'
  state['assetFilesVerified']=all((root/c['file']).is_file() for c in state['controls'])
  if state['coverage']!='rendered':
   state['coverage']='shared_component';state['renderedIn']=None
   state['composition']={'kind':'opaque-shared-state-panel-over-same-page-skin','sourceArtwork':p['output'],'panel':'assets/ui/controls/panel.png','titlePlate':'assets/ui/controls/title-primary.png','layers':[{'file':'assets/ui/controls/panel.png','role':'米白不透明状态内容层，覆盖原状态文字与不适用的胜利/奖励内容'},{'file':'assets/ui/controls/title-primary.png','role':'标题牌，标题为nativeText.title'},{'nativeText':'nativeText.body','role':'正文与动态数据'},{'file':state['controls'][0]['file'],'role':'主动作或禁用状态，标签为nativeText.primary'},{'file':state['controls'][1]['file'],'role':'返回/次动作，标签为nativeText.secondary'}],'hideFromPrimaryArtwork':['原状态标题和结果文案','原奖励格或旧星级数据（该状态不适用时）','原庆祝人物/胜利字样（失利或淘汰状态）'],'nativeData':'使用同一回执更新数字、段位、排名、开始时间、报名状态、奖励资格；不从整屏示意图读取。','keepSourceAspect':True,'separateRasterVariantGenerated':False}
 st['requiredStatesComplete']=set(p['requiredStates'])=={s['name'] for s in st['states']}
 if not st['requiredStatesComplete']:raise SystemExit('State mismatch '+ident)
 stpath.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
 output=root/p['output'];data=output.read_bytes()
 if data[:8]!=bytes.fromhex('89504e470d0a1a0a'):raise SystemExit('Not PNG '+ident)
 w,h=struct.unpack('>II',data[16:24]);sha=hashlib.sha256(data).hexdigest()
 generation=json.loads((root/p['generation']).read_text(encoding='utf-8-sig'))
 if sha!=generation['sha256'] or [w,h]!=[generation['width'],generation['height']]:raise SystemExit('Generation record mismatch '+ident)
 for ref in generation['references']:
  path=root/ref['file']
  if hashlib.sha256(path.read_bytes()).hexdigest()!=ref['sha256']:raise SystemExit('Reference mismatch '+ident)
 prompt=root/generation['prompt']
 if not prompt.is_file():raise SystemExit('Missing prompt '+ident)
 receipt=(root/p['generation']).with_name(Path(p['generation']).name.replace('.generation.json','.receipt.json'))
 if not receipt.is_file():raise SystemExit('Missing receipt '+ident)
 counts={name:sum(s['coverage']==name for s in st['states']) for name in ['rendered','shared_component','specified_only']}
 audit['pages'].append({'id':ident,'title':p['title'],'file':p['output'],'sha256':sha,'width':w,'height':h,'generation':p['generation'],'receipt':str(receipt.relative_to(root)).replace(chr(92),'/'),'stateSpec':p['stateSpec'],'prompt':generation['prompt'],'status':'design_ready_user_review','userApproved':False,'checks':{'pngSignature':'passed','hashAndNativeDimensions':'passed','referenceHashes':'passed','promptExists':'passed','receiptExists':'passed','requiredStates':'passed','concreteStateCopyAndControls':'passed'},'stateCoverage':counts,'visualReview':generation.get('review',{}),'dynamicCopyStatus':'native_text_binding_required'})
audit['issues']=[
{'id':'27-tournament-detail','severity':'sample_copy_consistency','field':'tournament.minLevel','currentRasterExample':'详情图10级；26同名赛事卡1级','canonicalSource':'designs/ui/modes/demo-data-contract-existing.json:tournaments.qingyun.minLevel = 1','resolution':'列表和详情同时绑定同一赛事ID的minLevel，原生文案显示“等级达到1级即可报名”。本次仅状态与文案合同，不声称重画了PNG。'},
{'id':'29-tournament-result','severity':'sample_copy_consistency','field':'tournament.totalGames','currentRasterExample':'成绩图总局数18；详情为三轮对局','canonicalSource':'tournaments.qingyun.resultDemo.totalGames = 3（美术样例），正式值来自比赛回执','resolution':'赛制轮次、局数与成绩统计由同一赛事配置/回执生成。18仅原图示例，不作为业务承诺。'},
{'id':'25-ranked-result','severity':'sample_copy_boundary','field':'participants[].rankScoreDelta','currentRasterExample':'三人均显示+120','canonicalSource':'每位参赛者自己的rankScoreDelta；本地玩家rank.resultDemo.scoreDelta = 120','resolution':'竞技积分与牌局输赢分分别命名并按参与者结果逐项绑定，不复制当前玩家增量到三人。未声称此图验证了实际计分规则。'},
{'id':'24-ranked-progress','severity':'terminology_boundary','field':'rewards[].displayName','currentRasterExample':'金币、灵石、赛季礼盒、灵气葫芦、头像框','canonicalSource':'项目统一道具表itemId→displayName；铜钱为钱包货币，灵石可为库存道具','resolution':'奖励图标与文字以统一道具配置映射，不继承旧游戏资源名；如铜钱为最终名称，原生标签统一为铜钱。'},
{'id':'28-tournament-waiting','severity':'interaction_boundary','field':'保持在线','currentRasterExample':'绿色状态牌造型接近按钮','canonicalSource':'28状态说明:候场.controls[0].role = status, enabled = false','resolution':'保持在线仅展示连接状态，不响应重复点击；实际退出只有退出候场入口并经确认。'}
]
audit['counts']={'selectedPrimaryPages':len(audit['pages']),'renderedStates':sum(p['stateCoverage']['rendered'] for p in audit['pages']),'sharedComponentStates':sum(p['stateCoverage']['shared_component'] for p in audit['pages']),'specifiedOnlyStates':sum(p['stateCoverage']['specified_only'] for p in audit['pages'])}
audit['status']='selected_art_and_state_composition_ready_user_review'
(batch/'audit-existing.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audit['counts'],ensure_ascii=False))

