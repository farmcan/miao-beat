# Character motion v2 — 可复用准备模块

2026-10-29。**状态：data / native API / point-path 技术验证通过；完整角色静态 gate、绑定和动态验收未完成。** 没有修改 public、源 native、生产部署或其他 agent 的模型。没有新增现金调用或付费服务。

当前完整角色尚在 C36/C37 与完整灰模整合阶段。本目录不提前扩角色动画；没有保存绑定后的 blend、动作、渲染片段或 GLB。准备工作的目标是：静态角色通过后，可以更换整张 connected skin 与作者关节锚点，同时保留实际琴弦路径、输入控制接口和可复验的接触来源。

详细研究、接口、映射边界与后续验收见 [motion-rig-reference-and-handoff-2026-10-29.md](../../docs/research/motion-rig-reference-and-handoff-2026-10-29.md)。

| 文件 | 作用 |
| --- | --- |
| `extract-c35-profile.py` | 只读 C35；读取 actual evaluated 六弦、nut、13 根 fret、5 个接触三角及来源；在内存创建无绑定 native scaffold 并检查 API |
| `native_rig_scaffold.py` | 8 骨、双臂两骨无拉伸 IK、独立 head、左爪世界接触位置；不切网格、不自动权重、不绑定角色 |
| `contact-motion.mjs` | 显式 host 时间驱动；单音单弦 / 和弦一次扫弦；140ms 闭环，覆盖式接管，无队列；head/blink 独立 |
| `remap-contact-bindings.mjs` | 合并后必须给显式 source→target vertex map；不使用 nearest；不继承旧接触 pass |
| `validate-motion.mjs` | 8 键、150ms 连按、单/和弦跨弦计数、70ms 中断位置连续、左锚不动、head/blink 不重启、错误 remap 拒绝 |
| `validate-path-geometry.py` | 对控制器真实输出点，重读 native 的 actual evaluated 六弦 tube 做距离检查 |
| `evidence/c35-rig-profile.json` | 原 native hash、实际几何、每键弦/品目标、接触绑定、未批准关节锚点 |
| `evidence/*validation*.json`、`*probe.json` | 机器可读结果；不是艺术或动态通过证明 |
| `sources/` | MIT 上游实现的固定 commit 源码、许可与 hash；只研究，不被运行模块 import |

复跑顺序：

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python design/character-motion-v2/extract-c35-profile.py
node design/character-motion-v2/validate-motion.mjs
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python design/character-motion-v2/validate-path-geometry.py
```

每 agent 同时只运行一个 Blender 进程。本目录脚本不渲染、不保存源 native。source 仍为 C35，不能拿这些结果代替后续完整整合角色的审计。

源码采用本仓库 MIT 范围；`sources/three-*` 与 Godot reference 各自保留上游 MIT 声明。未导入外部模型、权重、贴图或生成式资产，因此没有把代码许可错误套到美术资产。Blender 原生功能的使用不等于复制其 GPL 实现。
