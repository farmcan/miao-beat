# 唯一+2mm键组 / 双腕候选 · 灰静态待三评

2026-10-30。well / Boolean路线停止。只从immutable默认色native，作一次授权静态候选：**68白黑键整体world-Z+2mm；双腕原生IK world-Z+2mm保world朝向，左腕另保留world-X−5.962789mm对中，右腕不修X。** 原指关节、头身、case / knobs / 桌、base mesh、材质与原骨长不变，不扫描高度，不加杆 / 支架，不做动作。

**9张灰图与native已齐，全部实际查看；等待三位非builder灰gate。** 目录 `artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift/`，完整front / three-quarter，face / left-hand / right-hand，直视`key-rear.png` / `key-front-edge.png`，feet-support / support-side。manifest和SHA固定文件；脚本 `design/miao-reuse-keyboard-v1/probe_keygroup_lift_gray.py` 使用相对项目根。

| 本轮新测量 | 结果 |
|---|---:|
| 左pad目标悬停gap / normal | 2.904683mm / +Z平面 |
| 右pad目标悬停gap | 2.912790mm |
| L / R腕reach | 76.1855% / 76.0524%，无stretch |
| 两腕IK world矩阵误差 | 最大约5.96e−8 |
| 全手、全袖对有限键 / case / controls / 桌交叉 | 0 |
| 全68键静态对固定case / knobs / 桌交叉 | 0 |
| 同步固定014铰轴Z | .322000027m |
| 最大front行程 | 1.5mm，仅机械扫掠，不驱动手 |
| 五个扫掠截点对case / knobs / 桌 / 其它新键交叉 | 0 |
| 连续扫掠key最低Z | 约.312527533m |
| 固定case全几何maxZ | 约.312000010m |
| **case Z方向分离保守下界** | **约.527523mm**，不是欧氏精确最短距 |

receipt中1.973927mm只是“源key顶点向case的正竖直ray采样最小值”，**不是全连续面最小距离**。分离下界来自既有连续角区间几何极值整体+2mm与固定case全Z bbox；knobs / 其它键 / 桌分别用有限几何检查，不混为case界限。

68键彼此相对关系保留。原014 / black010隐藏重叠仍59pair，具体pair变化列表保留；它只是共同+2mm刚体平移后的原继承区，先前2–3近边界点分类与连续体包含性unknown仍在，不因整组抬高豁免整个black组件。全程使用render2匹配proxy；直接RENDER depsgraph缺口不变。case未打孔，mesh/material-slot hash前后相同。

**实际视觉保留项：**完整图仍有承托和脚影，双腕 / 袖口可读；低角`key-front-edge`无遮挡地显示均匀暗缝，`key-rear`显示键后部与固定控制台。其读作正常机械净空还是P0露缝 / 键组悬浮，由三方直接看图裁决，builder不以交叉0替代判断。不改高度、加暗片或遮住缝来凑通过。side诊断尾端裁切不算生产整帧；front/3Q才是完整帧门槛。

新pose SHA **`6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b`**；9次camera helper误差0。新native SHA及逐图SHA见 `inspection-manifest.json`。source默认色SHA仍 **`3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b`**。原CCBYcat / CC0keyboard-table / 项目MIT分项沿`licenses/`；旧v1失败与原包保留。新增actions0 / Boolean0 / color0 / clip0 / public0。灰未过不出默认色或动作。
