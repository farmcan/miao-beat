# C33：局部侧向自由度后的真实局部缺陷与内部诊断图

2026-10-29。C32归因之后的新方法：保留原Y/V方向、全部世界目标、物理Laplace与.005位置正则、原外部不等式；仅给非C8、非可见轮廓的upper内部增加unit-U小位移。没有扩大QP预算、U界或颜色/动作。

## 新自由度与一次方法

3746变量＝3089原Y/V＋657 upper unit-U变量。U物理界±.008u，约手宽.4944u的1.62%；依据父任务给定的小范围侧让出，不作为原创测得最优界。actual front/inside相机的upper轮廓边、upper开放边界及V>=.045趾尖不加U，共482轮廓点；原C8/根/可见前掌Y锁区保持。三趾原接触三角的重心U位移=0，V由U⊥V保持，世界琴弦／板下缘目标不变。

所有SAT轴仍在C25真实可分离的原安全轴中选择；固定规则优先最小化修复C32实际相交所需的U侧让，绝不任意翻到不安全侧。U量级、规则、权重均固定；最多8次同一主动集。

最初只读精确+.0008等式LP不可行；原授权接触gap[0,.002]区间却可行，max inequality违反1.39e-17。为避免自设过分精确条件，完整exact预检先存`exact-0p0008-readonly-preflight/`，随后只将接触约束纠正为原预声明区间，不移目标或变位移/碰撞要求。几何直到区间LP通过后才首次应用。

## 实际应用与停止

第0次严格unscaled OSQP solved，原A/l/u实际max residual5.874e-9，低于1e-7；应用这一个合格几何解。actual U max=.00553309u，没有顶到±.008界；Y/V最大约.0766140u，锁区及原C8点bit-exact。几何完整590793点/590465面、单连通闭合、flip0。

实际五gap约[.000528085,.002000081,.000273096,.001999828,.002000160]u，normal和实际源身份正确。第二趾与第二掌托有约8.1e-8/1.60e-7u的正间隙上界浮点超差，逐值保留，未自动豁免；这不是仍存真实穿入的替代解释。

此时指板／neck／弦1、2、4、5、6交叉0，第三弦8三角交对，skin self3 triangle pairs（审计为1 polygon pair）。加入22外部witness和27原安全skin式后，第1次OSQP在30s time limit，原约束违反7.275e-5>1e-7，因此没应用；同冻结qp-1的独立HiGHS也infeasible，不能声称有可用warm-start而停住。该限制只针对当前少量U/锁区/冻结局部平面，不是原握姿不可能。

## 剩余缺陷已定位到三个quad

- self：upper/source2 polygon **590434↔590446**，actual loop triangle交线span **.000110284u**；中心U约1.3497/1.3539，V约-.0181/-.0173。四边形角点离最佳拟合面最大.0003358/.0002601u，实际是非平面quad，不能只看flip0。
- 第三弦：全部8对均来自 **polygon590443**，U约1.3602–1.3620，V约-.0182。全部8对有实际交线，最长span .00329134u；不是纯BVH假阳性。
- 对这几个实际skin三角做32分割重心网格采样，102个点经actual tube最近三角面＋两个径向parity确认在弦管内；最大观测到最近管面的距离 **.000113716u**（inside约.0699px）。这是有限采样的实际穿入深度证据，不是全域解析最大值；交线长度也不能混写成穿入深度。

`self-intersection-attribution.json`、`string3-intersection-attribution.json`、`penetration-depth-diagnostic.json`保存actual polygon/vertex/actual tube triangle、交点、法线与采样点。没有更改目标来掩盖缺口。

## 明确失败下的内部灰图

父任务明确授权：在完成真实失败归因后，只对同一冻结native出front/inside内部诊断灰图，供判断形体与局部修复。`internal-diagnostic-render.json`保留此边界。

`internal-diagnostic-gray-front.png`完整显示猫、双爪、吉他；inside为作者诊断crop。**geometry/art/contact均未通过；图不是公开角色交付。** 图源native和原失败receipt哈希均未变，未save model、未改顶点/面。Builder实际打开两图：短圆三趾和连续掌背未见明显拉长或新横唇破坏；微小接触缺陷在此机位不明显，不因此变成通过。尚无独立三评放行。

## 交接与下一局部方法

冻结native `diagnostic-c33-infeasible-or-collision.blend` SHA `bae5552b97cf890c0ceab4a2368cf7665cc3defe60a3ec26234f38c7f9a361f4`。保留exact预检、区间修正、实际应用、QP time limit和同系统LP不可行历史。原C25/C27/C29/C32不变。

停止扩大QP或U参数。下一应只修590434/590446/590443这三个局部非平面quad：解析两个合法对角线并检查actual所渲三角；必要时局部双线性细分或有限curl，而不是改全掌/目标。需要实际改变被渲三角面并重新满足self0/所有木弦0/五ray门槛；本C33未实施该拓扑修复。

使用隔离本地OSQP/SciPy与Scenario MIT审计helpers，来源/许可证另见c29-qp-setup；无hosted service、新费用、Cloudflare、颜色、毛发、rig、动画、GLB或引擎扩展。旧绑定失效。
