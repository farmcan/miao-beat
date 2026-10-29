# 八键道具导出往返 · 独立 craft 复核

2026-10-30。非 builder，仅查看已生成结果、读取JSON／GLB结构及计算字节hash；没有导入、修改或渲染新源。

**GO，仅签署这个静态乐器道具可作为作者交接资产打包复用。** 本次往返预览未见阻止交接的新工艺退化。这不签署猫、手部装配、演奏、网页接入或完整机械安全；完整角色的既有HOLD保持不变。

实际打开 `artifacts/miao-eight-key-prop-probe-2026-10-30/prop-export/prop-reimport-three-quarter.png`，对照本人前次逐张看过的彩色全景／3Q／键前后低角，并重新打开 `color-gate/key-rear.png`。此次只有一个道具重导3Q，不冒称又完成了六机位重导检查。

## 看到的结果

- 八白键和分成两组的五黑键保留；每个键的边、圆角和独立间隔可读，没有新丢键、挤成一块、错层或比例突变。
- 象牙白／石墨黑键与灰绿壳仍分离，键面不是无细节的过曝白或黑块。壳前缘的平顺高光、厚度和侧角连续，没有新faceting、塌角或破面。
- 两个旋钮仍是独立圆柱帽，顶部白指标仍在各自帽面附近，未见掉到远处或整体悬空；无原色纹理丢失后通体变灰／变黑的退化。
- 键底与壳体之间的窄暗缝继续存在，没有在这个3Q中变成明显的宽亮洞或整排漂浮。原彩色低角的静态GO仍只覆盖原图组；此次单视角不能增强为对不可见安装结构的证明。

## 本人可复查的文件事实

`eight-key-cc0-prop.glb`实际为 **214,480字节**，SHA256 `d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6`。本人直接解析GLB JSON：有效v2 header，18 nodes／18 meshes，索引总计5,560 triangles，3 materials，4张图均以bufferView内嵌，无外部buffer URI；没有skins、animations、cameras或灯光扩展。18个名称恰为八白键、五黑键、原壳、两旋钮和两指标，没有猫／桌／rig节点。

最小native `eight-key-cc0-prop-native36.blend`的实际SHA匹配回执 `a37df130055401bcadfb2e7096763bfd5685143235873aeb1c92e77fd44bf150`。已读 `minimal-native-verification.json` 与 `reimport-verification.json`；原色scene SHA `8bd535e7…`前后相同、原世界布局／pitch和mesh往返误差0、native禁脚本复开、无Text等是builder执行回执，本人未重跑Blender，不以这些数字替代上述实际看图。

许可沿已核对的CC0乐器来源与修改记录交接；本复核只签运输／工艺，没有新增或扩大模型使用许可。包内应保留原来源、修改说明、note-map与已知边界。

## 明确保留

源黑白键内部安装交叠与near-boundary unknown没有被此次导出修复；matched-proxy也不是直接RENDER depsgraph证明。无hinge／key action、无按压或连续碰撞测试，不证明八键均可弹或1.5mm行程可见。道具无猫和双手，属于制作素材，**不是**符合完整猫／手／琴同帧约束的生产角色画面。此次GO不解除身份／精致度HOLD，也不授权扩动作。
