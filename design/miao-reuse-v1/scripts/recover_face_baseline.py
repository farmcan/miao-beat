"""Limited native face baseline restoration, retaining the failed hand pose."""
import hashlib
import json
import pathlib
import sys

import bpy
from mathutils import Vector

arguments = sys.argv[sys.argv.index('--') + 1:]
upstream = pathlib.Path(arguments[0]).resolve()
frozen = pathlib.Path(arguments[1]).resolve()
output = pathlib.Path(arguments[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(upstream), load_ui=False, use_scripts=False)
source_rig = bpy.data.objects['RIG-Cat']
control_names = ['FK-Head', 'Eye_Pupil.L', 'Eye_Pupil.R']
source_matrices = {name: source_rig.pose.bones[name].matrix_basis.copy() for name in control_names}
source_mouth = bool(source_rig.pose.bones['PRP-Head']['Sealed Mouth'])
source_quality = int(source_rig.pose.bones['Properties_Character_Cat']['Quality'])
assert source_mouth is False
bpy.ops.wm.open_mainfile(filepath=str(frozen), load_ui=False, use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']
receipt = {
    'scope': 'limited face baseline technical correction; hands/guitar remain failed and frozen',
    'upstream': str(upstream),
    'upstream_sha256': hashlib.sha256(upstream.read_bytes()).hexdigest(),
    'frozen_source': str(frozen),
    'frozen_sha256': hashlib.sha256(frozen.read_bytes()).hexdigest(),
    'mouth_before': bool(rig.pose.bones['PRP-Head']['Sealed Mouth']),
    'mouth_after': source_mouth,
    'quality_before': int(rig.pose.bones['Properties_Character_Cat']['Quality']),
    'quality_after': source_quality,
    'restored_native_controls': control_names,
    'upstream_scripts_executed': [],
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'frames': [],
}
for name in control_names:
    rig.pose.bones[name].matrix_basis = source_matrices[name]
rig.pose.bones['PRP-Head']['Sealed Mouth'] = source_mouth
rig.pose.bones['Properties_Character_Cat']['Quality'] = source_quality
helper = bpy.data.objects['HLP-scene_camera_dummy']
rotation_drivers = [curve for curve in helper.animation_data.drivers if curve.data_path == 'rotation_euler']
assert len(rotation_drivers) == 3
for curve in rotation_drivers:
    curve.mute = True
helper.rotation_mode = 'XYZ'
camera = scene.camera
camera.data.ortho_scale = 0.78
center = Vector((0.0, -0.045, 0.77))
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 96
for name, direction in [('face-baseline-front', (0.0, -4.0, 0.18)), ('face-baseline-three-quarter', (1.4, -4.0, 0.65))]:
    camera.location = center + Vector(direction).normalized() * 4.0
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    expected = camera.matrix_world.to_euler()
    helper.rotation_euler = expected
    helper.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    actual = helper.rotation_euler.copy()
    errors = [abs(expected[axis] - actual[axis]) for axis in range(3)]
    assert max(errors) < 1e-6, 'Camera helper local Euler sync failed'
    scene.render.filepath = str(output / f'{name}.png')
    bpy.ops.render.render(write_still=True)
    receipt['frames'].append({'name': name, 'output': scene.render.filepath, 'camera_world_euler': list(expected), 'helper_local_euler': list(actual), 'axis_errors': errors, 'max_error': max(errors)})
for text in bpy.data.texts:
    text.use_module = False
working = output / 'face-baseline-recovery-native36.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working), copy=True)
receipt['working_copy'] = str(working)
receipt['working_sha256'] = hashlib.sha256(working.read_bytes()).hexdigest()
receipt['upstream_sha256_after'] = hashlib.sha256(upstream.read_bytes()).hexdigest()
receipt['frozen_sha256_after'] = hashlib.sha256(frozen.read_bytes()).hexdigest()
assert receipt['upstream_sha256'] == receipt['upstream_sha256_after']
assert receipt['frozen_sha256'] == receipt['frozen_sha256_after']
(output / 'face-baseline-recovery-receipt.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps({'working': str(working), 'frames': receipt['frames'], 'mouth': source_mouth, 'quality': source_quality}))
