# 猫模型：值得看的链接与付费判断

2026-10-30。用户希望先看真实链接，只有足够好才考虑付费，避免低质量资产与无效迭代。当前**没有足够证据推荐为本项目购买以下候选**。这不是说全网没有合适模型；本轮未取得新的合格猫原生文件，也没有放行动画。

## 实际看过的三个作者模型

| 链接 | 实际视觉与格式证据 | 当前判断 |
| --- | --- | --- |
| [sanbianzi — Cartoon cute fat cat](https://www.turbosquid.com/FullPreview/2164765) | 正常浏览器实际看 gallery 1/9 和2/9，商品页显示 **$180**、Maya2019 / Arnold4.0.3、XGen毛发、rigged。毛发、鼻口、肉垫与材质确有制作完成度；第二图明确为趴姿四足猫。 | 值得看工艺参照，**不建议为本演奏项目购买**。前腿是承重结构，未证明拟人掌指，亦未证明能保留毛和rig移植Blender。价格与rigged标签不能解决这些差距。 |
| [Juliette — Stylized Chubby Cat Plays Guitar](https://www.fab.com/listings/5a18f454-1760-4dc0-a4bb-9ce7d640fc65) / [Sketchfab可查看入口](https://sketchfab.com/3d-models/stylized-chubby-cat-plays-guitar-c4d1cf1e76ed4e8d96ce1d00c7c1750f) | 实看完整作者预览，胖身短肢与抱琴题材接近；作者称hand-painted/rigged，Fab列FBX与转换GLB等。 | 值得看整体方向，**暂不买**。图中尖趾、脚腹脸侧块面明显，眼藏墨镜；爪在琴头/琴体边缘，未证明按品和拨弦。买回来仍可能需要重做手与表面。 |
| [PKO — Chubby Stylized Cat](https://www.blendkit.com/asset-gallery-detail/6ece9b9e-f62d-4543-9e47-a0c23ab53f5c/) | 作者预览胖裸毛身比制服飞行员接近参考；Full Plan / RF，原生未取得。 | **不建议为这个预览开会员**。前臂/掌/指骨不可读，毛发横层与原图短绒不同；核心演奏能力没有证据。 |

以上仅采购前预览判断，不是原生质量 gate。三个非 builder 角色均实际查看原参考和相同作者图，分别留档：[身份](cat-purchase-preview-identity-2026-10-30.md)、[工艺](cat-purchase-preview-craft-2026-10-30.md)、[接触/动作](cat-purchase-preview-motion-2026-10-30.md)。三者均不支持当前付费采购；没有用精致毛发平均掉不适用的手部结构。

TurboSquid的初始设备检查自行结束后才正常读取页面；未解验证码或绕鉴权。实际页面截图在 `artifacts/cat-paid-quality-comparison-2026-10-30/turbosquid-fat-cat-gallery-{1,2}.png`。作者图仅用于研究，没有放入产品或声称为项目成品。

## GitHub：实际源码不等于现成美术

- [kachus22/bongo.cat.3d](https://github.com/kachus22/bongo.cat.3d) / [在线Demo](https://kachus22.github.io/bongo.cat.3d/)：本轮重新读取官方README，作者明确是计算机图形课程项目，用primitive forms搭猫，A/D敲鼓。可参考Three.js按键响应，**不推荐把角色当作本项目精致原模**。Demo链接来自README，本轮没有重新运行Demo。
- [lucanicohe/bongo3d](https://github.com/lucanicohe/bongo3d)：本轮connector实际读取main递归tree，commit `d4956e61e2af67427ca98627c1eaa47e78819a64`；主要Unity编译Build/TemplateData，未列`.blend`/FBX/GLB源。不能当成已发现可import的成熟猫，亦不从编译游戏抽模型。
- 新检索的Rigvero官方README明确为idea/design阶段、无可用代码与下载，故不作为方案推荐。代码许可证也不会自动赋予第三方模型/贴图的使用权。

## 搜索覆盖与停止边界

本轮按旧官方API响应的`next`逐页读取BlenderKit cat查询其余201项，连同前50项共251条metadata；原响应与SHA保留在 `artifacts/cat-catalog-pagination-2026-10-30/`。这只是一次查询的完整目录覆盖，**不是251件都做过视觉、原生或动作验收**。主要通过rig/名称/尺寸筛选，实际新增查看Juris的Cute Cat：巨头、小制服身体、手为小末端，仍非目标梨身；不进入源取得。

中文/日文与开放biped路由分别记录于 [中文作者源核查](cat-native-chinese-source-2026-10-30.md)、[biped源核查](cat-native-biped-source-2026-10-30.md)。没有把免费或有骨架误写成可用开放成熟源。

下一次取得候选前，应先有清楚的裸身多角度图、前臂/掌指结构、去墨镜或侧视表情，以及实际按键/握持的控制证据。仅有好看正面或rigged标签的候选不启动大改，不再让低质量模板占用动作和网页迭代。
