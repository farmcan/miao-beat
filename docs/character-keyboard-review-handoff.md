# 成熟猫 + KeyForty：跨电脑静态 review handoff

2026-10-30。**本包仅为三方已GO的完整默认色静态baseline。** 允许另行研究单键动作，不代表单键、演奏、八键、浏览器/手机或最终Miao交付通过。单键operation由另一任务进行，未收入本包。没有失败smile、guitar-fit、失败web导出或动画clip混入。

## 包里有什么

解压 `miao-keyboard-static-review-2026-10-30.zip` 后，顶层目录保留必要的仓库相对路径：

- `artifacts/miao-reuse-keyboard-v1/default-color/keyboard-default-color-native36.blend`：已评审原生3.6.23，原bytes与SHA不改。
- 同目录8张默认色评审图：front / three-quarter / face / left-hand / right-hand / hands-top / feet-support / support-side。完整front/3Q始终同帧显示猫、双爪、键盘和承托。
- `public/character/whole-piano-v3/idle.jpg`：原piano参考，仅用于比较，不是本次新产出。
- `docs/research/miao-keyboard-{gray,color}-{identity,craft,motion}-judge-2026-10-30.md`：三方灰/色评审。灰报告保留历史HOLD与后续GO；历史失败图不附带。builder原inspection-manifest仍记pending，是其当时快照；当前静态GO依据三份color报告，见 `PACKAGE.json`。
- 原cat `.blend`（CC BY4.0）和provenance/ReadMe/嵌入源码，KeyForty及COMMON280原CC0 GLB与来源/许可回执；不需重新登录下载。原cat和assembly native的嵌入Python源码保留，完整GPL3文本随包。
- `design/miao-reuse-keyboard-v1/review_native.py`：默认只读重开/依赖核验，可选渲现有pose；不会保存native、切帧、套action或运行嵌脚本。
- `PACKAGE_MANIFEST.json`、`SHA256SUMS`：当前包内相对路径、字节数、SHA及文本转换记录。

键盘/桌原网页HTML不随包，防止临时下载URL/网页状态混入。版权声明取原GLB内的whole-file CC0和本地许可回执，canonical作者链接保留。回执/报告的本机绝对路径被转换为仓库相对路径；其原SHA和转换后SHA均见manifest。旧回执内的原始hash描述原仓库快照，当前包逐文件验证以 `SHA256SUMS` / `PACKAGE_MANIFEST.json` 为准。PNG、GLB、`.blend`等二进制保持原字节。

## 先校验，再打开

在解压顶层目录执行（Python3标准库，无pip依赖）：

```sh
python3 design/miao-reuse-keyboard-v1/verify_review_pack.py
```

已评审 native SHA256：

```text
3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b
```

原pose SHA：`4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be`。本次重开检查另见 `artifacts/handoff/keyboard-static-native-audit/native-audit.json`，12图像数据块，FILE图像均packed、无外链library或缺失依赖。native内部分历史路径字符串保留原样以维护已评审SHA；图像均内嵌，便携脚本会覆盖当次输出路径，不依赖原电脑目录。

使用**官方Blender3.6.23**。不以5.2打开后保存覆盖这个rig。runtime不放进小review包；从[官方3.6目录](https://download.blender.org/release/Blender3.6/)下载对应系统，核对包内 `runtime/blender-3.6.23.sha256`。Mac arm64 DMG已实测SHA为 `ecbeaef4abbeb045de8465e78b3f97aec9b67faf2fc71b20e5eca37bf1caf874`；Windows/Linux列于同一官方校验文件，跨平台本次未实机运行。

在解压目录运行（将路径换为该电脑的3.6.23 binary；不打开GUI）：

```sh
MIAO_BLENDER36="/path/to/blender-3.6.23"
"$MIAO_BLENDER36" -b --factory-startup --disable-autoexec --python-exit-code 1 \
  -P design/miao-reuse-keyboard-v1/review_native.py -- --out output/review
```

如确需重渲既有完整pose，用同一命令尾部加 `--render front three-quarter`。输出写入 `output/review/`，不保存/覆盖输入native。本次pack验收没有重渲已有图。

勿启用用户全局autoexec或运行 `.blend` 内CloudRig UI / lighting文本；不需安装MoveAI addon。三个camera-helper rotation表达式保持mute；**每次换相机/每次render前**脚本取 `camera.matrix_world.to_euler()` 写入 helper **局部** `rotation_euler`，逐轴assert误差<1e-6。不要换回旧TRANSFORMS近似驱动。

## 许可与修改边界

**Cat Rig (CC-BY) Blender Foundation | studio.blender.org**，CC BY4.0；上游[作者页](https://studio.blender.org/characters/cat/v1/)，收到版为固定MoveAI公开再分发commit的优化版本。原模型/纹理与pose不是项目原创。修改仅既有静态IK/指控制器、现有细分render2、相机/环境、键盘桌刚体与默认色compositor bypass；基网格和原材料未重造。

CloudRig相关嵌入代码单独保留来源与GPL3全文，不把它或cat资产套为项目MIT。此包不安装/运行这些上游脚本。KeyForty和COMMON280由Innerscene作whole-file CC0声明，含原材料/内嵌图；原GLB保持。项目相机/审计/打包脚本与地面环境代码按MIT。分项许可、修改记录和源码随包。

## 独立薄电琴 addon（可选，和键盘baseline分开）

`miao-thin-electric-clean-prop-2026-10-30.zip` 仅含 Rexodus HH geometry 的干净CC0衍生、新建常量PBR、clean原生/GLB、clean摄影图与分项来源许可。**不含原HH `.blend`、作者原预览、royalty_free材料/贴图或失败猫装配。**

该prop的native原本是5.2.3，原bytes保留；3.6使用已验 `thin-electric-clean.glb` 导入，不拿5.2 native给3.6打开。143 meshes /2.19M tris只适合离线authoring，未批准浏览器默认加载。prop素材GO不等于任何猫抱琴通过。包内独立README/manifest列明此边界。

## 重建这两个review ZIP

在具备白名单源文件的仓库，或解压后的keyboard包内，重建keyboard ZIP：

```sh
python3 design/miao-reuse-keyboard-v1/package_review_pack.py --output artifacts/handoff
```

完整仓库可加 `--kind both` 同时重建独立琴addon；只解压keyboard包时保持默认 `--kind keyboard`。脚本只读白名单，校验原manifest/native/source资产SHA，重算包内每个成员SHA，拒绝路径穿越、非白名单成员和敏感临时URL，采用固定ZIP时间戳以复现字节。不会启动渲染、修改scene、publish、commit或写public。receipt在 `artifacts/handoff/review-pack-receipt.json`；发布由root另行处理。
