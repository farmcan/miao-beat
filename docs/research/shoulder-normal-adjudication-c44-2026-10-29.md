# C44：只读复核左肩的20处法线未知项

未改C40网格、材质或源文件，未渲新候选。源SHA仍为`6dbc4183a57117079c1479b0c1361e52995f66ff3eaef3f2d3e00e1cba8bdc00`。旧C40失败回执及两射线方向分歧全部保留，本记录是补充证据。

采用三角形有向solid angle求和除以4π，直接对实际保存重开的1,181,582个三角形用float64求值，不依赖BVH重复射线的步进。公式依据[van Oosterom与Strackee原论文](https://pubmed.ncbi.nlm.nih.gov/6832789/)，内外判定用途参考[libigl官方教程](https://libigl.github.io/tutorial/#signed-distance)。未复制上游实现，也未新增运行依赖。

先用已知外向四面体验证：内部winding=1，外部约1.1e-18。随后覆盖全部20处旧分歧三角形，分别在实际三角中心沿法线正负2e-6、1e-5、2e-5u测试。60对结果全部为外侧0、内侧1（误差门槛1e-6）；7个原本射线一致的控制三角形也全部通过。源文件前后SHA一致，运行27.53秒。

这解除的是这20处采样位置的未知项，支持C40左肩没有在这些位置翻到皮肤内部。不能推成全身无自交、工艺通过或动画通过。旧C40实际局部self18→0、单连通/闭合/一致绕序、54个琴组件无新增表面相交等证据与本项一起使用；原图匹配、接触和整只猫仍需独立评审。

源码：`design/character-sculpt-v2/shoulder-winding-readback-c44.py`。完整逐点回执：`artifacts/character-shoulder-c44-readback/receipt.json`。不覆盖旧`failed-geometry-gate.json`，不把只读复核写成新的模型优化。
