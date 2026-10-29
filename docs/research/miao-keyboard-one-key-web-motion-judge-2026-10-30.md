# A/C4 实时网页 · 独立 motion/UI 短评

2026-10-30，非本页 builder。实操 `http://127.0.0.1:8953/design/miao-reuse-keyboard-v1/browser-one-key/`。隐藏IAB创建明确返回不可用，改用独立Chrome标签686373686；未操作root tab15。不改代码、资产或渲染，不用慢放/裁图替代本次实时判断。

**结论：motion/UI角色 GO，允许发布独立、明确仅A/C4的实验页供用户试；主站不替换。未见阻止这一级试用的新P0。手部全景可辨性仍P1/HOLD，不能叫完整角色动作、八键或最终Miao通过。**

实际点击开琴，17.1MB模型加载后canvas ready=true、真实Three绘制306 calls；完整猫、双掌、全琴与桌脚在同一画面。canvas约860×434.6 CSS像素，角色本身在中央更小。实际操作与DOM绘制读回如下：

| 操作 | 实测 |
|---|---|
| 点A/C4一次 | inputCount=1，maxRenderedAmount=.999332，PCM peakRms=.0155103，随后回0。 |
| 开启“按住C4” | count=2，实际renderedAmount=1、Down=1、theta=−.013393259rad；持续持住不自行增数。 |
| latch打开时按A | 按设计忽略，不产生第二个输入；源码明确互斥。 |
| 关闭latch，再按住键盘A约800ms并松开 | count仅2→3，max=1，松开后amount/weights/theta归0，未发生系统repeat连敲。 |
| 两次短A | count3→5；之后回0，没有追加排队输入。并发逐帧读回尝试因只读DOM作用域不提供rAF而失败，故不声称捕获到30ms重触发凹口的逐帧曲线。 |
| 再持住→停止 | count=6，持住时Down=1；停止后清除latch、amount/weights/theta=0、meter scaleX(0)。后续闲置仍count6。 |
| 停止后再按A一次 | count6→7，实际PCM与动作恢复；最终再次停止，count7、模型归0。 |

源`play.js`每个被接收press只调用一次SampledAudio.play，keyup/release/stop不调用play；与输入计数和无尾随观测相符。全程audioState=running，实际PCM peak约.0155–.0294（双短键叠加）；**peak是保留峰值，不是停止后的实时静音读数。**已检查stop调用stopVoices；没有扬声器物理试听或录音，不能声称主观音质/物理发声延迟已验。控制台error/warn读回为空。

本次contactRenderLatencyMs观测约30.2–46.1ms，含已提交绘制，未沿用离线片200ms静止前导；这只是CPU draw提交计时，不是GPU呈现/声卡/扬声器端到端延迟或严格音画同步证明。单次点击、持键、松开与停止能完成真实输入→PCM/模型状态闭环；高频全轨迹连续性未由本次UI逐帧重验。

**视觉与UI分开：**按钮的按下色、latch文字、C4状态和电平反馈清楚，原速整页没有新可见塌手、断袖或浮空。但食指与键前缘位移仍很小；即使知道目标位置，完整画面也难主动辨认每次动作，不能由按钮亮色签“手部清晰已生产达标”。本页足以收集单音真实试用反馈，若以自然清楚的角色演奏作为正式交付则仍HOLD。17MB等待、偏硬阴影及模板身份差异另由对应角色评审，未用本motion意见覆盖。

几何证据边界继续保留：父任务提供的14原状态morph有限检查外部0、pad约54μm、原black局部near-boundary unknown15，不是本人重跑结果；未证明连续实体/完整机械机构。sourceScene ca5…/pose6a…沿本候选。手机实机/物理扬声器、八键、长时间快连按、跨设备、发布后的正式URL及主站均未验；必须由生产验收另查。
