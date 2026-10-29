# C28 短毛可读性：独立结构／接触／可动画性窄关

2026-10-29。Reviewer：独立非 builder `/root/c24_flow_structure_gate`。实际用 `view_image` 打开获准原图和 C28 noisy／denoised，阅读 C28 README、geometry/render receipt、实际执行代码。未改资产、未运行新 Blender、未扩研究；运行数值是既有执行记录，reviewer 核对逻辑及文件哈希，未重新求值 native。

## 结论

**C28 当前静态 root-aware 后置缩放结构成立，未见根绑定被本次长度操作破坏的证据；动态／完整角色关未通过。毛感 P0 保留，不扩整身或动画。** 当前短划更可读不等于原图连续短绒已建立，AOV 约 13.4% 也不是美术通过分数。

## 实看与视觉判断

| 图 | 路径 | SHA-256 |
| --- | --- | --- |
| 获准完整猫／爪／琴原图 | `public/character/instrument-scenes-v1/guitar/idle.jpg` | `4418fd737891283f42568306cb427b1f7604a86cae5513b1d6c49b3c31f338d1` |
| C28 denoised | `artifacts/character-plush-readable-c28/controlled-native-run/render/same-bufferdenoised.png` | `4350d7a46b615dfb4021b6b2711b41c02682bb206dfc1d945d1dec88c4ef1038` |
| C28 noisy | 同目录 `same-buffernoisy.png` | `3a7d7def1f966e2bef09ced128c3794f6e41cad78be0435ddb0856e2fd831c48` |

原图在头、脸颊、腹部及前肢呈连续、低对比的短绒面，短肢连接自然、持琴放松。C28 denoised 的中央额头已经能辨认细碎短划，局部颗粒／短纤维结构较明确；但仍像一条加了纹理的额头带，周围橘色脸部与奶油口鼻明显偏平滑，未形成原图整体一致的柔软面层。没有肉眼可见的新长刺、悬浮毛片或伸入眼表的粗毛；这种有限观察不能逐根证实接触安全。

noisy 图中眼白、虹膜和阴影也有噪点，因此不能把所有细点归为毛。两图来自同一次 128 samples、seed 17 的静态 render，不是时间序列。投影 polyline median 从约 `.97070px` 到 `2.34881px` 说明预设几何可读性目标被测得；额头 AOV mean `.13410594` 是抗锯齿 hair response，不能解释为“13.4% 美术通过”或严格覆盖率。**本 reviewer 未从实际图解除毛感 P0；整体猫当然未通过。** 原图与 crop 尺度不同，不据此推算精确目标毛数。

## post-D0／GN 顺序与根绑定

成功脚本加载同一 C26 native，仅追加一个 GN modifier。它位于已有 surface Deform 与 C24 Rotate 之后；用当前输入 geometry 的 point Index 减 `Curve of Point / Index in Curve` 得每根首点索引，`Sample Index` 读取该输入 geometry 的首点位置，再通过 `Set Position` offset 实现：

`P' = P + (P - own_current_root) * (scale - 1)`。

这是**对已经过 native 绑定和旋转的求值结果**进行绕根缩放，不是先放大 raw guide 再假定 D0 会保持同一支点。根位置由当前输入曲线即时读取，没有把本姿态根向量烘焙到属性中；保存的是每 curve 标量 `c28_length_scale`，没有新增独立毛对象或 Python runtime 依赖。

该公式在首点处 offset 恒为 0；正的每曲线统一缩放也保持该次已求值折线的方向。因此，在上游 topology／曲线属性映射保持的前提下，它有清楚的根不动结构依据。**这只能说明本 modifier 不应主动把上游根拉走，不代表 D0 本身、上游形变或最终毛流随动作都已实测通过。** 本轮没有切换 shape key、转头、闭眼或改变动画时间。

| 当前静态检查 | 记录与核对结果 | 解释范围 |
| --- | --- | --- |
| 零变化控制 | scale=1 时 raw source arrays、evaluated positions／既有 metadata bit-exact | 支持追加 GN 本身在单位倍率下不扰动当前结果。新增 scalar 属性是有意新增，不能写成属性集合毫无新增。 |
| 实际 cohort | 549 原 patch + 6,125 C26 新根，共 6,674；其余 179,451 根不变。307 原根和 4,683 子根达到 2.5x，其余由同一边界 fade 过渡 | 不是所有 6,674 根都恰好 2.5x，也不是扩整身长度。 |
| 根／patch 外 | 186,125 根位移全为 0；patch 外 717,804 点位移全为 0；总数仍 186,125 curves／744,500 points | 支持本次静态长度操作没有拉动根或非 patch 点。不是动态绑定测试。 |
| root-pivot 与属性 | 求值位置对 root-pivot 公式最大残差 `1.2106e-7`；绝对长度倍率误差最大 `5.7851e-5`；所有 source raw arrays、radius／rest／UV 及其他既有 evaluated metadata exact | 实际求值结果符合所声明操作；原始 raw guide 并未被改写。rest/pigment 属性保持本身不证明动态变形安全。 |
| native UV | 186,125 valid／0 invalid；求值根对 native UV lookup 最大差 `8.2262e-5`，小于继承容差 `1e-4` | 支持同状态表面 lookup 仍有效。该统计覆盖全部根，不能与 C26 只对新增根报告的小误差直接比较并声称恶化／改善；本次根相对 C26 实际位移为 0。数值单位沿场景，不擅自换算物理长度。 |
| 保存与渲染链 | 保存重开 evaluated geometry hash exact；reviewer 本轮核对 native SHA `2c3d90f6157d86f886965df6384907cc69e5e96a55da020d247f6c9aa8b20559`，与 render input 一致 | 支持当前姿态保存重开一致，不证明其他姿态或软件版本。 |

## 接触证据与尚未验证

- **皮肤当前检查比仅测毛尖完整，但仍有限。** 6,674 根 × 3 段 × 5 点（`t=.125,.25,.5,.75,1`）共 100,110 个法向间隙样本，最小 `6.80909727783785e-5`。每段另作 body BVH ray，记录 `body_segment_hits=[]`；为避免首点自相交，ray 起点略过 `min(1e-6, segment_length*.001)`。因此应称“当前样本为正、所测静态中心线段无 body 命中”，不能称包括根附近与纤维厚度的通用零碰撞。
- **眼部是指定当前网格的线段检测。** 新长度下 `eye_segment_hits=[]`，对象仅为可见 C6 sclera／iris、C7 clear cornea。未涵盖所有眼睑／眉毛部件、带半径毛束体积、毛毛碰撞，也没有闭眼／转眼过程。
- **动态根与毛流未验。** 后置 GN 即时读取根的结构避免了固定姿态支点，但没有 D0 随变形的时序结果，未验证滑根、拉伸、折向、头皮穿插或长度扩大后的动态间隙。静态断言不替代形变范围及极值验证。
- **全身和交互未验。** 实际 crop 看不到前肢连接、关节、按弦／拨弦行程、爪琴支撑或脚底接触；保存 native 含完整猫／爪／琴不等于 reviewer 看过该候选全身。没有眨眼、头部跟随、呼吸、快速输入、毛／去噪时序稳定性、浏览器或移动扬声器验收。crop 不是满足每个生产帧含完整猫／爪／琴的交付帧。

本轮未观察到可归因于长度操作的新静态结构 P0；这不抵消现存毛感 P0，也不把缺失动态证据伪装成已发现的碰撞缺陷。继续保留为局部技术诊断，不扩大根数／长度范围或动画。未来若独立静态质量关通过，动作关仍需同候选的完整猫／爪／琴与接触近景，以及最小动作范围内 root 随动、皮肤／眼接触和时间连续性证据；本 reviewer 未执行这些后续工作。

审阅输入：`artifacts/character-plush-readable-c28/README.md`、`controlled-native-run/receipt.json`、`render/receipt.json`、`controlled-native-run/executed-script.py`。失败的 raw-guide 尝试不是当前受评候选；README 明确其在保存／渲染前停止，且未记录残差幅度，不补造失败数值或原因。render receipt 的 unchanged 只覆盖构造后的 C28 native 到 render 阶段，不是说 C28 相对 C26 没有长度改动。
