# Miao 动作 / native rig 准备与交接

2026-10-29。只读 C35 的技术准备。**现角色尚未通过完整 gray 与 shaded still 的三角色审查；没有进行绑定后演奏动画扩展。** 本文不把 skeleton API 成功、点路径通过或过去原型控制器当成完成动作。

## 实看来源与现实现

实际打开批准原图 `public/character/instrument-scenes-v1/guitar/idle.jpg` 与 C35 `artifacts/character-paw-grip-c35/gray-front.png`。原图右拨弦侧是厚短、连贯、放松的手臂；左手包琴颈，不能用一根硬摆杆或位置相同的 ASDFGH 形变冒充逐音演奏。本轮只沿用 C35 已审查的静态接触，不宣布其整体身份或动态通过。

实际阅读：

- `public/labs/character-compare/motion-controller.js`：现控制器输出 5 个 morph 权重；attack 60ms、return 160ms、FretLow/High 整体插值。它已有 phrase gap 600ms 与独立 idle 相位，但不提供实际弦表面路径、每键品位或一次输入跨弦计数。
- `public/labs/character-compare/three-renderer.js` 与 `design/godot-web-compare/main.gd`：两端当前都直接设 blend-shape 权重，**不是已绑定 Skeleton/IK 的实现**。新的空间 target 数据不能直接塞进旧 5 权重接口便声称完成集成。
- `design/blender-guitar-v1/scene.py:193` 起：实际源码按 equal-tempered formula 创建 frets；`k=0..5` 生成 `Guitar / string 1..6`，前三根半径 .0028、后三根 .0021。这个索引不是标准吉他弦号，也没有存音高。
- C35 `receipt.json` 与三份独立静态 review：本地静态 hold 通过限定于原冻结 native 和已声明范围。strict nominal contact 仍 false、authorized positive fp32 roundoff true；没有改这两个值。

固定输入 native SHA256：`3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce`。

## 先复用 native / primary 实现

选择 Blender 自带两骨 IK、Copy Rotation、世界 Copy Location，后续在同一 continuous skin 上提供人工审查权重。没有重复写 IK solver，也没有生成分离胳膊图层。Blender 官方文档域在本工具返回 402，未将错误当作已读文档；改查 [Blender 实际 RNA 源码](https://github.com/blender/blender/blob/main/source/blender/makesrna/intern/rna_constraint.cc)，并在本机 Blender **5.2.3 LTS** 实际构造与读取这些 API。RNA 实现属 GPL，只参考 API，未复制到项目模块。`scenario-blender-expert` 要求的 sibling `scenario-blender-rigging` 本机未找到；依 expert 允许的无人值守 fallback，明确保留该缺口，限定为 schema/API 技术准备。

Three 的 [CCDIKSolver 实际源码（固定 commit）](https://github.com/mrdoob/three.js/blob/4c39d071ab7bca531d464d00c8b738fe1981e812/examples/jsm/animation/CCDIKSolver.js) 已查看并保存在 `sources/`：它操作 SkinnedMesh 的骨骼链，支持角度限制与单链 blend，并校验父子链。它适合未来 Three adapter 复用；当前 runtime 是仓库已有 `three 0.186.1`，此 dev commit 只作固定研究样本，未与现 runtime 混用或 import。上游 MIT 全文与 hash 已保留。

Godot [SkeletonModifier3D 官方文档](https://docs.godotengine.org/en/stable/classes/class_skeletonmodifier3d.html) 及 [实际源码（固定 commit）](https://github.com/godotengine/godot/blob/cafc17a192acf67903910a68aeb3c076c0907a4b/scene/3d/skeleton_modifier_3d.cpp) 支持骨骼修改流程，且文档说明 modifier 位于 AnimationMixer 播放之后。建议未来通过统一 target 数据写 modifier，不再各端重建 stroke 时钟。MIT 声明留在源码头；没有声称本轮已跑 Godot skeleton 或 WebGL skin。

本轮新代码只组织路径/控制状态和 native 功能接口，无新的运行依赖。没有导入模型、权重或外部美术资产，不能从 MIT 代码推导猫形象资产的权利。

## 每键目标是可检验数据，不是已经按对的姿态

[Fender 标准调弦](https://www.fender.com/articles/setup/standard-tuning-how-eadgbe-came-to-be) 核实低到高 E–A–D–G–B–E；[Fender C 大调资料](https://www.fender.com/articles/scales/c-major-guitar-scale) 核实 C D E F G A B。数据用 MIDI `[40,45,50,55,59,64]` 建立标准弦音，逐项检查 `openMidi + fret == noteMidi`。

**显式作者方案**：将 source strings 1..6 赋为低到高 E2..E4；所以标准 string 1 对应实际物体 `Guitar / string 6`，标准 string 2 对应 `...string 5`。原源资产没有音高元数据，此赋值不是“源码中本来已存的调弦事实”。源粗弦在 -V、细弦在 +V 的朝向还需完整琴姿审查；本轮不静默倒置 geometry 或改已过静态接触。

| 键 | 音 | 标准弦 | 实际 source string | 品 | 目标 logical u |
| --- | --- | ---: | ---: | ---: | ---: |
| A | C4 | 2 | 5 | 1 | 1.598406 |
| S | D4 | 2 | 5 | 3 | 1.373177 |
| D | E4 | 1 | 6 | 空弦 | 1.698000，明确无 press target |
| F | F4 | 1 | 6 | 1 | 1.598406 |
| G | G4 | 1 | 6 | 3 | 1.373177 |
| H | A4 | 1 | 6 | 5 | 1.172520 |
| J | B4 | 1 | 6 | 7 | .993756 |
| K | C5 | 1 | 6 | 8 | .911826 |

nut、13 根实际变换后 fret 曲线按 nut→body 排序并读取，未凭 `.001` 名称猜品号。nut u≈1.698；实际 fret1≈1.576544、fret8≈.897235。按弦目标放在对应实际品丝 nutward 18% 的区间内；这是作者 pad 放置方案，不是原图可测出的真实压力。目标点通过对应 actual evaluated string 管面射线读取并投影一次至真实三角。七个需按弦的三维目标全部不同、位于各自实际品区间，E4 空弦不压弦。所有 world 坐标与实际物体名称在 profile，所有 `paw_pose_verified=false`。

同一根弦上的不同音由**左手不同品位**决定，不应为了按键视觉不同而虚构每音扫六弦。单音右爪只拨 source 5 或 6；未来必须让左爪真实换品且按各 pose 审计。当前左手始终固定 C35 hold，`applyRequestedPose=false`，控制器不会把这些位置当成已验证变形。

## 140ms 空间闭环与接口

`createContactMotion(profile)` 接受一次 host 时钟；`trigger(event, nowMs)` 只接收真实输入或 host 已确认的回放事件。它不发音、不合成输入、不写录音事件。时间沿用 host 的音频/回放时钟换算，不能让 renderer 自起另一段 stroke 时钟。

```js
const motion = createContactMotion(profile);
motion.trigger({ mode: 'melody', noteIndex: 0 }, hostNowMs); // C4 单弦一次
const frame = motion.sample(hostNowMs);
// frame.right.world -> 已批准 skin 的 right IK target，需转换坐标系
// frame.left.worldAnchors -> 冻结 hold；requestedPose 仅待验证数据
// frame.head / body -> 独立微动通道，不可移走实际琴/左爪锚点
motion.trigger({ mode: 'chord', sourceStrings: [1,2,3,4,5,6] }, nextHostNowMs);
```

单音在选中管面点两侧各 .009u 的窄区间跨一次；和弦仅在显式 contiguous 弦集合跨度上扫一次。带跳过弦的集合会拒绝，因为单段扫弦无法自行避免未选弦，尚无 mute/fingerstyle 实现。

| 相对时间 | 阶段 | 约束 |
| --- | --- | --- |
| 0–10ms | depart | 从当前位置抬至安全法向高度；已在高度上则不重复抬高 |
| 10–30ms | preposition | 在高处移到目标起侧 |
| 30–45ms | approach | 在弦外侧靠近，不跨弦 |
| 45–85ms | sweep | 只正向通过选中表面点 / 一次和弦跨度 |
| 85–100ms | clear | 先法向离开，避免回程再扫 |
| 100–140ms | return | 在高处回 neutral，140ms 无队列 |

150ms 输入间隔留 10ms 余量。<140ms 输入直接接管当前点，不排队、不重置整段；70ms 测试位置 C0 连续并显式 `interruptedStrokes=1`。没有承诺 <140ms 每个被中断输入仍能完成全路径，接管瞬间的速度连续性尚未验证。head phrase gap=600ms、1500ms 独立包络；快连按不逐音重启 head、blink 或 breathing phase。blink 通道是数据，未做眼睑 shape 或视觉验证。

坐标是 Blender Z-up world，不能直接塞入现 Godot Y-up 或 Three glTF 根变换；adapter 必须一致地变换 target、normal、骨架和 instrument。运行时只能渲染同一个完整猫/双爪/琴场景，任何交付图像仍必须捕获完整连贯同帧，不能用 body plate 加分离手臂图片。

## native scaffold 与 source remap

`build_unbound_scaffold(profile)` 在内存创建 8 骨：root、head、双侧 upper/forearm/paw；两骨 IK，`chain_count=2`，禁 stretch；左 paw 世界 Copy Location 和双 paw 世界 Copy Rotation。关节锚点是未批准作者占位，`anchors_approved=false`。没有自动权重、mesh modifier、skin binding 或动画。实际 rest forearm endpoint error：右约1.765e-7u、左约3.576e-7u。它只证明构造与求解 API 可用，**不是可交付 rig**；pole/关节轴限制、权重、关节皱褶与 deformation review 仍需最终静态角色后作者处理。

5 个 C35 static-contact skin 命中已绑定为实际 triangle + barycentric。三趾 9 个 triangle 顶点的全部 INT POINT source tuple 均唯一；两个掌托的 6 个顶点 tuple 各与 **3742 个**源点一致，无法按现 tuple 唯一重定位。这是实际数据缺口，不能 nearest 假装精确：

- support1 source-native indices：586683 / 586484 / 586485。
- support2：586290 / 586049 / 586147。

profile 留存各点原索引、原 world、全部 integer attributes、唯一性与 barycentric。合并器必须给出 **显式 C35→目标 mesh index map** 或先添加/保存完整唯一来源 ID；`remap-contact-bindings.mjs` 缺映射直接拒绝。synthetic map 测试只验证接口与拒绝行为，未拿它声称 C31/C36/C37 的真实映射已执行。即使重构误差为零，仍输出 `contact_pass_inherited=false`、`actual_contact_audit_required=true`。

## 验证结果与数值修正历史

`evidence/native-api-and-geometry-probe.json`：实际 source 坐标与 modifiers 内存中完全未改、源文件 SHA 未改；Blender 5.2.3 构造 API 通过；actual six-tube hit 最近误差最大 5.735e-7u；抬起跨六弦回程的 101 点最小距离 .074688u。

初始未做三角面投影的 BVH ray hit，最近距离最大 1.06624e-6u，超过原1e-6u诊断阈值，故那次 probe 真实失败。保留 `initial-unprojected-ray-probe.log`，没有放宽阈值；最终对命中的同一 actual evaluated tube 最近三角只投影一次，保留 `ray_to_actual_triangle_projection_u` 后重跑通过。没有移动乐器、原 skin、左接触目标或 C35 接触容差。

`evidence/controller-validation.json`：八键150ms连按，每键 sweep 只跨选中弦一次，总8次；140ms回 neutral；和弦各6弦一次；70ms覆盖接管无排队；左5锚恒定；head/blink与未重触发基准相同。错误键、非 contiguous chord、NaN、错误 SHA、缺 exact map 真实拒绝。

`evidence/path-geometry-probe.json`：将 Node 控制器每1ms实际输出重新对源 native 的六个 actual evaluated tube triangles 检查。选中弦表面近距≤5.735e-7u；sweep 距其余五管至少 .02958u；lifted return 最小约 .0746u。有限点采样不能证明连续 swept volume、不证明猫爪体积不碰邻弦，更不证明发力、弦形变、声音或按品效果。no-penetration 的完整动态结论仍未验。

## 后续真正 gate

先通过整合角色 gray 三角色、shaded still 三角色审查。随后在一张完整 skin 上批准关节轴/pole和权重，应用显式 source index map并重跑 C35 接触、wood、六管、self 与整帧视觉 gate。按八键逐pose验证指腹实际弦/品几何，不使用旧 FretLow/High 整掌平移取代逐pose接触。先只做一个慢音与150ms连按的最小完整场景，再独立审查动作/握持/头眼，不先扩一批片段。

绑定后的连续 deformation、手爪体积碰撞、头微动/眨眼/毛发跟随、音画同步、真实浏览器输入、Three/Godot adapter、移动设备观感/扬声器试听和生产交付均未做。没有因本目录通过而扩大成艺术/动作完成声明。公开状态/发布沿 root 的现有 Seed task 事件机制处理；本准备模块本身未发起外部部署或通知。
