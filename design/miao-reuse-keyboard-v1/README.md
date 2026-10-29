# Licensed keyboard reuse pilot

Keep the mature Wing It! Cat mesh/rig, Innerscene KeyForty keyboard, and COMMON280
table. Original assets and derived scenes live in `artifacts/`; they are excluded
from Git and delivered separately with licenses and hashes. Code is MIT; cat
assets are CC BY4.0, embedded upstream rig code separately GPL, keyboard/table
complete-file CC0. Do not infer model rights from this repository's code license.

Use official portable Blender **3.6.23**, `--background --factory-startup
--disable-autoexec --python-exit-code 1`. Never overwrite source packages with a
newer Blender save. No embedded Python is needed for the audited frozen scene.

The gray-supported and same-pose default-color stages passed three independent
static roles. That permits one controlled index-finger/key experiment only.
See [operation plan](../../docs/character-reuse-operation-plan-2026-10-30.md)
and the color identity/craft/motion reports under `docs/research/`.

Reference appearance: `public/character/whole-piano-v3/idle.jpg`. This licensed
stock pilot is visibly different from the original orange plush cat; no claim of
an exact reconstruction or finished product. Every production frame must show
the complete connected cat, both arms/paws, and the complete keyboard together.
Diagnostic hand crops are not separate arm assets.

The prototype `test_static_web_roundtrip.py` **fails visual transport acceptance**:
after reimport its eye colors and shadows differ. Do not publish its GLB or
replace the accepted native scene with it. The author smile-pose study also
failed (eye/nose artifacts) and remains isolated. Keep manual camera-helper
world-Euler synchronization before each render; the attempted SINGLE_PROP
driver binding did not reliably follow camera changes.

New input motion must pass finite pad/key/neighbor checks and independent actual
video review before expansion. Source static key geometry is not automatically
a complete mechanical keyboard rig. Eight-note operation, head response,
browser rendering and mobile experience require their own evidence.
