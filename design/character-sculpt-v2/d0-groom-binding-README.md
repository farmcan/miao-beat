# D0.2：真实C5 native groom表面绑定与一次局部技术扰动

2026-10-28。**已记录真实609383点猫体／180000根毛的窄技术闭环；还不是自然拨弦、正式rig、完整D0或美术交付通过。** 本builder不作为自己的独立验收人。

输入为D0.1副本 `artifacts/character-sculpt-d0/miao-d0-rest-bound.blend`，SHA256 `25d7d95ff1b21dfafbded4e0fb673faa1f45eb7234d2e010dd48f3c0125f15b6`。C5母版未修改，输入在执行结束重新核验相同。所有结果只在 `artifacts/character-sculpt-d0-groom/`，不发布、不commit。

## 实际接线与不变条件

采用此前**本机真实成功**的原生RNA/operator与内建节点，见 [native groom研究](../../docs/research/blender-native-groom-binding-2026-10-28.md) 和 `probes/native_hair_snap_probe.py`，没有另装库、换毛系统或尝试未跑通的Essentials bundle。

1. 在已冻结求值的猫体上新增专用 `BindUV`（FLOAT2/CORNER）；609060个polygon各占781×781 atlas中的一个独立guarded tile，按polygon loop顺序放凸正多边形。高角数ngon优先分配到UV原点附近以改善float32精度；最高126角。1218762个UV三角形，0个退化。
2. 本次发现冻结body实际已有 `UVMap`；保留其名字与所有数据hash，另增BindUV。新增前后mesh坐标、vertex normals、loop顶点索引、polygon loop start/total各自hash完全一致。BindUV只用于毛根定位，不承载视觉毛色。
3. `hair.data.surface=body`、`surface_uv_map='BindUV'`、`body.add_rest_position_attribute=True`；调用官方 `snap_curves_to_surface(attach_mode='NEAREST')`，实际返回FINISHED，产生180000项FLOAT2/CURVE `surface_uv_coordinate`。
4. 最短正式接线为 Group Input → builtin `GeometryNodeDeformCurvesOnSurface` → Group Output。没有手写替代的毛位移算法。

每个UV loop实际位于分配给该polygon的独占tile内，tile映射为全排列；因此不同polygon的BindUV岛不相交。构造留边目标为cell的0.11（float32边缘有量化），不把它当视觉贴图UV完成。全量根UV和tile→polygon映射分别保存在 `native-root-uv.raw.npy`、`native-root-uv.npy`、`tile-to-polygon.npy`；全180000根逐三角解码在 `root-uv-decode.npz`。算法按根所在polygon的少量三角形查找，未做180k×全mesh暴力扫描。

## 全180000根的实际证据

| 项目 | 实测（场景单位） |
| --- | --- |
| NEAREST初次根位移 max／p99 | 4.16748e-5／2.40274e-7 |
| 全720000点初次位移 max | 4.16748e-5 |
| 官方Deform静止根误差 max | 0 |
| 官方Deform静止全部点误差 max | 2.66560e-7 |
| 最终native Sample UV Surface.Is Valid | **180000 valid／0 invalid** |
| 静止全180000根到实际求值表面最近距离 max | 4.73708e-5 |
| 技术扰动后同项 max | 4.73708e-5 |
| 扰动后根到对应UV面目标 max | 8.21527e-5 |

最近距离是对**全部180000根**逐一调用求值body的BVH最近点，不是抽样。UV目标另按根的实际tile→polygon→triangle与barycentric重建，防止“跳到另一处表面但最近距离很小”被掩盖。几何误差阈值1e-4在验证前写入源代码，未为了通过调大。

官方 `GeometryNodeSampleUVSurface.Is Valid` 通过临时、只在内存中求值的诊断group，对全部曲线存储bool并读回。最终保存baseline.blend重新打开后又独立重跑该CPU检查，仍180000／0；见 `native-uv-validity.json`。临时诊断group不写进保存资产，不增加GPU render。

## 真实失败与精度修复：不忽略个别根

失败与旧文件保留，未删除或平均掉：

- `attempt-1/`：误认为冻结body无UV的断言停止，0次render。之后改为保留现有UVMap、新增BindUV。
- `attempt-2/`：普通tile顺序使126角ngon处float32误差放大，3/180000根bary越过预设容差，最差-0.013452；0次render即停止。高角数polygon排到UV原点附近后，该问题消除，没有放宽门槛。
- `attempt-3-pre-native-fix/`：Python容差重建和最近距离已小，但更严格的官方Is Valid发现**1根invalid**（139545），因此该pair没有算全量绑定成功。旧2张图／blend完整保留。
- 最终有界修复：仅将139545根的UV在**原polygon597524／triangle1195205内**向内部移动1.50734e-6 UV单位，保留raw值；新min bary约0.002025。没有删根、换面、改毛点或重置POINT rest。随后官方全量检查180000 valid，1e-4实际几何误差门槛也通过。源码限定若多于8根invalid就停止，不能批量掩盖坏atlas。

## 一次很小的技术形变及真实图片

只有一个拨弦爪局部shape key：椭球内立方平滑衰减，Z位移参数上限0.02；因为中心不在表面，**实际最大顶点位移0.01148665**，影响25421个顶点。6187根实际移动超过1e-6，根位移max0.01143491，证明不是官方节点静默原样传出。毛数量仍180000根／720000点。

静止、扰动两状态中，hair的 `miao_rest_position` POINT hash都与D0.1初始值相同；body的同名属性也不变。位置真实移动而rest不移动。独立hair着色器AOV读取／插值仍沿用D0.1的未证实边界，不能据CPU属性保留就宣称全部纹理防泳动通过。

最终同机位seed17／512px／32samples两张图为：

- `baseline-attached.png` 与 `baseline-attached.blend`。
- `local-paw-perturbation.png` 与 `local-paw-perturbation.blend`。

最终生成进程退出0，26.38秒；两次render分别7.25／7.02秒。**本小项累计4次GPU render：pre-fix pair两张＋修复后的最终pair两张。** 两次更早预检均未渲染；不把总数写成2。

复用已有D0.1 `named-rest-position.png` 对比最终静止图，没有第三次基准重渲染：全RGBA平均差0.00430107/255、RGB max6、4274像素有差、6像素>3、0像素>12。没有全身奶油腹部／条纹回退成统一橘毛的明显现象。技术扰动pair的133个>12像素全部在预设拨弦臂／腕ROI，较小外部差异仍可能包含灯光传播和采样／去噪；不把像素差当审美总分，也未分离重复渲染噪声。详见 `pixel-comparisons.json`。

## 复现与未验证范围

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b \
  --python design/character-sculpt-v2/d0-groom-binding.py
```

输入D0.1工程已有packed视觉纹理，无额外模型／库下载。Blender自带NumPy处理线性UV数组；像素诊断使用已有Pillow+stdlib。

主记录为 `receipt.json`，汇总与文件hash在 `final-receipt.json`。本次仅证明该冻结高密度猫体、完整180k毛绑定数据和一个很小的局部形变。没有自然拨弦轨迹、骨架／肩肘蒙皮、闭眼／头部组合、连续动作、音频时机、网页或导出验收；不能推广成任意大变形、retopo后角色或其他模型已通过。后续由非builder独立评审实际对照原图及最终两图，再决定下一项窄验证。
