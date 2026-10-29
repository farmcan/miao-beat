# 2026-10-29 · 对齐进展的独立整体身份评审

评审角色：独立非 builder，负责整体身份、轮廓与表情。实际打开下列现有图像进行目视比较；没有修改模型、源代码或资产，没有生成新候选，也没有外部研究。采用 `scenario-blender-expert` 的“实际看渲染、发现问题先阻断下一阶段”原则。

**总判断：整体未通过。** C38 有可用的表情与低眼凸方向，C40 有可用的左肩局部软化贡献，C34 保留了 Miao 色彩与已有毛。但这三个独立实验没有合成为同一个验收对象；任何局部改善都不能抵消整体 P0，不能描述为“已经像原图／可爱精致完成”。本评审没有把灰模缺少毛色当成几何否决理由。

## Scope 1 · 批准原图 → C36 repaired → C38 最终 head-expression-only

实际图像：

- 身份基准：[批准的 guitar idle](../../public/character/instrument-scenes-v1/guitar/idle.jpg)。
- 对照：[C36 repaired 正面](../../artifacts/character-alignment-c36/repaired/gray-front.png)。
- 唯一被评审的 C38 最终目录：[`head-expression-only/gray-front.png`](../../artifacts/character-alignment-c38/head-expression-only/gray-front.png)、[`gray-face.png`](../../artifacts/character-alignment-c38/head-expression-only/gray-face.png)、[`gray-three-quarter.png`](../../artifacts/character-alignment-c38/head-expression-only/gray-three-quarter.png)。没有以 C38 根目录、repaired 或 soft-ear 图代替它。

### 可保留的局部贡献

1. **头与视线的侧向意图更连贯。** 相比 C36 正面，C38 鼻口和眼部朝向不再完全正对镜头，画面右侧的注视方向更明确，有一点“留意身旁”的轻快感。它接近原图的侧看意图；但仍未达到原图那种放松、带好奇心的神态，不能称表情已经匹配。
2. **白眼的突出球感下降。** C36 正面眼下较明显的球形阴影和附着感减弱，C38 正面轮廓更干净；这是有用方向。降低眼凸并不自动等于“眼睛已经嵌入”。
3. **大轮廓保留一部分身份线索。** 宽下腹、细短四肢、弯尾、怀抱斜向吉他仍能让人读到同一个设计目标；没有因为局部调整完全丢失梨形猫的类别和基本姿态。

### P0 · 整体身份阻断

- **耳朵仍是硬、空、独立的三角框。** 正面与脸 crop 的耳沿像厚塑料框，下缘出现横向搁板，尤其画面右耳；三分之四视角还出现向外突起的折片读感。批准图是短小、圆钝、自然从头部生出的耳朵。这里即使加毛也不能替代耳根与外轮廓的结构修正。按给定变更范围，耳改形停用、只随 yaw；本轮不能记作耳 P0 已处理。
- **下脸—肩—身体仍是一段偏长的直立体块。** 原图的圆方脸有清晰但柔和的下边界，面颊短而饱满，很快落入肩部；C38 鼻口下仍有较长的无特征面，侧边近乎竖直，再向两肩外扩。正面像高筒上接宽梨体，三分之四视角更明显。问题不只是没有奶油口鼻色块：灰模本身的下脸长度、脸颊体积及肩部过渡仍使身份显得更长、更端正。
- **整只猫仍未形成原图的松软、短实、一体感。** 硬耳、长下脸与两侧可辨的臂根构件一起出现；从全身先看，仍像“可爱的猫灰模抱吉他”，没有达到“就是这只 Miao”的程度。这是组合后的整体判断，不能用某个眼凸值或单一轮廓指标覆盖。

### P1 · 明显风险与待修差距

- **新 flat-eye 风险：** 脸 crop 中白眼变成边界非常干净、近乎平贴的白圆片，深色瞳孔也偏图形化；上、下睑和眼眶之间缺乏足够的软包裹关系。批准图的眼白仍有浅体积、转面和眼缘张力。应保留减凸方向，同时避免从“外贴球”走到“贴纸眼”。本轮只能确认凸出感减弱，不能确认眼嵌入完成。
- 眉形较小而硬、嘴鼻仍很居中和简化，面颊的饱满承托不足；眼神更明确，但还偏警醒、规整，少了原图的温和机灵。
- 下腹底沿偏平、画面右下腹有较明显的鼓块转折；批准图更连续圆润，重心也更自然落在短腿上。
- 小脚仍有收细踝部与小鞋头的读感，三分之四视角尤明显；原图脚掌更宽、短、厚，脚趾和腿的衔接更自然。此项不会因灰材质自动消失。
- 两臂根和圆管上臂仍可辨，抱持姿态有基本可读性，但尚未达到原图那种“短肢自然长在绒体上”的松弛感。C40 的局部实验不是此 C38 图的一部分。

**本 scope 决定：P0 未清，整体身份 gate fail。** 可保留“轻微侧头／侧看、降低眼凸”的方向作为后续输入；不进入身份完成、着色通过或动画扩张结论。静态图不能证明眨眼、头部跟随、手指接触稳定或网页交互。

## Scope 2 · C40 左肩根的窄范围比较

实际同相机图像：

- 原 C31 左肩：[`read-only-left-shoulder-front.png`](../../artifacts/character-shoulder-c40/read-only-left-shoulder-front.png)。
- C40 诊断候选：[`diagnostic-left-shoulder-front.png`](../../artifacts/character-shoulder-c40/diagnostic-left-shoulder-front.png)。

**目视结论：左根连接确实更软，局部贡献可保留。** 原图在琴颈上方有较明显的半球状肩包和弧形明暗边界；C40 中这块肩包的顶端不再单独立起，肩斜面更连续地接到上臂，环形／插接感减弱。这个差别无需依赖 self-intersection 数字也可看见。

仍有 P1：斜肩到琴颈上方的外轮廓有折点；琴颈遮挡下的上臂、前爪仍有圆管／椭圆独立件的读感。此正面 crop 不能说明别的视角、另一侧肩、全身轮廓或运动时也更好，亦不证明按弦接触已经自然。

**技术阻断继续保留：** 本地 [`parity-interpretation-readback.json`](../../artifacts/character-shoulder-c40/parity-interpretation-readback.json) 记录 626 个实际三角 probe 中 606 严格正确、20 个方向不一致而未知、0 个一致 wrong-side，`geometry_gate_passed=false`。本评审不把这 20 个未知写成已证 inside-out，也不把局部 self0 写成全局几何通过。

**本 scope 决定：局部视觉改善成立；整体和交付均未通过。** 可记录为“左肩根圆包／环影减弱”，不能继承为 C38 的改善、全身软化完成或可发布资产。

## Scope 3 · C28 forehead → C34 真实 velour 底层

实际 denoised 图像：

- [`C28 same-bufferdenoised.png`](../../artifacts/character-plush-readable-c28/controlled-native-run/render/same-bufferdenoised.png)。
- [`C34 same-bufferdenoised.png`](../../artifacts/character-plush-substrate-c34/controlled-native-run/render/same-bufferdenoised.png)。

本地 [`provenance.json`](../../artifacts/character-plush-substrate-c34/controlled-native-run/provenance.json) 记录底层来自 Poly Haven `velour_velvet`、CC0-1.0，并记录原 Miao 色输入替换源红色 diffuse、Sheen Tint 变中性。这里仅使用已有本地来源记录，没有重新联网核验许可证。

**可确认的保留项：** C34 仍读成 Miao 橙色与额头虎斑，没有把整块变成来源材质的红／粉布；已有细短毛仍可见。它证明现有材质可在保留角色色彩与已有毛的前提下做局部底层比较。

**目视结论：没有确认比 C28 更接近批准图的软绒。** C34 在额头中部与虎斑周围增加了更密的深浅颗粒／斑驳，局部“有纹理”更明显，但方向、连续性和微观柔软感没有相应建立；更容易读成粗颗粒的织物底层。C28 更平滑，仍有塑料／蜡面的风险；C34 并未清楚解决这个问题，而是给它加了局部颗粒。

### P0 / P1 与适用边界

- **P0（用于完整角色交付时）：** 本图只是额头诊断 crop，不能证成完整角色的柔软材质 gate；Scope 1 的身份 P0 完全没有被本材质实验解决。不能把“真实 CC0 velour”或“毛数不变”换算成“全身精致软绒已通过”。
- **P1（局部观感）：** 颗粒对比偏显眼，额头中间像一小带不同粗糙度的区域；批准图的短绒是较细、连续、贴合体块的表面，并非只在额心出现的噪点层。局部 softness gain 不成立。
- 可复用贡献仅限来源／颜色适配与受控比较方法。此实验不宜按当前观感扩到全身；需要的不是先把更多区域铺满再求整体通过。

**本 scope 决定：色彩与已有毛的保留成立；软绒艺术 gate 未通过。** 未评估全身、侧背面、动画闪烁、距离缩小后效果或浏览器生产资产。

## 下一步判断边界

仍先解决身份层面的耳形、下脸与肩身整体关系，再确认减凸后的眼睛能否有自然软睑承托。C40 可作为局部方向，但必须保留其未过的几何门槛；C34 不应仅因来源可信而扩到全身。只有实际同一候选的全身、脸与爪部在匹配相机下通过独立评审，才可谈下一阶段。三个 scope 的局部好处不加总成整体 pass。
