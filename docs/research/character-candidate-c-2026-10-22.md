# 角色候选 C：淘气小鼓手 · 2026-10-22

## 方向与身份

一只会自己玩进音乐里的小猫。可爱不靠正脸摆拍，而是认真按键、抱着吉他扫弦、打鼓时偷偷得意；让人感到“它也觉得这段很好玩”。不是成人摇滚歌手，也不是三只造型不同的猫。

统一身份：炭灰短绒毛、奶油色口鼻/下巴、蜜金眼睛、粉色内耳与鼻子、鼠尾草绿耳机、圆短躯干、大爪、活泼弯尾。三格里保留这些识别点，分别用视线、肩部重心和动作表达不同乐器的音乐感。

与当前线上猫相比，重点不是更精细的毛，而是：

- 钢琴：往键盘里投入、双爪分工、脚尖跟拍；目光跟着音乐发生的位置。
- 吉他：抱住乐器、身体有斜线与扭动；抱琴与扫弦可读，不是把吉他贴在两拳中间。
- 架子鼓：一高一低的动作、单眼小得意、脚踏；音乐不是按键后才被动附加的表情。

本方案是原创方向探索，不声称为真实流行meme、第三方既有角色、可直接部署的动作资产或已完成3D模型。

## 交付与来源

- 仓库图：`design/candidates/playful-player-v1.png`
- 类型：一张三格角色概念板，1967 × 799，PNG，浅奶油背景，无文字。
- 字节：2,312,178
- SHA256：`e763353e699f899b3dcfea2da862596d12d1c5773cb4a1b1b1dd37803f6e1f5a`
- 生成工具：内置 `image_gen.imagegen`，单次调用；没有CLI、没有替代模型调用。
- 输入图：无。本轮之前实际看过现concept、线上overview/guidance/鼓组截图与当前atlas以理解问题；这些没有作为图像引用传入生成。
- 原始生成文件：`exec-cdd2f4dc-2b9d-44d1-a105-cde443fa54ee.png`，工具默认生成目录保留；复制到上述仓库路径，无像素编辑、裁切、压缩或覆盖原素材。
- 生成后实际查看了原始输出和最终保存文件；两者逐字节相同。
- 此处只保存概念板和本文，没有修改runtime、exporter或线上角色。代码许可不能替代角色素材的来源说明；本方案也没有额外宣称CC0或权利已全面清理。

## 实际图像自评：保留什么、警惕什么

**有效的部分：** 三格能看出同一只小猫，灰毛/奶油口鼻/耳机/尾巴一致。钢琴目光向下、两爪落到键盘上，脸带小小笑意；吉他斜抱与站姿把身体的节拍感带出来，眼神带好奇与得意；鼓手一只眼睛闭上、两臂方向不对称，脚与踏板位置有关联。整体没有成人服装、墨镜、摇滚舞台或正面双拳摆拍，也没有文字与水印。

**没有完全达到的部分：**

1. 鼓槌在小尺寸看起来像在敲，但前方横着的槌头与鼓面仍有可见间隙；另一根是举起状态。不能把它记录成严格接触帧。单侧镲也更像单片镲，不能据此声称已经准确表现完整踩镲机械。
2. 吉他扫弦爪带有烘焙在图里的运动模糊，能传达动作，却不能直接当可重触发的前肢贴图；分层时要做清晰的静态爪/前臂，模糊由动画或短残影另行决定。
3. 图是连在奶油背景与地面阴影里的概念板，不是透明组件atlas。钢琴凳、支架、琴身、鼓组与猫互相遮挡，不能简单抠四块就得到完整运动范围。
4. 三格角色有相近大小与一致方向，但站姿/坐姿、耳机转角和脚部姿态不是完全锁定的生产模型；后续角色基准需要固定比例、摄像机与乐器接触坐标。
5. 鼓手的眨眼适合作为短促的得意帧，不宜整段演奏一直固定闭一只眼；钢琴与吉他也需要独立的放松基态，不能每次用户开网页都停在高能表演姿势。

这张图支持“自发玩音乐”的设计判断，不证明运动插值已经自然、真实音画已经同步，或用户一定更喜欢C。

## 轻量2.5D可实施性

| 项目 | 能复用的结构 | 需要的新资产/校正 |
| --- | --- | --- |
| 共用猫身份 | 现有head/body/左右paw的rig思路、音频事件、取消与减少动态机制 | 将本方向固定为同一套比例和三分之四角度基准；新头/躯干/前肢/尾巴，不直接重用当前正面atlas |
| 钢琴 | 小幅躯干前倾、两侧下压/回弹、脚尖或尾巴轻跟拍 | 独立清晰前肢与固定键盘；下压接触帧对齐，尾部需要单层 |
| 吉他 | body轻转、短扫弦、持琴侧前肢大体保持 | 琴身与琴颈应独立、持琴爪遮挡层和清晰扫弦爪；不能用现在带模糊的画面反复平移 |
| 架子鼓 | 左右strike独立、减弱动态、按音频时钟显示响应 | 独立鼓槌/握槌爪、可读snare/镲落点、脚踏；先校正槌头到鼓面接触 |
| 表情 | 头部轻转、等待/预备/实际输入/收尾状态 | 中性睁眼头为主；短眨眼/得意头变体。独立眼球或耳朵若要运动需真分层，不能冒充已有 |
| 节拍感 | 一次真实触发一个短动作，身体滞后小回弹；快按采样当前姿态续接 | 一段完整待机→预备→3击→快速重击→停下的motion test；不是继续堆静帧 |

现有4层能力可以复用实现方法，但此三格图不是可以直接替换线上atlas的文件。建议先锁身份与一个相机，然后做可单独启停、部件不交叉的透明生产组件；先以钢琴三击和鼓的单次落点验证，再扩吉他，不同时跳到全方向3D或长视频。

## 用于交叉judge的问题

1. 将三格缩到实际猫舞台的小尺寸，是否仍能一眼读出“在弹/在扫/在敲”，并且仍像同一只猫？
2. 童真来自认真和小得意，还是只来自大眼睛？哪一格最有音乐范儿，哪一格动作像摆拍？
3. 相比候选A/B，C是否更适合用户随手乱弹也被猫接住，而不是只适合高手表演？
4. 如果只允许补一套最小资产，三分之四角度、乐器遮挡和鼓棒的成本是否值得？是否可以保留C的情绪/身体倾斜，换更容易做的视角？
5. 上线前必须校正哪些具体接触点？本图的鼓槌间隙与扫弦模糊不能因为表情讨喜而跳过。

## 完整生成prompt

```text
Use case: stylized-concept.
Asset type: one original character direction board for Miao Beat, a lightweight browser music toy.
Primary request: A playful little kitten musician with the spontaneous musical joy of a mischievous child, shown as THE SAME EXACT CHARACTER in THREE equally sized side-by-side panels: piano, acoustic guitar, drum kit. This is candidate C, the playful little drummer who can also play other instruments.
Scene/backdrop: pale warm cream studio background in all three panels, soft grounding shadows, clear separation by empty space only. No text, labels, letters, logos, watermarks, UI, or visible panel borders.
Character identity shared across all three scenes: one small round charcoal-gray kitten, warm honey-gold eyes, tiny cream chin, warm pink ear interiors, short soft simplified fur, oversized soft mitten paws, compact pear-shaped body, a lively curved tail and sage green child-sized headphones. Preserve exactly the same face, proportions, colors, headphones and rendering style across the three scenes. Sweet and impish, not an adult rock star. No clothing costume, sunglasses, leather, spikes or stage pyrotechnics.
Style: appealing polished animated-film concept art with readable rounded forms and restrained soft fur, tactile but clean enough to cut into a small 2.5D head/body/front-paw/tail puppet later. Not photorealistic, not a flat sticker mascot.
Composition: wide horizontal triptych, same camera height, same character size and visual weight in each scene, each entire kitten and instrument comfortably inside its own equal-width panel. Three-quarter view, asymmetric active poses, clearly readable small silhouettes. Avoid straight-on symmetrical portrait posing and two raised clenched fists.
Left panel, piano: kitten is genuinely in the middle of playing a small keyboard, body leaning into the beat, one open paw visibly pressing keys and the other about to land on different keys. Head angled attentively toward the keys, bright focused eyes and a tiny pleased smile; one hind paw and curved tail suggest a gentle foot tap. Anatomically coherent paws and believable contact with keys.
Middle panel, guitar: same kitten cuddles a small nylon-string acoustic guitar diagonally against its torso, one front paw visibly on the fretboard and the other strumming over the sound hole. A slight rhythmic shoulder twist and soft head bob, concentrated but cheekily proud expression. Correct guitar body, neck and string path; paws genuinely reach the instrument, no disconnected floating hands.
Right panel, drums: same kitten absorbed in playful drumming on a compact child-sized snare, kick and hi-hat kit, front paws naturally grasping two short wooden drumsticks. One stick is in credible contact with the snare while the other is raised toward the hi-hat, body has a small off-center rhythmic bounce, one hind foot works the kick pedal. One eye slightly narrowed in delighted focus, tiny self-satisfied grin, ears lively. Correct limb count and plausible stick grip.
Constraints: this is an original fictional kitten, no third-party character imitation or meme claim. Actual music-making body mechanics and shared attention toward each instrument are the focus. Keep the face fully visible enough to judge emotion, no instrument obscuring the head. No extra characters, duplicate paws, human hands, decorative floating musical notes, confetti, or generic front-facing display poses. A concept board, not an animation-ready atlas or completed 3D model.
```

