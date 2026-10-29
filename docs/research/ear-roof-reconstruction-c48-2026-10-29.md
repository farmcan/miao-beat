# C48：完整头顶/耳根重建的两个失败候选

**结果：没有可合入的耳形优化，两个实际候选到此停止。** 第一个去掉了旧三角框，但额顶出现明显 V 字接痕；第二个试图接一阶导数，额顶变成高尖峰。两组实际正面全身、耳 crop、三分之四均已打开查看。它们是有冻结证据的技术研究，不能用 self=0、闭合或新网格较干净来描述为角色通过。

## 与 C42 的实质不同

C42 的斜切 `z+.5abs(x)>3.42` 只移除了上半耳；C48 先读取真实前后截面，将阈值下移至3.30。两个切面在头顶中心相遇，产生实际 **700 点单闭环**，局部范围 X≈±.561、Y≈-.356..+.416、Z≈3.019..3.30。新表面从这条真实共享环直接建起，重建额顶和两只短耳；没有在旧耳槽上再盖薄片，没有压原近共线三角，没有 body remesh。

源是 C38 最终 `head-expression-only/miao-c38-coupled-head-gray.blend`，SHA256 `f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439`。实际删31051源顶点；相对切面留 .01u 保护余量的头顶外全部保留。原眉眼、鼻口、琴与手全部独立锁定。

为恢复原头顶部位，用11367个排除旧耳污染带的实际源顶点拟合 degree4 roof chart，RMS=.005651u、max=.025731u。先做过 degree6 数值拟合，但 X6 外推在外侧上扬，因此没有采用它出候选。拟合样本和两种结果均保留。新耳目标 peak Z3.425、相对基部半宽约.11u、半深.10u，浅凹最大.018u；是共享新皮肤上的短圆三角形体，不是独立圆锥/耳片。这些是初始目标而非对原图三维测量的精确复原。

## 新共享 patch 与保护

使用 Blender 原生 `mathutils.geometry.delaunay_2d_cdt`，700个真实边界点、2293个新内部点、5284个三角。保留原边界点位置，不依赖 CDT 返回的近似坐标替换源点。尝试仅合并新生成切环点（2e-6u），实际700点一个也未减少；从未全局 merge 原皮肤。

全部保留源点使用 `Miao_C35_vertex_id = 原 C38 index+1`，所有新点 canonical=0，旧 `C23 source vertex id` 在新点也归零，避免 BMesh 对新边界插值出伪来源。另进程原生重开 `independent-readback.json` 确认两组：

- 93个其他物件的 mesh/curve 坐标和 world transform exact。
- canonical正值唯一，所有保留源坐标 bit exact。
- C35 的5359个新左手点全部保留 exact。
- 新点2993个，两个canonical/source字段均为0。

新毛发、UV、色块、rig没有重绑；不能把 C23 的0值新点范围当作“全是旧左手”。后续合并必须用新 canonical 映射识别，且所有接触证明需要重新评估。

## Candidate 1：只有 C0 的高度图表面

目录 `artifacts/character-ear-c48/candidate-1/`；原生 `miao-c48-roof-ears-gray.blend`，SHA256 `3a57fe876312d2297f83c84088a07d8d7877979e21c89cdf05f440bc022d9ded`。

按拟合 roof 和短耳大形生成 prototype，再用 screened-harmonic residual 精确贴原边界位置。实际新 patch 的 XY 有效、全部新面normal_z>0；head/ear self=0、nonmanifold=0、loose=0、正体积。但正面全身已能看见明显 V 字额顶边界，耳 crop 有斜向明暗分区，三分之四仍像接上的新头顶。内耳凹形也很弱，不能称与批准图对齐。**构造只保证 C0 位置连续，不能拿它声称光顺一体。**

## Candidate 2：一阶约束失败，不能把方程求解成功称为 C1

目录 `artifacts/character-ear-c48/candidate-2/`；原生SHA256 `63eec6d69ab8dc1ea30366407c385e1d85e31267a480270b449be65406c468f9`。

基于相同图/ear大形，增加真实保留皮肤边界 normal 推导的高度梯度，用本地 SciPy sparse screened-biharmonic residual 求解（878个一阶高度先验）。无服务调用，使用现有已验证隔离环境 `artifacts/c29-qp-env/bin/python`。方程 residual max5.54e-15，仅说明线性系统解出。

实际约束有严重反例：边界normal_z最低-.138，88个梯度被限制到12u/u；一阶先验高度残差RMS=.00703u、max=.06289u。最大校正达到.36445u。全身/耳 crop/三分之四均出现很大的额顶尖峰和多尖折边，比原图明显更差。self0/nonmanifold0仍不构成一阶接面通过，**C1及艺术门禁均失败**。

`geometry_gate=true` 是构建 receipt 中“闭合/self/正体积/新面朝上”的有限技术子门禁，绝不代表一阶光顺、整体造型或交付通过。事后评审分开保存在 `review-summary.json`，不改写冻结构建receipt掩盖错误。

## 真正的结构性限制

另进程回到原 C38，从切环最近16个原始源点的真实 normal 做逆距离平均，检查是否仅 bisect 单侧法线估计有错。结果源本身62/700点normal_z<0，最低-.136511，76点低于.04。典型位置为头局部(-.453,-.262,3.073)，原前侧额头在此有 overhang。此最近点查询只作法线归因，**不作为 source ID 或接触来源映射**。

因此该真实切环并非能用正向 Z-height graph 严格接一阶导数的边界。把负normal_z硬当+.04分母再限幅，掩盖了这一前提错误并造成尖峰；这不是增加渲染采样或继续平滑可以解决的。后续若继续同切环，应构建允许 XY 与 Z 一起移动的三维 surface patch，沿实际原皮肤切向/控制截面接出头顶，再生短耳；不能再只解 Z 图，也不能继承本轮有限数值 gate 为整体通过。

## 文件与边界

源：`design/character-sculpt-v2/ear-roof-reconstruction-c48.py`；本地稀疏求解器：`ear-roof-surface-solve-c48.py`。完整切环、拟合样本、实际执行脚本副本、两个实际原生文件、灰图、receipt、重开记录与manifest位于 `artifacts/character-ear-c48/`。两个输出目录有冻结保护；没有覆盖 C42 或 C38。

没有新增动画、着色成品、生产资产或网页发布。没有要求非 builder 用功能或数值平均替失败外观放行；此轮自拒绝不是独立三角色通过评审。
