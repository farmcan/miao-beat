# Blender5.2 native短毛随表面变形：本机可复用接线

2026-10-28。研究者 `reference_geometry`，不是 D0 builder。**本机已验证官方节点和官方snap operator可完成原生hair attachment及刚性旋转/平移；没有在真实C5资产上绑定。** 不安装插件、不下模型、不修改root的角色/源文件。

## 实际本机证据

`/Applications/Blender.app/Contents/MacOS/Blender` 为5.2.3 LTS，build `e13b728c6880`。通过空场景后台Python实际检查RNA、append本机Essentials资产，再执行两个8毛点微型probe：

- 可提交源码和receipt：`design/character-sculpt-v2/probes/native_hair_deform_probe.py`、`native_hair_snap_probe.py`、`minimal-deform-result.json`、`minimal-snap-result.json`。
- 本机API/资产接口快照：`design/character-sculpt-v2/probes/local-native-hair-api.snapshot.json`。
- 原始完整资产节点检查：`artifacts/native-groom-binding-research/local-api-assets.json`。
- 两项probe均为一个带唯一UV的测试平面、两条各4点native hair；surface shape key旋转Y25°并平移(.13,-.07,.20)。官方节点输出8点与解析变换结果的最大误差均为 **1.4901161193847656e-08**。
- 第二项没有手写根UV，而是实际调用 `bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')`，返回 `FINISHED`，真实产生 `surface_uv_coordinate`，类型 `FLOAT2`、domain `CURVE`。

这不证明180k条毛的性能、C5真实绑定精度、肤毛颜色随动、非刚性肩肘变形或整帧动画质量已经通过；微型probe只是改变下一步选择的最低成本证据。

## 必需数据：真实RNA与官方节点源码一致

| 位置 | 本机实际属性/类型 | 用途 |
|---|---|---|
| hair的Curves数据 | `hair.data.surface = body` | 关联surface mesh对象，不能只设parent |
| hair的Curves数据 | `hair.data.surface_uv_map = "BindUV"` | 字符串，指定body上绑定UV属性名 |
| body Object | `body.add_rest_position_attribute = True` | 本机RNA说明是在shape keys/modifiers前拷贝position，求值面上提供rest_position |
| body原始与求值mesh | `BindUV`，`FLOAT2` / `CORNER` | 同一UV在原始和求值面都必须存在，不能重叠 |
| body求值mesh | `rest_position`，`FLOAT_VECTOR` / `POINT` | 官方节点用它推导旧/新切向，probe已实际看见 |
| hair curves | `surface_uv_coordinate`，`FLOAT2` / `CURVE` | 每条毛根一个二维UV，180k条就应180k项，不是每个毛点一项 |

`GeometryNodeDeformCurvesOnSurface` 是**内建节点类型**，不是必须从Essentials append的同名node group；只有Curves几何输入与Curves输出，surface/UV/rest是隐式输入。最短修饰器接线为 `Group Input.Geometry → Deform Curves on Surface.Curves → Group Output.Geometry`。

官方5.2分支[真实C++源码](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/geometry/nodes/node_geo_deform_curves_on_surface.cc)明确检查surface对象、UV名、原始/求值UV、求值rest_position和根UV；缺失时会原样传出并给警告。不能因为“没报Python异常”就认为毛跟随成功。该代码还保留不同三角形切向造成不连续的TODO，后续非刚性转动仍需看实际毛向是否跳变。

## 无需逐毛暴力搜索：官方snap operator已实际跑通

本机 `bpy.ops.curves.snap_curves_to_surface` 的RNA参数 `attach_mode` 实际只有 `NEAREST` 与 `DEFORM`，不是猜测的 `NEAREST_SURFACE` 等名字。

首次在**静止/冻结rest面**上绑定推荐：

```python
hair.data.surface = body
hair.data.surface_uv_map = "BindUV"
body.add_rest_position_attribute = True
bpy.ops.object.select_all(action='DESELECT')
hair.select_set(True)
bpy.context.view_layer.objects.active = hair
bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')
```

这套object-mode/background接线已在微型probe真实返回FINISHED并创建根UV。代码由Blender处理最近表面查询；[官方curves_ops.cc](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/editors/curves/intern/curves_ops.cc)使用surface BVH、三角形采样与UV插值，不是Python `180k×600k` 扫描。`DEFORM`按已有根UV重新贴回surface，不作为首次根UV建立的替代。官方operator函数读取的是 `surface_ob.data` 原始mesh；不能把这个一次性snap操作当成读取shape-key求值面并实时变形的节点。实时原始/求值差分由后面的Deform节点执行。`bpy.ops.curves.surface_set` 也真实存在，但没有必要再用UI交互方式选择surface，RNA直接赋值更窄。

snap会把毛根移动至所选最近表面；当前C5根本来取自实际求值面，因此若绑定的是同一个冻结面，预期初始移动应接近数值误差。这仍需真实C5测量，不能凭预期当通过。必须记录绑定前后根位移最大值/分位数、曲线/点数，避免把腹侧毛吸到附近手臂或琴上。surface只设猫体，不应把琴加入绑定面。

## C5的唯一绑定UV路线：专用每面独占atlas，不承载视觉色图

C5冻结mesh为609383点，毛根已在该实际求值表面。首轮曾假设没有UV；D0.2实际预检发现已有UV层，因此该假设已被纠正。现有UV的唯一性／完整性尚未验证，必须保留其名称与hash、不得覆盖；另建专用绑定UV。建议**在D0独立副本的冻结rest mesh上**创建 `BindUV`，保留原C5工程以便回退。不要把已有毛根重新当作更低分辨率原始body上的根，否则Subsurf/Boolean的rest偏移可能被二次施加。

绑定UV只用于唯一定位表面，不是美术贴图。可对每个polygon分配独占小方格，所有方格落在0–1内且有guard band；三角/四边面按环顺序在本格内放无重叠角点，ngon需保持有效非自交映射。令 `side = ceil(sqrt(polygon_count))`，面i用格 `(i % side, i // side)`，格内角点保留约10%边距。使用NumPy构造UV数组、一次 `uv_layer.data.foreach_set('uv', flat_uv)` 写入，避免逐毛×逐面的Python循环。

这是一条**明确的待实施绑定atlas方案，不是已在C5跑过的结论**。每面独占UV不等于有艺术UV，也不能用于给网页宣称贴图完成。其成本与mesh corners数线性相关，根绑定交给上述已验证Blender BVH operator。约百万面时格宽约1e-3，仍应实际检查float32精度、degenerate UV与毛根落在边界的情况，不写“永不出错”。

顺序：固定body rest拓扑/变换 → 建专用BindUV → 设置surface/UV/rest → 官方NEAREST首次根绑定 → 官方Deform节点 → 绑定rest姿势等值检查 → 一个局部shape/armature位移检查。**绑定之后不重做UV、不remesh、不重新采样毛根、不改变绑定面与毛对象的相对transform。** 若继续保留Subdivision，UV Smooth应设None并对照原/求值UV；当前D0既然已冻结求值mesh，优先不新增改变拓扑的modifier。后续低模retopo/正式rig需要重新验证attachment，不能拿本次高模可运行替代。

## 本机Essentials资产：真实存在，但operator更适合这次最小链路

实际文件：`/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/procedural_hair_node_assets.blend`。本次用 `bpy.data.libraries.load(..., link=False)` 实际append并检查了 `Attach Hair Curves to Surface`、`Set Attachment Surface`、`Rest Surface`、`Get Attachment Surface` 等组。

`Attach Hair Curves to Surface`在本机5.2的实际输入与identifier：

| 输入 | identifier / 默认值 |
|---|---|
| Geometry | `Input_0` |
| Surface Source | `Socket_2` / Object（Menu） |
| Surface Geometry | `Input_3` |
| Surface Object | `Input_4` |
| Surface UV Map | `Input_2` / vector field，**不是直接字符串socket** |
| Resting Surface | `Input_6` / False |
| Use Existing Attachment | `Input_10` / False |
| Snap to Surface | `Input_8` / True |
| Blend along Curve | `Input_12` / 0 |
| Align to Surface Normal | `Input_7` / False |

输出Geometry为 `Output_1`、Surface UV Coordinate为 `Output_9`、Surface Normal为 `Output_11`。组内有写 `surface_uv_coordinate` 与 `surface_normal` 的Store Named Attribute，并使用Sample Nearest Surface/UV Surface。5.2资产还包含Geometry Bundle相关节点；不能照搬旧版教程的字符串Surface UV Map接线。

**未验证边界**：本次试接该资产后，简单接线没有在求值输出上得到根UV，未把它记为成功；原始失败probe留在artifacts。没有为了套资产继续扩查复杂bundle。当前推荐已经真实成功的RNA+NEAREST operator+内建Deform节点，现成asset的详细接线仅作已检查接口，不声称它已绑定C5。

## 官方资料与版本边界

- [5.2 Deform Curves on Surface手册](https://docs.blender.org/manual/en/5.2/modeling/geometry_nodes/curve/operations/deform_curves_on_surface.html)：英文页面本次web抓取返回402，搜索索引的官方印尼语5.2页可读到隐式UV/rest要求；不把抓取失败解释为节点不存在。
- [5.2官方源代码](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/geometry/nodes/node_geo_deform_curves_on_surface.cc)：本次实际读过。分支会移动，本机build与probe receipt是实际运行版本锚点；没有把分支当前代码直接叫作本机二进制逐字对应commit。
- [官方曲线操作源码](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/editors/curves/intern/curves_ops.cc)：实际核查BVH snap/attachment实现。
- [官方3.3节点/物理发布说明](https://developer.blender.org/docs/release_notes/3.3/nodes_physics/)：可追溯曲面绑定功能来源；不能替代5.2本机实测。

当前研究已完成的真实闭环是**isolated微型attachment/deformation**，下一项由D0 builder在真实C5副本上建立唯一UV与180k根attachment，并实际量测、渲染、独立复评。色场rest绑定是另一条必要链路；它不会自动让毛跟随，反过来本节点也不会自动修正着色坐标漂移。没有新收费工具或安装需求。

## 补充微型实测：自定义rest色场不随position自动变换

另在 `design/character-sculpt-v2/probes/native_hair_rest_attribute_probe.py` 真实验证：先创建POINT/FLOAT_VECTOR的 `miao_rest_position`，将毛根故意放在测试面上方0.005u，再用NEAREST贴面，接官方Deform完成Y25°+平移。求值后position与解析预期误差1.49e-8；自定义rest属性相对初始快照maxdiff **0.0**。结果 `minimal-rest-attribute-result.json` 已归档。它与官方源码只改position/rootUV的行为相符；如果真实绑定初始snap有较大位移，自定义rest不会自动跟着补偿，builder须决定在rest绑定时一次校准，而非每帧重写rest。该额外probe仍没有加载或修改Miao工程。
