# D0.1：静态 rest-position 材质绑定小样

2026-10-28。**完成的是求值后表面属性存储、shader接线和两张静态对照；不是完整D0通过，也没有证明动态防泳动或毛根绑定。** Builder仅记录技术结果，后续独立评审另行执行。

输入为已评审C5可编辑母版 `miao-plush-static-study.blend`，SHA256 `d380a830212e3939d6276d4e575f0c11bcbbd4dae50ccfabf6e885112cbfe706`。root确认打包进程退出后才读取。试验始终在 `artifacts/character-sculpt-d0/` 的副本进行，输入SHA在结束时再次一致；不改母版、不替换public。

## 实际做了什么

- 在副本冻结猫体静态Boolean／Subdivision，以及两片coat上睑的Subdivision。所有相关modifier的viewport/render状态和层数原本一致；冻结前后求值mesh位置数组逐值相等。
- 在猫体609383点、两片上睑各3281点、native hair的720000控制点上，保存 `miao_rest_position`，类型 `FLOAT_VECTOR`、domain `POINT`。每点值为原始坐标乘真实 `matrix_world` 后的全局位置；不是近似爪中心、UV或统一零值。
- 原coat材质只有一条 `Geometry.Position → Separate XYZ` 输入。将它改为 `Attribute(GEOMETRY, miao_rest_position).Vector → Separate XYZ`，由此同时覆盖毛色色场和前臂world-Y／高度遮罩。没有修改木纹、灯光、相机或其他美术材质。
- 原来未接Vector的微观Noise/Bump仍保留C5行为；本小项没有把所有纹理坐标一并改写。

两张实际渲染使用**同一个冻结场景**、固定seed17、512×512、32samples：`baseline-position.png`使用原Position接线，`named-rest-position.png`使用rest属性接线。两次分别7.09／7.20秒，执行进程已退出0。保留180000根四点native hair，没有删毛或换成默认纯色。不是第三次重新渲染C5母版作基准。

## 像素对照事实

`pixel-difference.json`由Pillow+stdlib直接读取实际8bit PNG，没有新装NumPy。完整262144像素中：

| 指标 | 实测 |
| --- | --- |
| RGBA平均绝对差，量程0～255 | 0.00026512146 |
| RGB平均绝对差，量程0～255 | 0.00035349528 |
| RGB最大单通道差 | 2 |
| 有任意RGB差异的像素 | 272 |
| RGB差异大于3的像素 | 0 |
| Alpha最大差异 | 0 |

脸／上睑ROI最大差1；拨弦臂／腕最大差2；握琴爪最大差2；奶油腹部／短毛ROI最大差1。ROI坐标与完整结果在JSON和 `d0-rest-diff.py`中，未裁掉全画面结果。两图未出现奶油腹部或条纹被统一橘毛覆盖的明显回零现象。

这是一对固定seed静态图，未另测重复渲染噪声，因此不把微小像素差全部归因于shader，也不把它换算成审美分数。

## AOV失败与证据边界

尝试在同两次渲染中增加不接Surface的hair／rest审计AOV，但Blender5.2 FileOutput格式枚举只接受 `OPEN_EXR_MULTILAYER`，设置 `OPEN_EXR` 报错。按预定的有界fallback继续完成两张beauty，没有为了诊断增加第三次渲染。`receipt.json`保留原始错误，**没有hair专门AOV回读证据**。

所以当前能证明：四个对象的POINT属性真实存在且逐值正确；重开保存后的D0工程，其属性hash仍与生成时一致；材质输入确为具名属性；静态整体及局部beauty与Position基准近乎相同。**不能仅据此独立证明渲染器在每个hair着色点读取该属性的具体插值行为，更不能证明变形时不泳动或毛根跟随。** 该项仍需后续有针对性的证据，不能把诊断失败写成已通过。

源代码随后只修正错误路径：立即跟踪并移除未完成的FileOutput节点、临时AOV shader支路及ViewLayer AOV，防止后续复跑留下意外输出。对本次两个已保存blend也做了同样的CPU清理；`diagnostic-cleanup.json`证明清理前后Surface祖先图及compositor Image祖先图hash不变，追加GPU渲染数为0。重开final rest blend确认属性与接线仍在、诊断残留为0，见 `stored-rest-verification.json`。

执行时源快照保留为 `artifacts/character-sculpt-d0/d0-rest-binding.executed.py`，SHA256 `675d583cdd34edeed3bb670536f4fb947df27a634dd469be34b2e93447dc8d3d`；仓库脚本的差异只有这项非beauty错误清理。没有宣称清理后再做过GPU逐像素复验。

## 本地可编辑结果与复现

- `artifacts/character-sculpt-d0/miao-d0-position-baseline.blend`：冻结后的Position控制组。
- `artifacts/character-sculpt-d0/miao-d0-rest-bound.blend`：保存完整猫／双爪／琴／native hair的rest属性组。
- `artifacts/character-sculpt-d0/receipt.json`、`pixel-difference.json`、`diagnostic-cleanup.json`、`stored-rest-verification.json`和`final-receipt.json`记录实际结果、SHA和局限。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b \
  --python design/character-sculpt-v2/d0-rest-binding.py
artifacts/tool-cache/motion-venv/bin/python \
  design/character-sculpt-v2/d0-rest-diff.py
```

上述第一条会新渲染一对对照图，默认输出本地artifacts；本轮实际只执行过一对。Blender自带NumPy供其Python脚本使用，外部像素脚本只需已有Pillow。

未做骨架、蒙皮变形、闭眼、触弦、网页或媒体导出；没有把静帧近似一致写成这些内容通过。独立评审应按此范围比较原图、C5与这两张实际图，再决定下一项窄验证。

属性类型与shader向量输出的参考为 [Blender属性API示例](https://github.com/blender/blender/blob/main/doc/python_api/examples/bpy.types.Attribute.0.py) 和 [Attribute Node官方文档](https://docs.blender.org/manual/en/latest/render/shader_nodes/input/attribute.html)；文档支持不代替本机hair渲染实测。
