# 斗地主可接入 UI 素材

本批包含 **48 枚无字功能图标 + 16 个无字控件皮肤**，全部是真实 RGBA。3 个图标图集、2 个皮肤图集由宿主内置 image_gen 生成；另有1次导航图集AI修正。实际型号／质量未披露，逐图实际字段为 null，目标配置快照保留。

## 接入入口

- [manifest.json](manifest.json)：每条包括 id、kind、file、record、SHA256、真实尺寸、alpha 统计及源坐标。
- [control-metrics.json](control-metrics.json)：64个新素材与24个已有控件，共88项；以 kind/id 或 file 区分，源纹理像素与2560×1080逻辑像素明确分开。
- [font-contract.json](font-contract.json)：中文标题、正文、按钮、数字的字体栈、颜色、字号、换行与溢出规则；不附带或下载字体文件。
- [mapping.json](mapping.json)：完整60页UI的素材路径绑定；背景、人物用逻辑ID标待协调者接线，未冒称已接入运行。
- [qa-report.json](qa-report.json)：64个裁片逐项哈希、真实透明、可见主体、透明外沿、头像内圆透明、88项尺寸与60页路径核验。

图标统一位于 `icons/<id>.png`，皮肤统一位于 `skins/<id>.png`，图旁 `.derivation.json` 追溯原生源图与生成记录。已有 `assets/ui/controls` 的按钮、开关、输入框等直接复用。

## 尺寸与拉伸

图标、头像框、稀有度、红点、带居中玉饰的对话框、带指针tooltip、带流苏的完整窗口均等比显示。列表行、普通/选中物品槽与无中央图案的正文板可按metrics九宫格伸缩。任意比例正文窗口优先复用已有 `controls/panel.png`，标题和装饰分层，以免把流苏、玉饰或指针横拉变形。九宫边距是保守的美术接入参数，仍须目标引擎在最小/最宽尺寸验证。

## 来源和像素 QA

原生图集实际为1254×1254（3组图标与窗口皮肤）及1774×887（槽框皮肤）；不是提示词要求的2048原生。所有运行素材只裁切与透明通道清理，无插值、放大或程序绘图。原生alpha≤4低透明杂点清零；alpha<32且离实色主体2像素以外的游离杂点移除；主体alpha>16全部保留，记录逐图与逐片坐标。

首次导航v1按数学等分网格检查有FAIL：cross_cell_components=7、cross_cell_visible=7（阈值0）；WARN boundary_band=2805、safe_frame=16（阈值0），faint_specks floor88850/detached25。该稿还错误使用金发头像，已通过AI编辑修正为既有短棕发金发带道童。最终裁片不硬套等分网格，沿实际alpha>16零像素透明通道自适应切分；64片均通过透明外沿与主体不裁损检查。不能把原始等分失败说成已通过。

运行环境doctor有python.path WARN（PATH存在其他Python）；本批所有处理明确使用隔离Python3.12。未启用付费API、未进行任何Git操作。浅色/深色底像素复核图在 `designs/ui/runtime-kit/*-alpha-review.png`，它们是裁片合成检查图，不是新的AI生成。

