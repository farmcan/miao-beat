# C39 右拨弦爪/前臂：唯一新方法失败，实际灰图已看

C39 基于冻结 C35 连续 body，C37 全部历史保留。方向：解剖右臂在画面左、音孔上方；左 C35 握琴颈在画面右。本次授权后来扩至右肩连接，另一分支只处理 x>0 左肩；头 z>=2.43、左 C35 与全部吉他继续锁定。无新费用、颜色、动作、GLB、公开发布或部署。

## 先看公平化-only，再做一候选

先保存 `diagnostic-c39-fair-only-unpassed.blend`，实际渲染并打开完整 front、右爪近景与侧景，均为原穿琴未解决的内部诊断。公平化减浅两条方口，但掌端仍厚，尚无清楚的短圆三趾形。

实际皮肤深度层揭示前臂融合问题：XZ=(-.9,1.9) 的前皮 -1.18547Y 直接连到背皮 +.42278Y，没有独立臂背；XZ=(-.75,1.82) 才出现 armback -.64942Y 与 torsofront -.49775Y 的空隙。琴约 -.95Y 在融合体内部。仅把前皮向 -Y 推会扩大体积，不能据表面交线减少宣称琴已在皮外。

C37 窄 distalcap 范围的木交对为 soundboard472/rosewood248；本次完整右侧诊断范围检测784/980，范围不同不能混为同一前后改善指标。六弦 min vertex-to-actual-tube 距离原为约 [.238,.204,.169,.132,.095,.05965]，最近第六弦仍超过目标 .02–.04u。

## 唯一候选

一组固定操作：在实际 faired Q 上进行128步紧支撑平滑 ambient flow，以当前坐标重算掌轴/横向坐标；两个宽浅 web 退让、短圆 cap 下探及小幅前表厚度收敛。右肩允许区做50步固定软公平化（最大0.006655u）。随后用实际 rosewood outline 扩展 .065u、截在 x<=-.18/z1.475..2.30，建立背侧通道；前壁用圆横截面函数，不用琴的平面。后界 -.620Y，前界中心 -1.095Y。操作前 volume preflight 确认 cutter 闭合单连通、Euler2、volume .280386u³，30个抽样 cutter 边点处于原皮外，通道可达外部。

实际 manifold difference 是一次几何候选，不是参数扫。开始时因新增 canonical ID 要求，中止尚未进行 Boolean 的初进程、保留日志；几何常数不变，重启前加入术前 `Miao_C35_vertex_id = index+1`（全部590793点，含5359个原 C23 source0 左手新点）。术后精确坐标反查原身份，新增点全部 source0，不采用布尔插值整数作为真实身份。

## 几何失败

输入590793点；输出573187点，保留571467原点，新增1720点，未保留19326原点。完整 mesh component1、boundary0、nonmanifold0、Euler2，signed volume 6.628889→6.545041，不能据这些数字称解剖完成。

- 真实右区对全身 non-neighbour actual triangle self **173**；127对全保留点，46对含新/未证实点。相同完整右区原 C35 已有125对，其中 cap公平化/实际Q flow后、clearance之前剩116对，集中于 x[-.825892,-.755672], y[-.572932,-.494322], z[1.732945,2.008701] 的前臂/躯干融合背侧。新方法确实没有重演C37 stale-P cap45self，但它没有修掉继承融合区116对，Boolean又使最终173对。
- soundboard actual intersections **0**；rosewood **33**，且皮肤点 actual solid parity **156 inside**，无 ambiguity。剩余区在 x[-.536665,-.169050], y[-.662742,-.620000], z[1.462307,1.658897]，对应切窗底/右边界；不能放行微小穿木。
- 六弦 tube、neck、fretboard surface intersections0，最近 sampled skin-to-any-six-tube 距离 **.0682725u**，仍未达 .02–.04u。没有要求六弦全部压住。
- 全部吉他数据/变换 exact。术前头/左原点变形为0；但 Boolean 后有 **12个修区外头/耳点不再存在**（z3.208..3.412）。精确原坐标匹配和带 face provenance 的完整 cyclic-corner 验证均未恢复这12点，不能称纯浮点误差或冒用插值 canonical ID。新1720点ID0；原failed native 的canonical map不是完整可合并资产。
- 主 receipt 的 left 判据 `x>.5` 包含一个耳点，不能把它误说成左手受损。单独读回：5359个新左 C35 手点全部present/exact；实际左臂/爪区79425点全部present/exact。12个头点最近现有表面距离2.66e-6..7.30e-5u，而最近现有顶点距离.00019..00364u，支持全局Manifold简化删除，绝非仅坐标哈希误差。

## 实际灰图的决定性失败

在上述失败状态下，按 root 明确许可，对同一冻结 native 渲染三张内部诊断：`diagnostic-failed-gray-{front,right-paw,right-side}.png`，builder逐张打开看过。

清让切割在前臂中段造成明显琴形楔口/断裂观感；单 connected component 不能掩盖视觉上的截断。肩圆接口仍在，趾仍是浅槽，没有清楚自然的短圆三趾。此方法不能送三评当合格静态，也不能通过恢复12个头点就救成可用角色。

下一方法应为源点边界明确的完整右臂 shared-root、真实前后表面的自然 loft/局部重拓扑，规划肩根过渡、前臂厚度和三趾 cap；不能继续扩大 instrument-shaped subtraction 或扫切深。实际木/六弦/skin parity/自交必须一同验证。C39 不得合并到头、肩或生产分支。

## 冻结证据

- Source: `design/character-sculpt-v2/strum-paw-refinement-c39.py`
- Failed native SHA256: `59a97e06dca5b6f405fb912a47939a36f550ce9ac0827a458312a6dbd2e09ce6`
- Original failed `receipt.json` 不覆盖；geometry/topology/ray/parity/src map 与实际图保存在 `artifacts/character-strum-paw-c39/`。
- `failure-attribution.json` 记录173 self source ID/位置及wood33定位。`preclearance-and-head-deletion-attribution.json` 检查原/术前 self、12头点的实际表面/顶点距离，以及真实左手保留区。
- 两个只读归因脚本报错日志保留：C37 RNA引用失效已在C37记录；本次 Numpy int64 JSON序列化报错后只修类型转换重跑，没有重做候选或覆盖native。

这是已证伪的局部解剖研究，不是完成品；无独立艺术通过、颜色或动画结论。
