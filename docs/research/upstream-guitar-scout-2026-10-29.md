# 现成古典木吉他候选核验 · 2026-10-29

状态：找到一把值得独立外观评审的强候选，已合法匿名下载、只读审计、本机复现；**尚未外观通过，尚未改造、接触、动作、接入或发布**。另一把已下载核验但材质工艺较弱，列为筛除证据，不作为第二强候选凑数。

## 首选：Classic Guitar — Rohma Ansari / BlenderKit（现 Blendkit）

- [作者模型页](https://www.blendkit.com/asset-gallery-detail/8e698ef0-7ab1-4fab-acd6-e5accda027c1/)，作者 [Rohma Ansari](https://www.artstation.com/rohmaansari)。2024-12-26 发布，API 版本 1，asset version ID `f29d35dc-78af-46db-b9b9-50064ea02dcc`，源文件 Blender 4.3.0。
- 模型页与官方搜索 API 均标 `cc_zero` / Creative commons zero。原始模型、API、页面、作者预览、官方许可说明与 [CC0 1.0 法律原文](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en) 均已归档在 `artifacts/upstream-guitar-candidates/blenderkit-classic/`；完整 URL、作者与分项许可见 `provenance.json`。
- 模型/嵌入贴图：供应方将整个下载资产以 CC0 提供；未发现另附第三方贴图来源或独立条款。不能把这写成独立查证了三张贴图的作者身份。代码：未运行或复制 BlenderKit 插件；本次本地审计脚本与模型/贴图许可分开。渲染：可由 CC0 资产制作输出；CC0 不授予商标权。
- 官方下载 API 首次返回 403，正文是 `Parameter scene_uuid not set`，并非鉴权拒绝。按官方插件公开协议补随机场景 UUID 后，匿名 API 返回下载地址，curl 下载原始 `.blend` 成功；没有账号登录、凭据、付费、插件或访问控制绕过。临时下载签名未留档。
- 原始文件：`classic-guitar-original.blend`，17,344,119 bytes，SHA256 `e94d430f908ade7bf3daa3f8a3978f9f16ddd780aa7cd312d81135958067d900`。

作者预览（原始作者资产页面缩略图；不能代替本机复现）：

![作者原图](../../artifacts/upstream-guitar-candidates/blenderkit-classic/author-preview-1024.jpg)

本机检查图（24 samples，新增检视灯光/镜头仅存在内存；没有保存或改动原模型几何、材质、UV、transform）：

![本机完整琴](../../artifacts/upstream-guitar-candidates/blenderkit-classic/local-full.png)
![弦、琴码与音孔](../../artifacts/upstream-guitar-candidates/blenderkit-classic/local-bridge.png)
![品丝、琴颈与弦](../../artifacts/upstream-guitar-candidates/blenderkit-classic/local-neck.png)

### 实测结构

Blender 5.2.3 LTS，build `e13b728c6880`；`--background --factory-startup --disable-autoexec --python-exit-code 1`。只读脚本与检查 JSON 留档；未载入用户启动插件，未执行资产嵌入代码。

| 项目 | 本机核验 |
|---|---|
| 对象 | 单个 joined mesh `Classic Guitar`；没有 rig 或修改器 |
| 网格 | 71,372 vertices / 146,822 edges / 75,507 faces |
| 连通岛 | 55 个；六条长弦岛各 572–602 vertices；18 个品丝岛各 16 vertices |
| 是否独立弦 | 是真实几何连通岛，**尚不是六个独立对象**；未拆分或修改 |
| 材质 | 一个 `Guitar` 材质，Principled、normal map 与分通道纹理节点 |
| 贴图 | 三张 packed 4096×4096 图片，UVMap；外部贴图缺失不是本次阻塞 |
| 尺寸 | 0.413772 × 0.139267 × 1.111706 m；transform scale 全为 1 |
| 整体形制 | 古典木琴，槽式琴头、六弦、真实琴码/弦结、音孔与完整侧厚 |

### 对照原始 Miao 图的外观判断（侦察员初筛，非独立评审通过）

参照 `public/character/instrument-scenes-v1/guitar/idle.jpg` 实际原图：形制、原木面板、深色指板、古典槽式琴头、完整弦与琴码符合主要方向，明显优于自行拼粗糙琴体。尺寸可作为真实尺度起点，但与猫的比例未验证。

明确缺口：

1. 琴头有 **Ibanez** 字样，原始 Miao 琴无此品牌；CC0 不等于商标授权。若外观评审接受该候选，后续应先制作无品牌版本；本轮尚未动手。
2. 作者预览及本机复现都呈现偏灰、高反射的侧板，与原图暖棕木侧差别明显，需材质评审。
3. 音孔圈放大后偏软、像素感明显，面板木纹也较平。不能称其已达到最终近景工艺标准。
4. 琴颈/琴身比例比原始 Miao 的卡通琴更修长；不应为迁就模型而拉长猫手臂。
5. 只证明文件与材质可用、弦/品是真实网格；**没有验证**爪的握持、拨弦轨迹、弦距/弦高正确性、碰撞、变形或浏览器体验。

下一步：独立外观 judge 同看原始 Miao、作者预览、本机完整图与接触区细节。未通过以前，不做猫抱琴、动画或生产替换。

## 已筛除：Innerscene Classical nylon-string guitar（CC0）

[原始页面](https://www.innerscene.com/tools/library/3d-parts/classical-nylon-string-guitar-20d45d55) / [原站交互预览](https://www.innerscene.com/v/XUnLwyzOGKfTHBpPH985c) / [供应方条款](https://www.innerscene.com/tools/library/terms)。供应方声明是 original unbranded model、CC0，直接匿名下载可用。模型、贴图作为同一供应方资产提供，未列独立贴图来源；不涉及第三方执行代码。

本机 GLB：1,439,752 bytes，SHA256 `7840fb32d675b8c07ff9bb262fd01346f36216b37fea3cece6bcddb5d014eb55`；审计见同目录 `audit.json`。84 mesh objects，六条命名 `String 01`–`String 06` 的独立对象、品丝和琴码/弦结均存在，贴图 packed 2K；原站 viewer 显示 35,602 triangles。结构容易检查，但表面木纹呈较生硬重复条带，边缘/镶边工艺简陋，琴头太规整。**不因匿名 CC0 容易下载就认定高质量，不推荐进入当前外观门。**

![Innerscene 原作者预览](../../artifacts/upstream-guitar-candidates/innerscene-classical/author-preview.png)
![Innerscene 本机检查](../../artifacts/upstream-guitar-candidates/innerscene-classical/local-full.png)

## 其他搜索边界

- Sketchfab 的 [varebal Spanish classical guitar](https://sketchfab.com/3d-models/spanish-classical-guitar-80e6ddc78c054b6fa9ee1e779b207ea8) 公开元数据注明 CC Attribution、2M triangles、Blender 制作；页面访问 403，下载官方机制要求登录，未取得可核验原始包，不能当作已下载候选。未使用镜像、抓 viewer 或绕登录。
- BlendSwap 搜索到的老模型存在不含贴图/评论指出缺贴图，不取代已复现候选。ArtStation/TurboSquid/CGTrader 的免费不代表允许原模型再分发；未接受结算或购买条款。
- 未使用 Godot，没有修改 `public/`、没有发布。现阶段只交付侦察与审计证据，不属于生产美术资产交付。

## 可复现证据

- `artifacts/upstream-guitar-candidates/audit/inspect.py`：读取结构、连通岛、贴图清单；不写模型。
- `artifacts/upstream-guitar-candidates/audit/render_inspection.py`：在内存加入检查镜头和灯光，只输出 PNG；不保存 blend。
- 两个目录均有 `provenance.json` 与 `SHA256SUMS`。原始资产与检查输出分名保存。
