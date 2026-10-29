# C40：猫左肩根的同一候选与未过门槛

2026-10-29。**仅内部几何 / 视觉诊断，`geometry_gate_passed=false`。** 没有完成艺术优化，不进入颜色、动画或发布。原右侧水平管状上臂由 C39 独立负责，本 C40 对 `x<=0` 的所有点逐位锁定。

## 参考、修区与范围修正

已实际查看批准原图 `public/character/instrument-scenes-v1/guitar/idle.jpg`，C31 `gray-front.png`，C36 repaired `gray-front.png` / `gray-three-quarter.png`，并阅读 C36 三角色整体评审。原图需要的是短、软、嵌入躯干的肩臂，不是给身上再加一个球或新肩 mesh。

任务最初为双肩；初始只读 preflight 尚未改几何时，root 将猫右侧（`x<0`）肩以下完整划给 C39，因为该侧需要琴后负空间 / 连续拓扑重建。因此 C40 在**实际候选前**改成只处理猫左肩 `x>0`。初始双肩只读计数保留在 `artifacts/character-shoulder-c40-preflight.log`，不将其写成双肩修复。

进一步出两张 C31 原几何左肩诊断图：`read-only-left-shoulder-front.png` / `read-only-left-shoulder-three-quarter.png`。实际观察：左侧没有右侧那根完整水平管，主要是在琴颈后方有近圆形穹顶 / 环状阴影；不能将右侧的严重结构问题直接投射给左侧。对这一处只尝试一次连续表面公平化，判断能否柔化圆隆起和环边。

source 是完整 C31 native，SHA `13cbb1da83dfa23c0581ccfe7c07e893b9d0bca6a63244887ad0955f7d0c9c5d`。它与 C35 同拓扑并保留已审查的手部。未复用已拒绝的原始 primitive 建模来生成新肩，也未加独立肩 / 臂网格、改材料遮盖、hide 旧管或全局 remesh。

实际可编辑原表面点 22112 个，原坐标范围：x `.420139..1.199934`，y `-.691217...158768`，z `1.830035..2.399977`。以下不变：

- 所有 `C23 source vertex id == 0` 的 C35 5359 点。
- 猫右侧 `x<=0` 全部，`z>=2.40` 全部。
- 右 distal 的原显式锁，以及低臂 `y<=-.72` 或 `abs(x)>=1.10 && y<=-.50`。
- 非修区、琴、腿、尾、梨形腹及所有其他 scene object 的 geometry / matrix / visibility。

`deformation-evidence.npz` 给出 changed indices、source IDs、前后坐标、全部 hard locked indices、4725 个 C1 过渡带点索引及前后 coefficient；整合须按这些精确来源处理，不使用 nearest。

## 同一 field 与两次实现修复

采用原 connected skin 上的局部图扩散公平化，固定 **240 步、lambda .45**。空间系数 C1 渐消；局部 normal correction 补偿扩散失去的体积。它不是重建一个新球，原顶点和面结构不变。全身 volume 是 sanity check，不能由其正值推出所有法线正确。

1. 原 field 在**写入 mesh 前**触发预设 `.09u` 最大位移门槛，未保存 native / 出候选图。保留 `initial-unbounded-field-failure.log`。
2. 实现修复 1：用 `.09*tanh(displacement/.09)` 平滑 enforce 原 `.09u` trust region，未放宽门槛。该次仍被几何挡住；固定原 triangles 追踪显示 77 个方向反转、局部旧18 self→1但新增1。保留 `fixed-triangle-proxy-failure/` 的数据和日志。
3. 只读定位明确新增 pair 跨在既定低臂硬锁边；原18对 self 集中于左腋两小区 x≈`.804..840`、y≈`-.537..-.471`、z≈`1.865..2.007`，均为原 C8 retained source 点，非 C35 新点，不在低臂 hard lock 内。`baseline-self-localization.json` 留存具体 vertex/source IDs。法线追踪问题集中在 `.773..1.249 / -.675..-.471 / 1.825..2.166` 原肩 / 腋褶带。
4. root 明确授权实现修复 2：在**相同硬锁之前**给 diffusion coefficient 增加 C1 fade，保留240步 / .45 / 原上限与美术强度；不跨到 C39 的右侧。新增4725个过渡点清单已保存。

此前 fixed original triangle 的 old→new 追踪不能当作重新变形后 Blender actual tessellation。最终审计用临时**完整** mesh 重新 `calc_loop_triangles()` 读取实际隐式对角线；此临时数据没有作为肩部对象进 scene，更未作为交付部件。原追踪数字保留为代理诊断，不用 old/new dot 阈值替代 actual inside-out 判据。

## 最终实际几何与保留未知

唯一保存的候选：`artifacts/character-shoulder-c40/diagnostic-c40-left-shoulder-failed.blend`，SHA **`6dbc4183a57117079c1479b0c1361e52995f66ff3eaef3f2d3e00e1cba8bdc00`**。

- 修改22074点，最大位移 `.04486245u`，不超过原 `.09u` 上限；范围仍是猫左肩根，未越 `z2.40`。
- actual candidate 44911 个 touched triangles 无塌缩。原方向追踪仍有67个反向，最小dot≈`-.998668`；这不等同最终 winding 错误，也没有删除这项历史。
- actual 局部 neighborhood 79955三角，原 self18 → **candidate self0**、新增self0。
- actual whole connected mesh：components1、boundary0、nonmanifold0、inconsistent winding edges0，signed volume≈`6.61573426u³`。
- 编辑面与 **54 个 actual evaluated 吉他部件（含六根弦 tube）**分别相交检查，baseline / candidate / introduced pairs 均0。它不是全身对琴的整体无穿入证明；C39 正在处理的原右侧问题仍不属于本检查范围。
- 对由原方向追踪挑出的626个实际候选三角做完整 candidate BVH 法向正负两侧 `±2e-5u` 的双方向 parity：**606个严格正确、20个两方向不一致、0个两方向一致的 wrong-side**。

这20个是不一致 / 未知，不能宣称已证实 inside-out，也不能把 local self0 / winding0 平均成 parity 通过。可能涉及 grazing / fp32 / 遥远原表面的 ray crossing，未证实原因，**因此保持 geometry gate false**。`actual-normal-side-parity.json` 为原始完整记录；`parity-interpretation-readback.json` 追加解释，不改候选或删除失败证据。

## 实看灰图与交接

root 允许把同一未过候选保存并出内部图，以免继续纯数值盲改。实际打开 `gray-front.png`、`gray-shoulders.png`、`gray-three-quarter.png`：完整猫 / 双爪 / 吉他仍同帧。Builder 观察左肩的圆弧阴影稍软，但琴颈后仍可读出 dome；它是否足以改善套接必须独立评审，不能由 builder 自放行。右侧管臂和头脸依约保持原样，本轮不评价为修复完成。

`diagnostic-left-shoulder-front.png` / `diagnostic-left-shoulder-three-quarter.png` 使用与上述 C31 只读图**完全相同**的 camera position / target / ortho scale，便于逐处比较；它们是作者裁图诊断，不是完整帧生产资产。

独立进程 `independent-readback-and-left-crops.py` 重开原 source 与已保存 native，`separate-readback.json` 检查坐标、全 int point attributes、拓扑、body matrix、C35、右侧、头、非修区及其他 objects。该 readback 不是独立艺术审查。

当前最多一个候选、两次实现修复已完成，不再改几何或扫参数。交给 root 安排至少身份 / craft / motion 三角色实际看原图、C31 与 C40 matched views：可判这项局部视觉改善是否值得保留，但未解决 parity 方向不一致前不可称整体几何通过；即使局部审美通过，也不继承到后续整合、shaded still 或动态。

没有费用服务、颜色 / groom 重绑、骨架、动画、实际按弦、音画输入、网页修改或发布。其他 agent 的资产与 public 未修改。
