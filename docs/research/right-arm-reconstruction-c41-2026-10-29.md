# C41 右臂 source-boundary / 完整截面 loft 可行性预检

结论：**局部边界共享、躯干补面和 source 身份保留可行；本次完整草模几何与视觉仍失败。** 不是角色完成、灰模通过或动作资产。C35/C37/C39 全部冻结，C41 没对全身调用 Manifold。

## 同一次局部 source cut

基准 C35，全部590793点先有唯一 `Miao_C35_vertex_id = 原C35 index+1`（包含5359个 C23 source0 左手新点）。删面条件一次声明：每个原面全部顶点满足 x<-.205, y<.055, z1.455..2.405。91506个面被选，真实保留边界 **808边/808点，一个degree2闭环，无分叉**。旧融合背侧116自交区完整位于被替换片内。

仅 BMesh 局部删面和清除无面孤点；剩499690原点，全部原坐标 bit-exact、canonical唯一。头z>=2.43、所有x>0原点与左C355359点全部保留；全部吉他几何/变换/可见性独立读回 exact。未发生C39那12个头点的全局简化。

两张 `diagnostic-open-cut-full-*.png` 是开切口诊断，不是完整皮肤；实际打开看过。不能把这种孔洞中间态当角色交付。

## 躯干 front patch / 肩内环参数化

808点是弯曲躯干front/side边界，在PCA平面直接径向桥接会局部负sector；因此未强行径向连环。用未受右臂污染的躯干背侧横截面拟合 rx(z)/ry(z)，在实际(theta,z)图中建外808边、肩内64边的带孔域。SciPy Delaunay初始缺1条内约束边，按明确约束执行 **2次合法edge flip**，最终872条边全部存在，缺边0/多边0，4772个三角面。

躯干采用截面 superellipse 曲面，外边界用正权图Laplace调和修正，原边坐标精确固定，最大边界修正 .0113198002u。全部实际3D补面三角法线与解析 dθ×dz 同向，非正数0，最小cross-dot **3.07416896e-7**。这些是参数补面的几何可行性证据，不代表所有新肢体截面已可用。

已复用本机验证过的 SciPy1.17.1 / NumPy / BSD许可运行时和项目 pinned MIT Blender audit/retopo helpers；无新服务或现金支出。所有版本来源/许可证仍指向既有 `artifacts/c29-qp-setup/`。

## 完整连接草模

同一个 body mesh 内，补面真实肩内64环直接共享到上臂→肘→前臂变截面loft；掌端为32列front/back皮肤，三个趾根闭环22/24/22点，邻趾根共享web边，不是独立趾物体。所有新点canonical与原source点ID为0；保留点身份和原坐标都exact。

输出504283v/506378f，新增4593点，保留499690点；component1、boundary0、nonmanifold0、Euler2、signed volume6.5139026。原点/新增点显式map见 `loft-source-output-map.npz`。此结构有真实前臂背面与躯干前皮，不是内壳；例如 XZ=(-.9,1.9)，ray层为 armfront -1.36307、armback -1.11754、torsofront -.36621、bodyback+.42278Y，存在开放负空间。该空隙在视觉上仍过大，不可据此称贴近原图。

## 实际失败门槛与归因

- new skin 对完整body实际非邻接三角自交 **172**：arm-arm156、arm-toe16；torso patch/肩根/保留皮肤之间没有这批self。
- 按交对bbox中心粗分：肘103、前臂49、掌/趾根20。完整pair faces/regions/bbox均在 `readback-attribution.json`，无需再扩QP或在C41上扫半径。
- Actual surface intersections：soundboard0、neck0、fretboard0、六弦tube全部0。**rosewood18对，全部来自躯干补面region1**，bbox x[-.396746,-.205729], y[-.654630,-.643964], z[1.462307,1.555016]；arm与toe region2/3对wood/tubes均0。
- 实际wood parity新点：rosewood11 inside、1 ambiguous；其余木件0/0。不能放行 ambiguous，也不能用surface0掩盖inside。
- 六弦最近toe-vertex-to-actual-tube采样 [.138699,.103393,.072058,.046397,.0337932,.0371837]u，最近第5弦 .0337932 在idle目标 .02–.04 内；不是六弦全压、也不是完整连续距离证明或动作路径通过。
- 局部 winding flip0、zero-area0；这不等于self0。

## 实际灰图与明确视觉拒绝

同一冻结完整草模native渲染并实际打开 `diagnostic-shared-root-full-front.png` 与 `...three-quarter.png`。root也独立打开确认：C39琴形楔口消失，完整前后表面和负空间成立，但上/前臂偏细直，肘折像焊缝；掌端是平切袖口伸出3根stub，偏离原图连续丰满圆掌、浅分缝短圆趾。腋下空隙也不能继续扩大。**视觉失败，停止C41数值打磨。**

下一 C46 必须先在原 idle 上标注肩→肘→掌根→三趾尖的投影轮廓和截面宽厚；可以复用C41共享拼接方法，不能复用本次细管+平袖口形态。先恢复完整灰图形态，再精查局部误差，不把碰撞采样合格换成艺术通过。

## 冻结证据与重现顺序

- `design/character-sculpt-v2/right-arm-reconstruction-c41.py`：唯一source cut及open native。
- `right-arm-c41-chart.py`：既有隔离venv执行，参数域约束三角化与调和补面。
- `right-arm-c41-loft-preflight.py`：同一次cut的连接草模；`right-arm-c41-readback.py`：只读source/guitar/self/wood读回。
- 完整草模native SHA256：`0f5660c180f5b5f701f369ed917328f27f6985c7086561af7b54c60e113e2813`。
- 不覆盖最初open-cut receipt；最终草模用 `loft-preflight-receipt.json`，独立读回用 `readback-attribution.json`，统一manifest覆盖所有源/图/NPZ/receipt。

未做颜色、groom/UV绑定、rig、动画、GLB、公开发布或部署。未宣称独立三评通过。所有新skin仍属于同一真正焊接body，完整诊断图同时含猫/双臂/双爪/琴。
