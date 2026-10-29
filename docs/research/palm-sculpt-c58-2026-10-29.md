# C58：C52 原拓扑上的拨弦掌局部 sculpt，未通过艺术门

日期：2026-10-29。本轮只编辑解剖右掌（画面左、音孔上方）。未编辑头、耳、左手、琴或独立眼脸；未创建新肢体、完整手臂 loft、体板、指柱、动画或 public 资产。

## 实际参照和固定方案

已实际打开 `public/character/instrument-scenes-v1/guitar/idle.jpg`、C49 彩色完整图，以及 C52 灰色完整正面图。原图的拨弦掌短、掌背圆、趾根自然连入掌；两道短而明确的趾缝读出三短趾。C49/C52 的远端迅速收成小尖帽，不能当作已批准的掌形。

唯一基底为 `artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend`，SHA-256 `630c27d7de8d94f0fb85201e0a216bb7055c223bb85b6d05b704fd6ba0ad40bc`。C52 是 297850 顶点的均匀 .010u authoring mesh，旧 C35 点 ID 均为 0；不能继承旧接触、UV、groom 或 rig pass。

先实际读取截面：以 `C=(-.58,-1.19,1.80)`、掌轴 `D=normalize(.78,0,-.625)`、横轴 `T=normalize(.625,0,.78)`，掌轴 s=.20u 时横宽约 .342u，s=.325u 时只剩 .028u。对应记录 `artifacts/character-palm-sculpt-c58/palm-sections.json`，不根据旧 ID 猜选区。

固定有限场作用于 C52 原有掌壳：末端 Grab 最多回收 .052u、末端横向扩张 14%、掌背向前轻膨胀 .030u、两个趾间轴向回收 .014u、最后 4 次 .20 加权局部 Smooth。原掌外形/前臂连接继续使用原网格，不向琴逐点投影。r1 两道浅缝深 .012u、半径 .022u；r2 仅把同两缝改为深 .026u、半径 .023u、掌轴中心 .215u/半长 .095u。恰好两候选，无扫描，之后停止形变。

## 实际看过的结果与尚存差距

每个候选均实际看过两张 512 完整灰图后再看掌部正面/3Q裁切：

- `artifacts/character-palm-sculpt-c58/r1-gray-front.png`、`r1-gray-three-quarter.png`、`r1-gray-palm-front.png`、`r1-gray-palm-three-quarter.png`。
- `artifacts/character-palm-sculpt-c58/r2-gray-front.png`、`r2-gray-three-quarter.png`、`r2-gray-palm-front.png`、`r2-gray-palm-three-quarter.png`。

完整前/3Q镜头沿用 C52/C49 镜头。灰图只临时将皮肤上下睑改为同 body clay，保留眼白、iris、cap 和全部部件；避免橙色眼睑经 luminance 变成伪亮边。此 override 不写入 native，所有独立物件原材质仍保留。

建模者观察：掌背比原基底稍丰满，小尖端被回收，前臂整体与主轮廓没有重建；但正面仅能看出弱起伏，3Q 仍几乎读作连成一团的手套，两条短缝没有达到原图的清楚三短趾。r2 没有解决这个关键差距，不能称“精致掌形完成”或“自然拨弦动作通过”。

**艺术状态：未通过，仍为局部技术研究。** 独立三角色实际图评审尚未完成；本轮不能替代它，也不能因此启动绑定和动画扩张。尤其“短趾清晰度”仍是明确缺口。整猫的原有头耳/左掌问题属于其他范围，C58 不修改也不宣称恢复。

## 合并和证据

r2 native：`artifacts/character-palm-sculpt-c58/miao-c58-r2-local-palm-study.blend`，SHA-256 `8c0c0250c79aec59eff64d7f77e1d66e5ace1dd0eabde98f516130d9f98e92e9`。`r2-C52-indexed-palm-delta.npz` 包含精确 C52 index+1、有限 edit mask、6668 个实际变化点、完整 delta；最大变化 .0588827133u。body 仍为单一连通 297850v/297848f，边界与非流形边均 0，所有 mask 外 body 点逐值不变。

新增 POINT INT 属性只叫 `C58 source C52 vertex index plus1`，值为 C52 原始 index+1。所有旧 C35 整数属性继续为 0，没有最近点身份伪造、重采样、重排、删点或补面。可用于父任务与耳/左腕增量检查范围，**不能用于授予艺术或接触 pass**。

构建 receipt：`r1-receipt.json`、`r2-receipt.json`；源代码 `design/character-sculpt-v2/c58/palm-sculpt-c58.py` 与 `palm-sculpt-c58-r2.py`。首次脚本缺少 bmesh import 在变更前报错，修正后才构建两个候选；不是额外几何候选。只用本机现有 Blender 5.2.3 LTS，每 agent 单进程；无外部服务费用。

新鲜几何审计另见 `artifacts/character-palm-sculpt-c58/r2-fresh-geometry-audit.json`：全部 94 个非 body 对象（包含隐藏 groom 的原始属性、灯和镜头）与 C52 exact；全身真实非邻接三角 self 75→75，新增 0，右掌局部 0；受影响三角 normal reversal 0。全身 75 个旧 self 问题仍在未改的左掌/右耳，不能当成整体通过。

**木琴接触也未通过。** 对 6668 个变化点的封闭实际木体三方向 parity 显示：rosewood body 内部点 53→53、spruce soundboard 内部点 103→103，虽未新增已确认内部点，原有木体穿入仍存在。另有少量混合 parity 记为 unknown，未偷算为外部；桥内部 0→0。实际 evaluated 木体与六根弦管三角相交明细均在审计 JSON，不使用旧 gate。不能把“未新增”写成“已恢复接触”。

未做动作、实际拨弦路径、连续碰撞、动态接触、手感、设备/web 验收；不得从静态形变推断自然动作。
