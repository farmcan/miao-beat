# C38 / C40 / C34 独立动作结构与接触审查

2026-10-29。角色：独立非 builder 的 motion / 接触 / 整帧体验审查。三个 scope 分开判定，未修改资产、脚本、审计或 public；未运行 Blender、扩展外部研究、制作动画或测试浏览器。

**整体结论：HOLD，未通过整体 gray gate，也不进入动画扩展。** C38 的共同头脸方向调整、C40 的左肩根柔化和 C34 的底层材质隔离，各有可保留的局部研究贡献；它们没有组成一只已经通过审查的猫。静态形体 P0、C40 的几何未知与未制作动态分别保留，不能相互抵消。

## 实际查看与证据边界

本轮用 `view_image` 实际查看批准原图 `public/character/instrument-scenes-v1/guitar/idle.jpg`，以及：

- C38 最终 `artifacts/character-alignment-c38/head-expression-only/gray-front.png`、`gray-face.png`、`gray-three-quarter.png`。没有用 failed / repaired / soft-ear 试验图替代最终结果。
- C40 `artifacts/character-shoulder-c40/read-only-left-shoulder-front.png`、`read-only-left-shoulder-three-quarter.png`（C31 原形体）与 `diagnostic-left-shoulder-front.png`、`diagnostic-left-shoulder-three-quarter.png`（C40 同机位结果）。
- C34 `artifacts/character-plush-substrate-c34/controlled-native-run/render/same-bufferdenoised.png`。

阅读 C38 最终 `receipt.json` / `independent-readback.json`；C40 `receipt.json`、`matched-left-crop-receipt.json`、`separate-readback.json`、`parity-interpretation-readback.json`、研究文档及 README；C34 `controlled-native-run/receipt.json`、`render/receipt.json`、`saved-material-audit.json` 和 README。还读了 `c35-gray-motion-review-2026-10-29.md` 与 `c36-overall-motion-review-2026-10-29.md`，用于保持已有局部接触结论的真实范围。

这是独立图像与证据审阅，**没有独立重算几何、接触或 UV 审计**。native 身份以相应 receipt 为准：C38 `f481e8a0…ca1c8439`，C40 `6dbc4183…a8bdc00`，C34 `503bfb6c…8bf782e`。裁图是作者诊断，不能作为生产面板或分件动画资产。

## Scope 1：C38 头脸方向与整体动作基础

### 有用的静态贡献

最终正面与脸部图中，瞳孔、眼白、鼻口及头部方向能一起读出向画面右侧的注意力，不是只在正面脸上移动两颗黑瞳。三分之四中五官仍在同一张脸上，未见明显额头分界条、颈圈或五官被隐藏的补救做法。眼白的边缘相比旧评审描述的凸环问题显得较浅，但本轮没有重看旧图做逐像素对照，因此不以此量化“改善幅度”。

从动作设计角度，这个共同方向是可用的静态起点：将来可围绕一小段乐句维持注意力，而不需要每个音符把头归零再点头。此处是动作方向建议，**不是已经实现头随动**。

readback 支持眼、睑、鼻仍可见，既有顶点 / 面 / 材质身份保留；没有用隐藏眼睑消除可见问题。它还支持 C35 5359 个新手点及广义双爪锁点保持，其他 scene objects 的几何、矩阵保持。故不因本轮整体未过而重新声称原左手出现了五目标悬空或已证实穿琴。

### 仍阻塞整体的静态 P0

**P0-A：头脸下半部与肩部之间仍是较长的直立壁面。** 参考中圆方脸很快收进饱满梨形上身，侧望由眼神、眉与柔软面颊共同表达；C38 从嘴下到肩的面积仍显长、平直，完整三分之四也没有消除这个读法。小幅头随动若直接发生在这段壁面，可能强化“整段上筒弯折”的感觉；这是静态结构暴露的风险，未观察到真实变形失败。

**P0-B：耳朵仍保留硬三角内槽和厚口沿。** face 图足以看到深腔、近直壁与明显转折；receipt 的 `actual_ear_softening_max_delta=0` 与此一致。这不是无毛灰模的扣分，而是现有耳体的几何读感。共同转头不等于耳部工艺已修复，未来耳动也不能自动解决静态硬槽。

**P0-C：肩臂与右拨弦爪仍未形成参考的短厚、连贯动作结构。** 这里的右爪指猫自身右侧、画面左侧。正面可读出肩根到上臂的圆口 / 套接，三分之四更明显是一段水平短管接到粗前臂。末端爪仍像长圆封帽，两条刻痕不足以解释短趾体积；它表示“手在琴前”，尚未给出清楚的短掌缘 / 趾端触弦意图。参考则由短肘、厚爪和琴身遮挡组成一条连续软体弧。

直接用当前长掌整体摆动，可能使拨弦看成整段前臂扫动；环形肩根也可能在转动时更像插接关节。这些是可动画性风险，**不据投影断言穿弦、确定悬空或真实动作已经失败**。C38 明确未处理右臂 / 右爪，不能把其它尚未并入的候选写成已修好。

### 眼睑与动态判定

圆形开眼与共同侧向头姿比“只有眼珠偏移”更有表达基础，但仍是静态开眼。当前脸图没有证明上下睑可以贴合、覆盖眼球并在闭合时维持自然弧度；三分之四也没有闭眼样本。眼白前后排序、眼睑可见、静态没有显著凸圈，都不能推出眨眼不会穿插或变成硬罩。

**C38 判定：方向性局部贡献成立；自然眨眼 / 头眼随动未制作、未验；整体 gray gate 不通过。** C35 的静态 hold 仍仅限已声明冻结姿态、局部实际审计与授权正间隙 fp32 边界；strict nominal false 不能消失，也不能推广到全身碰撞或连续握持。

## Scope 2：C40 猫左肩根，同机位诊断

### 实际视觉差异

原 C31 的左肩在琴颈后是圆穹顶与环状阴影，并不是右臂那根完整水平管。C40 matched 正面中这一段阴影略平滑，三分之四中肩根与躯干之间的转折稍软，未见为了补形而多出一个肩球。差异是局部、轻量的；圆穹顶读法仍在，琴颈遮挡也使肩根的完整深度关系看不清，不能据两张裁图宣布肩已经自然。

手指、掌体与琴颈相对位置在 matched 图中保持同一静态意图。readback 支持所有 C35 ID0 点、硬锁、非编辑区、右侧 `x<=0`、头部 `z>=2.40`、整数来源属性及其它 scene objects 保持。故这一项有“柔化左肩根且保留既有静态持琴”的局部价值，但并未处理右拨弦侧，更不是双肩整体修复。

### 几何证据不能越级

receipt 记录实际局部 self 从 18 对降至 0、新增 0，实际 mesh boundary / nonmanifold / inconsistent winding 均 0；54 个 evaluated 琴部件与编辑面交对为 0。这些支持明确的局部进展，不是连续实体或动态碰撞证明。

必须保留 parity 的完整解释：626 个实际候选三角探针中，**606 严格正确、20 双方向不一致、0 双方向一致 wrong-side**。20 个是未解决的未知，不是已证实 inside-out；同样，self0、winding0 和正 volume 也不能把这项 strict gate 改为通过。`geometry_gate_passed=false` 继续有效。

**C40 判定：轻微局部视觉贡献可记录；几何 HOLD；左肩完整艺术 gate、整体 gray gate、shaded still 和动态均未取得通过。** 本轮不靠其它 scope 的改善平均掉该未知，也不把 C40 与 C38 当作已经整合的同一 native。

## Scope 3：C34 额头底层材质、UV 隔离与动态边界

### 静态路由与隔离证据

实际 denoised 图仍保留橙色 / 奶油色与额头虎斑，没有把上游红色布料 Base Color 带入；额头可见较细碎、颗粒状的局部纹理和短纤维。它说明这次材质能在指定局部产生可见表面变化。图中下半脸和额头局部的表面读感并不统一，未达到参考全脸连续、短而柔软的毛绒感；仅额头裁图也无法证明整身材料一致。

receipt / saved-native audit 支持复用真实 CC0 velour 节点图，且只声明两项颜色适配：原 Miao 色输出接入 Base Color、Sheen Tint 改为中性白；非颜色反射结构与参数保留。此处是证据审阅，没有重新联网核验许可证或上游文件。

独立 `C34_CoatXZ_3u` 明确供底层图像、Normal Map 与 Tangent 使用；原 `UVMap`、`BindUV`、active/render UV 及 hair binding 仍保持。186125 curves / 744500 points、根 / 长度 / 半径、raw 与 evaluated 属性、毛材质及身体几何 bit-exact 的 readback，支持**该固定静态候选中底层材质路由与毛绑定隔离**。它没有改变毛本身，也不是毛发质量提升的证据。

### 不能从静态隔离推出动态合格

Factor0 是结构上的原 shader identity，未渲染像素一致对照；hair AOV 是覆盖估计，不能当柔软度得分。当前一张 denoised crop 不能签署短毛自然度、光照全角度稳定、整身一致或材料 craft 通过。

新 coatUV 的静态隔离也没有证明变形后无拉伸、无滑动、无接缝、无闪烁；旧 BindUV 未改只说明本轮没有改写它，不保证后续把 C38 / C40 形体并入时仍能不经验证地复用。没有动态帧证明毛根能跟随头、耳或肩，也没有动中材质传播证据。

**C34 判定：固定局部底层材质路由 / UV 隔离有保存后证据；毛感与 shaded-still 艺术 gate 不通过认证，动态未制作 / 未验。** 不将上游材质能力写成 Miao 已实测能力。

## 可执行的后续门槛

先在同一完整灰模中解决长下脸 / 耳槽 / 肩臂与右爪的可见 P0，并解决 C40 parity 未知或采用另一个取得明确几何证据的方案；不以材质、毛或渲染采样掩盖它们。整合后的 native 是新候选，需同机位完整正面 / 三分之四、脸与双爪近景及实际手琴目标重新验收，再由三角色独立评审；不能从几个局部候选拼出“整体通过”。

静态整体及 shaded still gate 真正通过后，才有条件制作最小动态证伪：单次完整眨眼、小幅乐句级头眼跟随、右爪短行程拨弦与回位、左手持续保持接触；逐帧检查完整猫 / 双爪 / 吉他同帧、形体体积与绑定稳定。这里只定义未来验收范围，**三个候选的实际动态均未制作 / 未验证**，没有真实按键音画或网页体验通过声明。
