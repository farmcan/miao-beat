# C51：真实头部局部重网格的最低成本证伪

**这条方法比斜切耳/额顶补片有价值，但还没有交付人物。** 在实际 C38 头上只做一次.018u voxel remesh，然后保形贴源、局部浅耳变换与软边。实际渲染不再有 C48/C50 的 V 接缝、额顶尖峰和纵向折面，基本脸形/侧看保持。仍有耳底厚唇/框感、内缘工艺不足；临时分头的水平颈黑线是明确未焊接的 authoring 缺口，不能给生产。

## 方法边界

已读 `scenario-blender-retopology` 及 procedures。技能区分：自动 remesh 仅是 sculpt 起点，不能声称有合格眼/嘴/耳的变形环；不把顶点均匀或 self0 换算成可动画角色完成。

源为 C38 最终 `head-expression-only/miao-c38-coupled-head-gray.blend`，SHA256 `f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439`。在真实水平颈段 Z2.50 切下整个原头，临时闭合后只对此头做.018u voxel（原耳约.20–.25u高，11+体素跨耳），不是全身重网格，也不是换 primitive 头。

新头17468点/17466面。非耳区用原始实际头 reference、offset0 shrinkwrap保形；耳区在干净新拓扑上执行 C42 有截面依据的 Y 浅面变换，再一次固定3步局部.25软边。没有分辨率扫描，没有全头 relax；源独立五官、视线和身体下部保留。所有新头 canonical/source vertex IDs=0，不最近点恢复旧索引。

临时 `.blend` 的 head 是刻意分离的 authoring 对象。源下身体保留511918个原点 exact、C35新左手5359点全在。**尚未连接头/身体**，没有 UV、色块、毛发、rig或动画接受结论。

## 先纠正灯的接线再比较造型

首次灰图显示黑头，原因是原场景 Studio 灯使用明确物件 receiver collection，新头未加入。不能把该黑图当作外观改坏的比较。只补 `C7 original studio receivers`：74→75物件，光能/相机/几何/材质不变。

实际原生重开确认新头几何等于原构建最终坐标，positions SHA256 `a3a549cd66fee769d17f46296fe47b2db391ded4d9bc07336db6f2412de110c0`，头/身体同为 `C23 gray body`。补灯前 `.blend` SHA256 `279291f23831b6f95bacf5a1b2d3864f87e6fe8506e62d4e675ed3f5ff9e3e03`；补灯后 `lighting-repair/miao-c51-authoring-light-repaired.blend` SHA256 `c9674828e3bd82cd2de21d2d46907241369e7c36ed6f32dacacf9d498f4c9bda`。

**只用 lighting-repair/ 下的灰图作有效造型比较。** `gray-front.png`、`gray-ears.png`、`gray-three-quarter.png` 均已实际打开，root也已实际看过front。旧黑头图保留为接线诊断，不覆盖失败历史。

## 实际几何与重开

`independent-readback.json`：

- 93个原有其他物件的 mesh/curve/CURVES位置和world transforms exact。
- source body正 canonical 唯一，全部对应原 C38位置 bit exact；C35新左手5359点全保留。
- 620个新颈环点 canonical=0；旧 `C23 source vertex id` 在这620点仍是 BMesh 插值值，**不能作为来源依据**。下一 connected 步应全部清零。新头则所有canonical/source IDs都已0。
- 新头闭合、self0、正体积.668825u³。34932个实际 renderer三角对所属polygon normal反向=0，最小面积6.97e-8u²。
- 非耳14220新顶点到原实际表面的p95误差1.24e-5u、最大.003382u；不说整个新头几何exact。原始voxel到保形贴源最大修正.004473u。
- 眼白可见内部顶点 L2114/R2117；贴源头后的最小前向净距分别+.001654u/+.001447u，遮挡点=0。只是静态可见白眼内部检查，不证明眨眼、眼睑、鼻口与表情动画。

## 下一步

冻结此一次 authoring 对照后，单独做水平颈环连接：真实源body环与均匀新head环接为一个连续skin，允许颈段非常窄的双侧共享带公平化并明确释放旧ID集合；眉眼、下脸远端、双手与琴锁。不要把焊颈和耳工艺再次修改混成同一个候选，先得到 connected 全身灰图再安排独立身份/工艺/动作三评。

此轮局部耳框仍未清 P0，整体人物身份/工艺更不因拓扑研究而通过。源脚本 `head-retopology-c51.py` 和 `head-retopology-c51-lighting-repair.py`；完整本地证据与manifest位于 `artifacts/character-head-retopology-c51/`。没有生产资产或网页发布。
