# 最后一次 Wing It + 儿童尺寸六弦布局 · .55 FAIL / 持琴链冻结

2026-10-30。依据独立 motion 的一次 .55 证伪 GO，执行一个整体候选 + 一轮有限体测量修复；已查看同姿势 front、3Q、face、左右手全部5图。**最终仍 FAIL；冻结当前 Wing It 持琴链，不追加同分支缩放/角度/卷指/美化/动画。** 后续应转向胸前空间、臂长/掌琴比例更适合的成熟模板；不据这次整合失败贬低源资产工艺，也不重造源几何。

## 交三评的实际文件

根目录：`artifacts/miao-reuse-v1/child-electric-static/`。

- `child-electric-front-NOT-ACCEPTED.png`、`child-electric-three-quarter-NOT-ACCEPTED.png`。
- `child-electric-face-NOT-ACCEPTED.png`、`child-electric-left-hand-NOT-ACCEPTED.png`、`child-electric-right-hand-NOT-ACCEPTED.png`。
- `child-electric-static-native36.blend`、`child-electric-static-receipt.json`。
- `right-exit-reach-readonly.json`、`inspection-manifest.json`。
- 脚本：`design/miao-reuse-v1/scripts/build_thin_electric_child_static.py`。

官方 portable3.6.23 factory / disable-autoexec。输入 source / 已恢复脸 native / clean GLB SHA 前后相同；cat与prop base mesh hash 前后相同；new actions=0；没有运行上游 embedded scripts / MoveAI addon。各 render helper 均按原表达式同步 camera 世界 Euler 到 helper 局部，逐轴误差全0。所有旧证据保留。

## 唯一 .55 缩放与真实面重算

整琴143组件统一 .70→.55，**pivot为真实 clean Body canonical bbox中心** `(0,−.10480186,.26866618)m`。先保该中心的旧 world 锚点 `(−.12676747,−.23264736,.26391664)m`，再从缩后Body与 evaluated 腹部重算贴靠；最终中心 `(−.12661085,−.22938834,.26348624)m`。统一缩放无非均匀变形，颈仰20°/面上抬8°、躯干姿态和正确原生 palmar roll 保留。

腕没有沿用旧 world点。左取真实 `Head / Neck` 的 canonical z=.80低把位截面：实际前/背 y=−.12674457 /−.10351455m，背侧保源手26mm皮肤余量；右取真实 Spiral 六弦 z=.31–.35区，实际最前 y=−.13444896m，外侧保源手22mm余量。缩放后手皮肤余量仍以物理米计算，没有随琴偷偷缩手。

## 哪些门这次确实改善

| 修复后的真实指标 | 左 | 右 | 既有硬门 |
|---|---:|---:|---:|
| 肩腕 reach / 源两段臂长 |69.7200%|94.3856%|≤98%|
| 实际腕目标误差 |.000030mm|.000064mm|≤.2mm|
| 肘屈曲 |91.5867°|38.5689°|≥20°|
| 腕弯折 |25.0067°|24.9993°|≤40°|
| 原臂段 pose/rest 误差 |<1e-4|<1e-4|不拉臂|

两侧关节/腕可达指标通过这次静态布局门，不能继续把本次失败写成“右手仍伸到100%”。头与腹部对完整琴的 triangle overlap 和有限 solid inside 采样均0，解除旧 .70 的已测头部交叠；零命中不单独当完备无碰撞证书。

## 为什么仍必须拒绝

每侧205个真实核心皮肤顶点、374个核心三角，非空。交叉检查覆盖完整143组件，inside检查使用真实有限Body/Head-Neck局部截面，不是无限支撑半空间。

| 核心 / 全局拒绝证据 | 初始 | 一轮修复后 |
|---|---:|---:|
| 左核心 overlap / inside |553对 /4点|**327对 /2点**|
| 右核心 overlap / inside |1857对 /52点|**1857对 /52点**|
| 前臂/袖 GEO-arms overlap / inside |2019对 /40点|**2019对 /40点**|
| 衣领 GEO-collar overlap / inside |173对 /3点|**173对 /3点**|

左按有限颈体 inside点执行一次11.590mm背侧退出，仍有2核心点入颈，最近侧最大深度约5.560mm。右真实有限体退出需要22.252mm，超本轮20mm局部修复域，未执行；对实际肩腕数据只读计算，该退出目标会达 **102.331%** 原两段总臂长，因此也明确违反原臂空间，不只是预算差2.252mm。没有继续补第二次修复。

最终左/右全手 inside 2 /53点；右核心最近侧最大深度约11.022mm。碰撞结果拒绝已成立，不用“可达性变好”抵消。原 Thumb1 XYZ确实未锁/无约束，但核心P0未清，**finger_updates=0**，未进入左CMC/食指接触或右拇指3mm hover；不能写拇指本体无解，也不能写已完成手势。

## 实际看图与停止

完整图里琴已明显缩小，六调音钮、弦/品、桥/摇把仍能辨认；但右大掌遮住了大部分拾音/拨弦区，琴呈小玩具读感的风险更强。左手近景直接显示琴颈进入掌根，右掌仍摊在琴上、袖口跨面；并未形成自然抱持。脸的嘴/眼保持恢复，没有旧白三角或嘴消失。整体图与数值共同 FAIL，不依赖隐藏角度或对P0均分。

该一次 .55 假设证实了“缩小能改善头净空与右腕可达性”，也证伪了“只靠这次比例/有限退出即可形成自然持琴”。本 builder 不自判最终三评；将完整图与native/receipt交三非builder复核。当前 Wing It 持琴链按本轮明确停止条件冻结，不再追加此分支第N种参数。keyboard并行路线未触碰。
