# Wing It 原生身份适配 · 只读诊断

2026-10-30。任务是辨别哪些改善能由成熟作者资产少量适配完成，哪些会变成被禁止的重建。已实际查看 `public/character/whole-piano-v3/idle.jpg` 与 `artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/front.png`；未改变姿态、材质或场景，未生成新候选图，更没有艺术 GO。

**结论：可以少量改善飞行员猫的配色、配饰与视线，但不能靠这些改动得到原图的矮梨形裸毛橘猫。若目标仍是原图外观，优先换更合适的成熟模板；不要通过剥衣、拉胖身体或重造脸/手来强逼本模板。** 如果接受独立的暖色飞行员候选，才有理由安排一次范围明确的原生控制/材质适配，然后重新三角色静态 gate；当前诊断不是允许动画扩展。

## 实际运行与证据

- 只读脚本：`design/miao-reuse-keyboard-v1/inspect_identity_adaptation.py`。
- 官方 portable Blender **3.6.23**，`--factory-startup --disable-autoexec --python-exit-code 1`；以 `open_mainfile(..., use_scripts=False)` 打开冻结 native。
- 输入：`artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/keygroup-lift-color-native36.blend`，SHA256 `ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6`。
- 前后源文件 SHA 一致，pose SHA 前后一致为 `6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b`；0 pose application、0 frame_set、0 renders、0 native saves、0 embedded Python execution。没有给 rig 赋 action。
- 回执：`artifacts/identity-adaptation-2026-10-30/native-identity-readonly.json`，含112个非乐器/环境mesh/curve条目、31材质实际节点连线、461个有关骨条目、现有action与原生属性。日志 `artifacts/identity-adaptation-probe.log`。原生空 Render Result 的颜色空间枚举告警不用于资产质量判断。

## 可少改的部分：具体原生入口

| 对象 | 只读证据 | 合理的小改边界与未验证项 |
|---|---|---|
| 护目镜 | 独立 `GEO-goggles` mesh，1226 base vertices；四个材质 `cat.metal/goggles/goggles_red/goggles_glass`。独立成熟配件，不是头皮mesh。原生 `Goggles/Goggles_Front/Goggles_Lense_Thickness` controls 存在。 | 可以在派生副本隐藏该配件以减少飞行员识别符，或改现成材质；没有查到作者“无护目镜”显示开关。隐藏后的完整头顶/接缝尚未渲染检查，不能保证无缺面或新的 P0。 |
| 毛色 | `cat.fur_dark`、`cat.fur_bright` 和 `cat.fur_spikes_bright` 的 Principled Base Color 均由 packed **4096² `cat.base_color`** Image Texture 直接连入。 | 改未连接的 Base Color 默认值不会生效。可以在派生副本插入可追溯的 tint/ramp 或修改纹理副本；原texture保持不可变。现成灰/白图案变橘/奶油仍是原作者的图案与体型，不等于原图虎斑、短绒和梨形轮廓已恢复。 |
| 眼白/瞳孔色 | `CAT-eye_white.L/R` 使用纯 Principled `light blue`（当前RGB约 .05716/.39188/.77252）；`CAT-pupil.L/R` 使用独立 `cat.pupils` 近黑材质。 | 将眼白改暖白是直接可达的节点改色，可减少大块青色警觉感；并不把源相机相关曲线眼系统变成原图立体白眼球。不得为了复刻而新造眼球/眼眶。 |
| 视线与瞳孔 | 原生 `Eye_Pupil.L/R` 位置/旋转/缩放均未锁，均有指向相应 `CAT-eye_white.L/R` 的 **Shrinkwrap** constraint。相关CAT眼网格保留作者 GN-AvoidClipping、Shrinkwrap/Extrude 路径。 | 可把原生 pupil control 的有限变换作为侧视/较大瞳孔的候选入口，但本次未应用变换，也未证明某个数值范围的画面安全。必须保留源表情系统、相机 helper 语义和双眼可读性；不能只凭控制器存在签“侧视已实现”。 |
| 眉/鼻 | 原生 `Eyebrows_Mid`、`ROOT-Eyebrow.L/R` 控制及 `cat.eyebrows`、`cat.nose`、`cat.nose_dark` 独立材质存在。眉有左右作者Mask显示开关。 | 有界眉位/色变化可以单独评估神态；鼻为粉色现成材质，能直接改色。不能把细微眉色改变包装成整体可爱/酷已通过。 |
| 嘴 | `ACT-Mouth_Move`、`Mouth_Top.M`、`Mouth_Bot.M`、`ACT-MouthCorner.L/R` 等成熟控制存在，嘴中心骨受多个作者 ACTION constraint 驱动。`PRP-Head['Curvature']` 0–5，描述为“Brings the inner edge loops of the lips closer together”；当前5。 | `PRP-Head['Sealed Mouth']` 当前False，是口部表示路径开关，**不是**普通闭嘴pose。旧 `smile close` 252通道移植已有眼鼻 P0，继续冻结，不能重复套同一pose。单个原生lip control若要试验，必须先明确其作者驱动因果，不能跳过完整脸复审。 |

原生 `PRP-Head` 中 `Left/Right Eye`、`Left/Right Highlights`（0–3）、左右眉、`Tufts` 等开关真实存在。`Properties_Character_Cat['2D Face']` 的作者说明仅为 **Display the 2D face in the viewport**；不能把它当成经过验证的渲染风格或漂亮脸切换。Quality=1 也不应为换造型而盲改。

## 衣服不是盖在完整裸猫上的可脱壳

实际mesh和材质面证据：

- `GEO-body` 是单一连通mesh，580 base vertices/578 polygons；438面 `cat.suit_blue`、140面 `cat.suit_red`。它就是躯干表面，不是一层可去掉后露出另一个腹部的衣服。
- `GEO-arms` 两个连通部分，678 vertices，400面蓝衣、264面红袖；`GEO-legs` 两个连通部分，726 vertices，712面全为蓝衣。隐藏这些对象会把相应肢体一同去掉。
- `GEO-hands`、`GEO-head`、`GEO-tail` 是有fur材质的分立作者部件；没有找到另一套完整裸毛躯干/胳膊/腿对象。`GEO-body.Chest_* / Squash / Stretch` 等是无材质作者辅助形状，不能拿它们冒充独立finished裸猫资产。
- `GEO-collar/pockets/zipper_handle/zipper_line/badges/shoes` 是额外成熟服装细节；即使隐藏其余配件，`GEO-body/arms/legs` 的领口、袖口、裤形、窄身比例仍在。把蓝衣染橘，依然会读成橘衣飞行员。

因此“脱衣再染橘”不是现有模板的简单开关；若要原图宽下腹、短腿圆爪和头腹比例，需要变更成熟body/arm/leg基础造型与服饰拓扑，触及用户要求禁止的另一条 bespoke 重建链。不能这样证明复用路线完成。

## 静态差距与下一步选择

实际原图是下宽上窄的巨大暖橘腹部、小头/圆方脸、短融入式胳膊、三趾毛绒脚、温和侧视；当前模板是大头小躯干、制服/靴子、青色大眼与小瞳、微张嘴、平面线条感更强。颜色/护目镜/瞳孔虽可少改，**轮廓、头腹比例、眼部表示和服装实体仍决定其是另一个角色**。

可执行选择：并行检索更接近宽胖裸毛轮廓、真实成熟手/rig且许可可验证的新模板；当前实验页保留独立身份和有限签署。只有在明确接受本模板作为另一角色时，才做一次“隐藏护目镜＋暖色材质＋有限原生视线”的小改候选并跑灰/色三评；不为追原图接着造腹部、球眼、毛脚或分离新胳膊。没有新图之前，本报告不判断该小改是否真的更漂亮，也不扩大现有 A/C4 或吉他动画授权门禁。
