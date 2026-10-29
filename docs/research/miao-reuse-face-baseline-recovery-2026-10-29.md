# 原生脸部基线恢复 · 2026-10-29

状态：技术基线恢复，尚非整体美术/接触通过。上一次静态抱琴的失败图和两个场景继续冻结；手与琴没有再调。

## 已证实的问题

只读局部检查直接比较原相机表达式的应值和 helper 的局部值，而非只比较 matrix_world：

- 应值 `camera.matrix_world.to_euler()` = `[1.41860533, -1.56e-9, .33667481]`。
- 实值 `helper.rotation_euler` = `[1.45473087, -1.83e-7, -.75136518]`。
- 逐轴误差约 `[.03612554, 1.82e-7, 1.08803999]`。

相机与 helper 均无 parent。替代 TRANSFORMS driver 的 syntax/simple/valid 不代表原语义等价；本轮不继续猜该替代实现为何偏离，而按原公式执行一次静帧同步。

口部开关原值 `PRP-Head['Sealed Mouth']=False`，失败整合把它改为True。相关 mouth drivers 全部有效；True切换Mask/PetsMouth/UVDeform表示路径，不是一个已经被验证的普通闭嘴pose。缺嘴不是因为缺失driver。

## 本轮唯一有限恢复操作

脚本 `design/miao-reuse-v1/scripts/recover_face_baseline.py` 先以禁用脚本方式打开原上游资产，精确复制原生 `FK-Head`、`Eye_Pupil.L/R` 的 matrix_basis、原SealedMouth=False、原Quality=1；再打开冻结失败场景，只恢复这些已知原生值。

三条 helper rotation driver 只在新副本 mute。每次render之前执行：

1. 设置检查相机并更新 view layer。
2. 读取 `camera.matrix_world.to_euler()`。
3. 直接赋给 `HLP-scene_camera_dummy.rotation_euler`（XYZ局部欧拉值，正是源表达式写入的通道）。
4. 更新后逐轴比较，误差必须 `<1e-6`，否则停止。

两张图的逐轴误差实测均为 `[0,0,0]`。没有执行上游Python或开启用户/全局autoexec；没有改几何/UV/原材质、没有新关键帧。原upstream与冻结失败源文件SHA前后均相同。

## 实际看见的恢复结果

- `artifacts/miao-reuse-v1/face-baseline-recovery/face-baseline-front.png`
- `artifacts/miao-reuse-v1/face-baseline-recovery/face-baseline-three-quarter.png`

Builder已实际查看：两个角度原生嘴部都恢复为可读的微张表情，原左眼下方白三角均消失。这里同时恢复了已知正常的mouth、head/pupil、Quality和相机路径，因此不能把消失原因唯一归给其中一个参数；没有再开单因素渲染矩阵或继续刷参数。

工作副本：`face-baseline-recovery-native36.blend`。执行/相机逐轴验收/SHA回执：`face-baseline-recovery-receipt.json`；日志：`recover-face-baseline.log`。

这是源成熟脸部功能的恢复证据，不是新的闭嘴/侧视设计交付；它支持先正确使用专业rig，不能据失败整合弃用源资产。

## 手部只读测量与下一步边界

手/琴仍沿用被冻结的失败姿态。只读诊断 `static-hold/static-hold-readonly-technical-diagnostic.json` 已记录所有 DEF-Hand/Thumb/Index/Middle/Pinky 的真实世界轴、head/tail、原长/当前长，以及真实吉他网格的弦面与颈面射线点/法线。

- 吉他颈方向为原生+Z经当前整琴变换得到的世界方向；板宽方向必须从原生+X同样变换，不能凭近似向量手填。本轮旧姿态使用了错误近似方向并给finger固定Euler数组，不能复用。
- 当前local z=.70附近实际颈正面 y≈-.274099、背面 y≈-.261440，正面法线≈`-Y`，不是一张无厚度的接触平面。
- 左中指末骨端的最近表面 signed distance约-3.46mm，与评审看到的板内肉块相符；骨端不是皮肤，后续必须用实际手皮肤/指腹表面检查接触，而不是把末骨接近字符串当成通过。
- 右指骨端已从源吉他local z≈.328延伸到.179，支持评审认为垂指过低；仍须在实际音孔/桥/弦边界上重新确定静态指腹范围。

下一轮应先确定整琴与头/掌的比例，再用真实板宽/厚度/弦法线订出每个指腹接触点，通过原生控制器与真实局部轴求解；无证据前不再猜60°卷曲，不拉长手臂、不重造手掌/骨架。整体接触和比例必须再次交独立三角色静态gate，通过前不扩动画。
