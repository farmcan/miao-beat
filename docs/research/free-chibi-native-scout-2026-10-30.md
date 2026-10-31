# 免费成熟 Q 版猫：新增源核查

2026-10-30。按用户最新“许可清楚、无需付费的同类猫”方向，先读既有排除清单，不再把旧梨形轮廓差异当作新方向的否决。当前没有新 native 模型取得或通过静态三评；本轮最值得下一步核查的是 _polybit_ 的静态猫，而不是马上开动画。

## 1. _polybit_ — Cute Chibi Cat：值得评估静态源，尚不能算绑定模板

[作者页面](https://sketchfab.com/3d-models/cute-chibi-cat-8a7876b624554441b89926cfa380f36e)，[官方 metadata](https://api.sketchfab.com/v3/models/8a7876b624554441b89926cfa380f36e)。作者描述 ZBrush / Blender 制作，明确静态、无绑定和动作，允许个人与商业用途下载。官方记录 `isDownloadable=true`，许可 CC BY 4.0，requirements 明确商业使用可行、需署名；不是付费 personal-only 商品。

实际下载并查看作者 1920px 预览：圆方大脸、短绒/奶油灰色块、眨眼表情和清楚三趾爪垫，celshade 与粗描边有完整角色设计感，符合已允许的可爱 Q 版方向。图中手臂连接身体，右爪抬起；但这是作者特写，不是源模型或完整身体/手背/关节验收。

硬缺口：1,565,008 triangles / 782,822 vertices、0 animation，原始文件格式、可编辑低模/细分层级、指部拓扑、源材质和完整身体均未知。没有匿名原包链接，未取得 .blend/FBX，未提取 viewer 流。若实际只有固化高模、定姿融指或需要重做身体/手，不应进入另一轮自建重构；仅在原生检查证明可简单绑定时才有继续价值。公开模型“Downloadable”不等于已经下载成功。

证据：`artifacts/free-chibi-native-scout-2026-10-30/polybit-author.jpg` 与 `polybit-metadata.json`。前者是原作者预览，不是本地 Blender 渲染。

## 2. dendrite — TaiNeko：许可最清楚，外形结构不符合

[作者页面](https://booth.pm/en/items/8159495)明确 0 日元，`TaiNeko_source_v1.3.zip` 283KB 内含 `neko41.blend`（作者称 Blender 5.1、有骨骼权重）；另有 FBX / Unity 包。页面完整英日许可写明 CC BY 4.0，修改、商业使用、原版/修改版再分发可行，需署作者和 URL。没有把 Unity shader 许可推定为 Blender 材质许可。

实际查看作者封面：黑色锥状身躯、巨大尖耳和极简白眼，**两只带肉垫手掌悬浮在身体两侧，没有连接手臂**。这与用户完整连接肢体的硬要求冲突，且不是只改颜色可解决。视觉排除，不为免费/许可清楚降低标准；未下载源。

证据：同证据目录 `taineko-author.jpg`，原作者公开图。

## 3. ekiden — Clint Catswood：免费但不是 Q 版，许可也不能直接外推公开模型

[作者页面](https://booth.pm/en/items/8566295)列 0 日元、102MB ZIP，作者称 .blend/FBX/GLB/VRM、约 93k triangles。许可允许个人/商业 Streaming、YouTube、VTubing，允许个人修改，禁止原版/修改文件再分发；不能拿免费或列 GLB 当作可公开网页下发 GLB 的授权。

实际看作者封面是成年肌肉猫人：小头、宽肩胸腹肌、长成人形手指、腰带衣饰，非本轮 Mewchi 类 Q 版。外形排除，未取得源，也未为了它联系作者。

证据：同证据目录 `clint-author.jpg`，原作者公开图。

## 边界与下一步

三条新增作者源中，0 个已通过模型 gate；_polybit_ 是一个有明确商业 CC-BY、视觉值得复核但未绑定的来源。建议 root 先看它的实际预览，再走正常下载路径核验源格式与可动拓扑。取得源后仍需三位非 builder 对完整身体/脸/双手静态做评审。不要把本报告或作者图当作本地建模完成。

另查 Alpha Centauri 的免费 Responsible Cats FBX 双猫包，作者页未给明确许可证；未进入候选、未下载。GitHub `cat avatar blender` 本轮结果主要是 CATS 插件及网页工具，不是成熟猫模型 payload，不安装代替取源。未提交个人信息、注册/登录新账号、购买、执行外部代码、改应用或部署；公开状态由 root 统一记录。
