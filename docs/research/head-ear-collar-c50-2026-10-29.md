# C50：XYZ collar 两个大形与一次共享带修复，均不通过

本轮换掉 C48 的固定 XY 高度图连接，使用真实源切环、boundary tangent×skin normal 的无除法 co-normal，XYZ 都可移动的 Hermite collar，再接 source-fitted roof 和短圆浅耳。所有 front/ears/three-quarter 实际灰图均已打开。**依然没有可合入的耳形优化。**

源仍是 C38 最终 `head-expression-only/miao-c38-coupled-head-gray.blend`，SHA256 `f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439`。同 C48 实际双斜切3.30，700点共享头顶环，移除31051个源头皮点；没有原近共线耳三角压缩，没有独立耳片、custom normals或全身 remesh。耳峰初始目标Z3.425，几何浅凹最大.018u，独立眉眼鼻嘴、身体下部、琴和手保持。

## 两个大形候选

1. `artifacts/character-ear-c50/candidate-1/`，native SHA256 `f8edcb8ce224336093541fddc474e38f27b814dab0bdf2868902316f632649f4`。内环取外环 XY 的.94倍，6个真实中间截面。没有 C48 高尖峰，但 XY 内移太窄、局部高度差达到.324u，实际额顶仍有 V 接痕和纵向小折。实际闭合头审计 self6，6个实际三角相对所属 polygon normal反向。拒绝。
2. `candidate-2/`，native SHA256 `9a75f5673401fffd488c45cdab104c3419e4862945abcbcc21238d01ab4ce8c3`。内环改.78倍、8个截面，耳峰包含在较宽的三维 collar 中，沿 collar 后部渐变进入统一 roof+ear 函数；外端初始t=.025、内端t=.95捕捉实际离散切向。V带/细折仍可见，self24，16个实际三角反向。仍拒绝，未出第三个大形候选。

## 明确授权的旧/新双侧共享带修复

根允许适度释放旧切环两侧少数皮肤，避免把不合适的旧边界位置视为不可改的艺术标准。对 candidate2 只做一次 C25 同型40步 Taubin .45/-.47，共享拓扑双侧各3个邻接层。声明的旧源点2054、新点2798；旧/新位移上限.012/.025u，实际旧最大.005650u、新最大.005814u。

目录 `candidate-2-shared-band/`，native SHA256 `ec964e0e1e08140f5b7f0c967f1119c9da6d41eed879e7384909ca77094680e7`。声明释放的全部 canonical IDs、距离、before/after 保存在 `declared-release-map.npz` 和 `actual-displacements.npz`。不再声称所有 retained 源点位置 exact；**只对明确释放区以外保留 bit exact**。所有其他93个物件和 C35 新左手5359点仍由独立重开确认不变。

实际完整灰图中 V带、左侧细折仍留，工艺不通过。相同闭合头 probe self24→17，但实际三角反向16→18；不能以 self减少描述为修好。body/闭合头的 nonmanifold=0、loose=0、shared-edge winding一致、正体积只证明有限技术子项，无法抵消自交/折面。没有再扫平滑迭代或位移参数。

## 重开与真实三角审计

`artifacts/character-ear-c50/independent-readback.json` 从实际保存文件重开：

- 三组各93个其他物件的 mesh/curve 坐标及 world matrix exact。
- canonical正值唯一，新点 canonical/C23 source ID全为0。
- candidate1/2全部 retained 源点 exact；共享带修复除明确2054源点释放集合外 retained 源点 exact。
- C35新手5359点全部保留 exact。
- 相同闭合头 probe self分别6/24/17；实际 renderer loop triangles 相对 polygon normal 反向分别6/16/18。没有用 polygon winding一致偷换“所有实际三角都朝外”。

前期构造 receipt 明确将 self 后置至实际大形看图之后；没有把未做的技术检查预填为通过。其 `source_tangent_conormal_dot_min=0` 只是局部正交式的一个统计，不能当成全部切向质量证明。

## 可复用与停止条件

真实 source cut/canonical 锁区与无除法 co-normal 构造可用于方法研究，但不能合入已拒绝的整体形象。连续函数两端的导数相切，不等于离散网格整条带没有折面，也不等于艺术上不见接痕。沿细密旧斜切环反复补 collar 的路线到此停止。

没有上色、毛发/UV/rig重绑、眨眼或头动动画、生产资产或网页发布。构建与修复脚本分别为 `head-ear-collar-c50.py`、`head-ear-shared-band-c50.py`。完整实际源、灰图、原生文件、映射、执行副本、失败审计和manifest保留在 `artifacts/character-ear-c50/`。
