# 可换电脑打开的 Blender 研究稿

[下载 C49 原生工程与预览](https://github.com/farmcan/miao-beat/releases/tag/authoring-study-2026-10-29-c49)。压缩包约66MB，包含完整`.blend`、批准原图、三份实际预览、打开说明和SHA256。Blender5.2.x解压后可直接打开；三份文件贴图已packed，无外链library、嵌入脚本或object drivers。源码与三角色独立评审checkpoint为`7c02830`。

**这是局部进展研究稿，整体美术仍未通过。** 眼部蓝色/真实小高光与左肩局部改善可保留；耳、右臂/掌、头身转接、短绒仍需继续优化，没有新增皮肤动画。主站没有替换成这份研究稿。

GitHub服务端记录ZIP为65,969,898字节、SHA256 `12a9f38e9de3e0697cb162d9fec089d543000a78c7148302b1adcd6aa6fbca9c`，与本机逐项封装检查一致。原生文件SHA256 `0ea1505e0368ab01ed5dac5ba5a07cb4772426e25db8faeffcf35cee8ac7ad6b`。

本包可独立打开当前作者文件继续编辑；不是全部历史候选重跑包，未包含每个旧实验的native。C51/C52等重拓扑和后续动作研究仍在独立目录，未冒充已经合入本下载。

另有[最新静帧对照单文件HTML](https://github.com/farmcan/miao-beat/releases/download/authoring-study-2026-10-29-c49/miao-reference-progress-c59.html)，下载后用浏览器打开，可切整身、看脸、看手。它包含当前C59灰模的高清快照；C59不在C49原生压缩包内。该页已在真实浏览器检查三个视图，所有图像内嵌，可离线查看。

附件使用[GitHub Releases现有分发功能](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)，未启用Git LFS或新增付费托管。首次创建因短target SHA被API拒绝，使用已推送的完整commit SHA后创建成功，历史失败保留；本文件不把作者文件上传等同站点美术发布。

## 2026-10-29追加：上述自建分支已弃用

旧工程/HTML仅保留历史恢复与失败证据，不再作为当前优化基础。当前路线是复用成熟的Blender Studio猫与CC0完整吉他；[新原素材包](https://github.com/farmcan/miao-beat/releases/tag/licensed-source-assets-2026-10-29)，具体复现和验收边界见 `docs/character-licensed-assets-handoff.md`。新素材仍需持琴静态三评，不能因换用成熟模板就自动认定成品通过。
