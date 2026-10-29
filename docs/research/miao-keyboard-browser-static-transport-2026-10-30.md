# 本地浏览器静态传输：实际 WebGL 验证

2026-10-30，root实现和操作；这不是独立艺术签署，不是演奏demo。页源码在 `design/miao-reuse-keyboard-v1/browser-static-transport/`；仅本机authoring服务器，不写public或发布到Pages。

模型仍是v1默认色pose `4fb6d4c…` 经“省略未用Color层”修正的15,561,764B静态GLB。不是后续v2抬键组scene，不能把这里的浏览器结果继承给新pose。静态材质往返已获独立craft允许进入浏览器验证；模型没有skins/animations，不支持弹奏。

## 实际闭环

- IAB真页面打开后显示“模型尚未加载”；点击“加载模型 · 15.6 MB”才动态import已有MIT Three0.186.1和下载GLB。
- 实际回到“模型已加载”状态，WebGL画面出现完整猫、双手、键盘、桌和落地关系；不是替代PNG或截图。
- 实际轻拖视角后可见另一侧体积，点击“回到正面”成功复位。Orbit被限制小角度，因为源面部GN按front camera烘焙，不能据此宣称任意相机都还原作者原生效果。
- 最终DOM记录 `ready=true`、renderer实际渲染统计995190 tris /332 calls（含shadow passes，不是模型本身tris）。console error列表为空。页面空闲不持续RAF；未做帧率、手机或受限网络性能宣称。

首个WebGL灯光过暗、长阴影偏硬，实际看后修正为更充分的环境/填光和PCF软化；采用既有pinned Three bundle明确支持的ACESFilmic enum4。最后完整视图和侧视已实际截图，未把Blender AREA灯重导入的控制图当作浏览器结果。当前Three显示灯光和tone map是近似look，尚无独立浏览器艺术评审，也不等于原生像素精确还原。

证据：`artifacts/miao-reuse-keyboard-v1/browser-static-transport/browser-front.png`、`browser-three-quarter.png`；HTTP server log在该artifact父目录。浏览器页显著标明“尚未接入弹奏”。

## 未完成

没有实时指骨/形变、触键、音符输入、八键、头眼、录制、导出或线上替换。该静态GLB的用途是验证成熟模型可以进入真实浏览器；后续必须从通过新静态门槛的完整scene生成正确动作，不能使用旧模型的随意变形或把此固定准备位接到ASDF假装每键都对应。

15.6MB /479354模型tris与实际332 calls也需在后续加载/渲染预算中处理；当前仅显式点击加载，不能默认放进主站启动。新的v2模型与动作需重新导出/验证，不能覆盖这份已记载证据。
