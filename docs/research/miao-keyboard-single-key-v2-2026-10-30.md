# 键盘 v2 · 一次真实单键受控动作

2026-10-30。**数值/本机完整帧已完成，待独立 motion judge；没有八键、声音输入、头动或网页产品通过结论。**

从三方默认色 GO 的 `ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6` native 只读复制。只动 `FK-Index1.L` 原生局部 X 与 `Ivory piano key.014`，双腕、其它指、右手、头身/材质/网格/高度均保持。014 后端中厚度 world-X 铰轴固定 `(.057312503,-.413000017,.322000027)m`；满前缘行程 **1.5mm**，角度 −0.767377°，没有 adaptive 缩小行程。

18°准备 → 22.052161°触键 → 23.984959°最深 → 触点释放 → 18°回位。触键段真实 render2 匹配皮肤间隙 **52.363–61.870μm**（目标50±15μm），最深邻键投影净空 **1.757175mm**。49个生产状态及数值迭代状态：全手/袖对有限键、壳、旋钮、桌新增三角交叉0；014对固定外部新增交叉0。原 white014/black010 的59对和具体增退pair、同一原白键有限实体区域分类逐状态记录：confirmed outside0，near-boundary unknown最多3点保留，不能称完整机械机构或区间连续实体无碰撞证明。直接 RENDER depsgraph 不可得，沿用 show_render/render_levels2/IsViewportFalse 匹配 proxy；Quality1/simplify=False不变。

60fps、49张完整1400²帧，样本时间0–.8s，MP4容器时长0.816667s：0–.2s静止，.2–.2333s触键，至.2833s压满，hold至.3167s，键回弹至.4167s，指回准备至.5s，静止至.8s。每个生产帧完整猫/双臂双手/全琴/承托；5张手部近景与down3Q单列诊断。新增2个actions：猫1条局部X曲线；键3location+4有效quaternion曲线，均49采样点。未增加其它动作通道。

实际查看 ready/contact/down/release/end 五张完整图、五张手诊断及down3Q，未观察到新增可见穿插/塌手/袖口断裂 P0。又查看主MP4解码全部49帧的顺序拼图，在Chrome将1×原速单次片播放到ended（currentTime=duration=.816667、1400²）。**全景动作很小，列P1/HOLD待独立判断实际可辨性与自然度**；3×慢放仅帮助检查，不用作响应通过证据。原速片无声音，不声称音画或键盘输入闭环。

顺序 Blender3.6.23 factory/disable-autoexec native重开 **PASS**：49帧FK/键变换与已审轨迹等价，最大键world矩阵误差5.96×10⁻⁸，其他骨basis全部精确不变；回位pose hash恢复 `6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b`。全部55次渲染camerahelper误差0。源SHA前后不变，衍生native SHA `cc6e1eb01fa0de2d06b66abf3fa6d7f08a71f6912ee6e4542a2bda4cd73f1e13`。回位原始RGB仅16通道值差1/255，不冒称raster逐字节相同。

保留两项执行诊断：原回位断言混比viewport0眼约束和render2 proxy（约2μm），退出proxy后world精确回位；首次native误为QUATERNION键写入无效Euler旋转曲线，原失败native/hash已保留，改为同一49个已审world矩阵的有效quaternion后重开全过。离线完整帧始终直接用world矩阵，不受该序列化错误影响；未调整动作、重搜姿势或重渲。

证据目录 `artifacts/miao-reuse-keyboard-v1/single-key-v2/`：`inspection-manifest.json`、`single-key-numeric-receipt.json`、`render-receipt.json`、`native-reopen-verification.json`、`clip-package-receipt.json`、`SHA256SUMS`；主片 `single-key-once-60fps.mp4`，诊断慢片 `single-key-once-3x-slow-DIAGNOSTIC.mp4`，native `single-key-v2-native36.blend`。CCBY猫几何/纹理、CC0键盘/桌和项目MIT脚本/新轨迹分项许可继续沿用同级 `licenses/`，原包不改。

所有 Blender 进程已退出；不扩第二次敲击、八键或新表情，等待非builder motion judge。
