# Godot 本地环境与后续角色对比

Godot 4.7.2 标准版已安装：`/Applications/Godot.app`。

这是环境检查工程，不是Miao美术或动作版本。运行会真实渲染一个中性测试球，保存GPU截图和回执后自动退出。后续角色工程将在静态角色质量与材质迁移检查后加入；不能把这个球称为猫的优化。

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
