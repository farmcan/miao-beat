# Native hair surface-deform isolated probes

Blender5.2.3/e13b728c6880 本机实际运行。只在 factory-startup 场景中建一个测试平面与两条4点native hair；不加载、保存或修改任何 Miao 资产，不做角色模型、不渲染。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  --python design/character-sculpt-v2/probes/native_hair_deform_probe.py
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  --python design/character-sculpt-v2/probes/native_hair_snap_probe.py
```

第一项手设根UV，第二项真实调用官方 `bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')` 创建根UV；然后都接官方 `GeometryNodeDeformCurvesOnSurface`。平面shape key旋转Y25°并平移(.13,-.07,.20)，8个求值后毛点与解析结果最大误差1.4901161193847656e-08。第二项operator返回FINISHED并实际产生FLOAT2/CURVE的 `surface_uv_coordinate`。

receipt快照保存在本目录。脚本重跑输出在忽略的 `artifacts/native-groom-binding-research/`，不会覆盖已提交快照。`local-native-hair-api.snapshot.json` 记录本机RNA和真实Essentials资产接口。微型probe不等于真实180k毛/609383点C5已绑定、通过性能或动画验收。

第三项 `native_hair_rest_attribute_probe.py` 在snap之前创建POINT自定义 `miao_rest_position`，毛根故意离测试面0.005u；NEAREST实际将毛根贴面，再执行同一旋转/平移Deform。求值位置对“先贴面再变换”的解析结果最大误差仍1.49e-8，自定义rest属性对原始快照maxdiff **0.0**。它证明微型场景内snap/Deform不会顺便重写自定义rest色场，不等于真实C5色场已验收。
