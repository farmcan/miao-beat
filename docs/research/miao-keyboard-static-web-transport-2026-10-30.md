# 默认色静态GLB传输诊断：暂不采用

2026-10-30，root作为传输测试作者。输入为已通过三方原生静态门槛的 `default-color/keyboard-default-color-native36.blend`，SHA `3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b`。本实验不改源文件，不应用pose、不造动作、不替换public。导出测试不是角色本身的第二次验收。

## 实际执行和纠正

脚本 `design/miao-reuse-keyboard-v1/test_static_web_roundtrip.py` 在官方3.6.23 / factory-startup / disable-autoexec下顺序运行；所有输入原生文件SHA不变。render-matched VIEWPORT代理沿既有Subsurf/render开关与IsViewport=False处理，仍不是直接RENDER depsgraph捕获。

1. 首次测试的名字筛选错误：只包括GEO-* mesh，漏CAT-*眼部与Curve，且把隐藏的源模板复制进来；导出默认还遍历所有scene遇到源rig错误。已纠正为显式当前snapshot scene、过滤原生可见性、包含CAT-*与Curve，并在临时代理中realize原作者instances。旧失败log保留，不称来源模型缺眼。
2. 修正后evaluated snapshot完整保留脸、手、琴桌。glTF不支持AREA灯，因此控制测试在重导入后重新放回相同灯与world，分开评估几何/材料传输，不能假装灯光已包含在GLB。
3. root实际打开最终 `static-web-roundtrip/evaluated-snapshot.png` 与 `gltf-reimport.png`：几何轮廓/眼口/手均存在，但重导入的青色眼面明显变暗，手部与脸边阴影也变重。**当前传输视觉不通过，不用于网页。** 没有用更亮的一张截图掩盖差异。

最终测试GLB为17,616,796字节、479,354tris，SHA `61b5f71822e7fb6f94978136b21486f0372e06810eabc2550c626122e8148209`。这既不是默认页轻量资产，也没有通过浏览器性能/视觉检查。未把它上传public，未启动动画导出扩展。

## 已知与未知

GLB中`light blue`基色数值存在；源对应材质本身是简单Principled节点，shadow_method=OPAQUE，不足以据此确定变暗根因。没有完成逐顶点法线/材质侧向/阴影覆盖的归因，不能臆断原作者shader或模型质量有问题。源静态三评GO依然只适用于原生图，不继承给此导出。

短期继续原生Blender完整帧动作验证，避免GLB传输问题阻断唯一单键假设。将来重开web3D路线需要新的有限诊断证据与独立图像评审，不能直接采用本实验文件。一次按下/一次回弹、手指到不同真实键位、快速输入自然转向仍是后续验收项。
