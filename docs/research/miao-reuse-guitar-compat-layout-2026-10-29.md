# 现成吉他兼容转换与一次静态摆位建议

日期 2026-10-29。范围：复用已获独立 craft PASS 的 Rohma Ansari / Classic Guitar；仅格式转换、重导验证、只读尺度测量。未修改猫姿态或原吉他资产。实际静态抱琴由单独唯一 builder 负责。

## 兼容 GLB 已通过

文件：`artifacts/miao-reuse-v1/instrument/classic-guitar-compat.glb`，17,388,020 bytes，SHA256 `1e3da0406355be281e2442de80bd4093eba58cfda640a07a6acd53ab231b1e41`。

来源原包 SHA256 仍是 `e94d430f908ade7bf3daa3f8a3978f9f16ddd780aa7cd312d81135958067d900`，未保存回写。格式转换使用 Blender 5.2.3 的内置 glTF 2.0 exporter，factory startup / disable autoexec，不装或运行上游插件。

| 检查 | 结果 |
|---|---|
| 5.2 重导几何 | 原始和 GLB 都为 141,217 triangles；逐三角顶点坐标 multiset 在 1e-5m 精度下相同；双向最近顶点最大距离 0m |
| 六弦 / 18 品 | 完整保留；55 个按精确坐标虚拟焊接计算的连通岛一致；虚拟焊接仅供检查，没有改模型 |
| 顶点数量变化 | 原始 71,372 → GLB 重导 80,078，是 normal / UV seam 分裂；不表示几何丢失。18 个品丝不能用重导后的单岛顶点数 16 硬判，应按坐标几何核验 |
| 材质 / 贴图 | `Guitar` 标准 PBR，三张 4096² 嵌入 PNG；baseColor、normal、occlusion、metallicRoughness 连接保留 |
| 导出 sampler 警告 | 同一贴图源被多个 TEX_IMAGE 节点复用；已查四个节点均 Linear / REPEAT，因此选第一节点 sampler 不改变本次节点设置 |
| 格式 | glTF 2.0 GLB；无 required extensions、无 Draco / Meshopt 压缩依赖；glTF Y-up，Blender 导入恢复 Z-up |
| 3.6.23 实际兼容 | 猫 scout 在空 factory / disable-autoexec 场景实测成功：1 mesh、141,217 triangles、3×4K packed、尺寸完全相同、0 texts、源 SHA 前后不变。见 `artifacts/miao-reuse-v1/compat/guitar-native36-import-receipt.json` |
| 尺度 | 原始 XYZ 0.41377230 × 0.13926736 × 1.11170581 m，front=-Y，长轴+Z，origin 近琴底 |

本机 GLB 重导检查图（与原始检查图相同镜头；未修品牌 / 灰侧板）：

![GLB重导外观](../../artifacts/miao-reuse-v1/instrument/reimport-full.png)

源码位于 `design/miao-reuse-v1/scripts/export_guitar_compat.py`、`verify_guitar_compat.py`。`instrument/export-receipt.json`、`reimport-validation.json` 保存完整数据。

## 一次具体静态摆位方案

以下坐标针对 `artifacts/miao-reuse-v1/compat/wingit-working-native36.blend` 的实际未改 rest pose / identity transform。3.6 只读测量回执为 `instrument/static-layout-measurements.json`；导入 GLB 后只在数学计算中施加矩阵，未写入猫场景或琴对象。

整把琴使用同一变换：**uniform scale 0.50；Euler XYZ=(0°,65°,0°)；location=(-0.235,-0.241,0.235)m**。不得分别改琴颈或琴身比例。导入对象 `Classic Guitar`，材质 `Guitar`。琴颈朝+X，对应猫自身左手 L；右手 R 轻悬音孔弦上。

真实顶点计算后的整体 bbox：min `(-0.24939348,-0.27581683,0.16617313)`，max `(0.27001336,-0.20618317,0.48392844)`m；宽 0.51940684m、厚 0.06963366m、高 0.31775531m。不是把未旋转 bbox 当作变换后的精确外界。

| 接触目标 | 猫左手 L：握颈 | 猫右手 R：悬弦 |
|---|---|---|
| 测量局部依据 | 六条实际弦在 z=0.70m 截面中心 | 六条实际弦在 z=0.30m 截面中心，再沿-Y悬空 0.006m；缩放后为 3mm |
| 世界接触目标 | (0.08220775,-0.27498105,0.38291639) | (-0.09905379,-0.27728537,0.29839277) |
| 建议腕初值 | (0.08829124,-0.22539192,0.38489369) | (-0.10160593,-0.23053727,0.31594563) |
| 肩到目标 / 原上臂+前臂+手掌 | 0.25134279 / 0.30251638m，83.1% | 0.26908233 / 0.30251638m，88.9% |
| 肩到建议腕 / 原两段臂 | 0.20134280 / 0.24475918m | 0.21908230 / 0.24475918m |

原肩 L/R 分别是 `(±0.11278852,-0.02570365,0.39285594)m`；上臂 0.12197337m，前臂 0.12278580m，手掌骨 0.05775721m。目标不要求拉长骨骼。腕初值只是沿目标到肩方向退 5cm，不能替代实际 wrist roll / elbow bend / finger curl。

![实际bbox静态布局图](../../artifacts/miao-reuse-v1/instrument/static-layout-proposal.svg)

图是工程 bbox 与触及目标示意，虚线不是已摆好的手臂，不是抱琴渲染或接触证据。完整源数据 `instrument/static-layout-proposal.json` 包含六条弦在两截面的真实位置、变换矩阵和猫组件 bbox；图由 `draw_static_layout.py` 输出并已浏览器目视核验。

需要 builder 特别检查：头 mesh bbox 最低 z≈0.41529m，琴头最高 z≈0.48393m，局部 bbox 存在重叠区域；琴头位于右侧不意味着已经没有下颌穿模。琴背到躯干最前全局平面约 3.6mm 的间隙，也不证明曲面实际贴靠。上述 reach 仅是必要几何条件，尚未验证关节极限或外观自然度。

## 许可与剩余事项

- 吉他 CC0：原作者 / 原 URL / asset version / 下载证据、原许可 HTML 与分项说明均在 `instrument/licenses/`、`DERIVED-PROVENANCE.json`。转换 GLB 沿用 CC0；嵌入贴图按供应方整个资产的 CC0 提供，未找到独立第三方贴图署名。没有把本地脚本默认为 CC0。
- Cat Rig (CC-BY) Blender Foundation | studio.blender.org，CC BY 4.0；该图与测量结果基于其角色测量，已保留署名、原链接与修改说明；这里没有另行发布猫网格。
- Ibanez 字样、灰亮侧板与软音孔圈仍是局部表面修整待办；本轮没有重造琴或改动原贴图。
- 已通知唯一 pose builder 兼容路径、尺寸、变换、左右接触目标；没有争用或覆盖其猫场景。仍未做动作、浏览器接入或发布。公共状态由主任务统一留痕。
