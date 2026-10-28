# C10r3 按弦爪连续结构灰模候选

这是**一只按弦爪的结构试验，未通过最终美术／动作／接触验收**。它不是全角色完成，也没有替换网页或发布。输入 C8r2 保留不变。

## 实际产物

- `miao-c10-paw-topology.blend`：完整猫、双爪和吉他同一场景；按弦爪／腕／前臂／身体已通过局部Boolean union成为同一闭合mesh，不是独立手臂几何或贴片组合。
- `gray-front.png`、`gray-three-quarter.png`：1024整帧，固定源参考机位和诊断三分之四。
- `gray-grip-inside.png`：768掌背／琴侧局部诊断，仅制作检查，不是生产整帧。
- `hand-audit.json`：融合前小手patch的真实网格检查；2650顶点、2648四边面、0边界／非manifold／自交／flipped／loose。布线/自交数字不代表外形自然。
- `receipt.json`、`handoff-manifest.json`：输入SHA、工具固定版、源／目标几何、各图SHA和局限。
- `executed-script-r3.py`：实际此次执行的源码快照，SHA与receipt一致。
- `contact-audit.json`：后续纠正的只读真实弦／指板／皮肤射线检查；没有改native文件。

## 做了什么

按原图的短掌／弯趾和C8实际琴坐标，先做掌的前后宽度环，再从共享指根网格生长三根短弯趾，每根有7圈沿曲线的支持环；手腕从掌后方连到原前臂。小cage细分后才在C8完整身体副本上局部替换／融合。使用已审查的本地MIT `bx_retopo.bridge`，固定上游 `scenario-labs/skills@d44410f058991f677ccf733a8e86ce95110857eb`；未调用任何生成API、网络服务或付费模型。

没有以旧长袋掌为shrinkwrap唯一目标，没有在掌上加深切缝冒充手指。保留C8的相机、眼位和琴对象；C8 hold在构建副本冻结成rest，旧形态键不再作为可用动画数据。

旧native groom隐藏，因为新局部拓扑后，原UV／180k毛根绑定的通过证据**已失效**，需在灰模接受后重新绑定并独立检查，不能把灰模无毛变化解释为材质完成。

## 失败和修订历史

- 首次cage检查发现2个未引用控制点，检查中止，修复后才渲染；失败日志在上一层 `character-paw-c10-cage-check-failed.log`。
- `../character-paw-c10/`：r1，三趾过长像并排柱体，未宣称通过。完整图／native／快照保留。
- `../character-paw-c10-r2/`：r2，缩短后偏像三枚纽扣叠在薄掌，未宣称通过。
- 本r3修正首圈与后续趾环的前后基向量方向，取中等可见趾长、加厚掌背，消除r2的明显掌趾接缝。小手patch实测无自交；这不能替代视觉judge。

## 仍有的具体问题

制作者实看正／侧／局部后，仍认为掌背较扁、后侧腕接口阴影偏硬；三趾还需要更自然地由掌背转向琴面，而不是强调三根并排独立形状。旧拨弦爪长扁端面刻沟、头颊／鼻口的软体积和耳壳问题仍在，本任务没有修它们。

腕部Boolean接口不是干净的最终动画边流，尚无骨架／skin权重／极限curl测试。整猫单连通、闭合不等于全身无自交或可变形；全身约60万顶点，未把小手patch的自交0外推整猫。

## 接触审计的纠正

早期receipt里的 `contacts` 使用桥端第一段弦的斜率外推至琴颈，并从torso后方取首命中；这个原始表**不能用于握持接触结论**。已保留并追加 `legacy_contacts_status` 和新审计入口，不删除旧记录。

新的只读审计直接读取保存场景中6条弦的Bezier控制点／handles／object矩阵，512 samples/segment并与256采样复核；射线从Y=-.88向前，排除torso后方首命中，显式记录hit/miss，只有朝+Y背面才解释为背面间隙，没有nearest fallback。指板另用真实evaluated mesh射线。

36个有限样本：29有效背面、7miss、0前面误命中；弦近表面间隙约 **-0.01159 到 +0.06664u**。负数是潜在软爪／弦穿入，正数是空隙，不可称按实。部分射线可能落在掌或腕而非特定趾，尚不证明逐指触弦；缺指板hit的样本不能称无穿模。当前没有准确按弦／物理碰撞／演奏通过。

下一次若继续改抓握，应让远端短趾从顶部真正折落到琴弦前侧，而不是停在琴颈上方；同时保持饱满连续掌背。先以完整原图对照和实际局部检查再改，不为通过而扩大间隙阈值。

## 复现

在仓库根目录，Blender 5.2.3 LTS：

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/paw-topology-study.py -- --out artifacts/character-paw-c10-r3
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/paw-contact-audit.py -- --dir artifacts/character-paw-c10-r3
```

第一条保留早期raw接触诊断但不用于判定；第二条会追加正确审计并标明旧表不可采信。独立三方灰模review由root组织；制作者不担任该轮judge。没有彩色、动画、Godot角色或Web交付通过。
