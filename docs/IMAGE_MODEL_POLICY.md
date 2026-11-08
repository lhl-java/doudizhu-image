# 模型目标与逐图记录

唯一默认设置为 [config/image-generation.json](../config/image-generation.json)。用户本次指定 GPT Image 2.5，2026-10-26 核实 [Sunburst 官方模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)及[参数文档](https://developers.openai.com/api/reference/resources/images/methods/generate)。本批以配置快照保持一致；以后升级要遵守用户的显式型号选择。

优先内置 image_gen。本次工具接口没有 model、quality 选择器，继续宿主管理入口；配置和提示词是目标，不证明实际锁定某个 API 型号或质量。API／CLI 是需明确选择的单独计费备用路径，不因参考图读取问题改用付费 API。

每张新生成或 AI 编辑的图片，包括重试稿，保存旁置 `<图片名>.generation.json`：

- `file`、`sha256`、含时区的 `generatedAt`、实际 `width`、`height`、`format`。
- `tool`、`route`、可得的调用／结果 ID。
- `configSnapshot` 保存当次设置的完整目标快照。
- `submittedParameters.model`、`submittedParameters.quality` 只填真实参数；没有选择器则为 null，并说明未开放。
- `actualModel`、`actualQuality` 只依据本次返回或可靠元数据；未知为 null。
- `evidence` 保存结果／receipt／C2PA 等证据及对应字段；`unverifiedReason` 写明未确认原因。
- `prompt` 指向实际提示词，`references` 记录参考路径、哈希、用途；编辑关联前图。

未披露实际值时使用“宿主管理，工具未披露／无可核实元数据”。原生分辨率与导出分辨率分别记录。裁切、缩放、拼接等派生素材记录 `derivedFrom`、来源哈希与 `operation`，不冒称新生成。旧参考复制保留历史未知状态，不用新配置回填历史型号。

完成标准：本批每张新增图片均有可追溯记录，文件真实存在，经过视觉检查，README 可找到图片及记录；配置升级不改写旧图历史。

