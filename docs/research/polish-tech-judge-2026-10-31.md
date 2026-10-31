# Second polish pass · independent technical judge · 2026-10-31

Scope: read-only product implementation review of practice preferences, phrase selection/overview, activity-stop ownership, export layout/text and revised contact instrumentation. This judge changed only this report. No production delivery, real speaker latency or native encoded-file quality is inferred from tests.

## Initial release judgment

**Hold for the P1 pending-start cancellation defect below.** No P0 privacy/security issue found. The P2 restored-character startup mismatch is small and can be repaired in the same pass. The existing passing suite does not cover the reproduced pending-start stop-bar case.

**Final candidate judgment after parent repairs: no remaining P0/P1 identified in this scope; may proceed to build/provenance and production acceptance.** The initial findings are retained below with repair evidence at the end. No new art or continuous-motion acceptance is implied.

## Findings

1. **P1 · stopping from the activity bar can be followed by an awaited practice start.** Initial `public/app.js:329-331` stops current recording/session/clock but does not invalidate `lifecycle` or clear pending session ownership. A controlled invocation of the existing interaction fixture reproduced: start metronome; defer audio readiness; request guide; activity bar remains visible; click its Stop; guide hidden/clock stopped; resolve readiness; guide becomes visible and clock restarts. This is an observable cancellation failure, not a hypothetical data race. Minimal repair: the shared Stop path must invalidate pending guide/replay/record activation and refresh pending controls, using the same lifecycle ownership as explicit score stop/blur. Add a regression that resolves the old readiness promise after Stop and confirms it cannot restart or stop a later user operation.
2. **P2 · restored guitar/drums choice initially mounts a piano character.** Initial `app.js:33` restores only `instrumentSelect`; `mountCharacter(scene)` at36 reads `scene.dataset.instrument`, whose fallback remains piano. A fixture mount spy confirmed saved `guitar` produced initial character mode `piano`. Normal key input later calls `character.update` and fixes the instrument, but the refreshed initial scene is inconsistent. Minimal repair: synchronize scene mode to the final selected instrument (after URL override) before mounting. Add a startup spy/assertion rather than claiming a higher-level preferences-only test covers the renderer.

## Passed source/regression checks

| Area | Judgment and evidence |
| --- | --- |
| Safe preference persistence | `practice-preferences.js:2-10` emits a fixed object with compatible instrument/song, bounded integer BPM, allowed meter/phrase/loop/layout and version. Text titles, recordings and arbitrary extra fields are excluded. `app.js:31-33` caps input4096 characters and catches read/parse errors; persistence catches denied/quota errors. Reading choices starts no playback or recording. |
| Initialization order | Preferences are read before initial song population; compatible song choice is restored before phrase options are built at the final initialization block. Handlers capable of persistence are registered after initial population, avoiding partial initialization overwriting storage. No untrusted HTML is produced from stored preferences. Character-mode mismatch is listed separately above. |
| Phrase/score consistency | `practiceSelection()` bounds the selected phrase and reuses beat-domain `scoreWindow()`. Overview cards and native select dispatch the same change path. Preview content uses `textContent`; overview controls lock during active/pending work. Original event indices remain available for score highlighting; labels and lyric excerpts do not synthesize input events. |
| Export retains selected phrase | In recording replay and media export the old song/phrase are saved before rebuilding instrument options, then the phrase is restored only if the song stayed the same. Actual selected score events are captured before that rebuild. This addresses the previous silent reset to whole song. Human-only take persistence stays inside live `hit()`, outside score scheduling/export playback. |
| Export safety and canvas geometry | One complete source scene is drawn once, without cropping/limb composition. For square720×720, original720×880 and portrait720×1280, scene/frame rectangles stay inside the canvas and above the caption/footer. Heading wraps to at most two lines, fixed metadata/caption use measured ellipsis, and user text is drawn as text rather than markup. The new print treatment leaves room for header/title/description. Native-font appearance, actual text extents and final encoded playback remain real-browser/media acceptance. |
| Existing capture failures/cancellation | Prior regression still verifies source errors remain sticky during a failed active job, clear on capture cleanup and permit a later export. Existing media-start cancellation regression verifies a stale encoder cannot overwrite a later recording. The activity-bar pending-start hole is a separate path. |

Executed `node --test scripts/practice-preferences.test.mjs scripts/interaction.test.mjs scripts/media-export.test.mjs scripts/full-frame-character.test.mjs scripts/guitar-motion.test.mjs scripts/core.test.mjs scripts/guidance.test.mjs`: **76/76 pass** in the initial candidate. Audio and encoders are controllable fixtures; passing is not speaker/device validation.

## Contact metric boundary

Current `full-frame-character.js:133,190` adds accepted strike sequence and records contact delay once for the latest unmeasured strike, instead of letting subsequent contact redraws overwrite the value. This is a useful measurement correction. It measures accepted animation trigger to canvas contact draw invocation, not physical key event to audible output/compositor presentation. Rapid interrupted/same-pose inputs may be unmeasured, so report sample count/misses alongside any distribution; do not directly compare new values to the previous overwritten metric baseline or claim all inputs gained smooth motion. Existing orange complete-image identity remains unchanged.

## Independent repair recheck

- P1 repaired by parent: `stopActivity` now increments lifecycle and clears pending session/record flags before stopping current work. New regression covers both a deferred guide and a deferred recording while the metronome keeps the stop bar visible; resolving old readiness no longer restarts either path, and controls unlock.
- P2 repaired by parent: the final selected instrument, after the explicit URL override, is copied into `scene.dataset.instrument` before character mount. The new mount-spy regression confirms saved guitar initializes as guitar.
- Contact metric correction verified: the real renderer regression strikes a simultaneous held pose, paints its first contact at10 ms, then releases one held key to force a different complete contact frame at130 ms; the delay remains10 ms. It exercises the originally misleading redraw path, not merely a pure counter helper.

Independent final execution of the same seven-file focused command passed **78/78**. Source review and regressions verify the scoped fixes; the parent still needs current build/provenance hash acceptance, real browser layout/text checks, native media playback and production identity checks. Updating only the changed renderer runtime hash must not imply that image assets or motion quality were replaced.
