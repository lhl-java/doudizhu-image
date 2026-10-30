from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json
from PIL import Image
root=Path(__file__).resolve().parents[1]
report=json.loads((root/'docs/UI_DELIVERY_REPORT.json').read_text(encoding='utf-8-sig'))
validation=json.loads((root/'docs/FINAL_VALIDATION.json').read_text(encoding='utf-8-sig'))
assert validation['allPagesSelectedAndVerified'], 'Complete validation before final publication'
counts=validation['requiredStateCoverage'];rows=report['pages']
def relative_link(base,path):
    import os
    return os.path.relpath(root/path,base).replace('\\','/')
for batch in ['modes','components']:
    folder=root/'designs/ui'/batch
    pages=[p for p in rows if p['batch']==batch]
    cov=Counter(s.get('coverage') for p in pages for s in p.get('stateDetails',[]))
    lines=[f'# {dict(modes="模式、角色与商城",components="通用弹窗、控件与牌面")[batch]} UI 交付','',f'当前选用 {len(pages)}/{len(pages)} 项，全部已看图检查并标记 design_ready_user_review。状态 R/S：{cov.get("rendered",0)}/{cov.get("shared_component",0)}；没有指定范围中的 specified_only 遗留。','', '| 页面 | 当前图 | 实际尺寸 | 来源记录 | 状态规范 |','|---|---|---|---|---|']
    for p in pages:
        lines.append(f'| {p["id"]} {p["title"]} | [PNG]({relative_link(folder,p["output"])}) | {p["width"]}×{p["height"]} | [记录]({relative_link(folder,p["generation"])}) | [状态]({relative_link(folder,p["stateSpec"])}) |')
    lines+=['','模型目标读取项目配置，实际工具未披露的型号和质量仍为null。原生生成、AI编辑、裁切、原生文字与组件组合均按各自记录区分。','', '全部数值为美术示意；界面动态文案由最终配置与回执提供。待用户确认不等于已接入客户端。','']
    (folder/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    (folder/'manifest.json').write_text(json.dumps(dict(batch=batch,updatedAt=datetime.now(timezone.utc).isoformat(),total=len(pages),ready=len(pages),pages=[{k:p[k] for k in ['id','title','output','generation','stateSpec','width','height','status']} for p in pages]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 斗地主全套 UI 交付','', '按腾讯《欢乐斗地主》的斗地主相关功能梳理，延续相邻 image 项目已确认的道家 Q 版高清手绘风格。当前 60 项美术与状态设计已完成并逐项核验，均为待用户确认设计稿。','',
'## 查看整套结果','', '- [全量图形预览](preview/index.html)：筛选、搜索、逐页原图、生成证据、状态规范。', '- [公共状态演示](preview/states.html)：已有透明皮肤加原生文字，提供本地按钮反馈。', '- 本机在线预览：http://127.0.0.1:8771/preview/index.html 。服务停止后运行 tools/start_preview.ps1；直接打开 preview/index.html 也可查看本地静态目录。','',
'## 交付范围','',f'- 57 页独立界面，覆盖登录大厅、经典与好友房、对局与结算、排位赛事、残局、角色装扮、商城背包、日常社交与设置帮助。', '- 3 套公共图板：通用弹窗、24 个透明控件、牌面/身份/静态特效。', '- 94 个通用 PNG 素材：24 控件、16 牌面与身份特效源、54 张准确点数花色的牌。', f'- {sum(counts.values())} 个必要状态：{counts.get("rendered",0)} 个主图可见，{counts.get("shared_component",0)} 个以同源控件和具体原生文案/行为覆盖；0 个仅留说明。', '- 三位角色的原有概念设定与全套 UI 内的角色表现保持同源。','',
'## 文件目录','', '| 内容 | 入口 |','|---|---|', '| 全量当前选用清单 | [UI_SCOPE.json](docs/UI_SCOPE.json) |', '| 最终核验（无错误） | [FINAL_VALIDATION.json](docs/FINAL_VALIDATION.json) |', '| 全量成图与状态索引 | [UI_DELIVERY_REPORT.json](docs/UI_DELIVERY_REPORT.json) |', '| 大厅、房间、单机、能力、兑换 | [core](designs/ui/core/README.md) |', '| 牌局、结算、聊天、记牌器 | [table](designs/ui/table/README.md) |', '| 排位、赛事、残局、角色、商城 | [modes](designs/ui/modes/README.md) |', '| 背包、资料、好友、任务、活动、系统 | [support](designs/ui/support/README.md) |', '| 公共控件与牌面 | [components](designs/ui/components/README.md) |', '| 94 素材及其来源链 | [assets/ui/manifest.json](assets/ui/manifest.json) |', '| 54 张牌预览 | [deck-review.jpg](assets/ui/deck-review.jpg) |', '| 三位角色概念与生成记录 | [角色图](designs/characters/characters-trio-v1.png) / [记录](designs/characters/characters-trio-v1.generation.json) |','',
'## 尺寸与证据','', '整屏原生图通常约 1930–1932×814–815；公共透明图板为1448×1086，弹窗图板为1672×941。提示词尺寸目标与工具实际返回尺寸分别记录，未以放大冒充原生细节。', '按 GPT Image 2.5 最高质量目标配置，内置入口未提供型号/质量选择器或返回字段，实际值仍如实记为未确认。每张生成/编辑及当前组合图均有来源记录。', '54 张牌是同一生成空白牌框加原生点数/花色文字排版及两张生成大小王；不是54次独立AI生成。牌局修订组合保留实际来源链。', '公共特效为静态素材。该交付为完整 UI 视觉、通用素材与状态规范，客户端、服务器、支付或社交发送尚未接入。','',
'## 参考与后续资料','', '首要风格图见 [references/style](references/style/manifest.json)，新需求图片放 references/uploads/，也可在制作聊天中附图。', '功能核验与设计推导边界见 [REFERENCE_RESEARCH.md](docs/REFERENCE_RESEARCH.md)。制作规则见 [AGENTS.md](AGENTS.md) 和 [ART_DIRECTION.md](docs/ART_DIRECTION.md)。', '本项目远端尚未指定，当前交付位于本地 D:/work/doudizhu-image；不继承 image 的远端仓库或推送职责。','']
(root/'README.md').write_text('\n'.join(lines),encoding='utf-8')
deckroot=root/'assets/ui'
manifest=json.loads((deckroot/'manifest.json').read_text(encoding='utf-8-sig'))
preview=deckroot/'deck-review.jpg'
with Image.open(preview) as im:w,h=im.size
capture=dict(file='assets/ui/deck-review.jpg',sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),width=w,height=h,operation='review-contact-sheet-from54-card-assets-downscaled-for-review-only-not-AI-generation',derivedFrom=[dict(file=a['file'],sha256=a['sha256'],record=a['file'].replace('.png','.derivation.json')) for a in manifest['assets'] if a['file'].startswith('assets/ui/cards/')])
(deckroot/'deck-review.derivation.json').write_text(json.dumps(capture,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('README, batch indexes, manifests and review provenance finalized')

