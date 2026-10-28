# C17 · isolate the blue-eye horizontal band

2026-10-29; Blender 5.2.3 LTS, local only, no new cash cost. **Optical diagnosis, not an accepted replacement eye or a completed character.** This builder is not an independent judge.

## Frozen source and bounded cases

Input: `artifacts/character-head-c14-color/miao-c14c-head-color.blend`, SHA256 `9948a6eaa4c0001c6f511e86d4b98fcd0fc15a0928f8399c7e8a1f73f198a3a9`. The script reopens this exact native before each case; it never saves over the native. The original full-body orthographic camera and the established C14C 90mm head-front camera are reused. Both views render at 1024×1024, Cycles 32 samples, seed 17.

| Case | Sole changed setting | Output |
| --- | --- | --- |
| A-original | none; cornea IOR 1.38, visible | `A-original-whole.png`, `A-original-head.png` |
| B-ior-one | the shared cornea Principled IOR is 1.0 | `B-ior-one-whole.png`, `B-ior-one-head.png` |
| C-cornea-hidden | both cornea objects `hide_render=True`; original IOR retained | `C-cornea-hidden-whole.png`, `C-cornea-hidden-head.png` |

Hiding the corneas is **only a diagnostic control**, not a delivery workaround. The whole views remain actual complete-cat/paws/guitar renders, not body plates and separate hand images. Head views are internal optics crops taken with the same actual camera, not edited artwork.

The execution receipt records native/reference/source/output SHA, exact cameras, runtime settings and timings. Each reload checks all raw mesh coordinates/transforms and every light (including receiver-collection assignments) against A. All material socket defaults must remain identical except the single explicitly allowed cornea IOR change. Native/reference SHA are checked again at completion. This does not assert unchanged unseen future poses or real-time engine equivalence.

## What the actual renders establish

All six rendered images were opened. A retains the horizontal blue/dark layering and optical catchlights. B (IOR 1) and C (cornea hidden) both remove the visible horizontal layering, but also remove the wet bright catchlights and leave flat dark-blue radial irises. This localizes the observed band to a contribution of the current non-unit-IOR cornea optical stack under these cameras; it is not adequately explained by the unchanged diffuse radial iris tone alone. Builder observations and unproved boundaries are recorded in `builder-inspection.json`. A/B/C are the complete planned set; there is no fourth corrective candidate in this run.

Changing IOR affects reflection and refraction together. If B and C remove the band, this identifies a contribution of the current cornea optical stack; it does **not** uniquely prove refraction, reflection of the environment, surface-normal error, or a specific light is the sole cause. The diffuse iris source uses radial tones with small angular grain; that code reading alone would not prove a rendered cause.

Flat unhighlighted iris controls are not a satisfactory art fix. Any follow-up must preserve the expressive sideward gaze and recover believable wet-eye highlights without restoring the objectionable band, then receive three independent color reviews. Geometry/eyelid-envelope changes require the gray gate again. No blink, rig, paw contact, animation, browser interaction, video export or production acceptance follows from this diagnostic.

## Reproduce

Use a fresh output directory; the script refuses to overwrite an existing receipt.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/eye-optics-diagnostic.py -- --out artifacts/character-eye-optics-c17-recheck
```

Original local script; no new external asset or dependency. No paid API, Cloudflare request, web deployment, commit or push.
