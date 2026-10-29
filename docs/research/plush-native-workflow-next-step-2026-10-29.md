# C21之后：先验证短毛方向，不先把全身加密

2026-10-29。独立方法研究 `/root/gpu_route`，非builder。只读公开源码、官方文档与本机库目录；没有安装hair/shading skill、插件、云调用、生成毛发或修改原评审。

## 一个决定

**下一最便宜的单patch验证，优先做“方向”，保持C21r2短毛的长度、半径、根数与shader不动。** 原因是可见coverage稀不等于已证明根密度不足；当前实际毛并不是已经梳顺的plush guide层。先把同一批短毛的一小块从近法线竖立变为沿面流向倾斜，检验能否增加可读纤维、而不回到长刺。

这只是可证伪的下一假设，不是已生成候选，也不是“方向肯定是唯一原因”。本报告不推翻C21原毛感P0，也不把原图侧后方的真实毛流当成已知。

## 为什么从方向切入

实际已审图显示：原idle有沿曲面连续的细密短绒；C14C是短刺/暗点；C21r1/r2接近无毛控制，像平滑软胶公仔。128sample noisy仍没有足够可读连续细毛；线性hair-only AOV额头ROI mean约`.00278288`、p50=0，支持该视角可见hair响应稀，但它不是严格几何面积或全身根数测量。

本机源码有更具体的线索：`design/character-sculpt-v2/shade.py:74` 用 `roots + norm*(length*t) + 小随机bend*t²`生成原4点毛；C21只将root相对offset及radius乘`.4`（`plush-surface-diagnostic.py`）。因此长度缩小后，面对镜头的额头上许多毛接近端视，投影更像点；增加同方向细毛可能只是增加点粒。**这是几何投影推断，尚未测量每根实际投影方向。** 修改方向而不新增曲线，比先铺满全身更便宜，也更能排除“coverage只由根数决定”的假设。

## 固定上游：已读真实实现，不只看SKILL标题

固定仓库 [scenario-labs/skills@d44410f058991f677ccf733a8e86ce95110857eb](https://github.com/scenario-labs/skills/tree/d44410f058991f677ccf733a8e86ce95110857eb)，根LICENSE实际为MIT、copyright Scenario Inc.；若后续复制helper，须保留许可证/版权及固定来源。本机现有安装仅expert/sculpt/retopo；以下两个skill本次**只读上游**，没有安装。

- [scenario-blender-hair/SKILL.md](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-hair/SKILL.md)：先均匀少量guide与区域flow，再masked Interpolate增密；全密度渲染/实际姿态审查。其长毛preset不是Miao短绒配方，不能直接移植百万/m²或半径数值。
- [bx_hair.py](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-hair/scripts/bx_hair.py)，Git blob `2a9ade25985c5981887f36a78637a68a16c300cf`：实际有`add_asset`、`set_inputs`（解析UI socket且update_tag）、`count(full=True)`、`sample_roots`、`add_guides(flow=...,flow_blend=...)`、`groom_report`。`add_asset`调用Blender Essentials，而非另写毛插值器；上游自述测试于5.2.1，本机5.2.3尚未调用验证helper。
- [hair sources.md](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-hair/references/sources.md)：出处包括Daniel Bystedt的BCON2023 grooming、Kerstin Schmidbauer的BCON2025动物毛、Simon Thommes的Blender Studio程序毛。其笔记明确是字幕/讲话提炼、没有frame grabs；本次未观看全部视频，不据此宣称已验证某示例的视觉质量。
- [texturing-shading/SKILL.md](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-texturing-shading/SKILL.md) 与 [bx_materials.py](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-texturing-shading/scripts/bx_materials.py)，后者blob `674d16825dde88f6dea54133ad2b204c4429f64c`：重点是可分层mask、受控roughness与诚实光照，再bake。实际helper没有专门一键plush/velvet函数；不应把`stylized_skin`或任意噪声bump当短绒解决方案。

本次安全只读打开本机Essentials库目录：`/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/procedural_hair_node_assets.blend`，确有Interpolate/Duplicate Hair Curves、Set Hair Curve Profile、Attach Hair Curves to Surface、Trim Hair Curves。没有append到角色、没有保存/渲染；文件存在不等于已跑通Miao流程。

## 官方节点与velvet的边界

[Rotate Hair Curves](https://docs.blender.org/manual/en/5.0/modeling/geometry_nodes/hair/deformation/rotate_hair_curves.html)有Axis、Angle、Factor和Lock Ends等输入。**不能用默认根切线轴自转来冒充梳倒毛流**；需要明确倾斜轴，保root不动、Lock Ends不锁死tip。真实5.2 socket名称/行为应在试验前从本机node interface读取，不能只照5.0/5.2.1标识猜。

[Interpolate Hair Curves](https://docs.blender.org/manual/en/5.1/modeling/geometry_nodes/hair/generation/interpolate_hair_curves.html)可从guide在表面分布子毛，配Density Mask限制区域；Resting Surface与后续Deform的顺序有关。5.2上游明确新版从curves.surface/UV读取，不再照抄旧版Surface输入。它会继承guide形态，不会自动把当前法线刺毛变成正确梳理毛流。[Duplicate Hair Curves](https://docs.blender.org/manual/pt/5.1/modeling/geometry_nodes/hair/generation/duplicate_hair_curves.html)也是真实较轻的增密资产，但本轮不同时试它。

官方[Principled BSDF Sheen](https://docs.blender.org/manual/pt/5.1/render/shader_nodes/shader/principled.html)用于极小表面纤维的边缘柔反射；[Sheen BSDF](https://docs.blender.org/UATEST/manual/en/dev/render/shader_nodes/shader/sheen.html)包含传统velvet与Microfiber模型。它们是微表面散射近似，不能生成独立毛轮廓/根覆盖；应在纤维组织确认后再单独判断，不能这轮同时加sheen、换灯、加密来制造无法归因的“更软”。官方latest英文正文抓取返回工具402，搜索索引/官方旧版正文可读；没有付款或调用付费替代。

## 唯一建议的单patch试验

仅在独立诊断副本，使用128sample/AOV已定义的同一额头patch与相机：

1. **原毛复用，不新建全身groom。** 用已有root UV/表面区域选中额头中央，排除眼、眉、耳、奶油嘴和边界外毛；原4点短曲线保留。root位置、长度/半径、rest pigment、密度与shader、身体、光、相机均冻结。给区域画一个参考约束的简单沿面流向（单patch暂向额头一侧顺弧），不是猜全身解剖毛流。
2. **只改变guide方向一次。** 复用Essentials Rotate Hair Curves，经`bx_hair.add_asset/set_inputs`或同等原生节点设置明确轴：根据root法线N与所选切向T，绕`N×T`朝T倾斜；本试验预声明一次约45°的方向变化，不扫角度/长度。mask边缘平滑衰减，避免一条硬梳理边。root锚定与长度不变须实测；发生入皮/穿眼/异常tip即停，不用nearest fallback掩盖。
3. **只渲同crop：beauty noisy/denoised＋相同定义hair AOV。** 同一固定buffer条件，比较C21r2原patch；记录实际曲线/点数、root误差、角度分布和可见AOV，不要求某个均值自动达标。内部patch不是独立生产面片，也不改正式完整帧。

证伪标准：若同根数/短长度在倾斜后AOV与可读连续纤维均明显增加、未恢复针刺/硬梳理边，可支持方向是一个重要成因；若AOV增加但仍只像刻线/随机点，方向单独不足；若coverage与beauty都无实质变化，也不能继续称方向已解释稀疏。无论哪种都不自动通过plush，仍须独立实际图审查。候选只做这一项，不同时提高密度/微表面，也不将45°宣称为最终毛流。

## guide / interpolation如何复用

**应复用原生guide→mask→interpolation机制，但不是把180k全身毛当成新guide再全域倍增。** 先验证本patch原guide方向；如果方向测试之后才需要增密，可从该区域挑均匀少量guide，原生Interpolate仅在同区域分布children，保持短毛Profile、严格UV与root/rest属性验证，逐层count(full=True)。这种条件性后续不是本报告第二个候选。

现有BindUV与180k根只对既有冻结形状有已验证证据，新children不继承“全valid”结论；需明确surface/UV与原rest pigment字段传递、对应UV采样与visible-eye mask。`UVMap`/BindUV不能随意互换。若原生节点缺少所需字段或出现miss，停止并记录，不重写一套插值器来隐藏问题。

## M1预算与最终路径

本次方向patch不增加曲线数，避免先放大全身groom；节点仍可能产生求值副本，所以不能保证零额外内存。后续增密前须用真实evaluated curves/points和本机峰值RSS/渲染耗时设边界，低Viewport Amount只省预览，不代表最终render预算。上游长毛数值不适配当前scene units，不报未经实测根数/FPS或整机内存硬限。

Blender/Cycles离线完整帧可保留native curves、Hair BSDF、rest属性和原灯光，成本由本地实际渲染量控制；最终每帧仍要完整猫/爪/琴同场景。Godot/Web不是同等材质路径：原生curves/GN/Hair BSDF不会由GLB自动保留，需另做bake/cards/shell的独立损失/性能评估。本试验不为Godot导出验收，不把实时替代当原生毛已通过。

本次只交方法与已核实来源；没有构建patch、复制安装skill、改原C21报告、开动画/CF/云API/commit。当前毛绒P0保持。
