# 零新增费用边界：仅本地发布配置与已有证据核查

2026-10-28。本轮只读Miao Beat当前工作区、既有Seed安全工作副本的git／`.github`／wrangler／package配置，以及本地历史发布receipt；**没有请求Cloudflare API、生产站、GitHub API或账单页，没有部署、push、付款或修改配置／鉴权／自动化。** 也未在本轮重查官方现行价目，因此不引用“静态一定免费”等未核实价格结论。私人付款信息仅在本地pending元数据，不进入本文。

**结论：本地证据不足以证明今后一次push／发布不会新增费用。Seed的main曾明确触发Pages自动构建；Miao的外部Git集成状态未知。现阶段继续本地Blender与离线证据整理，push／部署／可计量生产QA保留pending。**

## 本地能确认的触发与执行范围

| 对象 | 实际本地证据 | 能说明什么／不能说明什么 |
| --- | --- | --- |
| Miao Git／CI | 当前无`.github/`；有效`core.hooksPath`未配置，common hooks目录无自定义非sample hook。所查`.blend`的有效filter为unspecified，无`.gitattributes`／`.lfsconfig`。 | 未找到本地pre-push付费步骤、仓库内Actions workflow或该模型文件的LFS路由；**不证明**外部GitHub App、组织工作流、Pages Git集成或其费用已关闭。 |
| Miao package／发布 | `package.json`只有build／test／dev，没有deploy、postinstall或自动push脚本。README记录先构建dist，再显式`wrangler pages deploy ... --branch main`。`wrangler.jsonc`指定Pages输出dist和一个D1 binding。 | 已知本仓维护流程有显式上传；不能由此推出服务端没有另一个自动构建触发器。wrangler文件不含账户当期用量或总账单封顶证据。 |
| Seed Git／CI | 所查安全副本同样无`.github/`、自定义git hook或LFS属性。`docs/todos.md`P5明确记录Pages原生Git集成监听main；本轮此前的本地pending／receipt保留Git部署skipped、clone_repo failure和后续成功历史。 | **有已发生的main push→Pages自动部署路径证据。** 改docs或只加状态事件也不能擅自当成不会触发；当前云端watch paths／禁用状态未查询。 |
| Seed package／发布 | package内`deploy:public-site`明确先检查／构建再执行wrangler；build本身是Python本地生成。 | deploy脚本是另一个明确发布入口。没有本地Actions workflow不阻止Pages自己的云端构建，也不等于构建分钟／相关服务收费范围已核验。 |

本轮没有执行git网络动作。有效hooks检查覆盖当前git配置，而非只看仓库局部配置；所查模型属性结论限该实际路径，不扩成所有未来文件都不可能使用外部存储。

## 为什么生产QA也不能笼统当免费静态访问

- Miao `public/_routes.json`仅将`/api/site-counter`送入Worker；其他文件走静态资产路径。`site-counter.js`在有计数器UI时会发GET或POST，worker读取／写入D1。`analytics=internal`和preview只改为**不增加访问数的GET**，仍有Worker＋D1读取，不等于零计量。
- Seed构建生成`include:["/*"]`的全路由gate，页面和JSON都先经过Worker；`tools/site-access.mjs`按认证分支还可能调用既有共享认证服务。401、200或只读请求都不能仅凭HTTP方法推断无执行计量。
- 因此不为“验收一下状态页”额外发生产请求，也不关闭鉴权来规避成本。静态路由结构是代码事实，是否包含于当前套餐／是否overage是另一项账户与现行条款证据。

## 仍未知、不能声称已核验的项

1. 当前Pages计划、构建额度／已用量／剩余额度、watch paths和自动部署启停；GitHub组织／App级CI及其runner预算也未查询。
2. Workers／Pages Functions、D1、共享认证等服务的实际付费计划、当期总量、其他项目共用额度和超额费。
3. 是否存在能阻止**账户总账单**增加的服务商硬上限及其实际配置。源码中的单请求CPU限制、重试上限、告警或应用级计数，都不能充当总账单硬封顶；本地配置也不能证明供应商端已配置封顶。
4. 今后一次Git push是否会通过云端集成触发具有现金风险的构建／发布，当前不能承诺零新增费用。既有套餐／付款方式不等于无限计费授权。

## 现在的执行边界

- 可继续已安装Blender的本机建模、离线渲染、原图对照、非联网本地校验，以及把结果和状态事件保存在本地文件。只做本地commit与本次未发现付费hook的事实应分开描述，不把commit等同push。
- 暂不执行Miao／Seed的push、wrangler发布、可计量生产URL或账户审计调用；新状态事件保留pending，旧历史与已验收receipt不删。
- 本轮未暂停／关闭云端任何配置，也未核实account usage。若后续允许一项有明确零新增现金边界的核查，应先验证具体触发器和相关包含额度／风险，再决定是否恢复发布；不能仅因“以前成功过”“是小改动”“只有静态文件”放行。

本地依据：Miao `package.json`、`wrangler.jsonc`、`public/_routes.json`、`public/_worker.js`、`public/site-counter.js`、README；Seed对应package／wrangler、`tools/build_public_site.py`、`tools/site-access.mjs`、`docs/todos.md`P5，以及本地character-quality pending与生产receipt。没有将这些文件误标为现行官方计费文件。

## 后续root窄范围核查：仅同步研究checkpoint的规避路径

这是对上面“尚未查询”的追加，不删除历史。root随后只读GitHub：当前Miao远端main仍为 `1b71f6693452dbdd45d4f523fc1a343a53efde17`，仓库Actions workflow清单 `total_count=0`，该commit check-runs也为0。本地仍无自定义push hook/LFS。未访问Cloudflare账户、Worker或D1。

同时核对现行[Cloudflare Pages GitHub官方说明](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/#skipping-a-build-via-a-commit-message)：commit message以`[skip ci]`等指定标记开头会省略该次Pages部署，大小写不敏感；不是关闭长期自动化或总账单硬封顶。本次研究代码/文档Git同步采用这个前缀，既不调用wrangler，也不增加生产访问QA。同步后仅确认Git远端及GitHub运行记录；未将同步解释为已上线或整体费用恢复。

这个窄路径只用于已有授权的研究checkpoint，不覆盖未来真正发布、Worker/D1执行或其他未知服务用量。新角色尚未通过美术/动作关，因此也没有理由触发生产替换。账户费用边界与状态页发布继续pending。

## 2026-10-29：用户明确请求三版对比后的静态例外

本次重新核对[Pages Functions定价](https://developers.cloudflare.com/pages/functions/pricing/)与[调用路由](https://developers.cloudflare.com/pages/functions/routing/)官方现行文档：不触发Functions的静态资产请求，在免费/付费方案下均不按请求收费。它不等于账户总账单硬封顶。

允许的窄交付是 `/labs/character-compare/` 与5张拥有权实图、证据JSON，展示原版/Blender/Godot及制作中缺口。页面无访问计数script、无fetch/iframe/外部服务，不自动调用API；`_routes.json`仍仅include `/api/site-counter`，本对比页及图片均不在其中。Wrangler身份已核实，采用本地构建和直接上传，不启动Git CI；commit仍用`[skip ci]`。不调用D1、counter或更改套餐/绑定。

发布前用静态 `release.json`核对原253个生产资产与本地构建全部hash一致，仅增7个静态对比文件，避免覆盖别处上线修改。普通Python UA读取该文件403，curl标准客户端成功；未使用鉴权绕过或关闭任何保护。

这只核实本次静态对比页面的增量路径，不覆盖原应用计数API、Seed全站gate、其他应用共享用量或总账单。新模型仍未通过整体美术/动作关，比较页是用户请求的审阅入口，不替换正式角色。Seed状态事件仍先pending，不能因本页可静态发布便宣称所有服务成本问题解决。
