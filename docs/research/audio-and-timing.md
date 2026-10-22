# Miao Beat：采样音色与节拍时钟研究

资料核对日期：**2026-10-22，Asia/Shanghai**。范围是独立网页乐器沙盒：跟节拍器自由演奏、摸索和创作。生日快乐、小星星、粉刷匠只作可看可不看的参考谱；不做瀑布谱、判分、连击或通关。本轮只写研究，没有替换音色、导入采样或实现录音/loop。

## 可以先定下来的技术边界

1. **换采样与换框架是两回事。** Bongo Cat的琴声确实来自音频文件，并非几根振荡器。改用Tone.js但仍放同样的简单合成音，不能称为已经解决音色问题。
2. **节拍器是稳定参照，键盘是即时乐器。** 二者共用一个AudioContext；节拍预排到音频时钟上，手弹不要等到下一个拍点才发声。
3. **优先候选是 smplr 1.1.0 + 自托管、许可明确的少量真实采样。** 先比较一套钢琴与一套真正的马林巴，再决定主乐器。鼓和吉他分别按需加载，不开局下载整套GM/管弦乐库。
4. **音色仍需听审。** 本轮核了原始资料、代码、版本、许可、文件体积；没有完成候选采样的手机扬声器/耳机A/B试听，也没有测物理输入到声音的延迟。下文的质量判断是候选理由，不能写成听感已达标。

## 1. Bongo Cat为什么值得学，但音频文件不能只看MIT

核查版本：[Externalizable/bongo.cat `591940644775d7cfd5167eceeeb6b97a1f9aadd4`](https://github.com/Externalizable/bongo.cat/commit/591940644775d7cfd5167eceeeb6b97a1f9aadd4)，HEAD补丁日期2023-10-14。

[`js/core.js`156–200行](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/js/core.js#L156)明确做了：预载`keyboard0…9`、`marimba0…9`、bongo及打击乐的`.mp3/.wav`，通过lowLag直接播放；按住状态也用于防止键盘自动重复触发。**采样播放是已核事实。** 真实瞬态、自然衰减、稀疏分工可能解释其清楚通透的印象，属于技术推断；本轮没有对其音频做响度匹配后的声学比较，不能证明lowLag本身让音色变好。

[仓库README](https://github.com/Externalizable/bongo.cat)记录原画作者对该网站的授权；[MIT LICENSE](https://github.com/Externalizable/bongo.cat/blob/591940644775d7cfd5167eceeeb6b97a1f9aadd4/LICENSE)是软件许可。已读材料没有逐个说明keyboard/marimba录音的原始录制者、音源库及其再分发许可，因此这些声音的独立权利链是**unknown**。不据此直接复制到Miao Beat。可复用的是明确署名的代码结构与交互经验；新项目仍应分别登记代码、图像、声音和乐谱来源。

也不建议整体搬入lowLag + SoundManager2旧音频栈：当前需求直接用现代WebAudio缓冲采样即可，老兼容层不是音质的证据。

## 2. 逐项核过的采样候选

“可采用”指已找到明确许可依据，仍需为最终选中的具体文件保存来源/版本/处理说明；不是本轮已下载并听审通过。CC0无需强制署名，但项目仍应保留来源清单。公共领域声明、CC0与CC BY分别记录，不改写成同一种许可。

| 声音/候选 | 原始或官方来源与已核许可 | 运行成本/适配 | 建议 |
| --- | --- | --- | --- |
| 钢琴：FreePats Upright Piano KW | [官方页](https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html)，版本2022-02-21，明确CC0 1.0；录制与编辑者列明 | 官方小尺寸版FLAC压缩包2.9MiB、WAV包4.3MiB；高质量双力度立体声版大得多。浏览器仍要转成经目标设备验证的格式 | **首批试听候选。** 权利清楚、体量有小版选项；不能仅凭小体积保证通透。先比较小版与正常版少量音符，不直接选“bright”版本 |
| 钢琴：Salamander Grand Piano V3 | [原作者Alexander Holm页面](https://rytmenpinne.wordpress.com/sounds-and-such/salamander-grandpiano/)明确2022-03-04起public domain；[FreePats镜像](https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html)仍列CC BY 3.0，版本V3+2020-06-02 | 官方镜像完整WAV为394MiB或1.18GiB，16力度层；完整包不适合作为网页首载。需要挑音域/力度、处理尾音，再压缩 | **第二钢琴候选。** 不能把Tone CDN或二次加工文件自动写成CC0。保留具体副本来源；沿用CC BY副本时保留署名与处理说明，或明确从作者公共领域发行重新取材 |
| 真正马林巴：University of Iowa MIS | [MIS总说明](https://theremin.music.uiowa.edu/MIS.html)由Lawrence Fritts说明可下载用于任何项目、不设限制；[马林巴官方页](https://theremin.music.uiowa.edu/Mismarimba.html)列演奏者、2013录音及yarn/cord/rubber槌、pp/mf/ff | 同时存在“一段文件包含半音阶”和ZIP内单音文件的资料；不能把`C4B4.aif`整个当成C4。应从单音包挑一到两八度，剪切与转码后自托管 | **首批马林巴候选。** 许可是作者机构自定义自由使用声明，不能标成CC0。推荐先试听yarn-mf和cord-mf的差别；精确单音清单、成品字节数仍待确认 |
| 木琴/颤音琴：VCSL、FreePats Xylophone | [VCSL作者仓库及LICENSE](https://github.com/sgossner/VCSL/blob/c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e/LICENSE)明确CC0；[FreePats木琴页](https://freepats.zenvoid.org/ChromaticPercussion/xylophone.html)再次明确CC0，版本2020-07-06 | 木琴WAV包4.3MiB、FLAC包2.3MiB；适合小范围采样。VCSL强调音准、一致录制与少量力度层 | **可选替代乐器。** 木琴、颤音琴、巴拉风不冒称马林巴；不能因为声音像就混名 |
| 原声鼓：Virtuosity Drums | [作者合作项目](https://github.com/sfzinstruments/virtuosity_drums)、[固定版本LICENSE](https://github.com/sfzinstruments/virtuosity_drums/blob/9f04cf9a734527edfbb0a4eee1f674e45bbf71bc/LICENSE)明确CC0 1.0 | 六种麦克风位置、很多力度与击法；网页只选单一合理麦位的kick/snare/closed hat/open hat等4–6个声音，不加载整库/六路混音 | **鼓组优先候选。** 想要自然鼓可先选它；实际爵士录音是否符合用户想要的节奏感仍须听审，不能保证像808 |
| 古典吉他：FreePats Spanish classical guitar | [官方页](https://freepats.zenvoid.org/Guitar/acoustic-guitar.html)，版本2019-06-18；2008年录音，作者Roberto；明确CC0 1.0 | 官方WAV包6.9MiB、解包19MiB；录音条件与降噪处理也如实说明。自托管少量单音，不必引入SF2运行时 | **吉他优先候选。** 可支撑真实拨弦单音；“扫弦”还需要弦序与错开发声，不能把六个完全同时的琴音称为已还原真吉他 |
| GM marimba/piano/guitar：FluidR3_GM | [原始分发仓库说明](https://github.com/gleitz/midi-js-soundfonts#soundfonts-available)将FluidR3_GM样本明确列为CC BY 3.0；仓库根MIT不能覆盖成样本MIT | 有现成每乐器MP3/Ogg字典，接入成本低；可能一次加载该音色整个音域，而非页面只需的十几个音 | **备用快速路线。** 可按CC BY署名与记录改动；真实选定文件仍留清单。不是必须引入128种GM乐器 |

### 不作为首选的方便素材

- **MusyngKite/FatBoy**：同一[原始分发仓库](https://github.com/gleitz/midi-js-soundfonts#soundfonts-available)明确是CC BY-SA 3.0；smplr Soundfont默认偏向MusyngKite。不是禁止使用，而是当前已有更简单的CC0/自由授权替代，避免默认选择时漏掉样本署名、修改与相同方式共享条件。不能说用了它就要求整个网站代码开源。
- **smplr默认SplendidGrandPiano**：其[样本镜像](https://github.com/smpldsnds/sfzinstruments-splendid-grand-piano)声明AKAI样本public domain，但本轮没有补齐AKAI原始授权文本；镜像还出现指向另一乐器仓库的模板残留链接。不是认定无权使用，而是相比FreePats/原作者已核路径，权利链信心较低。不要因它是示例默认就直接定稿。
- **smpldsnds/drum-machines**：[README](https://github.com/smpldsnds/drum-machines)泛称public domain，尚未完成每套录音的原作者链核验。可作试听索引，当前不直接复制整库上线。
- **tonejs-instruments全集**：[sample-source-info.txt](https://github.com/nbrosowsky/tonejs-instruments/blob/master/sample-source-info.txt)显示不同音色分别来自Iowa、Karoryfer、Freesound、VSCO等。不能用loader许可证给所有样本统一贴许可；也不需为四种网页声音打包整套仪器。
- **商业“royalty-free”样本包**：允许把样本用于一首音乐，不必然允许在网页上向任何人分发可直接获取的单个音频文件。未核到原始再分发条款的，保留unknown，不作为本轮素材。

## 3. 音频引擎：实际代码、发行与成本

本次读取npm registry元数据、发行tarball中的实际JS与仓库原始代码；未安装或执行上游包。下表体积是**发布文件原样gzip**，不是同一编译配置下的打包竞赛，也不是浏览器总下载量；不含采样音频。样本下载和解码内存通常比这几十KB更需要管理。

| 路线 | 本次核实版本/许可/依赖 | 实际发布文件体积 | 适配本项目的理由与代价 |
| --- | --- | --- | --- |
| 原生WebAudio薄封装 | 浏览器内建API；无第三方运行时代码 | 自己的封装大小unknown，不能宣称“0KB整个引擎” | 最少依赖，但缓冲缓存、按键释放、复音、音量包络与生命周期都要自己维护。若复用成熟采样器可减少这些新代码，不为了极小bundle重复造轮子 |
| **smplr** | [npm 1.1.0元数据](https://registry.npmjs.org/smplr/1.1.0)，2026-09-28发布；MIT；0个声明runtime依赖；仓库HEAD[`2c6c6aa`](https://github.com/danigb/smplr/commit/2c6c6aa8aba11639322fb0f1a475669dc45d4b1c)同日Release 1.1.0 | `dist/index.mjs`152,546B；gzip38,044B | **优先推荐的采样播放层。** 用Sampler接我们核过的样本，时间仍由共享AudioContext传入。支持过滤音符/力度加载；不是自带完整节拍器/DAW |
| Tone.js | [npm latest 15.1.22](https://registry.npmjs.org/tone/15.1.22)，2025-04-27发布；MIT；依赖tslib、standardized-audio-context。当前repo HEAD[`d707732`](https://github.com/Tonejs/Tone.js/commit/d707732171933e5c208a029002332ef31202b2da)是2026-10-21的15.5.58，npm标`next`，不是`latest` | 15.1.22的`build/Tone.js`345,500B；gzip79,283B | 有Transport、Sampler、效果等完整音乐抽象；若以后多轨编排很多可再考虑。当前单乐器+节拍器不必先上全部能力；更换框架不会自动获得更好采样 |
| soundfont-player | [npm 0.12.0](https://registry.npmjs.org/soundfont-player/0.12.0)，2020-01-27发布；MIT；audio-loader、note-parser、sample-player三项直接依赖；HEAD[`2b89587`](https://github.com/danigb/soundfont-player/commit/2b89587d7cc396c5c7b91056f8cb78831ead7436)为2023-05-16 README更新 | `dist/soundfont-player.min.js`22,717B；gzip7,204B | 现成GM播放很小；但发行较旧、样本许可仍需分库检查，也没有解决节拍架构。新项目不优先，已有项目可保留而非盲目重写 |

### 两个会真实影响接入的代码细节

**smplr的Mallet不是“随便写个marimba”就有。** 已读1.1.0的[`src/mallet.ts`](https://github.com/danigb/smplr/blob/2c6c6aa8aba11639322fb0f1a475669dc45d4b1c/src/mallet.ts)，helper列表有Balafon/Vibraphone/Xylophone等，没有名为Marimba的入口。真马林巴应通过Sampler接Iowa单音，或明确选择已核许可的GM marimba。VCSL马林巴的精确文件映射本轮没有核齐，不编一个可用名字。

[`voice.ts`](https://github.com/danigb/smplr/blob/2c6c6aa8aba11639322fb0f1a475669dc45d4b1c/src/smplr/voice.ts)默认以`context.currentTime`启动buffer，停止时带release envelope；[`voice-manager.ts`](https://github.com/danigb/smplr/blob/2c6c6aa8aba11639322fb0f1a475669dc45d4b1c/src/smplr/voice-manager.ts)跟踪和释放声音，没有看到自动限制最大复音/偷音的上限。因此“接上库就不会堆声音”不能成立，应用仍应设上限。

**Tone默认lookAhead可能让手弹多等100ms。** 已核[`Context.ts`](https://github.com/Tonejs/Tone.js/blob/d707732171933e5c208a029002332ef31202b2da/Tone/core/context/Context.ts#L163)：默认lookAhead为0.1，`now()`返回原始currentTime加这个值。用于预排节拍合理，直接把实时键盘音也放到默认`Tone.now()`会额外预排。若选Tone，应明确区分即时输入与Transport调度并实测；不靠全局随意设零来掩盖时钟设计问题。[Tone性能说明](https://github.com/Tonejs/Tone.js/wiki/Performance)也把低延迟与调度稳定性的取舍写得很清楚。

### 样本仓库版本快照

- VCSL：HEAD [`c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e`](https://github.com/sgossner/VCSL/commit/c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e)，2026-01-14，提交内容为补LICENSE。日期不代表当天重新录制所有声音。
- Virtuosity Drums：HEAD [`9f04cf9a734527edfbb0a4eee1f674e45bbf71bc`](https://github.com/sfzinstruments/virtuosity_drums/commit/9f04cf9a734527edfbb0a4eee1f674e45bbf71bc)，2026-04-21。读取LICENSE为CC0 1.0。
- FreePats的版本按上表官方发布日期记录，不虚构Git commit；Iowa按官方录制信息与本次检索日期记录。

## 4. 推荐的音频结构

```text
一次用户手势启用共享AudioContext
  ├─ 已解码采样 → 乐器voice + gain/release → 乐器总线 ┐
  ├─ 节拍事件 → 独立音量click总线                    ├─ 主音量/保守保护 → 输出
  └─ 将来可选loop事件 → 同一采样器/同一时钟          ┘

视图只读拍位置/已按音符；动画不负责产生声音时间
```

乐器、节拍器分别调音量；节拍清楚但不盖住旋律。一次只加载正在玩的音色，换乐器可先加载下一个，再释放旧缓存。CSS动画、Canvas和React渲染不能成为音符发声的时钟来源。[MDN的缓冲播放说明](https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode)支持对短采样用buffer、按需要创建source，已解码AudioBuffer可复用。

### 一个音频时钟，两条执行路径

**手弹路径：** keydown/pointerdown→检查该键尚未按住→以音频currentTime尽快触发→keyup/pointerup释放。不要等requestAnimationFrame，不在每次按键fetch/decode，不自动吸附下个八分音符；按键不是答题。键盘repeat、窗口blur、pointercancel与切出页面要释放，避免卡住的长音。移动端需多点触摸，电脑需检查常见三音和弦是否受实体键盘ghosting限制。

**节拍路径：** 用JS定时器“检查未来需要排什么”，用AudioContext安排“确切什么时候响”。依据[Chris Wilson原文](https://web.dev/articles/audio-scheduling)与[MDN序列调度示例](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques)，建议起点为每25ms检查一次、向前安排100ms。这是初始参数，不是保证所有设备永不抖动：

```text
while nextBeatTime < audioContext.currentTime + 0.100:
    scheduleClick(nextBeatTime)
    nextBeatTime += 60 / bpm
下一次检查：约25ms后
```

不能用`setInterval(() => playNow(), 60_000/bpm)`代替音频调度，也不要一次排整首歌。BPM变更作用到尚未排出的拍，停止时同时取消定时器并停止已排队click/voice，避免停止后又冒一拍。若主线程阻塞超过前看窗口，跳过已错过的拍并恢复相位，不把漏掉的拍挤成一阵连响。

节拍视觉从同一拍序号推导，有支持时用[`getOutputTimestamp()`](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/getOutputTimestamp)把音频输出与performance时钟对应；不支持则降级为近似视觉。蓝牙输出延迟不能通过“音频时钟很准”自动消除，也不能拿动画准时证明听到的声音准时。

### 移动端首次启用与恢复

[MDN建议](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices)是在用户手势里创建或resume音频context。一次“开启声音”可以同步发起resume，再显示样本加载状态；音色没ready时不要假装按键已奏响。网络失败要可重试，不默默回退成被用户否定的合成琴。

监听[`state`](https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/state)变化及页面可见性：iOS切后台/来电后可能中断；回前台检查状态，必要时提供点击恢复，重新设节拍起点。不要继续追赶冻结前的旧时间戳。[`latencyHint: "interactive"`](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/AudioContext)只是浏览器建议，仍须看baseLatency/outputLatency与真实设备，不承诺“零延迟”。

### 复音与防爆音

建议初始同时活跃voice上限16–24（移动）/32（桌面），优先释放最旧且已松开的尾音；这是待测预算。打击乐有one-shot长度/开放踩镲被闭镲截断的专门规则，琴音保留自然衰减。重复同音也不能无限叠加；每个发声实例保留stop句柄，停止/换音色/失焦统一释放。

样本先校准相近主观响度、保留瞬态，去除不必要的开头静音；不能简单把所有样本normalize到满幅再一起叠。master从保守音量开始，保留headroom；[`DynamicsCompressorNode`](https://developer.mozilla.org/en-US/docs/Web/API/DynamicsCompressorNode)可作保护，但不是保证绝无越界的砖墙限制器。是否需要额外limiter，由最大和弦+鼓+节拍的离线峰值/真机听审决定，不先引入重worklet效果链。

## 5. 轻量与好听的实际取舍

- 一个可用音域，先考虑C4–C5的13个半音或用户明确看到的两八度；不要显示一个八度却后台加载88键16力度。低音和高音需要时再加，尽量避免单个采样变调跨整个八度。
- MP3/AAC/Ogg等压缩传输不等于解码后也很小。示例估算：13音×2力度×3秒×44,100采样/秒×2声道×4字节，约27.5MB十进制PCM；这是预算公式，非实测内存。相较“引擎38KB还是79KB”，全库解码更可能改变移动体验。
- 首次核心音色目标可先设压缩音频≤3MiB、整组ready≤3秒（指定网络/设备测试）；达不到先缩范围/力度，不把自然尾音剪成塑料短哔声。这是验收目标，不是已完成的速度。
- 原始WAV/AIFF/SFZ留作可追溯制作输入；网站只发最终单音文件。优先保留一个广泛支持、已实测的格式，不开局给每音下载多种格式。转码需记录源文件SHA256、裁剪区间、gain、编码参数、输出SHA256。
- 如加入吉他，先做好真实单音与少量和弦。弦序、10–25ms一弦的扫弦错开可以作为听审变量；这是模拟演奏手势，不等于重新录制的真扫弦，也不应同时做完整指板、变调夹、教材体系。

## 6. 未来合拍loop：可以长出创作，暂不引入音游

先交付节拍器+即时乐器。用户想保留自己刚弹的东西时，再考虑1/2/4小节事件loop：记录相对于节拍起点的beat位置、音高、力度、持续时间；回放仍排到同一个AudioContext，不录成不易编辑的整段背景MP3。

现场演奏始终立即发声，默认不量化；未来“对齐节拍”应是用户主动选择的录入/回放编辑功能。循环长度、起拍和停止规则比多轨界面更重要：支持清空/撤销一层便足够先试，暂不做轨道矩阵、混音台或每日挑战。

参考谱不参与判分；每个音/和弦只提供可读的键位与节奏提示。乐谱的旋律、编曲与录音也分别有来源边界，不能因采样CC0就自动授权任何歌曲或商业录音。

## 7. 可测验收与停止条件

以下全部是**待实施/待测试**，不把源码阅读或headless构建当作声音已经好听。

| 项目 | 最小验收 | 如何留证/失败后怎么做 |
| --- | --- | --- |
| 音色听审 | 同响度播放单音、三和弦、连续八分音符；比较旧合成、两套真实钢琴、两种马林巴槌。用户明确更喜欢至少一套，再决定替换 | 记录相同音符/力度/音量、来源和设备；不靠“真实采样”标签替用户判断。没有明显提升则不扩大乐器数量 |
| 第一次发声 | Safari iPhone、Android Chrome、桌面Chrome/Safari均能一次手势启动，ready后第一键不丢；失败有重试 | 真实press→听见/输出录音；桌面测试不代替手机物理扬声器 |
| 手弹延迟 | 在指定有线/内置输出设备记录P50/P95端到端延迟；期望桌面P95≤50ms，手机P95≤80ms作为初始目标 | 用可关联输入触发的录音/loopback测；只记录JS调用耗时不能声称端到端。蓝牙单列unknown或实测，不混入“低延迟通过” |
| 节拍稳定 | 60/120/180 BPM各运行至少2分钟；前台滚动/轻动画下录到的点击间隔P95误差目标≤5ms，无累积漂移 | 用实际输出波形找onset，和目标拍序列对比；若主线程>100ms长任务引发断拍，记录超窗口失败并恢复，不把补发一串拍当通过 |
| 停止与调速 | 停止不再冒出旧拍；改BPM在已说明的下一未排拍生效；后台恢复不爆发补拍 | 录音与调度日志对应；失败先修取消/相位，不增玩法 |
| 复音/干净度 | 三至六音和弦、快速重复同音、鼓+节拍同响，无明显裂音/泵动；离线最坏组合sample peak目标≤0.98 | 扫描OfflineAudioContext渲染峰值并真机听审；不能只因加了compressor就标“限幅通过” |
| 释放 | 持键、松键、滑出、pointercancel、切页、失焦、换乐器之后无卡住的声音，活跃voice最终归零 | 声音实例计数与连续录音；失败先收紧生命周期 |
| 载入/内存 | 首载只请求当前乐器；真实记录压缩字节、decode时间、decoded buffer字节，切换后旧缓存可释放 | DevTools/调试统计；目标超预算就减范围，禁止悄悄载入全GM |
| 许可 | 每个出站样本都有作者/来源/版本或日期/许可链接/处理记录；代码notice保留 | unknown文件不进入生产音色包；不能用仓库MIT替代采样授权 |

## 8. 建议交给用户确认的具体选项

**建议路线：** smplr 1.1.0作为采样器，原生音频时钟做轻量节拍调度；主音色先在FreePats钢琴与Iowa真马林巴之间听审选择。乐器素材自托管，保留来源清单。鼓用一小组Virtuosity Drums，古典吉他用FreePats作为后续可选音色。

**备选路线：** 如果明确要多层loop、复杂调速/编排，再选择稳定版Tone.js；必须特别处理即时输入的lookAhead，仍使用同一批经听审的真实采样。不是换Tone就重做成音游。

**保留unknown：** 最终具体采样文件/哈希、Iowa ZIP单音清单、音色A/B结果、压缩后大小、iOS物理延迟、蓝牙延迟均未实测。UI当前可以按授权独立推进；这些声音路线没有因本研究自动变成已获批准的实现。
