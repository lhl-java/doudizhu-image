# 角色 UI 关键帧动画

3 位角色各有 `idle / think / play / win / lose`，共 15 个 clip、240 帧透明烘焙预览。全部艺术来自已有角色姿态、思考头像、头像框和玉绿牌背；这是 CPU 合成与整体变换，没有新生图、AI 视频、关节骨骼或全身连续动作。

入口为 `manifest.json`。`clips[]` 包含 `id / actor / action / file / sheet / frameSize / frames / durationsMs / loop / record`。各 clip JSON 提供毫秒关键帧、原 1024 角色画布 pivot `[512,920]`、步进姿态切换、smoothstep 数值插值、事件、来源路径及哈希。`engine.json` 是通用引擎图集导入数据，帧矩形按左上角像素坐标 `[x,y,w,h]`。

| 动作 | 长度 | 循环 | 行为 |
| --- | --- | --- | --- |
| idle | 1600ms | 是 | 整体呼吸，最大纵向缩放 1.2%、位移 5/1024 画布单位 |
| think | 1920ms | 是 | 整体轻倾斜、独立思考头像 HUD 渐入渐出 |
| play | 960ms | 否 | 整体前倾反馈，240ms 起显示已有牌背的视觉飞行与拖影 |
| win | 1680ms | 否 | 120ms 切真实 win 图，保持后在 1440ms 回 master |
| lose | 1680ms | 否 | 120ms 切真实 lose 图，保持后在 1440ms 回 master |

事件均为 `visualOnly` 展示提示。牌背飞行不会选牌、扣手牌、提交回合或决定胜负；这些由游戏控制器处理。循环每轮触发一次，seek 默认不触发。`clip_complete` 建议转回 idle，直接图集播放也可停在最后的 master 帧。

每个 PNG 为 640×800 的 4×4 图集，单帧 160×200，预览 pivot `[80,180]`，保留真实 RGBA。为控制本批在 10 MiB 内，烘焙预览使用小尺寸；高清运行使用原有 1024 PNG 加 JSON 时序。`player.mjs` 提供这种 Canvas 播放方式，320×400 画布中直接缩小原图，没有放大预览帧。`index.html` 可切换三人五动作及道童换装，需以项目根为静态站点访问。

```js
import { createActorPlayer } from './assets/animations/characters/player.mjs';
const player = await createActorPlayer(canvas, { actor: 'daotong', onEvent: console.log });
await player.setSkin('daotong_festival');
player.play('win');
// 释放时调用 player.destroy()。
```

五套道童换装复用关键帧，当前`character.json`各skin的`poses`含其master和独立win/lose PNG。胜负在120ms切到本服装独立姿势，1440ms回本服装master；不会切回基础青云衣。没有同服装思考头像时隐藏头像HUD。既有烘焙图集展示基础服装，高清换装动作使用原图与JSON时序，未重复导出五套皮肤的全部图集。

每人 `*-all-actions.webp` 为五动作串接的 7840ms 动画预览，WebP 质量 65、有 alpha，编码器可能合并相邻相同帧但保留时间。透明 PNG 图集与 JSON 是帧和时序依据。所有 PNG/WebP/验收图都有 `.derivation.json` 来源记录。图集制作先在不超过原图分辨率的中间画布做仿射，再以预乘 alpha 的 LANCZOS 缩小，避免小尺寸直接采样锯齿。

`validation.json` 包含 240 帧透明边界、六段循环首尾逐字节一致、来源哈希、120/1440ms 姿态、无放大与三份 WebP 全帧解码/时长检查。15 张完整图集和 3 张浅底时序检查图已实际查看。`player-validation.json` 是 Node mock Canvas 的来源选择与时序检查；本 worker 的浏览器入口返回“Local browser use is disabled in Work settings”，因此浏览器实播验收由根协调者完成，未把 mock 检查当作浏览器截图证据。
