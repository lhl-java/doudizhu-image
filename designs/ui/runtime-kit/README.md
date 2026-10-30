# UI runtime-kit 原生图集与来源

当前采用：

| 源图集 | 数量 | 原生尺寸 | 逐图记录 |
|---|---:|---|---|
| [导航图标v2](icons-navigation-v2.png) | 16 | 1254×1254 | [generation](icons-navigation-v2.generation.json) |
| [玩法图标](icons-gameplay-v1.png) | 16 | 1254×1254 | [generation](icons-gameplay-v1.generation.json) |
| [资源操作图标](icons-resources-v1.png) | 16 | 1254×1254 | [generation](icons-resources-v1.generation.json) |
| [空白窗口皮肤](skins-windows-v1.png) | 8 | 1254×1254 | [generation](skins-windows-v1.generation.json) |
| [物品槽头像框皮肤](skins-slots-v1.png) | 8 | 1774×887 | [generation](skins-slots-v1.generation.json) |

每张均实际附带两张用户指定style图。导航v2另附修正前图及已确认三人角色设定，修正道童身份。生成数为6次（5张当前源图+1张被替代源图），实际版本与画质未披露均记录null。

正式裁片和接入规范见 [runtime-kit](../../../assets/ui/runtime-kit/README.md)。`*-alpha-review.png` 为同批裁片在米白/深玉绿底的原生尺寸合成检查，非新的生成图，来源见 [alpha-review.derivation.json](alpha-review.derivation.json)。各图已实际查看，图标含义、顺序、控件空白、头像内圆透明及深浅底边缘均检查。

初始导航v1的网格/身份问题及后续自适应切分依据在qa-report保留。当前五张源图是有效切片输入，不作为无用中间图清理；被替代v1在引用和来源记录核实后只保留文字证据。

