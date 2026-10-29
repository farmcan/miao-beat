# 八键成熟乐器组件 · 异机导入说明

2026-10-30。这里交接的是 **CC0 乐器本体**，不是完整猫模型或已完成演奏。它由 Innerscene [Key Forty MIDI Keyboard](https://www.innerscene.com/tools/library/3d-parts/key-forty-midi-keyboard-0d9952a4) 的原成熟几何适配：八白＋五黑、原琴壳、两原旋钮及指标。没有新造琴键/壳/手或角色网格。

[下载八键作者包](https://github.com/farmcan/miao-beat/releases/download/licensed-source-assets-2026-10-29/miao-eight-key-cc0-instrument-2026-10-30.zip)。许可证据、署名来源、原改动、重导入数据、灰/色三角色评审及transport短评随包提供。源键盘complete-file CC0覆盖模型/原PBR，项目验证脚本MIT单列；本包不含猫、桌、骨架、动作或原嵌入脚本。

## 在另一台电脑上怎么用

1. 解压后运行 `python3 design/miao-reuse-keyboard-v1/verify_review_pack.py`，逐文件核对 `PACKAGE_MANIFEST.json`、`SHA256SUMS`。不要从本包推断当前猫已获最终美术验收。
2. 推荐在Blender新文件中 **File → Import → glTF 2.0**，选 `model/eight-key-cc0-prop.glb`。GLB仅214,480字节，18mesh、5,560三角形、3PBR材质、4内嵌图；在官方3.6.23已真实重导入并拍摄诊断图，世界矩阵/边界/键面/音阶间距已对照。
3. 或使用 **File → Append**，选 `model/eight-key-cc0-prop-native36.blend` 中的scene/objects。它是176,270字节的最小data-only资产库，不含workspace/camera/light；直接打开可能出现Library file初始化提示。若当前Blender没有可用workspace，采用Append或导入GLB。不要把没有展示相机误当成模型为空。
4. 全选导入物体后 **Frame Selected**（小键盘`.`）查看；需要自己的渲染时自行布光。本体保留原装配世界坐标，没有自动放到地面或归零；整体平移/旋转请用父Empty，不逐个改键间距。
5. `model/note-map.json`列每个白/黑键的GLB node、MIDI与世界中心。白014→021是玩家视角C4→C5；从对面看猫的观众world-X升序反而是降音。不要按世界X升序直接把A→K当成升音，会反向映射。该表只有静态语义，不含按键动作或评分。

GLB SHA256：`d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6`。

最小native SHA256：`a37df130055401bcadfb2e7096763bfd5685143235873aeb1c92e77fd44bf150`。

## 验收范围与不能外推的结论

八键在完整灰/色场景各经过三个独立非builder角色实看，仅允许保留prop与准备位；导出后还有一次独立transport craft查看。完整飞行员猫与原橘猫的轮廓/表情/材质差距仍为HOLD，不能把本包叫完整角色优化交付。包内报告的完整猫场景图属于仓库研究证据，不在CC0乐器文件内；包内`model/prop-reimport-three-quarter.png`只展示道具，供作者导入检查，不作为生产猫帧。

保留源黑白键内部安装交叠与near-boundary unknown；没有完整机械、连续碰撞或键程安全证书。没有动画，未证明1.5mm行程在网页全景可见，更没证明八键手指触达。线上A/C4实验本轮未被此静态道具替换。

原模型白键14–21＋黑键10–14保留原拓扑/倒角/材质；键组world-X×3.4、琴壳world-X×.7，旋钮/指标按原组件刚体移动。单白键宽约52.33mm，白键pitch55.675mm，壳宽504mm。静态版本用于下一只合格成熟猫模板的装配，先通过整角色静态gate，再做真实操作。
