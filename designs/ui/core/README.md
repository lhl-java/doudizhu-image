# 核心界面批次交付索引

核验时间：2026-10-26T11:29:38.2431775+00:00。本批覆盖全量 60 项中的 **13 个核心主界面**（01–10、56–58）；范围见 [UI_SCOPE.json](../../../docs/UI_SCOPE.json)，只报告 core 批次。

独立主图 **13/13**，逐图记录、提示词和实际视觉检查齐全。必要状态 **44/44** 已有设计覆盖：实绘 rendered **26**，共享组件 shared_component **18**，仅规格 specified_only **0**。

shared_component 指已核验既有图板、控件或牌桌，并定义具体原生文案、按钮、行为和禁用原因；它不是另外绘制的状态整屏，也不是已接入的客户端。多个 rendered 状态可同时出现在同一张主图。

所有页面均为 design_ready_user_review，userApproval=false。设计复核通过，不代表用户已批准。数值、昵称、技能和期限为本项目设计示意，未声称逐屏实测腾讯当前客户端。

提示词画布目标为 2560×1080；下表按 PNG 头实测原生尺寸，未用放大替代原生细节。使用宿主内置 image_gen；实际型号和质量未披露，记录保留 null。配置中的 GPT Image 2.5 Sunburst / max 仅为用户目标。

| 页面 | 主图 | 原生尺寸 | 生成记录 | 状态规格 | 提示词 | QA | R/S/O |
|---|---|---|---|---|---|---|---|
| 01-launch-login · 启动与登录 | [PNG](01-launch-login-v1.png) | 1931×814 | [generation](01-launch-login-v1.generation.json) | [states](01-launch-login.states.json) | [prompt](../../../prompts/core/01-launch-login-v1.txt) | passed_for_design_review | 2/2/0 |
| 02-lobby · 全功能大厅 | [PNG](02-lobby-v1.png) | 1931×814 | [generation](02-lobby-v1.generation.json) | [states](02-lobby.states.json) | [prompt](../../../prompts/core/02-lobby-v1.txt) | passed_for_design_review | 2/1/0 |
| 03-classic-select · 经典玩法选择 | [PNG](03-classic-select-v1.png) | 1932×814 | [generation](03-classic-select-v1.generation.json) | [states](03-classic-select.states.json) | [prompt](../../../prompts/core/03-classic-select-v1.txt) | passed_for_design_review | 1/2/0 |
| 04-stakes-select · 场次选择 | [PNG](04-stakes-select-v1.png) | 1931×814 | [generation](04-stakes-select-v1.generation.json) | [states](04-stakes-select.states.json) | [prompt](../../../prompts/core/04-stakes-select-v1.txt) | passed_for_design_review | 3/0/0 |
| 05-matchmaking · 匹配等待 | [PNG](05-matchmaking-v1.png) | 1931×814 | [generation](05-matchmaking-v1.generation.json) | [states](05-matchmaking.states.json) | [prompt](../../../prompts/core/05-matchmaking-v1.txt) | passed_for_design_review | 1/2/0 |
| 06-friend-room-entry · 好友同玩入口 | [PNG](06-friend-room-entry-v1.png) | 1931×814 | [generation](06-friend-room-entry-v1.generation.json) | [states](06-friend-room-entry.states.json) | [prompt](../../../prompts/core/06-friend-room-entry-v1.txt) | passed_for_design_review | 1/1/0 |
| 07-create-room · 创建房间 | [PNG](07-create-room-v1.png) | 1931×814 | [generation](07-create-room-v1.generation.json) | [states](07-create-room.states.json) | [prompt](../../../prompts/core/07-create-room-v1.txt) | passed_for_design_review | 2/1/0 |
| 08-join-room · 加入房间 | [PNG](08-join-room-v1.png) | 1931×814 | [generation](08-join-room-v1.generation.json) | [states](08-join-room.states.json) | [prompt](../../../prompts/core/08-join-room-v1.txt) | passed_for_design_review | 1/3/0 |
| 09-room-waiting · 好友房等待 | [PNG](09-room-waiting-v1.png) | 1931×814 | [generation](09-room-waiting-v1.generation.json) | [states](09-room-waiting.states.json) | [prompt](../../../prompts/core/09-room-waiting-v1.txt) | passed_for_design_review | 3/1/0 |
| 10-invite-friends · 邀请好友 | [PNG](10-invite-friends-v1.png) | 1931×814 | [generation](10-invite-friends-v1.generation.json) | [states](10-invite-friends.states.json) | [prompt](../../../prompts/core/10-invite-friends-v1.txt) | passed_for_design_review | 2/1/0 |
| 56-offline · 单机练习 | [PNG](56-offline-v1.png) | 1931×814 | [generation](56-offline-v1.generation.json) | [states](56-offline.states.json) | [prompt](../../../prompts/core/56-offline-v1.txt) | passed_for_design_review | 1/3/0 |
| 57-hero-skills · 英雄能力说明与选择 | [PNG](57-hero-skills-v1.png) | 1931×814 | [generation](57-hero-skills-v1.generation.json) | [states](57-hero-skills.states.json) | [prompt](../../../prompts/core/57-hero-skills-v1.txt) | passed_for_design_review | 4/0/0 |
| 58-season-shop · 赛季兑换 | [PNG](58-season-shop-v1.png) | 1931×814 | [generation](58-season-shop-v1.generation.json) | [states](58-season-shop.states.json) | [prompt](../../../prompts/core/58-season-shop-v1.txt) | passed_for_design_review | 3/1/0 |

R/S/O = rendered / shared_component / specified_only。

## 状态复用与交付边界

56 单机练习主图只实绘可开始的难度选择页。进行中、暂停、结束没有独立 PNG：进行中复用 [14 三人牌桌](../table/14-play-turn-v2.png) 与 [52 牌面](../components/52-card-and-effects-v1.png)，暂停与结束复用 [50 通用弹窗](../components/50-shared-dialogs-v1.png)、[51 通用组件](../components/51-common-components-v1.png)及其透明切片。离线标题、电脑身份、暂停、再练一局与不结算金豆等原生文案及行为见 [56 状态规格](56-offline.states.json)。

58 的可兑、不足、已兑在主图同屏可见；到期复用公共空态、禁用按钮及原生到期说明，没有另画到期整屏。其他共享状态的逐项来源、区域、哈希和文案见各页 states 或 [状态覆盖汇总](state-coverage.json)。

页面静态图和状态规范不等于可运行界面。客户端、服务器、真实认证、社交发送、支付、兑换与动态动画接入均不在本批美术完成声明内。supplementalStates 为额外交互规格，单独列于汇总，不计入 44 个必要状态。

## 可追溯汇总

- [batch-result.json](batch-result.json)：13 页文件、哈希、尺寸、QA与范围统计。
- [state-coverage.json](state-coverage.json)：44 个必要状态的实际覆盖与共享依赖，补充规格单列。
- [validation.json](validation.json)：13张PNG与宿主源图、提示词、回执、四张实际参考图的独立哈希核验。
- [索引生成脚本](.production/write-core-index.ps1)：从现存 scope、PNG、generation、states 和 prompt 重建本批汇总，只写 core 目录。
- [初版大厅支持参考](../lobby-ui-v1.png)与[三人角色稿](../../characters/characters-trio-v1.png)继续保留；本批全功能大厅为02独立新图。

本次脚本核验真实文件、原生尺寸、PNG/提示词/回执哈希、必要状态名与共享依赖哈希。图像内容的实际视觉核验记录保存在各 generation 和 states，不由脚本推断。
