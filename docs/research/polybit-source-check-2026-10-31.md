# _polybit_ 静态猫：取源前证伪清单

2026-10-31。用户进一步明确 3D 可以做到，问题在现有做法；继续优先成熟模型，不重造头身手。本次只补源路径和下一步判断，未下载三维模型，未执行生成或建模代码。

## 当前能证明什么

- [Cute Chibi Cat 原作者页](https://sketchfab.com/3d-models/cute-chibi-cat-8a7876b624554441b89926cfa380f36e)；此前取得的[官方公开 metadata](https://api.sketchfab.com/v3/models/8a7876b624554441b89926cfa380f36e)明确 downloadable、CC BY 4.0、商业可用、署名要求；作者文字明确静态无绑定。证据延续 `artifacts/free-chibi-native-scout-2026-10-30/`。
- 作者公开 profile API `https://api.sketchfab.com/v3/users/452733c0914c4421956ba2abd15beb01` 指向其[ArtStation 页面](https://www.artstation.com/digital_3d_vision)，没有因此发现合法直链原包或低模版本。
- 本轮文本浏览作者 Sketchfab 页返回 403，ArtStation 文本页无法访问。这是工具读取失败，不是源已下架、作者拒绝下载或全网无模型。
- 当前子任务没有可用 CUA 工具，已向 root 交接正常 UI 获取动作：打开作者页 → `Download 3D Model` → 检查原始格式/文件名 → 在既有登录及用户授权范围内正常领取。没有猜 archive URL、提取 viewer 流、注册、接受新条款或使用登录绕过方法。

## 拿到包之后，先回答这些再决定是否适配

1. 原包是否包含 `.blend`、未应用的 Subdivision / Multires、可编辑低模 cage？显示 156 万三角面可能是细分展示，也可能是固化雕塑，只有文件可区分。不能凭面数断言可直接用，也不能断言一定要重拓扑。
2. 完整身体是否存在？当前好看的作者图是脸/抬爪特写，完整腿、另一只手、肩肘、掌背和指根尚未实看。
3. 三个趾是分开的可弯网格，还是固定招手姿态的融合雕塑？掌垫看得清不等于指部可动。若需重造手，停止并换模板。
4. 肩、肘、腕和指根有没有足够轮廓/拓扑支持温和按键姿态？先灰模完整场景与双手近景三方评审，不能直接套自动绑定动作证明成立。
5. 源材质是否足以复现作者的 celshade / outline、眼神和毛色？作者预览不是本地默认灯光结果。缺贴图、版本或材质节点先记录，不用随意套材质掩盖缺失。

若只有固定高模雕塑、单一弯曲抬手或需大幅重构，则冻结该候选；它仍可作已授权 CC-BY 的视觉工艺参考，但不是成功模板。若保留好 cage、完整分指和源材质，则值得做**一次**静态原样导入，再做有限的材质/色彩和乐器布局适配。模型 gate 通过后才做动作。

## 可看效果的另一个明确参考，不冒充下载源

Juan Carlos CR 的鼓手猫成片：[作者 reel](https://www.instagram.com/reel/DcLCp78PeFT/)；[作者建模过程](https://www.instagram.com/reel/Db-IEa6voU0/)；[80 Level 报道](https://80.lv/articles/awesome-stylized-drummer-cat-rig-in-blender)。报道说明源设计来自 teretoast，且这一个猫 rig 不提供下载。它说明值得研究真实 3D 角色/乐器效果，不能被写成可复用的免费模型。

作者的[免费 rig 站](https://thedonutrig.com/)当前列 Donut / Donut Dog / Donut Sword；没有把别的免费角色冒称这个猫。文本工具打开 Instagram 被 throttled，本子任务未实播 reel 或评审动作。建议 root 有正常 UI 时先看成片及建模过程，区分雕塑体块、面部/指部绑定和最终灯材各自的作用；不下载作者未授权的源。

此外新看 productivminds 的[免费 Cartoon Cat - Rigged](https://www.cgtrader.com/free-3d-models/animal/other/cartoon-cat-rigged)：作者图是细长成人样身体、小头、圆鼠耳和直垂细手，不是成熟 Q 版可爱目标；虽列 Blender 2.8 / FBX、54k polygons，但仅凭免费和 rigged 不晋级。许可为 Royalty Free (no AI)，未取源或扩大解释许可。作者图留在同历史证据目录 `cgt-free-rigged-author.jpg`。

本轮没有新的猫源到手、没有 native/三评通过、没有动作、没有网页上线。root 统一记录公开任务状态。
