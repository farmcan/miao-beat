# Miao Beat 累计访问计数

2026-10-25。实现与本地验收已完成，生产绑定、提交与发布由主线程统一完成；本文件初始记录不代表已经上线。

## 复用来源与口径

读取了本机 MiaoTI `functions/api/site-counter.js`、`site/main.js`、`migrations/0001_counters.sql` 与 `wrangler.jsonc`。该工作区 HEAD 为 `3603fa3e87b2c5c12b785ef454b7a274f5a7bc17`。MiaoTI 的生产 GET `/api/site-counter` 本次只读返回 count 1402；没有向 MiaoTI POST 或改其代码/数据。

MiaoTI 使用 D1 `site_counters` 的固定 key `site-visits`，通过 24 小时 HttpOnly Cookie 防止同一浏览器反复刷新加数，并让匹配的 bot 只读。其 POST 拒绝 cross-site，没有跨站写入的 CORS 能力。因此不能让 MiaoBeat 直接调用该站 POST，更不能借它的已有数字当作 MiaoBeat 访问量。

MiaoBeat 复用现有 `miaoti-stats` 数据库及已有表结构，使用独立固定 key `miao-beat:site-visits` 和独立 Cookie `miao_beat_visit=1`。不需要迁移现有生产表，不读取 MiaoTI 人格统计。计数从此功能启用起累计，没有补造上线前历史。

页面文案：`累计访问 N 次`，说明 `从启用统计起累计 · 同一浏览器 24 小时内计 1 次 · 非独立人数`。这既不是每次刷新都增加的原始 PV，也不是去重真人数。换浏览器、清 Cookie、隐私模式、并发首次请求和未识别 bot 都可能影响计数；本实现不是防作弊统计系统。

## 接线

- `public/_worker.js`：Pages advanced mode，固定 `/api/site-counter`，其他请求交给 `env.ASSETS.fetch`。
- `public/_routes.json`：只让该 API 路径进入 Worker，静态页面不增加 Worker 处理。
- `wrangler.jsonc`：沿用现有配置文件，新增 `MIAOBEAT_DB` 指向已存在的数据库；未创建服务、账号、权限或付费方案。该配置仍需主线程生产部署才能生效。
- GET 只读。POST 无正文且同源才可计数，D1 用原子 upsert；计数 key 不来自请求。Cookie 使用 HttpOnly / Secure / SameSite=Lax / 24 小时有效期。只校验本计数的固定标记，不把 Cookie 原文写入日志，不跨站搬运 Cookie。
- 预览域名只读，内部验收 `?analytics=internal` 前端使用 GET；非正式域名 POST 也不会写生产总数。本地 localhost/127.0.0.1 可写本机模拟 D1，未启用 remote。
- `public/site-counter.js`：独立异步请求，无正文、无演奏/录制/身份字段；不发送 referrer，5 秒超时。不阻塞音频入口，响应结构/数字非法或请求失败都显示 `累计访问：暂时未知`，不显示伪造 0。新计数尚无行时 GET 返回真实的初始 0，不等于失败回退。
- `scripts/build.mjs` 显式 allowlist 新增 3 项。只从 public 构建 dist，不部署仓库根。
- `scripts/verify-production.py` 跳过 `_headers`、`_worker.js`、`_routes.json` 这三个部署配置；其他文件继续做线上字节核验。跳过 Worker 远程源码字节不等于已核源码一致，API 行为需要另验。

官方依据：[Pages advanced mode](https://developers.cloudflare.com/pages/functions/advanced-mode/)、[D1 bindings](https://developers.cloudflare.com/pages/functions/bindings/#d1-databases)。已实际读取。使用 cloudflare-deploy 技能核对配置；没有在本子任务执行部署。

## 验证

- 首轮全套 `npm test` 为 52/52；真实 workerd 发现空 browser POST 可能为非空流对象，修正零字节判定并新增对应回归后，针对性计数检查为 8/8，最终全套为 53/53。`git diff --check` 通过。
- `npm run build` 成功，76 项显式 public 文件。
- 原有 Wrangler 4.112 本机 workerd 过旧；改用已有缓存 Wrangler 4.149，local dev 单独覆盖兼容日期为 2026-10-13（它本机支持的最新日期）。源码/生产配置仍为 2026-10-22，没有安装新版本或修改生产日期。
- 本机 D1 只在 `.wrangler/state` 建立空 `site_counters` 表。CLI 日志明确 binding Mode=local；没有 --remote。测试之前 GET count=0。
- 真实 Chrome 打开 localhost:8897：首次成功显示 `累计访问 1 次`；刷新后仍为 1，随后 GET 确认 count=1。390×844 CSS 视口下文字完整显示，说明不挡其他入口。没有读取浏览器 Cookie 值作为证据。
- 本地 API 带 `{}` 正文返回 400，计数仍为 1；跨站、方法、bot、preview、数据库缺失/坏值等由专门回归覆盖。
- 另一仅静态的本地服务器模拟计数 API 不可用：真实 Chrome 显示 `累计访问：暂时未知`；仍能准备钢琴并按 A，显示 C4 与非零电平。失败没有阻塞演奏。未据此声称物理扬声器听感通过。
- 截图在本地 artifacts：`site-counter-local-mobile-2026-10-25.jpg` 与 `site-counter-local-unavailable-2026-10-25.jpg`；不进入 public。
- 生产待验：正式 GET 与只读浏览器页面、普通真实访问后的 Cookie 去重、无正文/跨站拒绝、预览只读、静态页面与音色/视频仍正常、源码 allowlist 字节核验。不要向生产写测试用录制/虚构访客数据。
