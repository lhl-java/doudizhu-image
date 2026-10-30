from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(__file__).resolve().parents[1]
scope=json.loads((root/'docs/UI_SCOPE.json').read_text(encoding='utf-8-sig'))
# A semantic layout contract: every control remains native and links to an actual art ID.
types={
'01':'login','02':'lobby','03':'grid','04':'grid','05':'matching','06':'grid','07':'form','08':'keypad','09':'room','10':'list',
'11':'table','12':'table','13':'table','14':'table','15':'table','16':'table','17':'table','18':'result','19':'result','20':'result','21':'settings','22':'replay',
'23':'rank','24':'progress','25':'result','26':'grid','27':'detail','28':'matching','29':'result','30':'grid','31':'table','32':'result','33':'characters','34':'character-detail','35':'wardrobe','36':'shop',
'37':'detail','38':'grid','39':'inventory','40':'profile','41':'list','42':'leaderboard','43':'tasks','44':'signin','45':'events','46':'mail','47':'settings','48':'rules','49':'notices','50':'kit','51':'kit','52':'kit','53':'chat','54':'vote','55':'counter','56':'grid','57':'characters','58':'shop','59':'progress','60':'account'}
items={
'03':['经典','不洗牌','癞子','天地癞子'],'04':['新手场','初级场','中级场','高级场'],'06':['创建房间','加入房间','最近房间'],
'07':['玩法：经典','局数：3局','叫地主：叫分','加倍：开启','倍数封顶：64倍'],'26':['青云挑战赛','每日入门赛','周末精英赛'],
'30':['第1关','第2关','第3关','第4关','第5关','第6关','第7关','第8关'],
'35':['青云衣','桃花春衣','暮色墨衣','桂月金衣','雪色白衣','庆典红衣'],
'36':['三人头像框','玉绿牌背','葫芦表情包','记牌器','改名符','桃花桌布'],
'38':['铜钱 ×1000','铜钱 ×5000','铜钱 ×10000','玉牌 ×20'],
'39':['记牌器 ×3','改名符 ×1','玉绿牌背','葫芦表情包'],
'41':['桃花牌友 · 在线','云中客 · 在线','葫芦长者 · 离线'],
'43':['完成1局对局','赢得3场胜利','邀请牌友同玩'],
'44':['周一','周二','周三','周四','周五','周六','周日'],
'48':['基础牌型','叫地主与抢地主','加倍与明牌','不洗牌','癞子与天地癞子','记牌与托管'],
'49':['版本公告','活动说明','常见问题','提交反馈'],
'56':['入门练习','普通练习','进阶练习'],'58':['青云头像框','玉绿牌背','桃花桌布','葫芦表情包'],
'59':['初试身手','青云牌友','每日成长','累计对局','牌技进阶'],
'60':['切换账号','用户协议','隐私说明','检查版本','资源下载']
}
cta={'01':['进入游戏'],'02':['快速开始'],'03':['选择场次'],'04':['开始匹配'],'05':['取消匹配'],'06':['创建房间','加入房间'],'07':['创建房间'],'08':['加入'],'09':['邀请好友','准备'],'10':['邀请'],'11':['不叫','叫地主'],'12':['不抢','抢地主'],'13':['不加倍','加倍','明牌'],'14':['提示','出牌'],'15':['不出','提示','出牌'],'16':['取消托管'],'17':['返回大厅','重连'],'18':['返回大厅','再来一局'],'19':['返回大厅','再来一局'],'20':['返回大厅','继续同玩'],'21':['保存设置'],'22':['暂停','下一手'],'23':['开始排位'],'24':['领取奖励'],'25':['继续排位'],'26':['查看赛事'],'27':['报名'],'28':['取消报名'],'29':['领取奖励'],'30':['开始挑战'],'31':['重来','提示','出牌'],'32':['重玩本关','下一关'],'33':['使用角色'],'34':['试听','使用角色'],'35':['还原','保存装扮'],'36':['查看详情'],'37':['取消','确认'],'38':['确认兑换'],'39':['使用'],'40':['编辑资料'],'41':['添加好友'],'42':['刷新'],'43':['领取奖励'],'44':['今日签到'],'45':['前往活动'],'46':['删除','领取附件'],'47':['保存设置'],'48':['返回'],'49':['提交反馈'],'53':['发送表情'],'54':['拒绝','同意'],'55':['关闭'],'56':['开始练习'],'57':['选择角色'],'58':['兑换'],'59':['领取奖励'],'60':['确认']}
iconwords={'经典':'classic','好友':'friend-room','排位':'rank','赛事':'tournament','残局':'puzzle','练习':'practice','能力':'skills','商城':'shop','角色':'character','装扮':'wardrobe','任务':'task','活动':'events','邮件':'mail','设置':'settings','背包':'inventory','排行':'rank','兑换':'season','回放':'replay','聊天':'chat'}
def icon_for(s):
    extra={'头像':'profile','个人':'profile','昵称':'profile','账号':'profile','货币':'coin','铜钱':'coin','金币':'coin','金豆':'coin','游戏币':'coin','玉牌':'token','点券':'token','代币':'token','协议':'check','勾选':'check','搜索':'search','语音':'voice','音乐':'music','音效':'sound','震动':'vibration','网络':'network','连接':'network','倒计时':'timer','计时':'timer','时间':'timer','底分':'coin','奖励':'gift','签到':'signin','表情':'emoji','礼包':'gift','排名':'rank','段位':'rank','星级':'star','锁定':'lock','关闭':'close','返回':'back','明牌':'classic','底牌':'classic','手牌':'classic','牌面':'classic','出牌':'classic','倍数':'add','胜利':'trophy','成就':'trophy','资料':'profile','帮助':'help','规则':'help'}
    return next((v for k,v in dict(extra,**iconwords).items() if k in s),None)
def canonical(value):
    for before,after in [('游戏币','铜钱'),('金币','铜钱'),('金豆','铜钱'),('点券','玉牌'),('代币','玉牌'),('赛季令','玉牌')]:value=value.replace(before,after)
    return value
screens=[];copy={'locale':'zh-CN','brand':json.loads((root/'config/brand.json').read_text(encoding='utf-8-sig')),'currency':{'soft':{'id':'coin','label':'铜钱'},'premium':{'id':'token','label':'玉牌'}},'common':{'back':'返回','close':'关闭','confirm':'确定','cancel':'取消','retry':'重试','loading':'加载中…','empty':'暂无内容'},'screens':{}}
for p in scope['pages']:
    num=p['id'][:2];kind=types[num];s=json.loads((root/p['stateSpec']).read_text(encoding='utf-8-sig'))
    content=items.get(num,p['controls'])
    st=[]
    for v in s.get('states',[]):
        name=v.get('name',v.get('state'))
        raw=v.get('copy',v.get('actualCopy',name))
        body=canonical('\n'.join(map(str,raw)) if isinstance(raw,list) else str(raw or name))
        behavior=v.get('behavior',v.get('interaction',''))
        if isinstance(behavior,list):behavior='\n'.join(behavior)
        st.append(dict(name=canonical(name),coverage=v.get('coverage'),title=canonical(v.get('title',name)),body=body,behavior=canonical(behavior),buttons=[canonical(x) for x in v.get('buttons',[])],disabledReasons=[canonical(x) for x in v.get('disabledReasons',[])]))
    icon=icon_for(p['title'])
    scene='night' if num in ['45','46'] else 'day' if kind in ['table','replay','chat','counter','vote','room'] else 'lobby'
    scre=dict(id=p['id'],title=p['title'],template=kind,referenceDesign=p['output'],art=dict(scene=scene,table='jade',panel='panel',button='primary-normal',icon=icon,actor='daotong'),logicalCanvas=[1920,810],safeRect=[48,32,1824,746],controls=[dict(id=p['id']+'.control.'+str(i),label=label,icon=icon_for(label),art='primary-normal' if i==len(p['controls'])-1 else 'secondary-normal',hitMin=[48,48],nativeText=True) for i,label in enumerate(p['controls'])],items=[dict(id=p['id']+'.item.'+str(i),label=t,icon=icon_for(t),nativeText=True) for i,t in enumerate(content)],actions=cta.get(num,['返回']),states=st,artSource='generated assets, native layout and text; reference design is not used as a baked runtime screen')
    scre=json.loads(canonical(json.dumps(scre,ensure_ascii=False)))
    screens.append(scre);copy['screens'][p['id']]=dict(title=scre['title'],controls=[x['label'] for x in scre['controls']],items=[x['label'] for x in scre['items']],actions=scre['actions'])
runtime=root/'runtime';runtime.mkdir(exist_ok=True)
(runtime/'screens.json').write_text(json.dumps(dict(schemaVersion=1,scope='60 visual screen bindings',layoutEngine='runtime/art-preview.html',screens=screens),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(runtime/'copy.zh-CN.json').write_text(json.dumps(copy,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Preserve the selected brand/event assets and their per-image QA evidence.
# A layout rebuild does not constitute a new visual review or a new image generation.
for name in ['brand','events']:
    chosen=json.loads((root/f'assets/{name}/manifest.json').read_text(encoding='utf-8-sig'))
    for asset in chosen['assets']:
        if not (root/asset['file']).is_file() or not (root/asset['record']).is_file():raise ValueError('Selected art missing: '+asset['file'])
print('60 native visual screen bindings built; selected brand/event records preserved')

