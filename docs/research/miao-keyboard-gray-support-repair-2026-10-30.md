# KeyForty 灰静态 · 有限承托修复与原生渲染细分恢复

2026-10-30。此前identity / craft因“键盘无承托、猫无落地线索”而HOLD；motion仅签ready-pose，不是按键或动作。root随后明确授权一次环境修复，另基于只读质量证据授权恢复作者已有render细分。**当前8张新灰图与native已齐，已实际查看、重开核验通过；等待三位非builder复审。没有先出默认色或动画。**

本轮没有移动猫 / 手 / 键盘，没有重建基础mesh、改脸 / 瞳 / 口或拉长骨骼。统一pose SHA仍为 **`4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be`**；猫+键盘原始mesh hash前后相同，键盘各world矩阵、rig world矩阵相同；new actions=0（源27actions保留）、无新keyframe。

## 交接图与native

全部新输出在 `/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/gray-supported/`。`inspection-manifest.json`固定8图 / native / 审计SHA，保留上轮灰manifest不覆盖。

![完整正面](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/gray-supported/front.png)

![完整3Q](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/gray-supported/three-quarter.png)

另有 `face.png`、`left-hand.png`、`right-hand.png`、`hands-top.png`、`feet-support.png`、`support-side.png`。我已实际看完8张：前/3Q保持完整连接猫、两臂双手、全键盘；桌脚和靴底有同向软接触影。side是承托间隔诊断相机，尾端在画面边缘被裁，不作为完整生产帧；front/3Q才是完整门禁主图。图像没有新缺眼 / 无口 / 破手P0的builder观察，但不能代替独立艺术判定。

3.6原生 `keyboard-supported-native36.blend` SHA **`31c427e53b47eb55251d0f25f9157545d0f81558183822837945c848085a1b9e`**。`native-reopen-verification.json`实际重开PASS，Quality1、use_simplify=False、source viewport驱动0 / render2均保存正确，没有意外静音的细分level drivers或临时proxy节点；25桌mesh的原始坐标 / 拓扑fingerprint与原GLB完全相同。

## 成熟CC0桌：原生导入与单一等比摆放

复用 [COMMON 280 communal work table — Innerscene](https://www.innerscene.com/tools/library/3d-parts/common-280-communal-work-table-0e45ba93)。原包2,038,380B，SHA **`27ba0fdfd0afde9fec6ccc6306bc0e0b2e3f6eb32d2820fa609f70c1301bceca`**，前后不变。原文件 / 来源HTML / receipt / glTF结构在 `artifacts/licensed-keyboard-support-2026-10-30/`。完整版权字段声明Innerscene原创、完整文件CC0；实际25mesh使用4PBR、6embedded图，无外部贴图URI、无skin / animation / rig-code。未把代码MIT当模型许可。

先在3.6 factory / disable-autoexec导入、核尺寸与材质，真实prop图为 `artifacts/miao-reuse-keyboard-v1/support-prop/table-author-materials.png`，已实际看。双oak面板、中心线槽、石墨腿、细木grain与圆角保留。原桌**6腿而非4腿**，没有删除中腿或线槽去凑预设。

实测原尺寸 **2.8 × 1.069 × .750999987m**。高细分匹配proxy中猫靴底floorZ为 **.000945851614m**；固定keyboard底为 **.270000010729m**。唯一等比scale **.358261203365**，计算为两者高度差 / 真实桌高。成桌宽 **1.00313136m**、深 **.38298121m**、高 **.26905416m**；比预估的.70–.78m更宽，原因是实际floor接近0而非.06m。不能靠压宽、切腿或暗移猫 / 琴让数字满足预设。

桌中心XY与keyboard外壳bbox中心一致，约 **(-.03325,-.405)m**。全部25对象接受同一uniform scale + translation，没有非均匀瘦身。两oak bank各3个真实垂直ray样点与keyboard底面接触误差最大 **0.0000894mm**；中心原线槽保留，不虚称桌面全连续。6个glide底对floor误差约 **0.000000058mm**。真实render-matched猫几何对各桌组件的有限三角交叉为0；检查对象清单与bbox见 `supported-receipt.json`。地面是唯一新增简单环境平面，不是新建桌架 / 角色。新增柔和contact shadow解释落地，没有用阴影贴片代替桌。

## 质量设置口径：先披露、再有界恢复

只读 `support-prop/frozen-cat-settings-audit.json` 发现：Quality=1（Default），多数GEO Subsurf的 viewport `levels=Quality-1=0`，`render_levels=2`。进一步 `render-geometry-equivalence-audit.json` 显示原工作scene **use_simplify=True、viewport与render cap均0**，故实际灰render也被压到0。这解释了部分指面 / 袖口折线，不能拿MoveAI优化版最低LOD当最终工艺。

经root明确新增授权，只在新副本 **use_simplify=False**，不升Quality，不改render_levels、mesh、head / pupil / mouth / pose。先出唯一 `render-quality-diagnostic/native-render2-front.png` 并实际看，眼圈 / 双瞳 / 高光 / 鼻口牙均正常，袖口和指面更圆顺，未观察到新P0，才用于本次支持修复批图。没有扫Quality参数或开启脸重建。

所有8次camera render前显式同步helper，逐相机max error **0**；posehash前后完全相同。灰仍为native材质输出后的原生RGBToBW compositor，不抹掉眼口信息；默认色只应在三评放行后旁路灰节点。

## 接触重新核对：不沿用视口0的2mm冒称render2

Blender handler尝试未取得独立RENDER depsgraph，只得到VIEWPORT；**直接render mesh点数source_gap保留**。使用独立、未保存的测量snapshot：show_viewport匹配show_render，Subsurf levels匹配render_levels2，暂时静音level driver；两个 GeometryNodeIsViewport 输出暂接False以匹配render context。测完恢复所有驱动 / modifier / node链接，再保存原工作设置。源码与native SHA未变。方法和限制在 `support-prop/render2-matched-proxy-fit.json`，不称直接捕获了RENDER depsgraph。

| 项目 | 原cap0测量 | 恢复render2的匹配proxy |
|---|---:|---:|
| hand总vertices / tris | 1138 / 2268 | 18148 / 36288 |
| 每侧Index2皮肤点（权重>.6） | 40 | 697 |
| 最低皮肤z−目标白键top | 约2.000mm | L2.90480 / R2.90474mm |
| 指腹投影到目标白键真实表面gap | 约2.000mm | L2.91261 / R2.91255mm |
| 最近邻白键投影gap | 约3.208mm | L3.67761 / R3.67752mm |
| 另一相邻白键投影gap | 约10.911mm | 约12.294mm |
| 双手全三角 vs 有限85键盘组件交叉 | 0 | 0 |
| body/head/arms/legs/shoes vs keyboard | 0 | 0 |

所以当前1–3mm静态悬停目标在匹配proxy仍成立；不是已经接触 / 下压，也不是邻键动态安全证书。最近邻比目标仅多约.765mm的垂直余量，未来不能整手下沉去假装独立按键。此前76.16% reach、原骨长和腕位保持不变。

## 权利、脚本与下一步

模型/材料/纹理：猫CC BY来源沿既有`licenses/CAT-CCBY-ATTRIBUTION.md`；KeyForty完整GLB CC0；桌完整GLB CC0，证据新增 `licenses/TABLE-CC0-EVIDENCE.json` / `TABLE-SOURCE.json`。原包均不可覆盖。环境平面 / 材料、灯光、审计和准备代码为项目原创MIT，`licenses/MODIFICATIONS.md`逐项记录，不将成熟上游建模冒称原创。没有安装 / 执行原插件或embedded Python；所有Blender同agent单进程顺序。

本轮脚本：`inspect_table_support.py`、`audit_render_geometry.py`、`restore_native_render_diagnostic.py`、`measure_render2_fit.py`、`build_gray_supported.py`、`verify_supported_native.py`，均在 `design/miao-reuse-keyboard-v1/`。

下一步仅交三位非builder看原piano、当前完整front/3Q、face/双手与feet/support证据，判断场景P0是否关闭。默认色、八键独立动作、press/release、头眼响应、Web/手机与产品交付均未开始或未验证；未改guitar scene / public、未发布。
