# 成熟模型单键网页实验 · 2026-10-30

范围：独立 `/labs/reuse-keyboard/`，A/C4 单键；不替换原版，不宣称八键、吉他演奏或最终角色设计。对比页增加明确入口。68 个独立琴键来自现成 CC0 Key Forty 模型，但目前仅第14号白键响应。完整猫、双掌、键盘和桌面由同一场景渲染。

模型来自 Blender Foundation Wing It! Cat CC BY4.0、Innerscene Key Forty 和 COMMON280 CC0；具体固定上游及改动在网页 credits.txt。成熟薄电吉他已单独清理与交接，但角色抱持仍未过接触验收，不因乐器精致而宣称吉他动作通过。

## 已验证

- v2 灰模和彩色同姿态均经独立 identity/craft/motion 三角色有限 GO；1.5mm 单键动作通过原生复开49帧核验。v1 键床碰撞失败留档，由全键组/手腕上移2mm的有界适配解决本次行程。
- 复用同一原生完整场景，将原生手部两个已验状态导出为 Contact/Down morph。只有一个原生手 mesh 形变，键14围绕已验原点转动；无分离手臂绘制、无额外角色几何。
- glTF unused Color 层会乘暗原来未读取该层的材质，已通过排除未使用颜色导出修复；未重绘眼睛或皮肤。
- WebGL GLB SHA256 `5c20616b3f7f1cbbdff257fb10729519c84eaf940bfee467803ba29fc5e0b69a`，17,144,124字节。网页按需加载，进入页面先显示完整静帧；图片与模型有独立署名。
- 真点击/持键→SampledAudio PCM与模型绘制；不播放包含200ms静止前导的影片。松开回弹，系统repeat忽略，重复按压有单次回提，停止清掉动作与声音；8个控制器测试及全仓126测试通过。
- root IAB 本机调整后：持住一次 inputCount=1、Down=1、theta=−.013393259rad、PCM峰值.0155103、CPU绘制提交接触48.7ms，松开量归0，随后750ms键盘A计数仅1→2、峰值.0160851，停止归零。该时间不是物理扬声器/GPU端到端延迟。
- 三独立网页评审允许仅实验页发布：[identity](miao-keyboard-one-key-web-identity-judge-2026-10-30.md)、[craft](miao-keyboard-one-key-web-craft-judge-2026-10-30.md)、[motion](miao-keyboard-one-key-web-motion-judge-2026-10-30.md)。原始网页偏小偏暗后做一次相机空间完整模型包围盒取景、曝光1.1与阴影强度.4调整；模型和动作轨迹未改。

## 仍未通过的目标

- 整体食指位移在完整全景中太小，生产反馈清晰度 P1/HOLD；不能用按钮亮色代替手部动作合格。
- 现成素材角色与原来橘色毛绒猫的外形/表情/短毛存在明显差距；不是身份定稿。头/眼/呼吸尚未扩展。
- 源黑白键内部安装近边界交叠仍存在有限分类 unknown；未声称完整机械模拟或连续全域碰撞证明。
- 17MB资源、479k三角形仍需设备性能优化；手机实机和物理扬声器未测。
- 该独立页暂未接曲谱、录制与导出；完整音乐功能继续使用原版。

## 可复现与发布

`python3 scripts/prepare-reuse-keyboard-public.py` 默认生成待审门禁；只有三角色网页评审完成后显式使用 `--web-gate experimental-page-go`。已实测待审状态构建被拒；构建核对精确模型SHA、内嵌纹理、无COLOR_0、唯一目标key/morph、资产指纹、公开文件白名单和隐私检查。仅 dist/ 发布到 miao-beat；正文和索引不得把本机路径/原始资料带到产品。Production active commit、正常与cache-busted canonical字节、CSP下真实载入/按压/松开/停止另记本机生产验收receipt；部署命令本身不算完成。

## 正式站验收完成

2026-10-30：生产 Active `d58c1711-de64-4e6c-8d6d-824c08c0c3f7`，source `8fd64a623a66f324e83d37c62cb17606635a15ef`（实现提交 `2809d69500fb545cad1890632afbbacb20ff555b`）。[正式单键试弹](https://miao-beat.pages.dev/labs/reuse-keyboard/)和[原对比入口](https://miao-beat.pages.dev/labs/character-compare/)已发布。

293个构建文件中290个公开source URL全部SHA匹配；配置文件 `_headers/_worker.js/_routes.json`不当作公开内容读取。六个正常/带版本查询URL（含17,144,124字节GLB、metadata、release与页面）字节一致。线上CSP仍self脚本/样式，仅本实验页允许blob图片/连接以解码内嵌glTF纹理；实际加载无控制台error/warn。首次旧verify helper未跟随Cloudflare的`.html`重定向，得到空redirect body导致误报；随后的验收明确跟随正常重定向并逐文件比对，全部通过。未用跳过失败路径来签验收。`scripts/verify-production.py`也已补上相同的`--location`，后续不再把正常canonical重定向误报为内容缺失。

IAB在正式URL重新开琴：短点击 inputCount1、maxRenderedAmount .999128、PCM peak .0155103、接触CPU绘制提交47.6ms，随后回0；持住 count2/Down1/theta−.013393259，松开归0；800ms物理A只增加为count3，PCM peak .0160851，松开回0；停止后latch=false、amount/weights/theta0、电平scaleX(0)。这证明当前单音功能闭环，不替代主观扬声器试听或最终动作美术验收。

本机证据在 `artifacts/miao-reuse-keyboard-v1/web-final/{canonical-acceptance.json,browser-production-acceptance.json,production-held.png}`；公开状态事件沿用既有Seed机制，独立交付，不宣布整个角色优化完成。
