# C52 C49 全身固定体素重拓扑对照

结论：**整体保形和更均匀雕刻基底有实证；完整body仍实际self75，未过几何或角色艺术门槛。** 本轮只有一次固定 .010u native voxel remesh＋一次很克制 native Smooth，没有耳/掌sculpt field、没有分辨率扫。

## 对象与范围

输入冻结 `artifacts/character-local-merge-c49/miao-c49-local-merge.blend`，SHA `0ea1505e0368ab01ed5dac5ba5a07cb4772426e25db8faeffcf35cee8ac7ad6b`。原图和C49只读。C51局部头重拓扑是另一独立方法比较，本轮不碰其目录或文件。

先实际看C49原完整彩色front/3Q，然后采用同512px/16samples、同camera/light，生成灰色body＋原生亮度compositor的before/after四张完整图。独立眼、脸、琴的geometry、transform、material、visibility逐项exact，未改成另一个猫，也没有拆肢体。灰对照显示黑色透明背景（与原C49彩色白背景不同），但本轮before/after严格相同；只据配对图判断形变，不把背景变化当模型变形。

## 固定方法

Blender5.2.3，Object mode native `voxel_remesh()`。把C49实际evaluated body冻结到本次内存分支，保留完整单body，移除旧body modifier/shape绑定。

- voxel `.010u`、adaptivity0、preserve_volume=True、fix_poles=True。耳缘/浅趾缝需约2–3格，因此固定 .010而非 .012；没有尝试另一resolution。
- 只加一次 native SMOOTH，factor `.15`、iterations1；不调用会headless崩溃的sculpt.mesh_filter，不另作全身Laplace或多轮fairing。
- 所有新body点的原身份/canonical/INT属性为0；显式 `output_to_C49_vertex_index=-1`，不nearest猜源ID。UV层0、vertex group0、legacy rest vectors无，旧groom/rig/contact通过全部失效，必须重绑/重验。未更改或覆盖C35/C49历史。

前两次脚本启动在灰compositor的Blender5.2节点/Socket API上报错，均发生在remesh前；修正到 `CompositorNodeRGBToBW.inputs[0]` 后才执行唯一固定几何方法，原错误日志保留。

## 轻量结果与实际图

|指标|C49 before|C52 after|
|---|---:|---:|
|vertices|590793|297850|
|faces|590468|297848|
|component|1|1|
|boundary/nonmanifold|0/0|0/0|
|Euler|2|2|
|signed volume|6.4576892187|6.4574879586|
|edge CV|.425749|.159649|
|min edge|1.27977e-6u|.00127509u|
|min actual triangle area|1.01749e-10u²|1.17142e-6u²|

体积变化约 **-.00312%**，旧sliver尺度大幅改善；间距更均匀不是动画-ready边流的证明。

Builder逐张实际打开四张512灰图：原C49梨形、短肢、头脸、眼神、尾巴及抱琴大姿态基本保留，耳缘和趾缝略软，未出现C41/C46球管/新楔口式形态退步。但原右爪封帽、耳形等P0也没有自动变好。本轮不混后续耳碗/圆掌雕刻。

## 唯一针对问题的实际self读回

图看完后只追加一次完整body actual-triangle BVH自交核查，不作18类全面交付审计。595696个实际三角，排除共顶点拓扑邻接，得到 **75对自交**；winding inconsistent edges0。不能因为体素化、闭合或体积稳定就称self0。

75对全部进一步以edge/triangle实际交点确认交线 span>1e-6，没有把BVH tangency当真穿入，也没有静默豁免：

|位置|pair数|actual bbox|最大交线跨度u|
|---|---:|---|---:|
|左按弦爪簇1|3|x1.166..1.187, y-1.080..-1.052, z2.067..2.094|.0024625|
|左按弦爪簇2|20|x1.215..1.236, y-1.139..-1.102, z2.141..2.173|.0081084|
|左按弦爪簇3|43|x1.102..1.136, y-1.135..-1.094, z2.094..2.125|.0056677|
|左按弦爪簇4|6|x1.059..1.101, y-1.126..-1.102, z2.027..2.063|.0045926|
|右耳细节|3|x.53476..55461, y-.06654..-.04422, z3.35088..3.36323|.00070923|

这次完整body检测没有右臂旧融合区的自交对。故全身重采样确实避开旧右臂病态面，但左握弦细节/耳细节仍出问题；C35旧接触绝不能继承。没有改变voxel resolution/平滑次数、没有把这些点投影修掉或加入新sculpt候选。

## 冻结与使用边界

- 新native：`artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend`。
- native SHA：`630c27d7de8d94f0fb85201e0a216bb7055c223bb85b6d05b704fd6ba0ad40bc`。
- `receipt.json`为原执行证据，`post-voxel-self-readback.json`及`self-pair-attribution.json`为独立只读读回，native/source hash不变。
- actual pairs/triangles/交点/位置都保存在 attribution，无source point map继承声明。
- 原脚本：`design/character-sculpt-v2/c52/body-voxel-retopology-c52.py`，两个只读脚本同目录。

此结果可作为**未通过的、保形较好的新均匀作者基底研究**，不代表接触、浅耳、圆掌、毛发或动画已完成。若后续在新拓扑上做耳/爪sculpt，应另立方法与source receipt，明确新身份0、局部self/真实木弦约束，以及新静态三评；本轮不混。未调用新服务、未付费、未发布public/部署，也未做颜色、groom/UV绑定、rig、GLB或动作。
