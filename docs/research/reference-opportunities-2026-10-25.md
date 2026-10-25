# Miao Beat：值得验证的开源/社区机会（2026-10-25）

本轮只研究，未安装参考项目、未修改产品、未运行它们的端到端演奏，也未发布。通过 GitHub 原始 API 核仓库、默认分支固定 commit、README、许可证和下列关键代码；网页 API 另查 MDN。维护时间为 2026-10-25 的读取快照，不将 stars、搜索排名或作者自述当作 Miao 转化证据。

## 结论

优先三件：**修正冷启动第一声的闭环、拿合格键盘素材验证可打断角色状态、把已有短录制做成可打开的链接**。这三件分别对应“第一下好玩、角色跟着我、弹完想发给朋友”。

先不加新乐器、AI 伴奏、社交房间或 DAW。短演奏视频导出有价值，但要排在猫动作验收后；否则只是更方便传播目前被用户否定的动画。原研究完成时没有可用键盘 MP4：此前签名视频未归档且已经过期，不能把流式观察替代可重复验收资产。随后已取得另一条新视频并归档，见文末追加记录；这不是旧对象找回。

本地审查基线为 `a0336eac721209fdef6dcaf766babf52cf685299`。发现：
- `public/app.js:80–87` 的 `hit()` 在所选音源未 ready 时先准备，再提示“再按一下”并返回；**首个演奏输入没有进入发音分支**。这是源码结论，尚未本轮真机复测；并非网络、浏览器都必然坏。
- `public/recording.js` 已有带版本/音源/乐器/BPM/拍号的真实输入事件格式及校验；`app.js:223–233` 已能回放和本地 JSON 导出导入。应复用它，不再发明一份分享数据模型。
- `app.js:98–100` 已使用 Pointer Events、capture/cancel 释放；“换成新键盘库”不是缺失能力。现有按键绑定没有逐指针跨键滑奏逻辑，可作为手机试验项，不能未经实测便叫缺陷。
- 已有口袋谱/跟弹/全屏演奏，新增引导之前应先测入口可发现性，而非再叠一层教程。

## 五个方向及实际复用边界

### 1. 第一下即有可理解反馈：上游 Bongo Cat

- 原始项目：[README](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/README.md)；[关键代码 `js/core.js:185–205`](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/js/core.js#L185)；[MIT](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/LICENSE)。
- 固定 commit：`591940644775d7cfd5167eceeeb6b97a1f9aadd4`，主分支提交日 2023-10-13；API pushed_at 2024-05-01T12:32:00Z，未归档。年代早，不按“活跃现代库”引入。
- 代码在同一按下分支去重、发声、改爪图；松开恢复。值得借的是**输入因果短而明确**，不是其旧 jQuery/lowLag/SoundManager 技术栈。
- 给 Miao：先做冷缓存/暖缓存、换乐器后的第一声检查；选择预备加载和清楚的 ready 状态，并保证真实输入不会静默丢失。若异步保留一次输入，必须绑定乐器/生命周期，在切乐器、隐藏页或取消时作废，不能迟到后冒出“幽灵音”。
- 不适合：整体搬老音频加载栈；原图获授的是作者给该网站的书面许可，MIT 不能自动转授这只猫的全部素材。继续使用 Miao 自己的角色/已核音源。

### 2. 动作有性格且不抢演奏：pixelpets 的状态优先级

- 原作者项目：[README](https://github.com/JOhnsonKC201/pixelpets/blob/79bad3a4fa340786e7fc793d20d76e7cf8db4d03/README.md)；[状态](https://github.com/JOhnsonKC201/pixelpets/blob/79bad3a4fa340786e7fc793d20d76e7cf8db4d03/src/overlay/state.js#L94)；[演奏相关优先级 `frame.js:215–230`](https://github.com/JOhnsonKC201/pixelpets/blob/79bad3a4fa340786e7fc793d20d76e7cf8db4d03/src/overlay/frame.js#L215)；[MIT](https://github.com/JOhnsonKC201/pixelpets/blob/79bad3a4fa340786e7fc793d20d76e7cf8db4d03/LICENSE)。
- 固定 commit：`79bad3a4fa340786e7fc793d20d76e7cf8db4d03`，2026-10-25T03:44:13Z；API pushed_at 2026-10-25T03:44:15Z，未归档。最近有改动不等于已稳定；README 明说 macOS beta 尚未由作者真 Mac 验证，本轮没有安装桌面包。
- 代码把最近输入维持在短活动窗内（其 typing 窗为 350ms），把闲逛/蝴蝶动作排在交互之后；被交互打断时取消旧路径，避免回到陈旧锚点。帧循环也有闲置降频。
- 给 Miao：只借“等待→准备→接触/回弹→收尾”状态与优先级；**连续输入不反复从第一帧重启整段视频，停输入后才收尾**。耳眼/呼吸可在低优先级，不能压过按键接触。
- 必须保留用户要求：键盘仍要能看出左右爪依次触及不同白键；持续演奏状态不能假装固定循环精确对应任意音符。音符真值继续由真实输入驱动。
- 不适合：把 Electron、全局键盘监听、桌面宠物功能或它的像素美术搬进网页；也不重复既有 video2dsprite/整角色生成框架。它是状态组织的参考，**不是 Miao 自然度实证**。
- 当前依赖：先获得新的、已本地归档且许可清楚的键盘动作素材；没有素材就只交付机制计划，不称动作验收完成。

### 3. 手机可连续玩：react-piano 的输入细节，保留当前 Pointer Events

- [README](https://github.com/kevinsqi/react-piano/blob/a8fac9f1ab0aab8fd21658714f1ad9f14568feee/README.md)；[`Key.js:78–100`](https://github.com/kevinsqi/react-piano/blob/a8fac9f1ab0aab8fd21658714f1ad9f14568feee/src/Key.js#L78)；[`ControlledPiano.js:99–118`](https://github.com/kevinsqi/react-piano/blob/a8fac9f1ab0aab8fd21658714f1ad9f14568feee/src/ControlledPiano.js#L99)；[MIT](https://github.com/kevinsqi/react-piano/blob/a8fac9f1ab0aab8fd21658714f1ad9f14568feee/LICENSE)。
- 固定 commit：`a8fac9f1ab0aab8fd21658714f1ad9f14568feee`，主分支提交日 2019-12-31；API pushed_at 2023-02-02T06:15:06Z，未归档。主分支多年未更新，不能按现代移动端兼容保证使用。
- 实码明确避免 touch/mouse 双触发、处理 touch cancel；鼠标可在按住后跨键滑奏。keyup 不因 modifier 状态跳过释放，避免持续卡音。
- 给 Miao：保留现有原生结构，把“双指同键/不同键、拖离键区、cancel、切后台、滑奏是否需要”做成一组真实手机试验；如要滑奏，再按每个 pointerId 管理当前命中的键，而不是整页禁止滚动。
- 不适合：为了几条输入规则引入 React 和旧组件，也不能把它的鼠标 glissando 当成“触屏滑奏已支持”的证据。默认仍是已有自由演奏，没有新增音游判分。

### 4. 弹完直接给朋友：BeepBox 的 URL 作品，不搬编曲器

- [README](https://github.com/johnnesky/beepbox/blob/355e510099d230d066d95074c16d748d59fe054c/README.md)；[`SongDocument.ts:71–96`](https://github.com/johnnesky/beepbox/blob/355e510099d230d066d95074c16d748d59fe054c/editor/SongDocument.ts#L71)；[版本化编码 `synth/synth.ts`](https://github.com/johnnesky/beepbox/blob/355e510099d230d066d95074c16d748d59fe054c/synth/synth.ts)；[MIT](https://github.com/johnnesky/beepbox/blob/355e510099d230d066d95074c16d748d59fe054c/LICENSE.md)。官网也说明歌存在 hash、用户主动分享才离开设备：[作者官网](https://www.beepbox.co/)。
- 固定 commit：`355e510099d230d066d95074c16d748d59fe054c`，2026-08-07T07:24:49Z；API pushed_at 2026-08-07T07:26:31Z，未归档。
- 实码从 hash 还原 Song、生成 compact Base64 字符串、监听 hash/history；源码在版本化格式中明确编码音色、速度、节奏等。尤其最新 commit **移除了失效的 is.gd 短链服务**，提示我们不要把第三方短链可用性当免费前提。
- 给 Miao：继续用现有 `makeRecording/validateRecording`，只加“分享这一小段”；把短真实事件写入显式版本的 URL fragment，朋友打开后点一次播放，并可接着弹。先限制短片段，超限保留 JSON，不先上数据库/账号。
- 不适合：搬整个 BeepBox synth/editor；它的序列编曲数据不等于 Miao one-shot 事件，也不能用换引擎破坏旧录制音色。链接是数据，仍需长度/事件密度/版本校验。
- fragment 通常不作为 HTTP 请求路径发送，但本页脚本可以读取它；不要承诺“绝对私密”。不自动更新分享地址或自动上传每次演奏。

### 5. 带走一段可播放作品：短音频/猫短片导出，先不整体装 RecordRTC

- [README](https://github.com/muaz-khan/RecordRTC/blob/725284477c1e7432c828971f1cff09dfcd5093d4/README.md)；[`CanvasRecorder.js:22–25`](https://github.com/muaz-khan/RecordRTC/blob/725284477c1e7432c828971f1cff09dfcd5093d4/dev/CanvasRecorder.js#L22)；[`CanvasRecorder.js:88–114`](https://github.com/muaz-khan/RecordRTC/blob/725284477c1e7432c828971f1cff09dfcd5093d4/dev/CanvasRecorder.js#L88)；[`StereoAudioRecorder.js`](https://github.com/muaz-khan/RecordRTC/blob/725284477c1e7432c828971f1cff09dfcd5093d4/dev/StereoAudioRecorder.js)；[MIT](https://github.com/muaz-khan/RecordRTC/blob/725284477c1e7432c828971f1cff09dfcd5093d4/LICENSE)。
- 固定 commit：`725284477c1e7432c828971f1cff09dfcd5093d4`，主分支 2024-02-21；API pushed_at 2024-05-13T00:39:07Z，未归档。README 的浏览器兼容表和源码中的 2016 注释不能当今天真机结论。
- 实码展示从 canvas stream 产出 WebM 的路线，但 **CanvasRecorder 构造器先硬性要求 html2canvas**，且它的 canvas stream 仅视频轨；不能称为“丢进当前 DOM 页面即能录带声音的猫”。StereoAudioRecorder 另有旧 Web Audio 录音实现。
- 给 Miao：较便宜的是先验证现有音频总线导出 8–15秒声音；等角色素材合格后，在离屏 canvas 只画角色/琴键/标题，合并 Web Audio 输出轨，导出一段文件。用户自愿保存/分享，不请求麦克风或录全屏。
- 优先复用浏览器 API，而非引入整套旧兼容层：[`createMediaStreamDestination`](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createMediaStreamDestination) 可产生音频 stream；[`canvas.captureStream`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/captureStream) 捕获 canvas 内容；[`MediaRecorder.isTypeSupported`](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/isTypeSupported_static) 用于探测编码，仍不保证资源足够或导出成功。
- 文件分享必须先探测 [`navigator.canShare`](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/canShare)，不支持则下载；不能承诺 iOS/微信都能直接发视频。采样的再分发与生成素材许可需对照已有 manifest 单独核，MIT 库许可不代替音源权利。

## 优先三个可验证方案

以下是**候选试验标准，不是当前实测指标或增长承诺**。建议一次只做一个隔离小样，不把三件并行改成一次大重构。

| 优先 | 最小样本 | 通过标准 | 停止条件与依赖 |
| --- | --- | --- | --- |
| P0 第一声闭环 | 当前默认吉他、冷缓存/暖缓存各10轮；按一次、快速换乐器、加载时切后台各一组。手机与桌面分开记录 | 用户能理解当前是否可弹；同一真实输入要么及时发声，要么明确准备态，不静默消失；无迟到音、无错乐器；录制仍只记真实输入 | 首包过重/异步导致迟到音时停止扩动画，先缩小选中音源准备成本；实体手机未测就不称全端通过 |
| P0 键盘动作状态小样 | **先补一条已归档的新素材**，只做左右交替六次按键及连续/停顿/重击三种输入；一只猫一个琴 | 连续完整片段可重复审看；左右接触/键下降/回弹可对应；连按不从头抽搐、不积压；静音观察也自然 | 视频未归档、机位/爪形漂移、任意输入无法合理映射时停止接回主站；不能用截图/计数/rig终态当自然度通过 |
| P1 短演奏分享链接 | 10–15秒、至多128事件的现有录制；暂定4KB URL预算，超限导出JSON。请3位朋友在不同设备打开并点击回放 | 无账号/无手工导入即可回听；事件顺序、BPM/音色版本一致；至少观察他们是否愿意主动再分享，而非只问“喜不喜欢” | 平台截断URL、无法说明版本、误触发自动演奏或无人愿意分享则停；4KB是试验预算而非浏览器统一上限 |

角色素材未补齐时可先验证第一声和分享链接，不能为等待资产把研究完成冒称动画完成。短片导出列为下一轮候选；实体手机输入细节先作为这三个小样的验收维度，不单独扩一套产品。

## 已排除与许可/维护判断

- 不使用搜索结果中的“official Bongo”或关键词堆砌下载仓库；必须找到真实上游、源码、许可证才纳入。没有把搜索到的 fork 列表当推荐。
- 额外核了 [Magenta Demos README](https://github.com/magenta/magenta-demos/blob/1146656d0ac54951ddf89486c264582c037f11e4/README.md) 和 [Piano Genie 转移说明](https://github.com/magenta/magenta-demos/blob/1146656d0ac54951ddf89486c264582c037f11e4/piano-genie-js/README.md)：固定 `1146656d0ac54951ddf89486c264582c037f11e4`，仓库 archived/inactive，Apache-2.0。官方[论文介绍](https://magenta.withgoogle.com/pianogenie)说明八按钮控制完整钢琴，但这会改成模型决定音高；模型/加载/维护成本和精确白键诉求不匹配。本轮不推荐移植，也不以旧 Glitch 链接当当前可运行能力。
- MIT/Apache 只解释所读代码许可；猫美术、采样、曲谱、模型与生成视频另核来源和使用条件。引用作者文字与代码机制，不复制其成品美术或现代歌曲片段。
- 本报告没有“已跑通手机”“提升留存/转化”“已发布视频”等结论。此前学习已覆盖的 Patatap、CML、video2dsprite、整角色视频路线不再重复包装成新发现。

## 本轮留痕

研究开始已 durable pending；线上状态发布未在本轮执行。此前签名视频未归档且过期，素材缺口仍需补齐；研究完成、素材待补和后续真实发布结果应分别追加，不写作动画恢复。



## 2026-10-25 后续：新素材已归档，旧对象仍未找回

用户提供了新的临时视频链接。按根线程执行证据，新下载归档脚本已将**新的键盘视频对象**保存到本地 ignored 素材目录并校验：2,775,311 bytes，SHA-256 `17a223bc41021898f120d2660b4c0787660a07ff157d1910d8f2f6f2572bd8a5`；10.041667 秒、1280×720、24 fps、H.264，无音频。临时签名链接不写入仓库。

这补齐后续动作小样可重复审看的输入条件，**不代表先前丢失的视频已恢复**，也不证明动作自然度、任意按键接触映射或音画同步已经验收。前文“素材待补”描述的是原研究时点；本次新对象已可用于后续试验。

用户随后授权整猫完整姿态 atlas 与输入驱动整合，避免每音从头重启整段十秒视频，同时处理横屏遮挡与音域导航。当前仅记录实施开始；实际源码、部署、连续输入、键盘触点、真实浏览器布局与录制回归结果仍须另凭证据追加。本研究整理没有修改公开产品或触发部署。
