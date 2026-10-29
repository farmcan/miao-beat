# 原作者 smile close · 隔离静态 face 小研究

2026-10-30。**安全隔离转移成立；实际图有可见 P0，研究结果不采用。默认未应用表情的 baseline 完整保留。** 不是新的成品静态GO，不是动画，不改main/public，不继续debug或扫描别的笑容。

## 只读 snapshot diff

直接读 immutable `wingit_cat.blend` 中 `default` frame1 与 `smile close` frame13 的单key数值；两者均7315 FCurves，无缺失通道。没有apply action、`frame_set`、evaluate clip或创建action/keyframe；其他corrective actions未当clip。

精确值差异 **252条，64个面部骨**（191条绝对delta>1e-6，61条更小浮点差也全保留）。全部属于mouth/eye/eyebrow/lattice/teeth控制：`ACT-MouthCorner.*`、`BehindEyes_*`、`Hook_Curve_Mouth_*`、`Hook_*Eye_*`、`LTC-*Face/BehindEye`、`Mouth_*`、`Muzzle_Top*`、`Lips_Bot_WithCorner`、面部 `ROOT-*`、眉毛 `STR-*` / `STR-TIP-*`、`Teeth_*_Root`及 `PRP-Head`。**没有body/arm/hand/finger路径差异。**

实际全部data_path / bone / component / from / to见 `artifacts/miao-reuse-keyboard-v1/artist-face-pose-study/changed-face-channels.tsv`；完整parent链和原值见 `default-to-smile-close-diff.json`。

必要property核对：

| PRP-Head参数 | 作者default | 作者smile close | 隔离研究处理 |
|---|---:|---:|---|
| Sealed Mouth |0|0|保False，未切True|
| Sealed Teeth |0|1|按作者差异设True|
| Teeth_Zigzag |0|1|按作者差异设True|
| Curvature |2.76470566|2.76470566|共享作者上下文；收到版当前值5，隔离副本恢复为此同值，单独记账|

不是仅切Sealed Mouth去猜闭嘴。除252条face差异与上述一个明确face上下文，未整套应用7315通道。

## 隔离执行与保护证据

输入来自 `gray-supported/inspection-manifest.json`，native SHA固定 `31c427e53b47eb55251d0f25f9157545d0f81558183822837945c848085a1b9e`；输入前后SHA相同。官方3.6.23 factory/disable-autoexec，不运行embedded code。

应用前/应用后/两次render后，五类子hash **全部逐字相等**：非修改骨matrix_basis；384个身体/臂/指/腿/脊/尾/头主控的evaluated pose；身体/臂/手等实际evaluated geometry；全部已有mesh基几何；112个rig/keyboard/table/ground对象world矩阵。Quality1、原render2、材料保持，仅用默认色builder相同的RGBToBW compositor bypass显露原色。new actions/keyframes/frame_set均0。

输出仅在 `artifacts/miao-reuse-keyboard-v1/artist-face-pose-study/`：

- `smile-close-front.png`：完整猫、双爪、键盘、支架桌同帧。
- `smile-close-face.png`：对应脸部特写。
- `artist-smile-close-keyboard-study-native36.blend`：隔离研究副本。
- `smile-close-study-receipt.json`、`builder-visual-inspection.json`、`inspection-manifest.json`。

每次render前helper局部Euler直接同步camera世界Euler，逐轴误差全0。停渲消息到达前该单进程已完成两张授权研究图；此后仅查看既有图与落盘报告，没有继续render。

## 实际看图结论：保原表情

已用图像工具直接查看两图。笑嘴可读，源的zigzag牙线表现出来，未发生嘴完全消失；但是双眼内下角出现奶油色三角块，鼻子视觉上缩成小红点，宽大露齿表情也不是默认色基线的轻松原表情。**这组隔离转移有可见P0，不能采用或声称作者pose完整兼容成功。**

只读diff证明“改变的数据域可限定face”，保护hash证明没有损坏身体/手/桌；它们不能替代face的视觉验收。未知是该snapshot对收到版rig/材质的完整上下文适配，不把本次局部转移失败归为源作者pose质量差。依停止条件，保留未应用baseline、冻结研究副本，不额外试笑容、调flag或做动效。

Credit：**Cat Rig (CC-BY) Blender Foundation | studio.blender.org**。[原作者角色页](https://studio.blender.org/characters/cat/v1/)；[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。这是原作者pose数据复用，新增审计/相机脚本与记录不把源pose冒称原创。
