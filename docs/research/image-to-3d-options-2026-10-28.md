# 从原图保留橘猫身份：图生3D、材质与rig候选

2026-10-28，北京时间。用户已否决本轮粗糙Blender样机，要求先研究现成项目、形成计划。本轮只读官方/第三方源码、模型卡与许可；没有安装这些模型、下载权重、执行安装脚本、付费或启用外部API。

## 先解决什么

目标是把现站橘猫的脸、胖体形、橘色条纹和毛绒质感带进可控动作。不能把“生成了网格”“加了PBR”“渲染成功”当作保留了同一个角色。

本轮已实际打开并对照当前生产测试图 `public/labs/blender-guitar/poster.webp`（final-r3，SHA-256 `62037cedfd1a1feb243ecd874e6bde7064a16b4d0c8be274ff4f66f0f0c8cc3d`）与主参考 `public/character/instrument-scenes-v1/guitar/idle.jpg`（SHA-256 `4418fd737891283f42568306cb427b1f7604a86cae5513b1d6c49b3c31f338d1`）。视觉判断：当前图仍是明显分界的大圆头与竖窄主体、分节足、正面大白眼、薄而平的眉和偏小偏横的琴；前臂粗长、肩臂分段感明显，表面偏光滑玩具。原图则是宽胖连续躯干与圆方脸、朝琴侧看的神态、厚弧眉、短圆有重量的爪子、更大更斜的琴和细微绒感。当前材质是橘色；不能沿用更早样机的肉粉色或抬肩缺陷描述。此前看的final-r2只保留为历史，不作为当前生产证据。再提高采样数、加琴弦，不能修复这些身份差距；当前候选仍不应作为通过的美术基线。

建议先做**一张图→一个静态候选→同机位原图比较**，通过后再投入retopology/rig和拨弦。图生3D的用途是初始几何/纹理，不是自动完成演奏模型。当前没有一个下列项目可以直接import进现站就自动变成精致橘猫吉他。

## 五个官方项目：源码和权重分开查

以下提交与模型revision在本次查验时固定；最近提交不等于仍在积极开发，更不代表本机已运行。

| 项目与代码固定提交 | 已实现的输出 | 代码/权重许可 | 运行条件与本机边界 | 当前定位 |
|---|---|---|---|---|
| [Microsoft TRELLIS.2](https://github.com/microsoft/TRELLIS.2/tree/75fbf0183001ed9876c8dbb35de6b68552ee08bd)，2026-06-05 | image→mesh+PBR；颜色、粗糙度、金属度、透明度；GLB、UV/烘焙、remesh/减面 | 代码MIT；[4B模型卡](https://huggingface.co/microsoft/TRELLIS.2-4B/tree/af44b45f2e35a493886929c6d786e563ec68364d)也为MIT；渲染依赖另有许可 | 官方只测Linux，NVIDIA≥24GB；源码有CUDA专用网格与光栅化；不是原生Mac路径 | 有匹配GPU时最值得做保真静态对照；不将其模型放进网页 |
| [VAST TripoSG](https://github.com/VAST-AI-Research/TripoSG/tree/fc5c40990181e2a756c4e0b1c2f4d6b5202faf8c)，2025-04-18 | 高细节形状，GLB白模；可限制三角面数 | 代码MIT，[权重](https://huggingface.co/VAST-AI/TripoSG/tree/2c1c516d22d58db486a058d98d31bb6177344e06)MIT；默认另下载BRIA RMBG-1.4，其权重是非商业许可 | CUDA≥8GB，CLI硬编码cuda/fp16；无经核实的官方MPS路径 | 只能做几何候选；没有毛色纹理，不单独满足原图质感 |
| [VAST TripoSR](https://github.com/VAST-AI-Research/TripoSR/tree/107cefdc244c39106fa830359024f6a2f1c78871)，2026-06-04 | 单图mesh；默认顶点色，可显式烘焙UV颜色纹理 | 代码与[权重](https://huggingface.co/stabilityai/TripoSR/tree/5b521936b01fbe1890f6f9baed0254ab6351c04a)MIT | README默认约6GB VRAM；CLI无CUDA会强制CPU；纹理烘焙用xatlas/ModernGL，需要另验环境 | 低成本粗筛轮廓/颜色，不应承诺毛绒、PBR或rig |
| [Tencent Hunyuan3D-2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/tree/82920d643c0dc2f7bfd7255f45f62d386edfe60c)，2025-10-17 | 分离shape与paint；UV、albedo+metallic/roughness PBR、带材质GLB | 代码/权重为Tencent Hunyuan3D 2.1 Community，非MIT；[模型revision](https://huggingface.co/tencent/Hunyuan3D-2.1/tree/0b94677654c57bb9a6b6845cd7b704ccf551d327) | 官方标注shape10GB、paint21GB、合计29GB；README声称Mac/Win/Linux，但paint源码仍设cuda，Mac必须核实移植路径 | 高保真候选；不能把装了Blender就视为具备本模型运行环境 |
| [VAST UniRig](https://github.com/VAST-AI-Research/UniRig/tree/6793c6640ff01c8fb389f3993434124bb43d2933)，2026-06-04 | 已有mesh→骨架预测、蒙皮权重、与原材质mesh合并；不是图生几何 | 代码MIT；[权重模型卡](https://huggingface.co/VAST-AI/UniRig/tree/36842e2b5947e9e60f89275b83208c8e74071c63)MIT | CUDA≥8GB；依赖spconv、torch-scatter/cluster等，未核实Mac可用路径 | 仅在几何/拓扑合格后考虑，不能自动纠正猫脸、融合手臂或演奏接触 |

这五项都没有“从一张抱琴图直接得到精修猫、吉他分离对象、毛发groom、可自然拨弦rig”的完整承诺。生成mesh常为三角网，减面/remesh不等于肩肘具有适合变形的边流。PBR表面属性也不等于实际短绒毛几何或毛发着色。

## 源码核查要点

**TRELLIS.2**：已读[example.py](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/example.py)、[image pipeline](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/trellis2/pipelines/trellis2_image_to_3d.py)、[GLB后处理](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/o-voxel/o_voxel/postprocess.py)与setup。后处理实际做UV展开、体素属性采样/烘焙和材质通道写入，但内部调用`.cuda()`、CuMesh与`RasterizeCudaContext`。示例`remesh=True`不是动画retopo或骨架。模型卡也列出小孔/拓扑不连续、审美未专门对齐等限制，不能仅因为模型分辨率高就假设猫更可爱。

**TripoSG**：[inference_triposg.py](https://github.com/VAST-AI-Research/TripoSG/blob/fc5c40990181e2a756c4e0b1c2f4d6b5202faf8c/scripts/inference_triposg.py)把输出顶点/面构造成`trimesh.Trimesh`并导出，未创建UV/材质或骨架。它会自动拉取BRIA模型；[BRIA模型卡](https://huggingface.co/briaai/RMBG-1.4)明确非商业权重，不因主仓MIT而消失。后续若用已有透明图并替换背景处理，必须核实实际代码不再下载/调用它。HF页面自动生成的通用Diffusers/MPS示例不等于这份CLI支持Mac。

**TripoSR**：[run.py](https://github.com/VAST-AI-Research/TripoSR/blob/107cefdc244c39106fa830359024f6a2f1c78871/run.py)会在没有CUDA时把device设为CPU，不能只传`--device mps`就声称走Metal。[bake_texture.py](https://github.com/VAST-AI-Research/TripoSR/blob/107cefdc244c39106fa830359024f6a2f1c78871/tsr/bake_texture.py)确有xatlas UV和颜色采样，但未输出PBR材质组/毛发或rig。

**Hunyuan3D-2.1**：[textureGenPipeline.py](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/82920d643c0dc2f7bfd7255f45f62d386edfe60c/hy3dpaint/textureGenPipeline.py)使用remesh、UV、albedo和MR多视图烘焙；config仍指定cuda。根[LICENSE](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/82920d643c0dc2f7bfd7255f45f62d386edfe60c/LICENSE)是判断许可的依据，不能用API文件里残留的“non-commercial”标题替代现行根文本。该许可有地域、分发和使用条件，阈值写的是发布日条件下前月MAU超过**1 million**。腾讯不主张输出所有权，同时条款仍限制Outputs/results在适用地域外的使用/展示；不能因为输出归用户便宣称可直接全球公开。

**UniRig**：已读[权重下载映射](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/src/inference/download.py)、[skin配置](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/configs/task/quick_inference_unirig_skin.yaml)与[合并代码](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/src/inference/merge.py)。HF当前文件列表实际存在`skeleton/articulation-xl_quantization_256/model.ckpt`及`skin/articulation-xl/model.ckpt`；模型卡仍有部分“skinning coming soon”旧文字，不能只按旧文字判断权重不存在。只有骨架不等于蒙皮，README亦要求先修正预测骨架再skin；论文Rig-XL/VRoid全部结果复现仍不能从当前文件列表推出。

## 追加的两条Mac路线：第三方移植，不是腾讯官方Mac实测

### A. Modelr：本机静态候选之一，便利度不作为采用理由

固定仓：[ZimengXiong/Modelr](https://github.com/ZimengXiong/Modelr/tree/c6a10959d2499477962aed5643fcb172dbf09457)，2026-07-12。MIT代码，Apple Silicon/macOS≥14；本轮没有安装或运行。README报告M4 Max数据，未给出可用来承诺本机32GB的最低统一内存或峰值。

已读`Sources/ShapeEngine.swift`、`PaintEngine.swift`、`BackgroundRemover.swift`、`Core/MeshExporter.swift`，以及内置Hy3DMLX/HunyuanPaintMLX的Pipeline、GLB writer。实际代码有本机MLX推理、Vision前景mask、串行GPU占用、UV展开与颜色/MR贴图、GLB材质写出和取消防陈旧结果。不是仅用Swift包装外部API；但没有骨架、蒙皮或演奏rig。包内README有“host glue not ported”的旧描述，后续Pipeline/宿主代码已实现相关部分，不能只读那行断言整套paint不存在。

[model_manifest.json](https://github.com/ZimengXiong/Modelr/blob/c6a10959d2499477962aed5643fcb172dbf09457/model_manifest.json)提供权重文件revision、大小和SHA-256，可以做复现校验：

| 槽位 | HF仓与revision | 文件总量（十进制GB） | 已核权重许可 |
|---|---|---:|---|
| shape small | `zimengxiong/hunyuan3d-mlx-shape-small` @ `b7536809d38ad13fe6a9b7769a41fd5d42e520df` | 3.820 | Hunyuan Community，非MIT |
| shape large | `zimengxiong/hunyuan3d-mlx-shape-large` @ `5ad04593521ff80875ac007ef8185209368f18bc` | 4.931 | Hunyuan Community，非MIT |
| paint small RGB | `zimengxiong/hunyuan3d-mlx-paint-small` @ `29bab9dbf2a4a4f9c6988a41b0e891156a517a23` | 3.897 | Hunyuan Community及所含组件许可 |
| paint large PBR | `zimengxiong/hunyuan3d-mlx-paint-large` @ `b56e8b86b4d1e62b0bb3bbef7e2070d6ec22620e` | 8.705 | Hunyuan 2.1 UNet、2.0 VAE，加DINOv2/RealESRGAN各自许可 |

以上是下载文件大小，不是推理峰值内存。small shape+RGB paint约7.72GB权重文件；large paint还含DINOv2等，不能只按UNet大小估算。四张转换模型卡明确不是MIT。部分模型卡`LICENSE.txt`链接已404，实际[2.0根LICENSE](https://huggingface.co/tencent/Hunyuan3D-2/blob/9cd649ba6913f7a852e3286bad86bfa9a2d83dcf/LICENSE)存在；large paint来源混合2.1与2.0，需按实际组件核对，不能套一个坏链接省略检查。

可见展示是README里的作者演示视频入口；本轮未据此声称全片审看过、猫模型质量已经过关。源码足以确认可导出带UV材质资产，不足以确认能保留我们的猫脸或毛绒感。若未来执行，先本地静态评审，暂不把Hunyuan结果直接放到全球免密站。

### B. hunyuan3d-2.1-intel：可审计的MPS/PyTorch兼容层

固定仓：[thehunterofshadows/hunyuan3d-2.1-intel](https://github.com/thehunterofshadows/hunyuan3d-2.1-intel/tree/6f4b63bd6419406f40291bca23a7c849bcaae2a3)，2026-08-09；页面标明fork自`VladimirTalyzin/hunyuan3d-2.1-mac-rocm`。它既不是腾讯官方仓，也不是仅面向Intel CPU；实际含Apple MPS/AMD ROCm后端。

已读`backend.py`、`compat_patches.py`、`paint.py`、`mesh_io.py`、`torch_rasterizer.py`和`tests/test_paint_render.py`。存在实际MPS设备分派、chunked attention、`torch.isin`/float64兼容补丁、纯PyTorch光栅化、UV/纹理GLB输出，以及不加载生成权重的渲染/bake对照测试。测试自身明确说不能替代完整扩散生成验证。

作者README报告：M4 Pro 24GB、macOS26、torch2.13，shape约344秒，Safe纹理约512秒；Safe为6视图/256多视图分辨率、2048纹理。**这些是作者报告，本机未测。** README例图明确全部来自AMD8060S，不是Mac猫咪质量证据。其安装会下载约30GB组件，MPS纹理阶段作者报告约8GB swap；32GB能否改善仍是推断，不保证。源码还会解除PyTorch MPS soft cap，不能把它说成无内存风险的轻量默认方案。

许可根文本与官方2.1 LICENSE相同；`LICENSE-WRAPPERS`仅列出的包装文件为MIT，不覆盖上游权重/代码。README写100 million MAU，而根LICENSE实际1 million，采用根文本。新增的其他文件是否在MIT文件清单内也要按实际声明判断，不把整个仓统称MIT。优点是底层路径/测试较透明，成本是环境/补丁和磁盘负担；本轮不运行安装命令。

## 能直接import什么

| 对象 | 能否直接进当前站 | 原因/正确位置 |
|---|---|---|
| 现站采样、按键、媒体导出组件 | 可以继续复用 | 已有`SampledAudio`、bindings、完整canvas的MediaRecorder链路 |
| 图生3D Python/MLX模型 | 不能 | 离线工具；显存/依赖/许可不适合直接塞浏览器 |
| 生成GLB/OBJ | 可导入Blender作候选，不能据此宣称网页演奏已接入 | 当前产品是完整场景帧播放；还缺拓扑、分物体、骨架和动作验收 |
| UniRig输出 | 仅离线候选 | 需合格猫体mesh与修正骨架；不能把吉他一起骨骼化 |
| 合格完整渲染帧/图集 | 符合现站素材接口 | 必须每帧完整猫、相连双爪和吉他；随后实际验证输入与成片 |

## 第一个最小可证伪试验（计划，尚未执行）

1. **冻结原图标准**。以现站`idle.jpg`为主参考，保留原始SHA和画布；列出必须保留的头型、瞳孔/眉鼻、腹部比例、橘色条纹和爪形。现有三视图仅作辅助，不默认与该图完全一致。先不做动作，不换猫，不继续在已否决模型上微调。
2. **只跑一个按质量筛过的静态候选**。先以原图保留程度、网格可修性和许可筛选，再看硬件与下载成本；Mac可运行不高于质量。若筛选后采用Mac候选，可用Modelr small shape作单个固定seed试验，确认环境、权重许可和可用内存后才执行；本轮尚不下载。先验证轮廓，通过后才追加RGB paint，不一开始跑PBR大模型。若可用NVIDIA环境下TRELLIS.2更符合目标，应优先按质量比较，而不是为Mac方便迁就低质输出；没有资源就记录缺口，不自行租GPU。
3. **同机位原图差距评审**。原图、候选同视角材质渲染、候选灰模、±45°与背面图并列；记录光照/焦距/尺寸。灰模看结构，材质图看颜色/条纹，不能只拿有利角度或强光掩盖差距。重点标出头身轮廓、眼距/朝向、口鼻、爪肩、猫与吉他是否粘连。只展示静帧时明确不是演奏成品。
4. **静帧通过后才清理与retopo**。单张抱琴图存在遮挡，模型可能把琴、胸、前爪融合成一块；这是几何问题。保留猫身份，分离猫与琴，补遮挡结构、肩肘变形边流；再重投射原纹理并检查UV接缝。自动remesh/减面不代替这一轮。必要时应采用成熟许可清晰的猫体底模并重塑/重贴图，胜过继续程序堆球。
5. **只rig一条拨弦链**。猫体合格后再尝试UniRig或已有Blender rig流程；吉他固定独立物体，左爪握持，右肩/肘/爪有连续变形。先三个关键姿态（准备、接触、离弦），每个都渲染完整场景并同原图评审；随后24帧短动作。最后才接独立网页测试、单按/按住/150ms与80ms连按、真实视频导出。

### 每轮必须留的质量记录

`输入图SHA / 代码commit / 权重revision / seed / 参数 / 时间 / 峰值内存或unknown / 输出mesh与贴图SHA / 固定机位对照图 / 通过与失败项 / 下一步`。结构、脸部身份、颜色/条纹、毛绒、肩爪连接、琴的比例各给“保留/部分/失败”，并附可见证据；不能用一个平均分掩盖脸部失败。毛绒只写贴图效果时，不称其有真实毛发groom。

### 停止条件

- 任一候选出现明显换脸、头身比例走样、眼神丢失或光滑球体感，静态阶段判失败，不继续rig和整段动画。
- 同一输入最多两次有目的候选；两次仍同类失败，就停止该路线并保留结果。不得靠调灯光/换角度/反复换seed凑通过。
- 猫爪与琴粘连、肩肘拓扑不能独立变形、主要纹理无法稳定重投射时，转清理/retopo或成熟底模，不继续网页动画。
- 内存/扩展不兼容、下载许可不清或必要资源不存在时，记录具体失败与下一可验证动作；不安装整套CUDA栈硬套Mac、不自行付费。
- 静态保真和动作两道关都通过前，不替换正式站。每轮都回看原图，不能把上一轮勉强能动的错误猫当作新身份标准。

本轮完成的是源码研究与可执行计划。所有新生成模型、毛发、蒙皮、Mac推理性能、网页自然度和公开资产许可适用性仍需对应实测/核验。
