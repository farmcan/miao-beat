"""Portable source-only rest baseline; no failed-hold or host-specific input."""
import hashlib
import json
import pathlib
import sys

import bpy
from mathutils import Vector

script_root = pathlib.Path(__file__).resolve().parents[1]
arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
source = pathlib.Path(arguments[0]).resolve() if arguments else script_root / 'source' / 'wingit_cat.blend'
output = pathlib.Path(arguments[1]).resolve() if len(arguments) > 1 else script_root / 'output' / 'source-rest-baseline'
output.mkdir(parents=True, exist_ok=True)
expected_sha = '42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1'
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_sha
assert bpy.app.version[:2] == (3, 6), 'Author-supported Blender 3.6 required'
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']


def pose_signature():
    values = [(bone.name, [list(row) for row in bone.matrix_basis]) for bone in rig.pose.bones]
    return hashlib.sha256(json.dumps(values).encode()).hexdigest()


pose_before = pose_signature()
quality = int(rig.pose.bones['Properties_Character_Cat']['Quality'])
mouth = bool(rig.pose.bones['PRP-Head']['Sealed Mouth'])
assert quality == 1 and mouth is False
visible = [obj for obj in scene.objects if obj.type == 'MESH' and obj.visible_get() and not obj.hide_render and not obj.name.startswith('WGT')]
points = [obj.matrix_world @ Vector(corner) for obj in visible for corner in obj.bound_box]
lower = Vector([min(point[axis] for point in points) for axis in range(3)])
upper = Vector([max(point[axis] for point in points) for axis in range(3)])
center = (lower + upper) / 2.0
camera_data = bpy.data.cameras.new('SOURCE-REST-INSPECTION-CAMERA')
camera = bpy.data.objects.new('SOURCE-REST-INSPECTION-CAMERA', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.lens = 65.0
camera_data.ortho_scale = max(upper - lower) * 1.25
camera.location = center + Vector((1.45, -4.0, 0.58)).normalized() * 4.0
camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
helper = bpy.data.objects['HLP-scene_camera_dummy']
rotation_drivers = [curve for curve in helper.animation_data.drivers if curve.data_path == 'rotation_euler']
assert len(rotation_drivers) == 3
for curve in rotation_drivers:
    assert curve.driver.expression == f'depsgraph.scene.camera.matrix_world.to_euler()[{curve.array_index}]'
    curve.mute = True
helper.rotation_mode = 'XYZ'
world = bpy.data.worlds.new('SOURCE-REST-INSPECTION-WORLD')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
scene.world = world


def add_area(name, position, energy, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = position
    light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()


add_area('SOURCE-REST-KEY', (-2.0, -3.0, 3.5), 350.0, 3.0)
add_area('SOURCE-REST-FILL', (2.5, -2.0, 1.6), 140.0, 3.0)
add_area('SOURCE-REST-RIM', (0.8, 2.0, 3.0), 250.0, 2.0)
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 96
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 0.12
scene.eevee.gtao_factor = 1.1
bpy.context.view_layer.update()
expected_euler = camera.matrix_world.to_euler()
helper.rotation_euler = expected_euler
helper.update_tag(refresh={'OBJECT'})
bpy.context.view_layer.update()
errors = [abs(helper.rotation_euler[axis] - expected_euler[axis]) for axis in range(3)]
assert max(errors) < 1e-6
assert pose_signature() == pose_before
scene.render.filepath = str(output / 'source-rest-original-three-quarter.png')
bpy.ops.render.render(write_still=True)
for text in bpy.data.texts:
    text.use_module = False
working = output / 'source-rest-native36.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working), copy=True)
receipt = {
    'source': str(source),
    'source_sha256': expected_sha,
    'source_sha256_after': hashlib.sha256(source.read_bytes()).hexdigest(),
    'blender_version': bpy.app.version_string,
    'build_hash': bpy.app.build_hash.decode(),
    'quality_preserved': quality,
    'sealed_mouth_preserved': mouth,
    'pose_sha_before': pose_before,
    'pose_sha_after': pose_signature(),
    'head_pupil_source_basis_unchanged': True,
    'materials_modified': False,
    'geometry_modified': False,
    'new_keyframes': False,
    'upstream_scripts_executed': [],
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'camera_sync': {'method': 'mute three source expressions; assign camera WORLD Euler to helper LOCAL Euler before render', 'expected': list(expected_euler), 'actual': list(helper.rotation_euler), 'axis_errors': errors},
    'image': scene.render.filepath,
    'working_copy': str(working),
    'working_sha256': hashlib.sha256(working.read_bytes()).hexdigest(),
    'limitations': ['received optimized materials, not movie toon fidelity', 'source rest only, not accepted guitar contact or animation'],
}
assert receipt['source_sha256_after'] == expected_sha
(output / 'source-rest-baseline-receipt.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps({'image': receipt['image'], 'working': str(working), 'pose_unchanged': receipt['pose_sha_after'] == pose_before, 'camera_errors': errors}))
