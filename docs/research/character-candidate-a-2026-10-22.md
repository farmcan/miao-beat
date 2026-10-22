# 候选 A：软萌卧室乐手

日期：2026-10-22。独立设计方向；没有改运行时、线上素材或 exporter。已查看旧 concept 和三张生产截图，再生成原创方案；没有向生成器引用旧图。

## 产物与追溯

- 项目文件：`design/candidates/bedroom-musician-v1.png`。
- 工具：内置 `image_gen.imagegen`，单次生成一张；未使用 CLI、外部 API key 或二次编辑。
- 原始输出：`generated_images/01a1579e-102d-7353-8d39-8df4d31c63f7/exec-d9564f01-53f4-47f7-afd9-d7c790af4a92.png`。原始文件保留，直接复制到项目文件，没有裁剪、重绘、压缩或像素修改。
- 输出尺寸：1942 × 809；PNG；2,415,346 bytes；奶油色背景，非透明底。
- 项目 PNG SHA-256：`586d43e48307d26ab857268d01b637c1d86c34b1e898fc1d75db1b06e6b7fbb9`。
- 图片已通过工具原样展示并实际查看。这里只是候选设计，不是已选最佳、用户已喜欢或已经上线。

## 身份与音乐气质

设计身份是温暖灰黑的团子猫、宽圆脸、短口鼻、琥珀眼、小奶白胸毛、短前臂与圆爪，带一点折耳特征。三格分别为键盘、尼龙弦吉他、架子鼓；没有靠耳机、衣服或漂浮音符证明它是乐手。

音乐感来自行为：键盘格视线落在琴键，一手落键、一手抬起；吉他格左侧爪接触音孔/琴弦，另一爪扶琴颈；鼓格两爪持短鼓棒，面向鼓面，左右动作不同。相比目前的整齐双拳，它更像在做一件具体的事。构图以猫和乐器为主，不靠摆满卧室道具补气氛。

## 实际观图后的优点与不足

优点：

1. 圆脸与短身更有软团感，胸毛和弯耳可以作为缩小时仍能保留的识别点；不依赖高亮玻璃眼。
2. 三格确实形成演奏关系，前爪高低与头部朝向不再完全镜像。
3. 琴键、琴颈与鼓面的接触意图比原生产图明确；暖木吉他与鼠尾草绿乐器配色协调。

不足，交给交叉评审而不是掩盖：

1. 原意是困困而专注，但生成的半闭眼呈斜角，可能被读为“很酷、漫不经心”或轻微挑眉；尚未完全达到温柔、不设防的目标。不可直接宣称可爱度已经改善。
2. 折耳的左右侧在三格之间有漂移。毛色/胸毛/眼色整体接近同一身份，但不能把这张概念板当成严格身份一致的生产设定图。
3. 仍有较细的 3D 毛发和金属鼓件，精细度比原画没有减少到特别简练的程度；小尺寸时须重新看剪影，不能只看大图。
4. 第三格右侧镲片/支架贴边，未完全满足所有乐器留白；鼓格脚部被鼓遮挡，不应拿来直接提取完整身体。
5. 三格站姿、坐姿与遮挡不同，不是可直接套同一锚点的组件包；不能把整张图轻晃当作分层演奏已经完成。

## 2.5D 可实施性

如果方向被选中，保留“团子猫 + 小胸毛 + 演奏注意力”的核心，先固定折耳侧与更柔和的眼神。再单独制作正面 head/body/left-paw/right-paw 透明组件，沿用当前四层 rig 和左右重触发机制。乐器仍可用现有 SVG，需按实际接触点调布局；无需为此引入 3D 模型或骨骼框架。

此图适合作为美术方向与三种动作关系参考；不应直接把三格裁下部署，因为它不是透明 atlas，也没有补齐被遮住的身体/手臂。现运行时头部是包含眼嘴的一层；若要真正眨眼或改变表情，仍要专门表情状态，不能声称已经独立控制眼睛。

候选判断建议：与其他方案用同一显示宽度比较“猫本身是否更想让人接近”“不看耳机是否仍像在演奏”“缩小后能否辨认身份和手部动作”。本方案不预先自判胜出，等待交叉评审。

## 完整生成 prompt

```text
Use case: stylized-concept
Asset type: original character concept board for a small browser music sandbox, landscape triptych.
Primary request: ONE original, very cute bedroom-musician kitten, with exactly the same identity repeated in THREE equal-width panels: left playing a small keyboard, middle gently playing a nylon-string acoustic guitar, right playing a small real drum kit. No writing anywhere.
Character identity: a soft warm-charcoal kitten shaped like a slightly squashed mochi dumpling; broad round cheeks, tiny rounded triangular ears with one ear tip gently bent, short muzzle, tiny cocoa nose, relaxed honey-amber eyes with soft upper eyelids and small understated highlights, a small ivory crescent-shaped chest tuft. Short rounded mitten paws with very shallow toe divisions, short soft forearms, a comfortably plump body, curled tail. Warm, shy and absorbed in making music, slightly sleepy but concentrating. The charm must come from believable musical attention and posture, not from headphones or costumes. NO headphones, hat, sunglasses, jewelry, or clothing. Avoid enormous shiny glass eyes, photorealistic fur, long human-like fingers, heroic posing or symmetrical raised boxing fists.
Style/medium: tactile soft felt and brushed plush, restrained 2.5D animation-friendly stylization, simplified memorable silhouette, gentle illustrated material rendering, not a glossy premium figurine. Subtle fur texture should support broad shapes, not obscure them.
Composition/framing: three parallel panels of exactly the same size, shared plain warm cream background, shared baseline, same near-frontal camera and character scale, each entire kitten and instrument fully visible with space around paws. The kitten's head is large but cheeks stay broad and ears short. Clear separation of head, torso and independent left/right forepaws suitable for a later layered 2.5D rig; this is a concept board, NOT a sprite atlas.
Musical action: LEFT kitten leans slightly toward a muted-sage keyboard with a correctly grouped black-key pattern; its eyes attend to the keys, one paw physically depressing a key while the other hovers just above a different key, elbows tucked. CENTER same kitten sits comfortably with a small honey-wood six-string guitar across its lap, neck to viewer's right; one paw touches the fretboard, the other is just brushing the strings over the sound hole, instrument supported against its belly. RIGHT same kitten has a compact sage-and-cream drum set with kick, snare and small cymbal; two short sticks held naturally by paws, one stick visibly contacting the snare and the other poised toward the cymbal; drum surfaces and contact points readable. Tiny differences of head tilt and paw heights make each pose feel absorbed and alive.
Lighting/mood: soft warm diffuse bedroom morning light, cozy and unhurried, small grounding shadows only.
Constraints: exactly three depictions of one consistent kitten, exactly one instrument setup per panel, no additional characters, no logos, no watermark, no labels, no text, no decorative floating musical notes. Original design, no existing franchise character.
```

