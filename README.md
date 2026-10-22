# Miao Beat

A small browser instrument playground. Follow a metronome, play your own music, keep a tiny event file. No falling-note game, score, account, microphone, or upload.

- Play: https://miao-beat.pages.dev/
- Research & decisions: https://farmcan.pages.dev/reviews/miao-beat/
- Delivery history: https://farmcan-seed.pages.dev/tasks/

## Status · 2026-10-22

Independent extraction from MiaoTI's keyboard-cat experiment. This release implements the **authorized UI and basic instrument workflow**: a controllable front-end cat, one chromatic octave, four percussion pads, 50–180 BPM metronome, 3/4 and 4/4, tap tempo, pocket reference scores, timestamp/key-code recording, local JSON export/import/replay.

**The old synthesized sounds remain temporary.** High-quality samples and the final character animation pipeline are researched, not silently approved or shipped. The generated plush-cat PNG under `design/` is a static concept, not a 3D model. Main recommendations require the user's direction confirmation.

## Run & verify

Node 22.13+ or 24 recommended; Python 3 for the local server. `npm ci` installs development-only JSDOM; the web app has no runtime npm dependencies or external assets.

```sh
npm ci
npm test
npm run dev
npm run build
```

Only `public/`'s explicit allowlist enters `dist/`; research, tests, generated concept art, credentials, and private event files are excluded. `release.json` records the Git commit and each source hash. `scripts/verify-production.py` compares the canonical deployment with those bytes.

Cloudflare uses the existing authorized account and independent Pages project `miao-beat`, branch main. Build then `npx wrangler pages deploy dist --project-name miao-beat --branch main --commit-hash <commit> --commit-dirty=false`; never deploy the repository root. Authentication is via local OAuth or external secret, never tracked files. Pages creation required its documented legacy `--force` creation route after CLI delegation failed; subsequent deployment does not use force.

## Ownership, reuse, and files

- `public/audio.js`: baseline independently synthesized MiaoTI experiment, adapted here for audio-clock scheduling and lifecycle cancellation. Not claimed as newly improved sample quality.
- `public/bindings.js`: a new virtual-piano layout, preserving stable recording codes. Inspiration starts with Bongo Cat; the old MIT notice is retained in `UPSTREAM-LICENSE.txt`. No Bongo Cat art or recordings copied.
- `public/clock.js`: bounded lookahead on the shared AudioContext, informed by official web.dev/MDN explanations; manual notes play immediately.
- `public/recording.js`: versioned one-shot events, strict validation, local files. Preserve engine/version compatibility if sounds change.
- `docs/research/`: sources, version snapshots, asset licenses, options, evidence gaps, and proposed phases. `scripts/export-review.py` publishes only selected reviewed derivatives to farmcan.
- `design/`: generated static character concept, source prompt, SHA and explicit limits.

MIT applies to our code; upstream notices and third-party musical works/sample/art rights remain separate. See research for each candidate. No third-party sample library is included in this release.
