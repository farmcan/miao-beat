# Miao Beat

A small browser instrument playground. Follow a metronome, play your own music, keep a tiny event file. No falling-note game, score, account, microphone, or upload.

- Play: https://miao-beat.pages.dev/
- Research & decisions: [research index](docs/README.md)
- Generate the next motion video on another computer: [one-document handoff](docs/video-animation-handoff.md), with committed reference images and copyable prompts.
- Public products never link back to the owner’s personal website or research hub.

2026-10-26 · 0.13.0: each confirmed guitar note or chord retriggers a visible right-paw contact and lift, even when the same note repeats. Seventeen complete-scene raised-paw images pair with the original contact images, keeping the left fret pose stable within each stroke. See [current release, asset sources and limitations](docs/guitar-pluck-release-2026-10-26.md).

2026-10-26 · 0.12.1: one confirmed input creates one guitar action. Removed the multi-note path that made a single K look like repeated playing. Release holds the final fret; long unreviewed changes land directly on the target plus one short recoil. See [0.12.1 historical release and limits](docs/guitar-single-action-fix-2026-10-26.md).

2026-10-26 · 0.12.0: guitar uses offline RIFE whole-scene intermediate frames for interruptible strumming/fret changes and return. Short taps finish the latest stroke; new notes take over immediately. A “平滑动作” toggle compares the old discrete swaps. Open `?instrument=guitar` for the pilot. Every selected tile is a complete cat, both paws and guitar; no separated limb composition. Audio and recording timing remain independent. See [0.12 historical verification, superseded by the single-action correction](docs/guitar-motion-release-2026-10-26.md). Naturalness awaits user review; exact fingering is not taught.

2026-10-25 · 0.11.0: piano (56), guitar (18) and drums (25) now respond with complete AI-generated cat-and-instrument scenes. Each frame contains the entire cat, both connected paws and instrument together; the product never combines separate limb/body images. Guitar has thirteen single-note and four simplified-chord gestures; drums have eight voices and sixteen two-side combinations. These are discrete cartoon poses, not precise fingering lessons or newly generated continuous video. See [0.11 release](docs/whole-band-release-2026-10-25.md). Marimba motion remains unfinished and is labelled in the product. The 0.9 separated-arm experiment remains rejected and withdrawn. Visit counting uses a 24-hour browser cookie, starts when enabled, and is not unique people or historical PV.

## Existing musical features · 0.7 baseline retained

Independent extraction from MiaoTI's keyboard-cat experiment. Four **self-hosted sampled instruments**: upright piano, marimba, nylon guitar, and eight drum voices. Guitar adds simplified C / Am / F / G six-note strums on 1–4; melodic notes use A–K plus W E T Y U, and drums use Z X C V / B N M L. Simultaneous key presses and pointer input share one path.

50–180 BPM metronome, 3/4 and 4/4, tap tempo, small reference scores, local timestamp/key-code recording/export/import/replay. New files use v2/sample-v1; old v1/ui-synth-v1 files retain their original synthesized sound. No multi-track editor or audio capture. Historical articulated and precise-contact rigs remain in source for provenance; they must not be activated in production under the user's whole-frame-only constraint. Technical tests of those historical rigs do not establish acceptance or override that constraint.

Mobile screens get larger scrollable piano keys and bigger chord/drum pads. **全屏演奏** requests native fullscreen when available and falls back to a page-filling performance view; a pinned exit control remains available. Short landscape layouts prioritize the selected instrument. Real iPhone/Android touch and native fullscreen remain device acceptance items.

## Run & verify

Node 22.13+ or 24 recommended; Python 3 for the local server. `npm ci` installs JSDOM for tests and pinned smplr 1.1.0. Build vendors the runtime; the deployed app loads code and samples only from its own origin. Run `npm run build` before the dev server to prepare vendor files.

```sh
npm ci
npm run build
npm test
npm run dev
```

Only `public/`'s explicit allowlist enters `dist/`; research, tests, generated concept art, credentials, and private event files are excluded. `release.json` records the Git commit and each source hash. `scripts/verify-production.py` compares the canonical deployment with those bytes.

Cloudflare uses the existing authorized account and independent Pages project `miao-beat`, branch main. Build then `npx wrangler pages deploy dist --project-name miao-beat --branch main --commit-hash <commit> --commit-dirty=false`; never deploy the repository root. Authentication is via local OAuth or external secret, never tracked files. Pages creation required its documented legacy `--force` creation route after CLI delegation failed; subsequent deployment does not use force.

## Ownership, reuse, and files

- `public/audio.js`: original synthesis retained for the metronome and exact legacy-file playback.
- `public/sampled-audio.js`: strict self-hosted loading, bounded voices, 15 ms strum spacing and initial bounded attack-window gain calibration. Uses smplr; physical listening and device latency remain separate from automated tests.
- `public/bindings.js`: a new virtual-piano layout, preserving stable recording codes. Inspiration starts with Bongo Cat; the old MIT notice is retained in `UPSTREAM-LICENSE.txt`. No Bongo Cat art or recordings copied.
- `public/clock.js`: bounded lookahead on the shared AudioContext, informed by official web.dev/MDN explanations; manual notes play immediately.
- `public/recording.js`: versioned one-shot events, strict validation, local files. Preserve engine/version compatibility if sounds change.
- `docs/research/`: sources, version snapshots, asset licenses, options, evidence gaps, and proposed phases. `scripts/export-review.py` publishes only selected reviewed derivatives to an owner-configured destination.
- `design/`: generated static character concept, source prompt, SHA and explicit limits.

MIT applies to our code; upstream notices and third-party musical works/sample/art rights remain separate. See research for each candidate. The deployed samples include FreePats piano/guitar and Virtuosity drums (CC0), and University of Iowa marimba (its unrestricted-project-use statement, not CC0). See `public/samples/LICENSES.txt` and `docs/research/sample-manifest-2026-10-22.md`. Raw source archives are excluded from Git and deployment.

Version 0.5 added optional audio-clock practice guidance, a larger pocket-score library and original drum exercises. “Listen” plays the reference; “Play along” provides timing/key cues without scoring or adding automatic notes to the recording. See docs/v2-release-2026-10-22.md for verification and limits.

Version 0.6 improves the first-screen sound entry, puts free-play keys before scores, and introduces the original indie-cat contact rig. See [release notes](docs/character-ui-release-2026-10-22.md). The more friendly character remains an aesthetic hypothesis; no human preference validation is claimed.

Version 0.6.1 links the MiaoTI and MiaoTarot public products and reuses the existing optional Alipay support image. All music features remain free; the app does not execute payments.

Version 0.7 brings the orange musician into the full product and unifies the instrument artwork and warm, quieter interface. Desktop places the player next to the character; mobile keeps the full cat and primary inputs accessible. Practice guidance stays above the keys, with both visible in short landscape performance mode. See [orange release evidence](docs/orange-product-release-2026-10-22.md).
