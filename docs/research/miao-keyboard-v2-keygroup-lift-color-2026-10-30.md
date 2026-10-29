# v2 键组抬高 · 同姿势默认色静态

2026-10-30。灰 identity/craft/motion 三方均 GO 后，仅将 compositor 的 RGBToBW 输出改接原 RenderLayers。默认 CCBY WingIt 毛色、服装、眼鼻口，CC0 KeyForty/桌 PBR 原样保留；没有重新调色、遮缝片或新增支架。

9 张图全部完成并实际查看：front、three-quarter、face、left-hand、right-hand、key-rear、key-front-edge、feet-support、support-side。相机/分辨率与本轮灰版一致，每次 camerahelper 同步误差 0。front/3Q 包含完整连接猫、双掌与整琴/承托；其余为诊断，side 继承尾端裁切，不作生产整帧。

Builder 未观察到新增 P0：原眼口正常，双腕袖口连续，手指分叉清楚，键盘与桌/脚支撑关系不变。低角 front-edge 的窄连续暗缝仍明确可见；默认色下没有加遮挡，保留为独立 craft/motion 的 P1 复核点。此自查不替代三方 color gate。

Blender 3.6.23 factory/disable-autoexec 顺序重开灰源与彩色副本 **PASS**：pose `6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b` 完全一致；全部基础网格/材质槽、材质节点及输入值、除相机/helper 外全部 world matrices、68 键彼此关系、原细分设置、环境、27 个原 actions 均相同。Quality1、simplify=False、作者 render_levels2 保留。新增 actions/keyframes0，未选表情、按键或头动。

灰源 SHA `bf893762d45c3210c845c28d8c290eb7d720fc875a089bbfda109349e61be28f` 前后不变。彩色 native SHA `ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6`。本轮只恢复颜色，复用灰版 render2 匹配 proxy 的接触证据；直接 RENDER depsgraph 不可得、继承白黑键机械重叠和 near-boundary unknown 继续保留，不声称已通过按压或完整连续运动。

输出 `artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/`：`inspection-manifest.json`、`default-color-receipt.json`、`native-reopen-verification.json`、9 PNG、`keygroup-lift-color-native36.blend`、`SHA256SUMS`。脚本 `design/miao-reuse-keyboard-v1/render_keygroup_lift_color.py` 和 `verify_keygroup_lift_color.py` 复用既有流程，root 由脚本相对路径求得。CCBY 模型/纹理归属、CC0 乐器/桌和项目 MIT authoring code 仍分项保存在 `artifacts/miao-reuse-keyboard-v1/licenses/`，原下载包未动。

当前：**待三位非 builder 默认色静态评审；未开始单键动作或公开替换。** 两个 Blender 进程顺序运行且已全部退出，释放评审 slot。
