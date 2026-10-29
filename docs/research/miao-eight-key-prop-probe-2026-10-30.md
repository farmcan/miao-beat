# 八白键复用装配 · 单一有界静态 probe

2026-10-30。Builder 的隔离技术研究，不是独立美术/接触签署，不替换线上A/C4实验，也不授权动画扩展。用户原图是稀疏的大键玩具琴；现有68键模型在完整页面中太密。此次复用同一CC0 Key Forty现成几何，不新增琴、手或角色网格。

## 实际源与唯一适配

源：`artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/keygroup-lift-color-native36.blend`，SHA256 `ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6`。原Cat Rig CC BY4.0、Key Forty/COMMON280 CC0许可与之前署名沿用，源下载与源native均未改。

先只读量测case、68个键、所有旋钮/指标、双臂与render2实际index皮肤；再只实施一次布局：

- 只保留source白14–21与黑10–14（C#、D#、F#、G#、A#），其余source键仅在隔离副本hide，未删/重建。
- 13个原键统一world X×3.4，单白键宽15.3925→52.3345mm；八键组外宽442.06mm。原case world X×.7并中心归0，宽720→504mm，Y/Z轮廓不动。
- 保留原source两旋钮及各自指标，移至X±200mm，隐藏其余旋钮/指标。没有新材质或标签几何。
- 只移动原native `IK-MSTR-Hand.L/R` 的world X，将原index实际最低pad对中两个端键；不改变wrist朝向、finger控制、pole、Y/Z、骨长或mesh。

## 实测结果与实际看图

`candidate-probe.json`：双腕reach均91.472%，原臂段长约121.973/122.786mm保留；双index准备位表面间隙分别2.90483/2.90471mm，左右各642个pad点垂直投影到各自目标。完整hands/arms/body/head/legs对18个可见琴组件的三角相交均为0；13键对case相交0。此检查没有证明完整实体/连续轨迹，不把近触点当作按压动作已过关。

Builder实际查看唯一完整彩色诊断：`artifacts/miao-eight-key-prop-probe-2026-10-30/eight-key-front-diagnostic.png`。大白键与2+3黑键分组更易读，双手在端键上方、原袖口连续；猫/全琴/支撑在同一完整场景帧。代价是双臂较原姿态张开、case从多八度MIDI变为短玩具控制器，须由独立评审判断是否自然。飞行员大头/服装/惊讶表情与原橘色梨形猫的身份差距完全没有解决。键宽增加也不自动让1.5mm键程的全景动作清晰；目前没有新clip或网页可验证此点。

诊断native `eight-key-isolated-static-native36.blend`，SHA `7179aa5967c7d01c735e63bfb419b3f69825b9fdd944d4f0ec230f740724b70e`；pose `40d5a61366db61d6149ad01d26f5ce4310dead1a7951fc5098620b5e1a7ae3fb`。再次禁脚本reopen检查原始mesh坐标/面拓扑/材质槽hash、对象/mesh/material/action数量均与ca5源一致；唯一pose basis变化仍只是两腕。新actions=0、newmeshes=0；源SHA前后一致。

## 保留的不确定性与下一步

- 原黑白键内部安装交叠没有被裁掉或偷藏；所有13键施加同一个可逆X仿射，因此继承的黑白键相交域没有被此次操作主动修复。此probe没有重新完整分类它们，之前near-boundary unknown仍是unknown，不能写成完整键盘机械安全。
- 原生render2匹配proxy不等于直接RENDER depsgraph。手腕/袖口原有缝合邻域、皮肤体积与支撑全域没有因本次三角外部0而获得全面安全证书。
- 脚本 `design/miao-reuse-keyboard-v1/probe_eight_key_layout.py` 支持`inspect / probe / verify`；使用官方Blender3.6.23、factory-startup/disable-autoexec，不运行上游embedded Python。没有多参数扫描，也没有第二个布局候选。
- root已要求将这个唯一候选提交正式灰模门禁：front/3Q/双掌/键前后低角，全部原材质保留，仅原生compositor灰度。灰门禁只审八键装配是否可保留，不借此解除角色production identity HOLD；三角色灰门禁后才考虑同pose彩色门禁，仍不扩动画。

## 正式灰模门禁证据已生成，待三角色判断

按root要求仅给这一个候选生成六图：`gray-gate/front.png`、`three-quarter.png`、`left-hand.png`、`right-hand.png`、`key-front-edge.png`、`key-rear.png`，全部由同一完整source场景拍摄，近景只供诊断。Builder已实际逐张打开；没有拿单一front图替代手掌或低角检查。此举不等于独立review。

灰native：`artifacts/miao-eight-key-prop-probe-2026-10-30/gray-gate/eight-key-gray-static-native36.blend`，SHA `42eae3f8eee59f60eeb8d1194f6d979ae55cf0e3140271eb5453be1b32c2fda8`，pose仍`40d5a61366db61d6149ad01d26f5ce4310dead1a7951fc5098620b5e1a7ae3fb`。脚本 `render_eight_key_gray_gate.py` 仅加入原生compositor RGBToBW，所有原source材质、mesh、pose与render subdivision保留；Quality1、use_simplify=False，每相机helper三个轴逐view同步误差0。6张SHA/相机信息在`gray-gate/inspection-manifest.json`，禁脚本复开PASS在`gray-gate/native-reopen-verification.json`；6图hash、源mesh/材质槽hash与pose均复核一致，source7179字节不变，原27个actions不增。

这些灰图只提交“八键装配能否保留”的窄门禁。角色原图身份、彩色材质工艺、任何新按压/八键动作/网页性能均未签；production identity继续HOLD。若三评发现新的严重露底、浮空、腕袖或非目标指接触，则停在反馈处，不用数值0覆盖视觉失败。未发布、未改public、未commit或push共享文件。

后续事实：灰门禁三角色均只允许保留本八键prop/准备位并进入同pose彩色；完整角色HOLD不变。同pose原色六图与复开证据已生成，见[彩色执行说明](miao-eight-key-color-static-2026-10-30.md)。这不是彩色三评已通过。
