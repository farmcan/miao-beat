# 候选 B：松弛即兴猫

日期：2026-10-22。独立角色概念，供多方案交叉评审；本轮仅生成一张原图并写本说明，不修改产品/runtime/exporter。使用 `imagegen` 技能 与内置 image_gen；没有使用 CLI、外部素材或旧图引用。此前查看旧概念与生产截图仅为识别问题，生成调用没有传入参考图。

## 身份与表演方向

**一只喜欢边听边弹、重心松弛的小猫乐手。** 暖灰短毛、白色下巴/胸前小块、琥珀眼、短圆爪、圆尾；没有耳机、墨镜、服装或舞台饰品。音乐感由身体略偏、头向手中乐器关注、左右手不同任务和接触点表达。

图中同一猫依次弹键盘、弹尼龙弦吉他、打小鼓组；三个画面相同奶油底与近似大小，角色身份和材质基本一致。道具也是柔和立体材质，避免旧版毛绒猫与平面粗描边道具的拼贴感。

## 原始文件与生成记录

- 工作区原图：`design/candidates/groove-cat-v1.png`
- 工作区文件：`design/candidates/groove-cat-v1.png`
- 工具原始路径：`generated_images/01a1579d-faee-7a81-985a-c50b3328dc15/exec-7097835a-e079-416d-a116-350a7a579d6b.png`
- 尺寸：2172×724；格式：PNG；字节：2,158,061。
- SHA-256：`472f59f411d540a9b438a73cda6530d9053e403fea032321ba8cb380fd7f4b96`
- 原图直接复制，未裁切、调色、抠图、修改像素或覆盖旧资产。工具模型未暴露，不臆测模型名。背景为实色奶油，不宣称透明素材。

## 实际查看后的自评

已用 view_image 打开保存后的原图；以下是静态概念审美与实施判断，不是动画测试结果。

- **有效：** 猫确实在看/照顾乐器，而不是三个模式都直视镜头。钢琴双爪一落一备，吉他拨弦与琴颈的左右任务可读，鼓有短鼓棒和具体鼓面。前臂/肩部低于旧版架起的双拳，身体有轻微不对称；无文字、水印或额外装饰。
- **身份一致性：** 三格的暖灰毛、白色口鼻/胸口、耳形和眼色一致，琴/吉他格头的倾斜与眼睑接近，鼓格眼睛更睁开。不是三只不同品种；但它们不是像素锁定的同一套rig，不能将概念板直接当动作帧。
- **需要交叉judge：** 低眼睑和斜眉也可能被读成“困/有点不屑”，尤其钢琴/吉他格，未必人人觉得可爱。这是B方案最大风险；若继续，优先减弱眉压、眼睛稍开，而不是加配饰。鼓格表情较明亮，可作其余两格的眼神校准方向。
- **接触局限：** 钢琴格的三趾偏浅色，有一点拟人小手感；鼓棒有一根贴近鼓边，精确鼓面触点还需生产校准。吉他前臂与琴身重叠自然但遮挡较多，静态好看不等于能无缝拆出整臂。
- **小屏局限：** 乐器细节和鼓支架丰富，缩到现有小舞台可能过密。生产版应保留接触点、简化支架/键数与皮毛微细节，不能直接把整张三格图缩到手机里当角色。

## 轻量动画可实施性

该图可作美术和姿态目标，**不是现成分层素材**。四组件思路可复用，但不能把三个不同抱持姿态强行拉扯成同一只前臂。

1. 先选一个固定相机/身体主姿态，输出中立头/身与完整前臂补全；钢琴、吉他、鼓分别保留自己的基础手位。头部与身体身份共用，乐器独立；吉他拨弦臂、鼓棒作为小图层。
2. 键盘只需短接触与回弹，吉他拨弦沿弦束扫过、另一爪稳定琴颈，鼓棒在对应鼓面/镲片到点后回弹。身体可以小幅重心变化，但不能整猫左右晃冒充演奏。
3. 乐器、爪/棒、头先按统一画布/锚点生产，补齐肩根与乐器后方被遮住的区域，再谈前端插值。半闭眼属于烘焙头图；真正眨眼/看向仍需局部眼部状态，不能靠压缩整头。
4. 建议先做同一身份6–8秒“键盘两下→停半拍→抬头回应”小样，验证松弛是否可爱，再补另外两种；不先批量生成动作包。

取舍：B比旧版更有听音乐的姿态，但牺牲了部分“大眼直视”的幼态亲近感。与其他候选比较时，应重点问“这是专注享受音乐，还是困/嫌弃”，而不是只比毛发渲染精细程度。是否胜出留待交叉评审，本说明不自称最优方案。

## 完整生成 prompt

```text
Use case: stylized-concept.
Asset type: original character direction B, a single wide triptych concept board for a lightweight browser music toy.
Primary request: design an original adorable cat musician with relaxed improvisational groove. Show the EXACT SAME cat identity in THREE equally wide side-by-side panels: piano on the left, nylon-string guitar in the middle, compact drum kit on the right. One finished image, not three separate images. No text anywhere.
Character identity: a compact round-bodied smoky warm-grey cat, a tiny off-white chin and small off-white chest crescent, soft short plush fur rather than hyper-detailed long hair, peach inner ears, small warm amber eyes with expressive lids, a tiny charcoal nose, rounded short paws, short rounded muzzle and a plump curved tail. Consistent face, fur markings, proportions and scale in all three panels. The cat is comfortably cute, not a glamorous performer, smug adult, or wide-eyed passive baby.
Musical acting: make the cat visibly listening to and making music through BODY WEIGHT, shoulders, eye focus, and clear instrument contact, not through accessories. A gentle off-center seated weight, relaxed low shoulders, slight head tilt and an engaged soft-eyed expression. Each panel has a different meaningful playing gesture. Keep its eyes primarily focused on the instrument or its paw, with a tiny contented expression; no uniform straight-ahead stare.
Left piano: a small softly rendered keyboard with readable white and black keys, cat's viewer-left paw visibly touching a white key at the fingertip, viewer-right paw lightly poised above another key, relaxed wrists, a little head-down listening posture and a softly swaying tail.
Middle guitar: a small realistic-proportioned warm wood nylon-string acoustic guitar resting against its body; viewer-left paw is clearly brushing the strings above the SOUND HOLE, viewer-right paw supports the NECK farther right, each arm has a readable silhouette. The cat gently leans into the rhythm with soft half-lidded enjoyment, not a smile pasted on.
Right drums: a compact sage and warm-wood drum set, short simple drumsticks held naturally in its short round paws, one stick tip making clear contact with the snare while the other is raised a little over a small cymbal. A small side-to-side weight shift and alert but relaxed expression; distinct hands and visible contact point, not both fists floating in the same place.
Style: cohesive polished stylized 3D illustration with sculpted storybook warmth and subtle tactile fur; simple clean forms readable at small website sizes. Instruments share the cat's soft material rendering, gentle bevels, and light, not flat black-outline clipart.
Composition: three parallel equal-size vignettes on the SAME pale warm cream background, equal ground line, identical camera height and restrained near-frontal slight three-quarter angle, full cat and entire instrument visible in each panel, equal cat head size, generous clean margins and separation, no overlapping panels or close-up crop. Soft studio light and small grounding shadows. Keep head, torso, left forearm/paw, right forearm/paw and instruments visually separable with sensible overlaps for later 2.5D layered animation. This is a character concept comparison sheet, not an already-rigged asset atlas.
Constraints: completely original cat design, no imitation of a named existing character, no sunglasses, no headphones, no hat, no clothes, no jewelry, no stage, no audience, no floating musical-note graphics, no branding, no letters, no panel labels, no watermark. Do not add extra limbs or human fingers. Preserve gentle groove and appealing silhouette rather than flamboyant posing.
```

