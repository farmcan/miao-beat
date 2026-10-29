# 乐器直接复用：当前选型

2026-10-30。用户补充“琴应该也有完善的模型”。本次复核现有原生文件、实际渲染及独立评审，乐器继续采用成熟资产路线。没有重新制造琴体、琴桥或琴键；本次未修改模型、动作和线上应用。

## 决定

| 用途 | 已取得的成熟源 | 当前选择与边界 |
| --- | --- | --- |
| 原图木吉他 | [Classic Guitar — Rohma Ansari](https://www.blendkit.com/asset-gallery-detail/8e698ef0-7ab1-4fab-acd6-e5accda027c1/) | 木吉他主选。已在本机复现、素材 craft 允许一次静态装配；原样还不能作为最终美术。六弦、品丝、琴码和槽式琴头已有真实几何，不再重造。 |
| 八键琴 | [Key Forty MIDI Keyboard — Innerscene](https://www.innerscene.com/tools/library/3d-parts/key-forty-midi-keyboard-0d9952a4) | 已用原成熟组件适配八白五黑，并交接可导入 GLB。键盘本体可复用；八键演奏、猫的最终形象仍未通过。 |
| 电吉他备选 | [HH Guitar with stand — Rexodus](https://www.blendkit.com/asset-gallery-detail/e641b80c-75ec-4888-b900-d63ef76057fe/) | 已保留成熟几何并换成项目新材质，独立素材 craft GO；2.19M 三角形、约52MB，只作离线 authoring。形制与原木吉他不同，不能因为较薄就认定更符合原图。 |

本次 root 实际逐图查看原图 `public/character/instrument-scenes-v1/guitar/idle.jpg`、木吉他 `local-full.png`、电琴 `full.png` 和八键 GLB 重导图。木吉他形制最接近参考，但侧板过亮偏灰、木纹和音孔圈需要在目标镜头中复核，琴头的品牌字样需要局部处理。该判断不等于已完成修整。

原素材与既有评审见 [木吉他来源核验](upstream-guitar-scout-2026-10-29.md)、[独立工艺评审](upstream-guitar-craft-judge-2026-10-29.md)、[电琴分项许可与清理](thin-guitar-clean-prop-2026-10-30.md)、[八键导入说明](../character-eight-key-prop-handoff.md)。木吉他与键盘的供应方声明为 CC0；电琴只沿用 CC0 几何，原受限材料不随 clean 衍生分发，不能以代码 MIT 代替资产许可。

## 当前本地文件复核

以下是本次重新计算的文件值，和既有回执一致；不是本次重新运行 Blender 的声明。

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| `artifacts/upstream-guitar-candidates/blenderkit-classic/classic-guitar-original.blend` | 17,344,119 | `e94d430f908ade7bf3daa3f8a3978f9f16ddd780aa7cd312d81135958067d900` |
| `artifacts/miao-eight-key-prop-probe-2026-10-30/prop-export/eight-key-cc0-prop.glb` | 214,480 | `d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6` |
| `artifacts/miao-reuse-v1/thin-electric-clean/thin-electric-clean.glb` | 51,857,764 | `1e61a29480aecff87ea53ff65338bed7d20d7a24704707b5d2c68b526bc26938` |

## 下一步按依赖推进

1. 先确定符合原胖橘猫身份、具备可用前臂与爪指的成熟角色。Panya 和 Yuki 本轮实看后均不适合简单改色；分别保留[来源核查](panya-cat-source-acquisition-2026-10-30.md)和[公开作者源补查](open-cat-template-route-2026-10-30.md)。没有合格新猫已下载的结论。
2. 用选中的成熟乐器做一次完整猫／双爪／乐器同场景静态装配。按短臂触达调整整把琴的尺度与摆位，检查承托、握颈、指腹贴弦或贴键；不拉长猫的胳膊迁就乐器。
3. 身份、工艺、接触三位非 builder 独立评审实际灰图及着色图。任一 P0 仍阻止扩展动作。
4. 通过后才做一键一动作、快速连按、持按释放和头眼小幅跟随。原生控制、整帧输出与真实网页反馈分别验收，不能由素材外观通过推导演奏通过。

当前卡点是符合原图的角色结构和手部接触，继续增加乐器面数不会解决它。主站本轮保持既有版本；未发布新的木吉他演奏或八键演奏功能。
