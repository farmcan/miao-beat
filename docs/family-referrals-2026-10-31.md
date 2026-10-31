# 三个猫咪项目的相互跳转记录

用户问题：不知道其他项目的入口有没有带来实际访问。假设：沿用现有互链，分开记录源站点击和目标站落地，能够判断值得保留或改善的入口。验收是三个项目的六个方向均有真实浏览器动作和对应生产内部汇总，不是只看到部署成功。

## 实现与边界

- `miaoti`、`miao-beat`、`miaotarot` 六方向；入口 `intro`、`result`、`family`、`unknown`。来源、目标由服务端的固定项目和有限枚举确定。
- `click` 是源站发生点击，`arrival` 是目标页加载客户端后报告到达。链接保留原活动名称，加上来源、入口。跳转不等待统计成功。
- 使用现有两个 D1 库，仅新增 `miao_family_referrals` 日汇总表；按北京时间分日，内部验收 `analytics=internal` 独立存储并随互链传递。普通访问计数在内部验收时只读。
- 不保存姓名、跨站身份、人格结果、塔罗问题、录音、原始 referrer、完整访问 URL、IP 或用户代理。不新增 cookie 或浏览器标识。上报使用 fetch keepalive + no-referrer，避免统计请求附带当前页面的完整查询参数。原有项目自身统计不在本次重构范围。
- 这些是尽力而为的事件次数，不是人数、逐人轨迹或严格转化率。刷新及浏览器前后退不新记到达；屏蔽脚本、丢失上报请求、右键菜单跳转、去掉链接参数会造成缺失。显式来源标记可被人为修改，因此不是可信身份凭证。旧流量不能追溯补记。
- 使用仓库既有原生事件、D1 原子 UPSERT、Pages Functions/Worker；没有为少量固定维度增加跨站用户分析 SDK。

## 查看

在 Miao Beat 仓库中运行：

```sh
python3 scripts/query-family-referrals.py --days 7
python3 scripts/query-family-referrals.py --days 1 --internal
```

需要现有 Wrangler/D1 权限。可用 `--wrangler /absolute/path/to/wrangler.js`。默认只读外部流量；输出六方向点击和到达、每日入口明细。任何库查询失败显示 partial/null，不把未知当作零。该命令及源文件不进入公开产品构建，不增加公开管理页面。

## 发布与验收

证据保存在本机 `artifacts/family-referrals-20261031/`；发布完成后补充实际提交、生产资源对应关系、六方向记录、窄屏真实浏览器和状态页验收。Tarot 的互链端到端用例同步更新；实际浏览器由 Codex CUA 操作，避免另启不受控的浏览器驱动。共同客户端的 DOM 行为在 Beat 与 MiaoTI 的既有 JSDOM 环境测试；Tarot 无 JSDOM 依赖，采用相同客户端 + 服务端契约单测 + 真实移动宽度检查，不为重复测试增加依赖。

独立技术 judge 未发现 P0/P1，并提出 beacon 无法指定 no-referrer 的非阻断建议；已据此统一改为 fetch keepalive，以减少统计传输中的页面来源泄露。

## 生产验收结果

2026-10-31 已完成三站发布与真实互链验收。运行源提交：Beat `a3e6bee`，MiaoTI `2127959`，Tarot `1f6096d`；对应部署 `a6ee929e` / `ae4063f0` / `22fd4b6d`。MiaoTI 使用主线隔离归档与临时索引提交，原有 `codex/meme-radar-lab` 的分支、索引、工作内容未切换或覆盖。

| 来源 → 目标 | 内部点击 | 内部到达 |
|---|---:|---:|
| MiaoTI → Beat | 1 | 1 |
| MiaoTI → Tarot | 1 | 1 |
| Beat → MiaoTI | 1 | 1 |
| Beat → Tarot | 1 | 1 |
| Tarot → MiaoTI | 2 | 2 |
| Tarot → Beat | 2 | 2 |

验收前新表为零；真实浏览器八次点击产生八次到达，分布在六个方向、12 个聚合桶中。外部流量桶仍为零，没有把测试当作自然用户。Tarot 在 320×568、390×844 两个真实视口分别点击两条链接，点击区域均为 44px，水平溢出为 0；截图与 DOM 证据保留于本机 artifacts。

Beat 全量 148 项回归通过，运输方式调整后五项相关单测再次通过；MiaoTI 站点、体验、计数、事件及五项新测试通过；Tarot 类型检查、计数与两项服务端契约测试通过，生产 smoke 通过。三端客户端一致，Tarot 移动端互链端到端用例已更新，真实执行使用 CUA，未另启 Playwright 驱动。

独立技术 judge：无 P0/P1。其建议已落实为 `fetch + keepalive + no-referrer`，避免同源统计请求携带当前页面查询内容。截图只是入口体验证据；真正记录成功的依据是两库生产查询与浏览器动作对应。
