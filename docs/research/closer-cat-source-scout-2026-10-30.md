# 更接近原图的成熟猫模板 · 有界补充检索

2026-10-30。先实读既有 `upstream-cat-scout-a/b`、`complete-cat-guitar-assets-scout`，实看原 `public/character/whole-piano-v3/idle.jpg`。本轮不重复推荐 Wing It、Fishy Cat 或 Quaternius，不改模型、不制作动作。

**结果：新找到一个比飞行员更接近“胖猫完整抱木吉他”的成熟作者作品，以及一个圆胖可爱角色；但可合法直接取得、开放再分发、实际native可检的合格新模板仍为0。** 未把付费预览、API动画数量或能看到viewer等同为源包已到手。以下是可进一步评估的实际来源，不是通过的替代品。

## 1. 最接近整体目标：Juliette 的 Stylized Chubby Cat Plays Guitar

- [作者Sketchfab页](https://sketchfab.com/3d-models/stylized-chubby-cat-plays-guitar-c4d1cf1e76ed4e8d96ce1d00c7c1750f)；[官方metadata](https://api.sketchfab.com/v3/models/c4d1cf1e76ed4e8d96ce1d00c7c1750f)；[作者Fab出售入口](https://www.fab.com/listings/5a18f454-1760-4dc0-a4bb-9ce7d640fc65)。作者 Juliette / JulietteArt，发布于2024-10-13。
- 实际查看1920px作者预览 `artifacts/closer-cat-source-2026-10-30/c4d1cf1e76ed4e8d96ce1d00c7c1750f.jpg`：圆方脸接胖梨形躯干、短肢短脚、嵌入虎斑；双臂与完整木吉他已经处于同一场景。比例及抱琴主题比蓝服/护目镜的 Wing It 更接近原图，且不需先自行构建持琴布局。
- 差距同样明确：白灰毛、墨镜遮眼、手绘低模/局部硬边，没有原图温和侧视与短绒层次；手较小，作者静帧右掌位于琴身上缘而不是明显弦接触。左手真实按弦、右手拨弦及袖口/琴接触不能从这张预览确认；不能因为它标题是“弹琴”就签动作通过。移除眼镜后是否有完整眼睛未知，不能预先保证“改橘色就好”。
- 官方metadata：33,870 vertices / 66,762 triangles、1条动画记录；作者称rigged/hand-painted。Fab明确源格式 **FBX**，并列converted GLB/glTF/USDZ，没有原生 `.blend` 证据。未检查骨架、指骨、网格、材质图或原速动作，未做Blender导入。
- **取得/许可未通过**：Sketchfab `isDownloadable=false`、Standard而非CC BY/CC0。Fab为购买入口，本次文本不显示价格；标注 **Allows usage with AI: No**、Generated with AI: No。该标签具体约束范围未在本轮解释或替作者同意，不能把它作为AI生成参考或直接接进公开GLB。没有购买、接受新条款或访问viewer archives。
- 可执行下一步：先由实际许可/源文件取得路径决定是否进入候选三角色预审；取得合法FBX后先只读检查原始眼/手/rig并按作者原始姿态渲染，不能直接宣称可用。若眼睛/手需要重造，按reset规则换模板。

## 2. 可爱但结构更不适合弹奏：deko_ai 的 Cute Chubby Cat

[官方metadata](https://api.sketchfab.com/v3/models/1de04206dde44ee6a86f89b0579e2305)、[作者模型页](https://sketchfab.com/3d-models/cute-chubby-cat-1de04206dde44ee6a86f89b0579e2305)。实际1920px预览在同证据目录。

实看是圆方大头、圆胖肚、白色口鼻/腹、短肢和可爱的玻璃黑眼，亲和力优于飞行员惊讶脸；但头身明显分球，手是无可辨指节的小圆团。没有乐器。2,940vertices/5,525triangles、metadata19条动画（描述18条）；这只能证明上游记录，不能证明手指可动。Standard、`isDownloadable=false`，没有取得源包或独立贴图许可。为了符合用户“手指清晰”恐怕需要重做手，不建议继续导入适配。

## 本轮公开许可结果为何没晋级

| 实看对象 | 许可/取得 | 不符合目标的具体证据 |
|---|---|---|
| [Omabuarts Toon Cat FREE](https://sketchfab.com/3d-models/toon-cat-free-b2bd1ee7858444bda366110a2d960386) | CC BY4.0、downloadable=true；未取3D | 实看是四足、1,358vertices/2,636triangles，耳/脸/腿有明显低模折角，无拟人手；改成抱琴/按键不是简单颜色适配。 |
| [alexandra.m.neville Behemot Cat](https://sketchfab.com/3d-models/behemot-cat-f7bc7fac947548c8a99836f9edbf5755) | CC BY4.0、downloadable=true；未取3D | 作者预览是细长黑猫、骷髅和灯笼，不是胖短肢毛绒猫；还涉及原画衍生权利边界。 |
| [Oscar Creativo CAT CARTOON CUTE](https://sketchfab.com/3d-models/cat-cartoon-cute-by-oscar-creativo-254bd1caa4d54300a625120913cf4cd7) | API CC BY4.0、downloadable=true，但作者描述同时All rights reserved；未取3D | 实看写实猫头/赛博单眼装置，非温和短绒胖猫；许可描述冲突保留，不静默只取宽松一侧。 |

BlenderKit/Blendkit新检索的[Adorable Rigged Cartoon Cat](https://www.blendkit.com/asset-gallery-detail/426deba8-c111-4ffd-8038-d378d9c9ba3c/)官方列Full Plan、Royalty free、5,367polygons；没有拿“有rig”替代明确造型或开放文件授权，不晋级。页面相关Free knitted cat toy不等于适合弹奏的成熟绑定手；不扩大下载。

## 检索与边界

本轮两批web聚焦检索 + 官方Sketchfab目录 `toon cat`（downloadable）、`cute chubby cat`、`cat character rigged`。最后一项初次本地打印遇到null license处理错误，之后只重取该查询并安全输出；不是来源“无结果”。只保存公开作者metadata与预览，没有下载任何三维文件、插件、外来脚本，没有购买或绕登录。全证据与SHA在 `artifacts/closer-cat-source-2026-10-30/provenance.json`。

更接近的完整抱琴成品确实存在，前轮0个结果不能解释为“不存在”；当前缺的是合适开放许可/源包与实物审查，而非再写一套自制几何。停止重复泛搜，优先判定Juliette整套资产的实际可用许可；否则继续现有成熟模型的原生控件/简单材质有界验证，任何需要大改头/躯干/手的方案仍应被静态gate挡住。研究输出由主任务统一记状态；本子任务未发布产品或状态页。

## Root 后续现场补证（不混入本 scout 的独立实看）

Root 随后通过 IAB 实际打开 [BlendSwap Toon Cat 22931](https://blendswap.com/blend/22931)，Cloudflare自动检查正常结束，无验证码、无绕过。其现场作者预览截图：`artifacts/closer-cat-paid-reference-2026-10-30/toon-cat-author-browser.png`。Root观察到高礼帽、紫长裤、黄披肩、细长拟人腿/白手套、蓬长毛脸；成熟，但不符合胖梨形/短肢裸毛目标。因此这一路现在可按“实际视觉不匹配”排除，不继续把旧CDN403当作预览未知或授权阻塞。本 scout 本人未重新打开该IAB页，以上明确为root现场证据与判断，不伪称独立复核。

Root还实看CGTrader `chubbycat6983384`：证据 `artifacts/closer-cat-paid-reference-2026-10-30/chubby-cat.webp` 及同目录receipt。Root报告$11、四足短腿/X眼、基本rig，无适用拟人手，已排除，不为它索预算；本 scout未做源包或独立许可/价格核验。Root的GitHub查询由其独立记录，不并入本报告的独立搜索覆盖。
