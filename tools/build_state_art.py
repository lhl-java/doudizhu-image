"""Create explicit art layouts for every existing screen state, without changing historical design records."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json
r=Path(__file__).resolve().parents[1]
s=json.loads((r/'runtime/screens.json').read_text(encoding='utf-8-sig'))
# One entry per state in the adopted state specifications, in their original order.
plans={
'01':['login','login','loading','error'],'02':['inline','badge','loading'],
'03':['selection','locked','rules'],'04':['inline','resource','selection'],
'05':['loading','inline','error'],'06':['inline','empty'],
'07':['selection','inline','error'],'08':['form','error','error','error'],
'09':['seats','seats','seats','seats'],'10':['list','list','empty'],
'11':['table','table','table','table'],'12':['table','table','table','table'],
'13':['table','table','table','table'],'14':['table','table','table','table'],
'15':['table','table','table','table'],'16':['table','table','table'],
'17':['loading','error','inline','seats'],'18':['result','result','result','result'],
'19':['result','result','resource'],'20':['result','result','confirm'],
'21':['settings','confirm','cards'],'22':['empty','table','table','result'],
'23':['inline','reward','locked'],'24':['progress','progress','locked','reward'],
'25':['result','result','result','progress'],'26':['list','locked','list','locked'],
'27':['inline','resource','inline'],'28':['loading','result','result','confirm'],
'29':['reward','reward','empty'],'30':['selection','locked','selection'],
'31':['table','table','table'],'32':['result','result','result'],
'33':['selection','locked','selection'],'34':['selection','selection','locked'],
'35':['locked','selection','costume','costume'],'36':['list','locked','list','selection'],
'37':['resource','resource','confirm','reward'],'38':['resource','resource','confirm','reward'],
'39':['list','empty','locked','inline'],'40':['profile','profile','form','inline'],
'41':['list','list','empty','list'],'42':['list','empty','loading'],
'43':['progress','reward','reward','empty'],'44':['reward','reward','locked','confirm'],
'45':['list','reward','reward','locked'],'46':['mail','reward','mail','locked','empty'],
'47':['settings','settings','inline','confirm'],'48':['rules','rules','rules'],
'49':['rules','form','inline','empty'],'50':['confirm','confirm','error','reward','empty'],
'51':['components','components','components','components','components'],
'52':['cards','cards','cards','cards','cards','cards'],
'53':['chat','chat','voice','voice'],'54':['seats','inline','inline','error'],
'55':['cards','locked','resource','rules'],'56':['inline','table','confirm','result'],
'57':['selection','locked','selection','rules'],'58':['resource','resource','reward','locked'],
'59':['progress','reward','reward','progress'],'60':['confirm','error','loading','error']}
actions={'empty':['返回'],'loading':['取消'],'error':['重试','返回'],'confirm':['取消','确认'],'rules':['关闭'],'locked':['返回'],'reward':['领取'],'resource':['取消','确认'],'seats':['邀请好友','准备'],'form':['取消','保存'],'voice':['关闭'],'inline':['关闭'],'badge':['关闭'],'selection':['使用'],'login':['进入游戏'],'costume':['保存装扮'],'profile':['关闭'],'settings':['保存设置'],'list':['查看'],'cards':['关闭'],'progress':['查看奖励'],'result':['返回大厅','再来一局'],'table':['不出','提示','出牌'],'chat':['发送'],'mail':['领取附件'],'components':['关闭']}
allstates=[]
for p in s['screens']:
    nums=p['id'][:2];kinds=plans[nums]
    if len(kinds)!=len(p['states']):raise ValueError('State count differs '+p['id'])
    for i,(st,kind) in enumerate(zip(p['states'],kinds)):
        name=st['name'];text=st['body'];disabled=list(st['disabledReasons'])
        unavailable=kind=='locked' or name in ['未到','售罄','过期','已领取','已领','已兑','已使用','已邀请','已报名','已签','使用中','未完成','未达','要不起','不合法牌型','未选','条件不足','余额不足','资源不足','不足','用尽','未拥有','未解锁']
        if unavailable and not disabled:disabled=[name]
        cta=st['buttons'] or (p['actions'] if kind in ['inline','selection','costume','table','resource','result','list','progress','login'] else actions[kind])
        # These are art-preview action labels, never a success/payment/gameplay claim.
        cta=[dict(label=t,disabled=unavailable and t not in ['返回','返回大厅','关闭','取消','查看','查看详情','提示','重试','不出','还原']) for t in cta]
        entry=dict(id=p['id']+'.state.'+str(i),screen=p['id'],index=i,name=name,title=st['title'],body=text,layout=kind,scene=p['art']['scene'],icon={'empty':'mail' if nums=='46' else 'inventory','locked':'lock','loading':'refresh','reward':'gift','error':'network','resource':'coin','result':'trophy','seats':'friends','progress':'star','voice':'voice'}.get(kind,'help'),actions=cta,disabledReasons=disabled,interactionSpec=st['behavior'],visualReview='pending_browser_visual_review')
        allstates.append(entry)
doc=dict(schemaVersion=1,updatedAt=datetime.now(timezone.utc).isoformat(),source='runtime/screens.json',sourceSha256=hashlib.sha256((r/'runtime/screens.json').read_bytes()).hexdigest(),scope='223 native art-state layouts with exact source copy and disabled reasons; local visual feedback only',states=allstates,counts=dict(total=len(allstates),layouts=dict(Counter(x['layout'] for x in allstates))),browserVisualReviewPassed=False)
(r/'runtime/state-art.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(doc['counts']))
