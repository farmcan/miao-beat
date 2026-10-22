# Miao Beat v2：动画与演奏引导

日期：2026-10-22（Asia/Shanghai）。范围：当前角色四组件与 SVG 道具、优秀作品的真实源码、轻量动画取舍、谱子/节拍引导。基于源码和文档的判断；本子任务没有完成外站通玩、实体手机帧率或音画延迟测量。父任务负责浏览器和发布验收。

## 建议

**继续当前原创毛绒猫四组件 2.5D rig，不为 v2 改成真 3D 或 GIF。** 最值得做的不是继续堆表情，而是让按键、接触、反弹与用户听到的一声对应；谱子提示应清楚回答“哪个键、几拍、当前哪里”，不变成追赶音符的游戏。

本轮发现并修复两个有明确源码依据的小问题：快速重触发不能先跳回固定起手姿态；运行中打开“减少动态效果”时，正在播放的 Web Animations 也要取消。除此之外不改变 PNG、道具、锚点、声音或谱子系统。是否需要更大动作和新姿态，待实际看完键盘/吉他/鼓三模式再定，不用数字位移幅度代替视觉验收。

## 1. 现有 rig 的能力与缺口

本轮读取 `public/character.js`、`public/character/rig.css`、`public/character/manifest.json` 和 `public/index.html` 中的道具结构。

- 一张 **1254×1254 RGBA atlas**（1,563,258 bytes），四个等尺寸 tile，分别是头、身体、左前爪、右前爪。用嵌套 SVG `viewBox` 裁切同一张图，四个 group 独立变换。共享一个图片资源不等于没有解码内存；仅按 RGBA 展开约 6MiB，浏览器合成开销需另测。
- 从后到前是身体→当前 SVG 乐器→左右爪→头。PNG 不含实际键盘/吉他，因此道具可独立显示；没有真实手指、瞳孔、关节、网格或皮肤绑定。头部微移是在表现关注，不应称“眼球准确追踪”。
- 身体以 1.2% 缩放呼吸；头部视线最大约 1.7 SVG 单位、0.85°，触屏不追指针；点头独立于视线 group。两爪各自 190ms WAAPI，当前 UI 的 `left-down/right-down` 为按住姿态；左右同时演奏不需要两套完整猫图。
- `ready` 等到图片和独立样式加载成功才隐藏旧 SVG 猫；失败时保留可用替代场景。无需为了动画把音频加载绑到猫图解码。
- 当前钢琴道具的琴面约在 y245，鼓面约在 y221，吉他为斜向琴颈/共鸣箱；**同一爪的同一运动不能证明三个道具都有精确接触**。吉他 CSS 有独立按住姿态，但 one-shot 仍是通用动作。这是后续需要实际对齐的美术/动作限制，不谎称已经做到真实拨弦或逐键弹奏。
- 源码检查时，旧 WAAPI 每次 cancel 后从固定 `translateY(-3px)` 起手，结束固定回 0，再交还 held CSS；重复敲击及按住状态切换存在位置跳变来源。CSS 的减少动态规则不等于会取消已创建的 WAAPI。

## 2. 三个实际源码参考，以及不能照搬的地方

以下为本轮实际读取源码，不是只看标题。维护日期为 GitHub `pushed_at`（UTC），不保证每项功能最近更新。

| 作品 / 原始来源 | 本轮看到的具体实现 | v2 应学什么 | 许可 / 维护 / 不能照搬 |
|---|---|---|---|
| [Bongo Cat](https://bongo.cat/) / [core.js](https://github.com/Externalizable/bongo.cat/blob/master/js/core.js) | `$.play` 将键位分到左/右爪，按下时播放声音并改变 sprite 的 background-position，松开恢复；`pressed` 防止同键重复触发。触屏通过乐器/点击层触发映射 | 极简、明确的“左手一下/右手一下”，乐器层切换后动作仍对应输入；简短键序可供参考，不先上教程 | [代码 MIT](https://github.com/Externalizable/bongo.cat/blob/master/LICENSE)，最后推送 2024-05-01，未归档。角色与声音来源独立核验，不能从代码 MIT 推断全部素材可自由重用。低延迟库、jQuery/Flash 历史兼容不适合照搬；本轮未重新实际试听原站 |
| [Patatap](https://patatap.com/) / [index.js](https://github.com/jonobr1/Patatap/blob/main/src/index.js) / [strike.js](https://github.com/jonobr1/Patatap/blob/main/src/animations/strike.js) | `trigger` 查动画状态，播放中先 clear，再 start；strike 将进入/退出 tween 分开。交互后隐藏 hint，20秒后允许提示再出现；有键盘、移动端触点格和 MIDI 映射 | 快速重复输入必须有明确打断策略；每次输入是短、可重叠的反馈。引导在需要时出现，开始演奏后退场，不拿巨型 banner 占演奏区 | README 写 MIT，package.json 写 ISC，许可标注冲突；声音亦需单独核权。最后推送 2026-01-29，未归档。本轮只研究机制，不移植代码/音源。其整屏触控禁止滚动适合抽象画布，**不适合本站还要横向浏览琴键、纵向到达记录区的页面** |
| [Chrome Music Lab — Melody Maker](https://musiclab.chromeexperiments.com/Melody-Maker/) / [Main.js](https://github.com/googlecreativelab/chrome-music-lab/blob/master/melodymaker/app/Main.js) / [Grid.js](https://github.com/googlecreativelab/chrome-music-lab/blob/master/melodymaker/app/grid/Grid.js) / [Sequencer.js](https://github.com/googlecreativelab/chrome-music-lab/blob/master/melodymaker/app/sound/Sequencer.js) | Sequence 用八分音符步进；callback 中 `grid.select(step)` 得当前列音符，再 `player.play(notes,time)`；Grid 维护 activeColumn，按 `_needsUpdate` 重绘当前列/音块。Transport 停止时清掉选中列；移动设备显式解锁 AudioContext | 时间位置是单独、可读的状态；停止就清状态。播放位置、真正发声的音符、用户自由输入要能区分。没有必要依赖大幅角色运动解释每个时值 | [仓库 Apache-2.0](https://github.com/googlecreativelab/chrome-music-lab/blob/master/LICENSE)，2026-04-19 已归档，属于历史 AMD/Tone/webpack 栈。本轮不复制旧框架。原代码在音频预调度 callback 即选列，不应原样当成今天音画时刻严格同步的证明；本站仍应按音频时钟到点再画 |

另看 [Chrome Music Lab Rhythm](https://musiclab.chromeexperiments.com/Rhythm/) 和 [Incredibox Demo](https://www.incredibox.com/demo/) 的官方入口作角色表演参考。但抓取 Rhythm 返回兼容提示，Incredibox 主页面是嵌入 Demo；本轮没有由此声称通玩、取得角色帧或验证手机。CML 总仓库没有 Rhythm 目录，不能用其 Apache 许可证覆盖 Rhythm 角色和音频；Incredibox 是保留权利的商业作品，不是素材包。

三个精选分别解决输入因果、重复触发、音乐位置。它们不是同一个产品模板，也不支持“换一个库就能拥有这些体验”的结论。

## 3. 本轮实现：连续姿态与实时减少动态

仅改 `public/character.js`；`rig.css` 无需修改。原 atlas、裁切、锚点、道具层级和控制器 API 保持既有实现。

1. 每次 strike 在取消该爪的上一动画前，读其当前显示的 transform，新动作从此处衔接；保留短起手→接触→恢复，190ms、`fill:none`，另一爪不受影响。避免旧动画中途被重新按下时硬回固定初始位置。
2. 最后一个关键帧只指定 `offset:1`，不写死 transform，让浏览器使用实时 CSS 底层姿态。这样按住、松开或切乐器发生在动画中途时，不会在结束时恢复到触发瞬间捕获的旧按住姿态。该行为依据 [W3C Web Animations §5.3.4](https://www.w3.org/TR/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect)：缺少某属性的终点时，组合使用该属性底层值；不是用 `commitStyles` 将动画结果写死成内联样式。
3. 监听 `prefers-reduced-motion` 的运行中 change：取消左右爪正在播放的 WAAPI、取消待执行视线帧并回中；destroy 解除监听。CSS 继续负责停止呼吸/点头和禁用头部跟随。参考 [MDN 减少动态说明](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) 与 [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API/Using_the_Web_Animations_API)。

没有改变音频何时触发，不延迟声音等待起手动画。动作变得连续不等于已证明“更像真实演奏”；接触阶段与听到的起音是否一致，仍需本轮浏览器观察/录屏。

静态/离线验证：`node --check` 通过；在 jsdom 中实际导入 character 模块，用假的图片加载与 Animation 实例检查等待资源、重复触发从当前姿态开始、终点不锁旧 CSS、另一爪不取消、动态减少运动时两爪取消、destroy 清理。这些是行为回归，**不代替原生 WAAPI 的插值/绘制验证**。

## 4. 技术取舍

| 路线 | 对本站最关键的能力 | 新成本与限制 | v2 决定 |
|---|---|---|---|
| 当前四层 2.5D + SVG 道具 + WAAPI | 左右手独立、看向与点头并行、可立即打断，固定机位能保留毛绒质感 | 旋转不能过大；肩/腕/耳机遮挡靠原画重叠；不能从一张头图生成真实眼球或新视角。每次重触发读取一次 computed transform，实际主线程成本要看设备 | **继续。** 当前瓶颈是接触与姿态，不是引擎；先把这四层用好 |
| 真 3D（如 Three.js） | 大角度视线、机位变化、真实关节和遮挡、动态灯光 | 需要网格/拓扑/骨骼/材质，不是将 PNG 放平面就变成真 3D；毛发和灯光、首包、低端手机耗电、失去 WebGL 上下文都增加验收范围 | v2 不引入。只有自由转身/镜头和精确跨道具手部姿态成为已验证核心需求，再做一个小样 |
| GIF / 整段预渲染视频 | 快速展示一次漂亮动作或分享预览 | 难以独立组合左右手/看向/按住/松开；浏览器 img 没有可靠任意帧控制；连续击键重启或串行等待会破坏因果。视频能 seek 也不等于动作任意拼接 | 不做演奏反馈。可用于介绍/分享封面，不用来替换正在演奏的猫 |
| 有限状态 sprite | 触底、闭眼、嘴形等形变可由真实帧表达 | 需同机位、位置校准和多个状态资产；组合状态过多会膨胀。现有 atlas 是组件包，不是动作 sprite | 只有现有刚性变换明显不够时，先补 2–3 个局部形变，不先生成一整套完整猫动作 |

## 5. 引导：多几首谱子，少一点认知负担

这部分给父任务接线参考，本子任务不修改 app、scores 或界面样式。

- **第一次：** 一个显眼的开声入口；开声后直接点/按一个键，猫回应。只提示当前设备动作（电脑字母键 / 手机点琴键），不先弹出音阶、拍号、录制、导出四层教程。
- **自由演奏：** 当前音名/按键即时显示，节拍器第 1 拍与其余拍有区别；文字讲清 BPM 是速度，4/4 的四个点是一小节四拍。不要把“一次键盘触发”强行等同“一拍”。
- **参考册：** 每个音显示简谱 + kbd + 时值，短句分组、有小节边界/休止；试听时当前音高亮并同步拍位置，停止/换曲清掉。示范速度和用户当前节拍设置的关系需明确，不能看着96BPM而试听实际120。
- **两种高亮有不同含义：** 实际按键的高亮表示“你按了”，谱子播放游标表示“示范到这里”。若同时出现，不能让用户误以为自己被判对/判错。谱子只参考/试听，不让猫替用户强制跟弹或给连击分。
- **手机：** 先露出能点的大键和横向滑动线索；参考册可折叠。长说明留在折叠区，退出沉浸、音量、选乐器、录制必须仍能到达。滚动提示要与真实 touch-action/取消行为匹配，不写假操作。
- **记录/分享：** 记下→回放→保存音画/可重建文件是一个闭环。只有完成第一段后，才提示“留住这段”；不要一进来强调导出格式或工具实现。键盘事件 JSON 是可重放数据，不等于社交平台能直接播放的作品。

## 6. 浏览器验收与停止条件

父任务可在发布前做以下有限检查，不需要再扩大功能：

| 情况 | 必须看到的结果 | 未通过时如何收缩 |
|---|---|---|
| 单次短按、按住后松开 | 爪动与一声对应；释放后不悬在错误位置；不叠出第二只手 | 回退该动作关键帧调整，保留独立四层 |
| 同侧 80–120ms 间隔快敲、左右交替/同时 | 前一动作可被同爪打断，但不跳回固定画面；另一爪继续自己的动作 | 缩短幅度/时长，保持双手独立，不排队播完动画 |
| 动画中松手/切乐器/失焦 | 当前按住状态被正确释放；终点跟随当前 CSS，不留旧姿态 | 优先修状态清理，不用新素材掩盖 |
| 系统减少动态在打开前/演奏中启用 | 停止呼吸、点头、爪动画、视线跟随；按键/声音和必要状态仍可用 | 不可只改 CSS 动画时长而保留 WAAPI |
| 钢琴/吉他/架子鼓 | 道具不穿帮、爪根不露缝；触点可理解 | 不准确时把描述收敛为“猫跟着你打拍”，不要宣称真实按指板/逐键落指 |
| 390×844、844×390 Chromium 响应式页 | 大键/退出/参考册可达，舞台不遮演奏 | 先收小舞台，不缩回触控键；这仍不是实体手机验收 |
| 实体 iPhone/Android（仍待验证） | 快敲没有音频中断、长任务/明显掉帧，触屏不持续追视线，滚动后能恢复输入 | 暂停无输入时呼吸/减少装饰，必要时退回静态角色+按键反馈，不先换 WebGL |

可设置一次15秒相同音符输入的旧/新动作对照录屏，比较接触、连续性和声音时刻；不把动画时长190ms误当输入延迟190ms，也不因 CSS transform 通常较便宜就宣称恒定60fps。若用户看不出提升或觉得猫更漂浮，优先回退帧调整，保留减少动态的正确清理；不以继续叠特效作为默认修复。

## 交付边界

已改：角色重触发/终点与动态偏好处理；manifest 中该 JS 文件大小与 SHA；本研究。未改：PNG、rig.css、主页面/app/style、谱子/声音、导出器、依赖与构建入口。主任务仍需检查真实浏览器动画、CSP、响应式页面和最终生产内容；本报告未宣称已上线或已通过实体设备验收。
