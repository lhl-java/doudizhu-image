# 配套 UI 批次

已生成并看图检查 15 / 15 项。全部使用宿主内置 image_gen，模型与质量目标读取项目配置，实际未披露值记录为 null。

| ID | 页面 | 成图 | 原生尺寸 | 来源与状态 | 评审状态 |
|---|---|---|---|---|---|---|
| 37-item-detail | 商品详情 | [37-item-detail-v1.png](37-item-detail-v1.png) | 1930×815 | [记录](37-item-detail-v1.generation.json) · [状态](37-item-detail.states.json) | 首版待用户确认 |
| 38-wallet | 仙豆兑换 | [38-wallet-v1.png](38-wallet-v1.png) | 1931×814 | [记录](38-wallet-v1.generation.json) · [状态](38-wallet.states.json) | 首版待用户确认 |
| 39-inventory | 背包 | [39-inventory-v1.png](39-inventory-v1.png) | 1931×814 | [记录](39-inventory-v1.generation.json) · [状态](39-inventory.states.json) | 首版待用户确认 |
| 40-player-profile | 个人资料 | [40-player-profile-v1.png](40-player-profile-v1.png) | 1930×815 | [记录](40-player-profile-v1.generation.json) · [状态](40-player-profile.states.json) | 首版待用户确认 |
| 41-friends | 好友 | [41-friends-v1.png](41-friends-v1.png) | 1931×814 | [记录](41-friends-v1.generation.json) · [状态](41-friends.states.json) | 首版待用户确认 |
| 42-leaderboard | 排行榜 | [42-leaderboard-v2.png](42-leaderboard-v2.png) | 1932×814 | [记录](42-leaderboard-v2.generation.json) · [状态](42-leaderboard.states.json) | 首版待用户确认 |
| 43-daily-missions | 每日任务 | [43-daily-missions-v1.png](43-daily-missions-v1.png) | 1931×814 | [记录](43-daily-missions-v1.generation.json) · [状态](43-daily-missions.states.json) | 首版待用户确认 |
| 44-sign-in | 七日签到 | [44-sign-in-v1.png](44-sign-in-v1.png) | 1931×814 | [记录](44-sign-in-v1.generation.json) · [状态](44-sign-in.states.json) | 首版待用户确认 |
| 45-events | 活动中心 | [45-events-v1.png](45-events-v1.png) | 1932×814 | [记录](45-events-v1.generation.json) · [状态](45-events.states.json) | 首版待用户确认 |
| 46-mail | 邮件 | [46-mail-v1.png](46-mail-v1.png) | 1931×814 | [记录](46-mail-v1.generation.json) · [状态](46-mail.states.json) | 首版待用户确认 |
| 47-settings | 系统设置 | [47-settings-v1.png](47-settings-v1.png) | 1931×814 | [记录](47-settings-v1.generation.json) · [状态](47-settings.states.json) | 首版待用户确认 |
| 48-help-rules | 玩法说明 | [48-help-rules-v1.png](48-help-rules-v1.png) | 1931×814 | [记录](48-help-rules-v1.generation.json) · [状态](48-help-rules.states.json) | 首版待用户确认 |
| 49-support-notices | 公告与客服 | [49-support-notices-v1.png](49-support-notices-v1.png) | 1932×814 | [记录](49-support-notices-v1.generation.json) · [状态](49-support-notices.states.json) | 首版待用户确认 |
| 59-achievements-growth | 成长手册 | [59-achievements-growth-v2.png](59-achievements-growth-v2.png) | 1933×814 | [记录](59-achievements-growth-v2.generation.json) · [状态](59-achievements-growth.states.json) | 首版待用户确认 |
| 60-account-notices | 账号与版本 | [60-account-notices-v1.png](60-account-notices-v1.png) | 1932×814 | [记录](60-account-notices-v1.generation.json) · [状态](60-account-notices.states.json) | 首版待用户确认 |

图片为独立完整窗口，未缩放或程序重绘。提示词位于 ../../../prompts/support/，每次实际附带两张主风格参考；涉及角色时附三人设定图。

每页 states.json 明确 rendered 与 shared_component。15页共有30个必需状态在整屏可见，另29个状态已用真实公共控件、具体文案和行为完成设计映射；共享依赖逐文件SHA256已与assets/ui/manifest.json核对。共享状态未单独渲染成整屏图，不冒称已绘制专用状态图。另附所有页面的空态、加载、失败及动作处理中/结果规范。视觉自检不是用户批准，也不是客户端与服务器接入验收。


当前选用42-leaderboard-v2.png与59-achievements-growth-v2.png；两张v1图片为已被替代的AI修正输入。其文字来源记录保留，图片在协调者完成全量清单的当前版本映射后可清理。状态统计见state-coverage.json。
