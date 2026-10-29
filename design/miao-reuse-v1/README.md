# Miao reuse v1 · local static compatibility experiment

This stage reuses Blender Studio's mature Wing It! Cat geometry, rig and received colors. It does not build a new cat, remove its outfit, expand animation, or publish production assets.

## Fixed upstream asset

- Original author page: https://studio.blender.org/characters/cat/v1/
- Credit: Cat Rig (CC-BY) Blender Foundation | studio.blender.org
- Asset license: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
- Licensed redistribution: https://github.com/move-ai/Move_API_and_retargeting_Blender_addon/blob/f449af53ccc71a7c66079b7a52e133a163a41fb7/data/rigs/wingit_cat.blend
- Required source SHA256: `42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1`
- Source path: `artifacts/upstream-cat-candidates/scout-a/wingit_cat.blend`
- MoveAI's changes: optimization, including simplified Principled/Emission materials. This working render cannot assert original movie toon shader fidelity. No MoveAI addon is used.

## Portable author-supported runtime

Existing user installation `/Applications/Blender.app` remains Blender 5.2.3 and is not replaced.

- Version: official Blender 3.6.23, macOS arm64, build `e467db79ca8c`.
- Index: https://download.blender.org/release/Blender3.6/
- Runtime DMG: https://download.blender.org/release/Blender3.6/blender-3.6.23-macos-arm64.dmg
- Official hashes: https://download.blender.org/release/Blender3.6/blender-3.6.23.sha256
- Verified DMG SHA256: `ecbeaef4abbeb045de8465e78b3f97aec9b67faf2fc71b20e5eca37bf1caf874`
- Portable binary: `artifacts/runtime/blender-3.6.23/Blender.app/Contents/MacOS/Blender`
- Download and checksum receipt: `artifacts/runtime/blender-3.6.23-runtime-receipt.json`.
- The DMG is verified before mounting read-only; the app is copied to the project runtime directory with `ditto`, never installed into `/Applications`. No user preferences are saved. Runtime licenses remain inside the app; GPL and copyright copies are also under the compatibility evidence folder.

On another platform, obtain Blender 3.6.23 for that platform from the same official index and verify against the matching line of the official `.sha256`; do not use the arm64 checksum for other packages. The rendering Python uses portable bpy/mathutils/pathlib APIs.

## Reproduce the actual colored static render

Run from the repository root after obtaining and verifying the fixed source asset and runtime:

```sh
artifacts/runtime/blender-3.6.23/Blender.app/Contents/MacOS/Blender \
  -b --factory-startup --disable-autoexec --python-exit-code 1 \
  -P design/miao-reuse-v1/scripts/render_native_color.py -- \
  artifacts/upstream-cat-candidates/scout-a/wingit_cat.blend \
  artifacts/miao-reuse-v1/compat
```

Outputs:

- `wingit-received-materials-color.png`: complete cat in the source rest pose, with the materials/colors/texture received from the licensed redistribution.
- `wingit-working-native36.blend`: separate local working scene, with the original cat, received materials, temporary inspection camera/lights/world and limited compatibility patch.
- `native-color-receipt.json`: version, source/working-copy SHA, exact limited changes and provenance boundary.

## Execution and modification boundary

`extract_upstream_texts.py` extracts native scripts without executing them and lists imports/calls. `inspect_native_shading.py` records material topology and lighting properties. Static findings are documented in `artifacts/miao-reuse-v1/compat/EMBEDDED-CODE-REVIEW.md`.

No upstream Python module executes. All autoexecution stays disabled. CloudRig UI's eval paths, registration, rig generation and UV repair helpers remain unused. For the three exactly matched `HLP-scene_camera_dummy.rotation_euler` expressions, the working copy uses a simple named transform driver referencing the actual inspection camera's world-space XYZ Euler. Other drivers are preserved. Embedded text module autoload flags are disabled in the new working copy. Source bytes are checked before and after rendering.

The only scene additions are inspection camera, area lights and background world. Geometry, hand/finger topology, rig pose and received materials are unchanged. There are no added keyframes, new animation clips, recoloring, outfit removal or guitar assembly in this stage.

This is a compatibility/static experiment awaiting the project review gates; it is not final character approval or animation acceptance.

## Superseding failure notice

The static hold/color experiment is now **FAIL and frozen**, not an accepted implementation. See `docs/research/miao-reuse-static-hold-builder-2026-10-29.md` and `artifacts/miao-reuse-v1/static-hold/inspection-manifest.json`. Mouth disappearance, an eye triangle, invalid hand contact and guitar proportions block delivery and animation. The simple camera-driver replacement also failed semantic equivalence on read-only reopening (world rotation difference 1.08858 radians) despite valid/simple driver flags; do not call it a completed compatibility fix. Official portable runtime/download and safe asset-read/color-render evidence remain valid. These are integration defects, not grounds to reject the mature licensed source model.

### Limited face-baseline correction after failure freeze

The failed hold scenes and images remain frozen. A separate authorized technical recovery restores upstream face control matrices, SealedMouth=False and source Quality=1, then mutes the three non-equivalent camera rotation drivers and assigns `camera.matrix_world.to_euler()` to the helper's local Euler before each render. Both two-angle face images recover a readable native mouth with no eye triangle, and every axis error is zero. Use `scripts/recover_face_baseline.py` and the receipt under `artifacts/miao-reuse-v1/face-baseline-recovery/`; this is a supported static fallback, not a functioning general camera driver or animation claim. Hand contact/proportions remain failed and awaiting a measured plan and independent review.
