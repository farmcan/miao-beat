# 手爪、头与耳：可复用工具和原生案例

2026-10-28；独立 identity reviewer。只读源码、资料和实际渲染；未安装插件、下载角色工程、修改模型或提交 Git。新增现金预算 0。保留此前 [C8 灰模评审](c8-gray-identity-review-2026-10-28.md)，其“可进入彩色试验”不等于彩色或整体美术通过。

## 先看当前缺口

实际打开原图 `public/character/instrument-scenes-v1/guitar/idle.jpg` 与 C8r2 的 `artifacts/character-fidelity-c8-r2-color/color-front.png` / `color-three-quarter.png`。后两张 SHA256 分别为 `1af441d8bd06ec97398f74b1e5208c7176677f2b7005a080c338a1313c0a9e18`、`60eb962ad2b45af459b1ab11c632d3bc9bfcd1032a3833293ab9cf1623eab9b3`。

本轮不能据此放行整体美术：以下是实际可见的结构差距，不能用加毛、提高采样或换 Godot 消除。

| 部位 | 原图与当前的具体差别 | 下一候选必须显现的形状 |
| --- | --- | --- |
| 手爪，P0 | 原图按弦爪是宽厚掌背连着短弯趾，趾尖沿琴颈落下；当前上端像两个分叉凸片，掌体向下拖成长袋。拨弦爪当前是厚扁端面上的刻线，缺少趾端转折与拇侧收口。 | 先做一个有掌背穹顶、短趾根、弯曲趾腹的完整连续手爪；分趾凹槽绕向侧面并渐弱，不把长切缝当手指。按弦爪去掉顶部的凸片/深折口，先匹配原图拱起掌背和紧凑指尖轮廓。 |
| 头与口鼻，P0 | 正面已有圆方脸色块，但侧图大面积头颊接近平直侧壁；鼻子是薄的倒三角，嘴线像贴在平面上。原图鼻头圆钝，奶油口鼻区有软组织起伏和下颌过渡，眼眶与颊肉属于同一个头。 | 在现有眼位/视线锚点下恢复低幅的双侧口鼻垫、鼻翼圆角、鼻下到嘴角的弧面以及下唇/下巴浅体积；用侧面和 3/4 灰模检查，不能只把白色贴图做渐变。不要照搬人类下颌/头高比例。 |
| 耳，P1 | 当前较长、直立、尖，内耳像三角槽的直墙；原图较短，耳缘圆钝，有耳壳厚度、耳根回转和朝内的柔软凹面。 | 保耳尖/耳根二维位置，做有曲率变化的内外耳壳：前缘圆，后缘较薄，凹面朝内前方，耳根连续融入颅面；避免沿整个边界挤出等厚框。 |

原图只提供一个视角；背面、掌侧被琴遮挡处的结构属于重建假设。以上不把相机差别当形体证据，也不提前判动作、闭眼、蒙皮或网页效果通过。

## 五项最匹配的复用对象

### 1. Scenario 的本地 Blender expert / sculpting / retopology skills：首选方法与局部脚本

固定仓库 commit [`d44410f058991f677ccf733a8e86ce95110857eb`](https://github.com/scenario-labs/skills/tree/d44410f058991f677ccf733a8e86ce95110857eb)，提交 2026-10-27；根 [LICENSE](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/LICENSE) 为 MIT。实际读过下列三个 SKILL 和两个 helper，不是只看介绍：

- [`scenario-blender-expert/SKILL.md`](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-expert/SKILL.md)：阶段备份、逐步转面检查、Blender 5.2 API / headless 限制；另外两项明确以前置它为要求。
- [`scenario-blender-sculpting/SKILL.md`](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-sculpting/SKILL.md) 与 [`scripts/bx_sculpt.py`](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-sculpting/scripts/bx_sculpt.py)。
- [`scenario-blender-retopology/SKILL.md`](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-retopology/SKILL.md) 与 [`scripts/bx_retopo.py`](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-retopology/scripts/bx_retopo.py)。

**源码对应这次怎么用：** `Sculptor.dab("inflate"/"clay")`、`grab`、局部 mask / smooth 用于做掌背、鼻翼和耳根的真实体积；`crease_line` 可处理趾间浅沟/耳缘转折，但必须在体积正确后用。`surface_samples` + `form_report` 能发现“轮廓对了，侧面仍是平板或单一球”的问题。`R.joint_stations` 在弯曲处安排中心与两侧三环；`ring/bridge/tube`、`socket_tube` 用于按掌根→趾根→趾尖构建连续拓扑；`carve_rings` 用于眼/口周闭环；`fit_subdiv` / `multires_recover` 恢复细分后损失的体积。[实际函数源码同上](https://github.com/scenario-labs/skills/blob/d44410f058991f677ccf733a8e86ce95110857eb/skills/dcc/blender/scenario-blender-retopology/scripts/bx_retopo.py)。

**本地使用接口示意，未在 Miao 上执行：**

```python
import sys
# 将已审查的两个 skill/scripts 绝对路径加入 sys.path
import bx_sculpt as S
import bx_retopo as R
sc = S.Sculptor(body_work_copy, symmetry_x=False)
# 先以参考标定局部 mask/center/radius；不要对抱琴姿势做全身镜像
sc.dab("inflate", palm_center, palm_radius, strength=small_strength)
sc.commit()
stations = R.joint_stations(root, curl_joint, toe_tip)
# 对新低模 cage 的局部环操作；不是对 60 万顶点直接全局重新拉伸
```

两个 helper 的 import 是 `bpy/bmesh/mathutils/numpy` 与标准库；`Clay.to_object` 另用 `openvdb`。未见网络客户端或生成 API 调用。本机只读探针已确认 **Blender 5.2.3 LTS / arm64、NumPy 2.3.4、OpenVDB、QuadriFlow、Multires Apply Base API 均存在**；未证明 helper 在本模型上成功。纯本地调用不新增 API 费用。前置 skill 的 GUI 章节另提 Scenario 插件/MCP；本轮不用该通道，也不用付费生成服务。`bx_gui.py` 本身调用真实 Blender 画笔，需要现有 GUI 上下文，headless 不能假装有画笔效果。

**重要边界：** skill 的专家来源和测量表是上游方法总结/自测，不是我们已复现的精致度保证。`head_guides()` 是人类写实头部比例，绝不能套给 Miao；其 `Clay` primitives 也不是被批准的猫基底。重拓扑投影到错误原形，只会精确复制错误，先修可见体积。MIT 复制需保留声明。

### 2. LoopTools：最轻的局部曲面整理，适合耳壳与掌趾环

官方扩展 [LoopTools 4.7.7](https://extensions.blender.org/add-ons/looptools/)；发布 2024-05-14，官方标记有限支持、Blender 4.2+、GPL-2.0-or-later、无额外权限。当前上游固定 commit [`c6490da1eb0c33bec195daba2fb46e152fa54ff8`](https://projects.blender.org/extensions/mesh_looptools/src/commit/c6490da1eb0c33bec195daba2fb46e152fa54ff8)，2025-05-14；实读 `source/blender_manifest.toml`、`source/operators/{bridge,curve,relax,space}.py`，非已归档的旧 GitHub mirror。

**具体用法：** 对人工安排的耳缘两条环用 Curve/Space 整理连续曲率，再 Bridge 成厚薄变化的耳壳；对掌根/趾根环局部 Relax 和 Space，避免弯爪时密集夹点。实际 operator 为 `mesh.looptools_bridge` / `curve` / `relax` / `space`。Curve 按控制点作样条，Relax 在环上插值，不会理解猫解剖；不能一键生成耳窝或从刻缝长出趾腹。[当前源码](https://projects.blender.org/extensions/mesh_looptools/src/commit/c6490da1eb0c33bec195daba2fb46e152fa54ff8/source/operators)。

Python + Blender API，无外部运行时/模型/现金成本；M1 预期不需额外二进制，**未安装、未实测 Blender 5.2**。这是小规模手工精修的辅助，优先于安装一个大建模框架。

### 3. RetopoFlow：手工可视重拓扑备选，不能代替雕刻

固定源码 [`ac2570c5292c1dd90190fd3641b4dbc42cf4bd63`](https://github.com/CGCookie/retopoflow/tree/ac2570c5292c1dd90190fd3641b4dbc42cf4bd63)，2026-05-18，manifest 为 3.4.11、Blender>=4.2；最新 GitHub 发布包 [3.4.10](https://github.com/CGCookie/retopoflow/releases/tag/3.4.10) 为 2026-01-29。发布记录 3.4.9 加 Blender 5.0，3.4.8 修复 Blender 4.5 Mac；仓库最近 push 2026-10-08。这些不等于本机 5.2 已验收。

实际读过 [`contours_ops.py`](https://github.com/CGCookie/retopoflow/blob/ac2570c5292c1dd90190fd3641b4dbc42cf4bd63/retopoflow/rftool_contours/contours_ops.py) 的 `new_cut/change_count`、[`polystrips_ops.py`](https://github.com/CGCookie/retopoflow/blob/ac2570c5292c1dd90190fd3641b4dbc42cf4bd63/retopoflow/rftool_polystrips/polystrips_ops.py) 的 `new_brushstroke`、[`relax.py`](https://github.com/CGCookie/retopoflow/blob/ac2570c5292c1dd90190fd3641b4dbc42cf4bd63/retopoflow/rftool_relax/relax.py) 的 `relax_doit/snap_vert`：能在已有雕刻表面画连续条带/截面、调整环数并贴回表面。适合将雕好的弯趾与耳窝，转为可变形低模；不会把当前平口鼻改成正确软体积。

**许可有差异，不能笼统写免费 MIT：** 固定 commit 的 [`RetopoFlow.LICENSE`](https://github.com/CGCookie/retopoflow/blob/ac2570c5292c1dd90190fd3641b4dbc42cf4bd63/RetopoFlow.LICENSE) 声明代码 GPL-3.0-or-later，非代码资产默认属于 CG Cookie、无许可不可再分发；manifest 却写 GPL-2.0-or-later，存在元数据不一致。按更明确代码许可保守处理，不把图标/材质/字体整体复制到产品。GitHub 提供免费发布包；无需购买支持。依赖 Blender GUI 和捆绑 Python/OpenGL 绘制工具，无 CUDA 要求；M1/5.2 的 overlay 与交互仍待实测。若 LoopTools + 原生 Shrinkwrap 足够，不为 Demo 增加此依赖。

### 4. Blender Studio CloudRig：造型通过后，复用短趾/眼睑控制

官方扩展发布版 [2.2.31，2026-10-05](https://extensions.blender.org/add-ons/cloudrig/)；实际上游 master 固定 [`05b6ddd98c5dc95cd1053443e49bdce418857bf6`](https://projects.blender.org/Mets/CloudRig/src/commit/05b6ddd98c5dc95cd1053443e49bdce418857bf6)，2026-10-06，`CloudRig/blender_manifest.toml` 已为 **2.2.32**、Blender>=5.0、GPL-3.0-or-later。发布包与源码工作版本分开记录，不声称它们相同。

实读 [`CloudRig/rig_components/cloud_finger.py`](https://projects.blender.org/Mets/CloudRig/src/commit/05b6ddd98c5dc95cd1053443e49bdce418857bf6/CloudRig/rig_components/cloud_finger.py)：`Component_Finger` 继承 IK/FK chain，含双骨 IK 和伸展逻辑；[`cloud_eyelid.py`](https://projects.blender.org/Mets/CloudRig/src/commit/05b6ddd98c5dc95cd1053443e49bdce418857bf6/CloudRig/rig_components/cloud_eyelid.py) 把眼睑与 Aim 眼球的方向通过 drivers 相连。短猫趾应克制 curl，限制伸展，保持宽掌；耳可用短 FK 链，不能每音抖动。眼睑不是再装一个球面盖子。

原生可研究的现成例子是**包内 Sintel metarig**；官方 [组件文档](https://studio.blender.org/tools/addons/cloudrig/cloudrig-types) 明确建议主角用手工 Action poses 做眼睑跟随，不依赖通用 sticky。当前文档也不再推荐 Face Grid 作为精细面部主方案。依赖 Blender Python、原生骨骼/约束/driver，不需云 API/CUDA/付费；扩展请求本地文件与剪贴板权限。M1 理论可用，未安装或生成 rig。[工作流来源](https://studio.blender.org/tools/addons/cloudrig/introduction)。

它省绑定基础设施，不自动补掌背/口鼻/耳壳。到 Godot 时，B-Bones、driver、约束应转换/烘焙后验证，不能因为 Blender 能动便声称 GLB 等效；本调研没有完成导出。

### 5. Rain v3：免费原生角色的结构/形变案例，不能换成 Miao

官方 [Rain v3](https://studio.blender.org/characters/rain/v3/)（2025-05-08）标记 Free、Blender 4.1+、CC-BY；页面要求保留 `Rain Rig (CC) Blender Foundation | studio.blender.org` 署名，未在页面明确 CC-BY 版本，不能自行写成 4.0。`.blend` 含 rig UI 脚本、层级面部控制和 corrective shape keys，不要求安装额外插件。Mac 使用取决于 Blender；**未下载/打开工程，不把页面宣称算成本机 5.2 验证**。

下一步若要看真正完成的“软组织随动作保持形”，可先只读其头/脸 corrective、手指屈曲时掌背体积与关节环；这比导入一个低模猫后继续拉比例更有价值。Rain 是人类角色，不能移植其脸比例、手长或模型外观来替代 Miao。官方原生完成度可以作方法标杆，不能作“已有同款猫可直接上线”的证据。

## 没选的捷径与立即可执行顺序

- **全身自动 QuadriFlow**：本机已有，不用再编译下载 2019 年停止更新的 [QuadriFlow 上游](https://github.com/hjwdzh/QuadriFlow)；它的 LICENSE.txt 是 BSD-3-Clause，不是 MIT。但自动四边面不保证眼/口闭环、掌趾关节方向或薄耳保形。Scenario 上游实测也记录薄耳被撕裂、眼口缺环；这只是上游证据。它可做躯干起点，不是本轮手/头/耳精致度主方案。
- **Blender Studio Wing It! Cat** 是真正的 [原生猫 rig 案例](https://studio.blender.org/characters/cat/v1/)，官方明示 **exactly Blender 3.6**，较高/低版本都可能坏，且当前库页未标 Free。CC-BY 使用许可不证明本次能零成本拿到下载，也不证明 5.2 兼容。未付费/下载；体型也不能直接替换 Miao。先看官方公开示例研究耳壳/爪，不把它列成即插即用方案。
- `edemaistre/blender-expert-skills` 虽有相似 helper，GitHub license 元数据为空；本轮优先采用已明确根 MIT 的 Scenario 固定版，不把缺许可当默认开源授权。

**建议最小验证：** 制作者先复用已审查的本地 sculpt helper，在副本上仅做一只完整弯爪 + 口鼻体积 + 一只耳壳；不重设眼位，不改全身比例。输出同相机正/侧灰模与掌背/趾腹/口鼻/耳壳近景，三角色独立评。灰模不过停止毛发/动画扩张；过后才重拓扑该局部、做一个 curl/触弦与一个头耳小动作，再评原速和慢放。工具顺序为 **Scenario 本地方法 → 必要的 LoopTools → 原生/CloudRig 绑定**；RetopoFlow 是人工交互成本值得时的备选。

这些步骤仍需美术判断。新工具能让局部形状可雕、拓扑可控、变形可修，不能证明资产已精致，也不能代替下一轮实际渲染与动作评审。
