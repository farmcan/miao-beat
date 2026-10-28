# Godot 本地环境与后续角色对比

Godot 4.7.2 标准版已安装：`/Applications/Godot.app`。

默认入口仍是环境检查工程，不是Miao美术或动作版本。运行会真实渲染一个中性测试球，保存GPU截图和回执后自动退出。另有完整猫迁移诊断入口，范围和限制见下文；两者都不代表角色优化完成。

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path design/godot-character-lab --rendering-method gl_compatibility --audio-driver Dummy
```

实测：Apple M1 Pro，OpenGL API4.1 Metal / Compatibility；640×480真实viewport读回与PNG保存成功。截图、详细引擎hash及日志在 `artifacts/godot-setup/`（本地，不纳入公开产品）。不是headless脚本模拟渲染。

- 官方来源：https://godotengine.org/download/macos/
- 固定版本：https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable
- 二进制完整版本：`4.7.2.stable.official.ed1daf0bf`
- macOS Universal ZIP，SHA512：`38aa16e5bba2083941fc5b3e54be0089bd4cc35e32415f5b9fd9a8a6a7b9818255d44532ea8ef94b5aef56c4b407c2d634fa4f657e4ebe681ebbf59b7bac69ca`，与上游 `SHA512-SUMS.txt`一致。
- Apple签名：Prehensile Tales B.V.，Team ID `6K46PWY5DM`；`codesign --verify --deep --strict`成功；`spctl`返回`accepted / Notarized Developer ID`。没有关闭Gatekeeper、删除quarantine或安装第三方插件。
- 没有额外安装.NET、Web导出模板、外部MCP或GDExtension。仅运行Godot无需导出模板；未来Web导出要另核实模板/渲染/资源体积。
- Godot为MIT免费开源软件；发行包含引擎时保留其许可：https://godotengine.org/license/ 。本工程源码为本项目原创，未复制上游动画代码。

执行计划：`docs/character-engine-comparison-plan-2026-10-28.md`。此环境成功不证明高保真角色、IK、随机动作、Web或音画导出完成。

## 最小短毛实现实跑（同样不是Miao版本）

已核实并引入 MIT `maxvolumedev/sofluffy` 固定 `09af7e68c17db7b85a4780220b28dc015da28a91` 的5个必要源码/资源；保留 `addons/so_fluffy/LICENSE.txt` 与文件hash，未复制示例bee模型。运行：

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path design/godot-character-lab \
  --scene res://fur-probe.tscn --rendering-method gl_compatibility \
  --audio-driver Dummy --resolution 640x640 --quit-after 600
```

实际完成0/8/16层的同相机640×640 GPU图，原样上游shader在Godot4.7.2原生Compatibility编译运行；未见脚本/着色器错误。实际计数分别1/9/17 draw calls、3168/28512/53856 primitives，符合加层会重复绘制网格，不能说免费提高毛数或宣称快多少。

首轮小取景/默认黑根看起来是颗粒；第二轮正交近景、root gradient0.55、density0.15后能见轮廓细毛，但表面仍有规则点阵/壳层感，**未达到Miao原图短绒标准**。所有轮次保存在忽略的 `artifacts/godot-fur-probe/`。这只证实一个免费候选能在此renderer运行，不证明蒙皮、眼睑、角色材质、WebGL2/Safari、性能或美术通过；也未测FPS基准，Blender可同时占用GPU。

## 完整猫与吉他的原生迁移诊断 · 2026-10-29

`export-static-diagnostic.py` 从**未获美术验收的旧 C8r2** 场景导出完整猫/琴/相机；评估网格、将程序化基础色烘为顶点色，之后去除包括内部 BindUV 在内的UV。未导出原生groom、灯光、rig或动画。源native SHA为 `2432d199edeae964631cb79d96b1d06a5ba2fb908143532fc5bb0a86f600f33e`，只读原文件。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/godot-character-lab/export-static-diagnostic.py
/Applications/Godot.app/Contents/MacOS/Godot --path design/godot-character-lab --scene res://static-cat-diagnostic.tscn --rendering-method gl_compatibility --audio-driver Dummy --resolution 1024x1024
```

实际输出 `artifacts/godot-cat-static/whole-cat-diagnostic.glb` 45,046,024 bytes，SHA `d9e4702b99646bf7582702ee672ac5f84afb2385fa511c095e63c807684bb0ff`。74个mesh，约170万三角，真实画面75 draw calls（含地面）。保留旧源相机4.200276正交尺寸。资源很重，**不作为生产网页资产**，也未进行减面或Web导出。

实际诊断依次发现并记录：

1. 导入后顶点色未启用导致白模，运行时对 COLOR_0 显式启用。
2. 对角条纹来自阴影设置；保持几何不变关阴影后条纹消失。当前无阴影只是隔离试验，不是最终灯光。
3. Compatibility 下 linear COLOR_0 显示发红；`vertex-albedo-compat.gdshader` 用 OUTPUT_IS_SRGB 分支编码，恢复暖橙。Godot官方文档说明 `vertex_color_is_srgb` 只在 Forward+/Mobile 生效：[BaseMaterial3D](https://docs.godotengine.org/en/4.6/classes/class_basematerial3d.html)。

最新 `godot-static.png` 是实际M1 GPU读回；白模/阴影条纹/未校正色及各自回执均保留。眼部目前 alpha=0.04 透明近似，**不等于 Blender 折射/眼光学**。原生短绒缺失、木纹顶点色采样损失、阴影关闭，整体显塑料；身体和爪仍为未验收旧模型。不能称“Godot精致版本完成”。

`load_and_45_frames_ms=1955` 包含等待45帧且有并行Blender负载，既不是独立加载时间，也不是FPS基准。没有实际输入、音频、蒙皮、眨眼、随机动作、浏览器/手机、录屏或导出验收。当前场景使用仓库外层忽略的artifacts路径，仅本地诊断；换电脑须先取得源资产并运行导出，不承诺仅clone代码即可复原大文件。

当前执行顺序见 `docs/character-execution-plan-2026-10-29.md`。先修 Blender 静态角色，再迁移同一获验资产和制作公平动作比较。
