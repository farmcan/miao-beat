# 成熟猫资产原生静态兼容闭环 · 2026-10-29

本阶段已取得作者支持的 Blender 3.6 环境，并成功实渲一张完整彩色 Wing It! Cat。它证明现成模型、原有四指、收到的配色/材质可以在本机支持版里形成真实静态画面。尚不构成最终模型、美术或动画验收。

## 完成且有执行证据

1. 官方 Blender 3.6.23 macOS arm64 包已下载；与官方 `blender-3.6.23.sha256` 的 `ecbeaef4abbeb045de8465e78b3f97aec9b67faf2fc71b20e5eca37bf1caf874` 完全匹配。portable binary 在 `artifacts/runtime/blender-3.6.23/Blender.app/Contents/MacOS/Blender`，build `e467db79ca8c`。没有替换用户 `/Applications/Blender.app` 的 5.2.3。
2. 对 native `.blend` 的 4 个嵌入 Python 文本进行了 import/call/side-effect 静态审计并保存源文本。CloudRig UI 含 `eval`、类/热键/handler 注册；本次不需要也未执行。lighting helper 已识别为只处理 Blender 内部灯光属性，但同样没有执行。post-gen 与 UV editing helper 未执行。见 `artifacts/miao-reuse-v1/compat/EMBEDDED-CODE-REVIEW.md`。
3. 仅在新工作副本把 3 条相机 Euler 的复杂 Python expression 改为显式绑定实际 inspection camera 的简单 transform variable（world-space XYZ Euler）。限定匹配原表达式，保留 before/after 回执。所有上游嵌入代码保持未执行，autoexecution 为 false，工作副本里的 text module autoload flags 也全部关闭。
4. 成功以 3.6.23 EEVEE 渲染 `artifacts/miao-reuse-v1/compat/wingit-received-materials-color.png`，1200×1200，96 samples，单帧约 8.5 秒，已实际查看。无新 pose、keyframe、动画 clip、改色、重做材质、脱装、几何/手指重造；只添加研究用相机/灯光/背景。
5. 独立保存 `artifacts/miao-reuse-v1/compat/wingit-working-native36.blend`。上游 asset SHA256 渲染前后均为 `42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1`，未覆盖源文件。
6. 吉他 scout 的 `classic-guitar-compat.glb` 在 3.6.23 factory 空场景实际导入成功：1 mesh、141217 triangles、3×4096² packed textures；XYZ 0.4137722999×0.1392673552×1.1117058086m，与 5.2 侧回执一致。GLB 源 SHA 前后不变；没有打开不兼容的 4.3 原生吉他文件，没有组装或改猫姿态。见 `guitar-native36-import-receipt.json`。

## 画面与能力边界

彩色图是**收到的 MoveAI 优化分发版材质**，31 个材质为 Principled/Emission，保留 gray fur / blue suit / red goggles 及 packed 4K 贴图。它不是影片原始 toon shader 的还原。当前渲染比作者影片预览偏平，仍需独立 shaded-static craft/identity/motion gate；没有把彩色图成功渲出写成“精致猫优化完成”。

原生短四指、掌指过渡和完整3D体积保留。角色仍穿原来的工装、护目镜，没有尝试从服装重建裸猫。四指猫的琴颈握持、左右手接触、缩放比例与遮挡仍待单个静态抱琴 pose 验证。动画和动作优化继续 HOLD。

## 跨机复现

`design/miao-reuse-v1/README.md` 包含固定 source/license、portable runtime URL/SHA 和完整执行命令。脚本目录是 `design/miao-reuse-v1/scripts/`，回执、原始嵌入文本、许可证说明、图和新工作场景在 `artifacts/miao-reuse-v1/compat/`。全部 Blender 调用使用 factory startup、disable-autoexec 和非零 Python 错误码；没有 MoveAI addon、账号、付费服务或全局偏好修改。

资产署名继续为 `Cat Rig (CC-BY) Blender Foundation | studio.blender.org`，许可 https://creativecommons.org/licenses/by/4.0/ 。来源页 https://studio.blender.org/characters/cat/v1/ ，分发 commit 及独立资产许可见 scout A 报告与 provenance。CloudRig 当前官方代码许可 GPL-3.0-or-later，和模型 CC BY 4.0 分开记录，不把上游成果说成原创。

下一步：由一个 builder 统一持有单静态抱琴工作副本，避免多个 agent 同时改 pose；先通过完整猫+琴+四指接触的独立静态检查，再决定是否开放后续动画。没有发布生产资产。

## 追加纠正：相机 driver 等价性未通过

后续只读重开诊断发现 `HLP-scene_camera_dummy` 与实际相机的世界旋转角差1.08858rad；三条新driver虽simple/valid，不能据此称行为已等价。撤回其“兼容已修好”的行为结论。3.6官方runtime、SHA、原配色真实渲染和GLB实际导入证据仍成立；后续静态抱琴整合FAIL，详见 builder 的冻结交接。
