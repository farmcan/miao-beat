# C53 · 可中断 C1 target 控制器技术准备

2026-10-29。**无模型 / 无音频的 target-path 准备模块，不是新角色动画或真实手部动作优化完成。** 整体静态 P0 仍阻塞绑定与动画扩展。旧 `character-motion-v2/` 和 public 未改。

使用同一只读 C35 profile，import 旧 v2 的控制器复用 phrase / head / blink 独立时钟、冻结左手和事件语义；新增右侧解析 Hermite target 状态，速度单位为 **scene units/ms**。不 import 上游 IK 实现，不新增依赖或服务。

```js
import { createContactMotionC53 } from './contact-motion-c53.mjs';
const motion = createContactMotionC53(profile);
const receipt = motion.trigger({mode: 'melody', noteIndex: 0}, nowMs);
// accepted=false 时旧 C1 plan 保留，输入显式受限；没有队列、自动补扫或补发音符。
const frame = motion.sample(nowMs);
```

单音仍只选一弦；和弦只接受连续弦子集、一个 stroke ID、一次沿 cross-axis 正向扫过，各选弦一次。静态左锚不随目标变化；requested fretting 仍不应用。所有实际目标点来自现有 profile，调弦 / 弦编号的 authoring 假设也原样保留。

每个直线段用有解析导数的 cubic Hermite。普通段各 knot 速度为0；中断时保留当前位置和速度，用不超过 `.25ms` 的短制动段，且最多走完当前段剩余距离的一半，避免多跨下一个弦 knot。随后先沿 profile normal 抬到所有弦之上的原 `.075u` clearance，再横移到新目标。全部仍在140ms结束；没有输入队列。

首次平直 rail 继承旧 profile 后，actual triangles 检查发现2.4–4.7e-6u的局部入弦诊断。失败代码、数据、轨迹gzip和日志保存在 `evidence/initial-flat-rail-failure/`。未放宽原 `2e-6u` surface-near 诊断门槛；修正为**精确原 contact 点之间的 `.007u` 向外 relief 节点**。它让路径从外侧接近每个点，不改变 contact 点、不反向或新增 sweep；这些停顿 / 小幅向外起伏是否适合真实演奏动画尚未验证。

极接近 knot 的浮点时间会出现可用制动时长小于 `1e-6ms` 的情况。控制器明确返回 `accepted=false / C1_ESCAPE_BELOW_NUMERIC_TIME_FLOOR`，保留旧 plan，不硬归零速度或放宽安全限制。`reset()` 是显式重置，不承诺跨 reset 连续。加速度 / jerk 没有设物理上限；C1 **不等于** 人体动作平顺或可执行。

| 文件 | 作用 |
| --- | --- |
| `contact-motion-c53.mjs` | 新的 C1 右侧 target 控制器；复用旧独立时钟 |
| `validate-c53.mjs` | 8 单音、21连续和弦、8指定中断边界、5040个中断、150/70ms连按、数值floor |
| `validate-actual-geometry.py` | 复用旧 `actual_tree`，只读 actual evaluated 六弦与四木体；不保存 native |
| `evidence/controller-validation.json` | 解析接合、有限差分、单向跨弦与时钟等 bench |
| `evidence/target-path-samples.json` | 真控制器79条路径、70676个点及其解析速度 / 阶段 / 允许旧弦退出区 |
| `evidence/actual-geometry-validation.json` | 上述输出的 actual tube / wood 有限几何检查 |
| `evidence/handoff-manifest.json` | 文件哈希、冻结 v2 来源与范围 |

复跑：

```sh
node design/character-motion-c53/validate-c53.mjs
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python design/character-motion-c53/validate-actual-geometry.py
```

结果：5040次被接受的整数ms中断，接合位置 / 速度误差均0；独立有限差分最大差约 `3.1753e-8u/ms`。150ms连按16次都完成整段；70ms连按16次中断15段，只有最后1段完成，队列均0。不保证快速输入每次都完成一次完整可见 stroke。

actual probe：79条、70676个实际输出样本、8931个唯一位置，失败0；未允许弦最近 `.03021288u`（原门槛>.025），return最近 `.07497907u`（原门槛>.07），四木体最近 `.08046436u`、采样折线 wood交对0。395个tube surface-near样本中，最小closest-normal值约 `-1.244e-7u`，属于原2e-6u诊断带；**不是严格零穿入认证**。

这些是有限 target-point / 采样折线检查，closest-normal不是全实体winding证明；没有完整解析扫掠体或真实爪体积碰撞、关节可达性、皮肤 / 毛绑定、按弦力、音频、网页、视频或角色艺术通过。C53 builder 不能为自己签独立三评。
