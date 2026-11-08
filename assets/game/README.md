# 完整美术接入

`manifest.json`是243项当前采用PNG及来源记录的唯一总索引。15项是低分辨率动画预览图板，其余228项是独立游戏美术；包含五套服装10张独立胜负姿势。图板不得放大当高清角色。背景、角色、牌桌、横幅等保留独立纹理。

## 文件与坐标

- `runtime-index.json`：稳定逻辑ID到文件的映射、角色/装扮、54牌、背景与牌桌、皮肤、图标、15角色clip及12FX。
- `atlas.json`：194个切片、2张RGBA图集；左上为原点，像素矩形`[x,y,w,h]`，原图1:1，无旋转、无裁边，4像素透明间隔。`godot/sprite-*.tres` 使用 `res://assets/...`，保持目录结构即可导入Godot4。
- `../ui/runtime-kit/control-metrics.json`：88条尺寸、内距、最小尺寸与hitbox。`uniform_contain` 的流苏/雕饰框整体等比显示；仅标为九宫格的控件使用 `nineSliceInsets`。画板不能按任意宽高直接拉伸。
- `../ui/runtime-kit/font-contract.json`：文字层样式、颜色与系统字体fallback。不分发字体二进制；客户端按目标平台选择可用字体并实测字形与溢出。
- `../../runtime/screens.json` 与 `copy.zh-CN.json`：60项页面和223状态的语义绑定，铜钱/玉牌文案。设计图中的旧示意数据不作为真实账户与定价数据。

背景以cover显示，必要时按safe-area中心裁切；透明牌桌以contain显示。默认横屏2560×1080逻辑坐标。源码实际尺寸见manifest，角色最终画布1024×1024、脚底锚点`[512,920]`。所有图像使用straight RGBA；图集混色与滤镜由引擎导入设置管理。

## 角色与特效

角色原图与`character.json`在 `../characters/<id>/`。三人为`daotong`、`taohua`、`hulu`；地主和农民是对局身份，可绑定任意角色。每人master/win/lose三姿势、八表情。道童含基础加五套服装。

`../animations/characters/manifest.json`绑定每人idle/think/play/win/lose。高清渲染读取1024原图与clip关键帧，预览图板每格160×200，不应放大。`player.mjs`的`createActorPlayer(canvas,{actor,skin,onEvent})`返回`play`、`seek`、`setSkin`、`destroy`；出牌在240ms触发`card_flight_visual`。待机/思考循环，胜负姿势定时切换。换装时从该皮肤`poses`加载独立胜负原图，复用关键帧时序；未做连续关节或AI视频重绘。

`../fx/manifest.json`提供12个事件特效、blend、时长、loop、源图、timeline与frames路径。可直接按`frames.json`逐帧播放384×384PNG；one-shot最后1ms为透明结束哨兵，循环不追加该哨兵。或按timeline渲染源图：位移单位是384像素画布比例，常规baseSpriteSize=300，发牌光带为220，随逻辑画布等比缩小；不超过384原生帧展示尺寸。引擎需在one-shot完成后释放实例。它们是静态AI插画的2D变换动画，不是逐帧AI重绘或视频。

## 预览与验证

从项目根运行 `powershell -ExecutionPolicy Bypass -File tools/start_preview.ps1`，打开分层预览；角色独立播放器另见 `../animations/characters/index.html`。原设计索引在 `../../preview/index.html`。预览用于美术层、文字与本地反馈，无生产账号/支付/服务器。

使用安装有Pillow的Python运行 `python tools/validate_full_art.py`；Node运行 `node tools/verify_art_runtime.mjs`。前者检查真实文件/像素/透明边界与时序，后者使用模拟DOM与Canvas核对引用和交互事件。报告在项目`docs`。`preview/integration`为已有素材离线组合检查，附逐图来源链。

当前真实浏览器自动操作被Work设置禁用；尚无引擎导入、实机性能、真实字体排版或用户美术批准的通过声明。美术文件的离线完成和生产客户端最终验收分别记录。
