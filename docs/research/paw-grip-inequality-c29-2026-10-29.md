# C29：外部接触／琴体约束可解，新增上掌自穿，未渲图

2026-10-29。在C25同mesh、同五目标上使用本地OSQP稀疏凸QP；无拓扑、目标或颜色改变。一次固定方法的主动集可行性求解，不是C27参数候选；最多8次真实交点cut更新，实际只用2次。

## 固定定义与结果

3089个标量自由度：upper沿Y、wrist沿实际V；587704锁点含585434原C8源点、原可见前掌Y<=-1.17及根V<=-.30，全部bit-exact。位移界.095u，实际max=.0774860u。物理Laplace位移能量＋.005位置正则；五个实际命中三角重心等式要求gap=.0008u。

外侧不等式来自actual evaluated指板／neck／六弦tube BVH，外退方向固定为toe -Y、wrist -V，不能投影到琴背。845顶点实际BVH约束、10773密集实际face约束，覆盖C27穿板的U1.30–1.48/V-.20到-.055邻域与upper接触区；初始548实际交点witness cut，补48个后总12214个不等式。不存在不可移动违反约束。

OSQP两次均solved：第0次五gap≈+.0008u、仅弦1剩10对面交；同一QP补实际witness后，第1次指板／neck／六弦actual面交全部0。5359手点的双方向parity：指板和neck内部点0、分歧0。五个目标世界坐标逐值不变，法线方向及实际源身份满足预设；掌托从actual下缘+.08V观察，避免C27旧ray origin掉入掌内。以上是外部接触与障碍约束的工程进展，不是握姿美术通过。

## 真正失败：49对手部自身面交

最终actual hand＋collar审计self49、flipped0；完整590793点/590465面、单连通闭合。因为self门槛未过，**没有front/inside灰图**。`self-intersection-attribution.json`读取冻结native后逐对核验：全部49对均为upper/source2↔upper/source2；48对在实际loop triangles确认有>1e-6u交线，1对仍标tangency/epsilon未决，绝不删作self0。

交对集中中趾及附近upper：U约1.34–1.38、V约-.017到+.006的样本最明显。若干面与原法线dot仍为正（.23至接近1），说明flip0确实不能排除自穿。实际源polygon索引、顶点、交点、交线跨度、原face center和normal变化均逐对留证；不是根据QP日志推测。

缺失的约束类是skin-skin分离。当前1D方向位移加外部障碍限制能闭合五目标且清除琴弦穿入，但未阻止中趾表面相互越过；不得把外部collision0当总体通过，也不声称原姿势不可能。

## 冻结与下一约束类

失败native `diagnostic-c29-infeasible-or-collision.blend` SHA `d03a4043465acd321195f2986ff4e6fb4a1f5ed5bc26002cc30043a6e6da2ec3`。所有NPZ、QP结果/残差、约束来源、5真实ray、锁区、位移、49自交原始细节和源码哈希保留。C25未改；C27历史不覆盖。

建议下一新方法在同QP补真实skin-skin主动分离切面：对相交两三角，在C25相同源顶点三角的法线/edge×edge/共面面内轴中找可靠正间隙，固定原安全侧，约束3×3顶点投影保持小正隙。若原无可靠正gap则记来源歧义或条件冲突，不任意翻面/推出。该约束类将另编号C32；本C29未实施第二候选。

求解器是隔离本地venv中的OSQP1.1.1、SciPy1.17.1、Python3.14.2；Blender通过NPZ调用外部Python，无ABI混装、hosted service或新增费用。官方wheel来源/SHA及本地license证据位于`artifacts/c29-qp-setup/receipt.json`和licenses/，不把依赖/原角色的权利当原创。复用Scenario MIT审计helper固定commit d44410f058991f677ccf733a8e86ce95110857eb。未改vendor，无颜色/毛发/rig/动画/GLB/引擎/部署；旧绑定失效，美术和动态未验。
