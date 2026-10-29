# C26 局部加根：独立结构、接触与可动画性窄关

2026-10-29。Reviewer：独立非 builder `/root/c24_flow_structure_gate`。本次实际用 `view_image` 打开获准原图及 C26 同 buffer noisy/denoised，阅读 C26 README、geometry/render receipt 和对应执行代码；未修改资产、未运行 Blender、未扩研究。以下运行数值来自既有执行记录；本 reviewer 核对实现逻辑与记录链，未重新求值 native 场景。

## 判定

**足以认为 6,125 个新根在当前静态姿态中已接入实际 native 表面绑定；不足以声称动画绑定或通用无碰撞已通过。毛感 P0 继续保留，不足以扩整身／动画。**

这不是只声明存在 D0、或把新毛平移到看起来贴皮肤的位置：代码为各新根建立独立的实际三角形／重心坐标／BindUV，并通过现有 native modifier 求值，再与独立 `Sample UV Surface` 查询和预期实际 body 位置交叉比对。保存重开后求值几何一致，进一步支持它不是仅在临时内存中成立的散点。但是所有检验仍发生在同一静态形变状态，没有主动改变 shape key、头部／眼睑或动画时间。

## 实际视觉证据

| 图 | 路径 | SHA-256 |
| --- | --- | --- |
| 完整猫／爪／琴原图 | `public/character/instrument-scenes-v1/guitar/idle.jpg` | `4418fd737891283f42568306cb427b1f7604a86cae5513b1d6c49b3c31f338d1` |
| C26 denoised | `artifacts/character-plush-coverage-c26/controlled-native-run/render/same-bufferdenoised.png` | `f813278683b6ae0f148870e8344765a971b27e57871da4935fc28780531375f4` |
| C26 noisy | 同目录 `same-buffernoisy.png` | `08ecd6f150db7ea5477b48a4b4a449749993a671656a13a5f61f081154f53494` |

原图的头、脸颊、腹部和前肢有连续而低对比的短绒表面，肢体短、握琴放松、猫与乐器同帧。C26 512×409 denoised 的中央额头可见细碎点状纹理，但其读法仍偏局部颗粒层；脸颊、口鼻和大面积橙色表面依然平滑，尚未形成原图连贯柔软的短绒。没有从这张 crop 看到明显新长刺、大块悬浮毛片或毛伸进眼表，但单图不能逐根验证亚像素间隙。noisy 的颗粒也遍布眼和阴影，不能全部算作短毛。

额头 AOV mean `.05862566`（约 5.86%）是抗锯齿 hair response 估计，不是柔绒评分、严格几何覆盖率或动作质量。`fraction_over_half=0` 也不能单独定义成功／失败。**本 reviewer 的实际图判断没有解除毛感 P0；绑定数值成立与美术成立是两项不同验收。** 原图与本诊断尺度不同，因此不据此推算精确毛数或密度。

## 新根是否真正绑定：证据核对

| 核对点 | 已有证据与代码行为 | 可得结论／边界 |
| --- | --- | --- |
| 实际 surface 与坐标空间 | 代码断言 `hair.surface==body`、`surface_uv_map=='BindUV'`，hair/body matrix 均为 identity；原 C24 native 输入 SHA 为 `430b5a9be23c8806bc584df9c71e9d0a6d63a8dfbea95d2db27b4f3e13c0a875` | 支持本场景使用正确表面和一致空间；没有用屏幕贴图代替 native 根。未覆盖未来变换／重拓扑的场景。 |
| 每根拥有自己的锚点 | 在实际 evaluated body 三角形内按面积提案；新 UV 来自该三角形的真实 corner BindUV，经 FLOAT2 量化后解码重心坐标，再构造 raw／actual／pigment 根。最小解码重心权重 `.02008778`；新根数据持久化到 `new-root-binding.npz` | 不复用父根 UV 或父 pigment 根。避开边界并在量化后回算，降低此静态状态的三角边界误差。raw、evaluated 和 rest 同索引三角形的对应关系在当前网格上有结果交叉验证；不证明未来 topology 改变仍有效。 |
| native 查询与实际求值相符 | `Sample UV Surface` 对全部 186,125 curves 报 186,125 valid／0 invalid；新根 lookup 对预期实际 body 最大误差 `4.1325e-7`；实际 evaluated root 对预期最大误差 `6.8514e-7`，对 native lookup 最大误差 `4.9332e-7` | 不仅 UV 可解析，实际求值后的根也落在同一预期表面位置；这是“当前静态绑定已建立”的关键证据。查询属于同一 Blender runtime 内另建查询路径，不是外部软件复算。 |
| 形状复用的边界清楚 | nearest existing guide 只用于短毛 offsets／半径 profile；绑定 UV、实际根、pigment 根另算。保留既有 native surface deformation 与 C24 rotate；新增根沿对应三角形切向给方向 | 不是把父根作为新根的绑定锚点。`miao_rest_position` 用于 pigment 连续性，其存在本身不是变形绑定通过证明。静态方向也没有验证动作下随皮肤转向的正确性。 |
| 原有毛未改写 | 180,000 原毛 raw 与 evaluated attrs bit-exact；720,000 原 evaluated 点位移全为 0；body/material/lights/source 保持 | 支持本轮隔离成局部加根试验。不能因旧资产没变，就宣布旧接触、旧形象或旧动画问题均已通过。 |
| 保存后仍成立 | `native_reopen_evaluated_geometry_exact=true`；输出 native SHA `4174110cea7294427973b7516f04cdc1da64ab5e1e8179c28611b61b32842a92` 与 render input 相同，reviewer 本轮另核对文件 SHA 一致 | 支持保存重开后的当前求值位置复现；没有测试换帧、变形或其他 Blender 版本。 |

新增后共 186,125 curves／744,500 points。原短毛半径 profile exact；raw 长度相对误差最大约 `6.98e-6`、evaluated 长度误差最大约 `.000321787`（0.0322%）。这支持没有有意增粗／加长，但不能把误差写成完全零变形或未经过 native deformation。

## 接触与运动证据的限制

1. **皮肤：静态抽样通过，连续／动态未验。** 73,500 个样本正好是 6,125 根 × 3 段 × 4 点（`t=.25,.5,.75,1`），最小带符号间隙 `8.696876673042198e-5`。代码对当前 evaluated segment 抽样最近表面法向间隙；不是段间连续带厚度扫掠，也未覆盖时间。根端 `t=0` 由绑定位置误差另行约束，不在这 73,500 个间隙点中。不擅自把场景单位换算物理长度。
2. **眼：限定表面的静态中心线无命中。** `eye_segment_hits=[]` 来自新增毛各折线段对当前可见、命名为 C6 sclera／iris、C7 clear cornea 网格的 BVH ray cast。没有验证闭眼、眼转、眉毛／眼睑全结构，也没有带毛半径体积或毛毛碰撞检查；不能写成“眼部零碰撞、眨眼通过”。
3. **变形绑定：当前有活动 C8/C14 shape key 的姿态能对上，并未运行状态变化。** 没有新旧 shape key 值之间的响应、插值、极值或时间序列。因此缺少滑根、掉根、毛流折转、拉伸、皮肤穿插的动态反证。D0 结构和静态有效 UV 都不自动补足这些证据。
4. **完整身体和演奏接触：未验。** 实际受评图只有脸部 crop，看不到前肢连接、关节、按弦／拨弦行程、爪琴接触与脚底支撑。native 保有完整猫／爪／琴是构建记录，不等于 reviewer 看过 matched-camera 全身与接触近景。
5. **时间与交互：未验。** 同 buffer noisy／denoised 是一次 128 samples、seed 17 的静态渲染。没有眨眼、头部跟随、呼吸、快速连打的时序效果，没有毛闪烁／去噪跳动检查，也未验证浏览器、导出或移动扬声器。此 crop 不满足生产每帧完整猫／爪／琴的交付要求。

## Gate 处置

本窄关承认 C26 已取得**当前静态 native 新根绑定的具体证据**，不把它降格为只有标签或只有贴皮位置。但毛感 P0 仍保留，动作／接触 gate 未通过，不扩全身根数、不扩动画、不交付为角色美术完成版。本轮未见能归因于新增根的明确新静态结构 P0；缺失动态证据也不伪装成已观察到的碰撞缺陷。

后续只有在独立静态身份／工艺关通过后，才适合以最小变形范围验证同一候选的 root 随动、皮肤／眼接触与时序稳定性，并取得完整猫／爪／琴的匹配相机证据。这些是尚欠的验收条件，本 reviewer 本轮没有执行或扩展。

审阅输入：`artifacts/character-plush-coverage-c26/README.md`、`controlled-native-run/receipt.json`、`render/receipt.json`、`controlled-native-run/executed-script.py`。renderer receipt 中的 unchanged 描述仅指已构造 C26 native 到 render 的阶段，不把它误写成 C26 相对 C24 未新增毛根。
