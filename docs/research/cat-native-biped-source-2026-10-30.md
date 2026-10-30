# 开放拟人猫原生源补查 · 2026-10-30

后续更正：本报告保留旧形象范围下的历史判断。用户此后明确接受“Mewchi这类成熟Q版猫”；新核查增加了裸身正背／灰模和清楚手势图。Mewchi已在新范围下取得三位独立**有条件采购预筛GO**，不能继续引用本报告的旧轮廓NO-GO作为当前否决。当前事实与取源条件见[交接说明](../mewchi-source-handoff.md)；原生文件和操作尚未通过。

范围：新拟人／chibi猫作者源，避开已筛除的WingIt、Fishy、Panya、PKO、Juliette、Yuki、ToonCat和Cheetah。实际看过原参考 `public/character/instrument-scenes-v1/guitar/idle.jpg`，按矮梨形身体、圆方脸、短一体手臂、温和侧视与清楚爪指筛选。中途收到用户没有Full Plan、继续找开放模型的澄清，未准备任何付费取得。

**结果：本轮没有取得合格的新猫原生文件。** 这是三条新候选的有限查验结果，不代表全网不存在。没有降低外形或手部标准，没有改模型、动作、网页或状态。

## 真正开放的候选：DreamNoms Bipedal Cat

[作者原页](https://sketchfab.com/3d-models/bipedal-cat-rigged-and-animated-0ca48b993335464d8ceeab27a75c4984)。文本工具403后，正常IAB浏览器实际打开了作者的模型页和可动viewer。页上明确标CC Attribution，并链接[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。作者称673 faces、walk/run/idle/alert idle/jump五段动作，另有324faces低模层；页面显示1.3k triangles、665vertices。这些结构/动作数量仍是目录声明，未导入原生文件实测。

实看viewer：灰紫色猫，头部横向很扁、巨大尖三角耳、眼睛与脸细节呈低分辨率贴图读感；身体虽有胖腹，仍有清楚脖颈/头身分段，手掌是很小的末端，未看到能逐指按键或握琴的分指。整体属于低多边形游戏角色的完成度，与目标短绒圆方脸和清晰厚爪差距大。**视觉NO-GO，不下载后再重建头身手。** 没有因CC-BY或已有动作而放宽质量门槛，也没有提取viewer模型。

证据：`artifacts/cat-native-biped-source-2026-10-30/dreamnoms-author-viewer.png`，为实际浏览器图；它不是本地Blender渲染或动作验收。

## 两条VRChat原作者路线：实际预览可用，但不属于本轮开放源

| 作者资产 | 实际作者图与原图差距 | 取得与许可事实 |
| --- | --- | --- |
| [drawforfood Squishy Base](https://booth.pm/en/items/4517355) | 逐张看了封面、表情和完整六体变体图。橘猫变体有完整裸毛身体，但细颈、长腿、较窄上身、小手与巨大幼态眼，不是原猫短脚、头腹连续的胖梨形。需要体块/肢体重构才对齐，NO-GO。 | 作者列Blender/FBX和手部权重修正。个人2,575JPY、商业6,437JPY（读取时页面值）；商业内容/品牌用途与源模型公开分发分开限制。不是CC0/CC-BY，也没有匿名免费源。未购买或下载。 |
| [drawforfood Mewchi](https://booth.pm/en/items/4627622) | 实看封面及三色完整站姿。圆润猫脸和可见爪垫有成熟设计，但耳与幼态眼很大、脸侧毛尖、腿长，预览身体被毛衣遮挡；不凭“毛衣可切换”断言内部身体符合原图。NO-GO。 | 作者列.blend/.fbx、表情、eye look和手势。个人3,216JPY、商业7,712JPY（读取时值）；商业内容用途与原模型分发分别受限。用户澄清后不继续付费路线。未购买、签条款或下载。 |

截图分别为同证据目录 `squishy-author-whole.png`、`mewchi-author-preview.png`。本地再用图像工具打开了后者，确认保存的是三色完整站姿，不是加载占位图。两条都不能以“VRChat有手势”推出原生独立指骨、权重或弹琴接触已验证。

## GitHub方法论线索不冒充成熟猫资产

[raydeStar/reference-asset-compiler](https://github.com/raydeStar/reference-asset-compiler) 是新检索命中。已通过GitHub connector实际读取完整递归tree，commit `cb4499ccc6c226b8ebc7b8412211a46da3dead6c`，`truncated=false`，未发现`.blend`／`.glb`／`.fbx`猫payload。

README把MIT用于工具流程，示例依赖Hunyuan生成、Blender整形与rig；猫的头身拟合和部分材质仍有未完审批说明。它可以作为方法论参考，**不是可直接import的成熟开放猫模板**。没有把工具MIT扩展解释为展示图片、权重或未提供模型的许可，也没有安装/运行其脚本、下载模型权重或启动新的自建链。

## 执行边界

- 未下载合格native，没有新增SHA可冒充模型取得；现有三张预览仅作研究证据，不进入`public/`。
- 未登录、注册、购买、接受新绑定条款、联系作者或绕访问控制；创建的IAB研究页已关闭。
- 不进入三角色candidate gate或动作。公开状态由root统一沿既有机制记录，本文件不宣称交付或目标完成。
