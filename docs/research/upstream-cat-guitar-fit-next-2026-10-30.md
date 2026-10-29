# 下一成熟双足猫模板 · 有界调研结果

2026-10-30。当前 Wing It 持琴链保持冻结；本轮没有改姿态、改色、建模、装配或动画。**结果：0个达到可采用/三评阶段的新强候选；1条访问 HOLD 线索（Toon Cat）。** 没有为凑两个名字把粗糙或缺许可模型晋级，也未把此次访问失败写成“没有成熟猫模型”。

证据目录：`artifacts/upstream-cat-candidates/scout-next-2026-10-30/`。`inspection-manifest.json`列出实际取得的作者网页、原预览与SHA。模型包下载数0、原生文件核验数0、Blender渲染数0；因此没有虚构灰全身/脸/手或finger rig通过。

## 优先核查：Toon Cat / squibblejack — 访问 HOLD

- [原作者模型页](https://blendswap.com/blend/22931)；[官方文件页](https://blendswap.com/blend/22931/download)；作者 [squibblejack](https://blendswap.com/profile/43129?tab=assets)。
- 作者页/下载页明确标 **CC0**，文件条目31.1MB、原生 `.blend`。CC0允许复制、修改及分发（含商业用途），许可说明见 [官方 CC0 deed](https://creativecommons.org/publicdomain/zero/1.0/)。这是模型页的声明；未取得文件，不能进一步核实嵌入代码、每个贴图/视频条目的单独来源。
- 页面自动标签为 Blender2.7x，但作者说明要求 **2.80或更高**，还描述pose lib、NLA和packed demo video。这些仅是上游声称；未核验可操作掌/指控制器、实际拓扑或现代版本兼容性。
- 官方下载页本次仍显示 **“Sign in to download”**。匿名网页抓取403；Chrome作者页停网站安全验证，未绕过/完成验证，也未创建账号、付款或接受新条款。未找到由作者明确授权的独立公开原包链接，不猜测隐藏下载接口。
- 实际预览URL已核对到作者页面的CDN图片，但CDN与公开preview route本地取图均403，浏览器亦受阻。图片搜索只返回索引描述，**不当作已亲眼检查像素**；本轮不能复核帽子风格、完整圆掌和手指质量。不得仅据pose/NLA字样给素材GO。
- 模型包SHA、native格式实物、指骨数量/层级、依赖、原色新鲜渲染均 **unknown / not acquired**。当前只保留有明确开放声明的访问线索，不能开始采用。

另一个未来实物检查点：作者称compositor以输入图片替换render layer。若以后合法取得，必须辨别实时几何渲染与packed预览图，不能直接把打开文件看到的合成图当作本机模型成功渲染。这个注意项来自作者说明，不代表已发现恶意代码。

## 实际看图后淘汰的相邻项（不是强候选清单）

### hiamBoz · simplecathumanblendfile

[原作者页](https://hiamboz.itch.io/simplecatpersonblendfile)声明CC0、`.blend`、Blender4.1.1、simple rig与三个动画。网页与两张作者原图已实际下载并用图像工具查看：`simplecat-preview1.png` / `simplecat-preview2.png`。

胸腹/臂长较充裕，但实际图是偏人体比例的纤长猫人，肘腕转折粗硬、手掌/指尖偏尖细，脸和材质还呈个人练习完成度；无法满足当前“精致可爱、有饱满体积、成熟圆掌明确指形、原色能生产”的素材门。**视觉淘汰，不下载它继续修成另一只猫。** 因已在预览门淘汰，不把原包未检查解释为rig失败，也不花时间安装4.1只为测一个不拟采用的模板。

### Alpha Centauri Studio · Free Cats Characters – Rigged

[免费原作者页](https://alphacentauristudio.itch.io/free-low-poly-rigged-cats)，对应[完整包](https://alphacentauristudio.itch.io/responsible-cats-pack)。已取得并实际看免费页两张作者原图：`responsible-cats-free-preview1.png` / `responsible-cats-free-preview2.png`，也在浏览器查看页面。

原图显示巨大圆头、短小身躯，厨房场景中的白手为简单mitten读法，没有足够清楚的成熟指形可作为本任务的强候选。免费页只列FBX/烘焙贴图、rigged，`.blend Source`仍写SOON；页面未明确CC0/CCBY或可再分发修改版的开放许可。免费价格不能补上资产许可与指骨证据缺口。进入其作者提供的免费入口并选择不捐赠后，浏览器文件页未可靠加载；没有支付/填邮箱/接受条款，没有取得RAR，亦没有把页面声称当finger rig已核验。**不晋级。**

## 补充搜索边界与排除理由

做了围绕CC0/CCBY、rigged、biped/anthro、`.blend`/GitHub原作者的focused搜索。未发现本轮可直接取得、又在实际质量/指掌/许可门同时成立的第二强候选。没有从Sketchfab封闭viewer提取资源，也没有将仓库MIT套到角色资产。

- [panya1bp free cartoon rig](https://panyabp.gumroad.com/l/axidf)继续保留此前的独立许可缺口；“$0+”不证明可修改再分发，不因搜索又命中而改判。
- [MirceaKitsune anthro wolf/fox/cat](https://blendswap.com/blend/19859)虽有CC0声明，作者定位是写实成人女性兽人解剖，明显偏离本轮可爱音乐角色，不将它列为强候选或下载后再大改。
- Cat Pilot等已实际否定的旧低模未重列；Trevor Henderson horror Cartoon Cat不是本任务风格；完整商业包/Full Plan与无源再分发范围的第三方镜像未下载。

## 当前交接

本轮没有可供三名非builder进行**实物**candidate gate的文件，不能称新模板采用完成。Toon Cat目前只适合等待合法作者下载访问条件变化后继续核验；不让访问unknown自动变成质量PASS，也不回退自建猫。

若要继续下一次模板研究，筛选重点仍是现成的较宽胸前工作区、足够自然弯肘余量、手掌与成熟六弦琴比例、作者原生拇指/长指控制器与原色成片质量；这些是设计偏好和实图问题，不设僵硬的头身数字门。Wing It键盘环境的并行支持没有被替换、缩小或编辑。
