# C37 右拨弦爪：同拓扑局部雕刻失败记录

C37 是一组 reference-driven 候选，输入 C35 冻结 native。先实看原始 `idle.jpg`、C35 完整 front，以及本次只读新渲的右爪近景、侧景。解剖右拨弦爪在画面左侧音孔上方；画面右侧握琴颈的是 C35 左爪，不能反过来。

当前右爪末端是厚楔形，两条布尔方口槽没有形成参考短圆趾的结构。候选仅对掌端做有限边界平滑公平化，再沿掌轴给两个宽浅 web setback，稍收厚度与横宽；不新建 primitives、不 remesh、不增加独立爪 mesh。修区、锁区、完整位移与 source IDs 保存在脚本、README 与 `authored-delta-and-locks.npz`。

唯一候选修改 16989 点，实际最大位移 0.0608297u。左 C35 全点、修区外、全部吉他几何/变换/可见性、全部整数点属性/source IDs 均 exact；完整 body 拓扑不变、单连通、无开边、无非流形边。

但真实几何门槛失败：受影响实际三角面与完整 body 的非邻接 self45，局部 polygon self 从 baseline5 变23，577 个受影响三角面相对原法线反向。不能把 winding flip0 或单连通当 self0。已保存失败 native `diagnostic-c37-gate-failed.blend` 和原始 receipt，未渲候选灰图，也未运行第二组雕刻参数。

实际琴三角面碰撞同时揭示 baseline 隐患：右爪局部与 spruce soundboard472对、rosewood body248对；候选465/238对。六弦实际 tube 都为0。减少穿琴对数不能称接触通过，之后的静态重建必须把真实 soundboard/body 外侧纳入约束。

对唯一操作做只读分解归因，结果见 `failure-attribution.json`。该文件不会保存或渲染另一个候选。首次只读脚本在切换 native 后引用失效 RNA 名称报错，日志保留；改用固定对象名后重跑，只读源/失败 native/receipt 哈希保持。

只读分解得到：baseline 实际 triangle self9（7 polygon pairs）；只保留公平化分量时 actual self0，但有267个相对旧 normal 反向。这可能包含旧折皱展开，不能单靠相对原 normal 判定真实新倒面；winding 一直保持。最终再次施加按旧 P 坐标计算的 web/厚度位移后 actual self45（26 polygon pairs），集中在 x[-.536735,-.462834], y[-1.306946,-1.072932], z[1.612485,1.665547]。这定位到对已公平化 Q 仍使用旧 P 参数的形变不一致；不是同拓扑本身不可能的证明。最终 native 与 fp32 delta 重建误差另记，不以重建替代 native 主审计。

此候选不具备灰模三评资格。下一方法应基于公平化后真实表面坐标施加可逆、限制 Jacobian 的有界形变，并加入实际 soundboard/body 外侧约束；若局部仍不满足再用保留臂根共享边界的局部 cap 重拓扑。不要继续平滑强度/深度参数扫。具体范围以只读 source IDs/坐标为准，不能影响左 C35 与头身分支的 exact 合并。

无颜色、毛发、骨骼、动作、GLB、公开发布、部署或新增现金支出。C35 输入保持冻结。静态失败模型不能进入动画扩展。
