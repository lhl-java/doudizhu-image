# 牌局 UI 批次

独占 11–22、53–55，共 15 项。画风沿用两张指定参考与本项目大厅、三人角色。每项独立整屏，逐图记录实际入口与来源。

| 页面 | 选用成图 | 实际尺寸 | 状态 | 来源类型 |
|---|---|---|---|---|
| 11-deal-bid · 发牌与叫地主 | [11-deal-bid-v2.png](11-deal-bid-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 12-rob-landlord · 抢地主 | [12-rob-landlord-v1.png](12-rob-landlord-v1.png) | 1930 × 815 | design_ready_user_review | builtin |
| 13-double · 明牌与加倍 | [13-double-v2.png](13-double-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 14-play-turn · 主动出牌 | [14-play-turn-v2.png](14-play-turn-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 15-follow-pass · 跟牌与不出 | [15-follow-pass-v2.png](15-follow-pass-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 16-trustee · 托管与恢复 | [16-trustee-v3.png](16-trustee-v3.png) | 1931 × 814 | design_ready_user_review | derived |
| 17-reconnect · 掉线与重连 | [17-reconnect-v2.png](17-reconnect-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 18-round-win · 单局胜利 | [18-round-win-v1.png](18-round-win-v1.png) | 1931 × 814 | design_ready_user_review | builtin |
| 19-round-loss · 单局失败 | [19-round-loss-v1.png](19-round-loss-v1.png) | 1931 × 814 | design_ready_user_review | builtin |
| 20-room-summary · 好友房总战绩 | [20-room-summary-v1.png](20-room-summary-v1.png) | 1931 × 814 | design_ready_user_review | builtin |
| 21-table-settings · 牌桌内设置 | [21-table-settings-v2.png](21-table-settings-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 22-replay-history · 战绩与回放 | [22-replay-history-v2.png](22-replay-history-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 53-table-chat · 对局聊天表情语音 | [53-table-chat-v2.png](53-table-chat-v2.png) | 1931 × 814 | design_ready_user_review | derived |
| 54-disband-vote · 好友房解散投票 | [54-disband-vote-v1.png](54-disband-vote-v1.png) | 1931 × 814 | design_ready_user_review | builtin |
| 55-card-counter · 记牌器与倍数详情 | [55-card-counter-v2.png](55-card-counter-v2.png) | 1931 × 814 | design_ready_user_review | derived |

每页旁置 .states.json 逐项说明 requiredStates。rendered 表示当前选用画面已看图；shared_component 表示已有同源公共皮肤、牌面和原生动态文字层可复用的状态规范，不表示每种变体都有独立 AI 截图，也不表示客户端已实现。

带 v2/v3 的 UI 组合稿把原生生成牌桌作为底图，再排版同源面板、身份徽章和正确点数牌面；记录 route=derived、derivedFrom、布局 JSON 与缩小/九宫格操作，不冒称新模型原生细节。原始源图的待修历史不改写。

静态牌局均为视觉示意，玩法回执、发牌合法性、实时计时、自动操作、联网与最终业务规则由客户端/服务端接入验证。

实际提示词及复现辅助脚本在 ../../../prompts/table/。生成目标为配置中的 GPT Image 2.5/max；当前工具未披露实际型号/质量，各源记录均保留 null 及理由。
