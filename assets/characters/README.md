# 斗地主角色运行时美术

本批完成 3 位角色的 9 张独立全身姿态、24 张透明表情头像、5 张道童换装，共 38 张正式运行时 PNG。状态为 `asset_ready_user_review`，程序与美术检查通过；不代表用户已人工批准，也不单独证明全游戏交付完成。

入口为 `manifest.json`，每项提供稳定 `id`、`file`、`record`、`width`、`height`、`anchor`、`kind`、哈希及原生源图关联。各人的 `character.json` 还包含身份特征、姿态/表情映射、建议显示高度和换装规则。

| 角色 ID | 角色 | 资源 |
| --- | --- | --- |
| `daotong` | 玉绿道童 | `daotong/master.png`、`win.png`、`lose.png`、`expressions/*.png`、`costumes/*.png` |
| `taohua` | 桃花女修 | `taohua/master.png`、`win.png`、`lose.png`、`expressions/*.png` |
| `hulu` | 葫芦长者 | `hulu/master.png`、`win.png`、`lose.png`、`expressions/*.png` |

表情依次为 `calm` 平静、`smile` 微笑、`laugh` 大笑、`thinking` 思考、`surprise` 惊讶、`smug` 得意、`sad` 难过、`angry` 生气。道童换装 ID 为 `daotong_spring` 桃花春衣、`daotong_ink` 暮色墨衣、`daotong_moon` 桂月金衣、`daotong_snow` 雪色白衣、`daotong_festival` 庆典红衣；青云衣使用基础 master。

全身图统一透明画布为 1024×1024，脚底锚点 `[512,920]`，建议画布显示高度 520px。表情头像为 256×256，底部锚点 `[128,244]`，建议显示高度 128px。每位角色的三姿态共用一个缩小倍率；道童五换装使用道童的相同倍率。每张的原图裁切矩形、原图锚点、倍率及偏移见 `.derivation.json`，没有放大生成细节。

14 张独立全身原生图均为 1254×1254 RGBA，3 张最终表情原生图集为 1774×887 RGBA，保留于 `designs/characters/runtime-20261026/`，用于当前导出与接入。三人没有从原三人设定拼图中切出独立 master；每张 master、胜负姿态及换装均为独立生成或 AI 编辑结果。24 个头像由最终 4×2 图集裁切并缩小导出，属于派生资产。

实际共调用内置生图/编辑 20 次，保留 17 张最终原生图。早期 3 张表情图集因间距过小被 v2 取代，旧图片已删除，逐图模型、提示词、参考哈希及编辑来源文字记录仍保留。没有保留拒稿图片备份。

配置目标为 `gpt-image-2.5-sunburst` / `max`。内置工具没有型号或质量参数，也未返回可核实的型号/质量元数据；逐图 `submittedParameters.model/quality` 与 `actualModel/actualQuality` 如实记为 `null`。本批未使用付费 API。

`validation.json` 记录真实检查结果：38 张正式 PNG 全部 RGBA、alpha 范围 0–255、画布四边 alpha 全为 0、文件与来源哈希匹配、所有缩小倍率不超过 1。三张浅色/深色检查图和派生记录在 `review/`，已实际查看全部姿态、换装与表情。环境 doctor 整体为 WARN：宿主 still image 路径已成功使用；未装 scipy/resvg、PATH 无 ffmpeg、未配置 API 密钥不影响本批透明 PNG 交付。

角色的 master/win/lose 为三张独立界面姿态。运行时可以做 2D 位移、旋转、缩放和姿态切换；本包不包含 AI 视频、骨骼全身连续动画或生成补间帧。换装播放变换动画时应保留该套衣服，避免悄悄切回青云衣胜负姿态。
