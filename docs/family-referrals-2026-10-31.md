# 三个猫咪项目的相互跳转记录

用户问题：不知道其他项目的入口有没有带来实际访问。假设：沿用现有互链，分开记录源站点击和目标站落地，能够判断值得保留或改善的入口。验收是三个项目的六个方向均有真实浏览器动作和对应生产内部汇总，不是只看到部署成功。

## 实现与边界

- `miaoti`、`miao-beat`、`miaotarot` 六方向；入口 `intro`、`result`、`family`、`unknown`。来源、目标由服务端的固定项目和有限枚举确定。
- `click` 是源站发生点击，`arrival` 是目标页加载客户端后报告到达。链接保留原活动名称，加上来源、入口。跳转不等待统计成功。
- 使用现有两个 D1 库，仅新增 `miao_family_referrals` 日汇总表；按北京时间分日，内部验收 `analytics=internal` 独立存储并随互链传递。普通访问计数在内部验收时只读。
- 不保存姓名、跨站身份、人格结果、塔罗问题、录音、原始 referrer、完整访问 URL、IP 或用户代理。不新增 cookie 或浏览器标识。原有项目自身统计不在本次重构范围。
- 这些是尽力而为的事件次数，不是人数、逐人轨迹或严格转化率。刷新及浏览器前后退不新记到达；屏蔽脚本、丢失 beacon、右键菜单跳转、去掉链接参数会造成缺失。显式来源标记可被人为修改，因此不是可信身份凭证。旧流量不能追溯补记。
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
