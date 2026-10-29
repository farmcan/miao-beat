"""C49 exact left-shoulder merge onto C47; partial art study, never a release."""
from pathlib import Path
import hashlib
import json
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/character-local-merge-c49'
OUT.mkdir(parents=True, exist_ok=True)
assert not (OUT / 'receipt.json').exists(), 'Preserve frozen output'
NAME = 'Miao / continuous pear and rounded-square face'
paths = {
    'shoulder': ROOT / 'artifacts/character-shoulder-c40/diagnostic-c40-left-shoulder-failed.blend',
    'base': ROOT / 'artifacts/character-integrated-gray-c31/miao-c31-head-hand-gray.blend',
    'head_eyes': ROOT / 'artifacts/character-eye-optical-c47/miao-c47-physical-optical-relight.blend',
}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def snapshot(mesh):
    p = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get('co', p)
    vi = np.empty(len(mesh.loops), np.int32)
    mesh.loops.foreach_get('vertex_index', vi)
    count = np.empty(len(mesh.polygons), np.int32)
    mesh.polygons.foreach_get('loop_total', count)
    return p.reshape(-1, 3), hashlib.sha256(vi.tobytes() + count.tobytes()).hexdigest()

loaded = {}
source_hashes = {k: sha(p) for k, p in paths.items()}
for tag in ['base', 'shoulder', 'head_eyes']:
    bpy.ops.wm.open_mainfile(filepath=str(paths[tag]))
    loaded[tag] = snapshot(bpy.data.objects[NAME].data)
base, topology = loaded['base']
shoulder, shoulder_topology = loaded['shoulder']
current, current_topology = loaded['head_eyes']
assert topology == shoulder_topology == current_topology
changed = np.any(base != shoulder, axis=1)
assert changed.sum() == 22074
report = {'status': 'partial-static-branch-integration-not-art-or-animation-acceptance',
          'sources': {k: {'path': str(p.relative_to(ROOT)), 'sha256': source_hashes[k]} for k, p in paths.items()},
          'shoulder_changed_points': int(changed.sum()),
          'topology_exact': True, 'premerge_shoulders_match_base_exact': bool(np.array_equal(current[changed], base[changed])),
          'whole_character_approved': False, 'production_changed': False, 'skin_bound': False}
(OUT / 'preflight.json').write_text(json.dumps(report, indent=2) + '\n')
assert report['premerge_shoulders_match_base_exact'], 'Conflicting branch deformation: do not guess or nearest-match'
merged = current.copy()
merged[changed] = shoulder[changed]
mesh = bpy.data.objects[NAME].data
before_other = {o.name: list(map(list, o.matrix_world)) for o in bpy.context.scene.objects if o.name != NAME}
mesh.vertices.foreach_set('co', merged.ravel())
mesh.update()
bpy.context.view_layer.update()
actual, actual_topology = snapshot(mesh)
assert np.array_equal(actual[changed], shoulder[changed]) and np.array_equal(actual[~changed], current[~changed])
assert actual_topology == topology
assert all(list(map(list, bpy.data.objects[n].matrix_world)) == m for n, m in before_other.items())
report['shoulder_coordinates_exact'] = True
report['head_paws_and_all_other_body_points_exact'] = True
report['all_other_object_world_transforms_exact'] = True
report['C44_scope'] = '20 previously ambiguous sample normals cleared by actual-triangle solid angles; not a global art gate'
report['limits'] = ['Right arm/ears/plush remain P0; this integration is not a production character.',
                    'Groom remains hidden pending new skin binding.', 'No new animation, GLB, browser or release created.']
scene = bpy.context.scene
scene.cycles.samples = 64
scene.cycles.seed = 17
scene.cycles.use_animated_seed = False
scene.render.resolution_x = scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.use_border = False
bpy.context.preferences.filepaths.save_version = 0
native = OUT / 'miao-c49-local-merge.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
report['native_sha256'] = sha(native)
report['renders'] = []
cam = scene.camera
loc, rot, scale = cam.location.copy(), cam.rotation_euler.copy(), cam.data.ortho_scale
for view in ['full', 'face', 'three-quarter']:
    if view == 'full':
        cam.location, cam.rotation_euler, cam.data.ortho_scale = loc, rot, scale
    else:
        cam.location = Vector((0, -6, 3.05)) if view == 'face' else Vector((-6, -9, 3.9))
        target = Vector((0, 0, 3.03)) if view == 'face' else Vector((.09881, 0, 1.609))
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cam.data.ortho_scale = 1.7 if view == 'face' else scale
    bpy.context.view_layer.update()
    file = OUT / ('c49-' + view + '.png')
    scene.render.filepath = str(file)
    bpy.ops.render.render(write_still=True)
    report['renders'].append({'file': file.name, 'sha256': sha(file), 'camera_matrix': list(map(list, cam.matrix_world))})
assert all(sha(p) == source_hashes[k] for k, p in paths.items())
(OUT / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'sources'}), flush=True)
