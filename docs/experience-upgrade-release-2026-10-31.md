# Experience upgrade · 0.17.0 · 2026-10-31

## Implementation and local acceptance

- Mobile first viewport fits the entire smaller orange cat, sound entry, playable keys and range navigation. Four instruments are directly visible. Free play/practice/record reveal their relevant tools; mobile primary actions precede metronome settings. An activity strip keeps stop/cancel reachable across modes.
- First cold input prepares sound with progress, retry and explicit readiness; stale taps are not queued. Desktop letter, fixed-note-degree and note-name labels remain selectable and agree with score/guidance. Fixed C-based numbers are explicitly not movable-do solfege in F-major arrangements.
- Current draft and previous take remain in local browser storage. Empty recording and invalid import preserve the existing take. Restore swaps the last two takes; deliberate two-click clear removes them. Quota/corrupt storage failures explain the limitation and preserve JSON download. Active takes checkpoint at most about once per second; abrupt browser/process loss can lose the most recent unsaved fraction. There is no cloud sync or identity store.
- Any existing phrase can be demonstrated/guided/looped. Actual BPM and recommended BPM are separate, with one-click adoption. Count-in and loops use the shared audio clock, including fractional pickups; each loop includes preparation beats. Only physical user key/pointer inputs enter the human recording.
- Export supports original 720×880, portrait 720×1280 and square 720×720 with optional title. Each output fits one full cat/paws/instrument source. Export renders the selected phrase/whole score once, regardless of the practice loop switch; it never exports an infinite loop or overwrites the personal take.
- Whole-image decode cache has a 40/80 MiB estimated RGBA budget (mobile/desktop), not a browser/GPU memory guarantee. Common piano frames are decoded early; required capture images are fetched/decoded before recording, but the bounded cache may evict older frames. Capture tracks full signatures, aborts sustained unresolved paints, image failure or a long capture-frame gap. Ordinary replay discloses skipped scheduling. No new artwork/3D or rejected continuity study is shipped.

## Independent judges and repairs

All three judges inspected the candidate independently, including browser paths, rather than approving the builder's description. Historical findings and repairs are retained in their reports:

- [UI judge](research/experience-ui-judge-2026-10-31.md): 390×844 mobile and portrait performance, high-key reachability, 844×390 landscape and complete-scene portrait output. Found portrait performance 640px overflow; repaired and rechecked at 350px playable width inside a 390px viewport.
- [Product judge](research/experience-product-judge-2026-10-31.md): actual recording, reload, empty-take protection, previous-take recovery, invalid import, recommended tempo, phrase loop and square/portrait native output. Found hidden running sessions after mode changes; cross-mode activity/stop repaired and rechecked.
- [Technical judge](research/experience-tech-judge-2026-10-31.md): found a timeout renewed by repeated target changes and fractional-phase beat/barline errors. Both repaired; blocked-decode regression and fractional-pickup tests pass. No remaining material implementation blocker in the reviewed scope.

Full automated suite: **141 passed**, including current and historical regressions. Targeted whole-frame checks after telemetry refinement: **8 passed**. Automated audio/encoder fixtures are not physical listening evidence.

Parent browser: actual three piano inputs → stopped take → reload restored all three → portrait MP4 saved. `ffprobe` confirms H.264 video, AAC audio, 720×1280 and 2.005333 seconds. Independent product judge generated and played both 720×1280 and 720×720. Local files/screenshots are under ignored `artifacts/experience-20261031/`.

## Anonymous referral attribution

MiaoTI's deployed `/v1/` introductory and result links already carry `utm_source=miaoti`; this was checked against the actual production HTML. Tagged visits classify explicitly; otherwise only the referring hostname is reduced to a fixed bucket. Arbitrary UTM text and raw referrer URLs are never forwarded by this feature.

Buckets: `miaoti`, `miaotarot`, `xiaohongshu`, `douyin`, `other-project`, `other`, `direct-unknown`. Same browser counts once in the existing 24-hour cookie window, attributed to its first counted arrival in that window. This is an arrival aggregate, not a person-level journey, conversion funnel, first-ever acquisition source or exact unique-person count. Cookie clearing, concurrency and undetected bots can affect it. Missing referrer is unknown, not proof of a typed/direct visit. Earlier totals have no historical source breakdown.

Reuse existing D1 `site_counters` with bounded `miao-beat:source:v1:<bucket>` keys. Total and source use a D1 transaction batch; no schema migration, new database or paid analytics service. Source counts are owner-readable through authenticated D1 administration; the public API continues to expose only the cumulative total. New source statistics start at deployment, not the original counter's start date.

Actual local workerd/D1 validation: total 1→2 and MiaoTI bucket absent→1 on a same-origin empty POST; repeating with the cookie leaves both unchanged. Production is checked separately below.

Useful tagged links:

- MiaoTI: `https://miao-beat.pages.dev/?utm_source=miaoti&utm_medium=referral&utm_campaign=play-next`
- MiaoTarot: `https://miao-beat.pages.dev/?utm_source=miaotarot&utm_medium=referral&utm_campaign=play-next`
- Xiaohongshu: `https://miao-beat.pages.dev/?utm_source=xiaohongshu&utm_medium=social&utm_campaign=launch`
- Douyin: `https://miao-beat.pages.dev/?utm_source=douyin&utm_medium=social&utm_campaign=launch`

## Production acceptance

Pending deployment and canonical byte/API/browser verification. Public start event persisted through the existing Seed task-status mechanism; end event follows actual production acceptance. Physical iPhone/Android touch, speaker latency and platform-native sharing remain unverified.

## Capture retry repair · 0.17.1

A final independent fault-injection check reproduced a sticky capture-failure flag preventing the next export's initial paint, even after normal cleanup. Capture-mode cleanup now clears the failed session flag; failures remain sticky during that session. The regression first failed on the old implementation and passed after the one-line repair. This is a recovery fix, not a claim of new animation frames.
