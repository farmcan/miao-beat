# Score reader and share outro · independent technical judge · 2026-11-02

Scope: read-only review of `public/score-reader.js`, app/performance integration, `media-export.js`, static QR generator/brand data and public page preview. This judge modifies only this report. Real-device touch/speaker behavior, real native fullscreen event ordering and actual encoded-video QR decoding remain parent production acceptance; fixture evidence below does not replace them.

## Initial judgment

No P0 found. **One P1 cleanup ownership risk needs the one-line guard and regression described below before release.** Otherwise the reviewed reader and outro design can proceed to real browser/native media acceptance. No new cat artwork/animation approval is implied.

**Final candidate judgment after repair: no remaining P0/P1 identified in this scoped technical review; may proceed to native-media, QR scan and production acceptance.** Initial finding and repair evidence are preserved below.

## P1 · preview cancellation can disconnect an unowned audio output

Initial `public/media-export.js:16,61-64` loads the optional preview image before constructing the media-stream destination. If the document becomes hidden during that wait, it throws before `destination` exists; the common cleanup still calls `audio.analyser.disconnect(destination)` with `undefined`. The analyser also feeds the user's real speaker output (`public/audio.js:13`). AudioNode has both destination and numeric-output disconnect overloads, so passing undefined is not an acceptable owned-edge cleanup operation. The caller must only disconnect when its actual destination exists. See [MDN disconnect overloads](https://developer.mozilla.org/en-US/docs/Web/API/AudioNode/disconnect).

Read-only controlled reproduction against the real exporter: provide an Image whose load is deferred, begin a branded video, make `doc.hidden=true`, complete image load. Export correctly rejects and no encoder was created, but the disconnect spy records **one call with undefined**. This proves the invalid cleanup call, not real-browser speaker silence. Minimal fix: `if(destination)` before disconnecting it; retain the other cleanup. Meaningful regression must assert no undefined/all-output disconnection when cancellation occurs during preview preparation, and confirm a subsequent export remains possible.

## Reader implementation and controlled verification

- `makeScorePages` uses original score indices/metadata; 4/6-page chunks never rewrite score duration, notes, phrases or input events. Independent iteration across every song for both page sizes compared flattened page events with `scoreEvents(song,song.bpm)` and matched exactly.
- The reader moves the actual `catStage`, `playingSurface` and `soundEntry` with original comment placeholders; it does not clone controls/canvas or create alternate input paths. Independent integrated fixture opened a simulated native fullscreen reader, then dispatched native exit: all three nodes returned to their exact original parents and the score-reading class cleared.
- During recording, manual page navigation stays enabled while song/labels/guide controls lock. Independent integrated fixture recorded one A input, changed reader page, stopped and exported JSON: still exactly `[[0,0]]`, with the original practice phrase unchanged. Paging generated no sound or stored input.
- Guide updates use original `current.index`. With follow enabled, advancing the shared audio time moved the page; a manual Prev disabled follow and subsequent audio-time advancement did not move the chosen page. Playback scheduling was not restarted by page navigation.
- Orientation resizing retains the first visible original event (or current guided event when follow is enabled) by index, rebuilding only page grouping. Current sync state is retained when the page is re-rendered. The portrait media query selects 4 events versus 6; real rotation/layout visibility still requires a browser/device check.
- Reader label changes route through the original key-label control and formatter; disabled state comes from the original app's media/session/record state. Native fullscreen exit is propagated via the performance controller's change event rather than polling or guessing orientation permissions.

## Outro implementation

- The optional video-only outro keeps its timer, stream and animation-loop state per job. Repeated Stop is idempotent; Cancel/error/background cleanup clears the outro timer and tracks. Once settled, delayed timer callbacks cannot publish a success. The reader/media controls lock while media work is active.
- Outro rendering deliberately stops checking the now-finished source animation but retains the >500ms capture-frame-gap guard. It renders a real static public product preview, fixed public URL, QR and plain address. It never writes synthetic notes to saved events. Audio-only export still stops immediately, and JSON data is not extended by the2-second visual card.
- The static QR matrix exactly matches `qrcode@1.5.4` generation for `https://miao-beat.pages.dev/` with correction M; its size is29 modules and the renderer supplies4 quiet modules at7 pixels each. This validates source matrix identity only: the actual encoded final-frame scan remains required.
- `scripts/generate-share-qr.mjs` verifies pinned package version and MIT license and copies attribution; no runtime QR SDK, credential or personalized URL is introduced. This judge viewed `public/share/page-preview.jpg`: it shows public game UI and the complete connected orange cat/instrument, with no personal record visible. Real production-page identity and license preservation remain build acceptance.

## Verification boundaries

Controlled integration script passed: native-exit DOM restoration, record-page-view-only behavior, guide follow/manual page behavior, all-song pagination event preservation. The separate cleanup reproduction exposed the P1 above. Parent is adding permanent regressions; final executed suite counts and repair check will be appended rather than inferred. Visual fit at320/390 portrait and844×390 landscape, physical mobile touch/audio, native encoded outro duration and QR readability are unverified by this code review.

## Independent final repair verification

Parent guarded cleanup with `if(destination)` and wrapped `onPhase` notification so a UI callback exception cannot prevent scheduling outro completion. The new preview-preparation regression sets `doc.hidden` before image load resolves and verifies rejection, an empty disconnect-call array, zero encoders and no surviving timers. This closes the observed undefined-destination cleanup path. New controlled-timer outro regressions verify that Stop continues recording for2 seconds and draws QR modules, then completes; Cancel or backgrounding rejects and clears all timers/rAF, while audio-only export adds no tail.

Independent execution: `node --test scripts/interaction.test.mjs scripts/performance.test.mjs scripts/media-export.test.mjs` passed **54/54**; `node --test scripts/score-reader.test.mjs` passed **4/4** (total **58/58**). The new reader tests cover all-song pagination, manual/follow/return/resize index continuity, source-node identity/listener restoration on exit, text-control keyboard exclusions, page boundaries and media-lock state. The independent integrated app fixture additionally exercised simulated native exit and verified record-time page navigation leaves JSON human-only. Source code for samples/audio engine and the recording format was not changed by this feature. This judge changed no product code/tests.
