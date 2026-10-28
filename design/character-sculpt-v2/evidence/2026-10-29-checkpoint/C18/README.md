# C18 D · reflection / refraction closure contrast

2026-10-29; local Blender 5.2.3 LTS, build `e13b728c6880`. **One new diagnostic setting, not a production material correction.** C17 A/B/C remain frozen. No animation, fees, Cloudflare request, commit or push.

## Why not just set Specular IOR Level to zero?

Checked the actual current shader and official Cycles source at the local build commit. C14C cornea has white base color, transmission 1, metallic/coat/sheen/emission 0, alpha 1, IOR 1.38, roughness .035 and multi-GGX distribution; its Normal input is unlinked. In the implementation, transmission builds a combined glass closure before the separate specular layer; the remaining layer weight is then multiplied by `(1 - transmission_weight)`. Specular IOR Level controls the later layer and therefore is not a dependable switch for the reflected part of fully transmissive glass.

Sources checked:

- [Exact-build Cycles closure implementation](https://github.com/blender/blender/blob/e13b728c6880/intern/cycles/kernel/svm/closure.h#L333): transmission setup around lines 333–390, separate specular adjustment around 391–432, refraction-only closure around 676–711.
- [Exact-build Refraction BSDF node definition](https://github.com/blender/blender/blob/e13b728c6880/source/blender/nodes/shader/nodes/node_shader_bsdf_refraction.cc#L9): available color/roughness/IOR/normal inputs and transmissive shader.
- [Official Principled documentation](https://docs.staging.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html): high-level IOR/specular controls. The specific pure-transmission implementation takes priority over interpreting the short UI phrase as a universal glass reflection switch.

The English manual Refraction page fetch returned a tool-side 402; no payment or alternative paid request was made. Exact-build official source was readable and used instead. Source was read for semantics only; no upstream implementation code was copied into this experiment.

## D: same refracting interfaces, one changed material output

Input remains `artifacts/character-head-c14-color/miao-c14c-head-color.blend`, SHA256 `9948a6eaa4c0001c6f511e86d4b98fcd0fc15a0928f8399c7e8a1f73f198a3a9`.

Only the shared cornea material's Surface output is rerouted from its original Principled to a new **GGX Refraction BSDF** with the same nominal IOR 1.38, roughness .035, white color and unlinked Normal. Corneas stay visible; geometry, both physical interfaces, camera, lights, linked receiver sets, iris material and all other materials remain unchanged. Original Principled stays disconnected in memory for audit; source native is never saved over.

This removes the reflected closure, but it also replaces Principled's combined Fresnel energy split and multiple-scattering compensation with single-scattering GGX refraction. Transmission energy and sampling can change. **It is a bounded material-closure contrast, not an exact one-physical-factor ablation.** The nominal IOR and surfaces retain refraction, unlike C17 B (IOR 1) or C (hidden cornea).

Only two new actual renders were made: `D-refraction-only-whole.png` and `D-refraction-only-head.png`. Same original whole camera / C17 90mm head camera, 1024×1024, Cycles 32 samples, seed 17. C17 A baseline images are reused after SHA verification; no baseline overwrite or parameter sweep. Raw geometry hashes, light/receiver snapshots, non-cornea material socket snapshots, exact camera matrices and source/output SHA are retained in `receipt.json`.

## Interpretation boundary

Both actual D renders and the C17 controls were opened. D loses the visible horizontal dark/cloudy band and bright catchlights while retaining the nominal-IOR-1.38 refracting shell; the blue iris remains a smooth, flat radial ring. This supports a contribution from the removed reflected/Fresnel part of the combined model. It does not prove a specific lamp, environment boundary, normal feature, double-interface interaction or sole root cause, and transmission-energy / multi-GGX coupling remains. Observations are saved in `builder-inspection.json`. D is not a satisfactory wet-eye art fix. A separately scoped correction and three independent color reviews are still required; flat, lifeless eyes are not accepted merely because a band disappears.

## Reproduce

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python design/character-sculpt-v2/eye-reflection-diagnostic.py -- --out artifacts/character-eye-optics-c18-recheck
```

Use a fresh output directory. The script imports only named ordinary helper definitions from the main-guarded C17 script; both source hashes are recorded. It does not execute C17's render loop.
