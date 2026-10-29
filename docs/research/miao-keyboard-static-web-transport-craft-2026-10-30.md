# KeyForty 静态 GLB 传输独立短评 · 2026-10-30

非 builder craft 角色实际查看三图：`default-color/front.png`，以及 `static-web-roundtrip-no-unused-colors/{evaluated-snapshot.png,gltf-reimport.png}`（均位于 `artifacts/miao-reuse-keyboard-v1/`）。未渲染或修改资产。

**判定：静态几何/材料传输 GO，可进入实际浏览器验证。** snapshot 与 GLB 重导入图中，青眼、双瞳/高光、粉鼻、灰手、蓝服红边、象牙键、深琴壳与木桌均保留；未见黑眼/手显著变暗的故障继续存在，也未见完整猫、双臂双手、键盘或承托部件丢失的新增 P0。与原 native front 的主要材质层级一致；两组图分辨率不同，本评审不声称像素级相同或所有角度均已验证。

只读 receipt 与当前实际 GLB：15,561,764B，479,354 tris，SHA256 `4ad3f506047e8094593fbf3f837f7c8d4d382e0e98740c9a41655b8eb2cc3f08`；实际 JSON 中 `COLOR_0` 为0，skins/animations均为0。receipt 记录源 shader 没有已连接的颜色属性用户、source/pose未变。原先未使用色层被 glTF 自动乘色的诊断，与关闭未用颜色导出后本轮实际观感恢复一致；这是传输修复，不是重画眼睛/改猫材质。

边界继续保留：源快照是匹配 render 设置的 VIEWPORT evaluated proxy，不是直接捕获的 RENDER depsgraph。glTF 不含原 AREA 灯，本次重导入控制环境另外恢复原灯/world，故阴影与颜色匹配**不能证明浏览器光照、色彩管理或阴影已通过**。没有导出 rig 动作，也没有验证浏览器加载、性能、按键或任何动画。

下一步应实际看浏览器中的同一完整场景，检查青眼/手色、缺件、键区、承托/接地与加载表现。当前 GO 仅说明值得进行该验证；不是浏览器通过、模型最终通过或生产交付。本轮仅新增本文档。
