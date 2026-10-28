# D0.3 · 实际眼睑 Shape Key 小样：关键姿态未通过

2026-10-28。本项是有界失败记录，可复用控制与验证源码，**不是自然眨眼成品**。两轮有目的视觉修复已经用完；没有生成最终短片；本项仅作为失败研究归档，不用于正式角色或生产素材。C5 母版与 D0.2 输入未改。

## 实际结果

输入 `artifacts/character-sculpt-d0-groom/baseline-attached.blend`，SHA256 `71dd111471361f5b748dd921ee48845619212d6cfd135b07af52e0e9b15b460f`。Blender 5.2.3 LTS。

输出均在本地 `artifacts/character-sculpt-d0-blink/`：

- `open.png`、`half.png`、`closed.png`：512px、Cycles 32 samples、seed17，同一固定相机、完整猫/爪/琴场景。
- `miao-d0-blink-study.blend`：可编辑三维眼睑小样，SHA256 `f3e0223bc0cb21a5b7f113bcf68eeb5ef56a01dc6bb1d369318a802e584c34f7`。
- `receipt.json`、`final-receipt.json`：真实输入/输出 hash、点数、失败历史、渲染计数。
- `geometry-check.json`：已修正世界/局部坐标变换的 9 档正面射线遮挡抽样。

两侧原始上睑控制笼各 245 点，经原 Subdivision 求值与冻结 3281 点逐坐标误差 **0**；保留原 open 网格，新增 8 个包覆式修正 Shape Keys。新增实际三维下睑皮面从脸内升起，与上睑相接；眼球及虹膜未隐藏、缩放、移动，图片未修图。眼睑用真实眼白、突出虹膜前包络生成，非平面眼片。

最终 open 与 D0.2 原静止图有 **8/262144** 像素的 RGB 差异，最大 **1/255**，平均 RGBA **0.0000076294/255**；这是加下睑后实际渲染结果，不能写成全图完全一致。猫体、手爪、琴、眼白、虹膜与 groom 原始几何 hash 保持。官方 BindUV 查询仍为 **180000 有效、0 无效**；720000 毛点 `miao_rest_position` 求值 hash 保持 `7446e079f4e27239ba9c195f1db388a0e2f515a3a2c8269e80eb79693337b419`。

**最终失败**：闭眼皮面仍像突出的橘色眼帽，缺乏自然柔和的睑缘。每眼 81×81 正面世界射线网格，Blink=1 首命中仍有左白眼 1、右白眼 5、左右虹膜各 33，共 **72** 个可见眼样本。此有限抽样不是完整碰撞证明；这些反例已经足够阻止交付。不能以多数样本被挡住替代自然闭合。

## 如何查看与操作

打开输出 `.blend`，选对象 **`D0 / Blink control`** → Object Properties → Custom Properties → **`Blink`**：0 为 open，0.5 为 half，1 为 closed。真实 Shape Key 通过驱动器读取此值；不直接手改各修正 Key 权重。两侧上睑和新增下睑都参与三维形变。原身体局部测试 Shape Key 保持 0。

该文件留作诊断，closed 不可作为新生产素材。默认保存 Blink=0；没有最终动画。眼睛不应因本试验的部分技术成功就被接受。

## 有界尝试与错误记录

1. `attempt-0-scalar-error/`：初始化计算误用了数组而非 `r[k]`，在渲染前报错；修正后重跑，无 GPU 图。
2. `attempt-1-upper-only/`：真实 3 图。上睑覆盖整眼形成橘球，顶部露白，停止短片。
3. 第 1 次视觉修复，保存在 `attempt-2-seam-gap/`：新增真实下睑，渲染 3 图，观感改善但缝隙仍漏眼。开始短片后发现自检脚本错误：眼对象含平移，BVH 是对象局部空间却用世界射线，导致 open 也错误报告零眼命中。旧结果明确保留为 **`geometry-check.INVALID-local-space.json`**，不得引用为通过。
4. 修正射线为逐对象局部空间求交，再转换回世界比较。该轮闭合仍有 236 个可见眼样本，立即终止短片；只留下 5 张完整场景帧，未编码视频。
5. 第 2 次且最后视觉修复：扩大下睑包覆并重叠睑缘，再渲 3 图。最终仍有 72 个反例，且眼帽感复发；按停止条件结束。

总计 **14 张已完成的实际 GPU 图片**：3+3+5+3。终止短片时可能有下一张 render 在执行，未完成调用不计入 14 张；没有完整最终短片。失败 clip 的 5 张帧均是完整场景渲染，未把身体底图与单眼叠片。

## 复现

从仓库根目录执行（会重建最终失败候选，3 次真实渲染）：

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python design/character-sculpt-v2/d0-blink-study.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python design/character-sculpt-v2/d0-blink-geometry-check.py
```

`--clip` 已加失败门：只有关键姿态 gate 明确通过才允许运行，目前 receipt 为 false，会拒绝；不能因读到这个参数就把当前失败形态扩为动画。最终生成时运行的源码快照与失败各轮源码保留在 artifacts。几何检查对眼对象实际 `matrix_world` 做射线变换，避免本次已发现的误判。

## 下一项建议与边界

先单独研究 C5 眼白/虹膜前凸量、眼窝深度和上下睑连续体积；必要时在副本小幅后嵌真实眼结构并重渲 open 与当前参考做对照，再重新设计睑缘。不要以覆盖更多橘色皮面代替眼窝设计，也不要把眼球藏掉或缩为 0。该下一项尚未执行。

本项没有 rig、头动、自然拨弦、闭开短片、浏览器接线或导出验收；没有证明所有毛发 shader 插值或完整 anti-swim。资产 builder 的失败判断不是三名独立评审，最终仍由其他角色查看实际图决定后续方向。
