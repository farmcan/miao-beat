"""One bounded three-pad solve, one clearly unaccepted diagnostic front render."""
import hashlib
import json
import math
import pathlib
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(args[0]).resolve()
proposal = json.loads(pathlib.Path(args[1]).read_text())
output = pathlib.Path(args[2]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
rig = bpy.data.objects['RIG-Cat']
hand = bpy.data.objects['GEO-hands']
guitar = bpy.data.objects['REUSE-CLASSIC-GUITAR']
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
traces = []


def set_angles(names, values):
    for name, value in zip(names, values):
        rig.pose.bones[name].rotation_euler.x = value
    bpy.context.view_layer.update()


def pad_surface(spec):
    evaluated = hand.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    group = hand.vertex_groups[spec['bone']].index
    bone = rig.pose.bones[spec['bone']]
    inverse_bone = (rig.matrix_world @ bone.matrix).inverted()
    weights = [next((entry.weight for entry in vertex.groups if entry.group == group), 0.0) for vertex in mesh.vertices]
    triangles = []
    facing = Vector(spec['facing']).normalized()
    for triangle in mesh.loop_triangles:
        ids = tuple(triangle.vertices)
        if sum(weights[index] for index in ids) / 3.0 < .25:
            continue
        center = sum((points[index] for index in ids), Vector()) / 3.0
        local = inverse_bone @ center
        if not spec['band'][0] * bone.length <= local.y <= spec['band'][1] * bone.length:
            continue
        if spec['pad_side'] == 'positive_z' and local.z < 0.0:
            continue
        if spec['pad_side'] == 'positive_x' and local.x < 0.0:
            continue
        normal = (points[ids[1]] - points[ids[0]]).cross(points[ids[2]] - points[ids[0]])
        if normal.length < 1e-10 or normal.normalized().dot(facing) < .10:
            continue
        triangles.append(ids)
    evaluated.to_mesh_clear()
    if not triangles:
        raise RuntimeError('No real pad triangles for ' + spec['bone'])
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True)
    point, normal, triangle, distance = tree.find_nearest(Vector(spec['target']))
    return point, normal, distance, len(triangles)


specifications = [
    {'label': 'left_index', 'bone': 'DEF-Index2.L', 'joints': ['FK-Index1.L', 'FK-Index2.L'], 'target': proposal['left_index_pad']['skin_target'], 'facing': [0, 1, 0], 'band': [.55, 1.20], 'pad_side': 'positive_z', 'bounds': [(0, 100), (0, 110)], 'tolerance': .0005},
    {'label': 'left_proximal_thumb', 'bone': 'DEF-Thumb1.L', 'joints': ['FK-Thumb1.L', 'FK-Thumb2.L'], 'target': proposal['left_proximal_thumb_back_support']['skin_target'], 'facing': list(-Vector(proposal['left_proximal_thumb_back_support']['surface_normal'])), 'band': [.30, .80], 'pad_side': None, 'bounds': [(-60, 60), (-60, 75)], 'tolerance': .0010},
    {'label': 'right_thumb', 'bone': 'DEF-Thumb2.R', 'joints': ['FK-Thumb1.R', 'FK-Thumb2.R'], 'target': proposal['right_thumb_prepare']['skin_target'], 'facing': [0, 1, 0], 'band': [.55, 1.20], 'pad_side': 'positive_x', 'bounds': [(-60, 60), (-60, 75)], 'tolerance': .0010},
]
for spec in specifications:
    names = spec['joints']
    bounds = [(math.radians(a), math.radians(b)) for a, b in spec['bounds']]
    values = [rig.pose.bones[name].rotation_euler.x for name in names]
    trace = {'label': spec['label'], 'bone': spec['bone'], 'target': spec['target'], 'initial_angles_degrees': [math.degrees(value) for value in values], 'updates': [], 'bounds_degrees': spec['bounds']}
    no_improvement = 0
    try:
        point, normal, error, triangles = pad_surface(spec)
        trace['initial_continuous_skin_error_m'] = error
        for iteration in range(15):
            if error <= spec['tolerance']:
                break
            jacobian = []
            for joint_index in range(2):
                step = math.radians(1.0)
                if values[joint_index] + step > bounds[joint_index][1]:
                    step = -step
                perturbed = values.copy()
                perturbed[joint_index] += step
                set_angles(names, perturbed)
                perturbed_point, _, _, _ = pad_surface(spec)
                jacobian.append((perturbed_point - point) / step)
            set_angles(names, values)
            residual = Vector(spec['target']) - point
            a00 = jacobian[0].dot(jacobian[0]) + 0.00001
            a11 = jacobian[1].dot(jacobian[1]) + 0.00001
            a01 = jacobian[0].dot(jacobian[1])
            b0 = jacobian[0].dot(residual)
            b1 = jacobian[1].dot(residual)
            determinant = a00 * a11 - a01 * a01
            deltas = [(a11 * b0 - a01 * b1) / determinant, (a00 * b1 - a01 * b0) / determinant]
            max_step = math.radians(5.0)
            candidate = [max(bounds[index][0], min(bounds[index][1], values[index] + max(-max_step, min(max_step, deltas[index])))) for index in range(2)]
            set_angles(names, candidate)
            candidate_point, candidate_normal, candidate_error, triangles = pad_surface(spec)
            improved = candidate_error + 0.000001 < error
            trace['updates'].append({'iteration': iteration, 'angles_degrees': [math.degrees(value) for value in candidate], 'continuous_skin_error_m': candidate_error, 'improved': improved})
            if improved:
                values = candidate
                point, normal, error = candidate_point, candidate_normal, candidate_error
                no_improvement = 0
            else:
                set_angles(names, values)
                no_improvement += 1
            if no_improvement >= 3:
                break
        set_angles(names, values)
        point, normal, error, triangles = pad_surface(spec)
        trace.update(final_angles_degrees=[math.degrees(value) for value in values], final_continuous_skin_error_m=error, final_skin_point=list(point), final_skin_normal=list(normal), actual_pad_triangles=triangles, target_distance_within_tolerance=error <= spec['tolerance'])
    except RuntimeError as failure:
        set_angles(names, values)
        trace['status'] = 'FAIL_EMPTY_OR_LOST_PAD_SURFACE'
        trace['reason'] = str(failure)
    traces.append(trace)
    print(json.dumps({'pad_finished': trace}), flush=True)

# Final skin check uses actual support groups: the hand group alone never exceeds
# .448; native Carpal/Sleeve/Forearm groups support the rest of the palm and wrist.
guitar.data.calc_loop_triangles()
guitar_points = [guitar.matrix_world @ vertex.co for vertex in guitar.data.vertices]
guitar_tree = BVHTree.FromPolygons(guitar_points, [tuple(t.vertices) for t in guitar.data.loop_triangles], all_triangles=True)
evaluated = hand.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
final_skin = {}
for side in ['L', 'R']:
    side_groups = {group.index for group in hand.vertex_groups if group.name.endswith('.' + side)}
    fixed_stems = ['DEF-Hand', 'DEF-Sleeve', 'DEF-Forearm2', 'DEF-Index_Carpal', 'DEF-Middle_Carpal', 'DEF-Pinky_Carpal']
    fixed_groups = {hand.vertex_groups[f'{stem}.{side}'].index for stem in fixed_stems}
    total = 0
    fixed_count = 0
    inside = []
    fixed_inside = []
    for vertex in mesh.vertices:
        weights = {entry.group: entry.weight for entry in vertex.groups}
        if sum(weight for index, weight in weights.items() if index in side_groups) < .5:
            continue
        total += 1
        fixed_weight = sum(weight for index, weight in weights.items() if index in fixed_groups)
        if fixed_weight >= .90:
            fixed_count += 1
        point = evaluated.matrix_world @ vertex.co
        front, _, _, _ = guitar_tree.ray_cast(Vector((point.x, -1, point.z)), Vector((0, 1, 0)), 2)
        back, _, _, _ = guitar_tree.ray_cast(Vector((point.x, 1, point.z)), Vector((0, -1, 0)), 2)
        if front is not None and back is not None and front.y + .0005 < point.y < back.y - .0005:
            item = {'vertex': vertex.index, 'point': list(point), 'depth_m': min(point.y - front.y, back.y - point.y), 'fixed_support_weight': fixed_weight}
            inside.append(item)
            if fixed_weight >= .90:
                fixed_inside.append(item)
    assert total > 0 and fixed_count > 0
    final_skin[side] = {'actual_side_vertices': total, 'fixed_palm_wrist_vertices': fixed_count, 'inside_count': len(inside), 'fixed_support_inside_count': len(fixed_inside), 'maximum_inside_depth_m': max((item['depth_m'] for item in inside), default=0), 'worst': sorted(inside, key=lambda item: item['depth_m'], reverse=True)[:8], 'limit': 'triangle ray envelope rejection, not a complete collision-pass certificate'}
evaluated.to_mesh_clear()
status = 'FAIL_CONTACT_SKIN_OR_UNSOLVED_TARGET'
report = {'status': status, 'source': str(source), 'source_sha256': source_sha, 'single_proposal': True, 'solver_limits': {'finite_difference_degrees': 1, 'maximum_step_degrees': 5, 'maximum_updates_per_pad': 15, 'no_improvement_stop': 3}, 'pad_traces': traces, 'final_actual_skin': final_skin, 'no_geometry_changes': True, 'upstream_scripts_executed': [], 'renders': 1, 'art_delivery': False, 'animation_allowed': False}
# Explicitly authorized single internal diagnostic, even on FAIL. No further pose
# or lighting search. A camera-parent text label is diagnostic UI only.
scene = bpy.context.scene
camera = scene.camera
center = Vector((0, -.01, .56))
camera.location = center + Vector((0, -4, .18)).normalized() * 4
camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 1.42
helper = bpy.data.objects['HLP-scene_camera_dummy']
for curve in helper.animation_data.drivers:
    if curve.data_path == 'rotation_euler':
        curve.mute = True
bpy.context.view_layer.update()
expected = camera.matrix_world.to_euler()
helper.rotation_euler = expected
helper.update_tag(refresh={'OBJECT'})
bpy.context.view_layer.update()
errors = [abs(helper.rotation_euler[index] - expected[index]) for index in range(3)]
assert max(errors) < 1e-6
text_data = bpy.data.curves.new('DIAGNOSTIC-NOT-ART-LABEL', 'FONT')
text_data.body = 'TECHNICAL STUDY / NOT ACCEPTED\nCONTACT GATE: FAIL'
text_data.align_x = 'CENTER'
text_data.size = .020
text_object = bpy.data.objects.new('DIAGNOSTIC-NOT-ART-LABEL', text_data)
scene.collection.objects.link(text_object)
text_object.parent = camera
text_object.location = (0, -.675, -2)
material = bpy.data.materials.new('DIAGNOSTIC-LABEL-RED')
material.diffuse_color = (.5, .01, .01, 1)
material.use_nodes = True
material.node_tree.nodes.clear()
emission = material.node_tree.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (.5, .01, .01, 1)
output_node = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
material.node_tree.links.new(emission.outputs[0], output_node.inputs['Surface'])
text_data.materials.append(material)
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.filepath = str(output / 'diagnostic-front-FAIL-NOT-ACCEPTED.png')
bpy.ops.render.render(write_still=True)
working = output / 'bounded-contact-candidate-FAIL-diagnostic.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working), copy=True)
report['diagnostic_image'] = scene.render.filepath
report['candidate_native'] = str(working)
report['camera_errors'] = errors
report['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
assert report['source_sha256_after'] == source_sha
(output / 'bounded-keypad-solve-FAIL-receipt.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'status': status, 'image': scene.render.filepath, 'skin': final_skin}), flush=True)
