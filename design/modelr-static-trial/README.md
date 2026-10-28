# Modelr → Miao 原图：单个静态 shape 候选

2026-10-28。本目录保存试验入口和复现条件。**真实链路已跑通，当前是待独立评审的静态候选。** 固定权重精确通过SHA和字节数校验；唯一seed17完整推理用69.93秒生成GLB，已导入Blender5.2.3保存原生工程并渲染三张1024px灰模。环境、推理和导入成功不代表角色保真、可绑定或美术通过；本builder不作自己的独立通过评审。

## 冻结的来源与许可

- Modelr：`https://github.com/ZimengXiong/Modelr` @ `c6a10959d2499477962aed5643fcb172dbf09457`。源码 MIT，保留 `Modelr-LICENSE`。固定 codeload tar.gz SHA256 `ae6333ffe5ac47a67a0867820133f6a47c889b8a202a75e5542749d1e9fc9544`。
- 仅 small shape：`zimengxiong/hunyuan3d-mlx-shape-small` @ `b7536809d38ad13fe6a9b7769a41fd5d42e520df`。`config.yaml` 1628 bytes / SHA256 `cabcba7f6115752c8fe5b370e12bf714936f70377a8a80f151872f76c2d64609`；模型 3819958234 bytes / SHA256 `3cc66f3bea33e4062b7dbc875ffe1d70c4888914aec3e91b60f94e9bd01b522b`。
- **权重不是 MIT**，为 Tencent Hunyuan3D-2 Community；模型卡明确指向此许可，根许可有地域、用途和分发条件。许可快照保存在本地 `artifacts/modelr-trial/Hunyuan3D-2-LICENSE`，模型卡在同目录 `model-card.md`。试验输出只供本地资产评审，未放入 `public/`、未在全球网站分发。没有购买、付费 API 或 paint 权重下载。
- 主参考：`public/character/instrument-scenes-v1/guitar/idle.jpg` / SHA256 `4418fd737891283f42568306cb427b1f7604a86cae5513b1d6c49b3c31f338d1`。

## 已实际跑通的环境

Apple M1 Pro（实际sysctl），32GB unified memory，macOS26；Swift6.4，Xcode CLI 与 xcodegen 存在。项目本身内置 MLX Swift0.31.1 和 SwiftNumerics，所以不额外安装 Python/CUDA 栈。

第一次 Xcode 编译在 Metal 编译阶段失败：`cannot execute tool 'metal' due to missing Metal Toolchain; use: xcodebuild -downloadComponent MetalToolchain`。启动过 Apple 官方838.9MB组件下载，但速度很慢；没有伪称已经安装。后续用**官方 Apple MLX 的同版本预编译 metallib**解决试验运行条件，停止了未完成的组件下载。

采用 PyPI 官方 `mlx-metal==0.31.1` 的 `py3-none-macosx_26_0_arm64.whl`（49256543 bytes），SHA256 `e7324b7c56b519ae67c025d3ced07e5d35bc3a9f19d4c45fe4927f385148c59e`；其上游代码与预编译库许可 MIT。在隔离副本的 `vendor/mlx-swift/Package.swift` exclude 数组追加 `mlx-generated/metal`，其 C++/Swift 保持原实现；从 wheel 提取 `mlx/lib/mlx.metallib`（131041909 bytes，SHA256 `198488eb61359e953580a9c4530400feee1a06dd2f28a930a6ffa58aec66a597`）放在 CLI 二进制旁。这样用同版本预编译内核，避免本机缺失的 Metal compiler。

实际 `MiaoShapeCLI --selftest` 成功输出 `MLX_GPU_SELFTEST [1.0, 4.0, 9.0]`；MLX源码的默认设备为 `.gpu`。证据 `artifacts/modelr-trial/mlx-selftest.log`；另已实际重跑本目录 `prepare.sh`，构建和同一GPU小测试再次成功，日志 `artifacts/modelr-trial/repro-prepare.log`。这项小测试只证明该环境可以执行一个 GPU 张量表达式，不证明完整网络或所有内核兼容。

## 入口与命令

`prepare.sh` 封装固定源码、同版预编译内核校验和编译；`run-once.sh` 在全部权重及原图SHA通过后以排他sentinel限制一次正式生成，并用系统`time -l`记录进程RSS等指标。运行时先协调停止同时进行的Blender重渲染，避免争用统一内存。sentinel仅防重复尝试，不能作为进程仍活或生成成功的证据；需另查实际exec session/PID和输出。

`main.swift` 是窄 CLI：原生 Vision 分割前景、保存 mask/cutout，然后调用上游 `ShapeGenerator.generateGLB`。固定 **seed17 / steps30 / guidance5 / resolution256 / octree=true / quantize0(fp16)**，只一次生成；不使用随机多seed挑选。

`trial.yml` 只构建 Hy3DMLX、上游 BackgroundRemover 和 CLI，不构建 GUI/paint。

在隔离源码 `artifacts/modelr-trial/source/` 放置 `TrialCLI/main.swift` 和 `trial.yml` 后：

```sh
xcodegen generate --spec trial.yml
xcodebuild -project MiaoShapeCLI.xcodeproj -scheme MiaoShapeCLI \
  -configuration Release -derivedDataPath ../build CODE_SIGNING_ALLOWED=NO build
```

在仓库根目录执行（权重大小与 SHA 精确通过后）：

```sh
artifacts/modelr-trial/build/Build/Products/Release/MiaoShapeCLI \
  public/character/instrument-scenes-v1/guitar/idle.jpg \
  artifacts/modelr-trial/weights/shape-small/model.fp16.safetensors \
  artifacts/modelr-trial/output/miao-shape-seed17.glb
```

输出包含完整静态 mesh、输入 mask/cutout、运行秒数、顶点/面数和 MLX peak memory。**MLX peak 不等于整个进程或系统峰值内存**；若没有外部测量，进程RSS／系统swap峰值写 unknown。

`download-shape.py` 是本地断点续传辅助，原位位于 `artifacts/modelr-trial/`，只读取固定源的 manifest，保留先前已接收前缀、按 Range 下载其余部分，最终先检查精确 bytes/SHA 再命名为模型文件。模型没有校验通过就不允许推理。每个 Range 最多两次有界传输；失败保留分段与日志，下次从实际字节继续，不丢弃已有进度。

## 已有输入证据

原生 Vision 分割成功并实际查看输出：完整猫、尾巴、琴头、双爪保留。细白边仍有数像素，须在灰模比较中留意是否影响表面。

- `artifacts/modelr-trial/output/input-mask.png` SHA256 `253192b7b5fd7f836843f5ae63baf0c1f6c8f5d930a81134b73611caf5a8e23d`。
- `input-cutout.png` SHA256 `8ba710c3636b468fa705541b0d63a7e7d6c6b0ab9e2702d979002cf6796b1489`。

本候选没有毛发、颜色、UV、眼睑、骨架或准确演奏承诺。生成后只用中性灰材质导入 Blender，先检查轮廓／脸／琴爪是否融合；任一主要身份 P0 不合格就停止 rig/动画扩张，保存失败结果。既有技术原型和首页都未修改。

## 本次实际完成证据

- 运行：2026-10-28 18:21:59～18:23:09，北京时间，唯一seed17；`shape-run.log`对应exec session退出0。
- 推理receipt：`artifacts/modelr-trial/output/miao-shape-seed17.receipt.json`。生成213650顶点／427384三角面。
- `/usr/bin/time -l`：69.93秒real；maximum resident set size **4173398016 bytes**；peak memory footprint **5507714648 bytes**；记录的进程swaps为0。MLX单独报告peak **5076428040 bytes**。不同指标不能混称同一个峰值；系统全局swap／统一内存整体峰值仍未测。
- GLB：`artifacts/modelr-trial/output/miao-shape-seed17.glb`，7693004 bytes，SHA256 `b4960819ae9ab32d0e037b2cc1a0ca8f967031ec5afe5b4f41f9b994c4d47152`。
- 原生Blender工程：`artifacts/modelr-trial/blender/miao-shape-seed17.blend`，9901074 bytes，SHA256 `bf979c95e1fb1f08956e1cd17bd7721f0dc0b8238ba174f8e46a318560052f93`。
- 1024px诊断图：同目录 `gray-front.png`、`gray-three-quarter.png`、`gray-back.png`；真实导入／三图渲染退出0，最后一图累计渲染日志18.9秒。实际看过前视与侧视，确认前机位方向确实看见琴正面；未用有利角度代替完整对照。
- 导入receipt：`artifacts/modelr-trial/blender/blender-import-receipt.json`。包围盒只计算导入主体，地板从统计中排除。
- 形状技术检查：`inspect-glb.py`实际解析GLB；一个mesh／primitive，两个连通分量（213612、38顶点），无skin、无animation。大连通分量本身不能指出猫／爪／琴的语义边界，**没有证明可以独立形变或已分物体**；该结果不能当成rig完成。
- 全部文件字节数与SHA：`artifacts/modelr-trial/output/artifact-hashes.json`。综合本地记录：`artifacts/modelr-trial/trial-receipt.json`。

所有Hunyuan模型输出（GLB、blend和诊断图）仍只在本地 `artifacts/`，不放 `public/`、不commit或全球分发。本次只生成一个shape，没有paint、rig、动画或网页发布。下一项由builder以外的三名评审实际对照原图／本候选；通过前不扩动画，也不把本试验替换为正式角色。没有运行中的推理或本试验Blender进程；原始下载分段、SHA校验与终止日志保留以便复核。
