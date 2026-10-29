import hashlib
import json
import pathlib
import sys

import bpy

arguments = sys.argv[sys.argv.index('--') + 1:]
working = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(working), load_ui=False, use_scripts=False)
helper = bpy.data.objects['HLP-scene_camera_dummy']
patches = [curve for curve in helper.animation_data.drivers if curve.data_path == 'rotation_euler']
assert len(patches) == 3
assert all(curve.driver.is_simple_expression for curve in patches)
assert all(curve.driver.expression == 'camera_euler' for curve in patches)
assert all(not text.use_module for text in bpy.data.texts)
assert bpy.data.images['cat.base_color'].packed_file
assert list(bpy.data.images['cat.base_color'].size) == [4096, 4096]
bpy.context.view_layer.update()
rotation_error = max(abs(helper.rotation_euler[index] - bpy.context.scene.camera.rotation_euler[index]) for index in range(3))
print('ROTATION-DIAGNOSTIC', list(helper.rotation_euler), list(bpy.context.scene.camera.rotation_euler), helper.rotation_mode, helper.parent, [(curve.array_index, curve.driver.is_valid) for curve in patches])
rotation_matrix_error = helper.matrix_world.to_quaternion().rotation_difference(bpy.context.scene.camera.matrix_world.to_quaternion()).angle
print('ROTATION-MATRIX-ERROR', rotation_matrix_error)
report = {
    'working_copy': str(working),
    'working_sha256': hashlib.sha256(working.read_bytes()).hexdigest(),
    'blender_version': bpy.app.version_string,
    'reopened': True,
    'embedded_module_autoload': False,
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'simple_camera_rotation_drivers': len(patches),
    'camera_rotation_euler_max_error_radians': rotation_error,
    'camera_world_quaternion_angle_error_radians': rotation_matrix_error,
    'camera_driver_equivalence_pass': rotation_matrix_error < 1e-5,
    'packed_images': 1,
    'materials': len(bpy.data.materials),
}
output.write_text(json.dumps(report, indent=2))
print(json.dumps(report))
assert report['camera_driver_equivalence_pass'], 'Simple-driver semantic equivalence failed; do not mark compatibility fixed'
