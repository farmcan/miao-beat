# 现成开放 Blender 猫角色：Scout A 实证研究

日期：2026-10-29。范围：作者页、许可、实际模型下载及只读 Blender 检查。没有改色、建模、改动作或发布生产资产。

本轮以实际原图 `public/character/instrument-scenes-v1/guitar/idle.jpg` 为观察基准，重点寻找可爱、有真实体积、完整掌指结构的现成模型。用户已允许优秀现成猫改色，不再要求逐点复制旧 Miao。按主任务后续分工，本 scout 集中完成最强的 Wing It! Cat 路径；不以粗糙模型凑满三个。

## 首选：Blender Studio《Wing It!》Cat

- **作者/权利方**：Blender Studio / Blender Foundation；作者模型页发布人 Demeter Dzadik。发布人不等于全部造型作者，最终署名应保留 Foundation/Studio 而不要擅自把造型归为单人。
- **作者原页**：https://studio.blender.org/characters/cat/v1/
- **可见作者原预览**：`artifacts/upstream-cat-candidates/scout-a/studio-cat-preview.png`；来源为原页公开预览。它同时展示影片成品及控制器视图；手部实际拿笔、拿夹板。
- **模型资产许可**：CC BY 4.0。原页许可链接为 https://creativecommons.org/licenses/by/4.0/ ，法律原文 https://creativecommons.org/licenses/by/4.0/legalcode 。`.blend` 内的 ReadMe 也指向同一许可，已只读导出为 `ReadMe.txt.txt`。
- **可修改与再分发范围**：许可允许非商业/商业使用、复制、改色、变形、改抱琴及再分发。须保留适当署名、原资产/许可链接、标注修改和既有修改；不可暗示上游认可。此处是许可条款摘要，以上述原文为准。
- **作者要求署名**：`Cat Rig (CC-BY) Blender Foundation | studio.blender.org`。
- **原生格式/支持版本**：`.blend`，原作者明确要求**恰好 Blender 3.6**，低于/高于该版可能损坏。5.2.3 打开成功不能取代这个版本约束。
- **访问条件**：作者原页对匿名用户显示 `Login to Download`。没有创建账号、没有购买、没有绕过登录；使用下述公开、明确标注资产许可的合法再分发版。

### 实际取得的 MoveAI 优化分发版

- **分发者官方仓库**：https://github.com/move-ai/Move_API_and_retargeting_Blender_addon
- **固定版本**：commit `f449af53ccc71a7c66079b7a52e133a163a41fb7`。
- **具体文件**：https://github.com/move-ai/Move_API_and_retargeting_Blender_addon/blob/f449af53ccc71a7c66079b7a52e133a163a41fb7/data/rigs/wingit_cat.blend
- **下载原文件**：`artifacts/upstream-cat-candidates/scout-a/wingit_cat.blend`，6,292,093 bytes。
- **SHA-256**：`42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1`。
- **Git blob**：`b85d8e2e6c4778ebd49f1e5ef611abaccd46bf32`。
- **分发许可证据**：固定 commit 的 README 明确单列 “Blender Studio's files”，说明 Cat rig 和 Barn 均为 CC BY 4.0，并说明做过性能优化。保存在 `move-ai-README.md`。这是资产自己的许可证据；没有把整个仓库的 GPL-3.0 代码许可证套给模型。
- **插件范围**：没有安装、运行仓库插件或调用 MoveAI 服务；无需 API key。只通过 git 读取指定资产/README。`move-ai-source/` 是未 checkout 的 provenance repository，不是已安装插件。

### 实测：Blender 5.2.3 LTS 只读审计

检查脚本是本次自行编写的只读资产清单，不执行上游脚本。启动使用 `-b --factory-startup --disable-autoexec --python-exit-code 1`，打开文件再明确 `use_scripts=False`，并将 `use_scripts_auto_execute=False`。

| 检查项 | 实测结果 |
|---|---|
| 原生文件读取 | 成功，Blender 5.2.3 LTS；退出码 0 |
| 场景对象 | 125 个；当前可见可渲染 mesh 56 个 |
| 主控制骨架 | `RIG-Cat`：982 bones，132 deform bones |
| 生成骨架 | `META-Cat`：254 bones；未尝试 regenerate |
| 手指 | 左右手都有 Thumb、Index、Middle、Pinky 各两节 deform bones；Index/Middle/Pinky 另有 carpal，均带 claw bones；即拇指加三指的卡通四指手 |
| 手部几何 | `GEO-hands`：1138 vertices / 1134 polygons，是真实完整手掌与指形 |
| 上臂前臂 | 每侧有 UpperArm1/2、Forearm1/2、Hand deform bones；IK/FK 控制名均存在 |
| 贴图 | `cat.base_color`：4096×4096，已 packed；外部 `//textures/cat.base_color.tif` 不存在但不构成缺贴图，因为数据已打包 |
| 外部 linked libraries | 0 |
| 对象层 driver | 856 条；存在依赖相机的复杂 Python expression |
| 嵌入 Python | `cloudrig.py`、`lighting_rig_setup.py` 标记为模块；日志明确显示被禁用和跳过；另有 post-gen/UV helper text，全部未执行 |
| 源文件完整性 | 渲染审计后 SHA-256 与下载时一致；没有保存覆盖原文件 |

原生完整审计：`wingit-cat-audit.json`；命令日志：`wingit-cat-audit.log`。

### 实际查看的整身/手部预览

检查图是当前**真实下载网格**的 Workbench 灰材质渲染，不是作者图替代本地模型证据；仅临时相机与观察着色，不更改或保存源文件。

- `wingit-full-front-gray.png`：整身正面，完整头、耳、身体、双手、双脚同时可见。
- `wingit-full-three-quarter-gray.png`：整身三分之四，能直接确认脸/身体的前后体积。
- `wingit-hand-gray.png`：手掌和四个完整圆润手指特写。
- `preview-receipt.json`、`preview-wingit.log`：渲染设置与日志。脚本 `preview_wingit.py` 可复查。

实际观察：角色是完整、成熟的圆润 3D 猫，脸部有明确的面颊与口鼻结构，掌指过渡自然，手指有体积；没有扁壳和面条手问题。短上肢、偏大头和紧凑身体适合继续做抱琴可行性试验。作者原览已表现握持道具，进一步支持这条路径。

差异与未验证：

1. 它的蓝色工装、护目镜、短腿和大眼睛是不同于旧 Miao 的角色设计；用户已允许优秀现成猫改色，但本 scout 没有改色或擅自确认最终美术方向。
2. 当前身体外观带工装，脱装成裸猫并非仅改一层色，须先检查 body topology/material 分工；不能把去服装说成已完成或零成本。
3. 四指手适合风格化乐器动作；真实吉他四根按弦手指的完全对应并不存在。琴颈握持、关节极限、贴弦与弹弦接触仍未实测。
4. 上游 toon shading 有自定义灯光/相机依赖。本轮无代码渲染日志出现 `restricted access disallows name scene`，这些 driver 被安全阻止，因此**不能声称原影片着色、CloudRig UI、复杂驱动和完整动画在 5.2 已兼容**。
5. 原作者支持版本为 3.6；后续若采用，应优先在官方 3.6 环境内做静态与握琴试验，再判断是否需要迁移。此报告不要求运行任何未审查上游代码。
6. 尚未进行项目要求的独立 identity/craft/motion 三角色灰模与着色静态 gate；本报告是现成资产研究及安全读取证据，不是新猫成品验收。

## 早期淘汰与未入选

- **Cat Pilot / Tomcat94**：https://opengameart.org/node/95204 ，CC0、可直接下载 `.blend`。已实际看作者预览 `cat-pilot-preview.png`；脸、眼和贴图呈明显旧低模风格，达不到本轮“精致优秀”的主目标，淘汰，不作为第三名凑数。
- **Panya free cartoon cat rig**：https://panyabp.gumroad.com/l/axidf ，原页搜索可读为 `.blend` / Rigify、$0+、3.6.5/4.0。但本环境 Gumroad 页面访问失败/正文空白，没拿到明确开放许可，未作为可用候选、未购买或下载。
- **BlendSwap Toon Cat / squibblejack**：https://blendswap.com/blend/22931 ，作者页 CC0、原生 blend、pose/NLA。浏览器可访问，预览戴高礼帽、风格不同；本轮优先集中完成 Wing It 的实际文件闭环，未验证其手指和下载，没有推荐它替换首选。
- 检索中出现的 Trevor Henderson Cartoon Cat 是恐怖长肢角色，与可爱饱满短肢目标明显不符，未采纳。

## 可复用结论与下一步

现成模型路线已经有一条可实际落地、许可独立明确的强路径：Wing It! Cat。下一步最便宜的证伪动作是保持全身整体角色，优先在 3.6 兼容环境里验证手掌绕琴颈、前臂接琴身以及大头不遮琴的单个静态姿态；静态质量和接触 gate 通过前不要扩动画。若失败，应回到其他成熟资产，不回到 primitive 自造猫。

本报告及模型未发布到产品；持续任务/公开交付状态事件由主任务统一接入现有 Seed 状态入口。
