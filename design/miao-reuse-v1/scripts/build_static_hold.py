"""One static hold using the existing CloudRig controllers, no upstream scripts."""
import hashlib
import json
import math
import pathlib
import sys

import bpy
from mathutils import Matrix, Vector

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
guitar_source = pathlib.Path(arguments[1]).resolve()
output = pathlib.Path(arguments[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
assert bpy.app.version[:2] == (3, 6)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']


def base_mesh_fingerprint():
    digest = hashlib.sha256()
    for obj in sorted((obj for obj in bpy.data.objects if obj.type == 'MESH'), key=lambda obj: obj.name):
        digest.update(obj.name.encode())
        for vertex in obj.data.vertices:
            digest.update(repr(tuple(vertex.co)).encode())
        for polygon in obj.data.polygons:
            digest.update(repr(tuple(polygon.vertices)).encode())
    return digest.hexdigest()


cat_mesh_before = base_mesh_fingerprint()
actions_before = len(bpy.data.actions)
changed_controls = []


def set_property(bone_name, key, value):
    bone = rig.pose.bones[bone_name]
    before = bone[key]
    bone[key] = value
    changed_controls.append({'bone': bone_name, 'property': key, 'before': before, 'after': value})


def place_control(bone_name, position, orientation=None):
    bone = rig.pose.bones[bone_name]
    pose_matrix = bone.matrix.copy()
    if orientation is not None:
        pose_matrix = orientation.to_4x4()
    pose_matrix.translation = Vector(position)
    bone.matrix = rig.matrix_world.inverted() @ pose_matrix
    changed_controls.append({'bone': bone_name, 'world_target': list(position), 'rotation_only_rigid_matrix': orientation is not None})
    bpy.context.view_layer.update()


def hand_orientation(finger_direction, palmar_normal, side):
    y_axis = Vector(finger_direction).normalized()
    palm = Vector(palmar_normal)
    palm = (palm - y_axis * palm.dot(y_axis)).normalized()
    # The received L/R hand bones have mirrored rolls. Preserve their native
    # handedness so positive finger curl bends toward the natural palm surface.
    x_axis = palm if side == 'L' else -palm
    z_axis = x_axis.cross(y_axis).normalized()
    x_axis = y_axis.cross(z_axis).normalized()
    return Matrix((x_axis, y_axis, z_axis)).transposed()


set_property('Properties_Character_Cat', 'Quality', 3)
for side, word in [('L', 'left'), ('R', 'right')]:
    set_property(f'PRP-UpperArm.{side}', f'ik_{word}_upperarm', 1.0)
    set_property(f'PRP-UpperArm.{side}', f'ik_stretch_{word}_upperarm', 0.0)
    set_property(f'PRP-UpperArm.{side}', f'auto_rubber_hose_{word}_upperarm', 0.0)
set_property('PRP-Head', 'Sealed Mouth', True)
bpy.context.view_layer.update()

left_orientation = hand_orientation((0.423, 0.0, 0.906), (0.0, -1.0, 0.0), 'L')
right_orientation = hand_orientation((0.1, -0.70, -0.70), (0.0, 0.0, -1.0), 'R')
place_control('IK-MSTR-Hand.L', (0.060, -0.218, 0.330), left_orientation)
place_control('IK-MSTR-Hand.R', (-0.105, -0.230, 0.340), right_orientation)
place_control('IK-POLE-UpperArm.L', (0.32, -0.005, 0.20))
place_control('IK-POLE-UpperArm.R', (-0.32, -0.005, 0.20))

finger_curls = {
    'L': {'Index': (60, 65), 'Middle': (65, 65), 'Pinky': (70, 70), 'Thumb': (-25, -35)},
    'R': {'Index': (20, 35), 'Middle': (25, 35), 'Pinky': (30, 40), 'Thumb': (10, 25)},
}
for side, fingers in finger_curls.items():
    for finger, angles in fingers.items():
        for joint, angle in enumerate(angles, start=1):
            bone_name = f'FK-{finger}{joint}.{side}'
            bone = rig.pose.bones[bone_name]
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.x = math.radians(angle)
            changed_controls.append({'bone': bone_name, 'local_x_degrees': angle})

head = rig.pose.bones['FK-Head']
head.rotation_mode = 'XYZ'
head.rotation_euler.y = math.radians(-3.0)
changed_controls.append({'bone': head.name, 'local_y_degrees': -3.0})
for side in ['L', 'R']:
    pupil = rig.pose.bones[f'Eye_Pupil.{side}']
    pupil.matrix_basis = Matrix.Identity(4)
    changed_controls.append({'bone': pupil.name, 'native_rest_eye_control_preserved': True})
bpy.context.view_layer.update()
cat_mesh_after = base_mesh_fingerprint()
assert cat_mesh_before == cat_mesh_after, 'Cat base geometry changed'

before_import = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(guitar_source))
guitar_objects = [obj for obj in bpy.data.objects if obj not in before_import]
guitar = next(obj for obj in guitar_objects if obj.type == 'MESH')
guitar.name = 'REUSE-CLASSIC-GUITAR'
guitar.scale = (0.5, 0.5, 0.5)
guitar.rotation_mode = 'XYZ'
guitar.rotation_euler = (0.0, math.radians(65.0), 0.0)
guitar.location = (-0.235, -0.241, 0.235)
bpy.context.view_layer.update()

scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 96
camera = scene.camera
camera.data.ortho_scale = 1.42
center = Vector((0.0, -0.01, 0.56))


def render_view(name, direction):
    camera.location = center + Vector(direction).normalized() * 4.0
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = str(output / f'{name}.png')
    bpy.ops.render.render(write_still=True)


render_view('original-front-fix1', (0.0, -4.0, 0.18))
render_view('original-three-quarter-fix1', (1.4, -4.0, 0.65))

control_measurements = {}
for side in ['L', 'R']:
    measurements = {}
    for stem in ['ORG-UpperArm', 'ORG-Forearm', 'ORG-Hand', 'IK-MSTR-Hand', 'DEF-Index2', 'DEF-Middle2', 'DEF-Pinky2', 'DEF-Thumb2']:
        bone = rig.pose.bones.get(f'{stem}.{side}')
        if bone:
            measurements[stem] = {'head': list(rig.matrix_world @ bone.head), 'tail': list(rig.matrix_world @ bone.tail), 'pose_length': bone.length, 'rest_length': rig.data.bones[bone.name].length}
    control_measurements[side] = measurements
for text in bpy.data.texts:
    text.use_module = False
working_copy = output / 'static-hold-original-v1-fix1.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working_copy), copy=True)
receipt = {
    'status': 'one targeted repair: active Euler mode on imported guitar and original eye control preserved; pending independent review',
    'source': str(source),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'guitar_source': str(guitar_source),
    'guitar_sha256': hashlib.sha256(guitar_source.read_bytes()).hexdigest(),
    'cat_base_mesh_sha_before': cat_mesh_before,
    'cat_base_mesh_sha_after': cat_mesh_after,
    'new_actions': len(bpy.data.actions) - actions_before,
    'upstream_scripts_executed': [],
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'changed_controls': changed_controls,
    'control_measurements': control_measurements,
    'guitar_transform': {'scale': list(guitar.scale), 'rotation_euler': list(guitar.rotation_euler), 'location': list(guitar.location)},
    'working_copy': str(working_copy),
    'limitations': ['not a contact or quality pass', 'no new keyframes or motion', 'materials remain received source palette'],
}
(output / 'static-hold-original-v1-fix1-receipt.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps({'saved': str(working_copy), 'new_actions': receipt['new_actions'], 'base_mesh_unchanged': cat_mesh_before == cat_mesh_after}))
