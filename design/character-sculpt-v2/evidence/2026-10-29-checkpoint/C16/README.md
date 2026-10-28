# C16 · 回到原 C8 弯臂的远端腕掌重置

2026-10-29；本地 Blender 5.2.3 LTS / bundled OpenVDB，新增现金支出0。**两次实际候选后冻结；仍有腕掌P0和hold缺口，不替换 C11，不进入颜色/动画。** 三位非 builder 评审由 root 另行组织，本文不是独立放行。

## 先测边界，未沿用 C15 坏体积

输入固定 `artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend`，SHA `2432d199edeae964631cb79d96b1d06a5ba2fb908143532fc5bb0a86f600f33e`。将已评估hold=1冻结为静态体，**未进行C11的径向缩腕，未引入C11/13 collar或C15长loft/躯干裁区**。新完整圆掌/三短趾只重用冻结C11的人工控制笼，去背中央口/连接杆，在内存副本中闭合掌背，原文件不改。

`C8-actual-sections.json` 保存实际 mesh/plane 交线；`C8-actual-section-landmarks.json` 是交线端点按1e-6u拼链后的面积质心；SVG有标签，PNG为同数据无字体栅格图。图中从左到右、从上到下Y=-.72/-.78/-.80/-.83/-.86/-.90/-.96。右手ROI内每层为一条闭合环，未见第二条躯干flank环。注意：**几何孤立环不等于已经语义认证为解剖腕口**，部分宽截面仍可能属于原始坏掌的近端；本次不能仅凭“闭合”证明它形体正确。

关键实际截面：

| Y | X范围 | Z范围 | 面积质心X/Z | 面积u² |
| --- | --- | --- | --- | --- |
|-.80|.92966～1.38757|1.52227～1.92500|1.18013 / 1.71117|.124751|
|-.83|.93307～1.38774|1.52729～1.93255|1.18371 / 1.71267|.122299|
|-.96|.95711～1.37906|1.58359～1.96659|1.19474 / 1.75523|.101306|

切区严格 X[.86,1.56]、Z[1.40,2.30]、Y<-.83。2103个原远端表面样本，裁后全部在保留体之外；最小场值+.0100008u。原源皮肤Y[-.80,-.72]的裁切场变化实测0。因此没有再把切割扩大到Y=-.37、躯干flank或肩肘。

## 两个目的明确的候选

r1：只跨约[-1.08,-.78]的腕短段。前端取完整C11掌的实际截面场（Y=-1.062、掌根Z<1.90），后端取实际C8前臂截面场（Y=-.798），用截面场morph及bounded smooth-min连接。没有猜固定X椭圆半径，更未重做整条臂。实际长棒/躯干鳍消失，但新掌后仍有宽杯环；来源色蓝区说明附加的短morph体积本身形成后垫，不能当只剩阴影。

r2：唯一一次目的修订。**不再把第三个腕体积联集到闭合掌后。** 下掌根Z<1.90区域，直接在实际C11完整掌3D场与实际C8完整3D场之间做有界形体替换；Y≤-1.13保掌、Y≥-.78回原C8完整3D场，Z≥2.02退出替换，中间用smoothstep权重。上掌/三趾仍为新掌与严格远端裁后body的组合。保留原3D臂的导数/曲线目标，避免用一个2D截面挤出成新长棒。

实际打开r1/r2全部整帧、3Q、inside、来源色：r2环槽变平顺，原C8弯臂与躯干轮廓保留，**但3Q/inside仍读作前方圆掌＋后方宽圆垫，腕掌P0没有解除**。这不是可交付优化，更不能凭单连通或0自交抹掉图上分层。

来源色：灰＝C8体积，橙＝C11完整新掌/趾，r1蓝＝短截面morph体积、紫＝平滑联集；r2紫＝完整3D场的有界替换/混合区，**r2没有第三个蓝色附加腕体积**。这些只标贡献场，不是独立生产肢体或语义骨骼分割。

## 当前根因边界

已量到：原C8 Y=-.83环中心Z≈1.713、横/竖径≈.455/.405，而C11新闭合掌底在Y≈-1.03、Z≈1.60，底环方向接近朝下。闭合圆掌与宽臂的根部坐标/朝向没有成为一个统一的解剖设计。两种不同体积过渡都仍显后垫。

据此推断，下一步应先统一**掌根朝向、下掌内部体积与实际前臂轴**，而非继续调blend半径或再叠一层遮缝。本轮没有做旋转掌根的反事实重建，不能说已经排除了所有算法影响。尤其r2用的是±.072u窄带场的空间插值，未重距离化；它不是全域精确SDF，饱和场插值可能影响腰部形状。这一数学局限也保留，不能把所有P0都武断归因于某一个美术点。

## 完整几何与段间连接

r2：928990v/928990quad，单连通、完整mesh 0开边/非manifold。腕ROI审计patch40815faces、0自交/翻面；290边界环属于裁出的审计patch，完整猫不开口。一次清理只移除腕ROI内8v微碎片，AABB体积上界及double精度居中体积约9.26e-13u³，见component-cleanup.json。

`segment-audit.json` 对当前实际保存mesh做Y截面；从-1.10到-.74，各层目标区域均有闭合曲线。中段- .98面积.054651u²，-.92为.063194、-.86为.104451、-.80为.123780、-.74为.128955。它说明不是一根点/薄线勉强接住，不证明干净变形环线、正确解剖或动态承托。

## 非腕/头脸/原前臂残差

体素 .006u；仅腕部copy dense：142×125×163，单float32阵11,573,000bytes；按18阵估208,314,000bytes，<1GB。未全身dense copy，但最终全身sparse提面，拓扑/UV/groom/shape全部重新失效。此估算不是全进程内存硬上限。

| 区域 | 样本 | mean / p95 / max，u |
| --- | --- | --- |
| 非腕 |6041|.00008000 / .00021472 / **.00891724**|
| 头前/眼高度区域 |7037|.00002316 / .00005424 / **.00264645**|
| 保留C8前臂，Y[-.78,-.20] |7233|.00010646 / .00040852 / **.00427189**|

全部为实际原顶点→新BVH最近曲面距离，最近点仅用于测量，不是miss自动替笔。有限单向样本不是Hausdorff或二维轮廓上界。非腕不写成完全不变，头/耳细节仍存在体素化影响。

## 接触：没有准确press或另一侧支持通过

r2contact审计绑定当前native SHA，显式BVH hit/miss与实际Bezier曲线，所有负gap保留。36点29背面/7miss，gap[-.01377536,+.06058906]u，**8负点，其中6点<-.005**；r1为7负点/5点<-.005。r2接触没有变好。

预声明3趾腹目标（第三弦，U1.245667/1.355/1.464333）gap **-.0059543 / +.0541670 / -.0066676u**：两个潜在穿入，一个明显空隙。不是正确press；不要求放松hold压下全6弦。

相对侧支持仍取真实指板厚度中面：实际前/后ray命中Y=-1.013/-.953，中面-.983。U1.28/1.40下缘到skin沿V的间隙 **.121337/.121529u**，均非有效接近。没有无依据补拇指/加球来让统计过关；未建新承托假设，本轮先限定腕。后续若做小型隐藏相对侧软垫，仍需依据真实neck/board几何并标为单视图重建假设。

## 冻结与再现

- `paw-distal-wrist-study.py` 新工作源码，r1/r2各有实际执行快照；`paw-distal-wrist-contact-audit.py`只读审计。
- 当前 `r2/miao-c16-distal-wrist.blend`、1024front/3Q、768inside与来源色齐。原C8/C11/13/15文件SHA见manifest，未改。
- r2后仅澄清继承的r1 native custom-property文字，`metadata-clarify.json`证明geometry hash前后相同；图/形体不变。contact/segment已对澄清后的同SHA重跑。
- 输入C8原light receiver集合已继承到new mesh，没有再次发生C15漏主灯的问题；灯/眼位/吉他/原相机不改。
- 旧拨弦爪/头耳等整体阻塞不在此轮修复；没有全身美术B/C、UV/groom重绑、retopo/rig、动画/引擎/网页/导出/发布验收。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/paw-distal-wrist-study.py -- --sections-only --out artifacts/character-paw-c16/recheck-sections
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/paw-distal-wrist-study.py -- --out artifacts/character-paw-c16/reproduce-r2
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/paw-distal-wrist-contact-audit.py -- --dir artifacts/character-paw-c16/r2
```

复用固定MIT Scenario helper d44410f058991f677ccf733a8e86ce95110857eb（bridge小掌笼/几何审计/截面），未安装额外工具。无付费、CF、commit/push。
