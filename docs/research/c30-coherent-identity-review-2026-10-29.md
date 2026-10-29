# C30 有效材质图：身份与柔绒风格窄关

2026-10-29。独立非 builder reviewer：`/root/c24_fiber_identity_gate`。本次只判断 `.35 × 原 fade` 邻域形状 Blend 在 patch 中心是否带来可靠的软融合收益。未改资产、未运行 Blender、未扩研究或浏览器验收。

## 结论

**修复材质后的 C30 可以用于这次视觉对照，但没有显示相对 C28 可靠、明确的柔软融合改善。** 实际打开两张 denoised 图后，额头中心仍是非常接近的短划/细碎颗粒面层。局部排列或细碎明暗有轻微区别，不能稳定据此认定纤维更柔软、面层更连续或更贴近原图。

**C28 的局部可读短纤维进展保留；C30 未在此基础上建立新的风格收益，柔绒 P0 继续保留。** 中心本身仍偏干、偏粗，短划与微颗粒容易分别被读出，尚不像获准原图的细腻、连续柔绒。这是 patch 中心的判断；周围未修改区域仍光滑不作为本轮局部无效的理由。

未见明确新增的长针束、毛刷轮廓、硬切矩形边或明显角色身份回退。“未出现明显新坏相”不足以证明 `.35` Blend 有有效收益，也不能解释为本轮通过。

## 实际图与来源边界

先逐张 `view_image` 实际查看：

| 图 | 相对路径 | 本次核对 SHA-256 |
|---|---|---|
| C28 denoised 控制 | `artifacts/character-plush-readable-c28/controlled-native-run/render/same-bufferdenoised.png` | `4350d7a46b615dfb4021b6b2711b41c02682bb206dfc1d945d1dec88c4ef1038` |
| C30 修复后 denoised | `artifacts/character-plush-coherent-c30/material-repair/render/same-bufferdenoised.png` | `a64ff8c40ffdf6db759026971e0ab8d5db948dbd02ccd2705e1e61ecb15ebd9c` |
| C30 修复后同 buffer noisy | `artifacts/character-plush-coherent-c30/material-repair/render/same-buffernoisy.png` | `60f7bd11811f924a8bca879312e14b99a9f36eddad033e39a67854816c82be7e` |
| 获准原图 | `public/character/instrument-scenes-v1/guitar/idle.jpg` | 本次实际打开；原图身份沿用同一文件 |

看图之后读取 `material-repair/repair-receipt.json`、`material-repair/render/receipt.json` 与该目录 README，并检查严格根失败/例外记录的相关字段，以确认比较是否有效。原先丢失求值材质的白屑图**不进入本次软硬、颜色或改善判断**，也不作为“C30 曾经更差”的艺术候选。

按修复记录，末端增加一个原生 Set Material，恢复原唯一 C21 hair shader；全部 186125 根材质索引为 0，求值几何相对冻结 C30 bit-exact，原 raw/evaluated 属性不变，body/material inputs/lights 保持。这里的“材质修复有效”是所读执行证据；本 reviewer 没有独立重新求值 native，不能将它升级为完整工程复审通过。

## 中心纹理对照

| 项目 | C28 与有效 C30 的实际观察 | 结论 |
|---|---|---|
| 短纤维可读性 | 两者都能辨认红橘额纹及两侧橘色区域的短划/颗粒组织；C30 没有回到 C26 那种主要是点的状态 | C28 进展保留，不是 C30 新增收益 |
| 邻域软融合 | C30 可能有很细微的短划排列变化，但在原生 512×409 图上没有稳定可辨的更连贯绒面或更柔和纤维层 | **未证实可靠软融合收益**；不以几何协调数值替代视觉判断 |
| 中心的细腻与柔软 | C30 中心仍显细碎、略干粗；可辨短划没有充分融为柔软的连续面层 | 仍低于原图细密柔绒，核心 P0 保留 |
| 颜色/额纹 | 当前有效 C30 图的短纤维保持橘色/红橘额纹，未见显著白屑或新色层割裂 | 当前比较可读；恢复原材质是实现修复，不能算 `.35` 形状 Blend 的美术改善 |
| 刺感/边界 | 未见明显新长刺或硬切线；局部额头纹理带仍存在，周围未改属实验范围 | 有限无新增坏相；最终面层一致性仍未验 |
| noisy 对照 | 中心组织在 denoised 后仍存在；noisy 的背景、眼与阴影也有采样噪点 | 不把 raw 颗粒当更多柔绒，也不从 noisy 图推导软融合更好 |

修复后的额头 hair AOV mean 为 `0.134064659`，约 13.406%，与 C28 `0.134105936` 接近。AOV 是抗锯齿 hair response 估计，不是柔软度、连续度或美术分。这个近似不变也不能代替看图判定“必然同样”或“已经通过”。

## 阻塞、数值例外与未验范围

- **视觉 P0 保留：中心未形成原图的细密柔绒风格。** 本轮不能称“软融合改善完成”，更不能据此扩全身或动画艺术交付。
- **P1：最终 patch 与全表面的风格一致性未验证。** 未改脸部的光滑状态是实验范围，不用于否定中心；当前也没有全身绒面可供最终过渡验收。
- **工程状态单列：严格 root bit-exact 仍失败。** 所读修复记录中 `strict_root_gate_pass`、`original_549_absolute_binding_pass`、`dynamic_binding_pass`、`production_pass` 均为 false。baseline-aware 例外只许可同一冻结几何的有限诊断，原严格失败、首次绝对阈值拒绝记录继续有效；它未通过原 549 根的绝对绑定误差，也不是根修复。
- 数值根漂移不被本评审写成实际可见脱皮；未见可见脱离也不能反向通过严格根门。工程例外与视觉 P0 不互相抵消。
- 旧 C21 眼仅为控制；C20 独立通过但未合并，不记为 C30 新改动或本关依据。
- 仅验固定正面 crop、灯光和尺寸。未验全身/侧后表面、完整猫/爪/琴同帧、其他光线/相机、持琴接触、动作/变形、Web、移动端或生产。整体猫未过。

本报告只完成身份/风格独立窄关；不代替材质工艺/灯光与运动/接触的其他独立角色结论。
