# WingIt 相机 helper SINGLE_PROP 小型诊断 · 2026-10-30

**结论：失败，不采用。** 在 Blender 3.6.23、自动脚本执行关闭时，把 `HLP-scene_camera_dummy` 的三条 rotation driver 换成读取实际 Scene 的 `camera.rotation_euler[i]`，初始数值正确，但相机属性变化后 helper 未跟随。`is_valid=True`、`is_simple_expression=True` 没有证明数值正确。继续保留现用的每次渲染前手动 `camera.matrix_world.to_euler()` 同步；未保存或采用失败的驱动副本。

## 范围与输入

- 官方二进制：`artifacts/runtime/blender-3.6.23/Blender.app/Contents/MacOS/Blender`，实际版本 `3.6.23`，build `e467db79ca8c`。
- 输入：`artifacts/miao-reuse-keyboard-v1/render-quality-diagnostic/native-render2-working36.blend`。首选文件实际存在，因此没有使用备用文件。
- 输入 SHA256 前后均为 `118d520128f3bc48189010ed20df8a15a1df6789b796210d824527be5f415c2c`。
- 仅打开独立 `artifacts/miao-reuse-v1/camera-driver-diagnostic/input-snapshot.blend`，其 SHA 与输入一致；输入文件未保存、未修改。
- camera：`SOURCE-REST-INSPECTION-CAMERA`；helper：`HLP-scene_camera_dummy`。两者均 XYZ、无 parent、无 constraint、无 delta Euler rotation。原三条 rotation driver 均 muted。
- 使用 `--factory-startup --disable-autoexec`，并且 `open_mainfile(..., use_scripts=False)`；没有执行嵌入 source scripts，没有 `frame_set`、渲染、建模、动画或 location driver 扩展。

## 方法与数值结果

仅把三条已有 FCurve 的 driver 改为 `SCRIPTED`，每条一个名为 `var` 的 `SINGLE_PROP`：`id_type='SCENE'`、`id=实际 scene`、`data_path='camera.rotation_euler[轴]'`、`expression='var'`，然后 unmute。没有 TRANSFORMS 变量。

在当前相机和两组有限 Euler 偏移上逐轴直接赋值，调用 `camera.update_tag(refresh={'OBJECT'})`、`scene.update_tag()`、`view_layer.update()`，同时读取原 helper 和 evaluated helper。期望值为相机实际 `matrix_world.to_euler('XYZ')`；两种 helper 读取结果一致。全程仍是同一 frame 1。

| 测试 | 相对初始 Euler 偏移（度） | X/Y/Z 绝对误差（弧度） | 每轴 < 1e-6 |
| --- | --- | --- | --- |
| current | 0 / 0 / 0 | 0 / 0 / 0 | 是 |
| offset_A | +8 / −5 / +11 | 0.1396263838 / 0.0872664526 / 0.1919862181 | 否 |
| offset_B | −12 / +7 / −9 | 0.2094395161 / 0.1221730560 / 0.1570796371 | 否 |

两组变化后 helper 始终停留初始 `[1.2448705435, -0.0, 0.0]`。所有测试三条 driver 的 valid/simple 均 true，autoexec 均 false。恢复原相机角度后误差又为零；这仍不能补救动态跟随失败。本次没有进一步试验新的依赖刷新或驱动架构，也不推断所有 Blender 版本均有此现象。

## 不变项与复现

- `RIG-Cat` authored bone `matrix_basis` SHA256 前后均为 `f1eb1783be5bf370504980a57d2b5c5da2b0051d58750da8ec9ec081456d7bf0`，每组测试也一致。此处只证明 authored pose 未改，不冒充 evaluated deformation 验收。
- action 名称清单不变，keyframe point 总数前后均 `91596`；没有新 action 或 keyframe。
- 完整第二次诊断 Python 段耗时约 `0.664` 秒。首次在 offset_A 即退出；随后只把断言移到两组变化收集完后，补全失败证据，没有换算法。命令以 exit 1 明确表示测试失败。
- 脚本：`design/miao-reuse-v1/scripts/test_camera_single_prop_binding.py`。其中 binding 函数是**失败实验代码**，不可 import 进 active builder。
- 数值回执：`artifacts/miao-reuse-v1/camera-driver-diagnostic/receipt.json`；`passed=false`、`numeric_binding_pass=false`、`driver_flags_pass=true`、`rig_pose_unchanged_all_cases=true`、`source_unchanged=true`。

```sh
artifacts/runtime/blender-3.6.23/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --disable-autoexec --python-exit-code 1 \
  -P design/miao-reuse-v1/scripts/test_camera_single_prop_binding.py -- \
  artifacts/miao-reuse-keyboard-v1/render-quality-diagnostic/native-render2-working36.blend \
  artifacts/miao-reuse-v1/camera-driver-diagnostic
```

该结果只是安全驱动的小型技术诊断，不是角色、美术、接触或动画通过；没有恢复旧 primitive 猫或 Godot，也没有修改 active 原生文件、公共代码或公开发布。
