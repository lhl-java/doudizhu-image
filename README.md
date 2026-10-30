# 道友请出牌 · 斗地主美术项目

游戏名定为 **《道友请出牌》**，玩法副标 **“斗地主”**，宣传语 **“三位道友，一桌好牌。”**。品牌唯一配置见 [config/brand.json](config/brand.json)。

- [透明Logo PNG](assets/brand/daoyou-qing-chupai/logo-v1.png)（1902×1015，原图1:1加透明留白）
- [原生生成图](assets/brand/daoyou-qing-chupai/logo-native-v1.png)（1774×887）、[1024宽导出](assets/brand/daoyou-qing-chupai/logo-1024.png)
- [Logo深浅底预览](assets/brand/daoyou-qing-chupai/preview.html)、[提示词](prompts/brand/daoyou-logo-v1.txt)、[生成记录](assets/brand/daoyou-qing-chupai/logo-native-v1.generation.json)

按腾讯《欢乐斗地主》的斗地主相关功能梳理，延续相邻 image 项目已确认的道家 Q 版高清手绘风格。按用户最新要求先交付UI、角色和地图场景：现有设计与独立资源已覆盖三位原创角色、五套换装、场景、牌桌、扑克牌、图标、品牌及活动。五套服装新增10张独立胜负姿势并接入预览，223状态已有26类显式原生展示布局。资源包离线合同与[全包校验](docs/FULL_GAME_ART_VALIDATION.json)仅证明对应文件范围；网页实际视觉与目标客户端实机验收尚未完成。最新品牌见[品牌交付报告](docs/BRAND_DELIVERY.json)。

## 完整美术入口

- [原生分层预览](runtime/art-preview.html)：60 项界面绑定、223 个状态文案、角色动作、换装、双牌桌和 12 种特效。
- [角色动画播放器](assets/animations/characters/index.html)：三位角色各 5 组动作，含逐帧与时间轴。
- [五套服装胜负姿势检查](assets/characters/review/costume-poses-light-dark.png)、[10姿势验收](docs/COSTUME_POSES_VALIDATION.json)、[223状态布局](runtime/state-art.json)。
- [独立素材与接入清单](assets/game/manifest.json)、[引擎接入说明](assets/game/README.md)、[两张纹理图集](assets/game/atlas.json)。
- [大厅组合检查](preview/integration/lobby.png)、[对局组合检查](preview/integration/table-day.png)、[换装组合检查](preview/integration/wardrobe.png)。三张为现有素材离线合成，附来源记录，不是浏览器截图。

运行 `powershell -ExecutionPolicy Bypass -File tools/start_preview.ps1`，打开 <http://127.0.0.1:8771/runtime/art-preview.html>。模块与 JSON 预览须经过本地 HTTP 服务；直接双击 HTML 会受浏览器文件访问限制。

| 美术类别 | 已交付文件 |
|---|---|
| UI设计与状态 | 57 页独立界面、3 套公共图板；223 个必要状态 |
| 三位角色 | 9 张全身透明姿势、24 张表情头像；角色固定锚点 |
| 道童装扮 | 基础青云衣及5套新增独立服装；新增服装各win/lose，共10张独立姿势 |
| 公共UI | 48 个透明图标、16 种无字皮肤、24 个既有控件；88 条尺寸/九宫格/hitbox规则 |
| 场景 | 3 张无字无人背景、2 张透明牌桌 |
| 扑克牌 | 54 张准确花色点数牌；牌背、地主/农民、选中框等16个源素材 |
| 角色动作 | 15 个可播放 clip、240 个预览帧、3 个动画 WebP；高清原图实时播放器 |
| 对局FX | 12 种透明特效、12 条时间轴、192 个导出帧 |
| 标识与活动 | 透明“道友请出牌”标题与“斗地主”副标、应用图标、3张节庆横幅、9个32–1024像素图标导出 |
| 资源接入 | 243项总索引（含15张动画预览图板）、194个1:1图集切片、2张图集、Godot AtlasTexture文件 |

动画采用真实独立姿势和表情配合位移、旋转、缩放、透明度关键帧；属于2D界面角色动画。五套新增装扮已有各自独立胜负图，复用时序并保持当前服装，不切回基础青云衣。它们没有连续全身骨骼或AI视频的验收声明。

文件/哈希、透明边界、图集逐像素还原、动画时序与引用校验已通过；[运行时检查](docs/RUNTIME_INTEGRATION_VALIDATION.json)覆盖60项/223状态的模拟执行。当前 Work 设置关闭本地浏览器自动操作，因此未把真实浏览器布局、视觉实播或客户端实机接入标为已验收。223 状态提供设计/文案绑定和本地反馈，不等于全部生产状态逻辑已经实现。音效配音、音乐、玩法程序、服务器与支付不在视觉美术文件范围。

原始特效图板曾有跨格与微小透明噪点告警，原报告保留；最终采用归属切片并另验全部成品边缘。发牌帧截边和月亮边缘异物已修复。被替换的月夜图片按用户保留规则清理，来源文字与哈希仍在。

## 查看整套结果

- [全量图形预览](preview/index.html)：筛选、搜索、逐页原图、生成证据、状态规范。
- [公共状态演示](preview/states.html)：已有透明皮肤加原生文字，提供本地按钮反馈。
- UI设计索引地址：<http://127.0.0.1:8771/preview/index.html>。也可运行 `tools/start_preview.ps1 -View design`。

## 交付范围

- 57 页独立界面，覆盖登录大厅、经典与好友房、对局与结算、排位赛事、残局、角色装扮、商城背包、日常社交与设置帮助。
- 3 套公共图板：通用弹窗、24 个透明控件、牌面/身份/静态特效。
- 94 个通用 PNG 素材：24 控件、16 牌面与身份特效源、54 张准确点数花色的牌。
- 223 个必要状态：122 个主图可见，101 个以同源控件和具体原生文案/行为覆盖；0 个仅留说明。
- 三位角色的原有概念设定与全套 UI 内的角色表现保持同源。

## 文件目录

| 内容 | 入口 |
|---|---|
| 全量当前选用清单 | [UI_SCOPE.json](docs/UI_SCOPE.json) |
| 最终核验（无错误） | [FINAL_VALIDATION.json](docs/FINAL_VALIDATION.json) |
| 全量成图与状态索引 | [UI_DELIVERY_REPORT.json](docs/UI_DELIVERY_REPORT.json) |
| 大厅、房间、单机、能力、兑换 | [core](designs/ui/core/README.md) |
| 牌局、结算、聊天、记牌器 | [table](designs/ui/table/README.md) |
| 排位、赛事、残局、角色、商城 | [modes](designs/ui/modes/README.md) |
| 背包、资料、好友、任务、活动、系统 | [support](designs/ui/support/README.md) |
| 公共控件与牌面 | [components](designs/ui/components/README.md) |
| 94 素材及其来源链 | [assets/ui/manifest.json](assets/ui/manifest.json) |
| 54 张牌预览 | [deck-review.jpg](assets/ui/deck-review.jpg) |
| 三位角色概念与生成记录 | [角色图](designs/characters/characters-trio-v1.png) / [记录](designs/characters/characters-trio-v1.generation.json) |

## 尺寸与证据

整屏原生图通常约 1930–1932×814–815；公共透明图板为1448×1086，弹窗图板为1672×941。提示词尺寸目标与工具实际返回尺寸分别记录，未以放大冒充原生细节。
按 GPT Image 2.5 最高质量目标配置，内置入口未提供型号/质量选择器或返回字段，实际值仍如实记为未确认。每张生成/编辑及当前组合图均有来源记录。
54 张牌是同一生成空白牌框加原生点数/花色文字排版及两张生成大小王；不是54次独立AI生成。牌局修订组合保留实际来源链。
原 UI 公共图板中的特效为静态素材；新增完整游戏包另外交付12组可播放时间轴及192帧。客户端、服务器、支付或社交发送尚未接入。

## 参考与后续资料

首要风格图见 [references/style](references/style/manifest.json)，新需求图片放 references/uploads/，也可在制作聊天中附图。
功能核验与设计推导边界见 [REFERENCE_RESEARCH.md](docs/REFERENCE_RESEARCH.md)。制作规则见 [AGENTS.md](AGENTS.md) 和 [ART_DIRECTION.md](docs/ART_DIRECTION.md)。
公开仓库发布目标：[lhl-java/doudizhu-image](https://github.com/lhl-java/doudizhu-image)。用户于2026-10-26指定公开发布；实际创建和推送状态以远端回执为准。本地制作目录为 D:/work/doudizhu-image，原 image 项目的远端与上传批次独立管理。

Git按最新已核验状态发布；图片、提示词及来源记录保持原字节，不依赖Git LFS。公开文件清单见 [PUBLISH_SNAPSHOT.json](docs/PUBLISH_SNAPSHOT.json)。
