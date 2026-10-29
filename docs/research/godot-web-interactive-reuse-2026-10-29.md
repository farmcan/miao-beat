# Godot Web：真实可操作角色的复用路径

2026-10-29。本轮结论：Godot 能把角色实时放进普通网页；已实际跑通本项目模型的 Web 导出、20 个形变网格与父页面输入桥接。它不会自动修好模型、手指或接触关系。当前仍是技术对比样机，未达到角色美术生产门槛。

## 先看已存在的实现

以下均来自 [Godot 官方 Web Demo 目录](https://godotengine.github.io/godot-demo-projects/)，有真实导出入口，源代码已拉取至本机阅读。目录会跟随 master 自动更新；本次源代码固定于 `b761b4cd5718a7118f2c95eb55f181d0a5f004f1`。官方演示不是精致橘猫素材库。

| 示例 | 直接试玩 | 读到的实际实现 | 对 Miao 的价值与界限 |
|---|---|---|---|
| 3D Inverse Kinematics | [Web](https://godotengine.github.io/godot-demo-projects/3d/ik/) · [源码](https://github.com/godotengine/godot-demo-projects/tree/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/3d/ik) | `skeleton_ik_runner.gd` 启动 SkeletonIK3D；`target_from_mousepos.gd` 将鼠标射线映到目标；另有 SADE FABRIK 插件。 | 可借鉴琴弦接触目标和手臂链约束；不会生成合适手指拓扑、毛发和猫的神态。原工程 README 标 Forward+；官方 Web 目录采用 Compatibility 适配，不可把桌面观感照搬。 |
| MIDI Piano | [Web](https://godotengine.github.io/godot-demo-projects/audio/midi_piano/) · [源码](https://github.com/godotengine/godot-demo-projects/tree/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/audio/midi_piano) | `piano.gd` 把21–108音高映射到键；`PianoKey.activate/deactivate` 分开处理按下与释放；音频从 A440 样本变调。 | 适合复用逐键状态与发音组织。没有动物动作。上游称支持外接MIDI，本轮未实测设备或浏览器MIDI权限。 |
| Rhythm Game | [Web](https://godotengine.github.io/godot-demo-projects/audio/rhythm_game/) · [源码](https://github.com/godotengine/godot-demo-projects/tree/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/audio/rhythm_game) | `conductor.gd` 读取播放位置、混音时间与输出延迟；`one_euro_filter.gd` 平滑时间抖动；单独的 metronome 依照歌曲时钟。 | 可借鉴节拍/画面统一时间源。Miao 三栏采用父页同一份 Web Audio 与同一权重流，因此不再额外启动 Godot 音频时钟。 |

证据边界：这三个官方地址已通过网页工具打开，真实 canvas 导出存在；代码已在本机阅读。本轮未逐一完成人工键鼠试玩、听音或移动设备验收。不要把目录可访问等同全部玩法已测。

许可证：官方 Demo 仓库的代码是 MIT，原版权声明须保留。根 README 链接 MIT 声明；素材仍须逐项核验，不能把代码许可自动套给全部模型/音频。Rhythm Game README 明确标节拍器录音为 Ludwig Peter Müller、CC0。当前 Miao 导出没有装入上述 Demo 的模型、音频或代码，仅参考其组织方式。

## 已做的最小真实路径

1. 已有本机 Godot `4.7.2.stable.official.ed1daf0bf`，此前没有 Web 模板。旧 `design/godot-character-lab` 是 C8 静态截图诊断场景，不是可玩网页。
2. 从 [官方4.7.2发布](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable)免费获取 `web_nothreads_release.zip`。只经 HTTPS Range 取需要的官方成员，核成员长度、ZIP CRC 和本地 SHA256；**没有**声称完整1.28GB TPZ已做官方SHA512全包验证。本地receipt保留此缺口。
3. `design/godot-web-compare/` 导入同一份 C20 LOD GLB，和 Three 栏共用角色；通过真正 `MeshInstance3D.set_blend_shape_value` 设置五种形变。实际负数读回为 `-0.5`，不会吞掉反向扫弦权重。
4. 导出真正单线程 Compatibility Web：`index.js` + `index.pck` + 官方 WASM。未使用 Three.js 冒称 Godot。父页面给 `miaoGodotPose(p,low,high,head,lift)`、view/orbit；Godot 不自发重复扫弦，也不播放第二份音乐。
5. 官方引擎 raw WASM 是39,514,754字节，超出当前 Pages 25MiB单文件门槛。精确 gzip 后10,054,758字节，浏览器限定作用域解压成原始 WASM；PCK14,774,840字节附近，具体以最新 `export-evidence.json` 为准。没有改 Worker、跨站隔离或 D1。

[官方 Web 导出说明](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)确认浏览器使用 WebAssembly/WebGL2、Compatibility；单线程可避免多线程所需隔离头。此选择保留普通 iframe 嵌入。程序化音频等模式有差别，所以本轮保留父页已验证的 Web Audio。

## 本轮实际验收

- `public/labs/character-compare/godot/` 被真实 IAB WebGL2 canvas 加载，画面是完整猫、双手、吉他；不是截图位移。
- console：Godot4.7.2、Emscripten4.0.20、single-threaded、Compatibility；ready包含 `web:true`、20 morph meshes、负数API读回 `-0.5`；无 Godot warning/error。
- 在真正三栏页点击“慢速演示”，父页计数增长到8；点击“双手”，Godot相机确实切换。停止按钮恢复静止。双手相机按独立judge反馈改为 target=(.3,1.7,1)、zoom=1.25；重导出、重载后左右爪都完整入框。该技术验收不代替动作自然度judge。
- 当前角色无导出的毛发，面部与接触仍不精致；环境光与 coat 只作 Compatibility 近似，接触阴影未调好，不能把引擎跑通写成美术交付通过。

复现说明：[Godot Web工程README](../../design/godot-web-compare/README.md)。最新产物大小与hash：[导出证据](../../public/labs/character-compare/godot/export-evidence.json)。源 GLB SHA256 `1a384c0a9a13ed60710469b7d9a4de646a8599fe3dcff5ef85d1f42c825cedf9`。发布和线上验收由主任务进行；此子任务没有部署或新增费用。

## 发布前 CSP 修复

Godot默认shell有inline CSS/启动JS，现已抽取为同源 `godot-page.css` 与 `godot-start.js`；`index.html` 没有inline script/style/event handler。ready桥从普通 `JavaScriptBridge.eval` 改为直接对象调用。重新真实导出后PCK为14,774,984字节，SHA256 `dccb15900900b55021f3a1c312ddc95120524152c840a3b565a6dc11ab979afa`。此变更后的严格CSP浏览器验收由主任务继续，本子线程复测时IAB不可用；不把无CSP旧验收当作严格CSP通过。

## 下一步最便宜的验证

先用同一输入在三栏检查：单次按下只一次动作，150ms连按仍看得见手部往返，左手按弦位置与音符组一致，停止无残留排队，转角后仍是立体模型。视觉不过时继续改美术/接触，不用更换引擎掩盖问题。

若采用骨骼下一步优先只做两个可测的接触目标：右爪琴弦穿越段、左爪固定琴颈握点；再加入柔和头部跟随。完整五指IK、毛发系统、自动随机动作和新框架不在这个最小可证伪闭环里。
