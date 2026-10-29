# 单次原 rig 整体粗姿势 · 实测 FAIL 并冻结

2026-10-30。按 root 授权执行唯一整体方案和每手一次解析退出；未进行参数网格、第二姿势、卷指求解、改色、建模或动画。**结果 `FAIL_COARSE_POSE_FROZEN`。** 已实际查看同一姿势的 front 与 3Q，均标 technical study / not accepted；新原生副本、回执与脚本全部落盘。

## 执行与证据

- 脚本：`design/miao-reuse-v1/scripts/build_whole_rig_coarse_diagnostic.py`。
- 回执：`artifacts/miao-reuse-v1/whole-rig-coarse/whole-rig-coarse-receipt.json`。
- native：同目录 `whole-rig-coarse-diagnostic-native36.blend`。
- 完整图：同目录 `coarse-front-NOT-ACCEPTED.png`、`coarse-three-quarter-NOT-ACCEPTED.png`。
- SHA / 文件清单：同目录 `inspection-manifest.json`。
- 输入：immutable upstream + face-baseline-recovery native；输入 SHA 前后相同。官方 portable Blender 3.6.23，factory / disable-autoexec；没有运行嵌入脚本或 MoveAI addon。

实际调整 Torso +5°、Chest +3°，肩根绕 world Z 左 +8° / 右 −8°，均无肩平移或 scale。琴 scale=.70、颈仰20°、面板向上10°，随后沿实际面板外法线一次定位琴背与 evaluated 腹部。手指恢复 source 的 FK matrix_basis；不是继续旧三组 curl。原生 head/pupil/mouth 恢复状态保留，头随胸自然继承，mouth=False / Quality=1。

手 frame 由本次琴表面方向构造，每侧仅一次；通过 `Hnew H^-1 C` 映射到 IK-MSTR-Hand；然后各作一次实际支撑皮肤的保守外移。没有因未到目标而重复调整。

## 真实骨长、腕位与核心：失败没有被目标值掩盖

| 检查 | 左 | 右 |
|---|---:|---:|
| 实际固定支撑皮肤点 | 205 | 205 |
| 唯一解析退出量 | 105.400 mm，沿颈侧横轴 | 78.703 mm，沿面板外法线 |
| 最终实际肩腕距离 / 原两段臂长 | 99.99998% | 100.00001% |
| 上臂 pose/rest | 1.00000006 | 1.00000000 |
| 前臂 pose/rest | .99999976 | .99999964 |
| 实际腕距目标 | **17.206 mm** | **104.905 mm** |
| 实际肘屈曲 | .361° | .361° |
| 实际腕弯折 | 143.547° | 71.000° |
| 实际前臂相对腕 twist | 131.202° | −103.968° |
| 退出后实际核心对支撑平面最小间隙 | **−12.380 mm** | **−66.680 mm** |

骨长未改变，而 arm IK 对超出可达域的目标夹在几乎完全伸直的位置。因此不能报告 desired wrist 已到位；轴方向误差虽很小，也不能抵消位置误差与极不自然的肘/腕。reach ≤95%、肘35–130°、腕弯折≤35°、twist≤60°和核心2mm门均未满足。

**这次保守支撑平面构造有明确局限**：205点包含 Sleeve / Forearm / Carpals，要求全部支撑区域位于同一琴外半空间，比“沿实际弯曲琴壳存在外部路径”更严。其105/79mm退出量不是专业手必须移动这么远的证明；只说明本次方向与 frame 选择不能同时满足所设外置半空间和原臂空间。不能用它断言完整 rig 所有自然抱琴姿势无解，或据此要求重造源身体/手。

## 完整几何与可见结果

| 实际 evaluated 对象 | 对琴 BVH triangle overlap 对数 | 内部 envelope 采样 | 最近 vertex→triangle |
|---|---:|---:|---:|
| GEO-body | 0 | 0 | 5.000 mm |
| GEO-head | 0 | 0 | 11.761 mm |
| GEO-arms | 497 | 95 | .113 mm |
| GEO-collar | 175 | 6 | .116 mm |
| GEO-hands | 1000 | 270 | .065 mm |

前臂和整手 envelope 最深入琴约47.46 /47.49mm。报告保留 BVH / envelope 作为拒绝证据；零命中不能独立作为完整碰撞 PASS。腹部与头的采样/相交未发现碰撞，不代表袖口/衣领通过。

实际看图：脸部嘴眼仍完整；正面与3Q能看见袖口、前臂直接经过琴板/琴颈，腕部接近完全拉直，手从侧面几乎叠成单块长条，未形成自然承托。这是当前粗摆的明显回退，不应称“手指恢复源 pose 就自然”。图像与数值一致拒绝本次整合；本轮没有进行手指接触操作来掩盖它。

每次 render 前 helper 局部 Euler 直接赋 camera 世界 Euler，逐轴误差均0；同一 pose 仅两视角，没有参数渲染矩阵。原 source、旧 FAIL 和 recovered native 均未覆盖；只增加独立失败副本及诊断文字对象，未改原猫/琴 mesh/material。

## 冻结与结论边界

本候选 FAIL，手指接触未尝试，配色/动画仍禁止。停止本轮，不另选 frame、不扩角域、不缩掌/拉臂、不重建几何。可交非 builder 查看实际结果与本方案局限；不能把“上身已有8°前倾仍失败”升级成“上游专业 asset 不适用”，因为本次整手 frame 与保守退出构造本身也已被实际图否定。
