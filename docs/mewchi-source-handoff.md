# Mewchi 源文件取得与下一道验收

2026-10-30。用户明确接受“Mewchi这类成熟Q版猫”，允许新的角色外形；没有授权购买或对外发信。本文件是具体取源准备，不是已经导入Blender、模型质量通过或动画完成。

## 已核实到的候选

[原作者商品页：Mewchi — drawforfood](https://booth.pm/en/items/4627622)。本轮正常浏览器实际查看封面、表情／手势图和裸身正背／灰色实体图；后两张解决了旧预览的“是否只有衣服身体”和“是否有不同爪指形态”疑问。

- 作者提供`.blend`、FBX、Unity包及纹理编辑资料；它们仍是作者声明，未取得文件，未验证真实骨架、权重和文件版本。
- 原作者实际图能看见张掌、指向、OK等不同手势，眼睛／耳朵的不同表情；图像不能证明单指骨或钢琴触达已通过。
- 当前页面个人版3,216 JPY，商业版7,712 JPY。仅为本次读取的标价；未创建订单、付款或接受购买条款。
- 作者的Unity展示依赖Poiyomi。Blender材质、眼睛与描边能否复现必须在取得源后实测，不能把作者预览当本地渲染。

三个非builder预筛在新的视觉范围下均为**有条件采购GO**：[身份／来源](research/mewchi-procurement-identity-2026-10-30.md)、[工艺](research/mewchi-procurement-craft-2026-10-30.md)、[手部／操作](research/mewchi-procurement-motion-2026-10-30.md)。只支持取源验证一次，不是原生角色gate或动作许可。

## 付款前需确认的具体用途

页面商业档列出商业VTubing、直播、YouTube及类似用途，同时禁止公开或分享模型。离线完整渲染帧用于公开交互音乐网页的范围未明示，因此当前不能直接把商业档推为本产品授权，也不准备公开可提取GLB。

[联系作者入口](https://drawforfood.booth.pm/conversations/new)已正常打开，当前会话重定向到BOOTH登录页，需BOOTH／Pixiv账户；没有登录、注册、勾选条款或发送消息。对外联系尚无用户明确授权。

可直接发送给作者的英文问题（尚未发送）：

> Hi! I'm considering the commercial license for Mewchi. I would like to use it in a browser music toy: modify and pose the character locally in Blender, render the complete character with a piano into 2D images or short clips, and display those renders in an interactive public website. Users could record their playing and download a video containing those rendered images and music. The original .blend, FBX, textures and any extractable 3D model would never be published or shared. Would the commercial license cover this use? If not, is separate permission available? Thank you!

保留作者回复和取得时的完整许可。若作者不允许该用途，不采购此源；不能用本站免费或公开帧而不是GLB自行推断许可成立。

## 合法取得后如何交给本项目

由有权取得资产的账户保留原始ZIP，将其置于本地忽略目录 `artifacts/private-source-intake/mewchi/`，不要提交源码包或向公开仓库上传。随后记录文件名／字节／SHA和取得日期，原包只读保留。作者规定双方持有许可的协作边界仍须遵守，不能将原包作为通用公共下载附件。

不要求提供账户、密码或支付信息。这里只需要依法可供本项目本地处理的原始资产和相应许可证明。

## 取源后的执行顺序与停止条件

1. 禁自动脚本只读打开，核对原生版本、armature、实际手／指骨、权重、shape keys、UV和packed图。不得运行未知插件或源内Python。
2. 用完整连接角色出默认原色、灰模front／3Q／侧面和脸／双掌近景。先审源本身；静态图每个阶段由三个非builder角色判断可爱、工艺和可操作结构。没有真实源不生成“通过”回执。
3. 用现成八键琴做一次完整场景静态准备位，不重建手、不拼分离肢体，不先作演奏动作。若只有整掌替换、需要新造指头，或手腕／肘需大幅重建才能够到键，保持HOLD。
4. 灰和着色静态三评都通过，才做一次触键—压下—释放，然后验证单次、持按、快速重复。头眼／耳的小反应随后进行，不按每个快音重置整个头部。
5. 交付完整猫／双爪／乐器的全帧结果并做真实网页按键验收；原模型留私有，公开输出范围服从确认后的许可。Web Audio、音符语义和只记录真实输入的约束继续保留。

本轮没有模型取得、Blender导入、动作或应用上线。现有单键技术实验与正式原版都未被该预筛替换。
