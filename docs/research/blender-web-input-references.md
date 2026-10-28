# Blender 完整场景到网页按键演奏：源码参考与纠正

查验日期：2026-10-28（北京时间）。本轮优先调研已有项目，用户接管 Blender 安装。当前网页候选移至 `design/blender-guitar-v1/web-draft/`，尚未接真实渲染素材、未发布；状态机测试通过不代表造型/自然度通过。没有安装以下插件、运行第三方脚本、调用付费接口或复制其猫图。

## 结论先行

现成方案已经覆盖输入去重、角色状态、Blender批量渲染、固定画布和图集，但不能据此把“自然的猫拨弦”当作已解决。最值得复用的是现有项目的边界与流水线：真实按键边沿只触发一次、没有历史动作队列、动作具有明确接触事件、整套帧共享相机与画布。我们继续直接import现站 `sampled-audio.js`、`bindings.js`、`media-export.js`，Blender只负责离线完整场景；网页每次只绘制一张含完整猫和吉他的图。候选motion.js是本轮自行实现，借鉴以下输入/周期原则，不是任何上游状态机的移植。

实际查阅了下面五个项目中的源码/文档，并核对默认分支固定提交。没有因为 stars 或 README 的漂亮展示就称其自然度已实测。Bongo Cat 浏览器演示页面可访问；其余展示页/图/视频入口已检查，但没有将页面可打开冒充插件已运行或视频全片已审看。

| 项目 | 默认分支最近提交（UTC） | 许可/依赖 | 已经做到什么 | 对当前方案的判断 |
|---|---|---|---|---|
| [Externalizable/bongo.cat](https://github.com/Externalizable/bongo.cat/tree/591940644775d7cfd5167eceeeb6b97a1f9aadd4) | 2023-10-13，`591940644775d7cfd5167eceeeb6b97a1f9aadd4` | MIT；jQuery/lowLag与SoundManager兼容层 | 浏览器键盘/触摸演奏；pressed去重；按下/释放直接映射爪状态 | 复用边沿语义；不引入老音频栈，不复制分离爪层 |
| [ayangweb/BongoCat](https://github.com/ayangweb/BongoCat/tree/47a73ed1765b13fdd674ec356d51b5b16a6b5a5b) | 2026-10-28，`47a73ed1765b13fdd674ec356d51b5b16a6b5a5b` | 当前固定提交为 Apache-2.0；Rust/原生runtime，Cubism组件另有许可 | 可靠按键边沿、模型输入参数、动作优先级、未完同动作幂等、一次周期、释放/重置 | 复用状态合同和测试思路；不作为网页运行时，不导入Cubism或模型资源 |
| [Blender-Spritesheet-Renderer](https://github.com/chrishayesmu/Blender-Spritesheet-Renderer/tree/445964c610ec24a2a833a46a0b2e71cdfb788e50) | 2021-09-15，`445964c610ec24a2a833a46a0b2e71cdfb788e50` | MIT；Blender、ImageMagick；README仅确认Blender2.9测试 | 批量动作/材料/视角渲染；相机边界计算；渲染结束还原场景；拼图 | 可参考固定边界/场景快照；版本较老，不能未经验证整包安装到新Blender |
| [SpriteSheetMaker](https://github.com/ManasMakde/SpriteSheetMaker/tree/5f48dfbd6f2049af23806924b3dcae0ee5ad5439) | 2026-09-08，`5f48dfbd6f2049af23806924b3dcae0ee5ad5439` | 仓库LICENSE为MIT，但同提交extension manifest声明GPL-3.0-or-later；要求Blender≥5.1并带Pillow轮子 | 3D动画到图集、统一格尺寸、边距对齐、行/strip/单帧输出、复用modules | 功能最贴离线图集；先记录许可声明冲突与版本要求，不直接vendor到MIT产品 |
| [FretDance](https://github.com/highmore9501/fretDance/tree/f63d1a6e5110a10d92b5c18fcdbd100e421b1878) | 2026-08-07，`f63d1a6e5110a10d92b5c18fcdbd100e421b1878`，提交为“仓库停更” | MIT旧仓；Python≥3.10/mathutils/mido/numpy；后续MusicDoll生成器非开源 | MIDI到左右手/琴弦演奏轨迹及Blender桥接 | 最贴真正的吉他演奏，但不等于现成网页猫模型；先读轨迹策略，不引入完整MIDI/人手系统 |

## 1. Bongo Cat：输入响应为什么清楚

[真实浏览器页面](https://bongo.cat/)仍展示A/D鼓、1…0钢琴等按键入口。[固定源码 `js/core.js`](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/js/core.js) 的 `$.play` 在按下时检查 `pressed`，已按住则直接返回；第一次按下播放声音，释放清除pressed。爪状态来自这个输入状态，没有播放一串与输入无关的随机动作。

这正是“按一下只动一下”的直接参考。它的爪通过CSS图层位置切换，不能照搬成我们的生产结构；用户已经要求每帧完整猫和乐器，新的Blender输出仍须整图。[LICENSE](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/LICENSE)是代码许可；README另署猫图作者，不能把代码许可直接当作所有美术已清晰授权给本项目。

## 2. 当前 BongoCat 桌面版：状态合同比“动画很顺”更值得借

已读[输入语义](https://github.com/ayangweb/BongoCat/blob/47a73ed1765b13fdd674ec356d51b5b16a6b5a5b/shared/behavior/input-semantics.md)、[动画语义](https://github.com/ayangweb/BongoCat/blob/47a73ed1765b13fdd674ec356d51b5b16a6b5a5b/shared/behavior/animation-semantics.md)、[实际模型参数应用代码](https://github.com/ayangweb/BongoCat/blob/47a73ed1765b13fdd674ec356d51b5b16a6b5a5b/crates/bongocat-runtime/src/rendering/model_input.rs)、[worker输入代码](https://github.com/ayangweb/BongoCat/blob/47a73ed1765b13fdd674ec356d51b5b16a6b5a5b/crates/bongocat-runtime/src/worker/input.rs)。重复key_down不重复触发；reset清除瞬时状态；同优先级未完同动作请求不重新启动；动作只运行一个周期，完成后保留末态。文档同时区分可靠按键边沿与可合并的cursor/axis高频值，不能随便把它们混为一个会丢release的队列。

我们可以直接沿用这些验收规则：按住不连发、blur/hidden清理、没有按键时不补旧动作、换模型不能被旧异步结果覆盖。不能把其Live2D参数层/原生输入钩子照搬成浏览器实现，也不需要为了一个网页玩具引入系统级键盘监听。

## 3. 两条 Blender 到图集流水线

旧版Spritesheet Renderer的[render_operator.py](https://github.com/chrishayesmu/Blender-Spritesheet-Renderer/blob/445964c610ec24a2a833a46a0b2e71cdfb788e50/render_operator.py)存在渲染校验、帧/动作循环与 `SceneSnapshot.restore_from_snapshot`；[Camera.py](https://github.com/chrishayesmu/Blender-Spritesheet-Renderer/blob/445964c610ec24a2a833a46a0b2e71cdfb788e50/util/Camera.py)处理一致取景边界；[ImageMagick.py](https://github.com/chrishayesmu/Blender-Spritesheet-Renderer/blob/445964c610ec24a2a833a46a0b2e71cdfb788e50/util/ImageMagick.py)调用外部拼图工具。其[README](https://github.com/chrishayesmu/Blender-Spritesheet-Renderer/blob/445964c610ec24a2a833a46a0b2e71cdfb788e50/README.md)明确只测过Blender2.9。因此可以复用思想或审过的窄模块，不能把旧兼容假设当作Blender4/5已可运行。

SpriteSheetMaker的[combine_frames.py](https://github.com/ManasMakde/SpriteSheetMaker/blob/5f48dfbd6f2049af23806924b3dcae0ee5ad5439/modules/combine_frames.py)直接用Pillow完成cell尺寸、行高、对齐/边距与组合；[sprite_sheet_utils.py](https://github.com/ManasMakde/SpriteSheetMaker/blob/5f48dfbd6f2049af23806924b3dcae0ee5ad5439/modules/sprite_sheet_utils.py)处理Blender侧捕获。作者README说明modules可独立复用，不过[LICENSE](https://github.com/ManasMakde/SpriteSheetMaker/blob/5f48dfbd6f2049af23806924b3dcae0ee5ad5439/LICENSE)与[extension manifest](https://github.com/ManasMakde/SpriteSheetMaker/blob/5f48dfbd6f2049af23806924b3dcae0ee5ad5439/blender_manifest.toml)许可声明不一致，兼容最低5.1也需满足。本轮只读，不导入其代码。

对我们可立即采用的输出约束：同一相机、同一分辨率、同一脚底锚点；包含手/琴运动的全范围边界；整帧记录明确帧号/FPS；不要按每帧可见物体重新裁切导致角色呼吸式缩放。以上工具解决导出，不负责做好猫的脸和演奏轨迹。

## 4. FretDance：真正的演奏系统不要求每音回准备位

已独立读取固定提交的[演奏轨迹代码](https://github.com/highmore9501/fretDance/blob/f63d1a6e5110a10d92b5c18fcdbd100e421b1878/src/animate/animate.py#L512)、[依赖](https://github.com/highmore9501/fretDance/blob/f63d1a6e5110a10d92b5c18fcdbd100e421b1878/pyproject.toml)、[MIT许可](https://github.com/highmore9501/fretDance/blob/f63d1a6e5110a10d92b5c18fcdbd100e421b1878/LICENSE)与README。提交日期/最新分支由同组judge核实；本Agent匿名metadata API遇403/代理503，未拿该失败当作仓库不存在，固定raw源码随后读取成功。

`rightHand2Animation`使用`int(FPS/15)`作为演奏时长基准，扫弦时间加倍；仅下个音留下足够间隔时才插回准备位。`ElectronicRightHand2Animation`保持`pick_position`，从当前拨片在哪侧决定上/下扫；拨完保持位置，注释明确无需强制回准备。这是对“每个音都完整归零”的直接反例：先考虑当前状态和下个音的时间，才决定是否需要完整回收。

后续可复用旧MIT实现中的接触点计算/准备和拨后姿态设计，前提是我们的猫爪rig、琴弦坐标和数据接口匹配，并保留许可。首版只做圆爪拨弦，不引入其人手逐指/MIDI指法搜索系统。若要上/下拨交替，也必须分别渲染明确方向的完整动作，不能倒放一段下拨来冒充上拨。

[项目README](https://github.com/highmore9501/fretDance/blob/f63d1a6e5110a10d92b5c18fcdbd100e421b1878/readMe.md)给出[电吉他](https://www.bilibili.com/video/BV183t9zXEu6/)和[古典吉他](https://www.bilibili.com/video/BV1HmY6zEEwZ/)作品入口，同时明确旧仓停更、新MusicDoll动画生成部分不开放源码，公开Blender/Unreal仓只是数据交换插件。不能把“新产品有demo”说成“整个生成器可免费import”。本轮没有运行其完整演奏系统、没有声称视频全片逐帧看过。

## 5. 对自己初稿的纠正

初版网页控制器在用户重触发时，会把 `2→23` 的恢复帧反向走回触弦帧2。这只在“恢复姿态恰好是一条可安全反向的单调轨迹”时成立，尚未有实际Blender画面证明。如果恢复包含下扫follow-through和离弦回收，逆走会反穿琴弦，产生无输入的第二次碰弦；单看 `contacts` 计数可能掩盖几何问题。

上述真实项目没有提供“倒放恢复天然正确”的依据。因此已按主Agent确认改掉：

1. 单按：准备→触弦→离弦回收→准备，一次周期。
2. 重触发：保持当前帧位置，只向前完成离弦回收；仅在末帧与准备帧相同的公共姿势处wrap，再开始下一次触弦。
3. 剩余回收最多加速3倍，重复输入不层层加速。最多保存一个最新请求；180ms（0.5x时360ms）过期请求不补演。
4. 极快输入动作合并，音频仍按真实输入即时发出；UI说明这一限制，不能宣称每个极密音都对应独立完整动作。
5. 不crossfade两张完整画面，以免出现双爪重影；不拆身体和手臂。

候选状态机7项测试通过，并有5项DOM/异步交互检查，包含正向单调与只在准备位wrap、没有历史动作队列、过期不补演等。但这仍不是自然度通过：下一步必须检查最终整帧、原速/半速、单击/150ms/80ms连按，以及真正导出的成片。若150ms连续演奏仍明显滞后，应参考FretDance的“从当前接触状态继续”或新增专用短行程动作，而不是继续压缩大动作成瞬间甩爪。

## 尚未验证

- Blender实际模型、相连肩肘爪、琴弦接触几何及最终静帧质感。
- 新版Blender中第三方插件的安装兼容性，未声称已运行。
- 新atlas的每帧像素、0/23准备姿势一致性、慢速与快速输入原速自然度。
- 独立测试页浏览器输入/音画同步、导出文件、移动端与真实扬声器体验。

检索中的论文项目链接 `https://pei-xu.github.io/guitar/` 与猜测仓库 `Pei-Xu/guitar`本次均404，保留为source gap，没有把论文摘要当成拿到了可复用代码。
