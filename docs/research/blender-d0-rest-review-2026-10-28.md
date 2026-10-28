# D0.1静态材质绑定：三方独立复核

2026-10-28。该小项builder为`modelr_trial`；下列三位均未制作此资产。各自实际打开512px的Position与named-rest两张渲染，另对照C5 1024静帧和主参考`guitar/idle.jpg`，并读说明与像素差JSON。主agent也实际打开两张图、独立Pillow读取PNG得到同一差异。

**结论仅是静态改线未引入新的可见P0，可继续下一项窄验证。D0整体未通过，正式演奏动作未验，C5全部精致度P1保留。**

| 独立角色 | 实图结论 | 必须保留的边界 |
| --- | --- | --- |
| `reference_geometry`：身份／轮廓 | 头身、侧向眼神、暖橘／奶油区、臂部条纹、无亮袖口、完整猫爪琴关系没有新身份P0；没有明显换色／归零。 | 512px不能代替1024精致度复验；毛粒、规则纹、鼻眉／高光、掌体／琴低位、耳尾块面与影重仍是P1。 |
| `gpu_route`：材质／工艺 | 未见新静态P0，cream／木纹及原C5结构保持；另用Pillow重算SHA和差异与报告一致。 | hair专属AOV因Blender5.2枚举报错未回读；不能证明每hair着色点插值、动态防泳动或毛根跟随。 |
| `modelr_contact_judge`：爪体／接触 | 未见改线造成的新爪体或接触静态P0，指沟／握琴轮廓与完整画面保持。 | 仍是弦前准备姿态；长扁拨弦掌、较大握掌P1不变；静图不证明贴弦、掌内空间、全碰撞或正式动作。 |

两张真实图只在同一冻结场景切换pigment输入：seed17、512×512、32samples。262144像素中272个有任意RGB差，最大2／255，RGBA平均绝对差0.00026512146，alpha差0；没有新增第三次GPU渲染。未测重复渲染噪声，不把微差全归因shader，也不换算成审美或自然度得分。

[复现与错误原文](../../design/character-sculpt-v2/d0-rest-binding-README.md) · [实际对照／receipt](../../design/character-sculpt-v2/evidence/D0-1/)。AOV错误分支的CPU清理前后Surface与compositor Image祖先图hash相同；未把未执行的清理后GPU复验写成完成。

下一项是实际609383点猫体、180000根native groom的UV／surface attachment与一个小局部形变；官方小平面probe通过不等于这项已完成。之后才是眼睑闭合、真正触弦／离弦、头眼身体配合、网页组合与导出。
