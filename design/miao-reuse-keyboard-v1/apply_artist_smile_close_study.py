"""Reuse only proven face value differences from an upstream pose snapshot.

No action assignment/evaluation, frame_set, keyframes, body/hand/prop reset,
embedded-code execution, geometry/material editing, or baseline overwrite.
"""
import array
import hashlib
import json
import pathlib
import re
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index('--')+1:]
manifest_path,diff_path,out = [pathlib.Path(value).resolve() for value in args]
out.mkdir(parents=True,exist_ok=True)
manifest = json.loads(manifest_path.read_text())
diff = json.loads(diff_path.read_text())
source = next(pathlib.Path(item['path']) for item in manifest['files'] if item['path'].endswith('keyboard-supported-native36.blend'))
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha==manifest['native_sha256']
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']
changed = diff['exact_value_differences']
face_names = {item['bone'] for item in changed}
assert len(face_names)==64 and len(changed)==252
allowed_prefixes = ('ACT-MouthCorner','BehindEyes','Hook_Curve_Mouth','Hook_Eye','Hook_L_Eye','Hook_R_Eye','LTC-BehindEye','LTC-Face','Lips_Bot_WithCorner','Mouth_Bot','Mouth_Corner','Mouth_Top','Muzzle_Top','PRP-Head','ROOT-Curve_Mouth','ROOT-Eye','ROOT-Eyebrow','ROOT-LTC-Face','ROOT-Lines_Teeth','STR-Eyebrow','STR-TIP-Eyebrow','Teeth_Bot_Root','Teeth_Top_Root')
assert all(name and name.startswith(allowed_prefixes) for name in face_names)
assert not diff['missing_from_default'] and not diff['missing_from_smile']
assert rig.pose.bones['PRP-Head']['Sealed Mouth'] is False
quality = rig.pose.bones['Properties_Character_Cat']['Quality']
action_count = len(bpy.data.actions)
keyframe_count = sum(len(curve.keyframe_points) for action in bpy.data.actions for curve in action.fcurves)
frame_before = scene.frame_current
body_tokens = ['UpperArm','Forearm','Hand','Thumb','Index','Middle','Pinky','Carpal','Spine','Chest','Torso','Hips','Thigh','Shin','Foot','Toe','Leg','Tail']
body_bones = [bone for bone in rig.pose.bones if bone.name not in face_names and (bone.name in ['root','P-root','FK-Head','FK-Head_Hinge'] or any(token in bone.name for token in body_tokens))]
body_objects = [bpy.data.objects[name] for name in ['GEO-body','GEO-arms','GEO-hands','GEO-legs','GEO-shoes','GEO-tail']]
prop_names = {item['name'] for item in json.loads((manifest_path.parent.parent/'prop/prop-receipt.json').read_text())['objects']}
fixed_objects = [obj for obj in scene.objects if obj.name in prop_names or obj.name.startswith('SUPPORT-') or obj.name=='ENV-GROUND' or obj==rig]


def digest_json(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def geometry_hash(objects,evaluated=False):
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects,key=lambda value:value.name):
        digest.update(obj.name.encode())
        instance = obj.evaluated_get(depsgraph) if evaluated else obj
        mesh = instance.to_mesh() if evaluated else obj.data
        digest.update(array.array('f',[number for vertex in mesh.vertices for number in vertex.co]).tobytes())
        digest.update(str([tuple(poly.vertices) for poly in mesh.polygons]).encode())
        if evaluated:
            instance.to_mesh_clear()
    return digest.hexdigest()


def protected_state():
    bpy.context.view_layer.update()
    return {
        'non_changed_bone_basis':digest_json([(bone.name,[list(row) for row in bone.matrix_basis]) for bone in rig.pose.bones if bone.name not in face_names]),
        'body_arm_finger_evaluated_pose':digest_json([(bone.name,[list(row) for row in bone.matrix],list(bone.head),list(bone.tail)) for bone in body_bones]),
        'body_arm_hand_actual_evaluated_geometry':geometry_hash(body_objects,True),
        'all_existing_mesh_base_geometry':geometry_hash([obj for obj in scene.objects if obj.type=='MESH']),
        'rig_keyboard_table_ground_world':digest_json([(obj.name,[list(row) for row in obj.matrix_world]) for obj in sorted(fixed_objects,key=lambda value:value.name)]),
    }


before = protected_state()
report = {'scope':'internal source-author smile close pose reuse; no final static GO',
          'source':str(source),'source_sha256_before':source_sha,'upstream_pose_source':diff['source'],
          'upstream_pose_source_sha256':diff['source_sha256_before'],
          'default_action':'default','smile_action':'smile close','exact_face_difference_channels':len(changed),
          'face_bones':sorted(face_names),'protected_bone_count':len(body_bones),'fixed_object_count':len(fixed_objects),
          'protected_before':before,'applied_channels':[],'context_restore':[],
          'frame_set_calls':0,'whole_action_applied':False,'upstream_scripts_executed':[],
          'new_keyframes':0,'new_actions':0,'renders':[],'credit':'Cat Rig (CC-BY) Blender Foundation | studio.blender.org'}
channel_pattern = re.compile(r'^pose\.bones\["([^\"]+)"\]\.(location|rotation_euler|scale)$')
custom_pattern = re.compile(r'^pose\.bones\["([^\"]+)"\]\["([^\"]+)"\]$')
for item in changed:
    path = item['data_path']
    index = item['array_index']
    value = item['smile_close']['value']
    transform = channel_pattern.fullmatch(path)
    custom = custom_pattern.fullmatch(path)
    if transform:
        name,property_name = transform.groups()
        old = getattr(rig.pose.bones[name],property_name)[index]
        getattr(rig.pose.bones[name],property_name)[index] = value
    else:
        assert custom,path
        name,property_name = custom.groups()
        assert name=='PRP-Head' and property_name in ['Sealed Teeth','Teeth_Zigzag']
        old = rig.pose.bones[name][property_name]
        rig.pose.bones[name][property_name] = bool(value) if isinstance(old,bool) else value
    report['applied_channels'].append({'data_path':path,'array_index':index,'baseline':old,'author_smile':value})
# Shared author context is not a creative adjustment: both author snapshots
# store Curvature 2.76470565796, whereas the received current pose stores 5.
context = next(item for item in diff['prp_head_context'] if item['data_path']=='pose.bones["PRP-Head"]["Curvature"]')
assert context['default']['value']==context['smile_close']['value']
old = rig.pose.bones['PRP-Head']['Curvature']
rig.pose.bones['PRP-Head']['Curvature'] = context['smile_close']['value']
report['context_restore'].append({'property':'PRP-Head.Curvature','baseline':old,'author_default_and_smile_close':context['smile_close']['value']})
assert rig.pose.bones['PRP-Head']['Sealed Mouth'] is False
assert rig.pose.bones['Properties_Character_Cat']['Quality']==quality
report['protected_after_application'] = protected_state()
report['protected_exact_equal'] = report['protected_after_application']==before
if not report['protected_exact_equal']:
    report['status'] = 'STOP_PROTECTED_STATE_CHANGED_NO_RENDER'
    report['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
    (out/'smile-close-study-receipt.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':report['status'],'protected_before':before,'protected_after':report['protected_after_application']}),flush=True)
    raise SystemExit(0)
# Same original-palette compositor bypass used by the separate baseline builder.
# No material edits or material override changes.
nt = scene.node_tree
render_layer = next(node for node in nt.nodes if node.bl_idname=='CompositorNodeRLayers')
composite = next(node for node in nt.nodes if node.bl_idname=='CompositorNodeComposite')
for link in list(nt.links):
    if link.to_node==composite and link.to_socket==composite.inputs['Image']:
        nt.links.remove(link)
nt.links.new(render_layer.outputs['Image'],composite.inputs['Image'])
helper = bpy.data.objects['HLP-scene_camera_dummy']
rotation_curves = [curve for curve in helper.animation_data.drivers if curve.data_path=='rotation_euler']
assert len(rotation_curves)==3
for curve in rotation_curves:
    curve.mute = True
helper.rotation_mode = 'XYZ'
camera = scene.camera
views = [('smile-close-front',(0,-3,1.50),(0,-.13,.53),1.38,1400),
         ('smile-close-face',(.30,-2,1.13),(0,-.08,.79),.74,1100)]
for name,location,target,scale,resolution in views:
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    expected = camera.matrix_world.to_euler()
    helper.rotation_euler = expected
    helper.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    errors = [abs(helper.rotation_euler[axis]-expected[axis]) for axis in range(3)]
    assert max(errors)<1e-6
    scene.render.filepath = str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    assert protected_state()==before
    report['renders'].append({'name':name,'path':scene.render.filepath,'helper_axis_errors':errors})
assert scene.frame_current==frame_before
assert len(bpy.data.actions)==action_count
assert sum(len(curve.keyframe_points) for action in bpy.data.actions for curve in action.fcurves)==keyframe_count
report['protected_after_render'] = protected_state()
report['status'] = 'INTERNAL_AUTHOR_POSE_REUSE_PENDING_VISUAL_INSPECTION'
for text in bpy.data.texts:
    text.use_module = False
native = out/'artist-smile-close-keyboard-study-native36.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),copy=True)
report['native'] = str(native)
report['native_sha256'] = hashlib.sha256(native.read_bytes()).hexdigest()
report['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
assert report['source_sha256_after']==source_sha
(out/'smile-close-study-receipt.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'status':report['status'],'protected_exact_equal':report['protected_exact_equal'],'native':str(native),'renders':report['renders']}),flush=True)
