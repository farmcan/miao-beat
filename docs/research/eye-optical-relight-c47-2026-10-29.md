# C47 · 真正丢失的是眼部反射灯的位置

本轮以 C45 r2 为基准，只重新摆放原有两盏 optical area。没有修改 mesh、curve、shader、材质、毛发状态、主灯、光能、光源尺寸或 receiver。实际打开 C47 的整身与脸图，并与 C43 A/B、C45、C20 和批准原图比较。

## 先做实际光学几何诊断

脚本：`design/character-sculpt-v2/eye-optical-relight-c47.py`。输出：`artifacts/character-eye-optical-c47/optical-diagnosis.json`。

使用实际 cap 的 smooth vertex normals。相机实际类型是 ORTHO，因而 view 使用相机旋转的恒定朝向，不用透视相机位置减表面点。对 cap 前面、半径约 .875 以内的 2016 个真实顶点，计算法线 n、view v、现有灯中心方向 l、半程向量 normalize(v+l) 以及所需镜面方向 `2(n·v)n-v`。

选中的真实 cap 点位于各自归一化虹膜左上约 (-.1875, +.32476)，实际顶点 index 801；没有另画高光点或在表面增加发光物。

| 实际诊断 | C20 L / R | C45 r2 L / R |
|---|---:|---:|
| 目标点所需镜面方向与现灯中心的夹角 | 6.92° / 9.86° | 116.72° / 117.25° |
| 内部采样能找到的最小镜面方向误差 | .871° / 1.136° | 36.13° / 53.96° |
| 灯盘在目标点的角半径 | 5.235° / 5.218° | 5.211° / 5.178° |

这些角度是几何诊断，不是完整 BRDF/遮挡可见性解。它们已足够暴露一个远大于“略微压平”的异常：C45 两盏灯的世界位置都精确是 **[0,0,0]**，从眼点看几乎朝下；C20 原灯在眼前上方约 z=4。

## 独立 loader 因果 probe

`loader-transform-causal-probe.json` 实测：

1. C20 已保存场景中，两灯 world 与 local 位置分别为 L `[.05736,-3.18527,4.13317]`、R `[2.34358,-2.39305,3.99139]`，没有 parent。
2. `bpy.data.libraries.load` 加载同样两灯、但尚未 link 到 scene 时，local 位置仍正确，**matrix_world 却都是 identity**。
3. 把 donor link 到 scene 并 `view_layer.update()` 后，world 与 C20 来源重新匹配。
4. C31 assembler 的旧代码直接读取未 linked donor 的 matrix_world，C45 继承的灯 world 正是 identity。根因与实际加载状态吻合；这不能再被归因为已经证明的 cap 曲率问题。

后续 assembler 应在源 head 场景已经打开且 depsgraph 已更新时冻结所有 feature 的 world matrix/hide 状态，跨场景加载时只取 data，随后应用冻结源矩阵。历史 C31/C43/C45 原生文件、图像与失败结论没有覆盖或删除。

实际修复进一步保存原 native transform channels：仅赋 `matrix_world` 会在 Blender 分解回 Euler 时造成最大1.49e-7的旋转矩阵差。当前 assembler 在真实源场景保存 location、rotation mode/Euler/quaternion/axis-angle、scale与delta channels，显式限定源/target没有parent或constraints，恢复原通道后再要求世界矩阵bit-exact。独立执行当前源码实际capture/transfer片段，17个feature的world、channels和hide全部exact；两盏灯参数和target receiver对象身份正确。证据`assembler-current-source-audit.json`；旧world-only浮点失配证据仍保留。这是后续源码修复，不覆盖历史C31 native。

## C47 唯一变更

沿真实目标点的镜面方向摆放现有光源，保留它到目标的原距离，转向该点。实际新位置：

- L `[.185831,-3.265477,3.957875]`。
- R `[2.882171,-1.876709,3.875115]`。

两灯都保持实际来源参数：100W、DISK .55、diffuse 0、specular 1、原 optical receiver collection。没有把 Studio receiver 加入 cap，也没有叠加 C43 B 的变量。两张图仍为 CPU Cycles、128 samples、seed 17、768px，相机与 C45 相同。

## 实际看图结论与边界

- `c47-full.png` 与 `c47-face.png` 中，两眼恢复可见的蓝色渐变、曲面镜面读法和小而清晰的光点，相比 C45 的黑圆片明显更有神。实际脸图没有看到灰片或新投影污染；这是可保留并提交独立审查的局部贡献。
- 这不是整体角色通过。白眼与软睑的包裹、耳根硬槽、下脸长度、肩臂、手部、毛发、动作仍未在 C47 改变或放行。未测试其他相机、头部转动、眨眼或视频中反光稳定性。
- C47 使用 C45 的恢复曲率 cap 加正确反射灯。它没有做“C38 原压缩 cap + 正确反射灯”的同条件对照，因此**不能从本轮反推 C45 曲率恢复必不可少**，也不能继续声称黑眼单由 42% 压缩引起。
- Builder 的判断不替代三角色独立审查。receipt 中 `art_gate_passed=false`，未改 public 或生产。

## 保存后原生重开核验

`native-readback.json` 来自另进程：所有 47 个 mesh 的坐标/拓扑/世界变换、所有 curve 几何、全部有效材质的节点/输入/连接 hash 都与 C45 exact；所有灯的非 transform 参数和 receiver 都 exact；**仅原有两盏 optical area 的 transform 改变**。

Native：`miao-c47-physical-optical-relight.blend`，SHA `1ab25c94d05b91f7cd11480d752dbed2154577f30c45a7c420d6d1a2dc77f146`。材质节点 hash `26b82e614a5e4ae8a08d94e7151464099e612a7ce23e51d81ac541c91a510864`。来源、脚本、图像与 native 逐文件 hash 见 manifest；大 native 仍只在本机，不声称已经形成跨机器完整 native handoff。

## 对修正后 assembler 的独立验证

第一次仅复制冻结 world 矩阵的策略恢复了正确灯位置，但 matrix→Euler→matrix 重算造成 L 1.49e-7、R 1.49e-8 的旋转系数差；严格 bit-exact 未通过，`assembler-transform-strategy-audit.json` 及首次失败脚本/日志保留。没有把该失败解释为再次丢失灯位置。

修正后同时冻结原 local location、rotation mode、Euler/quaternion/axis-angle、scale 及 delta 通道，明确限制源/目标 feature 无 parent/constraints。`assembler-current-source-audit.json` 直接抽取并执行当前仓库脚本的真实 source-snapshot 和 data-transfer 代码片段，经过 C20→C35 场景 reset + library load：**17 个 feature 的 world、hide 与全部 native transform 通道 bit-exact；两灯数据和原 target receiver collection 对实际 target cap/iris 的对象身份均正确**。body 坐标和 data 指针未变，未重建 body，也未重新渲染或覆盖历史 C31。完整 source SHA 与抽取片段见该审计。
