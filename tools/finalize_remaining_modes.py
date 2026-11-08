from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(__file__).resolve().parents[1]
scope=json.loads((root/'docs/UI_SCOPE.json').read_text(encoding='utf-8-sig'))
data={
'31-puzzle-play':[
('挑战中','rendered','残局对局','第4关，率先出完手牌。','保留8张AAKK9876、QQ待压制牌面与三席身份；可选牌出牌或重来。',['提示','重来','出牌']),
('提示','shared_component','出牌提示','当前待压制牌为一对Q，可参考一对K或一对A。','仅为此示例局面提示；确认后关闭，恢复原选择；正式最优解由残局逻辑给出。',['返回牌局','知道了']),
('无可行出牌','shared_component','暂无可出的牌','当前选择无法组成可出的牌型。','出牌按钮禁用并说明原因；可清除选择、重来或返回关卡，不擅自跳过服务端校验。',['清除选择','重来'])],
'32-puzzle-result':[
('成功','rendered','挑战成功','第4关，步数6，使用提示0，铜钱100。','展示三星、结算统计及重玩/下一关；奖励按真实回执更新。',['重玩本关','下一关']),
('失败','shared_component','挑战未完成','这次没能率先出完手牌，再试一次吧。','隐藏成功奖励，保留本关重试与关卡列表。',['返回关卡','重试']),
('全部完成','shared_component','全部关卡已完成','当前难度的关卡已全部通关。','下一关入口替换为返回关卡；已获得奖励不可重复发放。',['返回关卡','重玩本关'])],
'33-character-select':[
('已拥有','rendered','已拥有','桃花女修已拥有，可点击使用。','选中后更新底部介绍和试听；使用需保存成功回执。',['使用']),
('未拥有','rendered','未拥有','葫芦长者尚未拥有。','显示获取入口；不得在未获取时直接设置使用中。',['获取']),
('使用中','rendered','使用中','玉绿道童当前使用中。','金玉选框及状态文字同时表示当前角色，避免仅靠颜色。',['使用中'])],
'34-character-detail':[
('使用中','shared_component','角色使用中','桃花女修已设为当前角色。','使用按钮替换为禁用的使用中，角色选择同步更新；返回和试听仍可用。',['返回','使用中']),
('可使用','rendered','桃花女修','清风入扇，笑看牌局。','已拥有、三段试听、四枚表情与使用角色入口清楚。',['返回','使用角色']),
('未解锁','shared_component','角色尚未解锁','解锁后即可使用桃花女修。','显示具体获取条件及获取入口；不改变已保存的当前角色。',['返回','前往获取'])],
'35-wardrobe':[
('未拥有','rendered','未拥有','雪色白衣、庆典红衣尚未拥有。','小锁与文字共同表达；允许查看和试穿预览，不允许直接保存未拥有装扮。',['获取']),
('已拥有','rendered','已拥有','暮色墨衣、桂月金衣已拥有。','可试穿并保存；物品分类与已使用标记分开。',['试穿']),
('试穿','shared_component','试穿预览','当前试穿：桃花春衣。','图内桃花春衣卡绘及试穿入口提供视觉来源；试穿保持未提交态，左侧预览与选中卡同步由角色皮肤层提供，保存前可还原。未把卡面预览宣称为新角色全身资产。',['还原','保存装扮']),
('已使用','rendered','已使用','青云衣当前使用中。','当前左侧青云衣预览、金色选框和已使用标签一致；保存其他装扮成功后转移标记。',['还原','保存装扮'])],
'36-shop':[
('正常','rendered','商城','推荐、角色、装扮、道具；六件商品。','商品进入37详情；数量、价格、币种和余额使用产品配置的原生文字层。',['查看详情']),
('售罄','rendered','售罄','桃花桌布已售罄。','购买动作禁用，保留查看说明；刷新库存后再判断。',['查看说明']),
('限时','rendered','限时','三人主题头像框为限时商品。','期限由服务端提供，结束后撤下限时购买入口。',['查看详情']),
('已拥有','rendered','已拥有','葫芦表情包已拥有。','不可重复购买不可叠加的装扮；前往背包可使用。',['前往背包'])]
}
qa={
'31-puzzle-play':'已实际查看：三席、8张AAKK9876与中央QQ、6/5张余牌、目标及提示/重来/出牌清楚。界面美术不等于完整可解性校验。',
'32-puzzle-result':'已实际看image_gen返回原图：第4关、成功、三星、步数6、提示0、铜钱100、重玩和下一关完整可读；角色脚与按钮均完整。',
'33-character-select':'已实际看image_gen返回原图：三位角色身份与既有设定一致，已拥有/未拥有/使用中分别可见，角色/装扮页签与试听入口清楚。',
'34-character-detail':'已实际看image_gen返回原图：桃花女修完整立绘、已拥有、三段试听、四枚表情与返回/使用角色完整，玉绿米白暖金层级一致。',
'35-wardrobe':'已实际看image_gen返回原图：六格服装、四分类、拥有/未拥有、当前青云衣和还原/保存清楚。桃花春衣试穿入口存在，试穿完整角色皮肤作为动态资产层设计复用，未冒称另交付粉衣全身角色。',
'36-shop':'已实际看image_gen返回原图：六商品、四分类、余额、限时/售罄/已拥有可辨，商品说明与返回大厅完整。币种价格均为美术示意，由统一配置的原生文案提供。'
}
for pid,states in data.items():
    page=next(p for p in scope['pages'] if p['id']==pid)
    file=root/f'designs/ui/modes/{pid}-v1.png'
    genfile=file.with_suffix('.generation.json')
    gen=json.loads(genfile.read_text(encoding='utf-8-sig'))
    gen['status']='design_ready_user_review'
    gen['visualQA']=dict(status='passed_for_design_review',method='actual image_gen image display inspected by root, plus view_image for recovered 31',inspectedAt=datetime.now(timezone.utc).isoformat(),findings=[qa[pid]])
    genfile.write_text(json.dumps(gen,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result=dict(id=pid,title=page['title'],primaryArtwork=page['output'],controls=page['controls'],states=[],dynamicText='昵称、余额、币种、数量、期限、步骤和回执由同一产品配置及原生文字层提供；原画为设计示意。',sharedDependencies=['assets/ui/controls/panel.png','assets/ui/controls/primary-normal.png','assets/ui/controls/primary-disabled.png','assets/ui/controls/secondary-normal.png','assets/ui/controls/tab-selected.png','assets/ui/manifest.json'],status='design_ready_user_review',inspectionNotes=[qa[pid]])
    for name,cov,title,copy,behavior,buttons in states:
        result['states'].append(dict(name=name,coverage=cov,renderedIn=page['output'] if cov=='rendered' else None,title=title,copy=copy,behavior=behavior,buttons=buttons,dependencies=result['sharedDependencies'] if cov=='shared_component' else [],designEvidence='原画可见状态，或实际已生成同源透明控件+明确原生文字与行为；不是额外AI整屏生成'))
    (root/page['stateSpec']).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('31–36 records, visual QA and all required states saved')

