# 薄电琴单次静态装配 · FAIL 冻结

2026-10-30。使用已通过独立工艺门禁的 clean 薄电琴，完成 **1个整体候选 + 1轮有有限体测量依据的双腕局部修复**。结果 `FAIL_STATIC_INTEGRATION_FROZEN`；没有越过核心门做卷指、CMC 接触、配色、美化或动画。

## 原生与评审证据

目录：`artifacts/miao-reuse-v1/thin-electric-static/`。

- 完整同 pose：`thin-electric-front-NOT-ACCEPTED.png`、`thin-electric-three-quarter-NOT-ACCEPTED.png`。
- 必看细节：`thin-electric-face-NOT-ACCEPTED.png`、`thin-electric-left-hand-front-NOT-ACCEPTED.png`、`thin-electric-right-hand-NOT-ACCEPTED.png`。
- 原生：`thin-electric-static-native36.blend`；执行回执：`thin-electric-static-receipt.json`。
- 相机补证：`left-review-camera-receipt.json`；清单：`inspection-manifest.json`。
- 脚本：`design/miao-reuse-v1/scripts/build_thin_electric_static.py`、`render_thin_left_review.py`。

已实际查看以上 front、3Q、脸、左右手。初始 `thin-electric-left-hand-NOT-ACCEPTED.png` 为从背后观察，几乎全被袖/身体遮挡；保留这张失败取景，但不把它当左手通过证据。随后只补同 pose 的前侧左手图，native SHA 与全部骨骼 matrix_basis 不变，无新 pose 或 native 覆盖。

## 这轮实际纠正了什么

源 `FK-Middle2` 的 local +Z 指腹方向，约为源 `ORG-Hand` 的镜像 ±X，**不是 Hand +Z**。上轮粗姿势用错手面轴，能解释 edge-on 长条读法。本次用 source 实测框架相对映射，保留左右 roll 关系；手腕依据实际前臂方向，只向预期手方向偏约25°，没有用任意点反推不受限 roll。

Torso +6°、Chest +2°，肩根绕 world Z 对称6°，源局部肩平移/scale不动。薄琴统一 .70、颈仰20°、面板上抬8°，琴背按 evaluated 腹部外侧5mm定位；没有再次压薄琴身或改任何 source mesh。琴的长角和头/袖的有限几何也进入实测，不能只用 Body 板厚推断可行。

143 mesh /2,192,095 tris 的 clean GLB 实际导入官方3.6.23，仅离线。猫恢复版脸、默认材质、手几何保留。原猫与琴 base mesh hash 前后一致，输入 SHA 不变，new actions=0。没有运行 embedded CloudRig/lighting 或 MoveAI addon。

## 核心门先于手指：真实数值

手掌支撑选区每侧205个实际皮肤顶点、374个实际三角，非空。有限体 inside 检查只对真实 `Body` 与 `Head / Neck` 的实际局部截面；三角检查覆盖全部143个组件，包括弦、品、拾音器、螺钉与摇把。没有要求205点退出同一无限半空间。

| 指标 | 初始左 | 修复后左 | 初始右 | 修复后右 |
|---|---:|---:|---:|---:|
| 实际肩腕 reach / 源两段长 |72.407%|67.968%|99.933%|≈100.000%|
| 核心 triangle overlap 对数 |413|163|1968|1842|
| 核心 inside 顶点数 |7|4|14|8|
| 实际腕目标误差 |<.001mm|<.001mm|<.001mm|**6.940mm**|
| 实际肘屈曲 |87.211°|94.361°|4.209°|**.361°**|
| 实际腕弯折 |24.998°|24.921°|25.001°|27.225°|

唯一修复：按实际 finite inside 皮肤点到相应颈背/面板出口计算，左沿颈背方向13.662mm，右沿面板外方向7.891mm；均在预设20mm上限内。左碰撞减少，但仍有4点进入颈体，最大最近侧深度约6.198mm；右仍有8点入实体，最大最近侧深度约4.375mm。修复不是成功，因为真实 IK 夹在原臂最大长度，右腕仍未到目标。

实际上臂/前臂长保持 .12197337 / .12278579m，pose/rest 误差<1e-4；未拉臂。右伸直过度与可达性本身已足够否决，无需再卷指来迎合局部数字。

最终全手 inside：左11点、右8点；全手 triangle overlap 左806对、右1842对。核心 gate 已失败，`finger_updates=0`。源 Thumb1 左右均 XYZ 未锁、无约束，确认原生 CMC 多轴可用；本轮**未**尝试它，因此不能声称原拇指工作空间已否证。

## 整体 P0 和实际看图

最终 `GEO-head` 对琴952个 overlap 对、1个 inside 点；`GEO-arms` 2834对、36 inside；`GEO-collar`208对、7 inside。`GEO-body`无命中。这些是有限实际组件的拒绝证据；不把 BVH/射线的零命中独立当完备无碰撞证书。

front 与3Q中，蓝琴的成熟细节、薄体和手指体积均可辨，嘴/眼保持恢复，没有旧白三角或嘴消失。但：上琴角顶到下颌附近；前臂/红袖口跨过琴面；左手张开贴在琴颈周围，颈直接穿入掌根而非完成握持；右手仍像摊掌盖在弦区，伸臂无余量。左手补图清楚显示颈—掌根冲突，不能用完整 front 的遮挡说已形成自然支撑。

每次 render 前都按原表达式把 camera 世界 Euler 写入 helper 局部 Euler，逐轴误差全0。同一 pose 两个全身视角、脸/手必要观察图；没有新造型矩阵。源脸保留成功，不等于整体静态成功。

## 停止与结论边界

本候选和唯一局部修复均已冻结。无 P0 清除，无手指接触通过，无最终美术或动画授权。三方可据实际图/receipt复评；本 builder 不自判通过。

这次薄琴减小实体板厚，但源琴的突出长角、当前整体摆位和右臂路径仍冲突。结论是**这一组 rig/道具布局失败**，不是成熟猫本体差、所有自然姿势无解或 Thumb CMC 不可用。原源文件、旧 FAIL、脸恢复 native 均未覆盖。本轮不再换 frame、重摆琴或追加退出。
