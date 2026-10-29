# C42 耳形：两条实际诊断均拒绝，不合入人物

本轮只负责 C38 最终头脸上的耳朵，不修改肩、手、琴和其他脸部部件。实际打开批准原图、C38 face、C42 两组 front/face/three-quarter 图。使用本地 Blender 5.2.3，按 `scenario-blender-expert`、sculpting 的真实渲染门禁；没有发布或新增动画。

结论：**没有交付通过的耳形优化。** 第一次真实共享切环 loft 仍继承耳槽底部且变成尖薄帆片；第二次浅耳前面变换虽然连续场 Jacobian 为正，离散三角仍反转。二者都是保留证据的失败诊断，不得合入 C38 或解释为整体更接近原图。

## 基准与真实切环

原图 `public/character/instrument-scenes-v1/guitar/idle.jpg` 的耳朵短小、圆钝，浅内耳自然接入头部；C38 的厚三角沿、深槽和横向底搁板是 P0。基准原生文件：`artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend`，SHA256 `f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439`。

先逆共同 7.5° yaw 得到头部局部坐标，用实际 BVH ray 测量耳前后表面。`artifacts/character-ear-c42/probe.json` 保留截面。不是从二维耳图假定厚度：耳腔前面约 Y=-.09，耳沿约 -.16；根环包含头后弧，Y 总深度约 .57u。

`ear-reference-c42.py` 采用局部斜面 `z + .5*abs(x)=3.42`，得到左 276、右 269 点各一个真实闭环，无分叉。保存 `cut--1.npz` / `cut-1.npz`。保留顶点 bit exact；切面数值/边面清理导致切面邻域极少源点在数学平面下方也移除，严格留存断言失败日志。因此最终保护区按 `z + .5*abs(x)<=3.41` 检查，不把它说成所有 `<3.42` 点都保留。范围外其他头脸、手和身体点不删。

第一实现日志 `preflight.log` 是 BMesh 新增 attribute layer 后旧元素引用失效，修正为创建 layer 后再取得引用。`preflight-r1/r2.log` 保留过严切面下界断言，不删除失败历史。

## loft-r1：闭合不是精致

真实原生文件：`artifacts/character-ear-c42/loft-r1/miao-c42-local-ears-gray.blend`，SHA256 `2e4588991d532da6c4cd4e16c04004a5c9c931ee7b5ce909385b553ede997288`。

基于真实根环搭连续 24 层收窄 loft 和封口，非独立耳件。新 `Miao_C35_vertex_id` 为全部保留源点赋原 C38 的 index+1，新点为0；BMesh 插值的旧 `C23 source vertex id` 在新边界上不作为来源依据。下一次修订必须将所有新点的该旧字段也归零，不能依据它继承接触证明。

实际结果：nonmanifold=0，signed volume=6.4594，但 head/ear self pairs=15。正面 face 仍有旧槽底，新顶端读成薄帆，三分之四尤明显。**技术与视觉都失败。** 切面只移除上半耳，未完整覆盖原硬槽/厚唇，故不得以增加采样或毛发修饰掩盖。

图像：`loft-r1/gray-front.png`、`gray-face.png`、`gray-three-quarter.png`。本 builder 已全部实际查看。

## depth-r1：正 Jacobian 不能替源网格背书

回到完整 C38，不继承失败 loft。用前后截面拟合头局部浅耳面，采用仅 Y 的单调变换，沿 x/z 平滑回原皮肤。原拓扑和 source IDs 保持，无 custom normals。原生文件 `depth-r1/miao-c42-depth-diagnostic.blend`，SHA256 `ffc28578695edb3007221f3e540b24ddd803f36de6907e636aea65eda628705a`。

12657 点改变，最大位移 .108192u；连续场 Jacobian 最小 +.299857。实际源三角相对 inverse-transpose 传输法向有 **11 个反转**，最小点积 -.999765；head self pairs=2，严格 geometry gate=false。反例原/新三点坐标记录 `depth-r1/pre-gate.json`，不放宽阈值。

目视：耳腔较浅，但厚框/搁板仍在；耳根与额侧新出现横带/分区感，仍不是原图柔软一体的短耳。全身与三分之四依然偏硬，**不能收下“变浅”作为耳 P0 清除**。图像 `depth-r1/gray-front.png`、`gray-face.png`、`gray-three-quarter.png` 均已查看。

## 保护与下一步

另进程原生重开记录 `artifacts/character-ear-c42/independent-readback.json`；新耳不是可合入候选。源 `.blend` 及批准原图未修改。没有生产图、网页、绑定或新动画。脚本增加冻结输出保护，避免下一次运行覆盖此次失败目录。

停止继续压缩这一旧耳网格。下一个有意义的方法应先明确完整硬槽和厚唇的实际移除范围，用未污染头部横截面重建额侧/耳根过渡，再用干净、可控的浅内耳 patch。验证必须包括下部腔底已完全移除、单连续皮肤、完整正面/三分之四和独立身份/工艺/动作角色评审；不能用本轮自身评审替代通过门禁。

## 重开审计的额外纠正

`independent-readback.json` 确认两组各 93 个其他物件的网格/曲线坐标及 world transforms exact。loft 保留 canonical 正值唯一且坐标 exact，5359 个 C35 新手点全部保留；13627 个新点 canonical=0。depth 的 C23 source IDs 和 C35 新手点 exact。

但是 depth 原脚本对零权重区域仍做了 local→world 往返，原生重开发现 z<=3.12 的 **385 点有最大 5.551115e-17u 的浮点残差**。视觉不可见也不写成 bit exact。这个失败原生文件未覆盖；仓库脚本仅为未来执行增加零场区显式恢复输入坐标与冻结目录保护，没有重新生成另一个“修好”的候选。冻结执行副本与失败原生/receipt 留在各自目录。此细节再次说明不能据构造意图直接声称锁区原样。
