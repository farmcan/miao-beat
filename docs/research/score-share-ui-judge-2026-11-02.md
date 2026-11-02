# Same-screen score reader: independent UI judge · 2026-11-02

Reviewer: UI / responsive layout / actual interaction. The reviewer did not implement the candidate. Tested the actual candidate at `http://localhost:8894/?analytics=internal` in an independent Chrome QA tab, after reading the current source. No product files changed; only this report is authored here.

## Verdict

**PASS for the checked same-screen UI and controller-entered page-filling performance fallback. No P0/P1 found.** Score cards, the complete original orange-cat/paws/instrument image, and real playable keyboard are simultaneously visible in the tested portrait, short-landscape and desktop views. Pagination, opt-in following, range controls, Stop and Exit worked through actual UI input.

**Native browser fullscreen was not passed by this reviewer.** Clicking the real `看谱演奏` button invoked the shared performance controller and produced `body.className = "score-reading performance-mode"`, `data-performance-mode = "page"`, and `data-fullscreen-error = "TypeError"` in this Chrome tool environment. A separate default-desktop exit/reenter attempt after resetting the viewport produced the same result. The verified mode is the app's supported page-filling fallback, not a fabricated ordinary-layout preview and not a claimed successful native fullscreen session. No unsupported cause is assigned to the TypeError. Main-agent/native-device acceptance must retain this distinction.

## Actual UI coverage

Viewport values below are **actual DOM innerWidth/innerHeight**, checked after adjusting the tool's viewport for this browser's scale factor. Each screenshot was taken from the live rendered candidate; no body classes, DOM contents or app state were changed through page evaluation.

| Actual view | States checked | Same-screen outcome |
|---|---|---|
| 320×568 portrait | Sound unprepared, ready/manual playing, active phrase-loop guidance, active recording | Complete 108px cat stage, four score events, reachable melody keys and low/high controls fit together. Sound preparation remains available before ready. Active Stop bar does not cover score, keys or range navigation. |
| 390×844 portrait | Unprepared, active guidance, active recording | Complete 132px cat, four-event page and input surface remain visible together with ample clearance above Stop. |
| 844×390 landscape | Unprepared, active guidance and active recording | Complete 128px cat at left; six score events above all eight white keys at right. Preparing audio does not push cat/score/keys offscreen. Active Stop stays below all three. |
| Default desktop, actual 1374×732 | Active recording and manual page view; separate controller reentry | Complete 200px cat at left, six-event page and full keyboard at right, Stop along bottom. Native fullscreen attempt still falls back to `page`, as disclosed above. |

### Geometry evidence

- 320×568 **unprepared**: cat stage y55.99–163.98; score y270.97–330.23; keyboard y336.23–448.22; low/high navigation bottom499.22. Prepare Sound was enabled and visible. The 640px inner keyboard remains inside a constrained horizontally scrollable viewport; it is not a 640px page overflow.
- 320×568 **guidance active / ready**: score bottom277.24; keyboard bottom395.23; navigation bottom446.22; fixed activity bar top498.37. Complete cat stage remains y55.99–163.98. Screenshot confirms no overlap between the required three areas and Stop.
- 320×568 **recording active**: four score events remained visible; navigation bottom446.22 < Stop top498.37. Manual C4 input produced `1 次敲击`; turning a score page did not add an event.
- 390×844 **guidance active**: four cards; keyboard bottom435.23 < Stop top774.74. The manually selected page remained visible while audio guidance continued elsewhere, consistent with follow being off.
- 844×390 **guidance/recording active**: cat y101.98–229.98; score y103.98–159.61; keyboard y165.60–261.60; Stop top320.19. Range-navigation buttons are hidden here because all melody keys already fit; that is appropriate and differs from the historical expanded-scroll-viewport bug.
- Desktop **recording active**: cat y101.98–301.98, score bottom163.25, keyboard bottom315.23, Stop top662.01. Six cards and complete input keyboard were visible.

## Interaction evidence

1. **Real entry/controller:** clicked `看谱演奏`, not a CSS/DOM simulation. Outer ordinary header and unrelated tools disappeared; read-score controls and Exit appeared. App performance state was `page`, with the native-attempt limitation above.
2. **Manual default:** on initial entry and after a reload, Follow was unchecked. Clicked Next then Previous and saw the page count return correctly; no automatic playback started from those actions.
3. **Human input and range:** explicitly prepared audio, clicked C4, clicked High, clicked C5, then Low. Current-note feedback changed to the played notes; keyboard viewport actually moved. Labels and current page used the chosen note-name presentation.
4. **Follow is opt-in:** explicitly checked Follow, clicked `跟这句`, and observed the live phrase-loop session. Current page advanced from **60/63 to 63/63** during playback. This is actual following behavior, not solely inspection of a checked box.
5. **Manual override during playback:** clicked Previous while following. Follow became unchecked and the displayed page became **62/63**; it remained a manual view while the loop continued. Rotating into landscape changed pagination to six events and retained the current musical anchor (**52/53**), rather than resetting to the first page.
6. **Recording:** stopped guidance, exited, chose Record, started a take, then entered the score reader. Score-song/label controls appropriately locked while manual pagination and the actual keyboard remained usable. Clicked C4 and turned a page; recorded count was one. Repeated the active recording layout in 390 portrait, 844 landscape and desktop. No auto-generated guide notes were added by these manual-page checks.
7. **Stop and Exit:** used the real fixed Stop to finish both loop guidance and recordings. Exit returned `data-performance-mode` to `off`, hid `scoreReader`, restored cat to `.workbench` and real `playingSurface` to `.play-area`. Reentry worked. No detached or cloned input surface was substituted for the real instrument.
8. **Cold sound entry in landscape:** reloaded and reopened with sound state `idle`; Prepare Sound was enabled. Cat, score and keyboard remained together even while the sound controls were present. A network/audio error was not artificially injected.

## Limits and release implication

- These are desktop-browser viewport checks; not physical iPhone/Android touch, speaker listening, notch/safe-area verification or native-phone fullscreen acceptance.
- Native fullscreen failed in the observed tool environment and is not signed off. Supported app page-filling fallback worked through the actual controller; the ordinary-page/full-performance distinction was explicitly checked.
- Geometry checks and visual screenshots support the sampled states, not every song/page/device combination. Long existing 500 Miles lyrics were included; portrait four-event and landscape six-event rendering were both actually observed.
- The complete orange-cat asset route is unchanged. This review neither promotes a new character asset nor establishes new continuous animation quality.
- This is local candidate acceptance. Deployment byte hashes, production behavior and status-event publication belong to the main delivery audit and were not repeated here.

Checked local same-screen page UI is ready for that final production audit. Do not state that native fullscreen, physical-device behavior or publication are verified on the strength of this report alone.

## Final capture and cleanup note

At the main agent's request, captured fresh **320×568 active loop** and **844×390 active loop** screenshots through the same independent Chrome tool. The latter shows the current note's highlighted score cell and the human-played input surface together with the complete cat and fixed Stop. Both app states were checked as `score-reading` + performance `page`, not ordinary layout. These two JPEG screenshots are present inline in the tool record.

The available screenshot API returns JPEG bytes/inline images but exposes no documented `savePath` option. The reviewer informed the main agent and did **not** claim that `artifacts/score-reader-20261102/judge-reader-320.jpg` or `judge-reader-844.jpg` had been written. No alternate browser driver was used to work around that limitation. After capture the loop was stopped, Exit used, and default viewport reset.
