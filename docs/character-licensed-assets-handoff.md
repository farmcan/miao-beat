# 跨电脑：成熟猫与吉他原素材

这是**素材交接**，不是成品角色/动作验收。旧自建猫已弃用；新素材的首次抱琴整合也被三方评审拦下，当前禁止动画扩展。

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
