# v2 默认色 · 独立 motion/contact 静态短评

2026-10-30，非本轮 asset builder。实际查看原 piano reference、v2灰front/低角前缘及本轮全部9张彩色实图；manifest 12个文件的尺寸/SHA均核对一致。读取 color report、receipt 与 native-reopen-verification；不运行 Blender，不改资产或渲染。

**结论：本角色 GO，只进入一次同左食指、同白键014的按下回位试验。当前未见新增静态 motion/contact P0；不代表该试验已成功。**

- **键组不触发浮空P0：**无遮挡 front-edge 的暗缝仍细窄、连续，灰到彩色没有变成亮的贯通空层；rear 与完整front/3Q仍读作键组紧贴一体底座。侧面支撑也保持。这里通过的是视觉静态关系，未建立可制造的铰链、复位或键床机构。
- **手指/腕袖：**灰手、红袖口和蓝袖的边界更清楚，双腕连续且没有折断、拉长或脱袖；四指分叉与圆润掌形保持。左食指准备落点位于目标白键平顶区域，视觉没有挤到邻键侧棱；灰版render2 proxy的最低pad点X约0.057086m，距目标中心约0.227mm，normal +Z，悬停约2.905mm。它是准备位，尚未发生接触。不能由一个最低点宣称整个指腹、下压后的触点均留在平面内。
- **一次试验的前提成立：**当前姿态无需重新塑手或拉长手臂便可检验单指单键。完整帧保留猫、双掌、整琴和桌脚；具体键反馈仍很小，完整帧是否能读出这一下必须实际看运动，不能用手部裁图代替。原图8大键的易辨性差距仍在。

边界未变：native重开报告的pose `6a034f30…`、mesh/material、world矩阵与68键关系一致，仅旁路灰度；本评审读取该报告，没有自行重开native。接触数值继续来自render2匹配proxy，直接RENDER depsgraph缺口保留。约0.5275mm是固定014轴1.5mm扫掠相对case的Z分离下界，五截点不等于全组件连续安全；试验仍要检查手指同步和回位。

源white014/black010隐藏重叠59pair及末段具体pair变化、局部near-boundary分类和连续体包含性unknown继续保留，不能因数量不变豁免black组件。一次试验若出现确认的新非目标穿插、指腹离开平键面/跨邻键、袖口断裂、回位跳变，或只能靠整掌下沉/变形/遮缝才能成立，即STOP并保留失败。未知不能改写为零风险。

新增actions/keyframes0；同指同键完整下压/接触/释放、快连按、八键范围、浏览器实际输入/反馈、手机实尺寸、眨眼/头动均未验证。本次不签其中任何一项。

证据目录：`artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/`；接触旁证沿 `v2-keygroup-lift/lift-probe-receipt.json`。对应 builder report：`docs/research/miao-keyboard-v2-keygroup-lift-color-2026-10-30.md`。
