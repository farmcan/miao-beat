# 成熟猫角色资产检索 B · 2026-10-29

结论：本路没有找到一个比 Blender Studio《Wing It!》Cat 更强、又已确认能够直接抱琴的第二候选。不能把搜索结果里的“猫模型”一律当成可用角色。本路实际下载并打开了官方 CC0 毛绒猫 Fishy Cat，但它是静态造型，不适合只改颜色、摆姿后用作 Miao 主角；保留为工艺参考。Wing It! 的实际模型下载与原生检查由 scout-a 负责，避免重复工作。

## 目标及实看基准

实看 `public/character/instrument-scenes-v1/guitar/idle.jpg`：饱满圆方脸、胖梨形身体、短而连贯的四肢、圆三趾、温和侧视、橘色短毛/虎斑、身体和琴的比例自然。用户本轮已经允许优质 stock cat 改色，不把逐点复制旧身份当作唯一目标。研究重点仍是成熟、可爱、可抱琴，不是任何免费猫都算成功。

## 已取得的实物：Fishy Cat（不推荐作主角色）

- 作者：Manu Järvinen；Blender 2.74 官方 splash（2015）。[Blender 官方介绍](https://www.blender.org/news/cat-splash-fever/)明确称包含 `.blend` 的包为 public domain；[官方 benchmark readme](https://projects.blender.org/blender/blender-benchmarks/raw/branch/main/cycles/fishy_cat/readme.txt)明确 `License: CC0/Public Domain`。作者在[原始竞赛贴](https://blenderartists.org/t/2-74-cat-splash-contest/634544?page=6)也标注 CC0/Public Domain。
- [官方直接下载 ZIP](https://download.blender.org/demo/test/splash_fishy_cat_2.zip)，匿名下载成功，34,539,564 字节；原包保留在 `artifacts/upstream-cat-candidates/scout-b/splash_fishy_cat_2.zip`。
- 实际取得原生 `fishy_cat.blend`，33,346,847 字节；原包还含作者的最终 splash PNG、XCF 和 Comfortaa 字体 ZIP。字体与 Blender logo 不属于本次模型使用范围，未单独引入项目产品。
- 已打开包内作者 render：`artifacts/upstream-cat-candidates/scout-b/fishy-cat/splash_274-double.png`。毛发、眼球、角膜与灯光工艺成熟，原生造型有鲜明趣味；但巨头、小腿、嘴鼻表情与胖梨形拟人抱琴目标差异大。
- 用 Blender **5.2.3 LTS** 只读加载原 `.blend`，开启 `--factory-startup --disable-autoexec`；只运行本地自写对象清单脚本，**没有运行包内脚本**。记录：`fishy-cat/metadata.json`。实际 **0 armatures、0 actions**；`cat` 网格 108,409 顶点/216,712 面，存在 `long_hair` / `short_hair` 粒子毛发，眼球/角膜独立对象，`eye_iris.png` 与 `fish.png` 已打包。
- Blender 5.2 读取旧文件时，很多旧材质槽呈 null；因此不能把能打开文件等同为现代材质可正确渲染。尚未迁移旧材质，也未作新渲染或动画验收。
- 模型/原始场景数据许可：上游明确 CC0/Public Domain。纹理：原场景打包纹理，官方整体场景声明没有另列例外，但未发现纹理独立作者记录。脚本：文件有辅助 Text datablocks，未取用或运行，未因场景 CC0 推定这些辅助代码有独立可复用授权。
- ZIP SHA-256：`22769b4b003330eccd13de3450555bb50f2500827c4cf1997eefa365acfec275`。
- `.blend` SHA-256：`4b5a97bed6361f1a1f888e02eda8ebda338276ff0afe46c5a170dac55bba36d5`。
- 官方原文许可 readme 已存 `fishy-cat/upstream-readme.txt`；全文件清单及 SHA 在 `scout-b/sha256.json`。

**判定：静态毛发/眼睛工艺参考，不是“成熟绑定猫已找到”。** 为抱琴重新做躯干、肢体、手指、拓扑和绑定，已经超出“直接导入稍作修改”的低成本路线。

## 交叉核对及排除

| 项目/资产 | 实际证据与许可边界 | 不晋级原因 |
| --- | --- | --- |
| [Blender Studio Wing It! Cat](https://studio.blender.org/characters/cat/v1/) | 实看官方预览，成熟表情/手指/控制器；CC BY 4.0，指定恰好 Blender 3.6。匿名页 `Login to Download`。官方预览已存 `blender-studio-cat-preview.webp`。另一路已解决合法文件来源。 | 可晋级的第一主候选，由 scout-a 做文件和导入审查；这里不重复声称完成导入。 |
| [nrz/ylikuutio 的 JonasDichelle 猫](https://github.com/nrz/ylikuutio) | GitHub tree 当前 commit `18fc0276dc0ba3d468a3bb744393758202a22501` 确实含 `res/objects/www.blendswap.com/86110_rigged_and_animated_cat/cat.fbx`，1,373,356 字节，blob `c85764aa0ab8a9de7ceffd59ae94acffca49da67`。README 分别声明引擎代码 AGPL-3.0、猫模型 CC BY 3.0，不能混为一种许可。实际下载并打开仓库 `screenshots/cats_2020-10-08.png`。 | 是普通四足写实猫，和可爱胖拟人猫/抓琴需求差异显著。未因仓库活跃便断言旧猫模型近期维护。模型二进制下载一次 SSL 失败，因造型已排除，不作重试。 |
| [Quaternius Ultimate Animated Animals](https://quaternius.com/packs/ultimateanimatedanimals.html) / [Ultimate Monsters](https://quaternius.com/packs/ultimatemonsters.html) | 官方分别宣称 12 动物/50 monsters，FBX/OBJ/Blend，CC0。实看官方 `ultimateanimatedanimal.jpg` / `ultimatemonsters.jpg`。 | Animals 是四足低多边形；Monsters 里的 Cat 是无适用抱琴四肢的球形头像，成熟库不等于存在匹配猫。没有将整库作为猫候选。 |
| [Tomcat94 Cat Pilot](https://opengameart.org/node/95204) | 2019-03-09，作者页面明确 CC0、`.blend` 6.6 MB、diffuse、走跑/欢呼/戴眼镜动作及眼睛 blendshapes。实取并打开官方 `preview_787.png`。 | 手绘贴图与硬低多边形面部工艺低于目标；不为匿名可下载而推荐。未下载/导入其 `.blend`。 |
| [squibblejack Toon Cat](https://blendswap.com/blend/22931) | 页面 CC0、31.1 MB、描述 pose lib/NLA/hair dynamics；原描述要求 Blender 2.80+，与页面自动标签 2.7x 不一致，应以实物检查解决。下载页要求登录。 | 预览 CDN 403，未能实际看图和取得模型，不把文案当视觉验收。没有绕登录或猜测下载接口。 |
| [dvnobles Furry Kitty](https://blendswap.com/blend/12865) | CC0，旧 Blender Internal、简单 rig，衍生自 leonquist 的 Popsicle Cat。 | 年代久、只有简单绑定且原图/实物未验证，不能当高质量成熟角色。 |

Superhive `Free Pack - Cartoon Dog, Cat` 搜索摘要列 Creative Commons，但页面 403，具体猫造型、完整许可版本与下载边界未证实，**不列入候选**。GitHub 检索同时遇到仅工具/MCP、生成管线、无艺术品再分发授权的宠物项目，均排除，不能拿代码 MIT 自动覆盖模型。

## 本路可复用结论

先让 scout-a 的成熟 Cat 做真实导入、材质/表情/手指检查，胜过继续为已不匹配的低多边形猫扩大工作。若它的造型不能接受，再针对可爱胖拟人猫的作者源文件搜索；不回到重复 primitive 自建。此记录为研究输出，未修改生产猫、未制作新动画、未发布网站。
