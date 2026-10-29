"""One measured hand-frame placement and actual wrist/palm skin stop gate.

No render, no geometry edits, no finger-angle search. A fixed wrist/palm collision
stops before per-finger solving because finger curls cannot clear that region.
"""
import hashlib
import json
import pathlib
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
proposal_path = pathlib.Path(arguments[1]).resolve()
output = pathlib.Path(arguments[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
proposal = json.loads(proposal_path.read_text())
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
rig = bpy.data.objects['RIG-Cat']
guitar = bpy.data.objects['REUSE-CLASSIC-GUITAR']
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
report = {
    'source': str(source),
    'source_sha256': source_sha,
    'proposal': str(proposal_path),
    'status': 'measurement in progress',
    'scope': 'one fixed measured proposal; no finger search/render/geometry/animation',
    'upstream_scripts_executed': [],
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'hand_frame_calibration': {},
    'actual_reach': {},
    'wrist_palm_skin_gate': {},
    'finger_pad_measurements': {},
}
assert rig.pose.bones['PRP-Head']['Sealed Mouth'] is False
for side, word in [('L', 'left'), ('R', 'right')]:
    rig.pose.bones[f'PRP-UpperArm.{side}'][f'ik_{word}_upperarm'] = 1.0
    rig.pose.bones[f'PRP-UpperArm.{side}'][f'ik_stretch_{word}_upperarm'] = 0.0
    rig.pose.bones[f'PRP-UpperArm.{side}'][f'auto_rubber_hose_{word}_upperarm'] = 0.0
bpy.context.view_layer.update()
calibrations = {}
for side in ['L', 'R']:
    hand = rig.matrix_world @ rig.pose.bones[f'ORG-Hand.{side}'].matrix
    control = rig.matrix_world @ rig.pose.bones[f'IK-MSTR-Hand.{side}'].matrix
    calibrations[side] = {'hand': hand.copy(), 'control': control.copy()}
guitar.matrix_world = Matrix(proposal['final_candidate']['matrix_world'])
for side, key in [('L', 'left_index_pad'), ('R', 'right_thumb_prepare')]:
    desired = Matrix(proposal[key]['hand_basis_xyz_world']).transposed().to_4x4()
    desired.translation = Vector(proposal[key]['wrist'])
    original_hand = calibrations[side]['hand']
    original_control = calibrations[side]['control']
    desired_control = desired @ original_hand.inverted() @ original_control
    rig.pose.bones[f'IK-MSTR-Hand.{side}'].matrix = rig.matrix_world.inverted() @ desired_control
    bpy.context.view_layer.update()
    actual = rig.matrix_world @ rig.pose.bones[f'ORG-Hand.{side}'].matrix
    position_error = (actual.translation - desired.translation).length
    axis_errors = [(actual.to_3x3().col[axis].normalized() - desired.to_3x3().col[axis].normalized()).length for axis in range(3)]
    report['hand_frame_calibration'][side] = {
        'original_org_hand_world': [list(row) for row in original_hand],
        'original_ik_master_world': [list(row) for row in original_control],
        'control_to_hand_relative': [list(row) for row in original_control.inverted() @ original_hand],
        'desired_org_hand_world': [list(row) for row in desired],
        'actual_org_hand_world': [list(row) for row in actual],
        'position_error_m': position_error,
        'axis_vector_errors': axis_errors,
    }
    assert position_error < 0.0001 and max(axis_errors) < 0.0001, 'Native ORG-Hand did not reach calibrated frame'
    shoulder = rig.matrix_world @ rig.pose.bones[f'ORG-UpperArm.{side}'].head
    wrist = actual.translation
    arm_length = sum(rig.pose.bones[f'ORG-{stem}.{side}'].bone.length for stem in ['UpperArm', 'Forearm'])
    segments = []
    for stem in ['UpperArm', 'Forearm']:
        bone = rig.pose.bones[f'ORG-{stem}.{side}']
        segments.append({'bone': bone.name, 'pose_length': bone.length, 'rest_length': bone.bone.length, 'ratio': bone.length / bone.bone.length})
    report['actual_reach'][side] = {'actual_shoulder': list(shoulder), 'actual_wrist': list(wrist), 'distance_m': (wrist - shoulder).length, 'arm_length_m': arm_length, 'ratio': (wrist - shoulder).length / arm_length, 'remaining_m': arm_length - (wrist - shoulder).length, 'segments': segments}
    assert (wrist - shoulder).length <= arm_length + 1e-5
    assert all(abs(segment['ratio'] - 1.0) < 1e-4 for segment in segments), 'Arm stretch detected'

bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
guitar.data.calc_loop_triangles()
guitar_vertices = [guitar.matrix_world @ vertex.co for vertex in guitar.data.vertices]
guitar_triangles = [tuple(triangle.vertices) for triangle in guitar.data.loop_triangles]
guitar_tree = BVHTree.FromPolygons(guitar_vertices, guitar_triangles, all_triangles=True)
hand_object = bpy.data.objects['GEO-hands']
evaluated = hand_object.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
mesh.calc_loop_triangles()
skin_vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
weights = [{group.group: group.weight for group in vertex.groups} for vertex in mesh.vertices]


def envelope_collision(point):
    front, _, _, _ = guitar_tree.ray_cast(Vector((point.x, -1.0, point.z)), Vector((0.0, 1.0, 0.0)), 2.0)
    if front is None:
        return None
    back, _, _, _ = guitar_tree.ray_cast(Vector((point.x, 1.0, point.z)), Vector((0.0, -1.0, 0.0)), 2.0)
    if back is None or back.y - front.y < 0.0001:
        return None
    if front.y + 0.0005 < point.y < back.y - 0.0005:
        return {'skin_point': list(point), 'front': list(front), 'back': list(back), 'depth_from_nearest_envelope_m': min(point.y - front.y, back.y - point.y)}
    return None


core_failed = False
for side in ['L', 'R']:
    group = hand_object.vertex_groups[f'DEF-Hand.{side}'].index
    side_groups = {item.index for item in hand_object.vertex_groups if item.name.endswith('.' + side)}
    bone = rig.pose.bones[f'DEF-Hand.{side}']
    inverse_bone = (rig.matrix_world @ bone.matrix).inverted()
    ids = []
    collisions = []
    minimum_clearance = float('inf')
    for index, point in enumerate(skin_vertices):
        side_weight = sum(value for group_index, value in weights[index].items() if group_index in side_groups)
        if side_weight < 0.50:
            continue
        local = inverse_bone @ point
        if not -0.025 <= local.y <= bone.length * 0.80:
            continue
        ids.append(index)
        nearest, normal, triangle, distance = guitar_tree.find_nearest(point)
        minimum_clearance = min(minimum_clearance, distance)
        collision = envelope_collision(point)
        if collision:
            collision['vertex_index'] = index
            collision['side_weight_sum'] = side_weight
            collision['hand_group_weight'] = weights[index].get(group, 0.0)
            collisions.append(collision)
    assert ids, 'No real wrist/palm skin samples; fail closed'
    core_failed = core_failed or bool(collisions)
    report['wrist_palm_skin_gate'][side] = {
        'actual_evaluated_vertices_tested': len(ids),
        'selection': 'side deform weights sum >= .50 and actual DEF-Hand local Y in [-.025,.80L]; includes real Sleeve/Forearm/Carpal-supported skin',
        'inside_guitar_envelope_count': len(collisions),
        'maximum_inside_depth_m': max((item['depth_from_nearest_envelope_m'] for item in collisions), default=0.0),
        'minimum_unsigned_nearest_surface_m': minimum_clearance,
        'worst_samples': sorted(collisions, key=lambda item: item['depth_from_nearest_envelope_m'], reverse=True)[:12],
        'limit': 'actual skin vertices inside front/back triangle ray envelope reject; zero alone is not complete triangle collision proof',
    }

for key, bone_name in [('left_index_pad', 'DEF-Index2.L'), ('right_thumb_prepare', 'DEF-Thumb2.R')]:
    group = hand_object.vertex_groups[bone_name].index
    target = Vector(proposal[key]['skin_target'])
    bone = rig.pose.bones[bone_name]
    inverse_bone = (rig.matrix_world @ bone.matrix).inverted()
    candidates = []
    for index, point in enumerate(skin_vertices):
        local = inverse_bone @ point
        if weights[index].get(group, 0.0) >= .35 and local.y >= .6 * bone.length:
            candidates.append((index, point, (point - target).length))
    nearest = min(candidates, key=lambda item: item[2])
    report['finger_pad_measurements'][key] = {'target_world': list(target), 'closest_actual_tip_region_vertex': list(nearest[1]), 'closest_vertex_error_m': nearest[2], 'tip_skin_vertices_sampled': len(candidates), 'limit': 'discrete skin vertex proximity only; not accepted pad contact or a bone-tail proxy'}
evaluated.to_mesh_clear()
if core_failed:
    report['status'] = 'FAIL_STOP_FIXED_WRIST_PALM_SKIN_COLLISION'
    report['stop_reason'] = 'Measured fixed wrist/palm skin enters guitar. Finger-only two-joint X updates cannot clear the fixed high-weight DEF-Hand region; do not spend finger search or render this failed candidate.'
    report['finger_solver_updates'] = 0
    report['renders'] = 0
else:
    report['status'] = 'FIXED_WRIST_CORE_GATE_CLEAR_NEEDS_BOUNDED_FINGER_SOLVER'
    report['finger_solver_updates'] = 0
    report['renders'] = 0
for text in bpy.data.texts:
    text.use_module = False
working = output / 'measured-contact-candidate-skin-checked.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working), copy=True)
report['candidate_native'] = str(working)
report['candidate_sha256'] = hashlib.sha256(working.read_bytes()).hexdigest()
report['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
assert report['source_sha256_after'] == source_sha
(output / 'measured-contact-skin-gate.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'status': report['status'], 'actual_reach': report['actual_reach'], 'skin': report['wrist_palm_skin_gate'], 'finger_solver_updates': 0, 'renders': 0}))
