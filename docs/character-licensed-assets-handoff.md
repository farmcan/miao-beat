# 跨电脑：成熟猫与吉他原素材

这是**素材交接**，不是成品角色/动作验收。旧自建猫已弃用；新素材的抱吉他整合被评审拦下，该持琴分支冻结。独立键盘分支的后续状态见文末。

## 下载

[GitHub Release：Licensed source assets](https://github.com/farmcan/miao-beat/releases/tag/licensed-source-assets-2026-10-29)

下载 `miao-licensed-source-assets-2026-10-29.zip`，解压到本仓库根目录；保留压缩包原件。包内目录直接对应研究脚本。

- 大小：40168877 bytes。
- 整包SHA256：`cc7de4d86141fe4a6ac8bd2296b77fb9ebcdd23ae33c1f52502da4db9cc94965`。
- `SOURCE-ASSETS-SHA256SUMS`核对包内文件。

## 包里是什么

| 文件 | 来源/许可 | 如何使用 |
|---|---|---|
| Wing It! Cat 原生blend | Blender Studio；MoveAI固定commit优化再分发；模型CC BY4.0 | 用官方Blender3.6.23；保留署名，不执行嵌入代码 |
| Classic Guitar 原生blend | Rohma Ansari / BlenderKit；CC0 | 原文件为4.3，较新Blender打开；不在3.6强行读新native |
| Classic Guitar兼容GLB | 本项目从上述琴导出 | 已实际在3.6导入，六弦、18品、三张4K图完整 |
| 原素材预览、来源和许可 | 各源文件原样/原生渲染 | 用于辨识素材，不能代替整合gate |

猫署名：`Cat Rig (CC-BY) Blender Foundation | studio.blender.org`。MoveAI已有rig/材质优化，原包在本项目未改。许可与代码条款分开保留。琴商标及侧板材质还未完成产品修整。

## 下一步

先读 `design/miao-reuse-v1/README.md` 和 `docs/character-reuse-plan-2026-10-29.md`。官方3.6.23运行时没有放进本包，平台下载/校验见README；不会覆盖现有5.2。

脸部有限诊断已恢复原始嘴/眼外观；手与琴接触仍FAIL。完整静态猫+琴必须再次通过identity/craft/contact三评，才允许增加演奏、头眼动作和上线替换。不要把首次失败hold脚本作为生产方案。本包不含失败hold工作工程。

发布验收：GitHub公开附件大小与服务端SHA256均与本地一致，匿名canonical receipt下载逐字节匹配；代码/研究文档已commit并push（030607d），大模型原文件在Release附件内。

另有 `miao-reuse-source-rest-pack.zip`：自带猫原包和最小rest脚本，解压后用官方3.6运行即可，不依赖失败hold工程。新camera同步已逐轴验0，原pose hash不变；不是持琴或动画成品。大小6288279字节，SHA256 `0f565bbdcfe0a21a1fa31bc525d4967c25b82b8e2dd026a6bacb5cdae0097e8f`。GPL文本与模型署名均保留。

## 2026-10-30 增补：成熟键盘与薄电吉他

除了上述声学琴，已实际复用Rexodus HH薄电吉他CC0几何、Innerscene KeyForty键盘和COMMON280桌（后两者完整文件CC0）。薄电吉他的原royalty-free材质不再分发，干净衍生物只含CC0几何与本项目新PBR；它的独立prop工艺通过，但猫持琴的.70/.55测试仍穿模，冻结不扩动画。

独立键盘场景已通过灰模和彩色两轮、每轮三位非builder的identity/craft/contact静态评审，**只放行一指一键试验**。当前默认色保留作者飞行员猫身份，不声称原橘猫复刻、已自然演奏或网页已上线。[逐步计划](character-reuse-operation-plan-2026-10-30.md)记录验收和停止条件；后续键盘交接独立提供，不把旧失败吉他工程当成可直接演奏成品。

两项跨电脑附件已发布到同一个Release，并核对GitHub服务端大小/SHA、匿名canonical回执一致：

- [完整键盘静态review包](https://github.com/farmcan/miao-beat/releases/download/licensed-source-assets-2026-10-29/miao-keyboard-static-review-2026-10-30.zip)：28,178,410B，SHA `c2e63433bb37553583655f02012e5215cfead6e10e898d25010bfa7fb842d85e`。
- [干净薄电琴prop包](https://github.com/farmcan/miao-beat/releases/download/licensed-source-assets-2026-10-29/miao-thin-electric-clean-prop-2026-10-30.zip)：74,312,197B，SHA `d73fd232cad23a9f1ccd8c04e268474b97e6f78d0e2c39eacc5d66821b2d477b`。
- [操作文档](character-keyboard-review-handoff.md)：先校验，使用官方3.6.23重开已评审键盘native；琴addon内5.2 native与3.6兼容GLB分开说明。

解压后跨路径重打包的SHA完全一致，键盘实际重开无缺依赖。两个包都不包含未通过的动作。单键v1后来触发键—底壳交叉STOP，按 `research/miao-keyboard-single-key-v1-failure-2026-10-30.md` 保留证据；静态包原字节不因此改写。
