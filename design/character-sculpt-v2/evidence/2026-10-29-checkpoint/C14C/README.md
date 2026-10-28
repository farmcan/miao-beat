# C14C · head-only original-coat diagnostic

2026-10-29, local Blender 5.2.3 LTS. Builder `head_ear_builder`. This is a **head-only static material diagnostic** after the three independent C14 gray reviews cleared C12's horizontal beam / hidden nose-stem P0 regressions. Ear cavities and barrel side remain P1; the earlier whole-character paw/grip P0 is unchanged and blocks whole-character delivery or animation expansion.

Input is the frozen C14r1 native, SHA256 `6a61727939d1e9375d4e912685277cfb63bc4ca3427744c3c799461e824aab10`. C12/C14 sources, geometry, authored expression, coat, iris, cornea, linked optical lights/cards are untouched. Only native groom render visibility was restored. The original front camera and all existing light parameters stay unchanged; separate owned diagnostic camera copies match the established whole-3Q and 90mm head views. No GUI painting/polish, new shader, new light or geometry correction.

## Actual attachment checks before rendering

Reuse of pure `d0-groom-binding.py` helper functions is via AST extraction of named definitions only; importing that executable script directly would incorrectly run its rebind task. `receipt.json` records the exact upstream hash/functions. The existing groom uses the official `Deform Curves on Surface` node and body `BindUV`; there was no resnap, remesh, UV repair or rebinding.

- Official current-body UV lookup: **180000/180000 roots valid**, invalid 0.
- Evaluated roots to the **current corresponding UV surface**, independently sampled with Blender's official Sample UV Surface node: maximum `8.22618e-5u`, p95 `9.76225e-7u`.
- Evaluated roots to the current body **nearest surface**, all 180000 separately BVH-tested: maximum `7.43565e-5u`, p95 `1.78814e-7u`.
- Head region has **26928 roots**; corresponding-UV max `4.79695e-5u`, nearest-surface max `3.24961e-5u`.
- Raw and evaluated body/hair `miao_rest_position` hash-identical to original C8r2. Original body/hair raw positions and BindUV/root UV hashes also unchanged. Evaluated body and hair point coordinates are unchanged by this diagnostic.

These real static tests replace an assumption based on root counts. They validate this frozen shape's static attachment within the existing 1e-4u threshold. They do **not** prove deforming motion, eye closure, another topology, or future C15 resampling. Native and current positions have finite checked errors; no invalid roots were silently dropped.

## Evidence and scope

The script is `design/character-sculpt-v2/head-compact-color-check.py`, supporting --input/--out/--size/--samples. Use a new output directory to preserve this run. Render outputs: `color-front.png`, `color-three-quarter.png`, `color-head-front.png`, `color-head-three-quarter.png`; all are actual renders of the same complete 3D scene, not composited face/arm plates. The whole views include cat, paws and guitar; head views are internal material diagnostics. `miao-c14c-head-color.blend` is the restored-groom copy with original front camera.

No animation/Godot/web/audio/export/Cloudflare/API calls, paid services, commit or push. Three non-builder independent reviewers must judge the new actual color images against `public/character/instrument-scenes-v1/guitar/idle.jpg` and the C14 gray result. A local attachment pass or a prior B pass cannot approve all of Miao.

## Builder viewed actual color outputs — pending independent C review

Opened all four new actual color images and the original reference. Also reopened C8 whole-front and rendered/opened a **matched-camera C8 head-front control** (`control-c8-head-front.png`, separate receipt/script). This is one unchanged-coat probe plus one read-only baseline control, **zero corrective iterations**.

Observed: nose/stem/smile remain connected under fur; no C12-style horizontal beam appears in the color whole views or head 3Q. Rounded nose and embedded brows survive original shading. At these static views the eye whites show no conspicuous new fur penetration or widespread gray membrane. Both C14 and matched C8 head-front show horizontal dark bands inside the blue irises: therefore the band is **not newly introduced solely by C14**. This does not identify its optical cause or approve the original eye stack; no shader/cornea/card/light workaround was applied. New camera angles or motion could expose other optical failures.

The unchanged original coat is still rather saturated/flat in the whole views, hair reads as fine short prickles/grain rather than the source reference's more continuous plush, and the cream muzzle has a rectangular color boundary. These are visible comparison points for independent craft/identity review, not a newly solved material design. Colored ear cavities remain straight triangular grooves; head-side barrel P1 is not hidden or declared fixed by orange fur. Old unmerged paw geometry and grip P0 are unchanged. No shape or color was altered to cover these issues.

The complete native original-camera result is `miao-c14c-head-color.blend`. Source C14/C8 input SHA unchanged after all renders; body and groom evaluated coordinates, custom rest and binding UV verified unchanged. All existing light data/transform/visibility and original front camera data/transform compared equal after the probe. Three independent non-builder color reviews are still required; no motion expansion or full-character completion claim follows from this diagnostic.
