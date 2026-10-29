# Miao reuse v1 · current reproducible baseline and frozen contact study

The source-only original-color rest baseline is verified. Guitar-contact adaptation remains **FAIL**, frozen for independent review. No animation or product publication is authorized by these results.

## Current recommended source-only render

Use `scripts/render_source_rest_baseline.py`. It reads the immutable upstream file directly, preserves source Quality=1, head/pupil/mouth, the complete rest pose, received materials and geometry. It does not require a failed hold derivative.

From the repository root:

```sh
artifacts/runtime/blender-3.6.23/Blender.app/Contents/MacOS/Blender \
  -b --factory-startup --disable-autoexec --python-exit-code 1 \
  -P design/miao-reuse-v1/scripts/render_source_rest_baseline.py -- \
  artifacts/upstream-cat-candidates/scout-a/wingit_cat.blend \
  artifacts/miao-reuse-v1/source-rest-baseline
```

Actual outputs: `source-rest-original-three-quarter.png`, `source-rest-native36.blend`, `source-rest-baseline-receipt.json`. Source pose hash before/after is identical; camera helper local Euler is synchronized from the source formula's camera WORLD Euler before rendering and all three axis errors were zero. The original asset is unchanged.

The self-contained `source-pack/`, archived at `artifacts/miao-reuse-v1/handoff/miao-reuse-source-rest-pack.zip`, includes the exact source asset, the same script, license/provenance and official runtime hashes. It was actually run from its copied script with default relative paths. Unpack it elsewhere, supply official Blender 3.6, and run:

```sh
/path/to/blender-3.6 --background --factory-startup --disable-autoexec \
  --python-exit-code 1 --python scripts/render_source_rest_baseline.py
```

Default paths resolve from the script location. No failed scene, owner filesystem path, account, MoveAI addon or external Python library is required. The runtime is intentionally not inside the source pack; use the official package for the destination operating system.

## Immutable upstream and separate licenses

- Cat original: https://studio.blender.org/characters/cat/v1/
- Credit: Cat Rig (CC-BY) Blender Foundation | studio.blender.org
- Asset license: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
- Licensed redistribution: https://github.com/move-ai/Move_API_and_retargeting_Blender_addon/blob/f449af53ccc71a7c66079b7a52e133a163a41fb7/data/rigs/wingit_cat.blend
- Source SHA256: `42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1`.
- The received materials are optimized Principled/Emission with packed texture, not proof of original film toon shader fidelity.
- Embedded CloudRig code is retained unchanged and never executed. Its current official extension is separately GPL-3.0-or-later; source pack notices and GPL text retain that boundary. No MoveAI addon is installed or run.

Official runtime index: https://download.blender.org/release/Blender3.6/ ; hashes: https://download.blender.org/release/Blender3.6/blender-3.6.23.sha256 . Actual tested runtime is macOS arm64 Blender 3.6.23 build `e467db79ca8c`, DMG SHA256 `ecbeaef4abbeb045de8465e78b3f97aec9b67faf2fc71b20e5eca37bf1caf874`. It is portable under `artifacts/runtime/blender-3.6.23/`; the user's `/Applications/Blender.app` 5.2.3 was not replaced. Verify the corresponding official hash for other operating systems.

## Historical error and bounded face recovery

`render_native_color.py` is historical evidence of a rejected camera TRANSFORMS-driver replacement. Its simple/valid flags did not establish equivalence: helper local Euler differed from the original expression by up to1.08804 radians. Do not recommend or run it for fresh renders.

The supported static fallback mutes only the three reviewed camera rotation expressions, then explicitly assigns `camera.matrix_world.to_euler()` into helper local XYZ Euler before every still and asserts each axis error<1e-6. Autoexecution stays disabled, upstream Python does not run, and derivative text autoload flags are off.

A separate limited recovery restored source SealedMouth=False and exact source head/pupil/Quality controls. Two angles recovered readable original mouth and removed the eye triangle. See `docs/research/miao-reuse-face-baseline-recovery-2026-10-29.md`. This technical recovery did not pass guitar contact or final art.

## Contact study remains FAIL and frozen

The first one-pose-plus-repair/color trial is retained under `artifacts/miao-reuse-v1/static-hold/` with its three-role failure and builder diagnosis. A later evidence-led single enlarged-guitar/real-hand-frame proposal was actually placed through calibrated ORG-Hand↔IK-MSTR-Hand mapping, not copied blind into the master controller. Actual arm reach was91.4556%/97.07645%, with original segment lengths preserved.

`check_contact_candidate.py` initially exposed an invalid empty wrist selection: DEF-Hand's maximum weight is only .448, and real palm/wrist support also comes from Carpal/Sleeve/Forearm. The empty-set clear label was withdrawn and preserved as invalid historical evidence. Corrected nonzero skin selection and the final fixed-support-weight check reject this candidate.

`solve_keypads_diagnostic.py` ran only three actual continuous-skin triangle pad targets with1° finite difference, ≤5° steps, ≤15updates/pad and3 no-improvement stop. Left index improved to.0155mm target error; left proximal thumb remained14.747mm after the limit; right thumb was.128mm from the requested hover target. Final fixed palm/wrist skin still enters the guitar, including86 right-side fixed-support vertices and up to42.50mm envelope depth. These are rejection measurements, not a complete collision acceptance method.

The sole current diagnostic full-frame image is `artifacts/miao-reuse-v1/contact-correction/diagnostic-front-FAIL-NOT-ACCEPTED.png`, visibly marked TECHNICAL STUDY / NOT ACCEPTED. Native, numeric trace and exact hashes are in that folder's `inspection-manifest.json`. No additional pose, palette or animation search continues. Independent reviewers decide next steps; integration failures are not a reason to discard the professional source geometry or start another bespoke cat.
