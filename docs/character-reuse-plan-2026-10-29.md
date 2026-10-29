# 当前路线：复用成熟猫与吉他

用户在2026-10-29明确要求停止空手造模型，舍弃Godot。此前自建猫的扁身体、面条手、穿琴与粗糙表面未过评审；继续修补没有形成足够可见的改进。旧实验全部保留，但不再作为新角色基础。

## 1. 已取得的真实资产

| 素材 | 来源与许可 | 本机事实 | 当前gate |
|---|---|---|---|
| Wing It! Cat | Blender Studio；MoveAI官方优化再分发；模型CC BY 4.0，插件代码另属GPL | 6.29MB `.blend`，真实圆掌四指/独立拇指/成熟rig，贴图packed；原作者支持3.6 | 三个非builder均GO进入静态试验；最终成品与动画HOLD |
| Classic Guitar | Rohma Ansari / BlenderKit，CC0 | 17.34MB `.blend`，真实6弦/18品丝/完整厚度/三张packed4K图 | 独立craft PASS进入静态装配；整体抱琴未验 |

文件和许可证据在`artifacts/upstream-cat-candidates/scout-a/`、`artifacts/upstream-guitar-candidates/blenderkit-classic/`，原包不可覆盖。GitHub代码许可不能代替模型许可。猫报告及三评：`docs/research/upstream-cat-*`；琴报告/评审：`upstream-guitar-scout-*`与`upstream-guitar-craft-judge-*`。

## 2. 最便宜的静态闭环

1. 使用官方Blender3.6并存环境验证猫；优化分发版实际为PBR材质，不追不存在的完整原电影toon还原。不执行不必要的CloudRig UI脚本；相机driver若需修，用可追溯的显式变量兼容修复。
2. 琴在5.2导出标准GLB再导入3.6，避免旧运行时直接读取较新native。核对6弦/18品与贴图，保留原尺度。
3. 保留成熟角色比例、工装和掌指结构，先做一个暖色猫脸/手与简洁服装配色、自然静态抱琴。若这套角色必须重造身体才适合，换模板。
4. 输出实际完整正面/3Q与脸/双手特写；三角色判断可爱、体积、工艺、清楚指形、手与琴接触。任何P0不放行动作。原色作者图片不代替本机适配结果。

只做一个主静态方案和一次有具体依据的修复；失败后冻结，由三方先诊断。若需要重造身体/头/手，换成熟模板。若证实为本项目误用原生rig/驱动/接触摆位，允许有限且先量测的适配纠错，不以我们错误的使用方法否定优秀原素材；仍禁止几何参数实验链，也不得越过静态三评。

## 3. 页面加载修复独立推进

旧三引擎页默认同时准备约44MB资源。当前局部修复已移除Godot入口、将Three按按钮动态加载，默认排除33,262,073字节文件资产；118项测试与构建通过，真实浏览器按键/演示/停止与延迟加载已验，性能修复已提交1330fa0并部署，canonical验收进行中。这里只发布交互性能修复，不把旧3D猫称作新美术版本。

## 4. 动作与上线

仅静态完整模型三评通过后，才验证一个单键单次弹奏，随后慢/快连按、停止、手指接触、轻微头眼响应和录制导出。沿用成熟rig，页面按需加载。主站原2D版本在新角色实际验收前保留。

## 5. 首次整合实图结论（不是完成）

`static-hold/inspection-manifest.json`已锁定原色/暖色完整、3Q和脸/双手共10张。identity/craft/motion三方全部FAIL：左眼伪影、嘴不可读、握颈处不自然肉色块与右掌压琴。

已确认builder将`Sealed Mouth`从False误置True（这是封口实现开关，不是普通闭嘴pose）；相关9条driver有效，不能说缺失。camera helper兼容driver虽然valid，但方向行为尚未证实等价。下一步仅做源脸属性/相机helper有限基线诊断与握姿几何测量。禁止动画和生产猫替换。报告见`docs/research/miao-reuse-static-{identity,craft,motion}-judge-2026-10-29.md`。

## 6. 有限恢复与持琴量测

2026-10-29追加：恢复源mouth/head/pupil/Quality与每次render显式相机helper同步后，两角度真实渲染嘴与眼部恢复，identity与craft独立确认。该项关闭，不重建眼嘴；持琴仍未通过。

新持琴候选仅由真实mesh、皮肤proxy和原臂长量测得出；使用整琴统一0.70比例、15°颈轴上倾。左/右腕距分别0.223846m / 0.237603m，原两段臂长0.244759m；右侧仅约7mm余量，任何过伸立即阻止继续。量测不是实际姿态/碰撞通过。下一步是唯一builder按真实frame与指腹目标作有限静态纠错，先验eval皮肤再出主图，不拉长手臂或改手指网格，不提前改色或加动作。

跨机原素材包和说明见 `docs/character-licensed-assets-handoff.md`。
