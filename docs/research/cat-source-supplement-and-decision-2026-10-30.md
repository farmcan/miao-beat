# 更贴近原图的成熟猫模板 · 补充核验与当前决策

2026-10-30。本轮不是“新猫已找到并通过”。原图仍是 `public/character/whole-piano-v3/idle.jpg` 的暖橘色矮梨身、圆方脸、短融入四肢、温和侧视和短绒。Wing It! 飞行员只保留为技术实验；只读检查已确认其躯干/四肢本身就是制服造型，不存在隐藏衣服即可露出的完整裸猫。详见[原生诊断](miao-native-identity-adaptation-probe-2026-10-30.md)。

## 实际查验后的排除，不按标题或售价推荐

| 来源 | 实际证据 | 判断 |
|---|---|---|
| [CGTrader Cute Chubby Cat #6983384](https://www.cgtrader.com/3d-models/animal/mammal/cute-chubby-cat-rigged-stylized-animal) | 作者公开预览已下载实看，四足/巨大X眼、很短的四足末端；页面$11、basic armature、.blend/FBX/OBJ、RF。 | 不是有成熟可弹琴手指的胖拟人猫。没有为了便宜或rigged字样购买。 |
| [CGTrader Cartoon Cat #1857046](https://www.cgtrader.com/3d-models/animal/mammal/cartoon-cat-ab5d7d74-3ed1-457d-8b82-e0634a041312) | 实看作者彩图：绿大眼、小四足身体。页面称Rigify/脸shape keys/约2000基础面；未取得源。 | 四足骨架和角色比例不匹配；不能把头部可爱当作可直接抱琴。 |
| [TurboSquid Stylized Biped Cheetah #2516585](https://www.turbosquid.com/3d-models/stylized-biped-cheetah-rigged-3d-character-2516585) | 实看作者彩色与rig/wire图：成熟连续胖腹、分指、面部控制；页面$90、Blender4.5/5.0、17358 quads、Standard。 | 比粗模成熟，但豹脸/大牙/长臂/长趾与原猫差距仍大；改颜色不能解决身份。未购买/取得源/独立模型验收。 |
| [BlendSwap Toon Cat #22931](https://blendswap.com/blend/22931) | 常规浏览器安全检查自动结束后，实际看两张作者图：礼帽、紫长裤、长拟人腿、白手套与长绒脸；页面CC0。 | 不再是“预览无法取得”的unknown，现有实际视觉排除依据。没有解验证码/绕下载登录，也不因CC0而推荐另一种长身衣猫。 |
| [Juliette 胖猫抱木吉他](https://www.fab.com/listings/5a18f454-1760-4dc0-a4bb-9ce7d640fc65) | 实看胖身短肢虎斑完整抱琴预览。root实际Fab页展示FBX ZIP4.39MB/转换GLB等，个人$70.52/专业$125.44（未税，读取时值），Standard，Allows usage with AI=No。 | 体型方向更近，仍只有作者预览；源rig/手指/接触未实测，墨镜后眼睛未知。没有购买、签条款或提取viewer模型。不是可以直接进公开GLB的新源。 |

实际预览、价格截图及source/SHA回执在 `artifacts/closer-cat-paid-reference-2026-10-30/`；Juliette原始metadata见 `artifacts/closer-cat-source-2026-10-30/`。公开作者预览用于本地研究，不拷入产品。

## 新发现：PKO Studio 胖猫，值得取得源后检查，尚未合格

[Chubby Stylized Cat 官方页](https://www.blendkit.com/asset-gallery-detail/6ece9b9e-f62d-4543-9e47-a0c23ab53f5c/)，同作者另有[Chubby Cat 白色版](https://www.blendkit.com/asset-gallery-detail/5c41688f-618c-49a4-9afd-2593cbeb4eea/)。

通过官方公开搜索API一次取得cat前50项（总251，非全库穷尽），并只筛看5项metadata。读取页面和IAB实际作者预览后，灰色版可见没有制服的胖身、小耳、短脚、立体大瞳与毛发；比飞行员更值得作为轮廓方向继续核验。但前爪很小、贴近口鼻，图中没有足够证据证明独立手指；长毛与原图短绒、口鼻和头腹比例仍不同。不能只因文字写professional就认定成熟手部或动画可直接用。

官方metadata：Full Plan、`isFree=false`、`royalty_free`；349421面、50objects、3textures、2K上限、35.7MiB、`rig=true/animated=true`、armature、quad_dominant、manifold=false。作者与静态页面均只是上游声明，未用Blender打开验证；搜索API的版本id与页面当前版本不应混为一份源字节（必须下载后固定SHA）。RF不是CC0，也不能默认原始GLB可公开再分发；未来若采用，先按官方许可核对可用交付方式，离线完整帧渲染与直接提供源模型分开处理。

公开缩略图常规CLI返回403，实际浏览器网页的作者webp正常显示；没有绕访问控制、猜下载URL或从viewer抽源。截图 `pko-chubby-cat-author-browser.png`。未安装插件、未开新账号、未购买会员；本机常见BlenderKit设置位置没有发现现成配置文件。已向用户异步询问是否已有Full Plan，仅询问现有资源，不是购买/签约授权。该答复到达前可以做现有乐器的静态交接，不能声称猫源已下载。

## GitHub 的实际代码/源边界

- [kachus22/bongo.cat.3d](https://github.com/kachus22/bongo.cat.3d/tree/39b4142af9ddba6f63869a88a63697e0f3a20a05)：实际README明确用primitive forms的课程项目；MIT、可玩参考不等于优秀成熟猫模型。没有引入。
- [lucanicohe/bongo3d](https://github.com/lucanicohe/bongo3d/tree/d4956e61e2af67427ca98627c1eaa47e78819a64)：实际目录主要Unity Build/TemplateData及MIT；README仅一行demo链接。没有可审的原生猫建模/rig源证据，不提取编译游戏来冒充开放模型。
- [purryc/interactive-pet](https://github.com/purryc/interactive-pet/tree/ccacfb52124f4f5d24bfd81bfdfcd6f1d444502f)：实际README是四足暹罗猫，32bones/12Actions，明确无图像/模型/代码复用许可证，且表面无原设定绒毛、前爪无IK；不是可直接拿来抱琴的成熟开放模型。没有下载或执行其生成脚本。

这些是真实源码/README检视，不宣称运行或体验了对应demo。未用代码MIT自动覆盖第三方美术。

## 当前执行决定

1. 八键琴的原成熟几何适配可保留；灰/色三角色只签prop/准备位，整角色仍HOLD。不要以此扩展Wing It八键/头部动作，见[八键装配](miao-eight-key-prop-probe-2026-10-30.md)。
2. 不继续剥衣、造腹、替换球眼、拼手或重做当前模板，也不因为付费资产而降低视觉筛选标准。
3. PKO若取得合法源，先只读检查真实骨/手指/拓扑/材质/许可证，再一张原生全身默认渲染。若前爪无成熟分指、摆位会破坏梨形/短肢，或需大幅重建，立即排除；不先改色、做动画、接网页或订阅扩展。
4. 只有匹配成熟模板的灰/彩完整角色三角色门禁都通过，才进入实际触键、八键区分和克制头眼响应。采购预览、源文件可打开、当前prop GO均不算目标完成。
