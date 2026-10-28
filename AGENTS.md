# Miao Beat

- Independent lightweight browser music toy; research first. Current authorization: research + UI redesign + adjustable metronome + simple common key scores + local event recording/export/import/replay + Cloudflare publication. User confirmed real-sample audition followed by an original plush 2.5D cat; subsequently explicitly authorized guitar and drum-kit versions. Keep these lightweight; future unrelated gameplay changes still require scope agreement.
- Keep facts, tested behavior, hypotheses, and pending approval distinct. Do not call a UI prototype a finished audio redesign.
- Source baseline: MiaoTI experiments/keyboard-cat; original inline art and Web Audio synth were created there. Bongo Cat-derived key mapping retains full MIT license. Code and audio/art/sample licenses are separate.
- Work in main; publish only public/ to Cloudflare Pages miao-beat. Research exports use an owner-configured destination; public products/README must not link back to the owner’s personal site, reviews or status pages. No credentials or private records in public exports.
- Public deliveries/start/end events use existing Seed tasks status mechanism. Preserve historical events; persist pending if publishing fails.
- Key acceptance: actual press/click → audio/visual response; metronome shares audio clock; real browser QA. Mobile physical speaker listening is not implied by desktop QA.

- 2026-10-22 v2 explicitly authorized: expand selectable pocket scores, optional beat/key/time guidance, research good references and improve animation, then deploy the second version. Guidance is a practice aid, not scoring; actual human input must remain free and must be the only input written to a recording.

- 2026-10-25 explicit user constraint: every production cat frame must contain the complete cat, arms/paws and instrument together in one image or one captured video frame. Do not compose a body plate with separate arm textures, limb meshes or independently drawn geometry. Internal pose references may be generated for authoring, but are not production assets or proof of completed whole-frame animation.

## Character quality gate · user correction 2026-10-28

- The first Blender pilot is **visually rejected**. It proves the render/input/export chain, not a successful character redesign. Do not reuse its primitive body/head/limb construction as the accepted visual baseline.
- The approved appearance reference is `public/character/instrument-scenes-v1/guitar/idle.jpg`: preserve the squat pear silhouette, rounded-square face, short integrated limbs, expressive sideward gaze, short plush fur/embedded tabby markings, guitar scale and relaxed hold. A technically valid rig or higher sample count cannot compensate for losing this identity.
- Before calling a character/animation iteration complete, obtain independent subagent reviews against the actual original reference **and the current rendered result**: at least three roles covering identity/silhouette/expression, materials/craft/lighting, and motion/contact/UI experience. Reviewers must not be the asset builder. Persist concrete gaps, P0 blockers and evidence in docs. A builder's self-review alone is insufficient.
- Run the independent reviews at both the gray-model and shaded-still gates, before animation expansion; a final review alone is too late. The motion reviewer at a still gate checks grip, joint structure and animatability, with unmade clips/web behavior explicitly unverified or not applicable.
- Review matched-camera full-body and face/paw crops first. Any P0 visual regression blocks art delivery and further animation expansion; do not average it away with passing functionality tests or a composite score. Unpassed work remains a technical study, never a finished optimization.
- Prefer suitable licensed models/rigs/material workflows and reference-driven reconstruction over repeated primitive scripting. Verify code, model, weight and output terms separately; do not quietly replace Miao with a different stock cat.
- Head/eye/body response is in scope: small phrase-aware gaze/head follow, natural blinks and restrained breathing; avoid nodding or resetting the whole head on every fast note. Add these only after static character quality passes.
- The production whole-frame constraint remains: each delivered frame shows the complete connected cat/paws/instrument. Do not return to a body plate plus separate arm images or detached limb geometry.
