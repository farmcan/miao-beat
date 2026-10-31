# 3D 方法重选：先取得美术成立的源，再解决可控演奏

2026-10-31；独立调研角色，未制作本轮模型、未安装/执行新代码、未购买或上传资产。本次查阅当前上游官方网页、代码说明/模型卡与作者实测文章；没有把网页示例当本机或Miao质量验收。

**结论：3D路线有成熟实现基础；本轮应换“源资产与验证顺序”，不应继续替旧粗模加细节，也不应把失败归因于Blender做不到。首选成熟native角色＋现成精细琴，保留原生材质、固定相机离线渲染完整场景。实时GLB另设保真门，不让Web导出损失反过来限制原生美术质量。** 新模型静态三评仍是动画前置；新高模预览像好不能代替原包/关节结构验证。

## 三个值得直接看的实际方向

1. **可复用的开放操作链：[Mesh2Motion在线应用](https://app.mesh2motion.org/)、[源工程仓库](https://github.com/Mesh2Motion/mesh2motion-assets)。** 官方提供原生Blender控制rig、模型和动画，明确资产CC0，应用代码MIT；源说明使用Blender4.5。可下载研究骨架定位、控制器、动作导出和网页操作，而不是从零造整套动画基础设施。[官方应用README](https://github.com/Mesh2Motion/mesh2motion-app)要求手动调整骨架再测试，不是传模型即可获得正确演奏。[作者说明](https://mesh2motion.org/)称前端用常规JS/TS、不调用AI服务。本轮只核实仓库与许可，未运行其在线操作或审阅手指骨源码，不能承诺自带精确琴指。其示例美术也不自动符合Miao；只复用成立的工具/控制链，不把示例角色硬改成新猫。

2. **同资产可复核的方法案例：[Jefrie：作者对比AI绑定与脚本绑定](https://aaronorelup.com/ledger/ai-rigging-vs-a-script/)。** 文章附实际灰模对照及测试细节，10月8日还追加纠正。作者报告：标准人形适合AI，但特殊尾巴、披风和指名会出错，现有骨架上的skin-only比盲目换整套rig更值得试。属于作者测试，非本轮独立复现；其量化数字不推广为Miao结论。可借鉴的是固定同一网格、相同测试姿势、保留失败结果，不能借“脚本胜出”重新启用已被拒绝的自建猫。

3. **参考图保真静态生成上限：[TRELLIS.2官方可看结果](https://microsoft.github.io/TRELLIS.2/)、[代码](https://github.com/microsoft/TRELLIS.2)。** 官方展示带PBR和重新打光的3D资产，说明单图转几何/材质并非只能做到旧粗模；但这些是作者展示，不是Miao指掌、拓扑或绑定完成证明。代码/模型官方标MIT；官方当前运行条件仍是Linux、NVIDIA至少24GB。没有因此租GPU或付费调用，也不声称本Mac可原生跑。Hunyuan/Modelr旧失败及许可已在既有文档评审，不再换名字重复试。

## 自动绑定只解决一个阶段

新核对的 [SkinTokens官方代码](https://github.com/VAST-AI-Research/SkinTokens)和[官方权重卡](https://huggingface.co/VAST-AI/SkinTokens)都标MIT；支持生成骨架＋权重，也支持给现有骨架只预测权重（`--use_skeleton --use_transfer`）。官方要求NVIDIA至少14GB、CUDA；不是本机Mac现成能力。[官方免本地安装Space](https://huggingface.co/spaces/VAST-AI/SkinTokens)存在，但本轮未上传/取结果，免费队列、稳定性和模型质量未实测。主体模型/贴图许可仍随输入源，不被工具MIT替代；模型卡的许可声明也不能消除第三方输入资产的权利边界。

它不会补出缺失手指、修正错误脸壳或恢复猫琴粘连区，也不自动产出弹琴动作。只有源模型外观/结构通过静态门、且原生rig确实缺失或有测得权重问题时，才比较成熟原生绑定、Mesh2Motion模板与SkinTokens单个局部试验。先看掌指独立性、可弯折掌根、拇指方向和器物接触；不要先给坏几何自动rig再以“能动”包装。

## 成熟生产方法与本项目差异

Blender Studio的[Stylized Character Workflow](https://studio.blender.org/training/stylized-character-workflow/)与[Snow开发目录](https://studio.blender.org/training/stylized-character-workflow/chapter/snow-character-development/)列出从设计雕刻到身体重拓扑的阶段；本轮搜索可读目录，直接取正文返回402，因此不声称已看课程或取得课程源。成熟制作把造型、可变形拓扑、材质和绑定分开验收；增加细分/渲染采样并不等于完成这些环节。这个方法不意味着本项目应重新手工造一只猫，当前仍以用户批准的优秀模板优先。

旧Modelr灰模被拒的具体问题包括眼睑/眼球缺失、猫琴同大连通组件、弦桥孔软化、指掌遮粘。它证明“整幅抱琴图直接生成一体网格”不适合作本项目现成可演奏源，不证明图生3D或3D整体无效。若成熟源路线后来真无可用模型，新的生成输入应先是无琴、露出两掌和指间隙的角色设计，琴使用已取得的成熟独立资产，再完整场景渲染。此为备选方法假设，不是已批准重开生成/大修旧网格。

## 下一步只做一个决定性静态实验

- 先取得一个用户外观认可、许可清楚的成熟源。按作者支持版本打开，禁自动执行，保留原mesh/原下载，先看完整身体、脸和掌指，而非先改色。
- 用已取得精细琴装配一个固定相机全场景；不重建头身/手掌。若静态握持必须大改解剖，换模板。先做完整灰图＋脸掌近景三评，再同机位带材质三评。
- 先用native离线完整帧验证精细度；未通过时不扩动作、不靠有利角度/毛发/灯光藏问题。通过后首次动作只是一指压键与回弹，另测指腹接触、关节、器物固定和头眼配合；网页GLB往返或短帧序列传输再分别评。
- 明确停止：需要大规模造手/重建脸；源无可用变形拓扑且清理接近从零制作；灰/色任一P0；导出严重丢眼/材质。失败保留证据、换下一成熟源，不能把工具安装、能导入、能动当通过。

这条路线与图片方案不矛盾：精致native 3D可离线渲染成每帧整猫双爪乐器的轻量序列，浏览器不必实时加载复杂rig。最终仍须交付可操作效果和独立实际动作judge，不能止于研究链接。

## 更贴近目标的鼓手猫成品

[Juan Carlos CR作者成片](https://www.instagram.com/reel/DcLCp78PeFT/)与[建模过程](https://www.instagram.com/reel/Db-IEa6voU0/)，对应[80.lv报道](https://80.lv/articles/awesome-stylized-drummer-cat-rig-in-blender)。报道说明基于teretoast设计、用Blender重建并绑定动画，且该猫rig不提供下载；作者的[免费模板站](https://thedonutrig.com/)目前列Donut/DonutDog/Sword，不能误写免费猫。root已读取报道及作者资源站，Instagram直接抓取限流，未独立播放视频，不当作动作judge通过。它是具体目标与制作过程参照，非可复用猫源。
