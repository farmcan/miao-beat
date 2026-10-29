# 原 rig 整体粗姿势：只读链诊断与单次提案

2026-10-30。Builder 诊断，不是新静态通过。已读 identity / craft / motion 三份独立 FAIL，并实际查看冻结诊断 front。**本阶段只读两个 native；pose 修改、native 保存、渲染均为 0。** 上轮 FAIL 只否定固定手 frame + 局部卷指方案，不否定专业 source。

## 实测控制链

执行脚本：`design/miao-reuse-v1/scripts/inspect_whole_rig_chain.py`。证据：`artifacts/miao-reuse-v1/whole-rig-diagnostic/whole-rig-chain-readonly.json`；官方 Blender 3.6.23 factory / disable-autoexec，两份输入 SHA 前后相同。没有执行内嵌 CloudRig / lighting 代码。

| 部位 | 原生可用链 / 控制器 | 本次读取所得 |
|---|---|---|
| 上身 | `root → MSTR-Torso → MSTR-Chest`；`MSTR-Hips` 也在 Torso 下 | Torso / Chest 有作者 custom shape，无自身约束，旋转/平移未锁。源与失败稿两者 local Euler、location 都为 0；整体前倾尚未验证。胸 local X 约等于 world +X，可用正 X 小角使上身向前 −Y 倾。|
| 肩根 | `MSTR-Chest → P-ROOT-UpperArm.L/R → ROOT-UpperArm.L/R → ORG-UpperArm` | 两级肩根均有 cube 控制形状、无自身约束；源与失败稿旋转和平移均为 0。原肩在 (±.11279, −.02570, .39286)m。不需要另造肩骨。|
| 手臂 / 肘 | `IK-UpperArm → IK-Forearm`，Forearm 二骨 IK 指向 `IK-Hand`，pole 为 `IK-POLE-UpperArm` | pole 控制仅平移，旋转锁定；原两段长 .12197337 / .12278579m。**原 IK 没启用角限位**，不能以求解成功证明自然关节。|
| 手腕 | `P-IK-MSTR-Hand → IK-MSTR-Hand → IK-MSTR-C-Hand → IK-Hand`，ORG-Hand 最终复制 IK | master 有完整平移/旋转。parent switch=0 时跟 root，胸动不会自动带着腕一起前移；必须胸先定位、再用实际新肩重算腕。继续使用已验证 `Cnew = Hnew H^-1 C`，而非混淆 master 与 ORG frame。|
| 头 | `Chest → ROOT-Head_Hinge`；`FK-Head_Hinge` 原生 hinge=0 时继承该根；随后 `FK-Head` | 源 head 小 roll 2.477635°、hinge=0；失败稿已恢复同值。此次保持这些局部值和 pupil / mouth，不再盲改脸。头随轻微上身运动是否碰琴，要用实际 geometry 检查。|

还发现 MoveAI 收到版的六条 arm `ORG-UpperArm/Forearm/Hand` 的 **Copy Transforms IK driver expression 是常数 `1.0`**，虽然变量还指向 PRP 的 ik 开关；静态导出的源缓存 influence 为 0，失败稿为 1。因此不能声称仅设 PRP ik=0 就可靠回 FK。本提案保留 IK=1，不切 FK，不改这六条表达式，按最终 evaluated ORG 链验证。stretch 则仍由 `1-stretch` 驱动 `IK-STR-UpperArm / Limit Scale`；继续设置 stretch=0 并实测骨长，而非直接相信 IK constraint 的 `use_stretch=True` 字段。

## 唯一粗姿势提案（尚未执行）

从已恢复脸的 native 新副本开始；默认材质、source palm/finger geometry 不动。先把旧实验手指恢复源 pose，避免将那组三组 curl 当成天然握持。只做一套整体姿势，次序是 **胸肩 → 琴刚体 → 掌腕核心 → 必要接触**，不做网格扫描或逐指角度搜索。

1. **上身**：Torso local X +5°、Chest local X +3°（总前倾约 8°）；Hips、root、腿与脚源局部值保持。肩根只允许绕 world Z 对称内收约 8°，源平移/scale 保持，不把肩根平移当作延长臂。头局部、mouth=False、Quality=1、pupil 保持恢复基线。这里的角度是一次作者姿势选择，不是已经实测可行的 source 极限。
2. **琴**：保持统一 scale=.70。长轴从当前仰角15°改为20°；面板绕长轴向上抬10°（当前 world front −Y 的法线获得小幅 +Z 分量），让掌腕从外侧进入，而不是两手从琴板上方勾下。只允许一次刚体贴靠：琴背在实际衣服腹前留 3–8mm；头/颈不得为了构图穿入。琴的位置由该背面与腹部关系定位，不再死守旧 loc。无后续比例扫描。
3. **双掌先行**：左掌在真实颈背 / bass 侧外缘，长指横过颈宽；右掌在真实弦区外侧，指向琴桥方向，前臂自然跨琴上缘。握颈可落源琴 z=.62–.78m 的颈段，右准备可落 z=.26–.38m 的弦段；这些是可选**表面区域**，不是必须命中的旧 3D 点。用当前真实皮肤与局部表面法线确定 palm frame；一次定向后，沿外法线作一次最小整手退出，令固定掌腕核心至少留 2mm。左可沿颈侧边退出，不能以 front −Y 单方向冒充绕颈。
4. **肘与腕**：pole 依实际 shoulder–wrist 平面放在外下侧，保持肘向外下而非翻向头；不旋转锁定 pole。每侧实际 reach ≤95% 原两段臂长、长度比误差 <1e-4；自定保守肘屈曲 35–130°、腕弯折 ≤35°、相对前臂 roll ≤60°。这是本次诊断范围，非作者公布解剖限位。若需要超界就判该粗姿势失败，不借无原生 limit 继续拧。

上述第三步不是无界优化：每侧只接受一个由掌面/颈面方向构造的 frame 和一次皮肤支撑退出量；若与 reach / 角域矛盾直接停止，不反复换 frame。胸肩和琴选择也是一套，不向外扩参数域。

## 可证伪的门和停止条件

- **核心先行**：左右真实固定掌腕选区必须各非空（已知基线每侧 205 支撑顶点），报告实际顶点与三角数、最小间隙和最深穿入。使用真实 evaluated 三角，不能用 wrist 中心、骨尾、代理球或正面投影代替。任一固定核心入琴 ≥0.5mm、三角相交，或上述 reach / 骨长 / 关节超界，停止 finger 操作。
- **整体碰撞**：同一候选检查琴与头/颈、工装躯干/袖口、双前臂的实际三角交叉和内部采样；头至少 5mm、琴背衣服 3–8mm。接触区域之外不得互穿。ray-envelope 只能拒绝；零命中不能单独命名 PASS。孔洞/开放曲面无法判 inside 的区域标 UNKNOWN，结合三角交叉与可见侧面证据，不默认为清空。
- 核心成立才允许一枚左指腹轻触真实弦面、左拇指在真实颈背、右单拇指离弦约3mm；先用关节轴/皮肤证据选择一次姿势，不再统一 curl 或两节末端逐指搜索。其他指自然留在琴外。接触不成立也如实 FAIL，不因某 pad 小误差掩盖核心。
- 下一阶段最多一张完整粗姿势图，带数值状态的 technical-study 标记；数值与图矛盾即 FAIL/UNKNOWN。它只核对整体摆持与接触前提，不作美术交付。P0 未过不配色、不美化、不动画；若此一整体方案仍无自然外部路径，冻结并交独立判断，不继续叠补丁。

**当前结论：原 rig 的整体自由度存在，足以支持这一次有边界粗姿势诊断；可行性尚未验证。** 本文与 JSON 是提案，不是该姿势已经建立或通过碰撞的声明。
