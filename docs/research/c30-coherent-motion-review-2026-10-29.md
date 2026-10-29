# C30 材料传播修复：独立结构／接触／动作窄关

2026-10-29。Reviewer：独立非 builder `/root/c24_flow_structure_gate`。实际打开获准原图与 `material-repair/render/` 的 noisy／denoised，阅读修复 README、repair/render receipt、修复脚本、上级 strict receipt、engineering exception assessment／JSON 与 baseline-aware differential exception。未改资产、未运行 Blender、未扩研究；记录数值来自既有执行，本 reviewer 核对实现和文件哈希，未重新求值场景。

## 判定

**材料传播技术修复在当前静态诊断中成立；不代表 root 严格门槛、生产材质、柔绒或动作通过。** 修复恢复原 C21 材质的实际 evaluated 分配，且 groom 几何逐值不变，因此当前图可用来评审这个受限 C30 诊断。它没有修复原有根漂移、降低误差、重绑或重新放行 strict gate。整体猫未过，不扩整身或动画。

## 实际图与材料传播

| 图 | 路径 | SHA-256 |
| --- | --- | --- |
| 获准完整猫／爪／琴原图 | `public/character/instrument-scenes-v1/guitar/idle.jpg` | `4418fd737891283f42568306cb427b1f7604a86cae5513b1d6c49b3c31f338d1` |
| 修复后 C30 denoised | `artifacts/character-plush-coherent-c30/material-repair/render/same-bufferdenoised.png` | `a64ff8c40ffdf6db759026971e0ab8d5db948dbd02ccd2705e1e61ecb15ebd9c` |
| 修复后 C30 noisy | 同目录 `same-buffernoisy.png` | `60f7bd11811f924a8bca879312e14b99a9f36eddad033e39a67854816c82be7e` |

当前 denoised 中额头是细碎、偏干的短划／颗粒纹理带，未见醒目的白色碎片层；脸颊与口鼻仍显平滑。原图则有连续、低对比的柔软短绒表面。**当前修复图尚未建立原图连续柔绒，毛感 P0 保留。** 本轮未打开旧无效 white-fleck PNG，不据此作旧图与新图的直接视觉差分；旧图失效由 evaluated material table 为空及 AOV=0 的既有审计支持。noisy 眼、阴影也有颗粒，不把它们全解释成毛。两张当前图是同一个静态 render buffer，不是时间序列。

| 修复核对项 | 实现／记录 | 独立限定解释 |
| --- | --- | --- |
| 原因与最小修改 | 修复脚本先断言 raw materials 有唯一原 C21 材质、evaluated materials 为空；仅在现有 GN stack 末尾追加原生 `Set Material`，选择原 `C21 / short fiber native hair scattering` | 是恢复实际材料传播的实现修正，不是新 shader 参数候选，也未更改 Blend factor／radius。 |
| 实际材质身份 | 保存前验证 evaluated 材质 `.original==source`；其 node／link／input signature 与 source 相同，签名 SHA `5ee23487b2c1a67fba5b4e45dd62a154431be0114ac08a6c29446572f95b9043` | 比仅看槽名更强；没有把 Blender evaluated ID 副本误判成不同材质。签名是脚本所列节点属性／默认输入／连线的审计，不声称另做了外部纹理文件内容复算。 |
| 每根实际分配 | 临时 GN 用实际 `Material Index` field 在 CURVE domain 存储并读取；186,125 个值全部 0；随后移除 audit modifier／group | 支持全部曲线使用原唯一槽 0。没有因为显式 `material_index` attribute 缺失就判无材质，支持 Blender 的有效隐式零表示。 |
| 几何与旧属性 | 修复前后 actual groom coordinates bit-exact；原 raw／evaluated attrs 不变，geometry SHA `32c8e362c93e610f31159ca633e6058d13bd368a779cc5c16cbe995926644175`；body raw／evaluated、原材质 inputs 与灯不变 | 修复没有把根拉回、重采样或改变接触几何。它继承冻结 C30 的所有几何限制。允许新增材料分配不等于断言属性集合完全没有新增。 |
| 保存重开 | 重开实际检查 geometry hash、evaluated materials 名称列表及 source 材质 signature；修复 native SHA `256106a407e5ff24239d84e0a1b059b7f5baaa99308689097d628f5a9ac6d9b2`，与当前 render input 相符 | **代码并未在重开后再次运行完整 `.original` 身份及 186,125 个 Material Index field 审计。** 保存前完整审计与重开子集复验足以支持当前诊断链，但不扩写成重开后全部项目复测。 |
| 实际 render | 当前修复后一次 128 samples／seed 17 buffer；AOV forehead mean `.13406466`，非零；C28 记录为 `.13410594` | 支持材质 response 恢复及当前图可审阅。AOV 不是软度／质量分数，接近 C28 不能证明艺术改善。C30 历史另有一次无效 buffer，应如实计总共 2 次，不写成全过程只有一次 render。 |

最初用 Python pointer 直接比较 evaluated/source 材质而停止的检查，和后来正确使用 `.original` 的修复应分开。失败检查在保存／渲染前停止；不能把该次失败当成额外 render，也不能将技术检查修正写成艺术迭代成功。

## 严格失败与诊断例外必须保留

1. **Strict exact-root gate 仍失败。** C30 原生 Blend Hair Curves 在 6,674 根 patch 上的最大实际 root 位移 `2.4211522e-7`，非零。zero-factor root 为 0，但实际 factor `.35 * fade` 不满足 bit-exact root。它可能是浮点层面的微差；本 reviewer 不补造原因，也不从微小数值推出可见脱根。材料修复的几何 exact 仅指“相对冻结 C30 不变”，不是“相对 C28 根 exact”。
2. **第一次绝对绑定例外也失败。** 全 patch native UV error `1.4484243e-6` 超过 `1e-6`；C28 原 549 cohort 已为 `1.3270036e-6`。不能只取新增 6,125 根的通过值替代全 patch。上级 `engineering-exception.json` 的 `can_render=false` 与 strict 历史保持有效，不被之后的例外追溯改成通过。
3. **第二次 baseline-aware 例外只允许受限诊断。** 新 6,125 根 current UV error max `7.2020566e-7 < 1e-6`；原 549 根 positive error increment max `2.3865135e-7`，每根新增误差不超过其实际 root drift（加 `1e-12` 数值余量），同一 native UV reference bit-exact；全 patch 最大 matched-1024 漂移 `.0001200402px < .001px`；非 patch 点 exact。这个差分界控制的是新增加的误差，不证明继承的绝对误差已消除，也不等于所有根重新通过严格绑定。
4. **修复没有改变例外对象的几何。** 继承 frozen native 的完整 groom，未换 factor `.35`、root-merge radius `.0028111108` 或根位置。原始 native、strict／首次 rejection／baseline-aware 记录及旧无效输出保留。reviewer 本轮另核对三份关键历史 JSON 的 SHA 与 repair receipt 保存值一致。

因此应同时保留 `strict_root_gate_pass=false`、`original_549_absolute_binding_pass=false`、`dynamic_binding_pass=false`、`production_pass=false`。第二次例外和材料修复仅使当前受限图可评审，不能当作原门槛已通过。

## 接触与动作边界

- **当前静态接触证据继承有效。** 冻结 C30 有 100,110 个有限段内皮肤间隙样本，最小 `6.8068093e-5`、body／指定眼网格中心线段命中均 0；修复后几何逐值相同，因此这些几何测量无需被解释成“材料修复重新生成了安全毛”。它们仍不是带厚度纤维体积、毛毛碰撞或时间扫掠。指定眼对象也不等于所有眼睑／眉毛结构。
- **Blend 本身没有动态绑定证明。** patch 分离后才送 native Blend、非 patch bypass 并复序，支持静态范围隔离；native Restore Segment Length 的 pin-at-root 结构并没有在本次实际结果达成严格根相等。Blend Radius 是合并 root 点的距离，不是已经证明的最大邻居影响截断半径。邻居角度 mean／p90 变小而 median 变大，不能概括成所有毛流一致性全面改善。
- **后置 Set Material 不补足动态。** 当前材质身份／索引恢复不测试 D0 随 shape key、头动、眨眼、呼吸时的根稳定性或 pigment 时序；没有相邻帧及极值状态，也没有毛／去噪闪烁验收。
- **完整角色与 UI 未验。** 本轮实际图仍为脸 crop，看不到前肢、关节、爪琴握持与拨弦行程；完整 native 场景并不替代 matched-camera 整猫／爪／琴帧。浏览器连打、节拍、导出和移动扬声器未测，crop 不满足生产每帧完整猫／爪／琴要求。

本次认定技术修复成立，但保留严格根失败与毛感 P0，不称生产材质优化完成、不扩整身／动画、不发布。未观察到修复新增几何结构坏相；这不抵消继承的门槛失败，也不把尚缺动态证据说成已观察到的动态碰撞。

主要输入：`material-repair/{README.md,repair-receipt.json,repair-and-render.py,render/receipt.json}`；上级 `README.md`、`controlled-native-run/receipt.json`、`engineering-exception-assessment.md`、`engineering-exception.json`、`diagnostic-exception-baseline-aware.json`、`evaluated-material-audit.json`。上级 README 的“无 render”描述是 strict 阶段的历史快照，当前可审阅材料应以修复目录为准，不能据旧 README 否认后续已留痕的两次输出。
