# Independent design-reference judge · 2026-10-31

Scope: compare three relevant live browser music toys with the currently deployed Miao Beat, then identify a small set of worthwhile UI/design follow-ups. This reviewer did not build the Miao candidate. Research only: no product code, asset copying, publishing, new runtime, 3D sourcing or account changes.

## Sources and actual inspection

| Product / primary source | Actual inspection on 2026-10-31 | Limits |
|---|---|---|
| [Bongo Cat](https://bongo.cat/) · [source linked by its live page](https://github.com/Externalizable/bongo.cat) | Viewed full desktop screenshot and key legend; pressed A and inspected the resulting cat/instrument screen. | No instrument-by-instrument audio fidelity comparison or mobile physical test. Its partial-body composition is not an admissible replacement for Miao's whole-character frame requirement. |
| [Patatap](https://patatap.com/) | Initially saw loading 0/26, then the actual entry prompt. Pressed A/S/D; screenshot showed a large pink circle against the changed canvas background, and the promotional/navigation chrome had yielded to the visual performance. | The initial loading state was observed; no claim of measured load time or universal instant startup. Audio timbre and sound/animation latency were not measured or listened to independently. |
| [Chrome Music Lab: Song Maker](https://musiclab.chromeexperiments.com/Song-Maker/) | Loaded in actual Chrome, clicked three visible grid cells, clicked Play, and inspected the colored note blocks, playback column, Stop, tempo and Save-enabled states. Stopped playback. | Did not submit Save or test remote sharing, microphone, collaboration or mobile touch. A text-fetch tool returned a compatibility/tech-trouble page while real Chrome worked: the browser result, not that fallback, informs this judgment. |
| [Miao Beat production](https://miao-beat.pages.dev/?analytics=internal) | Loaded actual deployed UI, viewed free-play screenshot, clicked Practice and inspected the actual mode/tempo/phrase controls. Compared with this reviewer's earlier candidate interaction/export review. | Main agent reports production commit d4ef57a and 290 matching public-source hashes; this design review did not independently rerun the deployment byte audit. |

Screenshots were visually inspected through the browser tool during this review: Bongo full stage/key legend, Patatap loading/entry/triggered shape, Song Maker empty and three-note playing grid, Miao current free-play and Practice. These descriptions are evidence notes, not fabricated screenshot artifacts or pixel-performance measurements.

## What is more mature, and what does not transfer

### Bongo Cat: the shortest visual explanation

The top legend shows compact keycaps directly naming their sound. The central diagonal table edge, small cat face and large instruments form one readable scene; the rest of the screen is mostly white. A visitor can infer the action from the picture and keycaps without reading a controls panel. This is a stronger single-action presentation than Miao's current desktop entry, where the warm title, large full cat, separate virtual keyboard, drum pads and below-fold mode row compete for the first scan.

It is not an overall feature winner. The inspected screen does not teach phrase practice or expose Miao's take recovery and media-export path. Its table crop and separate-style limb construction must not be imported as Miao's production asset method. Borrow the economy and spatial relationship of instructions to action, not its cat art or composition constraint.

### Patatap: one coherent performance surface

Its live input produces a visual event with obvious scale, palette and motion against a single canvas, and the interface recedes once playing. The captured pink circle/background event communicates a deliberate visual vocabulary even without a mascot. That is more coherent as a visual performance than a collection of normal form controls with active states.

Miao should not become a flashing abstract audiovisual instrument. Its appeal is a recognizable cat playing a recognizable instrument; random full-screen geometry would obscure that contact and distract during phrase practice. The applicable lesson is to art-direct the existing stage and exported frame as a whole, with consistent hierarchy, spacing and color, while leaving the connected cat/paws/instrument intact. Also retain Miao's explicit prepare/ready/error states: Patatap's initially opaque 0/26 is not a better loading model in this session.

### Song Maker: creation, transport and result occupy one view

The actual desktop screen gives most area to a pale, regular grid; three entered notes become distinct colored blocks. The time column moves through the same surface. Play is the most salient blue control, the tempo value is explicit, instrument choices are in the same lower strip, and Save becomes available after an edit. This is a stronger hierarchy for understanding "where am I, what can I change, and how do I hear it" than Miao's small generic phrase selector and text-heavy practice setup.

Miao is a human-played toy with practice and a cat; Song Maker is a grid composition workflow. We should borrow its visual overview and hierarchy without adding a grid sequencer, multitrack editor, microphone or automatic notes to a human recording. A phrase overview can be derived from already-present score phrases and is far smaller than building another composition product.

## Miao's differentiated value and present weakness

**Value in this compared set:** the recognizable orange cat plus sampled instruments, freely played keyboard/pads, optional phrase guidance, local take recovery and complete-cat video/audio export make a useful "play a little, learn a little, keep a little performance" combination. This is an observed product combination, not a claim that no other product offers these features. The current three-mode disclosure and phone-size layout repair already improve the earlier version and must not be listed as missing.

**Main weakness:** the primary interaction still has a split personality: a friendly landing page above, a small instrument panel beside the cat, and the choice of Free/Practice/Record below the stage and drum pads. The practice selector conveys phrase index but little musical content. The functional export layouts do not yet have the same degree of editorial composition as a deliberately designed performance card. These are design judgments from actual screens; no user study or retention improvement has been measured.

## At most three next improvements, in order

1. **Bring the existing three-mode choice into the first scan.** Reuse Free / Practice / Record, but place a compact mode row above the instrument surface or in a small persistent player header. Keep the current progressive disclosure. In Practice, put selected song/phrase/Stop in that local context; in Record, put record status there. This addresses discoverability without adding a feature family or forcing fullscreen. Acceptance: in ordinary desktop and 390×844 browser view, all three intentions are discoverable before scrolling past the instruments; the selected mode and its next primary action are unambiguous. Preserve the complete-cat/input visibility gate.
2. **Replace anonymous phrase numbers with a compact musical overview.** Keep the existing phrase loop engine and add a small phrase strip with lyric excerpt when available, otherwise the first few note labels; indicate selected range and current position. Keep a text/select equivalent and current display preference. Borrow Song Maker's overview-to-playhead relationship, not its sequencer. Acceptance: a person can identify and resume an intended phrase without auditioning every numbered option; the strip, key cues and lyric/current-note display agree. Human input remains the only recorded input.
3. **Give exported videos a deliberately composed performance-card layout.** Improve the existing original/square/9:16 canvas presets rather than adding an editor: consistent title/instrument hierarchy, intentional full-scene scale, balanced negative space, a subtle boundary/background treatment compatible with the complete source image, and a concise footer that identifies the performance. The 9:16 preview checked earlier is complete and usable; this suggestion is about presentation, not repairing a failed export. Acceptance: original/square/portrait previews each look intentional at phone-feed size, title remains legible, no white source-image boundary looks accidentally pasted, and no cat/paw/instrument is cropped or reconstructed from separate limbs. Preserve actual media format/duration disclosure and existing local-only flow.

The first two are lightweight UI changes; the third is bounded canvas art direction. They are recommendations for a future iteration, not claims that the deployed version is incomplete, nor authorization to post content on social platforms. Do not copy reference art, sounds or musical works, and do not infer that code licenses cover any of those assets.
