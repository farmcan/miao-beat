# C53：无绑定 target 的 C1 接管准备与安全限制

2026-10-29。C53 builder 技术记录，**不是独立评审或角色动画通过**。新实现只在 `design/character-motion-c53/`；旧 v2 源码 / profile / 已推版本和 public 未覆盖。没有新模型、绑定、角色动作、音频、网页或发布。

## 问题与复用

旧 `design/character-motion-v2/contact-motion.mjs` 在新输入接管时保存当前位置，但新 smoothstep 从零速度开始；70ms中断因此只有C0，原回执诚实保留 `velocityContinuityVerified=false`。

C53 继续 import 旧工厂，复用同一 profile、冻结左锚、requested fretting 不应用、phrase600ms间隔与head/blink独立时钟。单音单弦 / 连续子集和弦一次正向扫弦、无queue、140ms闭环均保持。新增代码只替换右target路径，不接入生产，也没有 fork 一个角色模型。

## 解析方案

普通直线段用 cubic Hermite，各路径 knot 的位置 / 零速度由两侧共享。新事件到达时解析求旧计划当前位置及速度，首段使用相同位置 / 速度，并在不超过 `.25ms` 内制动至零；制动位移限制为当前段剩余长度的一半以内。单向 sweep 的每个实际弦 contact 都是 knot，所以制动不会为被取消旧段多跨下一个弦。随后仅沿normal抬到原安全高度，再去新目标；不把横向重定向直接拉过琴弦，也不补队列或回程扫弦。

这是C1位置 / 速度连续，**没有加速度或jerk物理上限**。微短制动不能直接施加到真实骨架。极近knot的浮点时刻若所需时长低于 `1e-6ms`，明确拒绝该输入并保持旧计划：`accepted=false / C1_ESCAPE_BELOW_NUMERIC_TIME_FLOOR`。不把这个受限分支写成任意机器时间都能无条件接管。reset另为显式重置，不承诺连续。

## 实际证伪与修正

第一次保留旧平直surface rail的C1方案通过controller bench，却在actual evaluated tube检查中触发 **128项局部signed-nearest-normal入弦诊断**，最小约 `-4.72e-6u`，超过原 `2e-6u` surface-near诊断门槛。旧v2实际检查只测 nearest distance，未包含此项；本记录不据此宣称旧路径经过完整solid包含裁定。

失败源码、控制器回执、actual回执 / 日志和真实轨迹gzip保留于 `evidence/initial-flat-rail-failure/`。没有扩大容差或隐藏失败。修正仍保留原actual contact点，加入固定 `.007u` 向外relief节点，使每个contact从外侧到达；投影保持单调、一stroke一次扫过，不增加音符事件。各contact零速以及轻微离弦起伏的真实音乐动作观感尚未验证，不能称自然拨弦。

## 已运行的技术验证

`validate-c53.mjs` 实际运行：

- 8单音与全部21个连续和弦子集，选弦各一次、非选弦零次；一个正向sweep，无返回sweep。
- 指定 `0 / 10 / 30 / 45 / 70 / 85 / 100 / 139ms` 中断边界，含单音换弦、和弦→单音、单音→和弦；另有移动中的内部时刻。
- 旧9类输入（8音+全和弦）→4类新输入、每个整数 `0..139ms`，共 **5040次accepted中断**。解析接合位置 / 速度最大误差均 **0**；两侧独立有限差分最大速度差 **3.17523785e-8u/ms**。
- 150ms连按16次，0中断、16完整stroke；70ms连按16次，15中断、仅最后1段完整，queue均0。不保证每个快速输入都完整展现stroke。
- 左锚不动，快速输入不重启head / blink / phrase时钟；新phrase规则保留；numeric-floor拒绝分支实测保持旧target / velocity，不吞掉为“通过”。

真实控制器输出 `evidence/target-path-samples.json` 含 **79条路径、70676个样本**（常规.25ms、精确knot、自适应制动细分），含解析速度、phase、stroke ID与旧弦安全退出许可。它不是手工示例点，也不是模拟角色动画。

`validate-actual-geometry.py` import旧extract模块的 `actual_tree`，只读同一冻结C35（SHA `3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce`），重读六条actual evaluated tube及rosewood / soundboard / neck / fretboard四木体。最终79条 / 70676点（8931唯一位置）有限检查 **0失败**：

| 检查 | 实际最小值 / 结果 | 原门槛 |
| --- | ---: | ---: |
| 非许可弦nearest | `.03021288477u` | `>.025u` |
| lifted return弦nearest | `.07497907430u` | `>.07u` |
| 四木体nearest | `.08046436310u` | 远离surface / local-inside检查 |
| 采样折线与木体surface | 0 hit | 0 |
| tube signed-nearest-normal | `-1.2436626e-7u` | 原2e-6u surface-near诊断带 |

共有395个surface-near样本。它们不是严格零穿入或力学接触认证。此处保持原诊断尺度，没有为C1放宽。

## 不可外推的范围

closest-normal是局部方向检查，不是全实体winding。当前有限点 / 采样折线不等于完整解析扫掠体、爪体积、肢体可达性、自交、关节变形、groom / skin新绑定或所有吉他硬件碰撞证明；未检查所有rosette / bridge等物件。C35坐标系统中的路径不自动适用于后续新模型或新琴变换。

实际眨眼、头动、呼吸、拨弦、回位、连续接触、音画输入、网页和视频都未制作 / 未验。整体灰模与shaded-still P0仍拦动画扩展。下一步由非builder独立审查本技术模块及其边界；builder的bench不能替代三角色艺术 / 动作审查。

详细接口、复跑命令与证据索引见 `design/character-motion-c53/README.md`；文件哈希见 `evidence/handoff-manifest.json`。
