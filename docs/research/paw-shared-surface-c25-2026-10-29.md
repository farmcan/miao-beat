# C25 shared surface band：真实几何进展，严格失败与诊断例外分开记录

2026-10-29。范围仅按弦爪局部共享带；保留 C23r2 及其三份视觉拒绝历史。C25 是新拓扑对应／曲面构造方法，不继续改变旧 Hermite 参数或移动减边 strip。

## 修区、锁区和映射

- 保留原臂根、全部 C8 源点及 r2 新腕到 u=.85 的 50 点环。其后显式单调 50→42 对应：4 个分离的3→1单元，消耗分配明确写入 `mapping-and-lock-plan.json`，不再由 shortest-spoke 搜索猜相位。
- 8 个减边新增点首先由已知 `(u,f)` 参数曲面直接求值，不用 helper 的空间弦中点。其后至实际 upper 的各环均42点、逐点对应。面数未增加。
- 共享公平化区跨过旧 V=-.07 人工切面：u>.85 新腕＋实际 C11 上掌 V<.005 的基部。一次固定40轮 Taubin(.45,-.47)，位移上限 .024u；实际1007点可动、最大位移 .0212058u。
- 锁定541个上掌/趾尖点（V>=.005）、原源口/臂根、三指定趾腹的实际命中面全部顶点及半径.023u邻域。锁区 bit-exact。掌体沿V的范围前后完全相同，避免把掌继续拉长成卵袋。
- 吉他、声明弦／指板目标世界坐标不变。原真实 hold 缺口不是“被锁定为通过”；仍须独立接触验收。

## 一次局部几何预检与严格失败

`build.log` / `local-preflight.json`：5359点/5257面，单连通，唯一198根边开口，零自交/翻面/零面积/重复点；99.7% quad。保留的早期减边和整只旧角色不在本次重建范围。

原脚本额外预设趾腹射线命中位移必须<1e-6u。实际局部 `BVHTree.FromPolygons` 对三趾产生7.39098e-6/0/1.31130e-6u，故**原严格receipt失败并停止**，保存 `diagnostic-failed-local.blend`；原 `receipt.json` 未改，SHA `0fed932bb427ba8818d6f23590f8c780d683856c2cfede2bcaca1d1adce32d19`。之前一次输入锁区解析在几何预检前因局部BVH与保存body的射线差异停止，日志 `initialization-lock-probe-failure.log` 保留；改用保存native的真实face/upper-id读取后，几何只求解／预检了一次。

## 只读核验后的独立工程例外

`locked-face-triangulation-diagnostic.json` 证明三处face的4个顶点bit-exact、循环次序也相同。原native的evaluated BVH与局部FromPolygons选择同一非平面quad的不同对角线；两种三角化的解析交点复现上述差异。768px、inside ortho1.25，最大世界误差的保守投影上界 **.004541px**；仅原.05u接触缺口的 .014782%。

父任务明确允许仅在锁区exact、自交/翻面0且投影<.01px时保存独立例外并渲诊断图。`engineering-exception.json` 写明授权、误差、来源与边界；没有放宽原严格门槛或覆盖其失败receipt。`executed-diagnostic-render.py` 只把已冻结patch按198源口身份焊进完整猫场景，**不再fair或改任何patch/source顶点**。实际邻接collar再次self0/flipped0，完整590793点/590465面、单连通闭合，才保存并渲两图。

完整诊断native：`miao-c25-shared-surface-diagnostic.blend`，SHA `59c4a6c37594209e740f0b41b148b11d41776c015b4e1e40aabb8bf4c49be8db`。front和inside均由这一冻结native对应场景输出；front完整展示连通猫/双爪/吉他，inside只是作者诊断crop，不作生产资产。

## 实看与接触边界

Builder实际打开批准idle、r2三图和C25 front/inside：原连续硬横唇、左黑夹点和明显纵线显著减弱，趾根成为较软的小鼓出；短圆趾及下掌尺寸保持。仍有小趾根起伏，掌趾比例是否自然、是否真正清除P0须身份／craft／motion三角色独立判断。builder不自放行，数值不代替美术。

同一完整诊断native的 `contact-audit.json` 使用实际六弦Bezier与完整body `FromObject` BVH：29背hit/7miss/3负gap；三指定趾腹gap逐值等于r2：-.0067011239/+ .0537173627/-.0073801400u；两下缘支持亦逐值等于r2：+.0485792616/+.0698318630u。说明锁定目标实际保留，同时**原hold P0并未修复**。局部FromPolygons严格门槛失败不删除；实际native数据提供不同三角化路径的补充证据。有限射线不是全域碰撞或动画证明。

## 使用和未验证

代码 `design/character-sculpt-v2/paw-shared-surface-c25.py`、独立诊断renderer、只读contact audit均冻结于本目录；manifest逐文件SHA。复用vendored Scenario `bx_audit.py`，MIT，固定commit `d44410f058991f677ccf733a8e86ce95110857eb`；未修改vendor，无云服务或额外费用。

没有第二几何候选、颜色、毛发改动、rig、动画、GLB、引擎或部署。旧UV/groom/shape绑定失效；既有整角色P0不因本局部改善豁免。此目录是带严格失败与工程例外证据的技术研究，不是完成的美术优化或生产交付。
