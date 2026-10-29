# C30 有效材质图：独立工艺窄评

2026-10-29；非 builder 工艺 reviewer，未参与资产构建。本次实际用 `view_image` 打开原图 `public/character/instrument-scenes-v1/guitar/idle.jpg`、C28 `artifacts/character-plush-readable-c28/controlled-native-run/render/same-bufferdenoised.png`，以及 C30 **`artifacts/character-plush-coherent-c30/material-repair/render/`** 内的 `same-bufferdenoised.png` / `same-buffernoisy.png`；读取该 material-repair 的 repair/render receipt。未用旧白屑失败图作本轮毛感判断，未改资产或渲染。

## 判断

**本次中心纤维软融合的改善不明显，不足以称干碎问题已修复；毛感 P0 保留。** 有效 C30 与 C28 在相同 512×409 crop 展示下很接近。中心仍有可辨认的短划与细碎点粒，保持 C28 已获得的纤维可读性；但没有清楚变成更连续、柔和、低对比的绒面。即便存在局部轻微排列差异，在这组图中也弱到不足以支撑“更软、更融合”的正面工艺结论。

该结论来自**已修改的 patch 中心本身**：短划仍偏干碎、部分像小刷痕／短屑，亮暗纤维没有融成原图细密柔软的表面。没有因为未修改的脸颊、口鼻仍光滑而否定该局部；上额纹理带与下脸的范围差异仍记为实验范围／P1，不能代替中心的判断。

| 实看项目 | C30 有效图观察 | 结论边界 |
| --- | --- | --- |
| 中心可读纤维 | denoised 仍能看到额头纤维短划，不只是 raw 噪点 | 保持可读性；未形成明确的柔软度增益 |
| 干碎／软融合 | 与 C28 非常接近，短屑与颗粒感仍在；未看见足以可靠认定的融合改善 | 不把微弱或难辨差异写成材质／groom 成功 |
| 白屑与材料有效性 | 本次有效图为橙／深橙的局部纤维响应，未呈缺材质的明显白屑层 | 按有效恢复原材质的结果比较；旧无材质输出不用于否定此次毛感 |
| 刺与边界 | 未见新的硬长针、明显浮起毛片或硬矩形边；纹理仍局限于上额 | 没有明显新刺感不等于软绒通过，亦非动态贴合证明 |
| raw | 中心短划伴随全图采样颗粒；虹膜、眼白、口鼻阴影亦有噪点 | 不把 raw 所有细点算作毛，不认定去噪是剩余问题的唯一原因 |

原图用于触感参照：其细绒与橙／奶油色斑柔和融合，面内细节连续，离散小亮暗屑不抢眼。原图为全身图、诊断为脸 crop，不据其尺度差推算物理毛长或密度；C28/C30 的直接比较使用相同大小 crop。

## 执行证据与未通过项

本轮指定变量为同 6674 根 patch 的 `.35` native Blend；根密度、长度、半径、shader 与灯固定。repair receipt 记录：只在既有 GN 末端用 Set Material 恢复原 C21 唯一材质；186125 条曲线实际 Material Index 均为 0，求值材质 node/input signature 与原材质一致，修复前后求值几何 exact，保存重开几何／材质保持。该记录使修复后的图可作为当前局部比较证据；恢复材质传播不是新美术材质通过。本 reviewer 未重跑这些工程校验。

**strict root exact 仍失败。** 当前材料修复继承的是 baseline-aware 差分诊断例外；任务记录的最大 root drift 约 `0.00012004px` 不作为绑定通过或肉眼无脱离的证明。repair receipt 同时明确 `strict_root_gate_pass=false`、`original_549_absolute_binding_pass=false`、`dynamic_binding_pass=false`、`production_pass=false`；本次静态工艺评审不覆盖或改写这些失败记录。

有效图来自一次 128 samples、seed 17 的 noisy/denoised buffer。额头 AOV mean 约 `0.13406466`（13.406%），与 C28 接近；它只是 hair AOV 抗锯齿覆盖估计，不能自动证明纤维软融合。旧失败与有效修复图均应保留原记录，不相互替代。

**本次净结论：恢复了可用于比较的有效材质图，但没有建立 `.35` native Blend 对中心干碎感的明确美术收益。** C28 的局部纤维可读性未丢失；C30 不能据此升级为软短绒完成或扩大到全身／动画。未验证动态、其他视角／光照、完整猫、Web 或移动端。
