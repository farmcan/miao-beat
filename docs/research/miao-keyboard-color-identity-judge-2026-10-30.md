# Keyboard 默认色 shaded static · 独立身份评审 · 2026-10-30

评审角色：identity / silhouette / expression，独立非 builder。只读并实际打开本轮八图和原 piano 图，没有修改 scene、script、姿态或渲染。灰阶段的初次 HOLD、有限修复和后续 GO 历史保留在 [灰身份评审](miao-keyboard-gray-identity-judge-2026-10-30.md)，本报告不覆盖它们。

**决定：shaded static identity GO，仅允许进入单键动作试验。** 当前实际完整静态中未发现阻挡这一步的新身份 P0；成熟 stock 猫的体积、可爱与完整双手具有继续复用价值。此 GO 不等于最终 Miao 外观通过，不等于动作／八键／网页可用，也不能独立替代 craft 与 motion 两角色的 shaded gate。

## 实际对象与证据边界

实际看过：

- 完整主图：[front](../../artifacts/miao-reuse-keyboard-v1/default-color/front.png)、[three-quarter](../../artifacts/miao-reuse-keyboard-v1/default-color/three-quarter.png)。
- 面部与双手：[face](../../artifacts/miao-reuse-keyboard-v1/default-color/face.png)、[left-hand](../../artifacts/miao-reuse-keyboard-v1/default-color/left-hand.png)、[right-hand](../../artifacts/miao-reuse-keyboard-v1/default-color/right-hand.png)、[hands-top](../../artifacts/miao-reuse-keyboard-v1/default-color/hands-top.png)。
- 支撑诊断：[support-side](../../artifacts/miao-reuse-keyboard-v1/default-color/support-side.png)、[feet-support](../../artifacts/miao-reuse-keyboard-v1/default-color/feet-support.png)。
- 原参考：[whole-piano-v3 idle](../../public/character/whole-piano-v3/idle.jpg)。

同读 [inspection-manifest](../../artifacts/miao-reuse-keyboard-v1/default-color/inspection-manifest.json) 与 [builder 静态报告](miao-keyboard-default-color-static-2026-10-30.md)。pose SHA 为 `4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be`，默认色 native SHA 为 `3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b`。本评审使用这些信息确定对象，未自行重跑 native／mesh 审计；hash 一致和重开 PASS 不作为艺术 GO 理由。

## 可爱、体积与精致度：可以继续复用，不是粗糙占位

1. **色彩让设计成为一套。** 灰毛／奶白脸、蓝飞行服、红护目镜和袖口、粉鼻与内耳彼此呼应；不是给粗灰块随意涂几种颜色。服装与手、脸与眼、键盘与桌面可以分层辨认，角色的识别性成立。
2. **立体感保留。** 3Q 中脸颊、头侧、圆袖口和手背仍有明确转面，服装躯干和尾部有体积；front 的图形化眼睛不会使整只猫退化为平面贴图。源作者的风格更接近成熟卡通玩具，不能按缺少原图长相就否定其设计质量。
3. **双手精度足够进入一个受控动作验证。** 两侧近景都能清楚辨认手指间隙、拇指、指腹和袖口；灰毛与红袖口的颜色分界帮助看清手腕连接。未观察到融合成拳、明显断手、破面或手指穿入键盘的静态 P0。
4. **完整场景可信。** 深色键盘落在木桌上，石墨腿与黑靴有共同落地关系。默认色没有重新引入灰初版的悬空道具问题；front／3Q 仍是完整连接猫、双臂双手及全键盘同帧。side 裁尾是诊断相机，不能作为完整生产帧输出。

这些是从图像读到的有限优点。当前比“只有可达数值或成功导入”多了真实整合结果，但仍不能概括成“原图级毛绒精致已经完成”。

## 与原 piano 的差异与 P1

| 维度 | 原 piano | 当前默认色 | 级别与影响 |
|---|---|---|---|
| 身份轮廓 | 短实梨形橘猫，宽腹、短脚、头身连贯 | 大头小身体的灰色飞行员猫、服装与靴子 | 明显模板身份变化；用户允许成熟模板，不要求重建原头身 |
| 神态 | 深色圆瞳侧看、闭口轻笑，温和放松 | 小瞳孔、大青色眼面、眉内侧压低、张口露牙 | P1：仍偏惊讶／绷紧，色彩让这一差距更明显 |
| 表面与边缘 | 细短绒、内嵌虎斑、柔和圆边 | 图形色块、简洁灰毛纹理、卡通服装与护目镜 | P1：可爱成立，柔软温暖程度和表面精致度仍达不到原图观感 |
| 乐器与场景 | 少量宽键、小木琴架，结构紧凑 | 长密键列、宽木桌与六腿 | P1：支持可信，但桌和细密键列增加画面负担 |

尤其需要保留以下观察：

- **青色眼面是画面最抢眼的区域。** 眼内大面积颜色较均匀，黑瞳很小，眼缘厚而干净，图形读感强于原图有浅体积的眼白与深瞳。这是现有默认设计的真实差异，不在本次无证据推断为材质错误或 rig 丢失。它没有构成不能做单键试验的 P0，但不能称“神态已优化”。
- 红护目镜和蓝服装使身份更像有性格的飞行员玩具；它们同时把观众注意力从手和键盘引开。后续产品尺寸必须实际看“手指动了哪一个键”是否可辨，不能由本轮高分辨率近景代替。
- 手指与袖口圆顺，但手背纹理和眼面仍相对简洁；与原图连续短绒的细腻度有差距。后续若需要微调，应先使用源模型支持的材质／表情能力，不开启自建毛团、头身重建或手部补丁链。
- 桌面宽于键盘，六腿和两片面板占了较多下半画面，原图更紧凑。当前没有挡住双手，也没有破坏支撑，因此保持 P1。

## P0 检查与有限签署

本轮实际图中**未发现新的身份 P0**：无缺眼缺口、无新破手、无完整主图裁断、无明显静态穿琴；旧承托 P0 仍保持解除。未见这些问题不等于宣称所有几何或遮挡已彻底审计。stock 继续复用的理由是当前整合图的实际表现，不是“源候选已经 GO”或某项 hash 满足。

**允许的下一步只有一个单键动作试验**，且须其余 shaded 角色门槛也放行。试验应保留完整猫、双臂双手、完整键盘同帧，实际证明准备位 → 一指触键／键行程 → 回到准备位；同时看整体猫脸与身体有无不自然漂移。当前静态只读成准备演奏，不是正在按下。

约 2.905mm 的皮肤间隙、邻键余量和无交叉沿用交接报告的 render-matched proxy；直接 RENDER depsgraph 捕获仍有缺口，不伪装成本评审新测量。静态间隙不批准整手下沉，也不批准八键动态安全。单键实际结果若出现穿透、断指、异常表情或明显邻键误触，动作继续 HOLD；不得以本静态 GO 冲掉新 P0。

以下均**未验证／未签署**：单键 press/release、邻键动态接触、循环自然度、八键扩展、头眼响应、网页输入到音画、真实浏览器及手机、最终 UI 尺寸、公开交付。吉他分支 FAIL／冻结不变。

**最终有限状态：默认色 shaded static identity GO → 单键动作试验；最终外观、动作与产品仍未验收。**
