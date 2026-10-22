# 竹知了与“梁氏滑动变祖器”：身份、机制与证据

核验日期：**2026-10-22，Asia/Shanghai**；本轮快照截至约12:11（04:11 UTC）。范围仅为公开资料和源码只读研究，没有复制第三方素材、部署衍生版、实现人物梗或修改产品。机器可读摘要见同目录 `hot-meme-evidence-2026-10-22.json`。

## 先给可采用的结论

1. **“竹 zhiliao / 之前 zhuzhiliao”最匹配 `imsai-sh/zhuzhiliao` 网页玩具。** 名称、此前项目研究对象和作者自己的仓库描述一致；这是高置信候选，用户未给具体链接，因此不写成绝对唯一匹配。其核心是画圈/甩动改变真实玩具采样的回放速率与响度，属于声音玩具。
2. **“梁文峰的滑动变阻器”高概率指梁文锋相关“滑动变祖器”这组梗。** 已核到多个独立网页、二创仓库和视频；具体是哪一个版本仍不能唯一确定。强候选是 `Lichtspektrum/liang-intensity-calibrator`，但不能把它的网页作者自动认作整个梗的最初图片/视频作者。
3. **梁氏滑杆当前可核玩法主要是视觉变形与社区表达，不是音乐演奏器。** 已读正式网页部署脚本和固定版本视频渲染源码：人物演变视频被显式设为静音。本轮没有证实“滑杆可弹音乐”的对应产品，视频可能有配乐，但曲目、原录音和许可均为 unknown。
4. **可学机制，不能直接拿现成资产。** 竹知了当前源码许可不授权公开部署/再分发；梁氏主仓库的代码 MIT 明确排除了人像素材。两者都不能按“GitHub 公开，所以连图与声音都可 fork 上线”处理。

## 身份匹配与同名项目分离

| 候选 | 原始来源与身份 | 本轮判断 |
| --- | --- | --- |
| imsai-sh 的竹知了 Web | [作者仓库](https://github.com/imsai-sh/zhuzhiliao)；README 指定 [imsai.top](https://imsai.top/) | **高置信目标**。当前指定入口经 web 解析跳到 `zhuzhiliao.games`；直接 CLI 抓取出现403，因此未把跳转后的完整动态 UI 当作已实玩验证 |
| `zhuzhiliao.imsai.cc`、`zhuzhiliao.icu` 等旧地址 | 旧页面/搜索快照出现这些地址；当前仓库只指定 `imsai.top` | 历史地址与当前指定入口分开登记；不能把名称相似域名都说成官方，也不能仅凭旧缓存上的声明覆盖新 README |
| andforce/ZhuZhiLiao | [原生项目仓库](https://github.com/andforce/ZhuZhiLiao)，自述 iOS/Android，SwiftUI/Metal 与 Kotlin/OpenGL，另有后端服务 | **独立原生候选，不是同一个单页 Web 仓库**。它的排行榜、地球与在线连接能力不能移植成 imsai-sh 当前网页已经具备的功能；本轮未核齐其素材授权，不建议拿来用 |
| 原页面宣传的 iOS“15种声音主题” | [旧地址搜索快照](https://zhuzhiliao.imsai.cc/)将相关功能列在“网页之外，更多原生玩法”下 | 只能当原生 App 宣传信息，不能推断当前公开 Web 源码含15音色、编曲/录音、音乐闯关；实际 App 版本与授权未核齐 |
| Lichtspektrum 梁系校准器 | [仓库](https://github.com/Lichtspektrum/liang-intensity-calibrator)、[作者列出的体验页](https://lichtspektrum.github.io/liang-intensity-calibrator/) | **梁梗网页强候选**，31档/6种称号，连续人物变化与投票。具体用户指向仍待链接确认 |
| `liang-slider.vercel.app` | [可访问页面](https://liang-slider.vercel.app/)、其同源 `slider.js` | **另一个具体实现候选**。页面标题和梁文锋头像旋钮直接匹配；站内未找到可核作者、发布日期或素材许可，因此不能认作 Lichtspektrum 原站或最初原梗 |
| HunLuanZhiZhu 连续版 | [作者仓库](https://github.com/HunLuanZhiZhu/liang-intensity-calibrator)明确致敬 Lichtspektrum | 已证实为**二创**，不是原梗作者证据。自述 AI 首尾帧+插帧+Canvas seek；人像使用权仍不由“AI生成”自动证明 |

## 竹知了：代码、日期、声音与传播

**版本钉住：** 当前远端 HEAD（`git ls-remote`）为 `199e203b038ffb515f3a21189a29da4b4fb8518f`。初始无父提交是 [`3cb289de090d8d0b42eda200480c2d92f9e2a6d2`](https://github.com/imsai-sh/zhuzhiliao/commit/3cb289de090d8d0b42eda200480c2d92f9e2a6d2)，原始提交日期 **2026-08-02 00:56:40 +08:00**。日期来自公开 commit patch，不是把搜索收录时间误当上线时间；提交出现也不能证明同一时刻官方网页已可用。

**核实过的实现：** 当前 [`index.html`](https://github.com/imsai-sh/zhuzhiliao/blob/199e203b038ffb515f3a21189a29da4b4fb8518f/index.html)包含内嵌真实玩具音频、随转速调 `playbackRate`、2D渲染，以及按需加载本仓库内 Three.js 的3D入口。声音解码失败另有合成兜底。基础2D能单HTML运行不等于完整3D无额外资源。手机体感还涉及安全来源和设备权限，不能只看桌面代码就说手机已测。

**当前计数已变化：** 源码1325行后为本机 `localStorage` 个人计数，旧访客ID会清理；README说明早期全站计数服务已下线。此前MiaoTI八月文档保留的“约120万来客/159万访问/1.52亿哇”是**2026-08-07旧页面自报记录**，本轮没有重新审计，绝不是当前UV或当前在线人数。GitHub当前展示约2.9k Stars/333 Forks，也仅为代码关注快照，不能当网页用户数。

**传播证据：** [新黄河2026-08-05原创评论](https://www.jinantimes.com.cn/news-57-5298745.html)直接讨论当时玩具二创风波，足以证明其已进入公共讨论；不能由此归因“某个网页导致了热度”。该文引用的相关内容/失效比例又是媒体转述，和此前其他报道的5.6万等口径并非同一数据集，本报告不合并、不选一个数字当全网真实总量。[Telegram社区直接帖子](https://t.me/s/jianjiaoPD?q=%23%E7%AB%B9%E7%9F%A5%E4%BA%86)还将网页与另一个TestFlight版本分别介绍，是跨渠道介绍的证据，帖子展示次数不是独立试玩人数。

**音频与许可：** [当前 LICENSE](https://github.com/imsai-sh/zhuzhiliao/blob/199e203b038ffb515f3a21189a29da4b4fb8518f/LICENSE)是 source-available 自定义许可：准许研究和个人本地运行，不授权公开再部署、再分发或商业使用。README自述主录音从实拍视频截取；本轮未找到对应原视频URL、录制者授权与独立采样再分发条款，因此具体录音权利链仍是 **unknown**。技术可读不等于音频可拿走；本轮没有提取音频。

## 梁氏滑动变祖器：原作链、视频链与当前实现

**能够钉住的网页项目：** 远端当前 HEAD为 [`5d0bbf6be5553f5e813ac0ff8b260e6ebc2bc76e`](https://github.com/Lichtspektrum/liang-intensity-calibrator/commit/5d0bbf6be5553f5e813ac0ff8b260e6ebc2bc76e)，commit页面原始元数据日期为 **2026-08-16 16:30:53 +08:00**。该提交只是合并README二创列表更新，不代表首次发布或核心功能在当天才出现。仓库首次发布日期、全网首张梗图/首视频的作者与日期，本轮均未唯一追到，保留 unknown。

**玩法事实：** 滑杆从 -15 到 +15；6个称号位于同一连续状态轴。视频帧负责平滑人物过渡；新增的社区层允许浏览器投票、显示平均值及每日快照。后端是 Worker+D1 的 `/api/score`、`/api/vote`、`/api/timeline`。这是“拖一维参数表达今天的评价”，和演奏音高/节奏是不同机制。[固定版本 `src/video-renderer.ts`](https://github.com/Lichtspektrum/liang-intensity-calibrator/blob/5d0bbf6be5553f5e813ac0ff8b260e6ebc2bc76e/src/video-renderer.ts#L95)创建视频后明确 `muted=true`；正式部署JS也相同。只读查询当前score接口返回403，**没有拿到实时投票人数**，也没有投票。不能把“存在计数实现”写成“已经查到活跃用户”。

**可核传播不止 Stars：** 仓库页面当前展示333 Stars/36 Forks；[NodeSeek直接讨论](https://www.nodeseek.com/post-870071-1)明确贴了该仓库和官方体验地址，另串联了不同价格驱动版本；作者README也列出多个独立二创/插件。它们共同支持“有人传播并延伸了此交互”，不证明网站已大规模成功或现在仍爆红。该论坛只显示相对日期，本轮不反推一个精确发布时间。

**视频链分开记录：**

| 页面 | 可核日期/归因 | 能证明与不能证明 |
| --- | --- | --- |
| [B站 BV1uHu66XEC1](https://www.bilibili.com/video/BV1uHu66XEC1/) | 搜索索引显示2Taken，2026-08-11 21:49:04，简介明确转自小红书用户5931227970，带AI生成标识 | 索引约7.6万播放，是该转载视频的历史抓取值；原页/API本轮412，非当前实时数。原小红书笔记ID/首发日期未得，**不能叫原视频** |
| [B站 BV1mVg76XEei](https://www.bilibili.com/video/BV1mVg76XEei/) | 搜索索引显示逸世itsuyo，2026-08-13 05:29:19，自称在Lichtspektrum项目上做二创并加投票 | 索引约4.9万播放，说明某个演示被观看；不是原网页UV。描述是否后改未知，不把视频时间直接等同于仓库首次上线 |
| [VibeFriends CSDN视频](https://live.csdn.net/v/539569) | 可访问原帖2026-08-14 00:18:27，介绍群友的 `zu.01mvp.com` 六阶段网页 | 证明还有另一实现及明确发布页；页面只展示未标口径的46，不能据此评判用户规模；创作者与Lichtspektrum是否同一人未知 |
| [子夜梦廊新浪/微博页面](https://www.sina.cn/news/detail/5332837163077541.html) | 2026-08-17 09:42，使用梁文锋滑动变阻器称呼 | 证明当时此称呼与人物已形成具体公共帖子；没有最初原作者和音频许可信息 |

本轮检索也遇到把图片作者归给 `Transformer-周`、把该谐音追溯到成龙版本的聚合/AI简报；没有补到相应最初原帖链，**不采用这些归因当事实**。即便多个二创都称某仓库“原项目”，也只证明它们继承的代码/网页来源，不证明整个网梗由该仓库作者首创。

**素材权利单独判断：** [Lichtspektrum README的素材说明](https://github.com/Lichtspektrum/liang-intensity-calibrator/blob/5d0bbf6be5553f5e813ac0ff8b260e6ebc2bc76e/README.md)明确：代码MIT，`media` 与 `public/frames` 的人像不随MIT共享。本轮也未找到任何候选人物图、视频音乐、现场原声或仿声的可公开再分发许可。AI生成标识只说明制作方式，不能补齐人物/素材授权。`liang-slider.vercel.app` 的同源脚本仅发现视觉滑杆逻辑，没有音频或音乐引擎；其作者与资产许可也仍unknown。

## 对 Miao Beat 的可复用结论

- **借单动作的反馈强度：** 竹知了把转圈直接连到音高、响度与惯性；对应到Miao Beat，是每次敲击马上听见可识别音色和看到明确一只爪的动作。此处是产品推断，不是证明换皮就有相同增长。
- **借一个参数的可读变化：** 梁系滑杆的价值在于每个位置都能看懂状态差异，并有表达意义；如果未来用原创猫角色做强度/情绪/音色参数，应让效果可听/可见，不能只换人物贴图。
- **保持当前目标：** 用户要自由演奏/创作；这些案例不构成加入音游判分、滑动成绩、人物评价榜或实时价格小部件的授权，也不证明应照搬它们的后端复杂度。
- **可复用的边界：** 研究技术方法、用本项目已有许可素材做独立验证；不复制竹知了受限实现，不导入梁氏人像/音乐，不按不唯一的原梗猜测制作人物meme。若后续用户给具体视频/网站，再补原作者链与实际声音，避免研究错对象。

本轮只新增本报告和证据JSON；没有以搜索结果数量、缓存播放数、Star数、作者自报计数或技术实现来冒充实际UV/流行度。
