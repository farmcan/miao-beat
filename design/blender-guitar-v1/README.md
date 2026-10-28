# Blender guitar first study

`scene.py` is an original procedural 3D scene draft, not an accepted production character. All meshes, curves and materials in this script are authored here. No reference asset below is imported by the script. The fixed camera renders the complete cat, both connected arms/paws, instrument and studio in every frame.

```sh
blender --background --python design/blender-guitar-v1/scene.py -- \
  --output artifacts/blender-guitar-v1 --size 640 --samples 32 --still
```

Use `--frame 2` for the nominal contact frame or `--all` for the 24-frame sequence at 60fps. `miao-guitar-v1.blend` preserves scene, editable materials and animation. Native render and contact/rig audits are complete as recorded below; subjective naturalness still requires user review. Geometry or a saved .blend alone is not proof of natural motion.

## Reuse investigation · 2026-10-28

| Candidate | Primary source and license evidence | Fit and actual limit |
|---|---|---|
| Blender Studio Cat from *Wing It!* | [Official Cat rig](https://studio.blender.org/characters/cat/v1/), CC-BY 4.0 with required credit “Cat Rig (CC-BY) Blender Foundation / studio.blender.org”. | Highest production-quality rig candidate. Official instructions explicitly require **exactly Blender 3.6**, warn other versions may break, and download requires a Blender ID login. Not downloaded, adapted or tested with the new environment. |
| Tomcat94 Cat Pilot | [Author's OpenGameArt upload](https://opengameart.org/node/95204), CC0, original .blend plus diffuse map and author preview available directly. | Actual downloaded preview is an older low-poly grey pilot cat, helmet/goggles/scarf and large monochrome eyes. Rig/eyelid shape keys may be useful for inspection; appearance does not match Miao and was not accepted as replacement. Download hashes are in `reference-assets/provenance.json`. |
| JonasDichelle Rigged and animated Cat | [Author's BlendSwap upload](https://blendswap.com/blend/18519), CC-BY, Blender 2.7x Cycles, 22.8MB. | Author describes full rig, walk/run and dynamic hair. Mature quadruped/old particle-hair system would need migration and substantial posing/redesign for a standing musician. File not downloaded or tested. |
| Marchen Stripe the Cat | [Author's BlendSwap upload](https://blendswap.com/blend/21698), CC-BY, 1,034 faces, no textures, walk/run and blinking. | Useful small rig reference, insufficient visual detail for the current request. Not used. |
| SSimpossible Acoustic Guitar | [Author's BlendSwap upload](https://blendswap.com/blend/2561), CC0, Blender 2.5x, 420KB. | Author explicitly says untextured. Older static mesh does not directly improve a detailed classical-guitar scene; not used. |

Reuse must improve the result. Public download counts and render previews are not evidence that a rig imports, contacts strings, or renders correctly in this environment. Do not replace the orange plush identity with an unrelated low-poly pilot solely to claim reuse.

## Motion acceptance

The first draft used an empty shoulder rotation and must not be shipped as proof of contact. Verify the actual paw surface relative to six string center lines and soundboard plane; the moving paw must approach strings, pass across their width once and lift away before return. Keep shoulder attached and the fretting paw/camera/body stationary. No browser limb compositing, no opacity crossfade, and no reversed recovery through the strings.

## Executed first version

The first version was actually rendered with **Blender 5.2.3 LTS**, build `e13b728c6880`, Cycles with Metal, **640×640 / 32 samples / 60fps / 24 frames**. The native editable scene is `miao-guitar-v1.blend` (relative render path `//renders/frame-###.png`). Reproduce using:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python design/blender-guitar-v1/scene.py -- \
  --output artifacts/blender-guitar-v1/reproduced --size 640 --samples 32 --all
```

Blender on another platform can use `blender` in place of the macOS absolute executable. `--device CPU` requests a CPU render when Metal is unavailable; `--no-render` rebuilds/saves the scene and its audits without rendering. The script automatically tries Metal when available and otherwise keeps the default CPU device. GPU first-use kernel compilation can take longer than the subsequent per-frame renders.

The 24 source PNGs and a 0.4-second native-speed `cycle.mp4` are local artifacts in `artifacts/blender-guitar-v1/final-r3/`. Public test-page packing is a separate reviewed step. Every source frame contains the **entire** cat, connected arms/paws and guitar; the website does not assemble limb layers.

### Motion and measurable boundaries

The picking shoulder stays fixed. An analytic two-bone IK with a stable outward pole solves the elbow for the whole-paw target; upper/forearm center lengths are 0.58 / 0.70 scene units. `rig-audit.json` records all 24 actual evaluated joint positions, with length errors below `1.6e-7`. A connected thick curve follows the three joint centers rather than stretching a disconnected arm image.

The paw descends across the strings once, then retracts toward the viewer before lifting to prepare. Frame 2 is the first nominal contact, frames 2–5 form one continuous light-contact window, and frame 6 has cleared the strings. `contact-audit.json` analytically samples the evaluated ellipsoid paw surface at the six string center lines. The smallest signed string gap is `-0.005759`; negative values are a bounded plush/string overlap, **not a full physical collision simulation**. The conservative paw-to-soundboard plane clearance stays at least `+0.039`. This audit does not certify all character-body intersections or physically correct nylon dynamics.

The camera, body and fretting hand are fixed in this first test. The fretting palm was flattened and moved behind the neck, with short curled toe shapes crossing its near edge so the fretboard remains readable. Finger-level fingering and a distinct chord grip per note are not implemented by this scene.

Frames 0 and 23 have the same evaluated pose, and Cycles uses fixed seed 17 with animated seed disabled. GPU/denoiser output still differs in a few RGB channels by at most one 8-bit level (mean channel error below 0.00004). `render-receipt.json` preserves this fact and source-frame SHA-256 hashes. A web atlas may reuse complete source frame 0 for the final closed-loop endpoint, but that normalization must be recorded; do not claim bitwise determinism of the raw GPU render.

### Iteration record

- Initial preview failed: reading an unevaluated parent matrix reset the picking-paw scale, producing an oversized sphere that obscured the guitar. Fixed by updating the view layer before preserving the parent transform. This failed preview was not promoted.
- The next preview exposed raised clay-like forehead/cheek stripes, thick eye spheres, a pale orange material and elevated shoulders. Surface-following thin stripe inlays, thinner eyes, a downward gaze, stronger orange, neutral lights and lower shoulders replaced those features.
- An early shoulder-rotation draft did not establish real surface contact. It was replaced by paw-target trajectories and explicit surface-gap auditing; an intermediate frame 3 had excessive string penetration and was rejected.
- An early proportional elbow follow stretched the apparent limb. The final scene uses constant-length two-bone IK and a continuous retract/lift return, rather than reversing a rendered stroke through the strings.

This is a **first motion-testing character**, with a crafted toy appearance. It is not the final plush-fur model, does not replace the current production cat by itself, and visual naturalness remains subject to the user's test-page review. Extra samples would reduce render noise, not fix a poor silhouette, inaccurate grip or bad timing.
