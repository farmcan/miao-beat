# 单键原生试验 v1 · 新增键—壳交叉，按STOP冻结

2026-10-30。默认色三方静态GO后，root授权仅L食指 / 白键014的有限试验。**结果FAIL，已冻结；不制作短片、release/end动作或网页demo，不启动v2。** 失败是移动键的机械净空问题，不是手指穿邻键；静态成熟猫 / 道具与此前三评GO不被追溯改写。现交独立motion诊断，不能把still或零手交叉写成动作通过。

## 已实际输出与观看

目录 `/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/single-key-v1/`：

- 完整场景：`prepare-front.png`、`contact-front.png`、`down-FAIL-front.png`。
- 同场景手诊断：`prepare-left-hand.png`、`contact-left-hand.png`、`down-FAIL-left-hand.png`。
- 冻结native：`contact-native36.blend`、`down-FAIL-native36.blend`。两者是状态快照，非动画。
- 数值：`local-axis-calibration.json`、`single-key-failure-receipt.json`、`single-key-progress.json`、`failed-key-chassis-forensic.json`、`failed-state-render-receipt.json`。
- `inspection-manifest.json`、`SHA256SUMS`固定全部本机文件和SHA。

我已实际看完6图：完整猫、双臂双手与全琴均保留，头脸正常；食指准备抬高与近触在手crop可区分，完整主图差异很小。0.364mm键行程在完整图难辨，因此即使几何没有失败，也不能仅凭crop或数字称操作反馈清楚。壳内交叉被外壳遮住，不能因最终PNG看不见就关闭该P0。没有做动态片段，因此没有自然下压 / 回弹的视觉证据。

## 原生方向与真实皮肤求解

全程Blender3.6.23、factory-startup / disable-autoexec、同agent顺序单进程。只校准 `FK-Index1.L` / `FK-Index2.L` 各原生局部X ±.5°，然后选择**仅Index1.X**求近触；Index2、其他手指 / 右手 / 腕 / 头身 / 原骨长 / 基网格 / 原材质不变。其他骨控制matrix_basis全不变与骨长不变有逐状态断言，未用整手下沉或stretch。

测量沿render-matched独立proxy：show_viewport匹配show_render、Subsurf levels匹配原render2、暂时静音level驱动、IsViewport=False；测后恢复。**直接RENDER depsgraph缺口仍在**。实际Index2皮肤697点及全手36288三角，不是骨尾代替指腹；有限键面 / 邻黑白键 / 壳 / 桌全部在检查范围。

| 原生校准 | 目标白键gap变化 | 全手对键/壳/桌交叉 |
|---|---|---:|
| Index1.X +.5° | 2.91261 → 2.56288mm | 0 |
| Index1.X −.5° | → 3.25540mm | 0 |
| Index2.X +.5° | → 2.82925mm | 0 |
| Index2.X −.5° | → 2.98694mm | 0 |

目标以有限真实键表面投影间隙求解，初始源18°；接触容差目标为50μm、允许±15μm，受限步长≤1.25°、最多10次，不扫姿态 / 轴 / 多个候选。近触收敛到 **22.11768198°**；仍留约63μm微间隙，不冒称数学上完全零间隙接触。准备抬指为15°，只抬同一个食指，无第二次敲击。

## 精确状态与STOP原因

| 状态 | Index1.X | 目标skin gap | 最近邻skin投影gap | 新增全手交叉 | 新增目标键对外部件交叉 |
|---|---:|---:|---:|---:|---|
| 原ready | 18.0000005° | 2.912611mm | 3.677607mm | 0 | 0 |
| 准备轻抬 | 15.0000005° | 5.051851mm | 6.029695mm | 0 | 0 |
| 近触 | 22.11768198° | .063241mm | **.624895mm** | 0 | 0 |
| 首个down猜测 | 22.56768198° | .092626mm | .312001mm | 0 | **Controller chassis：23三角对** |

此前聊天曾把近触邻键余量简写为.6816mm，**准确JSON为.624895mm，以此表 / JSON为准**；不影响STOP来自键壳而非手的分类。

键以原后端bbox中厚度作world-X pivot **(.0573125,−.4130000,.3200000)m**；源GLB并无真实hinge / action。front lever约112mm，按近触实际邻键余量选出的唯一front stroke为 **.363979445mm**、world-X角 **−.186201115°**，没有强压1–2mm。down首猜一遇新壳交叉立刻STOP，没有改小行程、换pivot或追加姿态搜索。

首次运行漏持久化中间trace，仅在错误日志留下STOP；随后**以同一确定输入重放一次**，修正记录遗漏、获得完整分类，没有改任何数值参数。分类发现不是目标指腹求解越界：下压候选的手皮肤仍有正gap，全手有限三角交叉0；新增的是白键本身切入琴壳。因此没有使用root只针对“目标skin微量越界”的一次数值起点修正例外。

## 原隐藏机械重叠与新增壳交叉分开

原静态白键014在后段已经与 `Raised black piano key.010` 有59三角对，属于源未切槽矩形白键与黑键的隐藏机械重叠。不能把这写成新手指穿键，也不能把一个静态CAD原文件当完整机械机构。

有限竖直占用区20×24采样中，继承重叠最大约4.0003mm、体积估计 **7.94477e−7m³**；唯一down候选降至 **7.75286e−7m³**，旧白黑重叠减少，仍59相交三角对。它被单列限制，不以此数量变化当新碰撞通过。

新增键壳交叉23对来自真实有限triangles。精确边—三角求交点bbox为：min **(.05056798,−.41105786,.31165305)**，max **(.06405702,−.30625570,.31200001)**m。壳局部最近法线为+Z、表面约z=.3120000，与源键底相邻，证据支持键床没有此行程所需净空。两个原键顶点还通过nearest-normal + ray parity确认进入壳，最大**顶点**深度6.438μm；这不是整个连续三角面的最大穿深，不能据此把23对交叉缩成“仅6μm可忽略”。无需据此断言专业来源质量差，也不能自行补造琴。

## 继承的对中口径问题与后续边界

render2原ready的最低pad x=.06304836m，目标键中心x=.05731250m；近触pad x=.06327529m，向邻键侧偏约 **5.963mm**。此前静态腕位按viewport0最低点对中，恢复原生render2后没有重新移动腕，所以近触余量小。root已提出后续可基于真实render2触点重对中，以及CC0派生最小键床空腔；**本轮均未执行**，不自启v2、不移动手 / 腕、不做Boolean或新琴。若后续明确修正，应先重新灰与默认色三评，再做动作；旧静态GO不自动继承新位置 / 几何。

源默认色native SHA **`3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b`**前后不变，原approved pose `4fb6d4c…`保持可恢复。所有6次render camera helper误差0；本试验新增actions0 / keyframes0 / clip0。原Cat CC BY、KeyForty与桌CC0和项目代码MIT分项边界保留，没有改guitar / public或发布。

新脚本仅 `single_key_geometry.py`、`calibrate_single_key.py`、`solve_single_key_states.py`、`render_single_key_failure.py`，位于 `design/miao-reuse-keyboard-v1/`。下一步是独立motion判读当前失败事实；未签可复用动作`sample_pose(q)`安全范围、未交single-key网页接入条件、未验证release/end或八键。
