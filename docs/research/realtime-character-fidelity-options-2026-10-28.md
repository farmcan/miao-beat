# Miao：可复用猫资产、毛发与 Godot 迁移边界

日期：2026-10-28。独立材料/工艺评审；未参与 C8 角色构建。本次只读代码、核验许可、下载一个明确免费的约 2 MB 旧版资产、在本机安全打开其文件；没有构建角色、安装插件、请求 Cloudflare 或发布。

## 结论

目前最值得复用的是 **Godot 短毛实现的方法和代码**，不是用一个现成低模猫替换 Miao。本次找到并实际打开的免费猫有骨架和动作，但外形是四足低模黑猫；尚未核实到同时满足「免费可用、实际文件可得、原图胖梨形/方圆脸/短肢、可直接弹琴」的现成 plush 角色。这个缺口是有限调查结果，不是断言全网不存在。

`sofluffy` 的 MIT shell-fur 是较小、可读的候选；只能称 **待本机验证的实现**。原生 Godot GPU 球体成功、插件 README 或导入 GLB 成功，都不能证明 Miao 材质、毛发和演奏动作已经保真。Godot 适合后续低延迟动作组合；当前整体造型/表情差距仍需在原模型上解决，换引擎不会自动变精致。

## 本次实际对照

实看原图 `public/character/instrument-scenes-v1/guitar/idle.jpg`、C8r2 灰模双机位与 `artifacts/character-fidelity-c8-r2-color/{color-front.png,color-three-quarter.png}`。后两张 SHA256 分别为 `1af441d8bd06ec97398f74b1e5208c7176677f2b7005a080c338a1313c0a9e18`、`60eb962ad2b45af459b1ab11c632d3bc9bfcd1032a3833293ab9cf1623eab9b3`。

C8r2 实图已改善持琴高度、完整身体和手臂的连接，但整体仍未达到原图：

1. **面部与短肢的软体积**：原图眼周/鼻口、手掌抓握有柔和起伏；当前鼻口更像附在平脸上的线件，拨弦掌仍呈平整长块、压弦指更像分开的圆块。应先用同机位脸/双爪局部修体积和掌指过渡，不能用 shell 毛遮结构。
2. **颜色和毛感**：当前大面积橘色/奶油色较匀、饱和，规则条纹和表面细颗粒弱于原图有层次、沿曲面嵌入的短绒。需要保留 rest 空间颜色，控制毛长/方向/粗糙度与柔和色区；换成通用噪声 shell 可能进一步丢失原图性格。
3. **琴与灯光的精细对比**：原图木材亮暗、琴侧厚度、音孔内沿与掌部遮挡更集中；当前琴面和大面积奶油肚偏平。迁移时必须另做灯光/木材校准，不能直接把 Cycles 图与默认 Godot 灯光图评分。

以上是整帧质感差距，不代表此前局部 B 门槛全失败；也不把 B 放行解释成 C/最终验收。用户仍未接受整体完成度，未扩演奏动作。

## 实际资产与许可

| 候选 | 本次核实到的文件/许可 | 对 Miao 的用途与缺口 |
|---|---|---|
| [Quaternius Animal Pack Vol.2，原作者 OGA 页](https://opengameart.org/content/animated-animales-low-poly) | 该页明确 CC0；实际 ZIP 有 Cat.blend/FBX/OBJ。Blender 5.2.3 以 `--factory-startup --disable-autoexec` 打开成功：406 顶点、402 多边形、Armature modifier、24 骨，Idle/Walking 两 action 均 0–40 帧 | 可当小型导入/骨架链路对照；预览为黑色四足低模猫，不能作为 Miao 的视觉替换。未在 Godot 播放动作，action 存在不等于动画导入正确 |
| [Blender Studio Wing It! Cat](https://studio.blender.org/characters/cat/v1/) | 作者页 CC-BY，要求署名，并指定 Blender 3.6；本次没有获取/打开实际角色文件 | 可参考成熟角色/眼睑工艺；复杂 NPR 材质与 rig 不等于可直接导 Godot。不得写成已验证 import |
| GitHub 常见宠物项目 | 例 [claude-pet NOTICE](https://github.com/Sabrina-creater/claude-pet/blob/main/NOTICE.md) 明确高级 cat.glb 要用户自备、资产许可未定 | 代码 MIT 不能推导模型许可。未把无授权 GLB 作为免费资产来源 |

Quaternius 核验文件位于忽略的 `artifacts/realtime-fidelity-research-2026-10-28/`；ZIP 大小 2,069,972 bytes、SHA256 `6d8f6789d65dbdb352ebad98a4209f26b41b384e87d81bc05e9ca76139db1248`。Cat.blend SHA256 `e9836027dc8591fd2da03e6d8d6575972bc5c7aebaa17a0762b82f7bc37264de`。详见该目录 `quaternius-cat-receipt.json`、`quaternius-cat-file-inspection.json`。压缩包内没有独立许可文件，依据是原作者对应下载页的 CC0 声明；未把下载归档重新分发到公共目录。

需要区分 [Quaternius 当前站点 QAL](https://quaternius.com/license.html) 与本次明确标 CC0 的老版 OGA 下载；不能把品牌名下所有新包都写成 CC0。也未购买其他市场模型。Modelr 旧候选的几何融合缺陷与输出地域许可边界仍成立，不作为全球站点可直接发布的替代模型。

## Godot 毛发：读过真实源码的三个实现

### 1. 优先做小验证：sofluffy

源仓 [maxvolumedev/sofluffy](https://github.com/maxvolumedev/sofluffy)，固定 commit `09af7e68c17db7b85a4780220b28dc015da28a91`，提交时间 2024-02-13。已读取 [MIT LICENSE](https://github.com/maxvolumedev/sofluffy/blob/09af7e68c17db7b85a4780220b28dc015da28a91/LICENSE.txt)、`project.godot`、`addons/so_fluffy/so_fluffy.gd` 和 `.gdshader`。

- 实际项目配置 Godot 4.2 / Forward Plus；尚无本次 4.7.2/Web 运行结果。
- 脚本以材质 `next_pass` 串联 shell，默认 64 层、LOD 最少 8 层，不需要把每层另存一份网格。源码仍然对每层重复渲染网格；没有几何副本不等于没有 GPU 成本。
- shader 是普通 spatial vertex/fragment：法线/方向位移、UV 噪声与透明裁切。已读主路径没有 compute/RenderingDevice 依赖，因而比依赖 compute 的实现更适合先做 Compatibility 小测试；这只是代码层可行性推断。
- 缺 fins；侧视轮廓、细毛阴影、壳层条带需要实图检查。原 groom 的 180k 根方向和绑定不会自动转换成它的噪声毛。
- 同一原网格多 pass 对蒙皮较有希望，README 也有 skinned bee 示例；未实测本角色形变/眨眼/指爪遮挡，不能声明已解决。

如采用，应连同 MIT 版权声明、固定版本一起保留；示例 bee 模型来自第三方，不能因插件 MIT 就沿用其模型许可。

### 2. 暂不作为 Web 默认：ShellFurSystem

源仓 [Jeff-Osbourn/ShellFurSystem](https://github.com/Jeff-Osbourn/ShellFurSystem)，固定 commit `462281c071412137da6f2c8b4921f09a89831673`，2026-01-19；实际 LICENSE 为继承的 MIT。已读 `so_fluffy.gd`、`core/compute_preprocessor.gd`、`core/instanced_renderer.gd`、`shaders/fur_instanced.gdshader`。

它扩展 sofluffy，不能把继承实现称原创。默认仍是 cascade、compute 默认关闭；compute 分支实际调用 RenderingDevice、SPIR-V 与同步。instanced 分支生成 MultiMesh，支持检查依赖 RenderingDevice；该 manager 没有发现 Skeleton/Skin 绑定转移。README 的速度提升比例与函数里的理论 draw-call/FPS 估算，不是本项目实测。先不要用它许诺 Web、蒙皮或性能胜出。

### 3. 方法参考：ShellFurGodot

源仓 [Arnklit/ShellFurGodot](https://github.com/Arnklit/ShellFurGodot/tree/b8ffa47b54511813bef9f1ccdf4d4eeb0756cb03)，该固定树的 `LICENSE.md` 已核实 MIT。实际 `project.godot` 仍 `config_version=4` / `PoolStringArray`；manager 使用 Godot 3 的 `tool`、`extends Spatial`，默认 40 层。尽管 shader 文件扩展名是 `.gdshader`，不能据扩展名宣称已适配 Godot 4。

manager 说明静态模型用 MultiMesh，skinned 模型另建多层网格；README 对 blendshape 有限制。适合作为 LOD/梳理/壳层原理参考，不优先增加一次 Godot 3→4 移植。未安装运行。

## 为什么当前工程不能「导出 GLB 就保真」

Godot `.blend` 导入也会调用 Blender glTF exporter；并不是在 Godot 内运行 Cycles。官方推荐 glTF 2.0，可携带网格/骨骼/形态键和符合协议的材质，但不等于完整 Blender 场景。[Godot 导入说明](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)

| 当前原生内容 | 转移风险 | 最小处理与判定 |
|---|---|---|
| 连续猫网格 609383 顶点；已有审计约 1,218,762 三角形 | 还不是实时拓扑；不能由「顶点数可加载」推出帧时间合格 | 先静态导入测真实 GLB/GPU 数据；保留 master，另做两档简化副本，优先保护面部、睑缘、掌指与轮廓 |
| 180k、每根 4 点 native hair，原生 root/deform 绑定 | curves/Geometry Nodes 的 groom 逻辑不会作为 Godot native hair 运行 | 原生渲染保留作标准；实时需重新选择 cards/shell 或几何化。全量转管状毛不应作为默认 |
| `BindUV` 每多边形独立绑定格；另有 `UVMap` | groom UV 不是可用的 base-color UV；UV seam 会导致导出顶点分裂。现有 UVMap 的展开质量尚未验证 | 在导出副本排除无用 BindUV，检查实际导出顶点数；材质先用 rest 色烘成 vertex color 诊断，之后验证 UV 再烘贴图 |
| `miao_rest_position` / 程序条纹 / 木材节点 | 自定义属性、任意 Cycles 节点树不自动变成实时材质 | 分开烘 albedo、roughness/metallic、tangent normal；顶点色方案启用 Godot Use As Albedo，并校验颜色空间 |
| linked area eyecards、世界光、shadow catcher、compositor 背景 | glTF 不导出 Area/World 灯光；合成结果不是实时灯光 | Godot 重建灯光/环境；眼睛高光、白眼厚度和背景阴影必须单独对照，不靠白色 emission 点伪造通过 |
| 角膜、眼睑、shadow-ray 透明近似 | 透明排序/反射与不同 renderer 不同；闭眼 P0 不能由开眼静帧推断消失 | 同渲染器实际开/半/闭眼与侧视检查，遮盖和眼角接缝有反例即停止扩展 |
| 骨骼/shape key/局部驱动 | glTF 支持并不意味着 Blender driver、GN 或约束原样运行 | 后续烘可导出的关键帧/形态键；实际测持琴接触、快速输入和连续动作，不能拿导入成功代替动作通过 |

Blender 官方说明 glTF 的材质转换只识别支持的节点布局，UV/硬边可增加导出顶点数，Area/World 被忽略；应依据实际 exporter 输出验收。[Blender glTF 手册](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html) 顶点色显示也必须在 Godot 材质启用对应选项。[Godot BaseMaterial3D](https://docs.godotengine.org/en/4.7/classes/class_basematerial3d.html#class-basematerial3d-property-vertex-color-use-as-albedo)

成本量级只是计算、不是性能实测：当前约 121.9 万三角形乘默认 64 shell，约 **7800 万 triangle-pass/帧**，还未计琴/阴影。180k 根 3 段毛若每段 6 边管截面，侧面约 **648 万三角形**（不含端盖；示例公式，不是实际导出结果）。二者均不应作为 M1/Web 的免费性能假设。

## 零现金、可证伪的窄比较

Godot 4 Web 当前仅 Compatibility / WebGL2，不支持 Forward+/Mobile/WebGPU。本机球体检查实际使用 `gl_compatibility`、OpenGL 4.1 / Metal Apple M1 Pro，见 `artifacts/godot-setup/smoke-receipt.json`；这个原生 Compatibility 检查仍不覆盖 Web 浏览器、角色或毛发。[Godot Web 官方文档](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)

建议保留原生 Blender/Cycles 完整帧路线，同时只比较以下四个独立可回退版本。不是要求一次做完四套动画：

| 版本 | 第一件事 | 必须记录 / 停止条件 |
|---|---|---|
| V0 原生 C8r2 基线 | 冻结相同机位、曝光、分辨率的整帧及脸/爪 crop | 仍未通过整体美术；不能作为用户认可的新参考。原图始终并排 |
| V1 Godot 无毛静态诊断 | 同一个完整模型副本、排除 BindUV、rest 顶点色、匹配机位；保留原始高模作损失定位 | 实际 GLB 字节/顶点/三角形、颜色丢失/眼睛、加载和帧时间；不能把无毛诊断版当交付 |
| V2 Godot 减面/PBR | 两档局部保护的简化副本；验证 UV 或保留顶点色，再烘必要贴图 | 对照趾缝、指节、方圆脸/琴轮廓；若剪影/闭眼/触弦出现 P0，不继续用更低面数追 FPS |
| V3 V2 + 短毛 | 先小局部/单一材料测试 MIT sofluffy 8/16 层；与少量轮廓 cards 比较。先 Compatibility，原生 Forward+ 可另列 | actual same-camera 图 + M1 real frame time；Web 必须本地实际导出浏览器试。壳层条带、透明排序、毛根漂移、掌/弦遮挡任一回退即停止 |

cards/shell 都是新的毛发近似，不是直接导入180k groom。对这只短毛猫，表面细节烘焙 + 少量轮廓毛/cards 可能比全身高层 shell 更便宜，但目前只是候选假设。素材 UV、方向与透明 overdraw 未测前不排优劣。

之后才测一个完整短动作：一次输入只拨弦一次，连续输入有清晰往返，不整头每音符重置；自然眨眼/呼吸需要实际序列检查。任何实时版都保留完整连接的猫、双爪与琴同帧，不退回身体板加分离手臂图片。静帧与动作都需要三位非 builder 独立判断；性能数字不能抵消身份/工艺/接触 P0。

本次没有任何 4.7.2 角色 import、Web fur 性能或动作播放结果；下一最便宜验证是 V1 的颜色/UV/网格损失检查，不是购模型、重建引擎或直接发布。费用与状态页继续按本地 pending 边界，详见 `cloudflare-zero-incremental-cost-boundary-2026-10-28.md`。
