# KeyForty 独立键盘静态分支 · prop与唯一摆位数值

2026-10-30。与吉他分支独立。本阶段复用 CC0 Innerscene **Key Forty - MIDI Keyboard** 与 CC BY WingIt 原生猫。**单prop真实图已出、待独立craft；只读单一完整摆位数值可达，尚未出整猫灰图 / 未获三角色静态验收。** 没有新建角色 / 琴体，没有键盘或头动作，没有新actions；源文件不覆盖。

## 单prop实际检查

在作者支持的 portable Blender3.6.23、factory-startup、disable-autoexec 下实际导入GLB；未执行来源脚本，没有插件。原GLB为734,812B，SHA `346f1f4ae12154dd7757e599abc0d3c285dc7aa61648e73c9c8bbc6c9e289a62`，前后不变。**40白 + 28黑键，68键全独立；85mesh、26,140tris、0actions。** 保留同一文件中的原PBR与4张packed图，不改变原材质。

![真实单prop](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/prop/prop-three-quarter.png)

![原生键面细节](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/prop/prop-keys.png)

已实际看这两张：有圆角壳体、键端倒角、清楚的独立黑白键、后控制条；材质朴素，尚不能自称精致终稿。可交独立craft判断适用性。native仅为导入与检查相机 / 灯光的3.6工作副本：`artifacts/miao-reuse-keyboard-v1/prop/keyforty-import-native36.blend`。逐键bbox、材质、尺度在 `prop-receipt.json`。

已实际看原线上钢琴图 **`public/character/whole-piano-v3/idle.jpg`** 与 `artifacts/miao-reuse-v1/source-rest-baseline/source-rest-original-three-quarter.png`。原图是橘猫、短圆手与小木键盘；stock猫是成熟飞行员猫，脸 / 服装 / 色彩有差异，允许模板差异不等于精致、可爱和完整手指已经通过。三角色整猫门槛仍须比较原图和实际新图。

## 唯一摆位的只读数值

没有先把720mm整琴任意缩小，**scale=1**。原白键宽15.3925mm、节距16.375mm、中央source14–21八白外缘130.0175mm。将琴整体绕Z转180°，使白键前缘朝猫、控制条向观众远侧；猫不必越过210mm机身去摸键。统一平移 **(-.03325,-.405,.270)m**，中央八白居中。

源肩坐标约 **(±.112789,-.025704,.392856)m**；每侧原臂长 **121.973 + 122.786 = 244.759mm**，禁用stretch / auto rubber hose。手掌朝下以source原生 FK-Middle2 的palmar轴相对ORG-Hand校准，不把Hand+Z盲当掌面。index仅绕各自原生局部+X作18°/27°两节放松卷曲，不统一所有指骨角度，其他手指保持源放松形态。只为一组世界触点作确定性的腕位平移，无姿态参数网格搜索。

| 项目 | L | R |
|---|---:|---:|
| 实际腕m | (.105582,-.210315,.368127) | (-.105582,-.210315,.368127) |
| 实际腕距 / 原臂总长 | 76.156% | 76.156% |
| source中央8键中目标 | Ivory piano key.014 | Ivory piano key.021 |
| 实际index最下皮肤点m | (.0573125,-.320000,.330000) | (-.0573125,-.320000,.330000) |
| 目标白键真实top | .328000m | .328000m |
| 实际皮肤到目标键净空 | 2.000mm | 2.000mm |
| 相邻白键皮肤投影最小净空 | 3.208mm / 10.911mm | 3.208mm / 10.911mm |
| 双手实际三角 vs 键盘有限85组件三角交叉 | 0 | 0 |

指腹选实际evaluated `GEO-hands` 中 `DEF-Index2` 权重>.6的40个皮肤顶点；不是骨尾代替皮肤接触。虽圆指腹在邻键有XY投影，邻键下方仍有曲率净空。这个数据支持静态单键悬停可用，**不是已验证独立按键行程 / 相邻键不会被完整下压的结论**。目标最近邻组件的3D最短间隙约2.699mm，白键正上方最低投影间隙3.208mm；其他邻键更远。

同时使用实际所有手三角与每个独立键 / 外壳 / 控制条的有限BVH，未用205点同一无限平面。`GEO-body`、`GEO-head`、`GEO-arms`、`GEO-legs` 的实际三角与键盘交叉均0；后续图仍必须查视觉腕折、手遮挡、脚 / 头比例及全身。probe尚未保存native或渲染整猫，不是已接触通过。

猫工作源SHA `5aba4ac3e648a0659aaae80e507885fd3ecf3ede395d035c30cb5d74e34b9593`；probe前后不变。原猫已有27个上游actions，本分支 **new actions=0**，未给任何action加keyframe。完整数值：`artifacts/miao-reuse-keyboard-v1/probe-receipt.json`、`source-fit-measurements.json`。

## 权利与推进边界

键盘作者／模型／材质／四张图：Innerscene完整文件CC0声明；[作者页](https://www.innerscene.com/tools/library/3d-parts/key-forty-midi-keyboard-0d9952a4)、固定原包、`SOURCE.json`、`LICENSE-EVIDENCE.txt`与条款均在 `artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/`。没有从MIT推导模型权利，没有另引外部贴图。猫、纹理与rig归属继续沿WingIt既有CC BY provenance，不把stock写成原创。新分析代码、相机、灯光按项目MIT；原包不可覆盖。

脚本在 `design/miao-reuse-keyboard-v1/`：`inspect_render_prop.py`、`measure_source_fit.py`、`build_keyboard_static.py`。所有Blender同agent顺序单进程。下一步严格为 **prop独立craft → 同一候选灰静态三角色 → 同pose默认色三角色**，不提前美化 / 动画，不更改guitar scene或public。主任务统一管理持续状态；该本地研究未公开部署。

## 灰静态已出 · 仍待三角色

prop经非builder `keyforty-prop-independent-craft-judge-2026-10-30.md` 条件GO，root授权按同一唯一摆位出灰图。现6张真实native整场景相机图齐：`gray-static/front.png`、`three-quarter.png`、`face.png`、`left-hand.png`、`right-hand.png`、`hands-top.png`。我已实际看完6张；front / 3Q含完整连接猫、双臂双手与全键盘。其余是同场景诊断相机近景，不是可拼接独立肢体资产。原眼口信息以native材料图保留，只通过Blender原生compositor转灰，未统一灰材质抹去面部细节。

pose SHA **`4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be`**，所有相机render前显式同步world camera helper，render前后posehash一致。3.6 native `artifacts/miao-reuse-keyboard-v1/gray-static/keyboard-gray-native36.blend`；整包路径和逐图SHA在 `artifacts/miao-reuse-keyboard-v1/inspection-manifest.json`，`gray-static-receipt.json` 保留数值。没有新actions / keyframes。

**实际图中未解决项：** 原键盘不带独立stand / 桌面，此次悬置，承托仍未处理；密集长键列在全身图中偏细；stock表情与橘猫原图有明显差异、手指材质与局部mesh层次仍须看原图独立判断。没有为了自评通过追加几何 / 支架 / 调色，也未启动默认色或动作。已交root安排三非builder灰gate，候选图未被自称验收。
