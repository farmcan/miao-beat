# Godot实时动作：可复用组件与Blender对照方案

2026-10-28。**结论：值得验证Godot作为实时动作控制／组合层；它不会自动修复角色、掌趾、蒙皮或闭眼结构。** 先保持同一Miao资产、相机、输入事件和接触标准，再比较Godot与Blender。当前完成的是官方与上游实际源码核查，未由本评审人安装插件、构建资产、运行这些demo或验证Godot/Web性能。新增现金／超额预算为0，只选本机及免费公开源码，不装未知MCP、不调用付费模型／算力。

## 固定版本与真实来源

- 官方最新release API本次返回 [Godot 4.7.2-stable](https://github.com/godotengine/godot/releases/tag/4.7.2-stable)，2026-08-18，tag commit `ed1daf0bf001b61586d9930840f2f1394092c079`。本次源码检查固定这个tag，不能用未来变化的stable文档替实际安装版本。
- 官方 [godot-demo-projects](https://github.com/godotengine/godot-demo-projects/tree/b761b4cd5718a7118f2c95eb55f181d0a5f004f1) 固定 `b761b4cd5718a7118f2c95eb55f181d0a5f004f1`，2026-10-08。实际API分支清单没有4.7稳定分支；不能直接假定master与任意stable完全匹配。不过本次所读 `3d/ik/project.godot` 明确声明 `config/features=PackedStringArray("4.7")`。
- engine与官方demo均为MIT，实际读取 [engine LICENSE](https://github.com/godotengine/godot/blob/4.7.2-stable/LICENSE.txt) 与 [demo LICENSE](https://github.com/godotengine/godot-demo-projects/blob/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/LICENSE.md)。借用代码保留声明；控制代码的许可不自动覆盖任意第三方角色／贴图。Miao仍用自有角色，不把机器人替换成最终猫。
- 本地只读源码／XML快照在 `artifacts/godot-motion-research/`；没有把阅读源码当运行成功。

## 收敛为四个可借鉴组件

| 组件 | 实际核查到的实现 | Miao用途／复用粒度 | 边界与风险 |
| --- | --- | --- | --- |
| **1. AnimationTree＋OneShot／过滤混合** | 读固定tag的 `AnimationNodeOneShot.xml`：FIRE／ABORT／FADE_OUT请求、下一process自动清请求、可过滤track、`autorestart=false`。官方 [platformer/player.gd](https://github.com/godotengine/godot-demo-projects/blob/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/3d/platformer/player/player.gd) 实际有输入上升沿、多个 `parameters/.../blend_amount`；对应player.tscn确有AnimationTree图。 | 借输入边沿、参数层及track过滤：演奏臂独立于头眼／呼吸时钟；单次动作结束回准备态。 | 它控制已有AnimationPlayer动画，不生成好动作。每键无脑FIRE可能重置动作；同帧多个事件也不保证逐个排队。需自己的phase／事件调度，不能用crossfade穿过琴面掩盖跳变。[官方说明](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html)。 |
| **2. 内置TwoBoneIK3D＋LookAtModifier3D目标修正** | 读 [TwoBoneIK3D.xml](https://github.com/godotengine/godot/blob/4.7.2-stable/doc/classes/TwoBoneIK3D.xml) 和 [实际求解C++](https://github.com/godotengine/godot/blob/4.7.2-stable/scene/3d/two_bone_ik_3d.cpp)：pole构成平面、两圆交点确定解。LookAt实际有bone、target、角限、阻尼阈值、origin safe margin、duration，父骨modifier须在子骨前。 | 右肩—肘—腕追随**琴局部跨弦目标轨迹**；左掌固定握颈。LookAt只让已有头骨小幅望向手／琴，不每音重置。 | 需要真实Skeleton3D／权重和已接受的掌趾结构。两骨IK不自动解决各指接触、关节限制或手腕扭转；目标不可达／pole共线要约束。当前浅贴合虹膜不能随意当自由球体旋转，眼部rig另验。 |
| **3. 内置SpringBoneSimulator3D** | 读 [4.7.2实际C++](https://github.com/godotengine/godot/blob/4.7.2-stable/scene/3d/spring_bone_simulator_3d.cpp)：Verlet尾点、stiffness／drag／外力、骨长限制、专用SpringBoneCollision处理后写回骨旋转。 | 小耳尖／尾端等次级响应，身体／头已动后自然跟随；主手与触弦不交给弹簧。 | 官方说明不支持Y型分叉链、骨架／骨骼缩放会有问题；碰撞器与PhysicsServer3D独立，不能当琴面／指尖通用物理。delta参与积分，暂停／掉帧／30/60fps需实测。不要用每帧随机force制造“活泼”。[官方类文档](https://docs.godotengine.org/en/stable/classes/class_springbonesimulator3d.html)。 |
| **4. WiggleBone纯GDScript单骨弹簧备选** | [detomon/wigglebone](https://github.com/detomon/wigglebone/tree/d45042dd05680149b4c1174771f1f666f262057d)，commit `d45042dd05680149b4c1174771f1f666f262057d`，2026-05-11，MIT（实际LICENSE）。读rotation／position modifier与properties：SkeletonModifier3D、频率／阻尼／摆角限制、reset、force／torque impulse，旋转用sin/cos弹簧更新，delta被clamp。 | 可直接import `examples/wigglebone/rotation/rotation.tscn` 或 `rotation_hang.tscn` 验单骨惯性；运行代码只取 `addons/wigglebone` 必要脚本与资源。作为内置Spring的对照，不对同骨叠两套spring。 | 源码仍覆写旧 `_process_modification()`，4.7.2已deprecated但保留；新实现宜按官方带delta回调迁移／验证。作者也有>PI极端旋转FIXME，不能称任意角度稳定。纯GDScript无native扩展，**推断**Web复用负担较低；本机／Web均尚未实跑。 |

[Godot SkeletonModifier3D官方文档](https://docs.godotengine.org/en/stable/classes/class_skeletonmodifier3d.html)及固定tag XML确认：modifiers位于Skeleton3D下，在AnimationMixer之后执行；新自定义modifier用 `_process_modification_with_delta(delta)`，可能收到0delta；`influence`由Skeleton应用，脚本不能再自行乘一次造成双重混合。顺序必须明确：基础动作／连续idle → 受限头部修正 → 手IK → 耳尾次级响应；不让随机层覆盖接触约束。

## 官方IK demo能直接借什么，不能照搬什么

[3d/ik](https://github.com/godotengine/godot-demo-projects/tree/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/3d/ik) 有四个现成场景，可借Target／MiddleJoint、鼠标目标和姿态观察方式。实际README为 **Forward+**；`skeleton_ik_runner.gd` 调旧 `SkeletonIK3D.start(false)`，SADE `ik_fabrik.gd`／`ik_look_at.gd` 都是Node3D脚本，不是现代modifier。FABRIK有10次迭代／.01容差，并保留较旧更新／override路径。故不要整套搬入新Web项目再宣称用了最新IK；主手优先内置TwoBoneIK，旧demo用来理解和对照目标控制。

本次另核查 [godot-ai-animation-toolkit](https://github.com/michaltomczykowski/godot-ai-animation-toolkit/tree/5e13a6c0099b1a0f9255d661f5c5ac17fc9c9082)（`5e13a6c0099b1a0f9255d661f5c5ac17fc9c9082`，2026-09-26，MIT）实际 `handlers/rig.gd`，有IK／LookAt／Spring设置与骨架检查；但不为Miao引入整套代理工具。其 `blink()` 默认把eye／lid骨Y缩至0.05，不能拿来解决我们的真实皮面闭合。旧 [Bauxitedev/godot-jigglebones](https://github.com/Bauxitedev/godot-jigglebones/tree/19229b3e8ea02ddda466a92f68cdccf8b4b9c85b) 是Godot3／2019代码，不选作4.7起点。

## 随机动作应是有状态的次级行为

主手保持确定的“准备—跨弦—脱弦—回收”与输入事件；随机只改变低频目光目标、允许时段的眨眼、轻微耳尾余振等。事件间隔和幅度可有有界差异，但seed／输入时间可复现，目标经过平滑和角限；连续快弹时不每音重启头、眼、呼吸。禁止每帧给骨位置抽随机数、把手指触弦交给弹簧自由晃、或随机重播整段idle。眨眼必须先通过真实眼睑＋角膜遮挡关，再接随机调度。

## Web边界会影响最终方案

[官方Web导出文档](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)确认：Godot4 Web需要WASM／WebGL2，只支持Compatibility；Forward+／Mobile不能直接用于Web，当前C#项目不能导出Web。单线程是默认，可避免多线程所需跨源隔离；Sample音频低延迟但有effects／程序音频等限制，改Stream又有延迟权衡。对Miao宜保留现有Web Audio采样／事件／录制能力，单独验证Godot canvas接线，而不是换引擎后把原功能丢掉。

骨骼modifier是引擎CPU能力，纯GDScript也无额外native插件；这是可尝试Web的依据，不是已测帧率。必须用Compatibility导出测本机浏览器、手机及Safari，记录包体、首帧、内存、输入到实际触弦延迟，不能拿桌面Forward+流畅作Web通过。

[官方导入文档](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)明确 `.blend` 导入也先调用Blender转glTF，并非直接运行Blender材质／groom。当前Miao约60万顶点和18万native短毛、程序毛色、角膜／linked lights不会自动以Cycles质感进入Web。须比较烘焙纹理、可接受的毛发网格／卡片／shader近似和真正蒙皮；没有Skeleton3D的静态hold key不能直接获得手IK。外观损失不能以帧率抵消，完整连续猫／双爪／琴仍须在同一场景帧内。

## 与Blender做可执行公平对比

| 项目 | Blender侧 | Godot侧 | 共同验收 |
| --- | --- | --- | --- |
| 同一资产 | 保留C8作者工程／Cycles美术参考 | 导入同一完整猫和琴，验证骨架、权重、blend shapes及材质近似 | 同相机、同占幅、同手位；不换机器人或粗猫来赢速度 |
| 单次／连奏 | 作者控制／关键姿态驱动，输出完整帧 | 同跨弦目标轨迹＋phase调度＋IK；头眼／耳尾独立连续 | 单按一次触弦；慢连每音清楚；快连不僵／不积压；停止不补演 |
| 精致度 | 短绒、暖橘、木材、湿润眼睛为美术对照 | Compatibility实际效果，不只桌面漂亮图 | 正面、3Q、脸爪琴局部及真实动作；P0不以性能平均抵消 |
| 导出与性能 | 记录真实渲染／编码时间、素材体积 | native及Web分别测实际运行；Movie Maker用于可复现离线对照 | 统一6–10秒事件序列，原速／慢放、接触侧视、音画时间对应 |

建议第一条对照序列：固定seed、idle2秒 → 单按 → 4次500ms慢连 → 8次150ms快连 → 停止。时长可延长但两边事件完全相同。事件文件至少有accepted input时间／ID、音频attack、主要触弦crossing与phase；judge必须实际看MP4与完整帧，不能只看日志。输入脚本回放与网页真实点击分开验。

Godot可用[官方Movie Maker](https://docs.godotengine.org/en/stable/tutorials/animation/creating_movies.html)离线固定步长抓完整画面／声音，例如准备好项目后：

```sh
godot --path /absolute/path/to/comparison --rendering-method gl_compatibility \
  --write-movie /absolute/path/to/output/comparison.avi --fixed-fps 60 --quit-after 600
ffmpeg -i /absolute/path/to/output/comparison.avi -c:v libx264 -crf 18 \
  -pix_fmt yuv420p -c:a aac /absolute/path/to/output/comparison.mp4
```

以上为待执行建议，不是本次跑过的命令。内置Movie Maker是离线录制，不替代实时点击延迟／浏览器录制验收；官方格式含OGV、AVI或PNG＋WAV，不能声称原生直接导出MP4。安全退出才能完成文件头。

**当前建议：先让Godot证明“同一只猫能即时、连续、受约束地动”，保留Blender作为造型／毛绒／高质量离线对照。** 若Godot的外观或Web性能不过关，不扩大随机动作和插件栈；若控制明显更好且外观守住，再考虑作为线上运行层。本轮只完成源码与边界调查，Godot导入、自然演奏、Web、媒体导出和最终取代方案全部待实测。
