# 有界备选素材研究：Innerscene Key Forty MIDI Keyboard

日期：2026-10-30。范围：现成键盘作者页／许可／真实 GLB 下载与纯数据只读检查。没有创建 Blender scene、没有改猫、没有做键盘动作或新架构；吉他薄琴适配继续，本项不替代当前目标。

## 结论与更正

**保留一个已实际取得的 CC0 次选道具：Innerscene 的 Key Forty - MIDI Keyboard。** 真实作者 viewer 已查看普通及放大画面，模型为有倒角、清楚黑白键缝、实体外壳和后排旋钮的深灰键盘；它比无倒角的纯方块占位物完整，适合进入“中央八个白键”的可行性检查，但不能宣称已是最佳／精致终稿或已适配猫爪。

它实际为 **40 白键 + 28 黑键，共 68 键**。此前研究中曾因超过 13–37 键而先行排除；现追加更正：13–37 只是本轮为短臂大掌提出的设计偏好，并非用户硬约束，所以撤回“仅因键数不合格”的结论并保留原有检查证据。只选中央一组八个白键，不必切掉其余源几何。未扩大搜索，也没有为满足自设数字改造键盘。

**素材可用不等于整猫静态或动作通过。** 模型没有按键 rig／动画，猫的腕位、指腹宽度、逐键触及、键程和遮挡均未实测。

## 来源、许可与访问

- 作者／权利声明方：Innerscene Corp；[作者素材页](https://www.innerscene.com/tools/library/3d-parts/key-forty-midi-keyboard-0d9952a4)。页面明确说明是 Innerscene 原创模型、CC0。
- [实际查看的作者 3D 预览](https://www.innerscene.com/v/1OsfHTpZk30OrLQ1R9ggSy)：Chrome 显示 `RENDERED` 和 `26,140 triangles`，普通视图后按 Zoom in 放大两次，实际查看完整键列、黑键分组、键端倒角与外壳厚度。没有用页面介绍代替视觉判断。作者 og-image 端点返回 403，未保存或伪造本地作者 JPG；成功查看的证据是作者 viewer 的实际画面。
- [公开原文件下载入口](https://www.innerscene.com/api/library/key-forty-midi-keyboard-0d9952a4/download)：无需登录、支付或接受新条款，实际下载为 GLB 2.0。
- [官方 CC0 说明](https://creativecommons.org/publicdomain/zero/1.0/)允许修改、分发和商业使用；[素材库条款](https://www.innerscene.com/tools/library/terms)说明贡献者须持有所含模型、纹理等的发布权。这里读取了条款，未创建账号或提交接受。

**模型／材质分别核验：** 作者页与 GLB `asset.copyright` 都明确写 Innerscene、CC0 1.0 和可修改再分发；材质是该同一文件内的三种 PBR 材质，四张图均嵌入，无外部贴图 URI、无另列第三方贴图库条款。材质／贴图按作者对完整原文件的 CC0 声明保留来源；没有把程序插件的许可证套给它。没有 rig-code 或嵌入脚本需要另行执行／授权。虽 CC0 不强制署名，项目仍宜保留来源和后续修改说明。

## 固定原包与只读实测

独立目录：`artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/`。

- 原包 `piano-midi-keyboard.glb`：**734,812 bytes**。
- SHA-256：`346f1f4ae12154dd7757e599abc0d3c285dc7aa61648e73c9c8bbc6c9e289a62`；检查后相同。
- 来源回执 `SOURCE.json`，作者页／条款／viewer HTML，文件内许可证据 `LICENSE-EVIDENCE.txt`，完整 glTF JSON `gltf-structure.json`，测量 `readonly-audit.json`，全目录校验 `checksums.sha256`。

检查仅用 Python 标准库解析 GLB JSON、二进制 POSITION／索引／PNG header 及节点变换，未导入运行任何来源代码，也未导出新的模型。

| 项目 | 真实文件实测 |
|---|---|
| 几何 | 86 nodes；85 mesh nodes；26,140 triangles |
| 按键组织 | 40 个 `Ivory piano key*` 与 28 个 `Raised black piano key*`；68 键全部为独立 node 和独立 mesh |
| 整体尺寸 | X 宽 720.000 mm；Y 高 76.000 mm；Z 深 210.000 mm，和作者所述一致；Y-up |
| 白键实体尺寸 | 宽 15.3925 mm × 厚 16.000 mm × 深 112.000 mm |
| 白键中心间隔 | 16.3750 mm；白键间隙约 0.9825 mm |
| 黑键实体尺寸 | 宽 9.1700 mm × 高 22.000 mm × 深 63.000 mm |
| 中央八白键范围 | 源白键 indices 14–21，`Ivory piano key.014` 至 `.021`；外缘跨度约 130.0175 mm，中心跨度 114.6250 mm |
| 键列规律 | 黑键按相邻白键间 2／3 分组，所选 14–21 是 C 至下一 C 的相对布局；源没有 MIDI octave 标记 |
| 原点／动作 | 键节点位于各自实体中部，不是已设置好的后端铰链；0 skins、0 animations；不能称可直接正确下按 |
| 材质 | 深灰粉末涂层、象牙色缎面、黑色塑料共 3 种；6 texture references 复用 4 张嵌入 PNG |
| 贴图 | 一张 256² normal，三张 128² base-color；是轻量材质，不是 2K／4K 精细贴图 |
| 外部依赖 | 无外部 buffer／贴图 URI，无 glTF 扩展，无 rig 或动画代码 |

## 审美与适配边界

预览的键与机身有真实厚度，黑白关系和键端圆角清晰，没有品牌文字负担。材质朴素，后控制条少；我将它定为可用次选，而非与 Blender Studio 角色同等完成度的高端产品渲染素材。台面总深 210 mm、白键可见实体深 112 mm；猫手应接近前缘键区，不能让短臂越过整个机身去摸后排旋钮。

720 mm 总宽不意味着猫必须触及两端。中央八键约 130 mm 可作为逐键试验范围；但白键仅约 15.4 mm 宽，大掌猫的实际指腹可能同时覆盖邻键，这一点仍未测量。不能仅因键已分离就宣称“八键逐个按”已完成。整体缩放可以等比改变键宽和琴体积，具体比例应在测量原猫可达范围与指腹后决定，不能先生成新装配图。

最便宜的后续证伪：只读比较源猫一根可用指腹在预定击键方向的投影宽度，与 15.3925 mm 键宽／16.375 mm 节距，以及中央八键位置的原生腕肘可达范围；先判断是否存在合理等比缩放与键盘位置，使单键接触且邻键不被同一指腹压住。没有可行区间就弃用此键盘；有区间也仍须整猫双爪键盘同框的静态三角色评审，之后才谈按键行程和动作。

## 有界探索留下的访问缺口

曾核实 [atilayas 的 NTK mini 作者页](https://sketchfab.com/3d-models/midi-keyboard-piano-instrument-3a518f3d6bd54ff08554206757c93168)，其页标 CC BY 4.0，但公开下载实际打开登录框，viewer 同时报模型过重；没有可用已登录会话，没有下载原包、没有独立材质许可清单，也未把它升级为本轮推荐。未创建账号、购买、接受条款或绕过下载限制；不继续为它扩大素材搜索。本报告只有上面这一个已取得的键盘次选。

研究结果未写入 public/、未部署、未替代吉他链。持续任务状态由主任务统一记录；本页是本地素材与许可证据，不是公开产品交付。
