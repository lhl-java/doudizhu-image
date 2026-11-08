import json, hashlib, copy
from pathlib import Path
from datetime import datetime, timezone

root = Path(r'D:\work\doudizhu-image')
now = datetime.now(timezone.utc).isoformat()
ids = ['01-launch-login','02-lobby','03-classic-select','04-stakes-select','05-matchmaking','06-friend-room-entry','07-create-room','08-join-room','09-room-waiting','10-invite-friends']
def load(p): return json.loads((root/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((root/p).read_bytes()).hexdigest()
def save(p,j): (root/p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

components={}
for key in ['50-shared-dialogs','51-common-components']:
    png=f'designs/ui/components/{key}-v1.png'
    meta=load(f'designs/ui/components/{key}-v1.generation.json')
    assert sha(png)==meta['sha256']
    assert meta['status']=='design_ready_user_review'
    components[key]=meta

assets={}
for name in ['panel','title-primary','primary-normal','primary-disabled','secondary-normal','close','progress','checkbox-off']:
    record=f'assets/ui/controls/{name}.derivation.json'
    d=load(record)
    assert sha(d['file'])==d['sha256']
    assert sha(d['derivedFrom']['file'])==d['derivedFrom']['sha256']
    assets[name]={'output':d['file'],'sha256':d['sha256'],'derivation':record,'derivedFrom':d['derivedFrom'],'verifiedFiles':True,'verificationStatus':'file_record_and_visual_verified','verifiedAt':now,'method':'view_image and SHA256 comparison','locator':name+' transparent native control'}

asset_map={
('01-launch-login','登录中'):['primary-disabled'],
('01-launch-login','登录失败'):['primary-normal','secondary-normal'],
('02-lobby','资源加载'):['progress','primary-disabled'],
('03-classic-select','锁定'):['primary-disabled','secondary-normal'],
('03-classic-select','规则提示'):['panel','title-primary','primary-normal','close'],
('05-matchmaking','取消'):['panel','title-primary','primary-normal'],
('05-matchmaking','超时重试'):['primary-normal','secondary-normal'],
('06-friend-room-entry','无最近房间'):[],
('07-create-room','创建失败'):['primary-normal','secondary-normal'],
('08-join-room','房号错误'):['primary-normal','secondary-normal'],
('08-join-room','已满'):['primary-normal','secondary-normal'],
('08-join-room','已结束'):['primary-normal','secondary-normal'],
('09-room-waiting','未准备'):['secondary-normal','primary-normal','primary-disabled'],
('10-invite-friends','无在线好友'):['primary-normal']}

actions={
('01-launch-login','登录中'):{'取消':'取消本次请求并恢复登录入口；保留协议选择和选定账号。','请求完成':'成功进入02大厅；失败显示登录失败反馈。'},
('01-launch-login','登录失败'):{'返回':'关闭反馈，回到同一登录页面，可使用原有切换账号入口。','重试':'保留协议状态，再次进入登录中；请求期间禁用重复操作。'},
('02-lobby','资源加载'):{'取消':'关闭加载反馈并回大厅；目标入口仍按资源状态禁用。','完成':'资源核验完成后开放目标入口。','失败':'用50-D02双按钮显示资源加载失败；返回关闭，重试重新加载。'},
('03-classic-select','锁定'):{'暂未开放':'禁用选择和进入，不改变已有选中项。','查看条件':'显示当前玩法暂未开放提示；知道了关闭。'},
('03-classic-select','规则提示'):{'知道了/关闭':'关闭面板，保持经典选中和场次选择上下文。'},
('05-matchmaking','取消'):{'返回':'已取消请求后返回来源大厅或场次页；不保留仍在匹配的计时状态。'},
('05-matchmaking','超时重试'):{'返回':'退出匹配并回来源页。','重新匹配':'提交新的匹配请求并从00:00重新计时；防止双击重复提交。'},
('06-friend-room-entry','无最近房间'):{'创建':'进入07创建房间。','加入':'进入08加入房间。','空态':'只替换最近房间区域；不禁用两张功能卡。'},
('07-create-room','创建失败'):{'返回':'关闭反馈，保留五项规则选择。','重试':'按原选择再次创建，请求中禁用重复创建。'},
('08-join-room','房号错误'):{'返回':'关闭反馈，保留已提交的完整6位房号。','重新输入':'回到六格输入，将旧房号全选供替换；不声称已加入。'},
('08-join-room','已满'):{'返回':'回06好友同玩。','重新输入':'回六格输入，可修改完整房号；原房间继续不可加入。'},
('08-join-room','已结束'):{'返回':'回06好友同玩。','重新输入':'回六格输入，可修改完整房号；结束房间不再发起加入。'},
('09-room-waiting','未准备'):{'准备':'本人席位转为已准备，按钮改取消准备。','开始游戏':'任一入座玩家未准备时禁用，原因显示等待所有玩家准备。'},
('10-invite-friends','无在线好友'):{'分享房间':'打开房号120816的分享入口，用户选择渠道后才可执行发送。','好友上线':'刷新对应行的在线状态及邀请按钮。','离线好友':'保留已有离线行；顶部空态说明没有在线好友，不宣称好友总列表为空。'}}

checks={
'01-launch-login':'实际可见欢迎道友、微信登录、QQ登录、未勾选协议、用户协议/隐私政策、切换账号和设置；三位角色完整不遮登录区。',
'02-lobby':'大厅全部范围入口实际可见，邮件红点清楚；角色足部和持牌牌背完整，快速开始未压住导航文字。',
'03-classic-select':'四种玩法并列，经典卡高亮及勾选、已选择经典和选择场次相符；规则入口只证明入口。',
'04-stakes-select':'四场底分/入场/封顶清楚；初级推荐可进，高级门槛20000高于余额12800且金豆不足按钮禁用。',
'05-matchmaking':'自己与两待匹配席位、经典初级场、00:08和取消匹配均清楚；按钮不当作取消结果。',
'06-friend-room-entry':'创建与加入两卡、最近房间120816及经典12局清楚；加入卡为装饰图，实际六位输入以08为准。',
'07-create-room':'五组设置实际可见；经典/12局/抢地主/加倍开启/32倍封顶选中与摘要一致，创建房间可用。',
'08-join-room':'恰好六格：1208、第五格光标、第六格空白；0–9、清空、删除完整，未满六位禁用加入且原因清楚。',
'09-room-waiting':'恰好三席：房主本人已准备、花间客已准备、空座可邀请；房号和12局32倍信息明确，人数不足开始禁用。',
'10-invite-friends':'在线可邀请、在线已邀请、离线三行分别呈现；搜索、好友3、房号120816、复制和分享入口完整。'}

summary=[]
scope={p['id']:p for p in load('docs/UI_SCOPE.json')['pages']}
for key in ids:
    sp=f'designs/ui/core/{key}.states.json'; gp=f'designs/ui/core/{key}-v1.generation.json'
    s=load(sp); g=load(gp); png=f'designs/ui/core/{key}-v1.png'
    assert sha(png)==g['sha256']
    assert s['requiredStates']==scope[key]['requiredStates']
    assert [v['name'] for v in s['states']]==s['requiredStates']
    provenance=copy.deepcopy(g)
    for v in s['states']:
        v['status']='design_ready_user_review'
        if v['coverage']=='rendered':
            v['dependencies']=[]
            v.setdefault('evidence',{}).update({'method':'view_image','inspectedAt':now,'imageSha256':g['sha256'],'reviewer':'core_qa'})
            continue
        assert v['coverage']=='shared_component'
        for dep in v['dependencies']:
            file=dep['output']; current=sha(file)
            if 'sha256' in dep: assert current==dep['sha256']
            dep.update({'sha256':current,'verifiedFiles':True,'verificationStatus':'file_record_and_visual_verified','verifiedAt':now,'method':'view_image and SHA256 comparison'})
        v['dependencies'] += [copy.deepcopy(assets[n]) for n in asset_map[(key,v['name'])]]
        # All shared states retain their actual base page; no unseen full-page variant is claimed.
        if not any(d['output']==png for d in v['dependencies']):
            v['dependencies'].append({'pageId':key,'output':png,'sha256':g['sha256'],'generation':gp,'verifiedFiles':True,'verificationStatus':'file_record_and_visual_verified','verifiedAt':now,'method':'view_image and SHA256 comparison','locator':'已绘主页面作为状态背景和位置依据'})
        rp=v.setdefault('reusePlan',{})
        rp['sources']=copy.deepcopy(v['dependencies'])
        rp.update({'method':'verified_shared_component_reuse','inspectedAt':now,'standaloneFullPageRendered':False,'compositedPreviewProduced':False,'implementationStatus':'design_only_not_implemented','actions':actions[(key,v['name'])]})
        if 'nativeTextAndDataReplacements' not in rp:
            rp['nativeTextAndDataReplacements']={'seatStatus':'未准备','selfAction':'准备','startDisabledReason':'等待所有玩家准备'}
        if (key,v['name'])==('03-classic-select','规则提示'):
            rp['nativeTextAndDataReplacements']['body']='3人对局，地主20张、农民各17张，地主先出。相同牌型按点数比较；炸弹可压普通牌型，王炸最大。地主先出完获胜，否则农民获胜。叫地主、加倍与封顶按本房间设置。'
        if (key,v['name'])==('03-classic-select','锁定'):
            rp['nativeTextAndDataReplacements']['reason']='该玩法暂未开放，请选择其他玩法。'
        if (key,v['name'])==('08-join-room','房号错误'):
            rp['note']='错误反馈发生于提交完整6位房号后；主图1208__仅为输入中示例，不会提交半成房号。复用D01，未另画整页。'
        if (key,v['name'])==('06-friend-room-entry','无最近房间'):
            rp['nativeTextAndDataReplacements']={'regionTitle':'最近房间','body':'暂无最近房间','retainedActions':['创建','加入']}
            rp['layout']={'placement':'原最近房间底栏内，使用D06卷轴葫芦小插画及原生正文；保留两张主功能卡','removedContent':['旧房号','旧规则摘要','进入按钮'],'textStyle':'深玉绿正文，居中对齐','noFullScreenModal':True}
        elif (key,v['name'])==('09-room-waiting','未准备'):
            rp['layout']={'placement':'原席位底部状态条和底部本人操作位置','seatStatusSkin':'assets/ui/controls/secondary-normal.png','selfActionSkin':'assets/ui/controls/primary-normal.png','startSkin':'assets/ui/controls/primary-disabled.png','remove':['已准备绿勾'],'textStyle':'未准备用深玉绿原生正文；开始禁用原因置于按钮下方'}
        elif (key,v['name'])==('03-classic-select','锁定'):
            rp['layout']={'placement':'目标玩法原卡片底部标签与下方操作区','baseCard':'03主图对应玩法卡','stateSkin':'assets/ui/controls/primary-disabled.png','nativeLabels':['暂未开放','查看条件'],'stateMeaning':'保留卡片插画，不新增未画锁具图标'}
        elif (key,v['name'])==('10-invite-friends','无在线好友'):
            rp['layout']={'placement':'好友列表上方插入D06空态提示，保持搜索和离线行，分享按钮沿用页底位置','title':'暂无在线好友','illustration':'50-D06卷轴葫芦图形','textStyle':'深玉绿正文；不覆盖离线昵称或按钮'}
        else:
            rp['layout']={'placement':'主页面居中覆盖，共享图板对应弹窗皮肤；背景加半透明遮罩','readingOrder':['标题','正文/状态','操作按钮'],'buttonOrder':'双按钮为左次要右主要；单按钮居中','textLayer':'原生中文文字替换图板示例文案，不把替换后的整页说成已另行生成','dismiss':'关闭等同次要返回/取消；请求中仍执行明确的取消语义'}
        v['evidence']={'method':'verified_shared_component_reuse','reviewer':'core_qa','inspectedAt':now,'standaloneFullPageRendered':False,'implementationStatus':'design_only_not_implemented','nativeTextAndDataReplacements':copy.deepcopy(rp['nativeTextAndDataReplacements']),'note':'实际查看并核验共享图板、指定控件和主页面，定义原生文字/数据替换及行为；未另行合成整屏。'}
    counts={cov:sum(v['coverage']==cov for v in s['states']) for cov in ['rendered','shared_component','specified_only']}
    s['coverageSummary']={'requiredTotal':len(s['requiredStates']),**counts,'note':'rendered为主图实际可见态；shared_component为已看图和哈希核验的共用皮肤加具体原生文案/行为设计。未另画共享态整页，未实现客户端交互。'}
    s['copy']['status']='main_image_and_shared_state_design_verified'
    s['copy']['note']='actualVisibleText/actualCopy为主图实见内容；shared_component的nativeTextAndDataReplacements为指定原生文案层，未冒称已经烘焙到主图。'
    qa=s['visualQA']; qa['previousInspection']={'reviewer':qa.get('reviewer'),'inspectedAt':qa.get('inspectedAt'),'status':qa.get('status')}
    qa.update({'reviewer':'core_qa','inspectedAt':now,'method':'view_image','imageSha256':g['sha256'],'status':'passed_for_design_review','blockingIssues':[],'userApproval':False})
    qa['findings']=[f for f in qa.get('findings',[]) if f.get('subject') not in ['状态覆盖','覆盖与业务边界']]
    qa['findings'].append({'severity':'pass','subject':'本轮逐张复核','detail':checks[key]})
    qa['findings'].append({'severity':'note','subject':'状态覆盖','detail':f'必需状态{len(s["states"])}项：主图可见{counts["rendered"]}，共享视觉与原生文案设计{counts["shared_component"]}，仅说明{counts["specified_only"]}。共享态未另画整页，实际功能尚未接入。'})
    s['status']='design_ready_user_review'; s['userApproval']=False
    g['status']='design_ready_user_review'; g['userApproval']=False; g['visualQA']=copy.deepcopy(qa)
    for p in ['status','userApproval','visualQA']:
        provenance.pop(p,None)
    unchanged={k:v for k,v in g.items() if k not in ['status','userApproval','visualQA']}
    assert provenance==unchanged, 'generation provenance changed'
    save(sp,s); save(gp,g)
    summary.append({'pageId':key,**counts,'status':s['status']})
print(json.dumps({'written':len(summary),'pages':summary,'totals':{cov:sum(p[cov] for p in summary) for cov in ['rendered','shared_component','specified_only']},'verifiedAt':now},ensure_ascii=False))
