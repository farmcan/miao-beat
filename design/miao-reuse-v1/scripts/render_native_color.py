"""Inspect the licensed, redistributed Cat with its received materials unchanged.

No embedded source executes. This creates temporary inspection lighting/camera only.
It saves a separate research working copy; it never overwrites the source,
changes keyframes/geometry/colors, or installs an addon.
"""
import hashlib
import json
import pathlib
import sys

import bpy
from mathutils import Vector

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
output.mkdir(parents=True, exist_ok=True)
expected_source_sha = '42d5c51c758e7f5427622375381058afa8dc398bec637f4822f5636b6b9a41e1'
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha == expected_source_sha, 'Unreviewed source asset bytes'
assert bpy.app.version[:2] == (3, 6), 'Use the author-supported Blender 3.6 runtime'

bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 96
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 0.12
scene.eevee.gtao_factor = 1.1

world = bpy.data.worlds.new('MIAO-INSPECTION-WORLD')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
scene.world = world

visible = [
    obj for obj in scene.objects
    if obj.type == 'MESH'
    and obj.visible_get()
    and not obj.hide_render
    and not obj.name.startswith('WGT')
]
points = [obj.matrix_world @ Vector(corner) for obj in visible for corner in obj.bound_box]
lower = Vector([min(point[axis] for point in points) for axis in range(3)])
upper = Vector([max(point[axis] for point in points) for axis in range(3)])
center = (lower + upper) / 2.0
extent = max(upper - lower)

camera_data = bpy.data.cameras.new('MIAO-INSPECTION-CAMERA')
camera = bpy.data.objects.new('MIAO-INSPECTION-CAMERA', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.lens = 65.0
camera_data.ortho_scale = extent * 1.25
camera_direction = Vector((1.45, -4.0, 0.58)).normalized()
camera.location = center + camera_direction * 4.0
camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()

# Replace only the reviewed camera Euler expressions with explicit simple
# transform variables. This compatibility patch exists only in the working copy.
# It reads the same inspection camera, without allowing arbitrary Python access.
camera_helper = bpy.data.objects.get('HLP-scene_camera_dummy')
camera_driver_patches = []
if camera_helper and camera_helper.animation_data:
    allowed_expressions = {
        f'depsgraph.scene.camera.matrix_world.to_euler()[{index}]'
        for index in range(3)
    }
    for curve in camera_helper.animation_data.drivers:
        if curve.data_path != 'rotation_euler':
            continue
        driver = curve.driver
        expression = driver.expression
        assert expression in allowed_expressions, 'Unexpected camera helper expression'
        while driver.variables:
            driver.variables.remove(driver.variables[0])
        variable = driver.variables.new()
        variable.name = 'camera_euler'
        variable.type = 'TRANSFORMS'
        target = variable.targets[0]
        target.id = camera
        target.transform_type = ('ROT_X', 'ROT_Y', 'ROT_Z')[curve.array_index]
        target.transform_space = 'WORLD_SPACE'
        target.rotation_mode = 'XYZ'
        driver.expression = 'camera_euler'
        curve.mute = False
        camera_driver_patches.append({
            'path': curve.data_path,
            'index': curve.array_index,
            'before': expression,
            'after': driver.expression,
            'simple_expression': driver.is_simple_expression,
            'target': camera.name,
            'transform': target.transform_type,
        })
        assert driver.is_simple_expression


def make_area_light(name, position, energy, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = Vector(position)
    light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()
    return light


make_area_light('MIAO-INSPECTION-KEY', (-2.0, -3.0, 3.5), 350.0, 3.0)
make_area_light('MIAO-INSPECTION-FILL', (2.5, -2.0, 1.6), 140.0, 3.0)
make_area_light('MIAO-INSPECTION-RIM', (0.8, 2.0, 3.0), 250.0, 2.0)
bpy.context.view_layer.update()

scene.render.filepath = str(output / 'wingit-received-materials-color.png')
bpy.ops.render.render(write_still=True)
receipt = {
    'source': str(source),
    'source_sha256_before': source_sha,
    'source_sha256_after': hashlib.sha256(source.read_bytes()).hexdigest(),
    'blender_version': bpy.app.version_string,
    'blender_build_hash': bpy.app.build_hash.decode(),
    'blender_binary': bpy.app.binary_path,
    'render_engine': scene.render.engine,
    'output': scene.render.filepath,
    'source_materials_modified': False,
    'source_geometry_modified': False,
    'source_pose_modified': False,
    'source_scripts_executed': [],
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'camera_driver_patches': camera_driver_patches,
    'temporary_scene_changes': ['inspection camera', 'three area lights', 'inspection world', 'three explicit simple camera drivers'],
    'limitations': [
        'MoveAI redistribution already simplified the original movie shaders.',
        'This render proves received native colors/materials, not original movie toon shader fidelity.',
        'No animation or guitar contact tested.',
    ],
}
for text in bpy.data.texts:
    text.use_module = False
working_copy = output / 'wingit-working-native36.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working_copy), copy=True)
receipt['working_copy'] = str(working_copy)
receipt['working_copy_sha256'] = hashlib.sha256(working_copy.read_bytes()).hexdigest()
receipt['working_copy_embedded_text_autoexecution'] = False
(output / 'native-color-receipt.json').write_text(json.dumps(receipt, indent=2))
assert receipt['source_sha256_before'] == receipt['source_sha256_after']
print(json.dumps({'output': receipt['output'], 'version': receipt['blender_version'], 'scripts_executed': []}))
