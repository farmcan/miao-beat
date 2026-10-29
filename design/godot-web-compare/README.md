# Genuine Godot Web comparison

This is the Godot renderer in the playable original / Three.js / Godot comparison. It uses Godot **4.7.2**, Compatibility, single-thread Web export. The C20 research model has not passed the character art quality gate.

## Reproduce

The installed official export template is `web_nothreads_release.zip` under Godot's `4.7.2.stable` export template folder. Template provenance and the exact selected-member check are recorded locally in `artifacts/godot-web-setup/template-install-receipt.json`. The full 1.28 GB TPZ was not downloaded or SHA512 verified; the selected ZIP member was obtained from the official release over HTTPS, with its central-directory size and CRC verified.

From the repository root:

```sh
mkdir -p design/godot-web-compare/model
cp public/labs/character-compare/model/miao-playable.glb design/godot-web-compare/model/miao-playable.glb
/Applications/Godot.app/Contents/MacOS/Godot --headless --editor --path design/godot-web-compare --quit
/Applications/Godot.app/Contents/MacOS/Godot --headless --path design/godot-web-compare --export-release Web
python3 design/godot-web-compare/prepare_web.py
```

Expected source GLB SHA256: `1a384c0a9a13ed60710469b7d9a4de646a8599fe3dcff5ef85d1f42c825cedf9` (7,483,568 bytes). The duplicate imported GLB and `.godot/` are ignored. The canonical GLB remains in the public comparison model directory.

`prepare_web.py` must run after every export: Godot overwrites the HTML and recreates the raw 39.5 MB engine WASM. The postprocess makes an exact gzip copy, verifies the roundtrip, retains raw WASM in local artifacts, and publishes only the compressed 10.1 MB file. The iframe's `compressed-wasm.js` intercepts only its own `index.wasm` request, decompresses the official binary in the browser, and returns an `application/wasm` response. It does not substitute a renderer or require Worker/header changes. Modern `DecompressionStream` support is required.

## Parent interface

```js
iframe.contentWindow.miaoGodotPose(pluck, fretLow, fretHigh, headTilt, lift);
iframe.contentWindow.miaoGodotView('whole'); // 'hands' or 'face'
iframe.contentWindow.miaoGodotOrbit(20); // degrees, -35..35
```

Pose order is `[Pluck,FretLow,FretHigh,HeadTilt,Lift]`, shared by all 20 morph meshes. Pluck accepts -1..1; the remaining weights accept 0..1. The parent supplies every frame's weights and owns input/audio/timing. This iframe has no music playback or independent stroke schedule.

The page sets `window.miaoGodotReady=true` and posts `{type:'miao-godot-ready'}` to `location.origin`. The parent must validate the message origin and source iframe. DOM diagnostics: `body[data-miao-godot-ready=true][data-miao-morph-meshes="20"]`.

## Verified on 2026-10-29

- Native API retains `Pluck=-0.5`; the Web engine repeats the same assertion.
- Real IAB canvas rendered the complete cat/guitar; console identifies Godot 4.7.2, WebGL2 Compatibility, single-thread mode and `web:true`.
- Through the actual comparison-page buttons, slow demonstration counted 8 inputs, Godot remained ready, and the shared hands view changed the actual Godot camera. Godot produced no console warnings/errors. Motion quality and physical mobile performance are not signed off by this technical check.
- No hair system was exported. Contact shadows are disabled pending renderer-specific tuning. Coat response is a Compatibility shader approximation using the model's vertex colors, original roughness/metallic, and opaque cornea clearcoat. These are visible fidelity gaps.

Runtime license: Godot MIT plus third-party notices, distributed in `GODOT-LICENSE.txt` and `GODOT-COPYRIGHT.txt`. No upstream demo model/audio/code is embedded in this renderer.
