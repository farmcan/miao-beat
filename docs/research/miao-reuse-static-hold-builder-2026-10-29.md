# Miao reuse · 单静态抱琴 builder 记录

日期：2026-10-29。状态：静态候选，等待三方独立 shaded gate；不是模型或动画交付。

## 输入与约束

- 猫：`artifacts/miao-reuse-v1/compat/wingit-working-native36.blend`；来自 Blender Studio Wing It! Cat 的 CC BY 4.0 优化分发版。保留原成熟拓扑、原四指、服装和护目镜。
- 吉他：`artifacts/miao-reuse-v1/instrument/classic-guitar-compat.glb`，source SHA256 `1e3da0406355be281e2442de80bd4093eba58cfda640a07a6acd53ab231b1e41`；比例与接触初值来自另一个 scout 的只读测量，不是 builder 自己宣称已通过接触。
- 环境：官方 portable Blender 3.6.23；factory startup / disable-autoexec；不运行 CloudRig UI 或 MoveAI addon。
- 只做一个主静态姿势及一次针对修复，无关键帧、无新动画、无新rig、无手臂拉长、无身体或手指重建、不触 public/ 或部署。

## 实现

通过已有 `PRP-UpperArm` 的 IK 开关、`IK-MSTR-Hand`、`IK-POLE-UpperArm` 与原来的 `FK-Thumb/Index/Middle/Pinky` 控制器摆姿势。两臂 stretch/rubber hose 关闭。左手的原四指卷曲围绕斜向琴颈；右手以松弛曲指位于弦面附近。原生闭嘴开关开启，头部只加 3°静态轻转。

吉他统一 scale 0.5，EulerXYZ=(0°,65°,0°)，location=(-.235,-.241,.235)m；不分别变形琴身/琴颈、不改弦品几何。

`static-hold-original-v1-fix1-receipt.json` 记录所有控制器、腕/肘位置、原生臂段前后长度、source hashes 和变更。源猫 base mesh fingerprint 在 pose 前后相同；new actions=0。上臂保持 .121973m，前臂保持 .122786m，原指节长度保持不变。

## 唯一一次针对修复

第一次完整图暴露导入琴对象还在 QUATERNION 模式，写 Euler 没生效，琴仍竖直；还观察到左眼小白三角。仅修正琴 rotation_mode=XYZ，使既定65°摆位生效；撤去不可靠的 pupil 独立位移，保留原眼控制值。初稿图/日志留存，未以初稿称接触已完成。

修复后的图已经实际查看。琴正常斜放，原成熟掌指和完整猫可见；但小白三角在撤去 pupil 位移后仍存在，闭嘴状态嘴线也不明显。遵守单次针对修复边界，没有继续自行试第二组pose。

## 同姿态少量配色

`finish_static_palette.py` 在完全相同 pose 上只改六个材质色：暖橘 fur_dark、奶油 fur_bright、深色工装与棕色袖口/原暗色边。原贴图通过乘色保留；没有刷橘覆盖工装假装裸猫，没有更换几何/眼形/rig。原色与暖色工作副本分别保存。

材质试验前后 pose matrix_basis hash 必须完全相同，脚本校验通过才写回执。颜色是本地试验，不代表已得到独立美术批准。

## 可审查输出

目录：`artifacts/miao-reuse-v1/static-hold/`。

- 原色完整：`original-front-fix1.png`、`original-three-quarter-fix1.png`。
- 原色局部：`original-left-hand-fix1.png`、`original-right-hand-fix1.png`、`original-face-fix1.png`。
- 暖色同姿态：`warm-front-fix1.png`、`warm-three-quarter-fix1.png`、`warm-left-hand-fix1.png`、`warm-right-hand-fix1.png`、`warm-face-fix1.png`。
- 原色场景：`static-hold-original-v1-fix1.blend`；暖色场景：`static-hold-warm-v1-fix1.blend`。
- 脚本：`design/miao-reuse-v1/scripts/build_static_hold.py`、`finish_static_palette.py`。

局部图只为检查，生产整帧约束仍要求猫/四肢/琴完整同框。没有输出生产动画帧。

## Builder 明确未通过/待判断的点

1. **脸部缺口**：左眼下方白色小三角和缺乏嘴线的闭嘴状态，不能被暖色配色或成功渲染掩盖。可能与上游 highlight/head/quality 联动有关，尚未定位；不把未验证推断写成结论。
2. **接触待独立判断**：图像中的左握颈、右悬弦可能有浮空、穿手或姿势不自然；臂长数值正常不等于接触通过。
3. **比例待独立判断**：大头小躯干与半尺度琴形成较可爱的玩具比例，但是否足够像吉他而非尤克里里，需要主任务/独立 judge 判定。
4. **上游琴表面**：原品牌与侧板材质仍是研究来源状态，不代表产品艺术已清理。
5. 无动作、音画、Web浏览器或发布验收。任何P0视觉/接触问题继续阻止交付及动画扩展。

## 冻结结论：FAIL，禁止扩动画

主任务转达 motion/contact 与 craft judge 已实际看完齐图并 **FAIL**。当前冻结 `inspection-manifest.json` 列出的全部图、两个工作副本和回执，不再改 pose 或继续渲染。第三 identity judge 的最终报告由主任务汇总。

明确失败：左手指板内部出现孤立肉块、弦在肉块上方；右掌覆盖音孔，三指垂向琴桥/琴板下方；琴相对大头/掌显得迷你；左眼下方白三角和嘴完全消失都是 P0。能渲图、臂长没变或没有改原网格都不能抵消这些问题。

这次失败属于 **builder 的触点安排、比例和成熟 rig 使用错误**，不是专业上游资产质量不足的结论。不得因此又回到 primitive 猫或另造手掌/骨架。之前的“围颈/轻悬弦”是设计目标；本轮图片没有实现它们。

### 口部：确切原值、driver 链与可推断边界

- 原始源 pose 控制器 `PRP-Head["Sealed Mouth"] = False`；builder 本轮设置为 `True`。
- 只读 `face-gap-readonly-diagnostic.json` 显示相关 mouth drivers 都是 valid/simple，没有发现“driver 缺失”。
- True 使 `GEO-head` 的 `RIG-MouthMask`、`RIG-GN-UV_Deform`、`RIG-GN-PetsMouth` 关闭，`RIG-InnerMouthMask` 与 `RIG-GN-PetsMouthMask` 开启；另联动 teeth hide 条件。这是 mouth representation/masking switch，不应在不验证其画面语义前当成普通闭嘴滑杆。
- 原始 `Sealed Mouth=False` 的 supported-runtime rest 彩图 `compat/wingit-received-materials-color.png` 有完整可见嘴部；因此上游资产本身有正常口部。回到 False 是最小的原生表达恢复候选，但当前 hold 直接回 False **没有渲染验证**，不能声称仅回 flag 已修复。优先恢复已知正常原生表情，再通过真实 mouth/lip 控制器求闭嘴，不能画新嘴遮错。

### 眼部与头转：没有做反事实实验，不补造结论

- 主 pose `FK-Head` 在原有 local-Z≈0.04324 rad 基础上增加 local-Y=-3°；source pupil location/rotation 均为0，fix1将 pupil matrix_basis 恢复为 Identity，白三角仍出现。
- **没有**实际渲染过“保持其余 hold 配置不变、只撤头转”这一反事实。因此是否撤头即可消三角仍是未知。
- 原始 rest 图没有三角，而本轮同时改了 mouth switch、Quality 1→3 和头转；不可仅凭共现把原因归为头转或上游 eye mesh。
- 只读检查另发现相机 helper 的 simple-driver patch 虽然语法simple/valid，但与实际场景相机的世界角差 **1.08858 rad**。行为等价性验证失败，撤回“这三条已完成兼容修复”的结论。它可能影响 view-dependent native modifiers，但尚未建立和眼三角的因果。

### 下一位 builder 应如何使用原成熟 rig

1. 先从 `rig.data['ui_data']` 的原生映射读出 `prop_bone` / `prop_id` / slider 文本/associated operator，结合原生 custom-shape、骨层和轴显示识别控制器；这些映射由嵌入 `cloudrig.py` 的 `draw_rig_settings()`（约1341行起）定义。官方说明：https://studio.blender.org/tools/addons/cloudrig/rig-ui 。不要凭骨名或属性英文猜语义。
2. 原胳膊 FK/IK property 已确认：`PRP-UpperArm.L/R` 的 `ik_left/right_upperarm` 原值0，本轮1；stretch从1关闭到0；`IK-MSTR-Hand.L/R` 和 pole 控制器确能带动原链。原上臂/前臂长度保持，不需要重造rig或拉长手臂。若切模式应理解原 UI 对应 snap 映射；嵌入 UI 有 IK/FK snap/bake framework，静态试验只应使用明确无keyframe的路径，不能顺手调用bake。
3. 左右 hand bones 的 rest roll 是镜像，finger/thumb 也不共享同一局部轴。先显示实际局部轴、确认每个控制器的骨链与原生关节范围，逐指检查再确定卷曲。此次一次性任意给 Thumb/Index/Middle/Pinky 固定 Euler 度数组没有形成合法握持，是失败方法，不能当成可复用抱琴参数。
4. 用吉他实际 fretboard front/back/thickness 和六弦表面建立接触边界：腕/掌放在颈侧或背侧，原三指分别跨过颈边触到弦面，拇指对侧支撑。不能让整个掌块穿到指板内再用“弦被手遮住”解释。右手掌应离开音孔中心/保留弦面间隙，指尖与琴桥关系逐视角确认。
5. 比例要连同头、手掌、琴身和琴颈一起看；骨链可达只是一条限制。若琴大到短臂不可达，调整整琴位置/抱持方式；若小到像迷你玩具，也不能为了数值可达就接受。成熟手指/拓扑应保留。
6. 恢复 source 已知正常面部与相机依赖后，再做一次有界静态接触修复并交三方；任何P0都继续阻止动画扩展。当前所有失败副本都只是研究证据，不进入public或产品资源。

## 后续有限技术恢复，旧失败证据仍冻结

按主任务澄清，造型盲调上限不应阻止已量测证明的开关/兼容纠错。后续只做了独立两角度原生脸基线：恢复原SealedMouth=False、源head/pupil/Quality，并按源相机公式同步helper局部Euler。两角度嘴恢复、眼三角消失，逐轴相机误差0；详见 `miao-reuse-face-baseline-recovery-2026-10-29.md`。没有动冻结手/琴姿态，整体接触/比例仍FAIL。这段不覆盖或删除上面的失败历史。
