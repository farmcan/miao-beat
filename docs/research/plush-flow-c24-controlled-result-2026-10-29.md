# C24受控方向试验：完成证据与否定结论

唯一艺术变量为原549根可见额头毛倾斜，307根完整45度，其余边界fade；数量、长度、半径、材质、灯固定。原生Rotate Hair Curves通过固定MIT bx_hair设置器调用，保留官方原生asset。

原节点会把缺省resolution变为显式INT CURVE12；零角对照实际最大位置误差2.3283e-10u、半径bit-exact、curve_type/rest/UV不变。因此使用1e-8u零角位置容差，显式记录元数据变化，不冒充所有byte相同。真正转向后检查根不移、原始曲线数据不变、段长相对误差界、radii不变、零角后的元数据一致、预声明旋转残差、采样皮肤和指定眼网格接触。

候选native SHA430b5a9be23c8806bc584df9c71e9d0a6d63a8dfbea95d2db27b4f3e13c0a875。保存后派生renderer因嵌套目录ROOT计算错误中断；没有重新生成同候选，只修派生renderer的仓库定位并在同一native完成一次128sample、seed17、同buffer noisy/denoised+AOV。原执行代码/失败/恢复记录都保留。

实际投影长度median约.488→.930px、低于1px比例89.8%→58.5%，hairAOV mean约.002783→.004610。三名非builder实看原图、控制、候选后仍拒绝毛感P0：方向有可测贡献，但beauty仍近光滑公仔。原C21眼堆栈只作控制，不据此推翻独立C20眼睛关。

后续C26固定局部密度反事实已另行执行并三评，不能把其输出混入本候选通过。两者均未扩全身、颜色组合、动作或生产页面。证据见design/character-sculpt-v2/evidence/2026-10-29-c23r2-c26/，实际native/EXR在artifacts/character-plush-flow-c24/controlled-native-run/。
