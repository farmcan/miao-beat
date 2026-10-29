"""One whole-rig coarse pose, one analytic exit per hand, no finger solve."""
import hashlib
import json
import math
import pathlib
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:]
upstream, recovered, out = [pathlib.Path(value).resolve() for value in args]
out.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [upstream, recovered]}
bpy.ops.wm.open_mainfile(filepath=str(upstream), load_ui=False, use_scripts=False)
source_rig = bpy.data.objects['RIG-Cat']
rest = {bone.name: bone.matrix_basis.copy() for bone in source_rig.pose.bones
        if bone.name.startswith(('FK-Thumb', 'FK-Index', 'FK-Middle', 'FK-Pinky'))
        or bone.name in ['FK-Head', 'FK-Head_Hinge', 'Eye_Pupil.L', 'Eye_Pupil.R']}
bpy.ops.wm.open_mainfile(filepath=str(recovered), load_ui=False, use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']
hand = bpy.data.objects['GEO-hands']
guitar = bpy.data.objects['REUSE-CLASSIC-GUITAR']
for name, basis in rest.items():
    rig.pose.bones[name].matrix_basis = basis
rig.pose.bones['PRP-Head']['Sealed Mouth'] = False
rig.pose.bones['Properties_Character_Cat']['Quality'] = 1
for side, word in [('L', 'left'), ('R', 'right')]:
    prop = rig.pose.bones['PRP-UpperArm.' + side]
    prop['ik_' + word + '_upperarm'] = 1.0
    prop['ik_stretch_' + word + '_upperarm'] = 0.0
    prop['auto_rubber_hose_' + word + '_upperarm'] = 0.0
rig.pose.bones['MSTR-Torso'].rotation_euler.x = math.radians(5)
rig.pose.bones['MSTR-Chest'].rotation_euler.x = math.radians(3)
bpy.context.view_layer.update()
for side, sign in [('L', 1), ('R', -1)]:
    bone = rig.pose.bones['P-ROOT-UpperArm.' + side]
    world = rig.matrix_world @ bone.matrix
    rotation = Matrix.Rotation(math.radians(sign * 8), 4, 'Z')
    desired = rotation @ world
    desired.translation = world.translation
    bone.matrix = rig.matrix_world.inverted() @ desired
bpy.context.view_layer.update()


def geometry(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    weights = [{group.group: group.weight for group in vertex.groups} for vertex in mesh.vertices]
    evaluated.to_mesh_clear()
    return points, triangles, weights


# One rigid guitar orientation. Its back plane is placed in front of the actual
# evaluated abdomen, without a locator picked by eye or a parameter search.
rotation = Matrix.Rotation(math.radians(70), 4, 'Y')
neck_axis = rotation.to_3x3() @ Vector((0, 0, 1))
rotation = Matrix.Rotation(math.radians(-10), 4, neck_axis) @ rotation
matrix = rotation @ Matrix.Scale(.70, 4)
matrix.translation = Vector((-.34314516, -.26864243, .205))
guitar.matrix_world = matrix
bpy.context.view_layer.update()
normal = (rotation.to_3x3() @ Vector((0, -1, 0))).normalized()
cross_axis = (rotation.to_3x3() @ Vector((1, 0, 0))).normalized()
body_points, _, _ = geometry(bpy.data.objects['GEO-body'])
abdomen = [point for point in body_points if .18 <= point.z <= .39]
assert abdomen
body_front = max(point.dot(normal) for point in abdomen)
guitar_points = [guitar.matrix_world @ vertex.co for vertex in guitar.data.vertices]
body_back = min(point.dot(normal) for point, vertex in zip(guitar_points, guitar.data.vertices) if vertex.co.z < .50)
body_shift = body_front + .005 - body_back
guitar.matrix_world.translation += normal * body_shift
bpy.context.view_layer.update()
report = {
    'status': 'MEASURING', 'scope': 'one whole-rig coarse pose; no finger solving',
    'inputs': hashes, 'blender': bpy.app.version_string, 'upstream_scripts_executed': [],
    'geometry_edits': 0, 'finger_pose': 'source matrix_basis restored; no curl updates',
    'torso_chest_x_degrees': [5, 3], 'shoulder_world_z_degrees': {'L': 8, 'R': -8},
    'guitar_scale': .70, 'guitar_neck_elevation_degrees': 20,
    'guitar_face_up_tilt_degrees': 10,
    'guitar_abdomen_analytic_shift_m': body_shift,
    'guitar_matrix_world': [list(row) for row in guitar.matrix_world],
    'hands': {}, 'body_head_geometry': {}, 'renders': [],
    'animation_allowed': False, 'art_delivery': False,
}
fixed_stems = ['DEF-Hand', 'DEF-Sleeve', 'DEF-Forearm2',
               'DEF-Index_Carpal', 'DEF-Middle_Carpal', 'DEF-Pinky_Carpal']


def fixed_selection(side, weights):
    indices = {hand.vertex_groups[stem + '.' + side].index for stem in fixed_stems}
    return [index for index, items in enumerate(weights)
            if sum(weight for group, weight in items.items() if group in indices) >= .90]


calibration = {}
for side in ['L', 'R']:
    calibration[side] = (
        (rig.matrix_world @ rig.pose.bones['ORG-Hand.' + side].matrix).copy(),
        (rig.matrix_world @ rig.pose.bones['IK-MSTR-Hand.' + side].matrix).copy())


def place(side, frame):
    old_hand, old_control = calibration[side]
    desired_control = frame @ old_hand.inverted() @ old_control
    rig.pose.bones['IK-MSTR-Hand.' + side].matrix = rig.matrix_world.inverted() @ desired_control
    bpy.context.view_layer.update()
    shoulder = rig.matrix_world @ rig.pose.bones['ORG-UpperArm.' + side].head
    wrist = frame.translation
    direction = (wrist - shoulder).normalized()
    l1 = rig.pose.bones['ORG-UpperArm.' + side].bone.length
    l2 = rig.pose.bones['ORG-Forearm.' + side].bone.length
    distance = (wrist - shoulder).length
    distance_clamped = max(.0001, min(distance, l1 + l2 - .00001))
    along = (l1*l1 - l2*l2 + distance_clamped*distance_clamped) / (2*distance_clamped)
    outward = Vector((.6 if side == 'L' else -.6, .1, -.2))
    outward -= direction * outward.dot(direction)
    outward.normalize()
    radius = math.sqrt(max(0, l1*l1 - along*along))
    elbow = shoulder + direction * along + outward * radius
    pole = rig.pose.bones['IK-POLE-UpperArm.' + side]
    pole_matrix = rig.matrix_world @ pole.matrix
    pole_matrix.translation = elbow + outward * .15
    pole.matrix = rig.matrix_world.inverted() @ pole_matrix
    bpy.context.view_layer.update()


for side in ['L', 'R']:
    # One frame for each hand, chosen from guitar surface directions. Right
    # fingers angle toward bridge/down-bout; left fingers cross neck width.
    if side == 'L':
        axis_y = -cross_axis
        axis_z = normal
        wrist = guitar.matrix_world @ Vector((.065, .075, .69))
        exit_direction = cross_axis
    else:
        axis_y = (-neck_axis * .35 + cross_axis * .94).normalized()
        axis_z = -normal
        wrist = guitar.matrix_world @ Vector((-.025, -.080, .39))
        exit_direction = normal
    axis_x = axis_y.cross(axis_z).normalized()
    axis_z = axis_x.cross(axis_y).normalized()
    frame = Matrix((axis_x, axis_y, axis_z)).transposed().to_4x4()
    frame.translation = wrist
    place(side, frame)
    skin, skin_triangles, weights = geometry(hand)
    core = fixed_selection(side, weights)
    assert core
    # One conservative support-plane exit, not repeated frame/angle trials.
    guitar_points = [guitar.matrix_world @ vertex.co for vertex in guitar.data.vertices]
    if side == 'L':
        relevant = [point for point, vertex in zip(guitar_points, guitar.data.vertices) if vertex.co.z >= .50]
    else:
        relevant = guitar_points
    outer_plane = max(point.dot(exit_direction) for point in relevant)
    core_minimum = min(skin[index].dot(exit_direction) for index in core)
    exit_amount = max(0.0, outer_plane + .002 - core_minimum)
    frame.translation += exit_direction * exit_amount
    place(side, frame)
    actual = rig.matrix_world @ rig.pose.bones['ORG-Hand.' + side].matrix
    shoulder = rig.matrix_world @ rig.pose.bones['ORG-UpperArm.' + side].head
    elbow = rig.matrix_world @ rig.pose.bones['ORG-Forearm.' + side].head
    wrist_actual = actual.translation
    upper_direction = (elbow - shoulder).normalized()
    fore_direction = (wrist_actual - elbow).normalized()
    elbow_flex = math.degrees(upper_direction.angle(fore_direction))
    fore_matrix = rig.matrix_world @ rig.pose.bones['ORG-Forearm.' + side].matrix
    wrist_bend = math.degrees(fore_direction.angle(actual.to_3x3().col[1].normalized()))
    q_relative = fore_matrix.to_quaternion().inverted() @ actual.to_quaternion()
    swing, twist = q_relative.to_swing_twist('Y')
    skin, skin_triangles, weights = geometry(hand)
    core = fixed_selection(side, weights)
    actual_clearance = min(skin[index].dot(exit_direction) - outer_plane for index in core)
    segments = []
    for stem in ['UpperArm', 'Forearm']:
        bone = rig.pose.bones['ORG-' + stem + '.' + side]
        segments.append({'bone': bone.name, 'rest_m': bone.bone.length,
                         'actual_m': bone.length, 'ratio': bone.length/bone.bone.length})
    total_length = sum(item['rest_m'] for item in segments)
    reach = (wrist_actual - shoulder).length / total_length
    axis_errors = [(actual.to_3x3().col[index].normalized() - frame.to_3x3().col[index].normalized()).length for index in range(3)]
    item = {
        'one_analytic_exit_direction': list(exit_direction), 'one_exit_m': exit_amount,
        'core_samples': len(core), 'core_support_plane_clearance_m': actual_clearance,
        'desired_wrist': list(frame.translation), 'actual_wrist': list(wrist_actual),
        'actual_shoulder': list(shoulder), 'actual_elbow': list(elbow),
        'wrist_target_error_m': (wrist_actual-frame.translation).length,
        'axis_errors': axis_errors, 'segments': segments, 'actual_reach_ratio': reach,
        'elbow_flex_degrees': elbow_flex, 'wrist_bend_degrees': wrist_bend,
        'wrist_forearm_twist_degrees': math.degrees(twist),
        'limits': {'reach_max': .95, 'elbow_flex_degrees': [35,130],
                   'wrist_bend_max_degrees': 35, 'twist_abs_max_degrees': 60},
    }
    item['failures'] = []
    for failed, reason in [
        (reach > .95, 'REACH_ABOVE_95_PERCENT'),
        (not 35 <= elbow_flex <= 130, 'ELBOW_OUTSIDE_COARSE_DOMAIN'),
        (wrist_bend > 35, 'WRIST_BEND_ABOVE_35_DEGREES'),
        (abs(math.degrees(twist)) > 60, 'WRIST_TWIST_ABOVE_60_DEGREES'),
        (actual_clearance < .0015, 'CORE_NOT_AT_TWO_MM_SUPPORT_PLANE'),
        (max(axis_errors) > .0001 or item['wrist_target_error_m'] > .0001, 'ORG_HAND_FRAME_NOT_REACHED'),
        (any(abs(seg['ratio']-1) > .0001 for seg in segments), 'ARM_LENGTH_CHANGED')]:
        if failed:
            item['failures'].append(reason)
    report['hands'][side] = item
    print(json.dumps({'hand_finished': side, 'measurements': item}), flush=True)

# Geometry evidence for final candidate: actual triangle intersection rejection,
# plus actual skin interior samples against a local-guitar front/back envelope.
guitar_points, guitar_triangles, _ = geometry(guitar)
guitar_tree = BVHTree.FromPolygons(guitar_points, guitar_triangles, all_triangles=True)
local_points = [vertex.co.copy() for vertex in guitar.data.vertices]
guitar.data.calc_loop_triangles()
local_tree = BVHTree.FromPolygons(local_points, [tuple(t.vertices) for t in guitar.data.loop_triangles], all_triangles=True)
inverse_guitar = guitar.matrix_world.inverted()
for name in ['GEO-body', 'GEO-head', 'GEO-arms', 'GEO-collar', 'GEO-hands']:
    points, triangles, weights = geometry(bpy.data.objects[name])
    assert points and triangles
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True)
    overlaps = tree.overlap(guitar_tree)
    inside = []
    nearest_distance = min(guitar_tree.find_nearest(point)[3] for point in points)
    for index, point in enumerate(points):
        local = inverse_guitar @ point
        front, _, _, _ = local_tree.ray_cast(Vector((local.x,-1,local.z)),Vector((0,1,0)),2)
        back, _, _, _ = local_tree.ray_cast(Vector((local.x,1,local.z)),Vector((0,-1,0)),2)
        if front is not None and back is not None and front.y+.000714 < local.y < back.y-.000714:
            inside.append({'vertex': index, 'approx_inside_depth_m': .7*min(local.y-front.y,back.y-local.y)})
    report['body_head_geometry'][name] = {
        'actual_vertices': len(points), 'actual_triangles': len(triangles),
        'triangle_intersection_pairs': len(overlaps), 'inside_envelope_samples': len(inside),
        'maximum_inside_depth_m': max((v['approx_inside_depth_m'] for v in inside),default=0),
        'minimum_vertex_to_triangle_distance_m': nearest_distance,
        'method_limit': 'triangle overlap and envelope are rejection evidence; no hits alone is not a complete watertight contact certificate'}

failures = [side+':'+value for side, item in report['hands'].items() for value in item['failures']]
for name, item in report['body_head_geometry'].items():
    if item['triangle_intersection_pairs'] or item['inside_envelope_samples']:
        failures.append(name+':GEOMETRY_INTERSECTION_OR_INSIDE')
if report['body_head_geometry']['GEO-head']['minimum_vertex_to_triangle_distance_m'] < .005:
    failures.append('HEAD_CLEARANCE_BELOW_5MM')
report['failures'] = failures
report['status'] = 'FAIL_COARSE_POSE_FROZEN' if failures else 'CORE_PRECHECK_CLEAR_CONTACT_UNVERIFIED'
report['finger_solver_updates'] = 0
report['finger_contact'] = 'NOT_ATTEMPTED: core/pose gate precedes any curl/contact work'
# Two views of this exact single pose. Camera helper local Euler equals original
# expression result before every render; no TRANSFORMS driver substitution.
for obj in list(bpy.data.objects):
    if obj.name.startswith('DIAGNOSTIC-NOT-ART-LABEL'):
        bpy.data.objects.remove(obj, do_unlink=True)
camera = scene.camera
camera.data.ortho_scale = 1.45
center = Vector((0,-.045,.55))
helper = bpy.data.objects['HLP-scene_camera_dummy']
rotation_drivers = [curve for curve in helper.animation_data.drivers if curve.data_path == 'rotation_euler']
assert len(rotation_drivers) == 3
for curve in rotation_drivers:
    curve.mute = True
helper.rotation_mode = 'XYZ'
text_data = bpy.data.curves.new('COARSE-DIAGNOSTIC-LABEL','FONT')
text_data.body = 'TECHNICAL STUDY / NOT ACCEPTED\n'+report['status']
text_data.align_x = 'CENTER'
text_data.size = .018
label = bpy.data.objects.new('COARSE-DIAGNOSTIC-LABEL', text_data)
scene.collection.objects.link(label)
label.parent = camera
label.location = (0,-.68,-2)
material = bpy.data.materials.new('COARSE-DIAGNOSTIC-RED')
material.use_nodes = True
material.node_tree.nodes.clear()
emission = material.node_tree.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (.5,.01,.01,1)
output_node = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
material.node_tree.links.new(emission.outputs[0],output_node.inputs['Surface'])
text_data.materials.append(material)
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 64
for name, direction in [('front',(0,-4,.18)),('three-quarter',(1.5,-4,.50))]:
    camera.location = center + Vector(direction).normalized()*4
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    expected = camera.matrix_world.to_euler()
    helper.rotation_euler = expected
    helper.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    errors = [abs(helper.rotation_euler[i]-expected[i]) for i in range(3)]
    assert max(errors) < 1e-6
    scene.render.filepath = str(out / ('coarse-'+name+'-NOT-ACCEPTED.png'))
    bpy.ops.render.render(write_still=True)
    report['renders'].append({'image': scene.render.filepath,'helper_local_euler_errors':errors})
for text in bpy.data.texts:
    text.use_module = False
native = out / 'whole-rig-coarse-diagnostic-native36.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),copy=True)
report['native'] = str(native)
report['native_sha256'] = hashlib.sha256(native.read_bytes()).hexdigest()
report['inputs_after'] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [upstream,recovered]}
assert hashes == report['inputs_after']
(out / 'whole-rig-coarse-receipt.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'status': report['status'], 'failures':failures, 'native':str(native)}),flush=True)
