# Experience upgrade · independent product judge · 2026-10-31

Reviewer: product judge, separate from the implementation builder. Scope: plan items 2/3/4/6 and tool disclosure; no product files changed. This is a local candidate review, not production or physical-phone acceptance. The original orange-cat complete-image route remains the baseline.

## Verdict

The intended product loop is materially better: a recoverable take, short phrase entry, explicit tempo choice and usable portrait export are real implemented paths. The first-round mode-switching regression below was reproduced, reported, fixed by the builder and independently rechecked. The tested desktop product paths now pass; production and physical-phone acceptance remain separate.

| Plan item | Status | Independently observed evidence | Limits / remaining work |
| --- | --- | --- | --- |
| 2 · local takes | **Complete for tested desktop paths; partial device/error acceptance** | Chrome at `http://localhost:8894/?analytics=internal`: prepared audio, recorded C4/D4 by clicking actual keys, stopped at 0.9 s / 2 inputs; refreshed and saw the same restored take. Empty recording retained it. A new E4-only take enabled previous-take restore; refreshed, restored previous and returned to 0.9 s / 2 inputs. Imported existing `public/samples/manifest.json` through the actual file chooser: rejected as unsupported recording, original take remained. | Clear uses an explicit second click in code; storage-denied/corrupt payload paths are covered by implementation tests, not physical-device testing by this reviewer. No cloud storage or upload was introduced. |
| 3 · actual/suggested tempo | **Complete for tested path** | Selected Five Hundred Miles: actual 96 BPM / suggested 80 BPM remained distinct. Clicked “用建议 80 BPM”: actual slider and hint became 80. | Human acoustic tempo verification was not performed. |
| 3 · phrase / loop / first phrase | **Complete for local functional path; partial musical-device acceptance** | Selected phrase 26 with its correct lyric, enabled loop and started guide. The guide displayed that lyric and remained running past one 13.9-second phrase. “先练第一句” subsequently selected phrase 1 and began its 4-beat preparation. Three targeted interaction tests independently rerun and passed, including shared-clock phase over several rounds and human-only recording. | I did not measure physical audio latency or subjectively judge every fractional pickup/count-in. Current loop deliberately includes preparation and bar padding; it is repeated practice, not a gapless backing loop. |
| 4 · export layouts and title | **Complete for portrait local output; partial cross-browser/device acceptance** | Actual two-input draft exported using portrait + title “产品独立验收”. App reported MP4 / 720×1280 / 409 KB; native HTML video metadata read 720×1280 and 2.386333 seconds. Actual preview showed the complete connected orange cat, paws and keyboard, with title; no cropped limbs. Square export was separately initiated and its result checked below. | This does not establish phone share-sheet, Safari encoder support or physical-speaker quality. Original/audio/JSON alternatives are retained in source and UI; not every alternative was re-exported by this reviewer. |
| Tool disclosure | **Complete for tested desktop paths after bounded repair** | Initial free mode hides practice/record tools; practice and recording buttons reveal their relevant controls. First-round gap and successful second-round repair are recorded below. | Phone layout is another reviewer's remit. Preserve practice↔record switching so human recording during guidance remains possible. |
| 6 · delivery and audit | **Partial / production unverified by this reviewer** | This independent review and the targeted tests exist. Browser evidence above comes from local real interactions. | Deployment bytes, production route behavior and Seed status publication were not independently verified here. The builder/other reviewer must supply those separate proofs. Local test success is not publication. |

## Reproducible issue

1. Enter 跟谱练 and click 先练第一句.
2. While preparation/playback is active, click 随便弹.
3. The guide remains active above the keys; all instrument switches remain disabled; the practice stop control and metronome controls are absent from the visible/accessible UI.

`setMode` currently changes only `body.dataset.mode`; CSS hides `.session-tools` in free mode. Recording mode has the analogous risk of hiding an active recording when leaving it. This is not a crash or loss of the saved take, but the chosen mode and actual operation disagree. It is a meaningful regression in the new layered UI.

Recommended bounded fix: a compact active-operation indicator with the relevant stop action across modes, or stop/finish when entering free mode while preserving guidance during practice↔record transitions. Verify guide, demo, metronome, recording and export separately; the cross-mode stop must not discard the just-recorded take.

### Repair and independent recheck

Builder added a cross-mode `activityBar`. Reloaded the actual candidate and repeated “跟谱练 → 先练第一句 → 随便弹”: the visible activity said “跟弹中 · 旋律你来弹” with a Stop button. Clicking that Stop removed guidance and released all instrument switches. Separately started recording, clicked C4, switched to free mode: activity said “录制中 · 只记录你的按键”. Its Stop ended recording; returning to recording mode showed 1.0 s / 1 input, local saved status, playback/export available and previous take retained. The material first-round gap is therefore resolved for both these tested paths. Other activity variants are covered by the builder's regression check, not all individually exercised here.

Square native-video metadata was also independently checked before reload: 720×720, readyState 4, 2.387133 seconds. The portrait still above was visually reviewed; square content framing was not separately pixel-reviewed in this pass.

## Value judgment and at most three further suggestions

1. **P2: persist only convenient non-sensitive choices** such as selected song, BPM, phrase and export layout, with safe defaults. Refresh currently restores the take but resets these practice choices; a future visit can resume more naturally. Do not auto-start playback or recording.
2. **P2: make practice-loop behavior explicit** with “每轮含预备拍”; a later gapless option should be separate and only justified by actual user need. Current timing is suitable for repeated practice and should not be sold as a beat looper.

No accounts, scoring, leaderboard, large editor or new 3D effort is warranted by this review. These recommendations remain proposals and are not proof of retention improvement.

## Verification run

`node --test --test-name-pattern='local draft|corrupt draft|phrase loop|first-phrase' scripts/interaction.test.mjs` — 3 matched tests passed, 0 failed. This is simulated interaction evidence, separate from the actual Chrome actions recorded above.
