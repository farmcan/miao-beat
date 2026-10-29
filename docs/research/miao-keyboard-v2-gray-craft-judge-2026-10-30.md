# v2 +2mm 键组灰静态 · 独立 craft 短评

2026-10-30，非 builder。**GO：只允许该新 pose 进入默认色静态评审；未见当前新增视觉 P0。** 不放行动作、按键或最终美术。未改资产、未渲染。

实际打开 `artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift/` 全9图：front、three-quarter、face、left-hand、right-hand、key-rear、key-front-edge、feet-support、support-side；另重看旧 `gray-supported/three-quarter.png` 与原 `public/character/whole-piano-v3/idle.jpg`。9图实际 SHA 均匹配 manifest。读过 `miao-keyboard-v2-keygroup-lift-gray-2026-10-30.md` 和本轮 manifest，没有用 builder 自评或交叉0代替看图。

**暗缝裁决：现阶段 P1，不是悬浮/露底 P0。**

- `key-front-edge` 低机位无遮挡地显示了白键底下的连续暗缝；它确实存在，不能称“看不见”。暗缝窄、均匀，紧随键底，琴壳紧接在下；未见透底的明亮通道、参差跳层、翘起端部或大段键块离壳漂浮。当前读法更接近可接受的机械净空。
- `key-rear` 中后端界面和白黑键相对高度整齐，没有新裂口或一组键突出另一组的断层。front/3Q中该分离没有抢走场景阅读。这一判断同时依据近景与完整图，不只因为主图里缝小。
- 这不是内部键床/支点已经建好或真实机构正确的认证；图中没有显示的机构不予虚构。零穿透、2mm抬高或扫掠下界只能另作几何证据，不能证明视觉必然可用。本轮没有据此平均掉潜在 P0。

**角色与承托没有新工艺退步。** face 的眼眉鼻口牙完整；左右掌/短指仍清楚圆顺，袖口与腕连接可读，未见因腕位变化出现明显硬折、裂开或独立手掌。琴壳仍坐在桌面上，桌脚、猫靴和地面软影成立；完整 front/3Q维持猫、双臂双手与全键盘同帧。低角和 side 是诊断，不能代替完整生产帧。

**P1 保留：**抬高键组在低角更像一层放在壳上的独立键排，默认色中若对比变强可能暴露更明显的漂浮感；必须继续看同机 `key-front-edge` / `key-rear`，不能加黑片、改照明遮缝或裁掉问题取巧。密键条在全身图仍细，光照偏平、暗区偏闷；与原图暖木/短绒完成度的差距仍在，不因这次小改动消失。

本次只签 **pose SHA `6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b` → 同 pose 默认色**。不是继承旧 `4fb…` 的颜色/传输通过。render2匹配proxy仍非直接RENDER depsgraph；继承黑键局部重叠及近边界包含性unknown保留，未因全键组共同平移豁免整组件。当前手是悬停，无新动作；按下时的键缝、邻键、指腹和返回形态尚未验证。本轮仅新增本文档。
