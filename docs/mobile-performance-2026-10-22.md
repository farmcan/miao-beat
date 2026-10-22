# 手机与全屏演奏 · 2026-10-22

用户追加要求：手机能玩、提供全屏能力，让琴键和鼓垫更容易按。范围是已有轻量乐器工作台，不增加音游轨道或重型编辑器。

## 做法

- 一个“全屏演奏 / 退出演奏”按钮。浏览器支持且允许时，在实际点击手势内请求元素全屏；失败或不支持时保留占满页面的演奏区。原生退出事件与按钮状态同步，页面模式也能按 Escape 退出。
- 不强行锁屏幕方向，不借视频全屏伪装交互全屏，不把浏览器地址栏隐藏能力当作所有手机都支持。
- 手机琴键不再挤成窄小按钮。白键目标至少52 CSS px，黑键至少44px；竖屏横向移动键盘，横屏展开更多键。鼓与和弦垫目标至少56px高，退出入口一直可达。
- 使用 safe-area / 动态视口单位，演奏区本身可滚动；保留节拍器、乐器切换与记录入口。

## 依据与适配边界

[MDN requestFullscreen](https://developer.mozilla.org/en-US/docs/Web/API/Element/requestFullscreen) 说明该调用需要临时用户激活，返回Promise且可能拒绝；[fullscreenchange](https://developer.mozilla.org/en-US/docs/Web/API/Document/fullscreenchange_event) 用于感知用户/系统退出。使用特性检测和实际调用结果，不按UA猜测。

[WebKit Safari26.4说明](https://webkit.org/blog/17862/webkit-features-for-safari-26-4/)提到iOS Fullscreen与硬件键盘状态相关的修复；[WebKit跟踪项206854](https://www2.webkit.org/show_bug.cgi?id=fullscreen-ios)仍有iPhone非视频全屏的限制反馈。这些不能推导为所有iOS都支持或都不支持，产品必须提供可退出的页面内fallback。

## 验收方式

既有浏览器viewport override未产生预期尺寸。为避免假称手机实测，使用同源开发检查页中的390×844、844×390 iframe，让真实Chromium按两个实际CSS视口渲染；iframe禁用原生fullscreen，专门检查页面fallback。另在顶层页面检查原生请求与拒绝后的退出路径。当前自动浏览器请求被TypeError拒绝，页面fallback仍正常；当前原生手势测试条件未具备，因此不声称原生手势已实测。检查页不进入部署白名单。

改版前在390窄视口实测：白键37.72px宽、黑键24.65px宽。改版后390视口实测白键73.71px、黑键44.29px；吉他和弦约87.5×60px，844横屏演奏鼓垫约198×64px。高C可横向滚动268px到达并实际点击发声（peak.01608）。顶层页面fallback进入/退出点击通过，iframe内Enter/Escape退出通过；该自动工具在iframe里点击fixed按钮未触发，尽管DOM命中是按钮，因此不将该动作记为触屏通过。iframe布局检查不代替iPhone/Android实体触屏、原生浏览器栏、刘海和声音延迟实测。

原生API回归覆盖拒绝/不支持、原生退出事件、按钮退出，以及“ESC取消后请求晚到成功”的竞态；晚到全屏会主动退出，界面不会错误停在关闭状态。29项测试通过。手机实际触屏、多点触控、原生浏览器栏和声音延迟仍待设备验证。

## 生产交付

最终产品commit `cfb1618a7b5e344404b0110964932c9dd42f0b35`，Cloudflare Pages `18c54914`。canonical release与55个公开文件SHA一致（56项清单含配置文件）。实际线上页面进入演奏区、13个琴键、固定退出入口及点击退出均通过，新增生产控制台warning/error为零。脚本未就绪时入口先禁用，控制器装载后启用，避免慢网络下点击没有响应。

390×844、844×390的实际Chromium CSS渲染已经检查；横屏8个鼓垫最下缘375.39px，在390px视口内同屏可见。该证据是布局与浏览器交互验收，不能替代实体手机、原生手势、多点触屏和手机音频听审。
