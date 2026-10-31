# Second polish: independent UI judge · 2026-10-31

Reviewer did not implement this candidate. Read-only product review of the actual built candidate served at `http://localhost:8894/?analytics=internal`, using a separate Chrome QA tab. Product code was not changed. Only this report is written by the reviewer.

## Initial verdict

**HOLD for two P1 performance-layout regressions; no P0 found.** Ordinary phone layout, early mode discovery, phrase previews, collapsed metronome settings, and the portrait fixed activity bar work on the checked paths. The regressions are bounded CSS placement/order issues and do not justify changing the cat route or implementation architecture.

## Actual viewport and interaction coverage

The browser's viewport capability operates through an existing scaling factor in this session. Actual `innerWidth/innerHeight` were read and verified, not inferred from the tool request: **390×844**, **320×568**, and **844×390**.

### Ordinary 390×844

- Screenshot: Free / Practice / Record now appear near the top, before the whole orange-cat scene; all three are discoverable immediately.
- Whole cat, connected paws and keyboard remain visible. Sound preparation, melody keys and low/high navigation remain in the first viewport after moving the mode row.
- No horizontal page overflow observed.

### Ordinary 320×568

- Screenshot: all three mode choices, complete cat and four instruments remain available; sound preparation is at the lower edge and playing keys require a normal vertical scroll. This is not claimed to fit every control in this smaller first viewport.
- Clicked Practice, then the second phrase chip. Selected preview and original select both changed to `第 2 句 · F4 · F4 · E4 · E4 …`.
- Selected phrase 6 through the original select. Preview text and chip pressed state changed to phrase 6. Phrase strip remained internally horizontally scrollable: clientWidth 280, scrollWidth 872, while page scrollWidth and innerWidth both remained 320.
- Small P2 convenience gap: selecting phrase 6 in the select does not scroll that active chip into view; the strip can still show phrases 1/2 while the selected phrase and text say phrase 6. Data state is synchronized and this is not a release blocker.
- Expanded and collapsed the native `拍号与音色` details through its visible summary. Meter, tap tempo, sound and accent choices appeared inside, and the ordinary BPM/beat controls remained available when collapsed.
- Started phrase guidance: the fixed activity bar stayed at the viewport bottom with an actionable Stop. Piano keys were usable above it; content can scroll clear of it.
- Started a persistent first-phrase loop and scrolled to the real document bottom. Actual footer bottom **484.03px** was above activity-bar top **498.37px**; body bottom padding was **84px**. Screenshot showed credits/footer clear above the bar. Stop successfully ended the loop and restored controls.
- Started a real QA recording, pressed A, and observed one human input plus changing elapsed time (`0:14`, then `0:39`/`0:59`) in the activity bar. No automatic notes were entered by this reviewer.

### Performance modes and discovered regressions

#### P1-A: portrait recording tools are ordered before the performance stage

Reproduce: Record → Start Recording → Fullscreen, actual 390×844 (also reproduced at 320×568).

The mobile primary-action rule `order:-1` on the recording strip becomes an order on a direct flex item when performance mode flattens the wrappers. It moves the entire recording/file-management block before the stage rather than retaining a compact recording control.

Measured at 390×844 during recording:

- recording strip y **33.99**, height **216.20**, computed order **-1**;
- bench topline y **250.19**;
- mode row y **294.18**;
- complete-cat stage y **350.18**;
- playing surface y **733.76**; piano begins around the fixed activity bar's lower-screen region.

The screenshot shows recording/import/draft management first and the performance keys pushed below the first viewport, with their first row behind the fixed transport until scrolled. Complete source cat frames are retained; this is page layout, not asset cropping. Exit remains separately usable at the upper right.

Required bounded repair: scope the ordinary-phone action-priority ordering to non-performance layouts, or reset practice/record tool order in portrait performance mode. Recheck both Practice and Record since both have mobile priority styles.

#### P1-B: landscape performance modes overlap the instrument tabs

Reproduce: actual 844×390 → Fullscreen.

Screenshot shows the Free / Practice / Record row spanning the screen **at the same vertical position as** Piano / Marimba / Guitar / Drums in the right column. Text and button surfaces visibly overlap. Source support: both mode nav and instrument tabs occupy grid row 2 after the new mode placement.

During active recording, the activity bar is in-flow at this width, y **228.66–290.48**; the piano playing surface begins y **310.47**, so piano keys only begin near the viewport bottom. That space pressure is secondary to the explicit overlapping controls. Exit is still reachable and Stop ended the recording successfully.

Required bounded repair: give the mode row a distinct grid row and move subsequent instrument/control/sound/input rows accordingly, or place mode controls in a deliberate non-overlapping location for short landscape. Verify actual screenshot and clicks after the change, not only DOM presence.

## Publication judgment and unverified areas

Do not label the second-round performance UI ready until P1-A and P1-B are repaired and independently rechecked. The ordinary portrait improvements may be retained. No new 3D/model/animation work is indicated.

This is browser viewport testing, not physical phone touch, keyboard rollover, speaker listening, safe-area/notch measurement or platform-native fullscreen acceptance. Current export-card construction was intentionally outside the main scope. No production deployment or hash audit was performed here. The main agent receives the concrete findings before deciding release readiness.

## Repair verification appended later on 2026-10-31

Main agent rebuilt fixes for P1-A and P1-B. This reviewer reloaded the actual candidate and repeated the affected interactions. Initial findings above remain historical evidence; the current assessment below supersedes the initial HOLD.

### Current local UI verdict

**Both original P1 issues are resolved on checked paths. No remaining P0/P1 found in this pass; a short-landscape activity-bar convenience issue remains P2 as described below.** The checked page UI can proceed to main-agent final production acceptance. This is not itself a production release claim.

- **390×844 portrait full recording:** recorded an S input; recording strip computed order is now **0**, appears after the playing surface at y **919.98**, rather than y34. Cat stage y **111.98**; playing-surface width **350px**, y **495.57**; full cat and navigation remain visible. Recording elapsed advances and Stop stays fixed at bottom.
- **320×568 portrait full recording:** management tools no longer precede the stage; full cat is present, with ordinary vertical scrolling needed to reach inputs at this small height. Actually clicked C4, then High and C5: recorded event count increased from 1 to 3, latest displayed note was C5. Surface width **280px** remained inside the 320px screen. This demonstrates real reachable inputs, not merely DOM presence. Stop and upper-right Exit remained distinct.
- **390×844 portrait full Practice:** practice strip computed order **0**, cat y **111.98**, practice tools y **921.98**; screenshot confirms practice controls no longer jump ahead of the stage.
- **844×390 full recording:** mode row bounds **x23.99–275.72**, instrument tabs **x297.72–820.55**. Screenshot confirms the formerly overlaid rows now occupy different columns with a clear gap. Activity bar computed position is **fixed** at the bottom for this width, not in-flow above the keys. Stop successfully ended the QA recording, and Exit worked in the prior repeat.
- Additional long-text check: at 320px width, selected 500 Miles and its last (26th) phrase through the strip. Long lyric preview wrapped inside the page; page width remained 320, selected range became index25 and matched preview/select. No new horizontal page overflow was observed.

### Residual P2 / narrow landscape initial view

At actual 844×390 during active recording, the fixed activity bar starts around y **320** while the initial-top piano spans approximately y **260–379**. It therefore covers the lower portion of the white keys in the initial top position. Scrolling the performance area brings the full keys above the bar; this reviewer actually clicked high C5 and the controls remain reachable. Hence this is not scored as a P1 functional block, but a compact ready-state toolbar for short landscape would improve the initial view. This finding was sent to the main agent; do not claim the bar never visually overlaps scroll content at any position.

The earlier phrase-select P2 (active chip not scrolled into view) has not yet been rechecked after any subsequent main-agent change. Default browser viewport will be restored before this review turn finishes.

### Strict no-key-overlap follow-up

The main agent requested the stronger numerical gate `melodyKeys.bottom <= activityBar.top` for the initial-top 844×390 performance recording view. After rebuilding a ready-state sound-entry collapse, this reviewer reloaded and repeated real recording + fullscreen.

- Actual viewport: 844×390. Sound entry computed `display:none`, confirming that change took effect.
- Keyboard top **226.65**, bottom **346.65**; fixed activity-bar top **320.19**. Remaining overlap **26.46px**.
- Exit bounds top10/bottom50 remain separate from the activity bar. Stop worked and the recording was ended; normal Exit worked; viewport reset.

Therefore the first compact-ready-state adjustment **does not yet pass that stricter gate**, despite improving the overlap. This is not a recurrence of the original P1 grid collision; an additional compact landscape adjustment is needed if the strict no-overlap criterion is required. Error-state recovery was not artificially fault-injected by this reviewer.

## Final bounded repair verification · current local verdict PASS

The main agent further reduced only short-landscape performance row gaps and label spacing, and adjusted melody-key height. This reviewer reloaded and performed another real recording/fullscreen check.

- Actual **844×390**, initial-top piano performance, recording active: full keyboard bounds **top198.65 / bottom310.65**, activity-bar **top320.19**. The strict `keyboard.bottom <= bar.top` gate now passes with approximately **9.55px clearance**. White-key height **112px**; black-key height **68.32px**. Screenshot shows complete white keys above the activity bar, and mode/instrument rows remain non-overlapping. Complete cat, paws and keyboard remain in the stage.
- Actually clicked **C4 and C5** in that view: latest note became C5 and recorded event count was **3** including the initial A input. Stop ended recording successfully. The earlier 320px high-navigation/C5 reachability check remains applicable because the latest sizing rule is limited to short landscape.
- Exit is still at top10/bottom50 and usable. After stopping, switched to an unprepared guitar: sound-entry computed display returned to **flex**, state **idle**, Prepare Sound **enabled**. This proves an actual unready recovery entry was retained. The source selector also excludes `.error` from its ready-row hiding rule, but an induced network/audio error was **not independently fault-tested** here; do not call that branch experimentally verified.
- The phrase-select convenience issue is also resolved: at actual **320×568**, selected 500 Miles phrase26 via the original dropdown. Whole-page `scrollY` remained **0**; after the horizontal smooth reveal settled, strip scrollLeft was **3511.82**, and the active card bounds **x160.04–298.03** fit inside strip **x20–300**. Screenshot after inspecting the card shows matching phrase26 preview/select/card. It did not scroll the whole page merely to reveal the selection.
- All QA recordings were stopped, fullscreen exited, and default viewport reset at the end.

**Final local page-UI publication judgment:** checked second-round requirements pass after the bounded repairs; no remaining P0/P1 was found. Initial P1 and subsequent strict-gate failures remain recorded above for provenance. Production byte checks, live post-deploy interactions, fault injection and physical-phone acceptance retain the previously stated boundaries.
