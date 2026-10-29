# C54：实际运行修复后的完整合并器

继C47的独立真实源码片段审计后，再运行完整CLI：

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/merge-head-hand-c31.py -- --hand-blend artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend --out artifacts/character-head-hand-c54-import-regression
```

实际进程exit0，17个feature的世界矩阵与真实源scene exact。两盏光学灯world位置分别为`[.0573594,-3.1852694,4.1331711]`、`[2.3435838,-2.3930523,3.9913914]`，不再丢到原点。C35新手点与已保留头部点exact断言通过，完整源文件未修改。输出native SHA`d1290c1baa569f38fd2a617f6b3faa0e32ab3e97ab07ec85cb8d5f7630af5d65`，回执在同目录。

此项是导入回归验证，无新美术图、无绑定、无动画，也没有生产发布。第一次命令漏了Blender参数分隔符`--`，Blender在执行脚本前exit2；该日志保留，修正CLI后只运行一次。没有覆盖历史C31与其失败证据。
