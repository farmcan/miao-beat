# C23r2：切线／减边修正已出图，横唇仍待独立门禁

2026-10-29。按实际磁盘恢复，旧进度“尚无新图”已过时：r2 的 build.log、receipt、native 与 front/inside/three-quarter 三图均已在 10:31–10:32 生成。本次没有重建相同候选；核对当前脚本 SHA 与 receipt 完全一致后冻结 executed-script.py，并新增同 native 的只读 seam/contact 审计。

证据目录：`artifacts/character-paw-plane-source-c23/r2/README.md`；native SHA `5f3f235aa0ea51f40c264ed80d91f9147e74e514002d85956fc66d026d5bfdda`。r1 历史与原始三份拒绝报告保留。

工程：最终590793点/590465面、单连通闭合；actual wrist+upper及邻接原C8 collar均self0/flipped0。585434原C8点、198源口、1419实际upper点bit-exact。min(1−κr)=+.23948，rail反向0；末端导数投影点积近0只是对源插值normal的近似切向条件，不等于最终离散mesh真正C1/C2。

修正将最后50→42移至u=.90，以u=.925后的Hermite趋近源切线。upper接口二面角median由31.29降至17.59°，p95由55.82降至42.20°，但max仍57.84°；wrist内部max165.81°。更关键的是8个实际helper新中点相对已知loft曲面proxy的最大偏差从r1约.01753增至.02273u，说明减边仍破坏预定表面。数值改善不能抵消图像横唇。

Builder实看批准idle、r1 inside和r2全部三图：短圆趾及掌腕一体的进步保留，横台沿有所减弱，但inside仍见趾根横唇/左夹点，3Q整帧仍有接线，掌面纵线也未清除。此为builder自检，不代替独立身份/工艺/动作三评；本次没有宣布灰模放行。

同SHA接触新审计：36点29背hit/7miss/5负gap，三指定第三弦趾腹仍为-.006701/+ .053717/-.007380u，下缘支持+.048579/+.069832u。只说明有限显式射线所见；不把命中数、正gap或self0叫握持已通过，不要求六弦全压。native字节未变。

**若独立评审仍判横唇P0，下一步换局部表面结构，不再扫Hermite或挪同一减边带参数。** 在实际upper邻接上重建跨切口的共享quad过渡带，锁源根和趾尖，允许窄趾根带双侧调整；以相邻真实面的切向和局部曲率约束公平曲面。所有新增减边点由已知参数曲面求值，不能留helper弦中点形成凹夹。先做窄patch、self/face-normal和同机位灰模独立三评；这只是具体方案，尚未实施或验证。

未新增第二候选，未改毛发文件/颜色/动作/GLB/引擎/Cloudflare；没有新费用。旧绑定失效边界保留。父任务负责公开状态事件与独立三评结论；不能把本地恢复当生产交付。
