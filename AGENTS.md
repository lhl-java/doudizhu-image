# 斗地主美术项目长期指令

用户于 2026-10-26 指定本项目用于斗地主 UI 与角色制作，沿用相邻 `image` 项目已确认的道家 Q 版高清手绘风格。所有工作文件放在本项目内；当前本地目录为 `D:/work/doudizhu-image`。新窗口开始工作及每次生图／AI 修图前重读本文件。

## 开始制作

1. 阅读 [风格规范](docs/ART_DIRECTION.md)、[制作清单](docs/PRODUCTION_PLAN.md)、[图像设置](config/image-generation.json)及[模型与逐图记录](docs/IMAGE_MODEL_POLICY.md)。
2. 实际查看 `references/style/01-mail-event.png` 和 `references/style/team-ui-v2.png`，在生成调用中附上实际参考图。它们是用户指定的首要依据；来源哈希见 `references/style/manifest.json`。
3. 有同功能已确认成图时继续查看并承接它。用户上传到 `references/uploads/` 的其他游戏截图默认只参考功能和布局，风格仍跟两张主参考。缺失图须报告，不从 Git 恢复已删除素材。
4. 用宿主内置 image_gen 制作位图。用户本次选择 GPT Image 2.5；具体最高质量目标只维护在配置中。无模型／质量选择器时继续内置入口，实际未披露字段按未确认记录。API／CLI 单独计费路径需要用户明确选择。
5. 新图使用新版本文件名；逐图保存提示词、真实尺寸、哈希、模型与质量证据。完成后实际看图，核对风格、文字、结构及透明度，再更新制作清单。

## 项目边界

- 品牌名称、品类副标和当前Logo读取 [config/brand.json](config/brand.json)；制作标题、启动页或品牌文案时先读取该文件。旧设计与逐图记录保留当时工作标题，不全局改写其中的“斗地主”。
- UI、角色、牌面和控件保持同一美术方向。尺寸以当前专项说明为准，原生尺寸与导出尺寸分别记录；设计稿不等于客户端已接入。
- 保留成品、当前唯一在制稿、有效风格参考和必要文字记录；成品及引用验证后清理已替代中间图片。原 `image` 项目只读，不处理其他窗口素材。
- 用户于2026-10-26指定公开发布到 GitHub [lhl-java/doudizhu-image](https://github.com/lhl-java/doudizhu-image)。按该目标核验登录账号、仓库所有者、公开可见性和实际推送回执；不得把准备发布或本地提交说成远端已成功。Git保存最新已核验文件状态，保持来源记录与字节哈希；本地运行资料在`.work/`忽略目录。原`image`项目独立，不操作其共享HEAD、index、refs或固定上传批次。

