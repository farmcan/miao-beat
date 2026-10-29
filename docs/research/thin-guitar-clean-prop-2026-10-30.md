# 薄电吉他干净衍生 · 待独立素材 craft

2026-10-30。按 root 明确授权，复用 Rexodus **HH Guitar with stand** 的 CC0 几何，制作一个原创浅蓝 PBR 方案。**已完成原生渲染与5.2 / 3.6实际导入验证，未装配猫；外观仍待独立 craft judge。** 全程 factory-startup / disable-autoexec，没有插件 / 原包脚本执行。保留高精度源几何：**此2.19M tris资产仅供离线authoring，不进入浏览器默认加载。**

## 评审图与可交接文件

全部输出目录：`/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-v1/thin-electric-clean/`。

![完整琴](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-v1/thin-electric-clean/full.png)

![侧面](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-v1/thin-electric-clean/side.png)

![六弦与桥部](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-v1/thin-electric-clean/bridge.png)

我已实际看完整 / 侧面 / 弦桥三张。外观为同一套新浅蓝琴身、蓝灰背侧、深色指板、银色弦品五金与浅色旋钮，不再带原作者火纹贴图。图像证明成熟琴本体细节和薄形体；不能证明短臂猫可握、可达或动作通过。

- `thin-electric-clean.blend`：5.2原生，39,428,460B，SHA256 `185a1a07704b2e778a53293a7cbd70e4598b77f12b223a3dea78b1b2a4d73ea9`。
- `thin-electric-clean.glb`：标准GLB，51,857,764B，SHA256 `1e61a29480aecff87ea53ff65338bed7d20d7a24704707b5d2c68b526bc26938`。3.6通过此兼容GLB导入，不直接打开5.2native。
- `clean-prop-receipt.json`：原始逐对象 evaluated mesh fingerprint、排除清单、统一刚体矩阵、新材质配方、SHA与零原材料核验。
- `source-preservation-audit.json`：独立重新读取源与native，所有143对象拓扑完全一致，逐顶点世界误差最大 **0.00016898mm**（浮点刚体坐标转换）；没有重建 / 拉伸 / 压薄琴。
- `verify-native-5.2.3.json`、`verify-glb-5.2.3.json`、`verify-glb-3.6.23.json`、`glb-structure.json`：实际回执与GLB JSON结构。
- `LICENSE-AND-DERIVATION.md`、几何CC0原文、项目MIT原文、`SHA256SUMS`：许可分项与固定交接文件。

## 保留 / 清理与实测

**143个真实Mesh，2,192,095三角面。** 六条 `Spiral` / `.001`–`.005` 的已评估真实Curve几何烘为独立mesh；原先量测确认的24个品丝对象全部保留。桥部 / 调音旋钮 / 摇把 / 金属细节保留，不造新琴，不新rig，不做风格搜索。

删除主 `Stand`，以及在首轮检查图发现的独立 **`Killer` 琴架上托**（U形托，原bbox宽91.84 / 深90.32 / 高20.80mm；位于琴颈两侧，属于琴架），删除8个Font字标、2条无面辅助Curve和原根Empty。未发现独立strap；作者图后方大黑条属于琴架。没有因对象名不熟就删除桥部五金。

全部原17材质、10图像数据（包括checker）、纹理、shader groups与9嵌入文本删除。仅6个新建 `Miao_*` 材质，每个为新Principled + Output；无Image / Group节点。native重开与两版GLB导入均为 **0 images / 0原材质 / 0 textures / 0 node groups / 0 texts / 0字体**；GLB JSON本身也为0 images / textures，仅6个原创材质。初次导入检查遇到factory自带无用户Material / Render Result / Viewer Node，已在导入**之前**清空工厂残留后实际重验；没有靠事后删除传入素材使结果通过。

统一轴为 **米，+Z琴颈，-Y正面，+X横向**；只有统一旋转与平移，保留物理原尺度，所有对象scale=1。整琴规范后bbox min **(-.18147479,-.16487184,0)** / max **(.18147479,-.06879044,1.12409759)**m，size **.36294958 × .09608140 × 1.12409759m**。Body真板厚 **41.33409mm**，原几何测量41.33410mm；整琴96.08mm深包括摇把、琴头后调音器，不能把全琴称41mm。此处保留源模型所有必要硬件，未用非均匀变形迁就短臂。

5.2 native重开、5.2 GLB导入、portable3.6.23 GLB导入均通过同样143mesh / 2,192,095tri / **6弦24品**与bbox核对。首次三项导入曾并行，不符合scenario skill单agent同时最多一Blender进程，已向root说明并结束；之后源几何比对顺序单进程执行，未重跑图像 / 搜索参数。

## 来源、权利与范围

[HH Guitar with stand — Rexodus](https://www.blendkit.com/asset-gallery-detail/e641b80c-75ec-4888-b900-d63ef76057fe/)，fixed version `73aaeeda-0e93-41de-8145-dccb68ee919f`（version1）。模型/API声明CC0；**原材料有royalty_free，不能随源包 / 原GLB公开分发或放入CC0 release**。原包继续私有，SHA前后均为 `6a3cb4ad3124240e6d812c52b8ce25bb105e79de9a3ba1648544251f9f61a0ef`。完整分项证据仍在 `artifacts/thin-guitar-alternative-2026-10-30/material-license-tags.json` 与研究报告；没有把代码MIT当成模型许可。

新材质、灯光、相机与以下准备 / 读验脚本为本项目原创，按仓库MIT；几何CC0保留独立声明，不将上游建模写成原创。脚本为 `design/miao-reuse-v1/scripts/prepare_clean_thin_guitar.py`、`verify_clean_thin_guitar.py`、`verify_clean_thin_source_geometry.py`。原包、原作者图 / 材料不会列入clean公开交付清单。

下一步仅由独立素材craft judge看三张当前图及来源。未修改猫scene / pose；没有接触通过、动作通过、浏览器性能通过或已公开发布的结论。

## 跨机脚本路径补充

准备脚本的仓库根改为从`__file__`推导，不依赖本机用户名；需要把依法取得的原文件放到上述artifacts原包位置。原始几何核验脚本可在Blender命令末尾 `-- <clean输出目录> <原始blend路径>` 指定本机源路径，避免读取回执内旧绝对路径。此处只改入口路径，既有模型/渲染/导入回执未重生成，也未改变资产SHA。
