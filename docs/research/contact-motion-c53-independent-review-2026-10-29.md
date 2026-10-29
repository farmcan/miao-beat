# C53 非 builder 独立技术审查 · 2026-10-29

结论：**允许保留为冻结 C35 profile 上的无绑定 target-controller 技术研究模块；不批准接入 production，不签角色、动作、音画或艺术通过。** 在正常单调毫秒时钟及已检查的输入域内，accepted 接管的位置与解析速度连续证据成立。模块没有发现阻止其作为研究准备保留的 P0/P1 问题；接口泛化及未来 adapter 仍有下列具体缺口。

本审查员未构建 C53。已读项目 AGENTS、C53 README、技术记录、控制器/两个验证器、v2 import 源码、冻结 profile、manifest、首次失败及最终回执。仅写本报告和 `artifacts/c53-independent-review/`；没有改 builder 文件、旧 v2/profile、native 或 public。没有运行 Blender、整个 app、浏览器或音频；几何结论是源码与既有产物核对，不是本审查员独立重跑 native 几何。

## 本次实际复跑

为避免验证器覆盖交付证据，将 C53 两个 JS 文件复制到独立 sandbox，并以 symlink 只读复用 v2，然后运行原 bench：

```sh
node artifacts/c53-independent-review/sandbox/character-motion-c53/validate-c53.mjs
node artifacts/c53-independent-review/adversarial.mjs
```

原 bench 复跑通过：29 个完整单音/连续和弦、5040 次整数 ms accepted 中断，位置/解析速度接合误差为 0，双侧有限差分最大速度差 `3.175237850427948e-8u/ms`。79 条路径、70676 样本；复跑 `controller-validation.json` 与 `target-path-samples.json` 的 bytes/SHA256 **均与交付原件完全一致**。150ms 的 16 次输入全部完成；70ms 的 16 次输入中断 15 次，仅最后一段完成；queue 均 0。

独立补充：

- 固定种子、6000 次混合 8 单音/21 连续和弦的单调时间接管，时间从 `1234.56789ms` 起，间隔包含 0 和非整数值：5997 accepted、3 次 numeric-floor reject；accepted 接合位置/解析速度最大误差均 0。
- 每种事件的所有 plan knot，检查精确时刻及 `±1e-5 / ±1e-8 / ±1e-11ms`：3735 次，2857 accepted、878 reject。所有 accepted 段时长严格为正、共享 knot 的 p/v 完全相同；所有 reject plan 保持不变。这里 reject 的比例由刻意构造近 knot 样本造成，不代表人类输入概率。
- 普通时间域可复现的同 timestamp 连续接管：先 melody0@0，再 40 次输入@54ms，前 18 次 accepted、后 22 次 numeric-floor reject。没有 queue 或隐式补发，拒绝保持旧 plan。每次同刻接管沿相同 incoming velocity 制动并再次缩短剩余制动距离，最终触发 floor；它不是只在不现实绝对时间下才可能出现的分支。
- `inspectPlan()` 是 detached copy；外部修改副本不改活动计划。`[3,2,2,1]` 和弦规范化为 `[1,2,3]`，不会产生重复弦事件。

完整脚本与输出：`artifacts/c53-independent-review/adversarial.mjs`、`adversarial-results.json`、`adversarial.log`、`builder-bench-rerun.log`。全部是点控制器测试，没有为新增随机轨迹重新执行 native 碰撞检查。

## 接管及跨弦定义

`contact-motion-c53.mjs:28–38` 是实际 Hermite 位置与解析导数；不是把有限差分重命名为速度。接管先求旧 plan 的 p/v (`:87`)，首段原样使用这对 p/v (`:101`)，末点为 `p+v*d/2`、末速为 0 (`:99`)。该特殊 Hermite 可化为沿 incoming velocity 的单向减速，位移为半个 `v*d`；`d<=remaining/speed` 保证制动最多走完当前直线段剩余距离的一半。其后共享零速 knot，抬升后才横移。至少对该冻结 profile 及内部非退化段，这是有效的 C1 构造。

C1 是一阶连续；`.25ms` 乃至接近 `1e-6ms` 的急刹无加速度/jerk上限，不是肌肉、关节或真实爪可执行运动。速度连续也不等于肉眼自然。每个 contact 零速以及 `.007u` relief 的反复向外起伏，真实音乐动作感仍未验。

单音/和弦的“一次”定义自洽但很窄：一个 accepted trigger 建立一个 stroke ID；完整 sweep 沿 cross axis 正向经过每个选弦的 surface-point 投影一次；和弦不接受非连续子集，重复 sourceStrings 去重。它不是每根弦的物理位移、发声或完整爪接触次数。中断可能取消尚未到达的选弦；同一选弦上的新用户输入可以开始新 stroke，并非“全局永不重复经过某弦”。这与 70ms 只有末段完整的回执一致。

## 发现与接生产前要求

1. **P2 · 视觉 admission 不能替代用户输入/音频 admission。** `:94–97` 的 `accepted=false` 已有明确 reason，旧 target plan 确实保留；README 也明确没有自动补扫或补音符。拒绝时 `lastInput` 会更新，但旧 clock factory 不 trigger，因此是“活动动作/phrase 不变化”，不是所有内部状态完全不变。尚无 UI/audio/recording adapter，不能声称用户看到拒绝提示或音画一致。未来 adapter 必须读取 receipt，区分“真实用户输入已发生”与“此视觉动作被拒绝”，不能把拒绝变成重放/合成音符，也不能宣称每 input 都有完整动作。上述同 timestamp case 必须纳入将来的 adapter 验收。
2. **P2 · nowMs 的有效数值域未明确。** `:12` 只检查 finite；正常 `performance.now()` 范围的本次随机/边界测试通过，但这不等于任意 JS finite 单调时间。`2**60` 起点的 `now+140` 实际差为 256ms；`Number.MAX_VALUE` 起点的 `endsAtMs===startsAtMs`，结束回执时仍为 depart；`-MAX_VALUE → MAX_VALUE` 两次有限单调输入导致复用 head/body clock 的 age 溢出并输出 NaN。建议在复用前明确相对时钟范围/精度要求并拒绝不可表示的时长，或重基准；不是正常音玩具输入或艺术 gate 阻断。
3. **P2 · 工厂不是通用 profile validator。** 正交校验 `:45` 用 `NaN > tolerance`，结果为 false；将复制 profile 的 `normal_world` 改成 `[NaN,0,0]`，工厂不抛错且 sample 产 NaN。v2 工厂只检查 schema/whole-frame flag。零长度、缺弦、无穷坐标等也没有完整结构契约。本模块目前依赖同一冻结、已核验 profile，不能把该 factory 描述为对任意 profile 安全；泛化前需 finite/结构/严格正段长度的 fail-closed 校验。本审查没有把恶意改 profile 的结果归到冻结 C35 几何失败。

这些 case 已发给 builder 与主 agent 讨论，没有擅自修复或覆盖已冻结证据。

## hash、来源、许可与几何证据边界

本次核对 manifest 的全部 15 个文件 bytes/SHA256、两个 `old_v2_frozen_sha256`、native SHA；全部匹配。native 为 `3097d74a…25cce`，profile 为 `d0819636…d01e`，旧 runtime 为 `66695161…055`。本次没有 source native 修改。manifest 是内容一致性记录，不是签名或艺术审批凭据。

C53 import 的唯一运行来源是仓库旧 v2；仓库根 `LICENSE`/package 标明 MIT，v2 README 把代码与美术/模型许可分开。v2 `sources/provenance.json` 的 three.js/Godot 三个 pinned 文件，本次核对 hash/bytes 均匹配，MIT 声明保留，C53/v2 runtime 没有 import 它们。没有新模型、权重、贴图或外部资产；因此本次无需把代码 MIT 外推为模型或图像授权，也不能据此为原角色资产补签许可。

首次失败 gzip 解压后的轨迹 SHA 与其 actual 回执一致；日志保留 128 项局部 signed-nearest-normal 失败。最终 `.007u` relief 修订没有改原 `2e-6u` 诊断带。最终回执及代码一致记录 79 条/70676 点、8931 唯一位置、0 失败：非许可弦 nearest 最小 `.03021288477u`、return nearest `.07497907430u`、四木体 nearest `.08046436310u`，局部 signed 值最小 `-1.2436626e-7u`，395 个 surface-near 样本。代码对四木体做了相邻采样点的 ray segment surface 检查；没有对六弦做完整解析连续 swept volume 证明。

这些只是六条 evaluated tube/四个命名木体的有限 target 点及木体采样折线诊断。closest-normal 是局部法向，不能代替全实体 winding/包含判断；surface-near 容差内微负数不能称严格零穿入。桥、rosette等其他硬件、爪体积、肩/肘/腕可达性、自交、skin/groom、完整连体角色、动态接触、音频/网页/视频均未验；新增随机路径也未获得该有限几何回执。C35坐标与旧琴姿态的结果不自动迁移到新角色或新琴变换。

保留意见因此只针对技术研究。整体灰模/shaded-still P0、独立三角色评审与 whole-frame 生产约束原样有效；本报告不能用作动画扩展或真实演奏动作的批准。
