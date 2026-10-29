# C59 真实窄腕带嫁接：全body self0；全琴接触仍未过

本轮完成一次真实连续body嫁接，保留C56耳修复、完整C35好左手5359点，闭合网格全身actual self0、winding0。实际图未见明显接缝。但扩测完整琴件发现原C35手中已有两根品丝穿入，保留body还有旧木/包边交线；**不能称全琴contact或角色通过**。原C52/C56/C35与C57历史全部冻结不改。

## 源与唯一候选

- body源：`artifacts/character-ear-sculpt-c56/gray-material-consistency/miao-c56-gray-skin-consistent.blend`，SHA `2af4802f996c61badb0883385d6be2048ec3f63494648042e11b0594ac9f463a`。有C56耳actual self0，且灰skin/lid材料一致；C52完整point顺序/拓扑相同，耳coords改动保留。
- hand源：C35冻结native，SHA `3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce`。本轮不借其旧pass代替新验。
- body在Y=-.70局部截开；hand保持原Y=-.72边界。原提议-.74会删除251个5359原点（含198根点），与完整保留约束冲突；root明确优先全部5359点，所以改用正宽 .02u带。
- 两实际环177/198点，单环、无分叉、XZ无严格自穿。按累计弧长单调zipper375个三角面，不凑相等点、不强拆奇偶、不做零宽桥接、不Manifold。
- 未应用fairing：所有保留C56 body点与全部5359原hand点保持bit-exact，连带只使用原边点，避免把contact区悄悄平滑掉。

## 真正一个body与provenance

输出291241v/291428f、582478 actual triangles，component1、boundary0、nonmanifold0、Euler2，signed volume6.4608020105。没有独立手对象或body/limb图层。

|来源通道|数量|含义|
|---|---:|---|
|`C59 C52 source vertex id` >0|285705|C56输入index+1，已证明ordered topology等同C52，coords保持修耳C56，不能还原旧耳|
|`C59 C35 source vertex id` >0|5359|真实C35输入index+1，范围585434..590792（0-based），不是nearest猜身份|
|两源ID均0|177|新body plane交点，另有实际原split edge/端点index/t/坐标证据|

两源ID在每个输出点互斥。`source-map-readback.json`独立打开两源/新native验证所有retained坐标exact、177个cut witness与最终点坐标误差0；头/耳z>2.5、全部x<0保留exact。C58候选右掌区域14800个源点全部在且exact。`exact-source-to-output-inverse.npz`有两个独立inverse map，后续可按明确source delta合并，不能coordinate-nearest，不能覆盖掉C56耳。

旧hand的点/面整数attrs保留，source face IDs另标。5个接触面同原cyclic顶点、原coords、原world target。所有独立可渲眼脸琴geometry/world/material/visibility与C56 exact。旧hidden `Miao / native short plush`已无有效binding，评估to_mesh会失败，明确排除geometry读取且一直hidden；不声称groom/UV/rig已恢复。

首次脚本在读取该hidden无绑定毛CURVES时停止，发生在body cut/接面/native保存前。改为明确记录排除项后执行相同唯一graft，原error log保留，不是第二个几何候选。

## 先看实际图

完整512gray front、3Q与腕侧crop均实际打开：未见C46式横唇、开口或明显P0接口，旧好手与sourcebody连接连续。这是builder观察，不替代独立三角色或整体角色艺术通过。完整两张含完整猫/双臂双爪/琴；腕crop仅内部诊断，不是production frame。

## 新的actual完整self与当前左手接触

同冻结native实际582478三角BVH，排除共顶点邻接后 **fullbody self0**；inconsistent winding edges0。zipper最小triangle area8.00515e-7u²，非zero-area。

左hand＋band＋proxim collar实际测全部可渲guitar件；wood/neck/fretboard/六弦tube交线0。四个木件对8622左皮肤点做双独立parity rays，inside0、ambiguous0。

五actual rays重新从当前body/current actual guitar测，world targets没动，命中的原C35 face一致，5个gap与原C35实测逐值delta0：

`[.0005280850455, .0020000813529, .0002730963752, .0019998277421, .0020001604571]u`

normal条件全>.2。严格名义0<=gap<=.002为False；原pure-fixed-C35-face已明确授权的positive-only2.5e-7u fp32上界容差为True。两项分开记录，不能写成严格<=.002，容差不覆盖任何真实穿入。

## 扩测发现：原C35仍有品丝穿入

C35早期gate只测wood和六弦，没覆盖所有实体品丝。本轮检测全部actual guitar件后，两根品丝各28对，全部来自旧hand region2，zipper无碰撞。

|实体|旧C35 face IDs|当前pair|原C35独立重测pair|max真交线spanu|max采样金属inside皮肤深度u|
|---|---|---:|---:|---:|---:|
|silver fret.002|585596 / 585756|28|28|.00277909|.00564051|
|silver fret.003|585755 / 585983|28|28|.00322252|.01171898|

56对全部edge/triangle真交线确认，不是切线。重新打开原C35测同实体得到相同28/28，所有碰撞皮肤原点在C59仍bit-exact；来源继承仅解释根因，不构成豁免。采样inside金属顶点深度是观测下界，不冒充连续最大穿透深度。4个碰撞face不是5个hit face本身，但与接触面共享若干点，后续不能假设随便平移四面就不影响接触。

原body region1还碰rosewood1391、soundboard550、两个continuous binding97/356对；旧hand/band对这些木/包边为0。没有对所有body点做global solid-parity，因为global surface已正数，不能称全琴通过。原body右拨弦/躯干问题、品丝穿入都仍block后续完整接触/动作门槛。

因此 `actual-graft-audit.json` 中：fullself0、左wood/six-string0、parity0为真实事实；`complete_body_all_instrument_surface_pass=false`，包含品丝的左contact工程总gate也False，`overall_character_or_animation_pass=false`。不能因原手被称“好手”便继承一个未测的pass。

## 冻结结果

- 新native `artifacts/character-wrist-graft-c59/miao-c59-c56-body-exact-c35-hand.blend`。
- SHA `efef0cfde423e567fe1af221d39c8bed27034df9f1bf4b630bd60b776d9de6fb`。
- `receipt.json`原建模/图证据，`actual-graft-audit.json`实际全self/琴件/5rays，`fret-collision-attribution.json`品丝源因，`source-map-readback.json`双源精确身份。各source/nativehash读回不变。
- 源码 `design/character-sculpt-v2/c59/`，统一manifest保存实际执行源码与所有证据。

这是一份**self0、可追溯且接缝目视合理的待修作者基底**，不是已通过整琴接触的完成角色。没有第二graft或新右掌shape；不修改5359原手去掩盖发现的品丝问题。新rig/UV/groom仍须重做，动画未扩展，无GLB、公开发布、部署或新增费用；不混进root的C49研究交接包。
