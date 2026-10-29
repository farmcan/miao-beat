# 三路弹奏对比工程复核 · 2026-10-29

审阅对象：`http://127.0.0.1:8904/labs/character-compare/`，本机 Chrome，独立标签页实际点击、物理按键与 DOM 状态读回，同时核对宿主页与 Godot 源码。本审阅者构建了 GLB 与 motion-controller，**只做行为工程检查，不给美术、可爱程度、动作自然度或生产标准通过结论**。浏览器截图已实际查看三栏真实渲染；不是截图移动冒充引擎运行。

## 结果

本次测试未发现一次点击变成多次声音触发事件、150ms 连按积累补演、停止后残留演示输入或 iframe 吞键。两个实时引擎共用同一五权重轨迹；原版保留自己的整帧播放器，不能把三个版本说成相同动画。

| 实际操作 | 读回结果 | 工程结论 |
| --- | --- | --- |
| 打开声音 | 显示“声音已打开”，原版 motion ready、Three ready、Godot ready；Godot iframe 内 `data-miao-morph-meshes=20` | 三路资产确实加载，不是未接通占位 |
| 只点击 C4/A 一次 | 总输入1；原版 strike/contact/lift 各1；Three inputs1；Godot ready；动作结束 Pluck/Lift 为0，FretLow 为1 | 一次输入对应一次原版拨弦，没有额外触发 |
| 150ms 快速演示八音 | 总输入1→9；原版 strike/contact/lift 各9，Three inputs9。进行中读到三维/Godot `[-.679,.731,0,.169,.663]`；结束右爪/抬爪归0，FretHigh1 | 八次输入均进入公共轨迹，结束无旧动作队列 |
| 点击 Godot 画面，再物理按 A | 输入9→10，原版三个计数均10 | 不会因点 iframe 画面后丢键；CSS 对 iframe 禁用了 pointer events，父页面保有输入 |
| 开始快演示后立即停止 | 只来得及产生一次输入，总数10→11；停止后仍11，后续未增长；原版 serial0、phase ready、confirmedKeys 空，三维 Pluck/Fret/Lift0 | 剩余七个演示 timer 已取消，没有补演 |
| 停止后关闭“3D头部微动作” | 总数仍11；宿主、Three、Godot pose 均 `0,0,0,0,0` | 头部开关生效；停止后没有隐藏演奏事件 |

停止时原版画面 `wholeFrame=guitar-up:KeyA`，而三维回中立权重，这是既有播放器的抬爪 ready 姿态：`guitar-motion.js reset()` 会置 active=false、serial0，默认选择 KeyA。不能把画面保持抬爪误报为未停止或仍在循环。停止前后 strike/contact/lift 数未继续增加，支持此判断。头部开关打开时停止后可有独立轻微待机动作，这也不是补演。

## 源码与计时核对

- 宿主页唯一 `new SampledAudio()`，每次通过 `play()` 的输入只调用一次 `audio.play()`；原版 `strike()` 与公共 `motion.strike()` 在同一个分发函数内执行。没有给 Three/Godot 各开音频引擎。
- Pointerdown 负责鼠标/触摸输入；`click` 只处理 `detail===0` 的键盘/无障碍点击，避免普通点击双触发。键盘过滤 repeat、held、修饰键、输入框与组合输入。
- Stop 清 timer、held、音频 voices，调用原版 reset、motion reset，并立即给两个引擎送零权重。blur/hidden 同样停止。原版的抬爪 rest 保留，如上说明。
- 宿主页 RAF 计算唯一 pose；Three 当帧应用，Godot 最快每24ms发送一次。Godot `_js_pose()` 直接将五值写入20个 mesh 的 blend shape；无 Godot 自己的 stroke 时钟或事件队列。负 Pluck 不会被截成0。
- Godot ready 消息验证 origin 和 iframe source；同源直接 bridge 调用。iframe 显示 ready 来自引擎 `_ready()` 完成后的回报，不只是宿主猜测。
- 公共 controller 的10项输出行为测试通过：单按、无迟到补演、500/150/80ms连按、输入当帧连续、抬爪中插入新输入、平滑且不同换把、头部快音不重置、reset、有限范围、非法参数。这些是代码验证；浏览器本轮实际跑的是150ms演示，不冒充完成80ms真浏览器硬件压力测量。

## 保留边界与小问题

1. Godot iframe 上宿主 `data-pose` 是发送值，**不是引擎逐帧应用 ACK**。引擎20mesh实际就绪、源码直接 setter、画面可见支持通路成立；尚未记录每次 setter 后的引擎读回或丢帧统计。弱设备上的峰值捕获率和端到端延迟未量化。
2. Godot最多约41.7Hz权重更新，Three跟随宿主RAF；两者 pose 可有约一帧差。短 attack 会被采样，不能声称严格每帧同步或三路完全同姿态。
3. Chrome console 发现一条警告：`PCFSoftShadowMap has been removed. Using PCFShadowMap instead.` 未见本轮错误；当前上游会降级，建议直接使用 PCFShadowMap 消除噪声。
4. 代码证明声音只分发一次，本轮未通过扬声器录音或音频采集核对实际声学输出，也未验证新三维路线的视频导出、触屏多指与移动端性能。
5. 原版与三维的 rest、爪动作、手位策略不同；GLB 未通过原图精致度与真实演奏接触验收，工程闭环不能抵消这些差距。

本轮不修改生产资产或应用代码，不部署、不产生费用。后续美术与动作 judge 应由非 builder 独立审阅真实页面/录屏，对照原图分别列 P0。
