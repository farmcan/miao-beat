# 小红书小工具 · 独立技术可行性判断 · 2026-11-03

本 judge 只读产品与相邻仓库，只编辑本报告。未操作 Creator、上传、模拟器或真机。结论：**现有网页不可原样打包；先做音频／完整猫探针有条件 GO，平台上线尚未获本 judge 验收。**

## 当前规则与冻结基线

来源是本次 Creator 获取的 Skill 1.8.0（本地`.codex/skills/minitool-zip-builder/SKILL.md`）及[官方在线能力文档](https://miniapp-sandbox.xiaohongshu.com/minitool/doc)（页面标注更新2026-10-30，本轮实时读取）。Skill 的 `references/js-api.md` 是2026-09-23快照，只作差异基线。没有把相邻项目旧口令或管理CLI当成当前授权。

相对冻结基线，在线明确新增的公开能力组：

| 组 | 新增入口 | 条件／本项目建议 |
| --- | --- | --- |
| AI文本 | `xhs.AI.createModel / generateText` | App内、非流式、appId内测加白；本轮不用 |
| 窗口 | `getWindowInfo` | 9.49+；优先用于安全区与原生顶部按钮避让 |
| 定位 | `getLocation` | 9.49+；本轮不用 |
| 振动 | `vibrateShort / vibrateLong` | 9.50+；仅可选增强，不当发声成功证明 |
| 陀螺仪 | `startGyroscope / stopGyroscope / onGyroscopeChange / offGyroscopeChange` | 9.50+；本轮不用 |
| 关注 | `followAuthor / getFollowStatus` | 9.51+；本轮不扩展引导 |
| 云存储 | `addCloudStorage / updateCloudStorage / queryCloudStorage / removeCloudStorage` | 9.51+内测；不作为草稿唯一依赖 |
| 排行榜 | `submitScore / getRankList / getMyRank` | 9.51+内测，涉及上传资料授权；本轮不用 |

已有能力更新：相册保存现明确最低9.42+，冻结基线未标。Storage、文件系统、评论区、发笔记原来已有，不能重新包装为新增能力。`postNote`成功仍不等于最终审核通过。

当前在线规则禁止网络请求、网页下载、原生全屏与外跳；文件选择不能导入JSON。需Chrome61／ES2017基线。音频`AudioContext`／`decodeAudioData`没有明确能力承诺；可用与否应标未知。Skill另外明确音视频元素不能使用`data:`／`blob:`源，而包扩展名表没有MP3／MP4；不能借此保证任意媒体文件可上传。完整约束以原文为准，不将静态审计当运行验证。

## 现有代码的具体差距

1. `public/sampled-audio.js`以fetch读取音色manifest与MP3，再解码。`public/full-frame-character.js`也fetch图像manifest和Blob。即使URL相对、资源已在包内，现有调用路径仍不能照搬。`site-counter.js`和`family-referrals.js`的服务端请求须从小工具入口排除；端内不支持直接互跳，不复用网页跨产品链路。
2. 网页当前JSON／媒体导出依赖`a.download`，JSON导入依赖文件选择。小工具应保留事件数据／本地回放，改平台Storage保存及Canvas图片→平台相册／笔记路径；不把网页下载按钮做成可点却无结果。视频生成与原生写文件／发布需另证，不能只因普通浏览器有MediaRecorder就承诺。
3. 当前全屏会调用`requestFullscreen`，只能保留CSS演奏展开。样式用了`:has()`、flex gap、`env()`、`min/max/clamp`等；应提供确实覆盖当前UI的Chrome61基础布局，尤其安全区和停止/退出。JS转译不自动补`.at`、`flatMap`、`Object.fromEntries`、`Promise.finally`等内建API。
4. 整图资产原始目录：钢琴8,152,033字节、吉他/鼓10,185,900字节、吉他拨弦10,729,874字节；采样总目录1,147,089字节。不能复制整个`public/`（还包括历史实验）。图片可按真实展示尺寸等比例编码，但每张仍须完整猫/双爪/乐器；不能为减包改成分离四肢。

## 最小验证与可复用路径

最便宜探针：一次真实C4输入，原始`piano-kw/C4.mp3`32,032字节，完整idle/KeyA参考图各约150KB。图片若内嵌应先按显示尺寸编码并记录变换来源；音频可作为小型字节数据候选，`atob → ArrayBuffer → decodeAudioData`不使用`audio.src=data:`，但这只是**待模拟器证伪的方案**，不代表平台已声明支持。音色失败不能静默换合成器后仍称原采样版通过。

探针成功后复用：

- 原仓库`bindings.js`、曲谱索引、真人事件录音schema、共享音频时钟；保持录制只写人输入。采样应复用已核验CC0钢琴来源和校准逻辑，不重做音色。
- 相邻MiaoTI/Tarot的独立入口、显式资源清单、Chrome61 IIFE、包外来源/哈希审计、官方目录+ZIP审计流程。不要把它们整个框架或业务数据搬来。
- 相邻Tarot的版本检测、串行Storage、`:ok`响应校验、原生安全区、图片临时文件与相册/笔记桥接；移植须保留其MIT通知。标准网页未注入SDK时明确禁用原生按钮，不能调用替身后声称真实保存。
- 当前Skill性能预算：ZIP≤10MiB，建议≤2MiB；单项内嵌解码数据>100KiB需检查，>1MiB不得内嵌。文本大于建议预算须据实解释，不改扩展名或压缩字符串掩盖运行成本。大场景不能只写`is_high_consumption_scene:false`便视为合规。

## 停止条件与验收边界

P0停止：官方模拟器里AudioContext被拦、解码失败或真实输入无声；猫/双爪/乐器不完整；包内仍有禁用请求/下载/外跳；页面本地看似成功但官方模拟器失败。先保存失败证据，不继续扩大乐器和动画范围。

继续条件：当前包通过官方静态审计，并在官方模拟器证明点击→音频解码/调度→完整图响应，返回后台/取消不会继续播放；再做曲谱/录制/恢复与平台图片分享。三层证据分开记录：普通浏览器开发检查、官方模拟器、Android和iOS真机；没有最后两端验收不声称端内全流程已完成。上传、发布状态与普通用户从笔记挂载进入试玩也分开验收。

本报告不证明当前客户端真实发声、视频导出、保存相册、笔记最终发布或审查完成；这些由主代理在实际候选与平台链路后追加证据。

## 官方模拟器超时 · 一次有界只读诊断

主代理反馈：音频probe上传到创建表单后显示部署成功，但官方预览为空，宿主console报告30秒remote simulator超时；未发布。针对页面实际引用的版本，仅做一次HTTP／源码检查，没有操作表单、重新上传、改动浏览器保护设置或执行第三方下载代码。

| 实际引用资源 | 结果 | 边界 |
| --- | --- | --- |
| `/simulator/releases/v0.2.2-9d88c5546499-0b9c738464e0` | HTTP200，875字节 | HTML壳可读，不等于模拟器启动 |
| CDN `runtime.9d88c.js` | HTTP200，889,311字节 | SHA-256为`9d88c5546499eee61fea8cd987795555c0346e0c6864474e99881cd962ba0529`，与版本指纹一致 |
| 版本内`sw.js`及其引用的CDN `sw.0b9c7.js` | 均HTTP200 | 不能据此推断浏览器允许ServiceWorker注册／控制 |
| 版本内`request-manager` | HTTP200，335字节 | 仅证明壳资源可读 |

CDN脚本响应提供跨源允许头。未发现“服务整体不可达／版本JS文件404”的证据。HTML配置中的`/simulator/csp`独立GET为404，但当前runtime源码没有消费该配置字段；不能把这条旧配置直接宣判为根因，也没有继续尝试变体URL。

读取公开runtime源码可见：它等待宿主消息／MessagePort初始化，获取运行配置（POST、15秒超时后可降级），再初始化`iframe-service-worker`渲染器并回传ready。故宿主30秒超时可能涉及握手、浏览器跨站ServiceWorker环境或策略阻断；HTTP检查无法区分这些原因。探针音频脚本尚未获得执行证据，**不能据此断言AudioContext不支持，也不能称音频链通过**。

有意义的下一步按成本排序：

1. 在现有官方预览上做一次浏览器console／网络失败reason观察，区分runtime脚本、ServiceWorker注册和host握手；不禁用安全机制。若同一故障重复且没有新证据，停止重载／重传。
2. 在独立标签只读打开已有MiaoTI的官方预览作同宿主对照；成功只说明宿主不是普遍失效，失败则支持平台／浏览器环境问题。均不把另一项目成功替代本probe验收。
3. 使用**同一上传probe的官方真机预览**：已授权设备镜像能连接时读取实际点击和可见状态，或由用户扫码。记录端侧AudioContext状态、解码时长、音频时钟／非零分析值与图响应，并单独确认扬声器声音；设备/SDK状态不可伪造。

直接在普通Chrome打开probe、单独打开runtime URL、注入本地SDK替身，均不能替代该平台门槛。当前维持“缺少平台核心运行证据”的P0停止条件，暂不展开完整小工具实现或发布。

## 网页手机改动 · 独立技术复评

复评范围是当前`public/media-sharing.js`、app接入、`keyboard-navigation.js`与按键输入路径。本节是普通网页代码／受控DOM检查，不能覆盖前述平台P0。**本轮网页新增改动未发现P0/P1，可进入主代理的真实浏览器／生产验收。**

- 分享文件在编码完成时预构造；点击事件进入`share()`后，在第一个await之前直接调用`navigator.share`，没有先做异步编码／转Blob等会丢激活的操作。`canShare({files})`是构造阶段的能力探测；不支持／抛错时隐藏分享按钮并保留原下载说明。成功文案只说交给系统并要求目标应用确认，没有冒称发布笔记。
- pending标志在原生调用前设置，两类分享按钮同时禁用，重复点击不会创建第二个分享请求。取消和非取消异常均通过finally解锁，File保留可重试。app的mediaBusy在准备／编码期间阻止分享，随后refresh恢复可用状态。
- File由原Blob构造，MIME剥离`;codecs=...`参数，文件名沿用编码器实际扩展名。分享不依赖预览ObjectURL；新导出替换／撤销旧URL不会把已交给系统的旧File变成新文件。每类仅保留一项；失败导出不覆盖上次成功文件。原网页下载／预览仍保留。
- 音域条只调用scrollTo和导航更新，不调用hit／visual／recording；独立集成检查还把真实导航控制器接到app fixture，避免仅凭函数名认定没有录音副作用。琴键触摸立即发声与拖动音域条分开；真实触摸取消／多指行为仍需浏览器或设备检查。

独立执行结果：

1. `node --test scripts/media-sharing.test.mjs scripts/interaction.test.mjs`：42/42通过。
2. 额外受控分享检查：待处理时双击仅调用一次；两按钮锁定；结果替换后待分享File仍是旧名字／旧字节数，下次点击使用新File；MIME正确；同步NotAllowedError后可重试。
3. 额外app＋真实导航fixture：录制中音域条到50%（模拟scrollLeft=180）及高音按钮没有发声；随后只按一次A，导出JSON恰好1个真人事件。该检查没有改产品或仓库测试文件。

非阻塞建议：将第3项固化为导航／录音集成回归。目前正式interaction suite中`mountKeyboardNavigation`是stub，现有42项通过本身不能证明新音域条集成；上述额外检查已补当前候选证据。失败重试后保留旧成片是合理的数据保护，但以后可以明确提示“上次生成的文件仍可保存”，减小新旧结果误解。

未验证：真实手机系统分享面板、用户取消后各浏览器的原生Promise时序、目标应用是否接收具体MIME以及最终发布／保存结果。受控navigator替身只用于断言调用与状态机，不是平台SDK成功或系统分享成功凭据。平台小工具正式包仍维持暂停扩展。

## 平台探针恢复 · 有条件继续

主代理在新的官方创建表单加载**相同ZIP**后恢复预览，报告并保存了`artifacts/mobile-xhs-20261103/xhs-audio-probe.jpg`。本judge已实际查看该截图：Creator部署成功，模拟器内可见READY、running、44100Hz、decoded4.839秒；一次C4后clock增加0.250、peak57、image=true，完整猫/琴仍在。此前30秒超时作为历史保留，不再解释为持续平台失败。

这足以清除“官方模拟器核心声画完全无证据”的停止条件，允许推进有界钢琴候选。它不证明其他音符映射、并发/取消/恢复、相册/笔记、真机扬声器或普通用户入口。新候选仍须独立验证，不能把探针成功写成全部平台功能通过。

### 最小桥接与存储复用定位

- 相邻Tarot的`site/src/platform/xiaohongshu.ts`：`checkedCall`、`prepareImage`、`saveResultImage`、`openResultNoteComposer`可作为图片桥接基础；响应必须包含明确`:ok`，不把空对象视为完成。`postNote`只交给平台处理，用户仍可编辑、取消，最终状态以平台为准。
- `site/src/platform/minitoolStorage.ts`：`nativeStorage`、`serial`、`checkedNative`和闭合schema校验可复用。版本判断取`floor(buildVersion/1000)`；9.46起用原生Storage，读失败不当成空，不从旧浏览器数据强行恢复；写入确认后才清理旧副本。启动恢复不得迟到覆盖用户已经开始的新录制，需用顺序/版本或初始化禁用保护。
- 相邻MiaoTI的`minitool/bridge.js`提供现成ES2017组织方式，但其`checked`接受缺失errMsg的对象，弱于Tarot严格确认；新候选不应继承这一宽松语义。MiaoTI的3秒超时也不能不加区分地用于相册/发布确认，以免把仍待用户处理的原生操作宣判失败并鼓励重复提交。
- 两相邻项目的MIT通知须保留；Tarot LICENSE为`Copyright (c) 2026 farmcan`。小工具只需NOTICES.json中的许可文本与移植说明，不打入TS源码、测试、平台账号或私有诊断。

官方`getWindowInfo`条件再次核验为客户端9.49+（版本比较值9490），无业务参数；读同步启动版本，不存在再异步获取，检查方法并处理失败。返回坐标已经是容器逻辑像素，不能另加statusBarHeight。上方避让取有效safeArea.top及可见back/me/share的bottom最大值，下方取windowHeight-safeArea.bottom的非负值；按钮可为null，返回字段不合法时走CSS保守回退；窗口改变后再读最新值。相邻封装本身仅检查方法，移植时应补明确版本判断。

本节只读抽取与判断，没有改产品代码或操作其他仓库。后续将对实际候选审查闭环与授权边界。
