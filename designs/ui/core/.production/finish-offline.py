import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r'D:\work\doudizhu-image')
NOW = datetime.now(timezone.utc).isoformat()
PAGE = '56-offline'
IMAGE = f'designs/ui/core/{PAGE}-v1.png'
GEN = f'designs/ui/core/{PAGE}-v1.generation.json'
STATE = f'designs/ui/core/{PAGE}.states.json'

def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))

def digest(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def source(page, image, record, region):
    r = read(record)
    assert digest(image) == r['sha256'], image
    return dict(pageId=page, output=image, generation=record,
                sha256=r['sha256'], region=region,
                verificationStatus='verified_by_view_image_and_sha256',
                verifiedFiles=True, verifiedAt=NOW,
                note='本轮实际打开图像并核验PNG与generation哈希；仅复用所述现有画面/组件，不宣称离线变体已独立成图。')

def control(name):
    p = f'assets/ui/controls/{name}.png'
    r = read(f'assets/ui/controls/{name}.derivation.json')
    assert digest(p) == r['sha256'], p
    assert digest(r['derivedFrom']['file']) == r['derivedFrom']['sha256']
    return dict(file=p, derivation=f'assets/ui/controls/{name}.derivation.json',
                sha256=r['sha256'], source=r['derivedFrom'],
                verifiedAt=NOW, verificationStatus='verified_by_view_image_and_sha256',
                note='实际查看透明切片及51原图，逐字节哈希与派生记录一致。')

table = source('14-play-turn', 'designs/ui/table/14-play-turn-v2.png',
               'designs/ui/table/14-play-turn-v2.generation.json',
               '完整三人牌桌：中上底牌、两侧电脑座位、下侧本方手牌、中央提示/出牌操作。')
dialogs = source('50-shared-dialogs', 'designs/ui/components/50-shared-dialogs-v1.png',
                 'designs/ui/components/50-shared-dialogs-v1.generation.json',
                 '左上D01双按钮确认弹窗：米白面板、玉绿标题、主次按钮、关闭。')
controls = source('51-common-components', 'designs/ui/components/51-common-components-v1.png',
                  'designs/ui/components/51-common-components-v1.generation.json',
                  '第一行玉绿按钮、第二行米白按钮、第三行标题牌、底部左侧空白面板。')
cards = source('52-card-and-effects', 'designs/ui/components/52-card-and-effects-v1.png',
               'designs/ui/components/52-card-and-effects-v1.generation.json',
               '四花色/大小王/牌背、地主农民身份、选中牌框，与已有牌桌一致。')
skins = [control(n) for n in ['primary-normal', 'secondary-normal', 'panel']]
g = read(GEN)
assert digest(IMAGE) == g['sha256']
s = read(STATE)
s['status'] = 'design_ready_user_review'
s['userApproval'] = False
s['renderedState'] = dict(status='design_ready_user_review', coverage='rendered',
    description='可开始的单机练习选择页；三档难度、无需网络标识、练习说明及无存档禁用态可见。',
    actualRequiredStates=['可开始'], image=IMAGE, generation=GEN)
s['copy'] = dict(status='actual_image_copy_verified_and_shared_dynamic_copy_defined',
                 note='主图实际难度为入门/进阶/挑战；共享态文案是原生动态文字规范，不伪装成已经烘焙在主图内的文字。')

def setup(st, coverage, copy, behavior, disabled, deps, note):
    st.update(coverage=coverage, status='design_ready_user_review',
              image=IMAGE if coverage=='rendered' else None,
              copy=copy, behavior=behavior, disabledReasons=disabled,
              dependencies=deps,
              evidence=dict(inspectedAt=NOW, method='view_image + SHA-256',
                  imageSha256=g['sha256'] if coverage=='rendered' else None,
                  note=note))

for st in s['states']:
    if st['name']=='可开始':
        setup(st,'rendered',
              ['单机练习','返回','无需网络','选择难度','入门','进阶','挑战','练习说明','与两位电脑牌友对局','练习不计入排位战绩','开始练习','继续上局','暂无存档'],
              ['选择一档难度，选中卡显示玉绿底和金勾；点击开始练习进入本地三人对局。', '返回进入大厅；本页无需网络。'],
              ['无本地存档时继续上局为灰色且不响应点击，说明为暂无存档。'], [],
              '实际主图三张难度卡、入门选中、开始按钮和灰色继续上局均清晰；没有牌桌或结果弹窗，故只计可开始实绘。')
        st['actualCopy'] = st['copy']
    elif st['name']=='进行中':
        setup(st,'shared_component',
              ['单机练习','无需网络','难度：{入门/进阶/挑战}','电脑·桃花女修','电脑·葫芦长者','提示','出牌','暂停'],
              ['复用14已绘制的三人牌桌布局与52牌面皮肤，两个对手绑定本地电脑；按真实牌型和回合更新手牌、底牌及身份。',
               '顶端模式栏原生文字改为单机练习及所选难度；保留无需网络标识，联网余额和排位数据不进入本局。',
               '右上设置位置使用51次按钮皮肤和原生文字暂停；点击进入暂停层，手牌与选中牌保留。',
               '提示/出牌沿用14的点击/选牌反馈，未选择合法牌时出牌禁用；电脑操作与计时由本地回合驱动。'],
              ['非本方回合或选择无效牌型时出牌不可用；无可压过牌时保留不出选择，不能虚假提交。'],
              [table,controls,cards],
              '实际查看14-v2和50–52；三人对局画面已绘制。离线差异是上述标题、AI标识及暂停按钮的原生层复用，未生成或合成一张离线进行中PNG。')
        st['sharedDesign'] = dict(isIndependentStateImage=False, compositionPreview=None,
            visualTemplate='designs/ui/table/14-play-turn-v2.png', nativeCanvas=[1931,814],
            nativeTextLayers=[dict(region='顶端模式信息带，x≈710–1220,y≈114–167',text='单机练习｜难度：{难度}｜无需网络'),
                              dict(region='两侧人物姓名牌',text='电脑·桃花女修 / 电脑·葫芦长者'),
                              dict(region='右上原设置入口',text='暂停')],
            skins=skins[:2],
            delivery='复用现有三人牌桌视觉布局与通用皮肤，原生动态文字和行为已定义；不是单独渲染后的离线全屏图。')
    elif st['name']=='暂停':
        setup(st,'shared_component',
              ['练习已暂停','本地对局已暂停，手牌和当前回合将保留。','继续练习','重新开始','退出练习'],
              ['在进行中的牌桌上显示50-D01同款中央米白弹窗，标题为练习已暂停；遮罩拦截牌桌点击。',
               '继续练习为玉绿主按钮；重新开始为米白次按钮；退出练习为弹窗底部原生文字操作。',
               '关闭和继续均恢复原本地手牌/轮次/计时；暂停期间电脑决策和本地计时停住。',
               '重新开始触发D01二次确认：重新开始练习？/本局进度将被重置。/取消/重新开始；确认后同难度重开。',
               '退出触发D01二次确认：退出本次练习？/本局进度将不会保存。/取消/退出；确认回到难度页。'],
              ['暂停遮罩期间手牌、提示、出牌和电脑轮次操作禁用，必须继续或明确退出。'],
              [dialogs,controls],
              'D01面板和主次按钮以及透明皮肤已实际查看并哈希核验；暂停动态文字与操作映射完整，不称为独立已画暂停屏。')
        st['sharedDesign'] = dict(isIndependentStateImage=False, compositionPreview=None,
            visualTemplate='50-D01', modalAnchor='牌桌居中，背景保留并加半透明遮罩',
            nativeTextLayers=dict(title='练习已暂停',body='本地对局已暂停，手牌和当前回合将保留。',
                                  primary='继续练习',secondary='重新开始',footerAction='退出练习'),skins=skins)
    elif st['name']=='结束':
        setup(st,'shared_component',
              ['本局练习结束','{练习胜利 / 再接再厉}','难度：{难度}','本局身份：{地主/农民}','练习不计入排位战绩，不结算金豆。','再练一局','返回'],
              ['结束时冻结已完成牌桌，以50-D01同款双按钮结果面板显示原生结果、所选难度及本局身份。',
               '主按钮再练一局按相同难度创建新本地牌局；次按钮返回与关闭均回单机难度选择页。',
               '本地结果仅写练习记录；不显示联网货币增减、充值入口或伪造排位奖励。'],
              ['结算层显示时手牌、提示、出牌不可操作；重开处理中主按钮暂禁用并显示正在开始。'],
              [dialogs,controls,table],
              '实际查看双按钮结果容器和牌桌；练习结束使用这些已画通用皮肤+动态结果文字，未声称存在56专用结束PNG。')
        st['sharedDesign'] = dict(isIndependentStateImage=False, compositionPreview=None,
            visualTemplate='50-D01', modalAnchor='已完成牌桌居中',
            nativeTextLayers=dict(title='本局练习结束',result='{练习胜利 / 再接再厉}',
                                  details=['难度：{难度}','本局身份：{地主/农民}','练习不计入排位战绩，不结算金豆。'],
                                  primary='再练一局',secondary='返回'),skins=skins)

s['coverageSummary'] = dict(requiredTotal=4,rendered=1,shared_component=3,specified_only=0,
    meaning='设计覆盖完成；shared_component表示已核验的既有美术+具体原生文案和行为，非3张独立离线状态成图，非客户端已接入。')
s['visualQA'] = dict(status='passed_for_design_review',reviewer='root',inspectedAt=NOW,
    method='view_image',image=IMAGE,imageSha256=g['sha256'],userApproval=False,blockingIssues=[],
    findings=[dict(severity='pass',subject='风格与结构',detail='玉绿标题、米白金边卡片、仙山庭院及道童与两张主参考同源，文字无明显错漏。'),
              dict(severity='pass',subject='可开始与禁用',detail='三档入门/进阶/挑战、入门选中和开始练习清晰；继续上局置灰并标暂无存档。'),
              dict(severity='note',subject='状态证据边界',detail='主图仅实绘选择态；进行中复用14牌桌，暂停和结束复用50-D01及51组件，已记录具体原生文案与交互。')])
g['status']='design_ready_user_review'
g['userApproval']=False
g['visualQA']=s['visualQA']
for p,data in [(STATE,s),(GEN,g)]:
    (ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(s['coverageSummary'],ensure_ascii=False))
