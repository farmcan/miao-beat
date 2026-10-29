"""Preserve failed Euler serialization; write identical audited matrices via active quaternion.
No trajectory/pose/mesh/render change. No additional model search or motion variation.
"""
import bpy,json,math,hashlib,shutil
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[2];O=R/'artifacts/miao-reuse-keyboard-v1/single-key-v2';N=json.loads((O/'single-key-numeric-receipt.json').read_text());P=O/'render-receipt.json';r=json.loads(P.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();failed=O/'single-key-v2-native36-serialization-FAIL.blend';shutil.copyfile(r['native'],failed);assert sha(failed)==r['native_sha256'];bpy.ops.wm.open_mainfile(filepath=r['source'],load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];key=bpy.data.objects['Ivory piano key.014'];j=rig.pose.bones['FK-Index1.L'];K0=key.matrix_world.copy();basis0=key.matrix_basis.copy();pivot=Vector(N['fixed_hinge_world']);assert key.rotation_mode=='QUATERNION';assert rig.animation_data.action is None and (not key.animation_data or key.animation_data.action is None);stored=[]
for row in N['frames']:
 j.rotation_euler.x=row['q_radians'];theta=row['key_theta_radians']
 if not theta:key.matrix_basis=basis0
 else:key.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot)@K0
 bpy.context.view_layer.update();stored.append({'frame':row['frame']+1,'joint_x':j.rotation_euler.x,'key_location':list(key.location),'key_quaternion':list(key.rotation_quaternion),'key_world':[list(v) for v in key.matrix_world]})
rig.animation_data_create();key.animation_data_create();ra=bpy.data.actions.new('MiaoSingleKeyV2_Index1L_Once');ka=bpy.data.actions.new('MiaoSingleKeyV2_Key014_Once');rig.animation_data.action=ra;key.animation_data.action=ka
channels=[(ra,'pose.bones["FK-Index1.L"].rotation_euler',0,[v['joint_x'] for v in stored])]+[(ka,'location',i,[v['key_location'][i] for v in stored]) for i in range(3)]+[(ka,'rotation_quaternion',i,[v['key_quaternion'][i] for v in stored]) for i in range(4)]
for action,path,index,values in channels:
 fc=action.fcurves.new(data_path=path,index=index);fc.keyframe_points.add(49)
 for k,v,row in zip(fc.keyframe_points,values,stored):k.co=(row['frame'],v);k.interpolation='LINEAR'
 fc.update()
sc.frame_start=1;sc.frame_end=49;sc.render.fps=60;sc.render.fps_base=1;sc.frame_set(1);bpy.context.view_layer.update();pose=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest();assert pose()==N['source_pose_sha256'];assert len(bpy.data.actions)==29;assert sha(r['source'])==r['source_sha_before'];bpy.ops.wm.save_as_mainfile(filepath=r['native']);fix={'failure_native':str(failed),'failure_sha256':sha(failed),'cause':'source key active rotation_mode QUATERNION; inactive Euler fcurves did not reproduce rigid hinge on native playback. Offline world-matrix renders and collision audit unaffected.','correction':'same49 audited world matrices serialized as3location+4activequaternion channels; FKonly1localX channel; no resampling/new pose/geometry/render','corrected_native_sha256':sha(r['native'])};(O/'native-serialization-correction.json').write_text(json.dumps(fix,indent=2)+'\n');r.update(native_sha256=sha(r['native']),new_fcurves=[(a.name,[(f.data_path,f.array_index,len(f.keyframe_points)) for f in a.fcurves]) for a in [ra,ka]],stored_native_trajectory=stored,native_serialization_correction=fix,native_reopen='pending quaternion replay verification');P.write_text(json.dumps(r,indent=2)+'\n');print('NATIVE_SERIALIZATION_CORRECTED',json.dumps(fix))
