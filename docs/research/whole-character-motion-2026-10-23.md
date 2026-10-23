# 整角色动作路线复查

2026-10-23，Asia/Shanghai。用户再次否定0.7连续动作。本次不发布新动画；交付视频素材准备包及可核验的上游方法。

## 先前结论修正

“骨长固定、末端到位、没有求解warning”只证明一些工程约束，不证明自然。先前将这些检查作为动画交付依据，标准不足。用户提出的整角色视频方法应先在一个扫弦动作上真正试验，不能读过参考之后仍只交付另一套拼肢体运动。

根线程重新打开生产页，实际触发吉他和弦及钢琴A/K/W/A并查看姿态；先等采样准备好再触发，早先加载中的按键不算动作观察。根观察仍主要是浏览器实时操作与抽帧，未做逐帧视频录制/盲评。可见静态身体与分离前臂关系不完整，不能称连续动态自然。

独立角色评审核对当前源码指出：

- 上臂固定在身体/乐器后，前臂和爪固定在乐器前，不能表现手臂绕过琴边、掌爪握颈的遮挡关系。
- 同一正面拳状爪被旋转用于压键、持棒、扶琴颈，落点准确不能补出这些不同体积和握法。
- 所有动作共用68ms移入、47ms停留、150ms回程；更像往返点，缺少一口气扫过琴弦的动作设计。
- 当前速度在travel中被截限，之前“速度连续”的表述过宽。

以上前三项中可见效果与源码机制相互对应，但不是新一轮观众偏好数据。停止在原9块肢体上继续调骨长、回转方向和裁切来宣称自然度升级。

## 原小红书的重新核对

[陈小爷《用AI做一只3D可交互的追光小猫～》原分享](https://xhslink.cn/o/8oQtxWNLGCT)。重新读到作者正文说明选一张猫图、生成各方向视频，再交给Agent。作者回复提示词在视频各段。

本轮视频画面可读即梦Seedance 2.0 Pro，以及16:9、1080p、10s；可见提示词约束固定摄像机、米色静态背景、不变位置比例、不加其他物体、眼先动头稍后跟随、连续看向。这个新观察补充此前“具体网站未知”的记录，不删除旧记录。评论区点点有AI总结，不能将其当作作者源码或独立实测。

它证明的是一种视频→代表帧→网页交互的制作思路，不能证明任意乐器动作、多输入组合、手机性能或真正实时3D。没有复制其猫图、视频和未知授权素材。

## GitHub真实skills与复用边界

独立上游评审核对实际SKILL、脚本和LICENSE，未安装或调用外部API。

| 候选 | 固定commit | 本轮采用的结论 |
| --- | --- | --- |
| [karem505/character-animation-skill](https://github.com/karem505/character-animation-skill/tree/6fb1cdb1071c32d381ea0ee995014f9b0b6d96fd) | 6fb1cdb1071c32d381ea0ee995014f9b0b6d96fd | Path C支持已有视频抽帧；其`--size`强制正方形，不能原样处理16:9；腿宽归一化不适合抱琴猫。不自带按键/中断状态机。 |
| [0x0funky/agent-sprite-forge video2dsprite](https://github.com/0x0funky/agent-sprite-forge/tree/5324342fdfab72430f4e9604f3fe427009f8596d/skills/video2dsprite) | 5324342fdfab72430f4e9604f3fe427009f8596d | 当前版本支持用户视频，不能照过时搜索摘要称Grok-only。统一画布/锚点、oneshot、impactMs与durationsMs值得复用；JS有frameAt等辅助，但应用输入切换仍需自己接。 |
| [WU-HAOTIAN34/2dimg2motion](https://github.com/WU-HAOTIAN34/2dimg2motion/tree/d4d73e243b6ff64b7cbb3879e45e951f972a7e62) | d4d73e243b6ff64b7cbb3879e45e951f972a7e62 | 整角色关键姿势再补14帧，可作视频失败后的备选。验证画布/基线/首尾一致不能证明接触或自然度。 |

三个仓库代码LICENSE均为MIT；示例美术、模型和视频服务产物另核权利。没有将其依赖、付费生成API或全部运行栈引入产品。

关键原始来源：

- [Karem抽帧实现](https://github.com/karem505/character-animation-skill/blob/6fb1cdb1071c32d381ea0ee995014f9b0b6d96fd/scripts/video_to_frames.py)、[归一化实现](https://github.com/karem505/character-animation-skill/blob/6fb1cdb1071c32d381ea0ee995014f9b0b6d96fd/scripts/frames_to_sheet.py)。
- [Sprite Forge导出实现](https://github.com/0x0funky/agent-sprite-forge/blob/5324342fdfab72430f4e9604f3fe427009f8596d/skills/video2dsprite/scripts/engine_export.py)、[JS播放辅助](https://github.com/0x0funky/agent-sprite-forge/blob/5324342fdfab72430f4e9604f3fe427009f8596d/skills/video2dsprite/references/runtime/forge-runtime.mjs)、[限制说明](https://github.com/0x0funky/agent-sprite-forge/blob/5324342fdfab72430f4e9604f3fe427009f8596d/docs/known-limitations.md)。其浏览器证据限headless Chromium/SwiftShader，不代表Safari/iPhone或硬件GPU已测。

## 本轮产物和下一步

`design/video-motion-pilot-2026-10-23/`包含三视图、三个完整场景首帧、实际生图prompt、视频prompt和权利/哈希。内置image_gen生成原创素材，未替换public中的生产资产。三视图锁身份，单场景图作图生视频首帧；先只让用户生成一条吉他5秒单次扫弦。没有要求先为四种乐器批量付费。

视频回来后，先看完整角色/琴/握持能否持续稳定，再选动作帧；先单击、再快按、再停手收尾。每音把完整视频归零会再次抽搐，应按实际素材设计短演奏段及收尾状态。输入发声仍保持即时，琴键/谱面承担音符位置反馈，不承诺每一个音符都对应爪子沿13个琴键机械跑动。

最便宜的停止条件：两次同类视频仍出现多爪、琴形变或握持滑脱，就换整角色关键姿势/人工动作设计；不继续以更多prompt、方向、特效或工程测试掩盖。
