# v2 键组整体抬高 · 独立灰静态 motion/contact 评审

2026-10-30。非本轮 asset builder；不运行 Blender、不改 scene/script。本次实际查看原 `public/character/whole-piano-v3/idle.jpg`，以及 `v2-keygroup-lift` 的全部9图：front、three-quarter、face、左右手、key-rear、key-front-edge、feet-support、support-side。manifest 的11个文件尺寸与 SHA 均核对一致；另读 builder report 与 lift-probe-receipt。

**结论：本角色 GO，仅允许这一个冻结姿态进入默认色三方静态复审；未发现本轮新增的静态 motion/contact P0。不是按压、动画或浏览器 GO。**

- **前后缘：**低角 key-front-edge 确实露出一条窄、连续的暗缝，读作键组与壳体间的净空，不像整体漂离底座。key-rear 的白键边与控制台仍形成紧凑关系；front/3Q 与 side 中没有明显“键盘悬浮层”。因此本次不触发预先约定的浮空 P0 STOP。该结论来自这组灰图，上色后仍须重判，不能据此声称实际机械支撑已建成。
- **手与关节：**双腕从袖口连续伸出，没有新增折腕、细颈或被袖口截断的读感；肘到掌仍放松。四指形体和分叉清楚，左手对中后准备姿态没有明显侧歪，掌面未压进黑键/壳体。约2.9mm是准备悬停，不能称已接触或已按下。完整front/3Q仍能看清双手在琴上方的关系，桌面、脚与阴影支撑保持。
- **UI：**整体角色、双掌与乐器可读；细密68键中辨认具体目标键仍弱于原图的8个大白键。本次抬高和对中没有解决这一既有缺口。中央8白键仅占全琴宽约18%；缩至手机显示后，不能只依赖细微指尖/键位位移表达输入。网页实尺寸、8键映射/高亮均未验证；近景可看清不等于完整UI可辨。

数字仅作旁证：左目标pad位于平顶（normal +Z），gap约2.9047mm，邻键最小投影gap约5.8891mm；右目标约2.9128mm。全手/袖对有限组件交叉0，与图像未见新增穿插相符。固定014轴1.5mm扫掠的 case-Z 分离下界约0.5275mm，只针对该case界限；五个截点不等于其它组件的全连续碰撞证明，也未驱动手指同步。

**保持未知：**几何来自 render2 匹配 proxy，未获得直接 RENDER depsgraph。源 white014/black010 仍59 pair，末段有1个新增pair/1个退役pair；局部近边界分类及连续体包含性 unknown 保留，不用总数相同豁免。真实铰链/键床机构、触点随按压的移动、完整 down/contact/release、重复或快速输入、八键范围、支撑后动态、网页均未制作或未验证；新增actions0。

下一步只评同pose默认色。若颜色/阴影使前后缝读成浮空、腕袖断开或手掌穿插，按P0停止；不加遮片、不扫高度、不继承旧pose的通过结论。

证据：`artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift/inspection-manifest.json`、`lift-probe-receipt.json`；builder说明 `docs/research/miao-keyboard-v2-keygroup-lift-gray-2026-10-30.md`。本次冻结pose SHA：`6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b`。
