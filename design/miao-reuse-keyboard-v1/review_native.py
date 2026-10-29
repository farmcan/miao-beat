"""Portable read-only reopen/audit and optional same-pose review renders.

Run only in official Blender 3.6.23 with factory startup and scripts disabled.
Does not save/overwrite the accepted native, set frames, assign actions or run
embedded Python. Camera-helper synchronization is explicit before each render.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--native',type=Path,default=ROOT/'artifacts/miao-reuse-keyboard-v1/default-color/keyboard-default-color-native36.blend')
parser.add_argument('--out',type=Path,default=ROOT/'output/review')
parser.add_argument('--render',nargs='*',choices=['front','three-quarter','face','left-hand','right-hand','hands-top'],default=[])
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert bpy.app.version==(3,6,23),'Use official Blender 3.6.23; do not resave in 5.2'
args.out.mkdir(parents=True,exist_ok=True)
source_sha = hashlib.sha256(args.native.read_bytes()).hexdigest()
assert source_sha=='3def58d233e39d1a97c67bc6b46edf7b0c882ba86e1b9584f23af42945f6e38b'
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
bpy.ops.wm.open_mainfile(filepath=str(args.native.resolve()),load_ui=False,use_scripts=False)
scene=bpy.context.scene
rig=bpy.data.objects['RIG-Cat']
pose=lambda:hashlib.sha256(json.dumps([(bone.name,[list(row) for row in bone.matrix_basis]) for bone in rig.pose.bones]).encode()).hexdigest()
expected_pose='4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be'
assert pose()==expected_pose
images=[]
missing=[]
for image in bpy.data.images:
    packed=bool(image.packed_file) or bool(getattr(image,'packed_files',[]))
    record={'name':image.name,'source':image.source,'packed':packed,'size':list(image.size)}
    images.append(record)
    if image.source=='FILE' and not packed:
        missing.append('unpacked_image:'+image.name)
for library in bpy.data.libraries:
    missing.append('external_library:'+Path(library.filepath).name)
for collection_name in ['movieclips','sounds','fonts']:
    for item in getattr(bpy.data,collection_name):
        filepath=getattr(item,'filepath','')
        if filepath and filepath not in ['<builtin>','<built-in>'] and not getattr(item,'packed_file',None):
            missing.append(collection_name+':'+Path(filepath).name)
assert not missing,missing
assert rig.pose.bones['Properties_Character_Cat']['Quality']==1
assert not scene.render.use_simplify
helper=bpy.data.objects['HLP-scene_camera_dummy']
rotation_drivers=[curve for curve in helper.animation_data.drivers if curve.data_path=='rotation_euler']
assert len(rotation_drivers)==3 and all(curve.mute for curve in rotation_drivers)
report={'status':'READ_ONLY_NATIVE_REOPEN_PASS','blender':bpy.app.version_string,'native_filename':args.native.name,
        'native_sha256':source_sha,'pose_sha256':pose(),'images':images,'missing_dependencies':missing,
        'linked_libraries':len(bpy.data.libraries),'Quality':1,'use_simplify':False,
        'actions_total':len(bpy.data.actions),'embedded_texts':[{'name':text.name,'bytes':len(text.as_string().encode()),'sha256':hashlib.sha256(text.as_string().encode()).hexdigest()} for text in bpy.data.texts],
        'autoexec_enabled':bpy.context.preferences.filepaths.use_scripts_auto_execute,'upstream_scripts_executed':[],
        'native_saves':0,'frame_set_calls':0,'new_actions':0,'new_keyframes':0,'renders':[]}
views={'front':((0,-3,1.5),(0,-.13,.53),1.38,(1400,1400)),
       'three-quarter':((.95,-2.5,1.3),(0,-.13,.53),1.38,(1400,1400)),
       'face':((.30,-2,1.13),(0,-.08,.79),.74,(1100,1100)),
       'left-hand':((.40,-.85,.83),(.08,-.28,.35),.32,(1200,1000)),
       'right-hand':((-.40,-.85,.83),(-.08,-.28,.35),.32,(1200,1000)),
       'hands-top':((0,-.35,1.25),(0,-.30,.33),.48,(1400,1000))}
for name in args.render:
    location,target,scale,resolution=views[name]
    camera=scene.camera
    camera.location=location
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'
    camera.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=resolution
    scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    expected=camera.matrix_world.to_euler()
    helper.rotation_mode='XYZ'
    helper.rotation_euler=expected
    helper.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    errors=[abs(helper.rotation_euler[index]-expected[index]) for index in range(3)]
    assert max(errors)<1e-6
    scene.render.filepath=str(args.out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    assert pose()==expected_pose
    report['renders'].append({'view':name,'file':name+'.png','helper_axis_errors':errors})
assert hashlib.sha256(args.native.read_bytes()).hexdigest()==source_sha
assert pose()==expected_pose
(args.out/'native-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'images':len(images),'missing':missing,'native_saves':0,'renders':len(report['renders'])}),flush=True)
