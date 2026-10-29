# C62：宽形先 Smooth、短趾缝最后刻，单候选失败

2026-10-29。C58 冻结，本轮单独存放在 `design/character-sculpt-v2/c62/` 与 `artifacts/character-palm-sculpt-c62/`。唯一基底仍为 C52，SHA `630c27d7de8d94f0fb85201e0a216bb7055c223bb85b6d05b704fd6ba0ad40bc`。只有一个主候选，未做深度扫描、第二候选、public 修改、绑定或动画。

## 固定顺序与像素预核验

按父任务指出的 C58 混因重排：先完成宽掌 Grab/inflate 与 4 次 .20 加权 Smooth，再读取实际最终表面法线，最后刻两条短 crease，不再整体 Smooth。旧 `frontY` 乘子不参与最后 crease。原图、C58 与 C52 已实际看过，本轮沿用相同原图三短趾目标。

末端 web 沿掌轴回收 .030u；法线 crease 峰值 .028u、半径 .030u（C52 .010u 网格上每半径 3 cells）、两中心横轴 -.063/.060u，纵轴中心 .215u/半长 .100u。先写 `main-detail-preflight.json` 后才应用字段。实际 matched 相机 scale 4.200276u：512 整图中 .030u web 正面投影 3.65px、3Q 3.04px；两缝完整宽投影 7.30/7.19px，中心间距约 15px。掌 crop scale 1.4u，web 10.96/9.19px。法线深度是光照形变，未冒充可见缝宽。实际 crease 峰值 .0279808u，未被旧前表面深度因子减半。

## 实际图与结论

已逐张实际打开完整 `main-gray-front.png`、`main-gray-three-quarter.png`，再打开 `main-gray-palm-front.png`、`main-gray-palm-three-quarter.png`。两条凹口在 3Q 末端轮廓比 C58 可辨，但正面第二缝附近出现偏尖捏皱阴影。新鲜几何审计确认它是折叠，不能当作细节完成：

- 全身非邻接三角 self：75→127，新增右掌 52 对。
- 受影响三角 normal reversal：57。
- 6668 顶点实际变化，最大位移 .0974575u。
- body 拓扑仍 297850v/297848f、1 connected component、0 boundary/nonmanifold，但这不抵消 self 与翻面。
- body mask 外逐值 exact；全部 94 个非 body 对象 exact；旧 C35 INT IDs 保持 0。只增加 `C62 source C52 vertex index plus1`。

**C62 几何与艺术均失败，不得合并、绑定或交付。** 只保留失败证据与参数、阶段数组。无第二候选。

已存阶段的纯只读因果分离进一步确认：宽形+4 Smooth self75/新增0/翻面0；仅加同一 .030u web 仍 self75/新增0/翻面0；只加同一法线 crease 则 self124/新增49/翻面29；最终两字段叠加 self127/新增52/翻面57。最终 52 对全部有实际边/三角相交段 >1e-6u。折叠集中在掌轴 s=.138–.178u、横轴 t=-.094–-.039u 的一条缝，而不是全掌或木体。该证据将主要失败定位到 .028u 法线 crease 在现有局部表面上的回折；web 单独并未产生 self。没有据此改参数或产出另一形状。

## 旧木体穿入的局部读数归因

对本轮变化点使用实际 evaluated 木体三方向 closed-solid parity，保留 mixed votes 为 unknown。rosewood 的旧内部 53 点全部在正 Y 背壳，source normal_y=.609–.742；source x[-.666,-.538]、y[-.950,-.934]、z[1.660,1.815]，掌轴 s=.0207–.0546u。soundboard 的旧内部 103 点同样全部正 Y 背壳，normal_y=.563–.742；x[-.676,-.524]、y[-.965,-.944]、z[1.650,1.845]，s=.0152–.0721u。

这两组均位于按掌轴定义的中央后表面，**没有任何 distal s>.14u 的趾尖点**。本轮对这两组的最大位移分别只有 .00000368u/.0000394u，inside 均保持 53/103，未新增已确认木内点。不能把它们写成“本轮新趾尖穿琴”，也不能忽略原始后表面与木体的实际相交。C52 已失去原始 anatomical face provenance，不能仅由几何轴强行声明其全部属于 torso；坐标、法线、逐点 C52 index 已保留，可由后续实际局部视图进一步定位。

实际 affected triangle intersections：rosewood 71→71、soundboard 141→141；六弦管无相交。未把“未新增木体穿入”写成接触 pass，连续运动与静态支持目标也未验证。

## 文件

失败 native `artifacts/character-palm-sculpt-c62/miao-c62-main-local-palm-study.blend`，SHA `1ee98ee509f7b685ca2be10cb1df3d729b179b68ccc360f350f215560310289a`。`main-C52-indexed-palm-delta.npz` 包含原始 co、宽形 smooth 后 co、最终实际 co、最终表面法线、web/crease 场与精确 C52 index；这些是失败诊断，不是可直接合并的进展。

构建 `main-receipt.json`、实际审计 `main-fresh-geometry-audit.json`、纯只读阶段归因 `detail-fold-causal-attribution.json`。阶段归因只计算已存字段分别作用的三角 self/normal 读数，不生成新 native、渲染或参数候选。未做新独立艺术评审；几何 P0 已拦截。所有文件仅本机，未 commit 或发布。
