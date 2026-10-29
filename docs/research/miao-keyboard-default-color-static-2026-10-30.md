# KeyForty 同pose默认色静态 · 待三方shaded gate

2026-10-30。三位非builder已在原灰报告追加确认gray-supported GO；root授权同pose默认色。**已输出8张真实原生默认色图与独立3.6 native，逐张实际查看，保存重开验证PASS；等待三方彩色静态评审，未自称最终通过。**

![完整默认色front](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/default-color/front.png)

![完整默认色3Q](/Users/levi/wrksp/miao-beat/artifacts/miao-reuse-keyboard-v1/default-color/three-quarter.png)

其余 `face.png`、`left-hand.png`、`right-hand.png`、`hands-top.png`、`feet-support.png`、`support-side.png` 与上述两图均在 **`artifacts/miao-reuse-keyboard-v1/default-color/`**。front/3Q保持完整猫、双臂双手与全键盘同一原生帧；side裁尾仍仅为承托诊断，不用于完整生产帧。8图与native / receipt逐项SHA见 `inspection-manifest.json`、`SHA256SUMS`。

唯一外观改变：**旁路Blender compositor的RGBToBW**，直接把原RenderLayers Image接Composite。原Cat灰毛、蓝服、青眼、粉鼻、红护目镜 / 袖口，以及KeyForty深灰壳、象牙白键、黑键与桌子橡木 / 石墨PBR全部保留。不调色、不美化、不改变光位 / 地面 / 接触阴影、不应用default/smile close/smile open pose库。源表情与身份差距仍由三方实际图像评审，不写成已恢复原橘猫身份。

| 固定项 | 核验 |
|---|---|
| pose SHA | `4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be`，所有相机render前后相同 |
| 全部mesh坐标 / 拓扑 / material slots | hash前后相同 |
| 原材质node / link graph | hash前后相同 |
| 琴、桌、ground world矩阵 | 前后完全相同 |
| 质量 | Quality1，render_levels2，use_simplify=False，保留灰门槛恢复后的原生渲染设置 |
| camera helper | 8视图逐render显式同步，max error均0 |
| actions / keyframes | 原27actions保留，新增0；无新keyframes、无press/head动作 |

独立native **`keyboard-default-color-native36.blend`**，SHA **`3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b`**。来源supported native SHA `31c427e53b47eb55251d0f25f9157545d0f81558183822837945c848085a1b9e` 前后不变。`native-reopen-verification.json` 在factory-startup / disable-autoexec实际重开，pose / mesh-slot hash / 直接彩色Composite链接 / Quality与render设置均PASS。所有Blender顺序单进程，现均结束。

静态皮肤 / 有限碰撞证据沿相同geometry与pose的 `support-prop/render2-matched-proxy-fit.json`：目标白键约2.905mm、最近邻投影约3.678mm；这是独立render-matched proxy，直接RENDER depsgraph捕获缺口未被补上。本轮没有因默认色另跑姿态或改造接触，不把悬停写成按下，也不宣称八键动态安全。最近邻相对目标投影余量仅约.765mm，未来不能整手下沉冒充单键。

权利分项沿 `licenses/`：Cat Blender Foundation / MoveAI优化版CC BY4.0；Innerscene KeyForty与桌完整文件模型 / 材料 / 图像CC0；新脚本 / 环境MIT。原包不可覆盖，全部source credit与modification notice保留；没有从MIT反推模型许可。新增脚本仅 `design/miao-reuse-keyboard-v1/render_default_color.py` 和 `verify_default_color.py`。

下一步交三位非builder实际比较原 `public/character/whole-piano-v3/idle.jpg`、当前完整front/3Q、脸 / 双手 / 支撑图后判断；P0不能平均。当前不做表情库选择、press/release、头眼动作、八键扩展、浏览器 / 手机、公开发布；未改guitar scene / public。

## 后续独立门槛结果

三方已分别实际看原参考与本次8图，`miao-keyboard-color-identity-judge-2026-10-30.md`、`miao-keyboard-color-craft-judge-2026-10-30.md`、`miao-keyboard-color-motion-judge-2026-10-30.md` 均为 **GO，仅允许一指一键受控试验**。原生静态未发现新P0；青色大眼/紧张神态、短绒风格差距与完整图键区偏小仍P1。静态门槛不等于最终艺术/八键/动作/网页通过；root据此授权独立单键副本。先前“待三评”是当时交接状态，历史不覆盖。
