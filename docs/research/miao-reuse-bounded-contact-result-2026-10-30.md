# 单次实测接触纠错：FAIL / 已冻结

日期：2026-10-30（上海时间）。唯一新front诊断图已实际渲出并由builder查看；主任务也已确认看图。它是有红字标识的内部技术研究，不是art交付。继续禁止动画、配色扩展和公开发布。

## 本轮完成的真实链路

1. 从已恢复脸部的原生副本出发，保持源可读嘴/眼/Quality，不再重开脸部参数矩阵。
2. 仅使用 guitar scout 的一组实测整琴矩阵：scale .70、Ry75°和位置(-.343145,-.268642,.205)m。
3. 先读取实际 ORG-Hand世界矩阵H和IK-MSTR-Hand矩阵C，按 `Cnew = Hnew H^-1 C` 校准控制器；再eval校验实际手头与轴误差。没有把ORG目标直接盲写IK主控。
4. **实际**双腕可达率为左91.455603%、右97.076450%；实际原上臂/前臂长度ratio约1.0000000，右剩余7.156mm。此为pose后的实测，不是proposal目标值。
5. 真正执行三项关键pad的有界原FK-X数值解。使用evaluated手皮肤三角面BVH的连续最近点，不把离散vertex距或bone tail距当接触gap。每指1°差分、每步≤5°、最多15次、无改善3次停止；未扩域。

## 数值结果与停止点

| 约束 | 初始连续皮肤目标误差 | 最终误差 | 更新次数 | 结论 |
|---|---:|---:|---:|---|
| 左Index2指腹 | 2.940mm | .0155mm | 1 | 单个目标接近，不等于整手通过 |
| 左Thumb1近端背颈肉垫 | 20.349mm | 14.747mm | 15 | 达到上限仍未解，FAIL |
| 右Thumb2准备点 | .128mm | .128mm | 0 | 已接近请求点，但不代替整掌/hover法线与碰撞验收 |

最终每侧真实hand skin均569顶点；独立固定掌/腕支持权重(Hand+Sleeve+Forearm2+三Carpal)≥.90的皮肤各205点。左3点、右86点仍落入实际琴三角网格前/后ray envelope；右最深42.50mm。右最严重样本固定支持weight=1.0，不能靠继续转末端finger phalanx清掉。因此停止，不再尝试其他指curl、另一组腕位或琴变换。

Ray envelope能提供明确拒绝证据，但零命中也不是完整triangle collision PASS；本轮有多处穿入，不存在该接受歧义。当前目标误差小的两个pad不能抵消左拇指失败与固定掌腕P0。

## 空集合检查错误已纠正并留痕

初版wrist筛选错误地要求DEF-Hand权重≥.65，实际该group最大只有.448035，因此左右0样本却暂写CORE_GATE_CLEAR，这是错误标签，已撤回为UNKNOWN_INVALID_EMPTY_SELECTION，旧回执留在 `measured-contact-skin-gate-invalid-empty-selection.json`。

只读权重检查发现真实掌腕同时由DEF-Sleeve、Forearm2、Index/Middle/Pinky_Carpal支持。纠正后按真实side权重及掌坐标范围分别选中208/192点；最终又按实际固定支持权重≥.90逐点测205/205点，非空并明确FAIL。没有把Infinity/空集合当安全通过。

## 唯一诊断图与交接

目录：`artifacts/miao-reuse-v1/contact-correction/`。

- `diagnostic-front-FAIL-NOT-ACCEPTED.png`：完整猫、双手和放大吉他；图内红字TECHNICAL STUDY / NOT ACCEPTED / CONTACT GATE: FAIL。
- `bounded-contact-candidate-FAIL-diagnostic.blend`：新数值失败native，供独立三方检查；没有覆盖上游、旧FAIL或recovered native。
- `bounded-keypad-solve-FAIL-receipt.json`：完整每步角度/连续皮肤误差、最终皮肤数据、相机误差0、source hash前后同值。
- `inspection-manifest.json`：精确图/场景/回执路径及SHA，状态FAIL_FROZEN_PENDING_INDEPENDENT_REVIEW。
- `hand-weight-selection-diagnostic.json`：真实权重分布和空样本原因。

实现落盘于 `design/miao-reuse-v1/scripts/check_contact_candidate.py`、`probe_hand_weight_selection.py`、`solve_keypads_diagnostic.py`。只有一张新诊断render；原猫/手指/琴几何没有重造，上游Python/MoveAI插件未执行，未加关键帧。

原生脸部与琴体积改善可直接从诊断图看到，但builder不自判接触/美术通过。专业源资产仍保留；本轮只证实这组固定腕/琴布局和有界两关节目标不满足实际皮肤约束。三方独立评审由主任务组织，当前builder已停止修改。

## 与跨机基线区分

可复现的上游source-rest baseline仍成功：`render_source_rest_baseline.py`直接从原source生成完整Tpose3Q，保原Quality/head/pupil/mouth，camera逐轴误差0、pose hash不变。当前推荐README与source-pack已改此入口，历史 `render_native_color.py` 的未等价TRANSFORMS patch不再推荐。原source-rest包由主任务补齐GPL全文并更新ZIP/hash/Release，本报告不复写其发布状态。
