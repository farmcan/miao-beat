# 对比页按需加载修复 · 2026-10-29

## 问题与范围

原交互对比页打开时同时启动原版完整帧动作、Three GLB 与 Godot Web 导出。用户反馈打开慢，并明确舍弃 Godot 交互链路。本次仅修改 `public/labs/character-compare/` 的 `index.html`、`play.js`、`play.css`、`three-renderer.js`，增加相关 DOM 回归测试；没有改原版生产图片、GLB、建模或动作美术，没有部署或提交。

## 实现

- 交互页只保留原版和 Blender → Three 两路。删除 Godot iframe、运行时初始化入口、ready 消息/轮询、pose/view/orbit 转发。历史 `godot/` 导出、许可证、校验和静帧证据保留，构建白名单未变；保留的历史独立 URL 不等于当前交互页仍启用 Godot。
- 原版沿用现有挂载与动作准备方式。打开页面不会 import Three renderer/vendor，不会请求 GLB 或任何 Godot 文件。点击“加载3D对比”后才 dynamic import 并创建 WebGL renderer、下载模型。
- 三维入口显示尚未加载、加载中、失败/重试和成功状态；等待期间原版与共用声音可以继续使用。重复加载去重，失败实例释放后可重试；只有初始化成功才显示画布。失败后的重试入口保留。
- 加载成功时采样当下的 motion controller，应用当下视角、orbit、头部开关；不保存和补演下载期间的输入。停止时清空计时器、held、声音与动作。新增 demo 取消版本，停止、失焦或离开能取消仍在等待音色准备的演示。
- 首次按键若音色未准备好，明确提示该次未发声、就绪后重新按键；不排队延迟发声、不更换音色。
- 保留 8 个白键、4 个和弦、500ms/150ms 演示、停止、全身/双手/脸、单独看/两栏、头部开关、orbit。桌面间距与舞台高度局部压缩（舞台 38vh，有上下限），目标是在 1280×720 同屏看到整猫及键盘；实际几何与整猫裁切需要浏览器验收，DOM 测试不证明布局。

## 默认请求减少多少

下面是冷启动旧入口会触达、现在不点击 3D 就不会触达的文件。数量按源码入口推导，大小取当前仓库文件；Three renderer 取修改前 `HEAD` 的 3,965 bytes。它们是文件字节数，不是开启 HTTP 压缩/缓存后的线上 transferred bytes，也不声称已测到打开耗时。

| 默认排除的资产组 | 文件数 | 文件字节合计 |
| --- | ---: | ---: |
| Godot `index.html/index.js/index.pck/index.wasm.gz/compressed-wasm.js/godot-start.js/godot-page.css/index.png` | 8 | 25,138,156 |
| Three `three-renderer.js/vendor/three-runtime.mjs/model/miao-playable.glb` | 3 | 8,123,917 |
| 合计 | 11 | 33,262,073（约 33.3 MB / 31.7 MiB） |

其中四个主要大文件是 Godot WASM gzip 10,054,758 bytes、PCK 14,774,984 bytes、GLB 7,483,568 bytes、Three vendor 636,384 bytes，合计 32,949,694 bytes。Godot audio worklets 的条件请求未计入，避免把引擎的运行期分支假定成已测请求。

点击 3D 后保留的按需资源约 8.1 MB（GLB + vendor + renderer）；Godot 不会被该按钮加载。原版动作包/帧的加载方式未改，仍有原版资源开销，因此本次不是“首屏零下载”或完整资源预算优化。

## 本地验证

- `node --test scripts/compare-loading.test.mjs`：10/10 通过。
- `npm test`：118/118 通过。
- `npm run build`：通过，283 个显式公开文件，历史资产校验继续生效。
- 新增测试覆盖：无 eager Three/Godot 入口；原版 8 键/4 和弦不触发 import；视角/solo；加载去重；加载期间实际输入仍只发一份声音；下载完成仅同步当前姿态；模块/模型失败重试；500/150ms 节奏与停止；首次音色未准备不补音；等待音色期间停止；头部开关；下载中停止、失焦与 pagehide。

这些是可控音频/三维替身的 DOM 与调度测试，不证明 WebGL 真实渲染、听感、网络瀑布或真实浏览器几何。根任务继续做实际浏览器 QA、公开状态事件和后续发布；本记录不将构建成功当成线上完成。

## 根任务实际浏览器补验

- 本地IAB（1280×720）实际打开，两栏全身与8键/4和弦同屏；修复共享全帧挂载设置aspect-ratio后舞台缩到左侧的问题（舞台显式width:100%）。
- 初次未点3D时HTTP日志无Godot、Three runtime/renderer或GLB请求；冻结证据 `artifacts/compare-load-fix/before-3d-request-check.json`。
- 开音后一次点击输入计数只加1；150ms快演示共8次，停止显示无排队动作；再点击旧3D按钮实际WebGL就绪，之后一次输入提示两路同步。
- 旧自建3D明确标为已弃用。该性能修复不代表新复用角色已经上线或美术通过。
- 无移动设备扬声器听音结论，未测冷网下载时间。

## 生产验收

- commit `1330fa0a5eeec5e767e4588977601d40916f10fb`，Cloudflare Production部署 `59543d6e-bc1c-4486-981b-4102a7fe03e7`。
- canonical `release.json`与四个修改的公开文件逐字节SHA均匹配dist；普通canonical URL实际浏览器显示新两路页、旧模型弃用提示、3D默认未加载。
- 线上开音后150ms演示共8次输入，停止成功；截图 `artifacts/compare-load-fix/production-final.png`。没有把开发server速度当生产冷网耗时。
- `/api/site-counter`路由与worker代码未改；当前comparison为静态路由。
- 公开状态事件已持久化到Seed现有pending事件入口；Seed状态页尚未补发，覆盖缺口保留。
