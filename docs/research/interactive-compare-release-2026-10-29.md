# 原版 / Blender→Three / Godot 真实弹奏比较

## 可验收动作

入口： https://miao-beat.pages.dev/labs/character-compare/

打开声音，按 A S D F G H J K 或屏幕琴键：同一输入、单份采样音频，分别触发现有完整帧播放器、Three.js 实时模型和真正 Godot Web 引擎。提供 500ms/150ms 演示、停止、全身/双手/脸部、单独看、头部微动作开关和三维转动。旧静态比较保留在 stills.html。

## 实现与边界

- 原版直接 mountCharacter，共用线上完整猫+琴帧；只公开原有 reset 方法，不替换主站播放器。停止后原版保留原有抬爪 ready 姿态，3D回到零形变，两者rest姿态不同。
- Blender是作者工具；Three.js 0.186.1负责浏览器实时渲染。Godot4.7.2 Compatibility单线程是真Web导出，两者使用同一7.48MB GLB、20个形变mesh、五个权重。
- 形变是完整连续角色表面变形；没有把身体底图和分离手臂贴图拼成演奏。
- 3D是C20研究模型，去掉原生毛发并减面。毛感、头脸身份、分指、真实按弦接触均未通过生产美术gate。技术接入成功不代表原有P0已清除。
- 两个3D引擎接受同一权重，Godot约24ms更新一次。父端DOM pose是发送证据，不能充当Godot接收ACK。
- Godot压缩引擎10.05MB、PCK14.77MB，浏览器DecompressionStream恢复官方WASM；无新Worker/服务/付费接口。第一次Godot加载比Three慢。

## 已验证

- 构建283个显式允许的public文件；Godot逐文件hash与GLB固定hash检查。
- npm test 108/108通过，含10项共享motion controller测试。
- 实际IAB与独立Chrome输入：八键各一次+8、慢速演示+8、150ms演示+8、单击无多击；两种3D均真实出画且能动。Godot日志确认实际引擎、WebGL2、20个形变网格。
- 独立UX检查发现双手裁切，已统一缩放1.25并调整3D中心重新导出。Three已改用当前PCFShadowMap，清除废弃接口告警。
- 全身/双手切换已实际点击，Godot真实镜头同步变化。iframe不截获父页按键。
- 本机通过不等于手机扬声器听音、低端手机性能或生产美术验收。

独立评估：interactive-compare-engineering-review-2026-10-29.md、interactive-compare-ux-motion-review-2026-10-29.md。原有身份/工艺/动作生产拒绝见 production-comparison-*-2026-10-29.md。

## 参考与下一步

Viola the Bird最接近精致动物演奏目标；Three RobotExpressive可借鉴动画混合与表情形变；Bongo Cat可借鉴按键反馈。链接、代码检查和许可证边界见同目录 interactive-avatar-live-references-2026-10-29.md 与 godot-web-interactive-reuse-2026-10-29.md。

下一步优先修角色身份、连贯爪型与接触，再扩展手指与头部表演；单纯换引擎不能补足角色建模和动画设计。

## 线上策略修复

原全站CSP会阻止同源iframe和WASM，本机普通静态服务器未覆盖此项。已仅对/labs/character-compare/*配置同源frame和wasm-unsafe-eval，保留主站原策略。Godot启动脚本和CSS全部外部化，去除JavaScriptBridge.eval；不启用普通unsafe-eval或内联脚本。root严格CSP本机实测ready=true、20个mesh、完整角色出画、零warn/error。Cloudflare头部合并/移除规则依据 https://developers.cloudflare.com/pages/configuration/headers/ ，生产仍须验实际响应头和浏览器。
