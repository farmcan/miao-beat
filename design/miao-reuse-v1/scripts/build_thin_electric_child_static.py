"""Final child-sized thin-electric static integration, actual finite geometry rejection.

One candidate and at most one measured wrist translation repair. No new mesh,
limb scale, infinite hand-support plane, animation, or original-script execution.
"""
import hashlib
import json
import math
import pathlib
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:]
upstream, recovered, glb, out = [pathlib.Path(value).resolve() for value in args]
out.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
source_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [upstream,recovered,glb]}
bpy.ops.wm.open_mainfile(filepath=str(upstream),load_ui=False,use_scripts=False)
source_rig = bpy.data.objects['RIG-Cat']
source_basis = {bone.name: bone.matrix_basis.copy() for bone in source_rig.pose.bones}
source_hand = {side: (source_rig.matrix_world @ source_rig.pose.bones['ORG-Hand.'+side].matrix).copy() for side in ['L','R']}
source_palm = {side: (source_rig.matrix_world @ source_rig.pose.bones['FK-Middle2.'+side].matrix).to_3x3().col[2].normalized() for side in ['L','R']}
thumb_controls = {side: {'locks': list(source_rig.pose.bones['FK-Thumb1.'+side].lock_rotation), 'constraints': [c.type for c in source_rig.pose.bones['FK-Thumb1.'+side].constraints]} for side in ['L','R']}
bpy.ops.wm.open_mainfile(filepath=str(recovered),load_ui=False,use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']
hand = bpy.data.objects['GEO-hands']
cat_meshes = [obj for obj in bpy.data.objects if obj.type=='MESH' and not obj.name.startswith('REUSE-CLASSIC')]


def mesh_hash(objects):
    digest = hashlib.sha256()
    for obj in sorted(objects,key=lambda item:item.name):
        digest.update(obj.name.encode())
        digest.update(bytes(memoryview(__import__('array').array('f',[v for vertex in obj.data.vertices for v in vertex.co]))))
        digest.update(str([tuple(p.vertices) for p in obj.data.polygons]).encode())
    return digest.hexdigest()


cat_before = mesh_hash(cat_meshes)
actions_before = len(bpy.data.actions)
for obj in list(bpy.data.objects):
    if obj.name.startswith(('REUSE-CLASSIC','DIAGNOSTIC-','COARSE-DIAGNOSTIC')):
        bpy.data.objects.remove(obj,do_unlink=True)
for name,basis in source_basis.items():
    if name.startswith(('FK-Thumb','FK-Index','FK-Middle','FK-Pinky','P-ROOT-UpperArm')) or name in ['MSTR-Torso','MSTR-Chest','MSTR-Hips','FK-Head','FK-Head_Hinge','Eye_Pupil.L','Eye_Pupil.R']:
        rig.pose.bones[name].matrix_basis = basis
rig.pose.bones['PRP-Head']['Sealed Mouth'] = False
rig.pose.bones['Properties_Character_Cat']['Quality'] = 1
rig.pose.bones['MSTR-Torso'].rotation_euler.x = math.radians(6)
rig.pose.bones['MSTR-Chest'].rotation_euler.x = math.radians(2)
for side,word in [('L','left'),('R','right')]:
    prop = rig.pose.bones['PRP-UpperArm.'+side]
    prop['ik_'+word+'_upperarm'] = 1.0
    prop['ik_stretch_'+word+'_upperarm'] = 0.0
    prop['auto_rubber_hose_'+word+'_upperarm'] = 0.0
bpy.context.view_layer.update()
for side,sign in [('L',1),('R',-1)]:
    bone = rig.pose.bones['P-ROOT-UpperArm.'+side]
    world = rig.matrix_world @ bone.matrix
    desired = Matrix.Rotation(math.radians(sign*6),4,'Z') @ world
    desired.translation = world.translation
    bone.matrix = rig.matrix_world.inverted() @ desired
bpy.context.view_layer.update()
old = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb))
props = [obj for obj in bpy.data.objects if obj not in old and obj.type=='MESH']
assert len(props)==143
canonical = {obj.name:obj.matrix_world.copy() for obj in props}
prop_hash = mesh_hash(props)


def geom(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
    weights = [{g.group:g.weight for g in v.groups} for v in mesh.vertices]
    evaluated.to_mesh_clear()
    return points,triangles,weights


rotation = Matrix.Rotation(math.radians(70),4,'Y')
T = (rotation.to_3x3() @ Vector((0,0,1))).normalized()
rotation = Matrix.Rotation(math.radians(-8),4,T) @ rotation
C = (rotation.to_3x3() @ Vector((1,0,0))).normalized()
N = (rotation.to_3x3() @ Vector((0,-1,0))).normalized()
SCALE = .55
body_object = next(obj for obj in props if obj.name=='Body')
canonical_body_points = [canonical['Body'] @ vertex.co for vertex in body_object.data.vertices]
pivot_local = Vector(tuple((min(p[i] for p in canonical_body_points)+max(p[i] for p in canonical_body_points))*.5 for i in range(3)))
previous_matrix = rotation @ Matrix.Scale(.70,4)
previous_matrix.translation = Vector((-.300,-.160,.190))
pivot_world_before_fit = previous_matrix @ pivot_local
G = rotation @ Matrix.Scale(SCALE,4)
G.translation = pivot_world_before_fit-G.to_3x3() @ pivot_local


def apply_guitar():
    for obj in props:
        obj.matrix_world = G @ canonical[obj.name]
    bpy.context.view_layer.update()


apply_guitar()
body_points,_,_ = geom(bpy.data.objects['GEO-body'])
abdomen = [p for p in body_points if .18 <= p.z <= .39]
prop_body = next(obj for obj in props if obj.name=='Body')
body_prop_points,_,_ = geom(prop_body)
shift = max(p.dot(N) for p in abdomen) + .005 - min(p.dot(N) for p in body_prop_points)
G.translation += N*shift
apply_guitar()
report = {'status':'BUILDING','inputs':source_hashes,'scope':'final .55 child-sized candidate plus <=1 measured local wrist repair',
          'blender':bpy.app.version_string,'upstream_scripts_executed':[],
          'thumb1_native_controls':thumb_controls,'guitar_meshes':len(props),
          'guitar_matrix_world':[list(row) for row in G],
          'uniform_scale':SCALE,'scale_pivot_canonical_body_bbox_center':list(pivot_local),
          'scale_pivot_world_before_body_fit':list(pivot_world_before_fit),
          'scale_pivot_world_after_body_fit':list(G @ pivot_local),
          'guitar_back_abdomen_shift_m':shift,'palm_frame_correction':'native FK-Middle2 positive-Z palmar direction mapped relative to source ORG-Hand; not Hand+Z',
          'stages':[],'repairs':[],'renders':[],'animation_allowed':False,'art_delivery':False}
# Actual canonical finite solid BVHs and world per-component BVHs. Hardware and
# strings stay in the collision scene, including the protruding tremolo arm.
prop_records = []
for obj in props:
    obj.data.calc_loop_triangles()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    triangles = [tuple(t.vertices) for t in obj.data.loop_triangles]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    prop_records.append({'name':obj.name,'points':points,'triangles':triangles,'low':low,'high':high,'tree':None})
solid_records = []
for obj in props:
    if obj.name not in ['Body','Head / Neck']:
        continue
    points = [canonical[obj.name] @ v.co for v in obj.data.vertices]
    triangles = [tuple(t.vertices) for t in obj.data.loop_triangles]
    solid_records.append({'name':obj.name,'tree':BVHTree.FromPolygons(points,triangles,all_triangles=True)})
assert len(solid_records)==2
invG = G.inverted()
neck_record = next(item for item in solid_records if item['name']=='Head / Neck')
left_section_z = .80
neck_front,_,_,_ = neck_record['tree'].ray_cast(Vector((0,-1,left_section_z)),Vector((0,1,0)),2)
neck_back,_,_,_ = neck_record['tree'].ray_cast(Vector((0,1,left_section_z)),Vector((0,-1,0)),2)
assert neck_front is not None and neck_back is not None
string_local_points = [canonical[obj.name] @ vertex.co for obj in props if obj.name.startswith('Spiral') for vertex in obj.data.vertices]
string_region = [point for point in string_local_points if .31 <= point.z <= .35]
assert string_region
right_string_front_y = min(point.y for point in string_region)
report['surface_derived_wrist_regions'] = {
    'left_neck_section_z':left_section_z,'left_real_front':list(neck_front),'left_real_back':list(neck_back),
    'left_wrist_back_skin_allowance_m':.026,'right_string_region_z':[.31,.35],
    'right_real_string_front_y':right_string_front_y,'right_wrist_front_skin_allowance_m':.022}



def basis_from_y_palm(direction,palm):
    y = direction.normalized()
    x = (palm-y*palm.dot(y)).normalized()
    z = x.cross(y).normalized()
    x = y.cross(z).normalized()
    return Matrix((x,y,z)).transposed()


native_frames = {side:basis_from_y_palm(source_hand[side].to_3x3().col[1],source_palm[side]) for side in ['L','R']}
calibration = {side:((rig.matrix_world @ rig.pose.bones['ORG-Hand.'+side].matrix).copy(),(rig.matrix_world @ rig.pose.bones['IK-MSTR-Hand.'+side].matrix).copy()) for side in ['L','R']}
frames = {}


def position_hand(side,frame):
    H,C0 = calibration[side]
    desired_control = frame @ H.inverted() @ C0
    rig.pose.bones['IK-MSTR-Hand.'+side].matrix = rig.matrix_world.inverted() @ desired_control
    bpy.context.view_layer.update()
    shoulder = rig.matrix_world @ rig.pose.bones['ORG-UpperArm.'+side].head
    direction = (frame.translation-shoulder).normalized()
    l1 = rig.pose.bones['ORG-UpperArm.'+side].bone.length
    l2 = rig.pose.bones['ORG-Forearm.'+side].bone.length
    distance = min((frame.translation-shoulder).length,l1+l2-.0001)
    along = (l1*l1-l2*l2+distance*distance)/(2*max(.0001,distance))
    hint = Vector((.8 if side=='L' else -.8,.2,-.5 if side=='L' else .6))
    hint = (hint-direction*hint.dot(direction)).normalized()
    elbow = shoulder+direction*along+hint*math.sqrt(max(0,l1*l1-along*along))
    bone = rig.pose.bones['IK-POLE-UpperArm.'+side]
    matrix = rig.matrix_world @ bone.matrix
    matrix.translation = elbow+hint*.15
    bone.matrix = rig.matrix_world.inverted() @ matrix
    bpy.context.view_layer.update()


for side in ['L','R']:
    if side=='L':
        wrist = G @ Vector((.070,neck_back.y+.026/SCALE,left_section_z))
        preferred = -C
        palm = N
    else:
        wrist = G @ Vector((-.050,right_string_front_y-.022/SCALE,.33))
        preferred = (C*.94-T*.35).normalized()
        palm = -N
    target_rot = basis_from_y_palm(preferred,palm) @ native_frames[side].inverted() @ source_hand[side].to_3x3()
    frame = target_rot.to_4x4()
    frame.translation = wrist
    position_hand(side,frame)
    forearm = rig.matrix_world @ rig.pose.bones['ORG-Forearm.'+side].matrix
    fore_y = forearm.to_3x3().col[1].normalized()
    # Native wrist follows actual forearm rather than an arbitrary target roll.
    # At most 25 degrees toward the intended hand direction, a single construct.
    angle = fore_y.angle(preferred)
    blend = min(1.0,math.radians(25)/max(angle,1e-8))
    hand_y = fore_y.rotation_difference(preferred).slerp(__import__('mathutils').Quaternion(),1-blend) @ fore_y
    target_rot = basis_from_y_palm(hand_y,palm) @ native_frames[side].inverted() @ source_hand[side].to_3x3()
    frame = target_rot.to_4x4()
    frame.translation = wrist
    position_hand(side,frame)
    frames[side] = frame.copy()
fixed_stems = ['DEF-Hand','DEF-Sleeve','DEF-Forearm2','DEF-Index_Carpal','DEF-Middle_Carpal','DEF-Pinky_Carpal']


def finite_inside(point):
    local = invG @ point
    results = []
    for solid in solid_records:
        front,_,_,_ = solid['tree'].ray_cast(Vector((local.x,-1,local.z)),Vector((0,1,0)),2)
        back,_,_,_ = solid['tree'].ray_cast(Vector((local.x,1,local.z)),Vector((0,-1,0)),2)
        if front is not None and back is not None and front.y+.0005/SCALE < local.y < back.y-.0005/SCALE:
            results.append({'object':solid['name'],'front_exit_m':SCALE*(local.y-front.y),'back_exit_m':SCALE*(back.y-local.y)})
    return results


def collisions(points,triangles):
    if not triangles:
        return {'status':'UNKNOWN_EMPTY_TRIANGLES'}
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    tree = BVHTree.FromPolygons(points,triangles,all_triangles=True)
    counts = {}
    for prop in prop_records:
        if any(high[i]<prop['low'][i] or low[i]>prop['high'][i] for i in range(3)):
            continue
        if prop['tree'] is None:
            prop['tree'] = BVHTree.FromPolygons(prop['points'],prop['triangles'],all_triangles=True)
        overlap = tree.overlap(prop['tree'])
        if overlap:
            counts[prop['name']] = len(overlap)
    return {'triangles_tested':len(triangles),'component_triangle_overlap_pairs':counts,'total_pairs':sum(counts.values())}


def measure(label):
    points,triangles,weights = geom(hand)
    result = {'label':label,'hands':{},'other':{}}
    for side in ['L','R']:
        side_groups = {g.index for g in hand.vertex_groups if g.name.endswith('.'+side)}
        support = {hand.vertex_groups[stem+'.'+side].index for stem in fixed_stems}
        side_ids = {i for i,w in enumerate(weights) if sum(v for g,v in w.items() if g in side_groups)>=.5}
        core_ids = {i for i in side_ids if sum(v for g,v in weights[i].items() if g in support)>=.9}
        core_tris = [tri for tri in triangles if all(i in core_ids for i in tri)]
        all_tris = [tri for tri in triangles if all(i in side_ids for i in tri)]
        assert core_ids and core_tris
        inside = [{'vertex':i,'point':list(points[i]),'solid':finite_inside(points[i])} for i in side_ids]
        inside = [item for item in inside if item['solid']]
        core_inside = [item for item in inside if item['vertex'] in core_ids]
        H = rig.matrix_world @ rig.pose.bones['ORG-Hand.'+side].matrix
        shoulder = rig.matrix_world @ rig.pose.bones['ORG-UpperArm.'+side].head
        elbow = rig.matrix_world @ rig.pose.bones['ORG-Forearm.'+side].head
        fore = (H.translation-elbow).normalized()
        upper = (elbow-shoulder).normalized()
        lengths = [{'bone':'ORG-'+stem+'.'+side,'rest':rig.pose.bones['ORG-'+stem+'.'+side].bone.length,'actual':rig.pose.bones['ORG-'+stem+'.'+side].length} for stem in ['UpperArm','Forearm']]
        result['hands'][side] = {'actual_wrist':list(H.translation),'actual_shoulder':list(shoulder),'actual_elbow':list(elbow),'actual_reach_ratio':(H.translation-shoulder).length/sum(v['rest'] for v in lengths),'arm_segments':lengths,'wrist_target_error_m':(H.translation-frames[side].translation).length,'elbow_flex_degrees':math.degrees(upper.angle(fore)),'wrist_bend_degrees':math.degrees(fore.angle(H.to_3x3().col[1].normalized())),'actual_side_vertices':len(side_ids),'actual_core_vertices':len(core_ids),'core_geometry':collisions(points,core_tris),'all_hand_geometry':collisions(points,all_tris),'inside_samples':inside,'core_inside_samples':core_inside}
    for name in ['GEO-body','GEO-head','GEO-arms','GEO-collar']:
        p,t,_ = geom(bpy.data.objects[name])
        result['other'][name] = collisions(p,t)
        result['other'][name]['finite_inside_vertices'] = sum(bool(finite_inside(v)) for v in p)
    report['stages'].append(result)
    print(json.dumps({'measured':label,'hands':{s:{'reach':h['actual_reach_ratio'],'wrist_error':h['wrist_target_error_m'],'core_pairs':h['core_geometry']['total_pairs'],'core_inside':len(h['core_inside_samples'])} for s,h in result['hands'].items()},'other':result['other']}),flush=True)
    (out/'in-progress-receipt.json').write_text(json.dumps(report,indent=2))
    return result


initial = measure('candidate-before-repair')
# One finite-volume correction only, capped at 20mm; not an infinite support
# plane. If the entire palm is already outside, no displacement is invented.
for side,h in initial['hands'].items():
    if not h['core_inside_samples']:
        continue
    field = 'back_exit_m' if side=='L' else 'front_exit_m'
    distance = max(entry[field] for item in h['core_inside_samples'] for entry in item['solid'])+.0015
    if distance>.020:
        report['repairs'].append({'side':side,'status':'NOT_APPLIED_EXCEEDS_20MM_BOUND','measured_exit_m':distance})
        continue
    direction = -N if side=='L' else N
    frames[side].translation += direction*distance
    position_hand(side,frames[side])
    report['repairs'].append({'side':side,'status':'APPLIED_ONE_FINITE_SKIN_EXIT','distance_m':distance,'direction':list(direction)})
current = measure('after-single-local-repair') if any(v['status'].startswith('APPLIED') for v in report['repairs']) else initial


def core_failures(result):
    failures = []
    for side,h in result['hands'].items():
        if h['core_geometry']['total_pairs'] or h['core_inside_samples']:
            failures.append(side+':PALM_WRIST_CORE_INTERSECTION')
        if h['actual_reach_ratio']>.98 or h['wrist_target_error_m']>.0002:
            failures.append(side+':WRIST_NOT_NATURALLY_REACHABLE')
        if h['wrist_bend_degrees']>40 or h['elbow_flex_degrees']<20:
            failures.append(side+':JOINT_DOMAIN')
        if any(abs(v['actual']/v['rest']-1)>.0001 for v in h['arm_segments']):
            failures.append(side+':ARM_STRETCH')
    for name,data in result['other'].items():
        if data['total_pairs'] or data['finite_inside_vertices']:
            failures.append(name+':GUITAR_INTERSECTION')
    return failures


failures = core_failures(current)
if failures:
    report['finger_contact_status'] = 'NOT_ATTEMPTED_CORE_P0'
    report['finger_updates'] = 0
else:
    report['finger_contact_status'] = 'CORE_CLEAR_BUT_CONTACT_STAGE_NOT_IMPLEMENTED'
    report['finger_updates'] = 0
    failures.append('CONTACT_SURFACE_GAPS_AND_NORMALS_UNVERIFIED')
report['failures'] = failures
report['status'] = 'FAIL_STATIC_INTEGRATION_FROZEN' if failures else 'PENDING_INDEPENDENT_REVIEW'
report['cat_base_sha_before'] = cat_before
report['cat_base_sha_after'] = mesh_hash(cat_meshes)
report['prop_base_sha_before'] = prop_hash
report['prop_base_sha_after'] = mesh_hash(props)
assert report['cat_base_sha_after']==cat_before
assert report['prop_base_sha_after']==prop_hash
report['new_actions'] = len(bpy.data.actions)-actions_before
assert report['new_actions']==0
# Full front/3Q and useful independent face/hand views, one exact pose.
helper = bpy.data.objects['HLP-scene_camera_dummy']
for curve in helper.animation_data.drivers:
    if curve.data_path=='rotation_euler':
        curve.mute = True
helper.rotation_mode = 'XYZ'
camera = scene.camera
label_data = bpy.data.curves.new('THIN-DIAGNOSTIC-LABEL','FONT')
label_data.body = 'TECHNICAL STUDY / NOT ACCEPTED\n'+report['status']
label_data.align_x = 'CENTER'
label_data.size = .018
label = bpy.data.objects.new('THIN-DIAGNOSTIC-LABEL',label_data)
scene.collection.objects.link(label)
label.parent = camera
label.location = (0,-.68,-2)
material = bpy.data.materials.new('THIN-DIAGNOSTIC-RED')
material.use_nodes = True
material.node_tree.nodes.clear()
emission = material.node_tree.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (.5,.01,.01,1)
output_node = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
material.node_tree.links.new(emission.outputs[0],output_node.inputs['Surface'])
label_data.materials.append(material)
views = [('front',Vector((0,-.045,.55)),(0,-4,.18),1.45),('three-quarter',Vector((0,-.045,.55)),(1.5,-4,.5),1.45),('face',Vector((0,-.10,.78)),(0,-4,.18),.75)]
for side in ['L','R']:
    wrist = rig.matrix_world @ rig.pose.bones['ORG-Hand.'+side].head
    center = wrist + (C*.025 if side=='R' else -C*.025)
    direction = (1.2,-4,.5) if side=='R' else (1.4,-3.6,.6)
    views.append(('left-hand' if side=='L' else 'right-hand',center,direction,.36))
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 64
for name,center,direction,scale in views:
    label.hide_render = name not in ['front','three-quarter']
    camera.data.ortho_scale = scale
    camera.location = center+Vector(direction).normalized()*4
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    expected = camera.matrix_world.to_euler()
    helper.rotation_euler = expected
    helper.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    errors = [abs(helper.rotation_euler[i]-expected[i]) for i in range(3)]
    assert max(errors)<1e-6
    scene.render.filepath = str(out/('child-electric-'+name+'-NOT-ACCEPTED.png'))
    bpy.ops.render.render(write_still=True)
    report['renders'].append({'name':name,'path':scene.render.filepath,'helper_axis_errors':errors})
# Save with full scene camera, after restoring helper to that camera once more.
center = Vector((0,-.045,.55))
camera.data.ortho_scale = 1.45
camera.location = center+Vector((0,-4,.18)).normalized()*4
camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
label.hide_render = False
bpy.context.view_layer.update()
helper.rotation_euler = camera.matrix_world.to_euler()
bpy.context.view_layer.update()
for text in bpy.data.texts:
    text.use_module = False
native = out/'child-electric-static-native36.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),copy=True)
report['native'] = str(native)
report['native_sha256'] = hashlib.sha256(native.read_bytes()).hexdigest()
report['inputs_after'] = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [upstream,recovered,glb]}
assert source_hashes==report['inputs_after']
(out/'child-electric-static-receipt.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'status':report['status'],'failures':failures,'native':str(native)}),flush=True)
