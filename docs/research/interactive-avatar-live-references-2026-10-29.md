# 可直接打开的虚拟形象交互参考 · 2026-10-29

本轮目标是找真实网页成品，而不是再列渲染引擎。只用了项目网站、原仓库和创作者/Google 官方介绍。未安装、付费、复制第三方资产或修改线上页面。

最值得先看 **Viola the Bird**：可爱动物与乐器组成一个完整角色，直接操弓演奏；它最接近 Miao 想做到的完成度。**Bongo Cat** 是立即上手和输入反馈的基准。想看有明确开源代码的前端 3D 动画控制，再看 **Ecctrl**。

## 入口与证据

| 项目 | 真实网页入口 | 已有交互与画面 | 本轮实测边界 | 源码 / 许可 / 维护证据 |
| --- | --- | --- | --- | --- |
| Viola the Bird · David Li / Google | [启动实验](https://artsandculture.google.com/experiment/nAEJVwNkp-FnrQ) | 精致紫色羽毛鸟，爪持乐器、喙带弓；官方提供 Concert、Freestyle、录制分享。左右拖动操弓，角色与演奏动作是一件事。 | 官方详情与启动后的实验界面加载成功，能读到操作与录制控件；直接官方 embed 在当前 IAB 返回平台不支持，未完成实际奏响验收。不能写成本机已完整玩通。 | [官方介绍，2023-07-12](https://blog.google/company-news/outreach-and-initiatives/arts-culture/meet-viola-the-bird-a-new-experiment-inspired-by-the-cello/)。未找到已核验的公开项目源码、角色资产许可或当前维护承诺。只能当质量/交互参考。 |
| Bongo Cat · Externalizable | [直接玩](https://bongo.cat/) | 页面直接给键位；A/D 邦戈鼓、数字钢琴、Q–P 马林巴，几乎没有学习步骤。 | **实际按 1，画面切到键盘；再按 A，切回邦戈鼓。** 是真实输入驱动页面，不是视频。截图在松键后捕获，不能用它证明逐帧落爪时序；未进行物理扬声器听感验收。 | [原仓库](https://github.com/Externalizable/bongo.cat)，MIT 项目标注；README 单列原画作者给予该站的书面使用许可，不能把代码 MIT 等同所有美术可任意搬用。仓库显示 62 commits；本轮未核验最后提交时间，不称持续活跃维护。 |
| Blob Opera · David Li / Google | [启动实验](https://artsandculture.google.com/experiment/blob-opera/AAHWrq360NcGbw) | 四个有眼睛与嘴的软体角色；纵向拖动音高、横向控制元音，其余角色跟随和声；有录制与分享。 | **已启动到实时角色教程画面**，看到紫色角色、眼神变化与拖动提示。发出了两次拖动，但教程未推进；未把拖动成功/实际发声列为通过。 | [官方技术背景](https://blog.google/company-news/outreach-and-initiatives/arts-culture/story-behind-blob-opera-world-tour/)。Google 提及 I/O 特别版本使用 WASM SIMD，不能据此认定当前公开版本或具体美术渲染栈。未核验公开源码/角色许可。 |
| Ecctrl · pmndrs | [直接玩 3D 控制器](https://ecctrl.app/) | 浏览器中完整人形，WASD 移动、Shift 跑、Space 跳；有实时参数面板。它是角色控制/动画的技术参考，不是 Miao 的造型样板。 | **已加载实时 3D 场景并发送 W 长按**，场景/跟随视角发生位移；截图为松键后的站立态，没有记录完整动作过程。页面显示输入提示、运行帧率与参数。 | [原仓库](https://github.com/pmndrs/ecctrl)、[当前 README](https://github.com/pmndrs/ecctrl/blob/main/readme.md)：React Three Fiber + Rapier，可导入运行时动画状态控制；MIT。演示页另标动画来自 Quaternius Universal Animation Library（CC0）。版权年份到 2026；最后提交时间未核验。 |
| Neko Space · でぶねこ | [直接玩猫咪漂浮](https://asobi-nekospace.vercel.app/) | 完整 3D 猫漂浮；点按弹开、长按旋转、拖动抛掷、悬停注意。视觉是低多边形猫，**达不到 Miao 的精致标准**；仅参考互动。 | **已加载多猫实时场景并打开玩法说明**；未完整验收拖放。 | [创作者方法文章，2026-10-23](https://zenn.dev/devnekoo/articles/be51a4dbc53801)：Blender 猫导出 GLB，再由 Three.js / GLTFLoader 在网页加载；指针映射、惯性与缓动有代码片段。未核验公开完整仓库与模型复用许可。 |

## 能确定的实现，不靠外观猜引擎

**Bongo Cat 的在线前端入口**是 [core.js](https://bongo.cat/js/core.js)。本轮读到键盘按下/松开处理、音频播放、图片层可见性与背景位置切换；实际页面脚本还加载 jQuery、lowLag 和 SoundManager2。这说明简单可爱的反馈无需 3D，但它的分层方案不能直接当作本项目的生产方案：Miao 已明确要求完整猫/爪/乐器共同出现在每个生产帧中。

**Ecctrl** 的前端技术栈由原仓库直接说明，适合研究输入状态怎样接动画状态、如何保持持续动作，不能解决 Miao 猫脸、绒毛和正确握琴本身的问题。无需为固定机位演奏引入它的车辆、重力与完整物理场景。

**Neko Space** 的创作者明确给出 Blender → GLB → Three.js 的流程。这是“Blender 负责做资产，网页负责实时呈现”的实物例子；Blender 与前端渲染是上下游关系。项目中的猫并不是 Miao 可直接使用的精致资产。

**Viola / Blob Opera** 有真实网页实验和官方产品说明，但本轮没有得到可确认的角色渲染源码。不要仅凭截图就断言 Three.js、Godot 或 Blender 渲染，也不要把官方图片当成本机交互通过的证据。

## 对 Miao 的具体启发（判断，尚未实现）

1. **以 Viola 的“角色正在做一件可信的事”为质量目标。** 关键是抓握、接触点、目光与连续动作互相解释。羽毛、灯光、动作都服务同一个角色，不靠页面动效掩盖姿势错误。先验收完整猫与琴的静态接触，再做连续演奏。
2. **以 Bongo 的零门槛为输入基准。** 用户第一下就应确定“我按的是哪一个、猫做了哪一下”；不能一次触发多次完整动作，也不能连续按键时只改变声音、右爪不动。
3. **以 Blob Opera 的连续身体响应研究生命感。** 观察眼睛如何关注输入、主动作如何带动身体和回弹，而不是每音符重置头部。它没有手指/琴键接触，不能替代该项验收。
4. **技术验证先复用动画混合的思想，不搬整个游戏控制器。** 用极小的固定机位场景验证单次拨弦、连续拨弦、停止回位、头眼低频响应。模型与动作达标后再决定 Three.js 或 Godot；更换引擎本身不会补齐造型差距。
5. **没有找到能合法直接替换 Miao 原图、同时提供精致猫和清晰演奏动作的完整开源成品。** 这是本轮检索结果，不等于不存在。现阶段可直接复用的是开源控制基础与工作流参考；角色资产、琴爪接触和动作仍须专门制作与独立评审。

## 验收与来源缺口

- 浏览器：本轮为 Codex IAB 桌面环境；不代表 Chrome、Safari、手机扬声器或触摸设备已验证。
- 网页可加载、渲染可见、输入有效、声音听感、录制导出是不同层次；本表逐项区分。
- GitHub 公共 API 本轮返回 rate limit exceeded，未拿到可复核的最新提交时间；没有用第三方索引补成已确认维护事实。
- 本文没有复制第三方代码或资产，没有把未知许可证当可复用授权。
