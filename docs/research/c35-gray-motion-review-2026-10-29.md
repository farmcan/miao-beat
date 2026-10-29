# C35 独立静态握持 / 结构 Gate

2026-10-29。独立非 builder 审查。未制作资产、修改审计、重新求解几何、打开 Blender 或运行浏览器。

**结论：此前因目标悬空 / 潜在穿入造成的 static hold P0，可在本 C35 冻结姿态及已声明的近接触范围内解除。** 本角色审查允许推进 C20 头部与 C35 手部的整合灰模检查；不授权 / 不认证本轮扩动画。整角色身份、craft、shaded still 与整合后的接触仍需各自 gate，不能由局部通过代替。

## 实看与证据身份

本次实际用 `view_image` 查看：

- 批准参考 `public/character/instrument-scenes-v1/guitar/idle.jpg`。
- `artifacts/character-paw-grip-c35/gray-front.png`。
- `artifacts/character-paw-grip-c35/gray-inside.png`。

读取同目录 `README.md`、`receipt.json`、`vertex-provenance-readback.json` 与 `handoff-manifest.json`。contact、actual evaluated 木体 / 六弦 tube 三角面交对、木体 parity 和三 quad 拓扑记录均内嵌于 `receipt.json`，并非另有独立 audit 文件。本次是独立证据审阅，不宣称独立重跑这些计算。

冻结 native：`miao-c35-fixed-vertex-tessellation.blend`，SHA `3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce`。

## 实际渲染的结构与自然度

正面完整图能够读出短圆趾绕琴颈、掌体连接短臂的放松持琴姿态；内部诊断图中，趾根到掌面的连续性保留，没有重新出现 r2 那条明显的横向唇缘、尖夹裂或上下双掌垫的分件读法。近景可见的琴颈与爪没有明显新穿透轮廓，完整图中的手没有为追目标被拉成细长肢体。

这仍是简化的三趾卡通握持：趾的排列较规整，掌面有轻微纵向痕迹，柔软度与参考不完全相同。这些属于后续整合 / craft 检查项；在本次两视图中，没有看到足以继续阻塞静态放松持琴的结构 P0。也没有凭图像宣称实际按弦或力学承重：深度与间隙仍由下面的明确审计补足。

参考的核心意图是厚短爪自然包住琴颈，而非六弦全按实。C35 的当前姿态和修正后的近接触证据足以支持这项静态意图。这里解除的是原先明确失败的握持 P0，不是认证全部视觉身份已还原。

## 五个实际目标：近接触通过，严格 nominal 仍为 false

`receipt.json.after_actual_target_rays` 的五个原世界目标保持不变，均实际命中声明来源（趾为 source 2、掌托为 source 1），无 fallback，朝向条件通过：

| 目标 | 实际正间隙，场景单位 |
| --- | ---: |
| 趾 1 | +0.0005280850455 |
| 趾 2 | +0.0020000813529 |
| 趾 3 | +0.0002730963752 |
| 内掌托 1 | +0.0019998277421 |
| 内掌托 2 | +0.0020001604571 |

此前约 0.05–0.07u 的悬空以及负间隔不再出现在这五个声明目标中。它们都为正间隙，不称作精确零距离接触、真实弦形变或实际发力按弦。

必须同时保留两个布尔值：

- `strict_nominal_contact_band_pass=false`：趾 2 与掌托 2 分别超过 nominal 0.002u 上限约 `8.1353e-8u` 与 `1.6046e-7u`。
- `authorized_positive_gap_roundoff_pass=true`：在父任务已授权的 nominal `[0, 0.002]` 加 `2.5e-7u` 正间隙 fp32 上界范围内通过。该容差只覆盖此正上界数值差；没有覆盖任何 self、穿木或穿弦。

因此结论必须称“授权 fp32 边界内的静态近接触通过”，不能抹掉 strict nominal false，也不能把这项小量差与此前实际穿入 / 大间隙混为一谈。

## actual 几何审计支持的范围

- actual hand + 邻接 retained collar：`self_intersections=0`、`flipped_faces=0`。
- 对 actual evaluated 指板、neck、六根弦 tube 分别做三角面相交，八项 `surface_intersection_pairs` 均为 0；不是只以弦中心线或圆柱代理估计。
- 5359 个手部点对指板与 neck 分别用两条独立方向 parity 射线检查：两木体内部点均 0、分歧均 0。
- 三角面表面相交检查本身不能证明全部实体包含关系；parity 是有限顶点探针，也不是连续体积的数学证明。两者组合足以支持本次冻结局部静态 gate，不推广到整猫、所有姿态或动态。

这些证据与当前实际图像一致，故不再以原来的五目标失败或已修复的 actual self / wood / tube 交对继续维持 static hold P0。不能反过来用数值通过覆盖其它独立角色审查的可见 P0。

## C35 拓扑改变的真实边界

C35 相对 **C33** 的 590793 个顶点顺序与 float32 坐标逐位一致，最大位移 0；这不等于 C33 或此前 QP 从未改变过更早版本的手形。只有原 polygon `590434 / 590446 / 590443` 被实际替换为六个显式三角面，其中两个改对角线；面数由 590465 到 590468。最终仍单连通闭合、边界 0、非流形 0。

这是真实面结构改变，而非只换审计解释。源 face 属性、材质与 smooth 属性按记录保留；保存后 readback 也支持 ordered coordinates 与整数 source IDs 一致，适合作为后续精确 source-ID 整合的输入。初始平均 normal 代理检查的纠正历史仍保留，不据该代理误判所有显式三角化非法。

原顶点不动也不代表旧 UV、groom、shape 绑定自动有效。面拓扑改变后的这些绑定仍须重建或验证；更不能仅由静态自交为零证明关节变形质量。

## 下一步与未验

可以将当前 C35 冻结手部与 C20 头部整合到全灰候选后，重新检查 source-ID 合并、完整连通、手 / 琴相对变换、相同实际目标及整帧图像。该整合结果是新候选，不能直接继承本 native 的接触通过而跳过验收。保持完整猫 / 双爪 / 吉他同帧约束；inside 只是作者诊断裁图。

当前没有动态、绑定变形、连续握持、松握 / 回位、拨弦、逐音输入、头眼响应、音画同步或浏览器体验证据，全部 **未制作 / 未验**。本轮不扩动画。整合灰模之后仍按独立身份、craft、motion 三角色检查及 shaded still gate 推进。

**本角色的最终判定：原 static hold P0 解除（限定 C35 冻结姿态、实际审计范围与授权正间隙 fp32 边界）；动态不通过也不判失败，而是尚未制作 / 未验。**
