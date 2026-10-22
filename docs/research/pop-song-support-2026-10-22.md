# 三首现代歌曲接入核验

日期：2026-10-22。对象按用户指向固定为青蛙乐队《小跳蛙》、伍佰《挪威的森林》、李晓杰《朋友的酒》。仅研究，不修改运行时；没有下载、转录或再发布完整现代旋律、歌词或录音。

## 当前可交付的边界

三首都找到可辨认版本及平台来源；**尚未找到明确允许本项目公开再分发完整旋律谱/编配的授权**。不是认定不存在此种授权，也不是把售卖谱本说成盗版。当前能快速落地的是官方试听/原曲入口，以及用户自己演奏、导入本地作品的既有功能；不能把这个包装成“三首歌曲已内置可跟弹”。

| 歌曲 | 可核的版本来源 | 调性、音域现状 | 可复用路线与未完成项 |
|---|---|---|---|
| 小跳蛙 | [Apple Music 专辑版](https://music.apple.com/us/song/1713919241)，青蛙乐队、《我们爱音乐》、平台标 2009-01-01；[Shazam](https://www.shazam.com/song/1712287252/e5b08fe8b7b3e89b99) 列彭钧/李润与 BPM 117。另有同歌手单曲版本，勿混 ID。 | [编配者在售谱](https://www.guitarworld.com.cn/pu/q75829) 标 C 调；[另一上传者](https://chord4.com/tabs/24356) 标原调 C。这是第三方标注，非发行方确认。全曲人声最低/最高音 **unknown**，没有用调号推音域。 | Apple 官方提供嵌入播放器机制；本歌专辑/曲目入口已核，具体账号/地区播放尚未实测。适合后续取得授权后先做单线短句入门版，不先假设全曲能塞进 C4–C5。 |
| 挪威的森林 | [滚石官方 MV](https://www.youtube.com/watch?v=gPpZJlE0Ca8)，发布 2012-05-21，频道为滾石唱片 ROCK RECORDS；说明列伍佰词曲。[官方艺人频道的发行音源](https://www.youtube.com/watch?v=yov7SJrzwa8) 标 1996-06-18、Magic Stone Music。不是 Beatles 的 Norwegian Wood。 | [制谱者在售谱](https://www.guitarworld.com.cn/pu/q178909) 标原调/选调 G、4/4、67 BPM。另有编配页标 112 BPM，说明版本/计拍不能混用；未经原音源节拍核对，不把某个数字当全曲精确时基。完整人声音域 **unknown**。 | 官方 MV 的 YouTube oEmbed 已实测返回 iframe。后续若拿到准确授权谱，优先吉他分段和弦/扫弦版；当前四个和弦键不足以宣称支持原曲。 |
| 朋友的酒 | [发行方供片 Topic 音源](https://www.youtube.com/watch?v=Z05PqxeRqZM)：李晓杰、Provided to YouTube by 青火音乐、℗ 青火音乐、平台标 2010-02-13、阮汛词曲。[Apple Music《老大》版本](https://music.apple.com/us/song/1834904921) 同日期。选择李晓杰原版，不混任贤齐翻唱或 DJ 改版。 | [楚唯吉他在售谱](https://www.guitarworld.com.cn/pu/q67405) 标原调 A、G 指法 Capo=2、4/4；页面明确编配有删改、旋律“大体一致”。完整人声音域 **unknown**。 | Topic 音源的 YouTube oEmbed 已实测返回 iframe。适合将来在准确谱源与授权齐备后做吉他节奏版/旋律分句；鼓组可自由伴奏，但未核对原曲鼓谱，不冠以“原版鼓谱”。 |

## 可直接复用的官方播放器

### YouTube

[官方嵌入说明](https://support.google.com/youtube/answer/171780?hl=en-GB) 与 [IFrame API](https://developers.google.com/youtube/iframe_api_reference) 提供现成播放器，不需要下载音源、引入代理或搭建播放服务。

2026-10-22 用 `curl` 请求官方 `https://www.youtube.com/oembed?url=...&format=json`，下列两项均返回 JSON 的 `type:video`、正确曲名/频道、`html` 中的 iframe：

- `gPpZJlE0Ca8`：滾石唱片 ROCK RECORDS，《挪威的森林》官方 MV。
- `Z05PqxeRqZM`：李晓杰 - Topic，《朋友的酒》。发行信息由该平台曲目说明提供，并非把所有 Topic 内容泛称唱片公司官方 MV。

此结果验证“官方端点接受并提供嵌入代码”，**不是浏览器已成功出声**。实际播放仍受内容所有者设置、登录、地区和用户网络影响。内容失效时回退到原平台链接，不能绕过限制或换第三方盗链。没有把 B 站标题写“官方原版”的个人搬运账号当官方来源。

若接入，用用户点击后才加载的可见播放器；保留平台控件，不遮挡、抽取纯音频或隐藏播放。[YouTube 最低功能要求](https://developers.google.com/youtube/terms/required-minimum-functionality) 规定嵌入视口至少 200 × 200，并要求 Referer。本站当前 `Referrer-Policy: strict-origin-when-cross-origin` 可保留；当前 CSP `default-src 'none'` 未开放 `frame-src`，必须仅对白名单播放器域调整后做线上浏览器验收。静态 iframe 不必加载 IFrame API；没有可靠音频时钟同步时也不承诺原曲与本地节拍器精准锁拍。

### Apple Music

[Apple Support：Share music from Apple Music on the web](https://support.apple.com/guide/music-web/share-music-apdm0783785d/web) 明确提供 Copy Embed Code；[Apple Music for Artists 的播放器说明](https://artistsupport.cdn-apple.com/support/1117-apple-music-marketing-tools) 说明未登录可预览、登录订阅者可听整曲，具体仍取决于账号/地区。

《小跳蛙》选择专辑版 ID `1713919241`，专辑 ID `1713918737`，不要混成同歌手单曲版 `1712287252`。建议从 Apple 的 Copy Embed Code / Marketing Tools 取得实际代码；本次只验证了曲目页面与 Apple Web Embed HTML 可响应，没有在浏览器完成登录、试听或三端播放。官方嵌入能力不等于本站获得旋律谱、录音文件或歌词的再分发权。

网易云/QQ 音乐本轮没有核到针对这三首且可实测的官方 iframe 代码。没有采用网上互相矛盾的第三方教程，也没有把普通歌曲页强塞 iframe。

## 谱源与授权缺口

吉他世界的上述三页是制谱者自己的在售条目，可据此联系编配者讨论接入；购买条目主要显示个人查看/打印等服务，没有发现公开网站再分发、转成机器音序、再授权给用户、开放源码打包的许可。只标“免费谱”“学习交流”或收到个人购买 PDF，不能自动推断这些权限已经覆盖。

《小跳蛙》的权利信息还有历史公开记录：[北京市文化娱乐法学会的案例分析](https://www.yulelaw.com/law/law/getContentDetail?id=7ae9a3b64ca146a7a8b4909b82e27626) 涉及麒麟童公司的录音制作者权，[判决全文转载](https://m.thepaper.cn/baijiahao_8057634) 记载作者转让及专辑来源。这是历史案例资料，不能据此断言 2026 年所有权利仍由同一主体持有或已经取得许可；它足以说明不可将本曲按公共领域童谣处理。

未来若要公开内置，需要实际核实：词曲相关权利的授权主体、所用编配者的新增表达、网页公开展示/转调/机器演奏/录制文件分发的许可范围。当前三项均是 `public_score_license:unknown`，不是已拒绝、不可授权或已获授权。本站采样包的 CC0/其他许可也不会顺带覆盖用采样演奏的现代曲目。

## 最小执行顺序

1. **现在可实现**：独立的“三首原曲试听”入口，明确歌手和版本，点击才加载官方播放器并提供原平台链接。继续保留自由演奏、节拍器、已有本地录制导入导出。这一步不占用 `SONGS` 的可跟弹选项，不假装有曲谱。
2. **技术可先完成且不依赖曲库许可**：让用户在本机录入自己拥有使用权的短谱/录音事件，再用当前引擎本地回放；不自动上传、不随部署打包、不建立用户共享歌谱库。现有时间+键码录制文件可复用，无需为三首歌新增重型编辑器。文件来自用户也不自动获得公开发布许可。
3. **有准确可用谱源以后**：逐首核对最低/最高 MIDI、半拍/切分/弱起、真实和弦与段落，然后选一段明确标注的旋律或扫弦练习。当前 C4–C5 单线只有一个八度：整体转调只能移动音域，不能压缩跨度；超范围需要用户选择换八度/扩展键区或明确“单八度改编”，禁止静默折叠后称原版。吉他当前只有 C/Am/F/G 四键，也不能用同一通用循环替代三首具体歌曲。

未做：原调逐音听审、完整音域测定、付费购买、联系权利人、浏览器实际播放、源码或生产修改。以上未验证项是明确交付边界，避免把“查到链接”写成“歌曲已接入”。
