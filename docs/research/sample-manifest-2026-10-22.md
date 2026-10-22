# Miao Beat 真实采样试听包

制作与许可核验：2026-10-22，Asia/Shanghai。用户已授权真实钢琴/马林巴 A/B、真实尼龙弦吉他和轻量架子鼓。这份交付只准备素材，没有修改 app、音频引擎或页面，也没有替代人类听审。

**已完成：** 四组 33 个可解码、自托管 MP3；完整来源/输入输出 SHA256、切段秒数、编码命令、声道/采样率、峰值和起音指标均可检查。**未完成：** 用户实际试听、耳机/扬声器听感判断、手机物理输出与端到端延迟、最终各乐器/鼓件的响度混合。不能写成“音色已经好听”。

| 组 | 文件与覆盖 | 压缩字节 | 解码 float32 PCM | 许可 |
| --- | --- | ---: | ---: | --- |
| piano-kw | 5 锚点，C4–C5；最近邻最多变调 1 半音 | 131,210 | 3,599,600 | FreePats CC0 1.0 |
| guitar-spanish | 7 锚点，C3–C5；最近邻最多变调 2 半音 | 133,831 | 4,206,696 | FreePats CC0 1.0 |
| marimba-iowa | 13 个真实半音，C4–C5，无需变调 | 458,021 | 16,158,624 | Iowa 官方不限制项目使用的声明，**不是 CC0** |
| drums-virtuosity | 8 个真实单击鼓件，每件一个麦位 | 410,262 | 13,828,328 | Virtuosity Drums CC0 1.0 |

四组合计 **1,133,324 B（约 1.081 MiB）**。每组均远低于 2 MiB；吉他低于 1 MiB。首次应只下载当前乐器，需要鼓时再加载鼓组，不能用合计体积小就默认全部解码。

## 可直接接入的映射

运行时的实际映射在 `public/samples/manifest.json` 的 `groups[group].noteURLs`。URL 相对于公开站点根页面：

```js
// piano-kw
{
  'C4':'./samples/piano-kw/C4.mp3',
  'D#4':'./samples/piano-kw/Ds4.mp3',
  'F#4':'./samples/piano-kw/Fs4.mp3',
  'A4':'./samples/piano-kw/A4.mp3',
  'C5':'./samples/piano-kw/C5.mp3'
}
// guitar-spanish
// C3, E3, G3, C4, E4, G4, C5
// -> ./samples/guitar-spanish/{sameNote}.mp3
// marimba-iowa
// C4,C#4,D4,D#4,E4,F4,F#4,G4,G#4,A4,A#4,B4,C5
// -> ./samples/marimba-iowa/{C4,Cs4,D4,Ds4,E4,F4,Fs4,G4,Gs4,A4,As4,B4,C5}.mp3
// drums-virtuosity: stable voice IDs, NOT pitched note names
// kick,snare,closed-hat,open-hat,tom-low,tom-high,crash,ride
// -> ./samples/drums-virtuosity/{sameId}.mp3
```

吉他是独立真实拨弦单音；将六弦顺序音符以约 12–20 ms 错开可组成轻量扫弦。素材里没有复制整首歌曲或和弦录音循环。只给一个音调到所有弦、或六音完全同时响，均不能据此宣称还原了真实六弦演奏。

## 原始来源、版本和许可

- 钢琴：[FreePats Upright Piano KW 官方页](https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html)，[本次实际小版 WAV 包](https://freepats.zenvoid.org/Piano/UprightPianoKW/UprightPianoKW-small-SFZ-20190703.7z)。**包内 readme/SFZ 是 2019-07-03**，官网整个音库标题的 2022-02-21 不能当小版发布日期。录制者 Gonzalo、Roberto，2017 年 Kawai 立式钢琴录音。CC0 原文和包内 readme/SFZ 已保存。
- 吉他：[FreePats Spanish classical guitar 官方页](https://freepats.zenvoid.org/Guitar/acoustic-guitar.html)，[实际 WAV 包](https://freepats.zenvoid.org/Guitar/SpanishClassicalGuitar/SpanishClassicalGuitar-SFZ-20190618.7z)。2019-06-18 版本，Roberto 制作，2008 年录音，CC0。原作者说明录音条件有限并做过降噪；不把“真实”自动等同于高质量。
- 马林巴：[Iowa 官方录音页](https://theremin.music.uiowa.edu/Mismarimba.html)，[实际 yarn-mf ZIP](https://theremin.music.uiowa.edu/sound%20files/MIS/Percussion/Marimba/Marimba.yarn.mf.zip)，[官方使用许可说明](https://theremin.music.uiowa.edu/MIS.html)。Andrew Thierauf 演奏，2013-03-20 录音，Daniel Frantz/Will Huff 技术。许可原句摘录："may be downloaded and used for any projects, without restrictions." 这不是 CC0 文本，不把两者混标。
- 鼓：[Virtuosity Drums 原仓库](https://github.com/sfzinstruments/virtuosity_drums)，固定 commit `9f04cf9a734527edfbb0a4eee1f674e45bbf71bc`，[该 commit 的 CC0 LICENSE](https://github.com/sfzinstruments/virtuosity_drums/blob/9f04cf9a734527edfbb0a4eee1f674e45bbf71bc/LICENSE)。Versilian Studios/Karoryfer Samples，Austin McMahon 演奏。仅从固定版本 raw URL 下载 8 个单文件，没有克隆/下载全库；每个完整 URL 都在 manifest。

素材许可独立于应用/采样器代码许可。本次未使用 Tone CDN、未核权利链的 Bongo Cat 声音或任意 GM 音库。公开署名清单在 `public/samples/LICENSES.txt`，完整 CC0 文本在 `public/samples/CC0-1.0.txt`，没有产品回链个人站点。

## 实际处理与技术检查

所有文件使用本机 ffmpeg 的 `libmp3lame -q:a 2 -ar 44100` 编码；保留源声道数量，去除元数据；统一先减 3 dB，留出 MP3 重建峰值余量。没有按单音满幅归一化、加混响、改变频率或把合成器冒充采样。完整命令、源/输出格式和 SHA256 在制作 manifest；编码器具体版本一并登记。

**钢琴：** 使用 C4、D#4、F#4、A4、C5 五个源锚点。小版的前三个源文件原本配 SFZ 循环，不能称为完整无限自然衰减；本次作为 one-shot 使用全部可用录音，并按原 SFZ `ampeg_release=0.6` 对末尾做 600 ms release fade。A4/C5 保留完整源尾，仅 10 ms 文件边界淡出。没有为了几 KB 把琴音硬剪成半秒。已测主要起音阈值（相对单音峰值 -20 dB）均在文件头 5.3 ms 内。部分钢琴音的二次泛音强于基音：Goertzel 最强 bin 可能为高八度，不能误判成切错音高。

**吉他：** 原样保留可用尾音，10 ms 文件边界淡出。大部分源起音靠近开头，G4 从文件开始到峰值 10% 约 42 ms；这可能包含真实较轻的起弦/拨弦过程，未经听审不进一步粗暴切掉。该延迟是样本内容本身，不是已测设备延迟。

**马林巴的关键实物纠正：** 官方 ZIP 实际包含按八度组织的长半音阶录音，**不是单音文件**；C4B4 是 43.349333 秒、96 kHz/24-bit/双声道。先识别 12 次独立敲击，再取 C4–B4，并从 C5B5 取第一击 C5。用 10 ms RMS 窗找候选起音、1.6 s 最小间隔；候选前 100 ms 内用局部峰值 10% 定位，并保留 5 ms 前垫；切到下一独立起音前 15 ms，或原文件结束，避免混入下一个音。最后 10 ms 仅做边界淡出。13 段在 100–400 ms 分析窗的最强半音基频 bin 逐一与 MIDI 60–72 相同；主要起音阈值均≤5.1 ms。此为切分/顺序的客观核查，不能替代精细调律或听感判断。

**鼓：** kick 用 kickmic/中间力度，snare 用 snaremic/center vl16，toms 用 overhead/center vl10，镲片用 overhead/中间力度。每件仅一个麦位，避免无验证地把六路相加。去掉主要敲击前冗余垫音，保留 5 ms 起音前垫与完整尾音；crash/ride/open-hat 保留长衰减，不剪成固定短音。closed/open-hat 互斥与 choke 属于播放引擎行为，素材本身没有替应用实现。

**全文件实解码检查：** 33 个文件均成功解码，核过 44.1 kHz 和输出声道；对所有声道的所有 float32 样本扫描后，**没有绝对值≥1 的重建样本**。这只说明单音文件没有数字越界，不证明多声部/鼓+节拍合成输出不会超限。

## A/B 与鼓件音量必须校准

原音库录音电平不一致。前 150 ms 的 RMS 中位数是：钢琴 -10.862、吉他 -13.277、马林巴 -23.156、鼓 -36.554 dBFS；全段 RMS 受长尾/静音影响更大，不适合直接比较。鼓单击峰值的跨度也很大。不能用同一个 gain 播四组后把“更响”当成“更好听”。

建议先对 A/B 同样单音/三和弦/连续八分音做保守主观等响，记录每组增益，再请用户选择；鼓要独立平衡各 voice、限制复音与输出余量。manifest 提供峰值与前 150 ms RMS 供初始参考，这些不是最终混音目标。尤其不要为追求全段 RMS 一样而把长镲尾和底噪猛烈放大。

## 检查入口与可公开清单

- `assets-source/samples-2026-10-22/sample-manifest.json`：逐文件源 URL→源 SHA256→区间/gain/编码命令→输出 SHA256/字节/声学指标。
- `assets-source/samples-2026-10-22/licenses/`：官方页面快照、CC0 原文、两套 FreePats 包内 readme/SFZ、Virtuosity 固定版本 LICENSE/README。
- `assets-source/samples-2026-10-22/prepare.py`：从本地核验原包制作；`fetch-drums.py` 拉固定 commit 8 个文件；`verify.py` 解码并逐文件校验。
- `public/samples/` 的 **33 个 MP3 + manifest.json + LICENSES.txt + CC0-1.0.txt** 可按上述许可公开自托管。
- 原始包、展开 WAV/AIFF/FLAC 和临时 7-Zip CLI 只留制作目录；该目录内 `.gitignore` 排除 `archives/`、`extracted/`、`tools/`，避免把几十 MB 原始包和工具塞进网页/仓库。原包哈希仍在 manifest。

本次听审状态统一为 `not_auditioned` / `auditioned:false`。没有调用外部音频上传服务，没有上传用户录音。
