"""Read-only camera-local equivalence, DEF axes and real guitar-surface probe."""
import json
import pathlib
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
landmarks_path = pathlib.Path(arguments[2]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
bpy.context.view_layer.update()
scene = bpy.context.scene
camera = scene.camera
helper = bpy.data.objects['HLP-scene_camera_dummy']
expected = camera.matrix_world.to_euler()
actual = helper.rotation_euler.copy()
report = {
    'scope': 'read-only; no source writes, pose changes, renders or counterfactual experiments',
    'source': str(source),
    'camera_local_equivalence': {
        'expected_camera_world_euler': list(expected),
        'actual_helper_local_euler': list(actual),
        'absolute_axis_errors': [abs(expected[index] - actual[index]) for index in range(3)],
        'maximum_axis_error': max(abs(expected[index] - actual[index]) for index in range(3)),
        'camera_parent': camera.parent.name if camera.parent else None,
        'helper_parent': helper.parent.name if helper.parent else None,
        'driver_variables': [],
    },
    'def_axes_and_points': {},
    'neck_surface_samples': [],
    'string_samples': [],
    'finger_tip_nearest_surface': [],
}
for curve in helper.animation_data.drivers:
    if curve.data_path != 'rotation_euler':
        continue
    item = {'axis': curve.array_index, 'expression': curve.driver.expression, 'variables': []}
    for variable in curve.driver.variables:
        target = variable.targets[0]
        item['variables'].append({'name': variable.name, 'type': variable.type, 'target': target.id.name if target.id else None, 'transform_type': target.transform_type, 'transform_space': target.transform_space, 'rotation_mode': target.rotation_mode})
    report['camera_local_equivalence']['driver_variables'].append(item)
rig = bpy.data.objects['RIG-Cat']
for bone in rig.pose.bones:
    if not bone.name.startswith(('DEF-Hand.', 'DEF-Thumb', 'DEF-Index', 'DEF-Middle', 'DEF-Pinky')):
        continue
    world_matrix = rig.matrix_world @ bone.matrix
    axes = world_matrix.to_3x3()
    report['def_axes_and_points'][bone.name] = {
        'head_world': list(rig.matrix_world @ bone.head),
        'tail_world': list(rig.matrix_world @ bone.tail),
        'local_x_in_world': list(axes.col[0].normalized()),
        'local_y_in_world': list(axes.col[1].normalized()),
        'local_z_in_world': list(axes.col[2].normalized()),
        'pose_length': bone.length,
        'rest_length': bone.bone.length,
    }
guitar = bpy.data.objects['REUSE-CLASSIC-GUITAR']
guitar.data.calc_loop_triangles()
world_vertices = [guitar.matrix_world @ vertex.co for vertex in guitar.data.vertices]
triangles = [tuple(triangle.vertices) for triangle in guitar.data.loop_triangles]
tree = BVHTree.FromPolygons(world_vertices, triangles, all_triangles=True)
front_normal = (guitar.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()
report['guitar_front_normal_world'] = list(front_normal)
report['guitar_neck_axis_world'] = list((guitar.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized())
for position_z in [0.60, 0.65, 0.70, 0.75, 0.80]:
    for side, local_y, direction in [('front', -0.15, -front_normal), ('back', 0.15, front_normal)]:
        origin = guitar.matrix_world @ Vector((0.0, local_y, position_z))
        point, normal, triangle_index, distance = tree.ray_cast(origin, direction, 0.20)
        report['neck_surface_samples'].append({'source_z': position_z, 'ray_side': side, 'hit_world': list(point) if point else None, 'normal_world': list(normal) if normal else None, 'triangle': triangle_index, 'ray_distance': distance, 'classification_limit': 'actual joined-mesh neck surface hit; may hit fret hardware, not semantic face labels'})
landmarks = json.loads(landmarks_path.read_text())['local_landmarks']
for label in ['six_string_intersections_z_070', 'six_string_intersections_z_030']:
    for local_point in landmarks[label]:
        world_point = guitar.matrix_world @ Vector(local_point)
        point, normal, triangle_index, distance = tree.find_nearest(world_point)
        report['string_samples'].append({'label': label, 'landmark_source_local': local_point, 'landmark_world': list(world_point), 'nearest_actual_surface_world': list(point), 'nearest_surface_normal_world': list(normal), 'distance': distance, 'triangle': triangle_index})
for side in ['L', 'R']:
    for finger in ['Thumb', 'Index', 'Middle', 'Pinky']:
        name = f'DEF-{finger}2.{side}'
        bone = rig.pose.bones[name]
        tip = rig.matrix_world @ bone.tail
        point, normal, triangle_index, distance = tree.find_nearest(tip)
        report['finger_tip_nearest_surface'].append({'bone': name, 'tip_bone_tail_world': list(tip), 'tip_bone_tail_guitar_local': list(guitar.matrix_world.inverted() @ tip), 'nearest_surface_world': list(point), 'normal_world': list(normal), 'unsigned_distance': distance, 'normal_signed_distance': (tip - point).dot(normal), 'triangle': triangle_index, 'limit': 'bone endpoint is not skin surface; does not certify contact'})
output.write_text(json.dumps(report, indent=2))
print(json.dumps({'camera_local_equivalence': report['camera_local_equivalence'], 'def_bones': len(report['def_axes_and_points']), 'neck_surface_samples': len(report['neck_surface_samples']), 'finger_tips': report['finger_tip_nearest_surface']}))
