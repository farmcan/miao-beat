"""Render the single approved audited trajectory, then store only its2 native actions."""
import bpy,json,hashlib,array,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];A=R/'artifacts/miao-reuse-keyboard-v1';O=A/'single-key-v2';N=json.loads((O/'single-key-numeric-receipt.json').read_text());S=Path(N['source']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(S)==N['source_sha_before'];assert N['status']=='SAFE_ALL49_FINITE_FRAMES_PENDING_VISUAL';bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];joint=rig.pose.bones['FK-Index1.L'];key=bpy.data.objects['Ivory piano key.014'];K0=key.matrix_world.copy();basis0=key.matrix_basis.copy();pivot=Vector(N['fixed_hinge_world']);q0=joint.rotation_euler.x;others={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b!=joint};actions0=set(a.name for a in bpy.data.actions);oldactions={'rig':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,'key':key.animation_data.action.name if key.animation_data and key.animation_data.action else None};pose=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest()
def meshhash():
 h=hashlib.sha256()
 for o in sorted((o for o in sc.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());h.update(array.array('f',[c for v in o.data.vertices for c in v.co]).tobytes());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([m.name if m else None for m in o.data.materials]).encode())
 return h.hexdigest()
mb=meshhash();world0={o.name:[list(v) for v in o.matrix_world] for o in sc.objects if o!=key and o.name not in {sc.camera.name,'HLP-scene_camera_dummy'}}
def put(row):
 joint.rotation_euler.x=row['q_radians'];theta=row['key_theta_radians']
 if abs(theta)<1e-12:key.matrix_basis=basis0
 else:key.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot)@K0
 bpy.context.view_layer.update();assert others=={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b!=joint}
cam=sc.camera;helper=bpy.data.objects['HLP-scene_camera_dummy'];errors=[];renders=[];framesdir=O/'frames';framesdir.mkdir(exist_ok=True)
def view(name,loc,aim,scale,res,path):
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();helper.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();err=max(abs(helper.rotation_euler[i]-cam.matrix_world.to_euler()[i]) for i in range(3));assert err==0;errors.append({'view':name,'max_error':err});sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);renders.append(str(path))
# Every production frame is the original full connected scene. No camera gesture.
for row in N['frames']:
 f=row['frame'];put(row);view('full-frame-'+str(f),(0,-3,1.5),(0,-.13,.53),1.38,(1400,1400),framesdir/f'{f:04}.png');print('RENDERED_FULL',f,flush=True)
for label,f in N['critical_frames'].items():
 put(N['frames'][f]);view(label+'-left-hand',(.40,-.85,.83),(.08,-.28,.352),.32,(1200,1000),O/(label+'-left-hand.png'))
put(N['frames'][17]);view('down-three-quarter',(.95,-2.5,1.3),(0,-.13,.53),1.38,(1400,1400),O/'down-three-quarter.png')
# Only audited sampled trajectory: one FK local-X channel; target rigid key loc/rot.
assert key.rotation_mode=='QUATERNION';stored=[]
for row in N['frames']:
 put(row);stored.append({'frame':row['frame']+1,'joint_x':joint.rotation_euler.x,'key_location':list(key.location),'key_quaternion':list(key.rotation_quaternion),'key_world':[list(v) for v in key.matrix_world]})
rig.animation_data_create();key.animation_data_create();ra=bpy.data.actions.new('MiaoSingleKeyV2_Index1L_Once');ka=bpy.data.actions.new('MiaoSingleKeyV2_Key014_Once');rig.animation_data.action=ra;key.animation_data.action=ka
channels=[(ra,'pose.bones["FK-Index1.L"].rotation_euler',0,[v['joint_x'] for v in stored])]+[(ka,'location',i,[v['key_location'][i] for v in stored]) for i in range(3)]+[(ka,'rotation_quaternion',i,[v['key_quaternion'][i] for v in stored]) for i in range(4)]
for action,path,index,values in channels:
 fc=action.fcurves.new(data_path=path,index=index);fc.keyframe_points.add(49)
 for k,v,row in zip(fc.keyframe_points,values,stored):k.co=(row['frame'],v);k.interpolation='LINEAR'
 fc.update()
sc.render.fps=60;sc.render.fps_base=1;sc.frame_start=1;sc.frame_end=49;sc.frame_set(1);put(N['frames'][0]);cam.location=(0,-3,1.5);cam.rotation_euler=(Vector((0,-.13,.53))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.38;sc.render.resolution_x=sc.render.resolution_y=1400;helper.rotation_euler=cam.matrix_world.to_euler();bpy.context.view_layer.update();assert pose()==N['source_pose_sha256'];assert meshhash()==mb;assert world0=={o.name:[list(v) for v in o.matrix_world] for o in sc.objects if o!=key and o.name not in {sc.camera.name,'HLP-scene_camera_dummy'}};assert sha(S)==N['source_sha_before'];assert len(bpy.data.actions)==len(actions0)+2
native=O/'single-key-v2-native36.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));r={'status':'RENDERED_PENDING_ACTUAL_VIEW_AND_INDEPENDENT_MOTION','source':str(S),'source_sha_before':N['source_sha_before'],'source_sha_after':sha(S),'native':str(native),'native_sha256':sha(native),'pose_baseline_and_end_sha256':N['source_pose_sha256'],'all_mesh_material_slots_hash_before':mb,'all_mesh_material_slots_hash_after':meshhash(),'other_bones_wrist_right_hand_head_body_unchanged':True,'other_scene_world_matrices_unchanged':True,'camera_helper_errors':errors,'renders':renders,'full_production_frames':49,'fps':60,'sample_times_seconds':[row['time_seconds'] for row in N['frames']],'encoded_duration_note':'49samples0–.8s encoded60fps=.816667s; no time scaling for primary','new_actions':2,'new_action_names':[ra.name,ka.name],'old_active_actions':oldactions,'new_fcurves':[(a.name,[(f.data_path,f.array_index,len(f.keyframe_points)) for f in a.fcurves]) for a in [ra,ka]],'stored_native_trajectory':stored,'new_mesh_geometry':False,'new_materials':False,'no_press_expansion_or_head_motion':True,'visual_limits':'full-scene finger/key movement small; diagnostics and optional3x playback cannot prove real-size response accepted','native_reopen':'pending'};(O/'render-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('RENDER_SINGLE_V2_READY',json.dumps({'native':str(native),'sha256':sha(native),'new_actions':2}),flush=True)
