# C32：补原安全侧自碰约束，剩余中趾局部冲突，无灰图

2026-10-29。接C29的五接触／外部琴弦约束可解、upper self49反例；C29所有历史保留。C32只新增真实skin-skin分离约束类，固定C25源、五世界目标、3089个1D自由度、原权重／锁区／.095u界，不扫参数。

## 先核验安全方向，再求解

`baseline-SAT-preflight.json`：C29 actual loop-triangle BVH中90对非邻upper三角，对应C29的49polygon自交区域。C25相同源顶点三角90/90具有可靠正SAT分离轴，最佳gap最小.00273408u，全部大于1e-5。轴来自两面法线、edge×edge及必要面内轴；固定原安全侧，未按candidate任意翻面。

每对三角取原安全轴，对3×3顶点施加投影分离≥.0002u（margin=min(.0002,.25*baselinegap)）。90对数学上810式，去重后731条新增；随后actual skin相交witness再加同类cut。原外侧不等式仍来自真实指板／neck／六弦tube BVH，不用AABB阴性替代。

## 单次方法的主动集轨迹

- 第0次QP solved：五gap约+.0008u；指板/neck0、仅弦1有10交对；upper非邻三角对12。
- 第1次QP solved：五gap约+.0008u，指板/neck/六弦实际面交全0，upper非邻三角对8。
- 加下一批SAT约束后，第2次原OSQP报告primal infeasible；没有应用不可行向量，保存第1次最后可解状态。110对原安全SAT三角累计约束、总13101不等式，无原安全轴缺失或不可移动违反项。

最后保存native仍为完整590793点/590465面，单连通闭合；587704锁点含585434原C8 source点全部bit-exact；五个固定世界目标和实际源身份／法线合格，所有实际琴弦面交0，5359手点双parity的指板／neck内部点0／分歧0。**但最终polygon self5，未达到self0，因此未渲front/inside，不算美术或握持完成。**

## 数值输出不能冒充不可行证明

原`receipt.json`和OSQP输出保留。只读重建冻结qp-2的原A/l/u后，原certificate代数检查失败：||Aᵀv||∞=.17537、finite-bound weighted sum=+.0060867。故原scaled-termination的certificate不能作为可靠数学不可行证明，不能只复述状态就判原姿势不可能。

同一冻结QP采用unscaled严格数值复核，未改矩阵/目标/相对权重，30秒66204迭代到time limit，primal residual=.0019586，达不到1e-7，故无可应用合格解。原无效certificate和失败复核均留证，没有因自设禁止应用而丢掉可行解。

独立HiGHS仅检查同一冻结A/l/u，报告infeasible；再将五接触从精确.0008等式改为**原预声明允许的gap[0,.002]区间**作只读核验，仍infeasible，排除了单纯“过分精确目标”的假阻塞。后者没有移动世界目标、改模型或应用替代向量。

进一步只读诊断，在其余冻结约束全部保留时最大化原中趾contact functional：所需Y重心位移.0529173627u，最大可达.0487524038u，缺.0041649589u；其他不等式违反3.47e-18、其他接触残差0。最强限制链是原中趾contact三角[590286,590312,590291]（重心约.21877/.00000761/.78122）→原安全SAT邻面→589628处实际第三弦外侧界。

上述结论都仅限**当前1D方向、锁区和保守原侧SAT平面线性模型**，不是原图姿势或所有三维网格修复不可能。`numerical-status-addendum.json`独立追加这些纠正，未覆盖旧receipt。

## 剩余5对的实际几何

`self-intersection-attribution.json`：5对全部upper/source2。3对在actual saved loop triangles上确认交线跨度约.006901／.001312／.000157u；另2对在实际loop triangles未确认，仍标tangency/epsilon/三角化歧义，不删成self0。

五对的原面均为非平面四边形，角点到最佳拟合面距离约1.1e-5–2.54e-4u；位置集中中趾根U≈1.36–1.37、V≈-.018到-.016、Y≈-1.056到-1.053。最大实际交线.0069u显著大于该平面误差，不能全部当float tangency。原polygon/vertex/normal/实际交点均逐对保存。flip0也不能替代此事实。

## 下一步与边界

不要无限加SAT或改目标扫参数。当前限制链已定位在中趾接触面及其相对邻层；建议下一步先对这小片薄折／非平面四边形做局部网格修复与有限三维curl/切向可动性验证，同时保留C32已解的腕掌承托与外部琴弦条件。新修复必须说明哪些原位／外轮廓仍锁定、原安全侧如何保证，并重新走实际self/琴弦/五ray门槛；这里未实施。

冻结native `diagnostic-c32-infeasible-or-collision.blend`，SHA `12bf24ea58a4ef9195e53f9cdeecce7e4f1f570dbd9d1a5405150890ec4cec68`。源C25 SHA仍59c4a6c37594209e740f0b41b148b11d41776c015b4e1e40aabb8bf4c49be8db。源码、同QP NPZ、求解日志、失败证书、严格复核、HiGHS诊断、原安全轴及剩余自交归因逐文件冻结。

复用本地OSQP1.1.1/SciPy1.17.1与Scenario MIT审计helpers；隔离依赖来源/官方wheel SHA/license证据见`artifacts/c29-qp-setup/receipt.json`，无hosted service或新增现金费用。未改C25/C27/C29、vendor、颜色、毛、rig、动画、GLB、引擎或Cloudflare。旧绑定失效，美术/动态未验。
