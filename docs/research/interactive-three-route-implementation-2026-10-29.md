# 可操作三路线对比：2026-10-29

本轮交付是可操作技术对比，不是角色美术验收。原图仍是 `public/character/instrument-scenes-v1/guitar/idle.jpg`；冻结 C20 只解决局部眼睛静态问题，爪形、毛发、原图相似度及动作仍有未通过项。

## 实现边界与复用

| 路线 | 实际渲染 | 最少复用 | 本轮不能声称 |
| --- | --- | --- | --- |
| 原版 | 浏览器整帧图像播放器 | `full-frame-character.js` | 真正三维或手指物理模拟 |
| Blender 派生 3D | Blender 创作的 GLB，由浏览器 WebGL 渲染 | 冻结 C20 完整场景，研究 LOD + 五个形变目标 | Blender 在浏览器运行、角色精修通过 |
| Godot Web | Godot WebAssembly/WebGL 引擎导入同一 GLB | 同一资产、同一形变权重和节拍事件 | 不同模型质量、更高画质、物理正确 |

比较必须实际按键出声、拨弦爪移动、按弦爪换位置。相同图片旋转不能代替三维路线。建议宿主页拥有唯一音频时钟、输入去重、录制事件和回放调度；三种 renderer 接收相同事件和 `[Pluck, FretLow, FretHigh, HeadTilt, Lift]` 权重。单击一次只触发一次 stroke；快速输入不得排出延迟动作队列。

`app.js` 本身 import 并调用 `loadSiteCounter()`，删 index 中 script 不足以免计数。`site-counter.js` 在找不到 `siteVisitCount` 元素时立即返回，因此专用 embed 去掉该节点即可不请求 counter；`analytics=internal` 仍是 GET，不能叫零请求。原版 document 键盘监听与 iframe 焦点会冲突，专用 renderer adapter 比完整应用嵌套更清楚。

旧 `public/labs/blender-guitar/` 是真实 Blender 整帧图集的 Canvas2D 播放器，可诚实保留为“旧技术对照”。它支持按键、慢放、快速触发测试、录制及媒体导出，但全音符复用右爪一段 clip，左爪不换品位；是已被拒绝的粗模，不应放进“精修 3D”名下。旧 Godot `static-cat-diagnostic.gd` 仅导入、等待、截图退出，没有可交互琴键，不能等同可玩 Web 版。

## 已核验可交互参考

1. [Three.js RobotExpressive 在线例子](https://threejs.org/examples/webgl_animation_skinning_morph.html)；[源码](https://github.com/mrdoob/three.js/blob/83f6bd095356c68334df7d9b7ec03a0abebff3fc/examples/webgl_animation_skinning_morph.html)，固定 commit `83f6bd095356c68334df7d9b7ec03a0abebff3fc`。GLTFLoader、AnimationMixer、LoopOnce、fadeToAction 以及独立面部 morph。代码 MIT；[模型说明](https://github.com/mrdoob/three.js/blob/dev/examples/models/gltf/RobotExpressive/README.md) 标记机器人 CC0。实际浏览器已点 Wave，姿态变化可见；未作 FPS/移动端测试。可借鉴一次性动作与持续状态分离，不需引入整个框架。
2. [Miso 3D Cat 在线](https://echoscarrie-lab.github.io/miso-3d-cat/)；[仓库](https://github.com/echoscarrie-lab/miso-3d-cat)，固定 commit `48766764c9e5bdeed1419ae92d4d88a0842d09a2`。MIT，Three r128，原生动画循环和 Meow/Pounce/Feed/Milk/Spin 按钮。实际浏览器点 Pounce，蹲伏及身体位移可见。模型为程序几何，视觉远低于 Miao 原图；只能参考交互与待机动作，不建议直接换猫。

以上是实际网页点击验证，不代表所有代码功能或设备兼容已验收。公开站抓取失败时用浏览器核验，不把搜索摘要当实测。

## 最便宜的可证伪验收

1. 同一音符在三路触发一次声音、一次右爪 stroke，按弦爪沿琴颈换位，身体和吉他根不漂。
2. 按住键不重复触发，80/150ms 连按不积累尾部动作；松开后能回到静止。
3. 整猫、双爪、琴每帧在一起；不得拼接手臂贴图。GLB 本体连续表面局部形变是研究授权下的真实几何动画。
4. 同摄像机静态与动作起/中/末截图审阅；原图相似度、材质、动作接触分别 judge，P0 不可由运行成功抵消。
5. 现有 Canvas2D 导出成功不自动证明新 WebGL/Godot 录制成功；需要独立验证 canvas captureStream/readback 及音画同步。

研究 LOD、顶点颜色 bake 和 morph 为浏览器资产转换，不能称建模优化；原生毛发不进入 GLB，损失必须声明。零新增费用，本报告及本轮资产不部署。

## 本轮导出实测

`public/labs/character-compare/model/miao-playable.glb` 为冻结 C20 派生，7,483,568 bytes、258,726 tris。连续 body 73,129 vertices，20 个带形变的 mesh 均含同序五 target；琴根不含形变。body 局部 Pluck/Lift 9,541 点、FretLow/High 6,164 点、HeadTilt 10,595 点。Pluck 最大位移0.1406，换把最大位移0.105，头部约3度，Lift 离弦0.06；均为场景单位。

局部 body game-delivery 工程审计 errors0/parts1；4条多面共边及无UV为保留 warning。不能据此推导接触或精修通过。C20 眼球外盖仍为 OPAQUE，GLB 导出 clearcoatFactor1、clearcoatRoughness0.035、roughness0.14，未退回旧透明角膜。

实际 Blender 同镜头起/峰/末图在 `artifacts/interactive-compare/{start,contact,end}.png`，已打开看过。起末权重均为0，视觉回到静止（未宣称PNG文件逐字节相同）；峰值拨弦爪位移可见，脸/眼/胡须同步随头。文件名 contact 只表示动作峰值，不构成碰撞/弦接触通过证明。材质无原生毛发，明显更光滑；旧爪与整体相似度问题保留。详见公开 manifest 与本地审计。
