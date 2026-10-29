# C57 原因分解＋旧好左爪替回的腕截面预检

结论：**C52的75对自交不是单次Smooth制造；未Smooth已有110对真交线。固定全身参数停止。局部旧好手替回的输入截面则简单且高度匹配，可以另立有限腕带连接预检；本轮没有接出新body或宣布接触通过。**

## 同源/同.010的因果分解

C49原native、C52冻结native均只读，使用与C52完全相同的Object-mode native voxel选项：`.010u`、adaptivity0、preserve_volume=True、fix_poles=True。

未Smooth输出仍297850v/297848f、单闭合component，actual non-neighbour triangle BVH **110对**。独立读取保存的preSmooth坐标与pair三角，全部110对再以edge-triangle真实交点确认 span>1e-6，最大 .00828046u；不是BVH切线噪声。

在同一内存网格再施加原 factor.15/iterations1 Smooth，输出与冻结C52的**ordered coordinates、ordered topology全bit-exact，最大坐标误差0**。C52 afterSmooth的75对已逐条确认，因此Smooth减少了对数，没有制造这条分支的根因。没有调整resolution/flag或再造native-noSmooth候选；本轮仅保存只读派生NPZ/receipt，`noSmooth_branch_saved=false`。

不应由此概括所有Blender voxel方法都不可用；这里只否证这组固定全身参数作为无self的完成资产。

## 实际同平面 wrist cut

方向：处理**猫解剖左按弦爪，画面右侧/世界x>0**，不做新的右拨弦掌shape。复用C23真实source wrist plane `Y=-.72`，同一局部ROI x(.75,1.62)、z(1.3,2.35)、原面中心y<-.55。只BMesh局部bisect/delete，无全身Manifold。

两份只读派生：C52保留proxim/body并删除distal坏手；C35冻结已通过的原hand按同plane保留完整distal手和腕端。

|输入|保留侧|boundary loop|分叉/严格XZ自穿|实际self|原保留点|
|---|---|---:|---:|---:|---|
|C52|proxim/body|1环177点|0/0|3（画面右侧x>0耳）|bit-exact|
|C35|distal好手|1环198点|0/0|0|bit-exact|

C52 cut后286240点，其中177个新plane交点显式provenance0。原C35 hand5359点、5260面，boundary198，**本次cut没有产生新点**；每个原hand点都直接带C35输入数组index+1，不能因它们在旧C23属性里source0就丢掉身份。所有C35 hand坐标exact，5个原实际contact face均完整存在、同一cyclic旧顶点indices，旧target世界点不移。独立核两源guitar geometry/world frame exact。

C52坏左爪的72对自交已在这份proxim/body cut中消失，剩3对耳区交给独立C56工作。注意此前“右耳”指画面右侧x>0，不是猫解剖右耳。

## 匹配度与明确的接法边界

均匀arclength256样本只用于几何诊断，不给任何点nearest恢复ID：最佳cyclic phase0，RMS `.00184015u`、最大 `.00243959u`；真实两polyline双向Hausdorff `.00101824u`，截面面积比C52/C35 `1.00067507`。实际SVG/PNG overlay已打开，两个D形腕截面近乎重合。

这是**简单同平面输入可匹配**的证据，尚不等于安全接面：177是奇数、198是偶数，且两环同平面有轮廓微交错，不能直接做零轴向宽bridge或硬weld。

下一有限方案可以Y=-.72为中心，分别在body约-.70、oldhand约-.74重新切一小段真实轴向腕带，按实际新counts决定一次明确parity处理/monotonic zipper或等数strip；窄双侧fair只在远离contact的连接区。上述两个Y只是下一方案，不是本轮已执行的第二/第三cut。新的截环仍需独立single-loop/截面检查，不能假设counts沿用177/198，更不能盲用midpoint reduction后不看真实曲面。

任何实际保留graft之前，必须新验证完整单body、全self（含耳分支）、真实木/弦和5actual rays；原C35手完整保留也不能直接继承最终body的接触通过。不得用5ray通过冒充整个角色或右拨弦接触通过。

## 追溯与使用方式

- 原C52 SHA `630c27d7de8d94f0fb85201e0a216bb7055c223bb85b6d05b704fd6ba0ad40bc`。
- 原C35 SHA `3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce`。
- C49 SHA `0ea1505e0368ab01ed5dac5ba5a07cb4772426e25db8faeffcf35cee8ac7ad6b`。
- `smooth-cause-receipt.json`、`pre-smooth-line-confirmation.json`、`wrist-graft-preflight.json`分别是因果、真交线、腕环输入证据。
- 两份 `*-same-plane-cut.npz`有实际co/flat faces/sizes与原输入点ID，不是接好的body。下一实际装配应从冻结native再次执行同cut以完整保留原face attrs/materials，而不能把NPZ几何当完整旧绑定。
- 若后续同时接入C56耳工作，body与hand要分两个来源通道：retained C52 inputindex、imported C35 inputindex，各自显式ID；不可把两个输入的整数ID当同一namespace或nearest猜对应。C52的旧C35 canonical仍全0，C35手的真实来源另记。

源码 `design/character-sculpt-v2/c57/`，artifact `artifacts/character-body-voxel-c57/`。本轮只有固定原因重建与同一中央平面的两源预检，无新graft native、无新的右掌shape、无全身参数扫。原C52/C35/C49 native hash不变。无颜色、groom/UV/rig、动画、GLB、公开发布、部署或费用；不混入root的C49研究交接包。
