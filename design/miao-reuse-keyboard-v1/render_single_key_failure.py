"""Frozen first failed single-key state: forensic classification and 3 still pairs only.
No repair/search/clip/new action. Source preserved.
"""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'design/miao-reuse-keyboard-v1'));from single_key_geometry import RenderMatchedProxy,record,overlaps
A=R/'artifacts/miao-reuse-keyboard-v1';O=A/'single-key-v1';F=json.load(open(O/'single-key-failure-receipt.json'));S=A/'default-color/keyboard-default-color-native36.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);assert before==F['source_sha256_before'];bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];joint=rig.pose.bones['FK-Index1.L'];key=bpy.data.objects['Ivory piano key.014'];K0=Matrix(F['key_source_world_matrix']);pivot=Vector(F['hinge_world_pivot']);base_other={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b.name!='FK-Index1.L'}
def put(q,theta):
 joint.rotation_euler.x=q;key.matrix_world=K0 if abs(theta)<1e-12 else Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot)@K0;bpy.context.view_layer.update();assert base_other=={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b.name!='FK-Index1.L'}
fail=F['failed_state'];put(fail['joint_x_radians'],fail['key_world_hinge_radians'])
def segment_triangle(p0,p1,a,b,c):
 d=p1-p0;e1=b-a;e2=c-a;h=d.cross(e2);det=e1.dot(h)
 if abs(det)<1e-15:return None
 inv=1/det;s=p0-a;u=s.dot(h)*inv
 if u< -1e-7 or u>1+1e-7:return None
 q=s.cross(e1);v=d.dot(q)*inv
 if v< -1e-7 or u+v>1+1e-7:return None
 t=e2.dot(q)*inv
 if -1e-7<=t<=1+1e-7:return p0+d*t
 return None
with RenderMatchedProxy():
 a=record(key);b=record(bpy.data.objects['Controller chassis']);pairs=a['tree'].overlap(b['tree']);cross=[]
 for ia,ib in pairs:
  va=[a['p'][i] for i in a['t'][ia]];vb=[b['p'][i] for i in b['t'][ib]]
  for tri,other in [(va,vb),(vb,va)]:
   for i in range(3):
    p=segment_triangle(tri[i],tri[(i+1)%3],*other)
    if p is not None:cross.append(p)
 # Independent nearest normal + ray parity for actual key vertices in case.
 inside=[];direction=Vector((1,.314159,.1729)).normalized()
 for i,p in enumerate(a['p']):
  nearest,n,_,distance=b['tree'].find_nearest(p)
  if distance is None or distance<1e-8 or (p-nearest).dot(n)>=-1e-8:continue
  origin=p+direction*1e-8;hits=0
  for count in range(24):
   point,normal,index,dist=b['tree'].ray_cast(origin,direction,3)
   if point is None:break
   hits+=1;origin=point+direction*1e-7
  if hits%2:inside.append({'vertex':i,'point':list(p),'nearest_chassis':list(nearest),'depth_m':distance,'nearest_normal':list(n),'ray_parity_hits':hits})
 forensic={'failed_state':fail['label'],'target_key_vs_chassis_triangle_pairs':len(pairs),'exact_triangle_edge_intersection_points':[list(v) for v in cross],'intersection_bbox':None if not cross else {'min':[min(v[i] for v in cross) for i in range(3)],'max':[max(v[i] for v in cross) for i in range(3)]},'inside_key_vertices':inside,'maximum_key_vertex_chassis_depth_m':max((v['depth_m'] for v in inside),default=0),'hinge_world_pivot':list(pivot),'source_rear_min_y':min((K0@v.co).y for v in key.data.vertices),'interpretation':'read-only frozen-state localization only; no pivot or stroke repair attempted'}
(O/'failed-key-chassis-forensic.json').write_text(json.dumps(forensic,indent=2)+'\n')
prepare=next(s for s in F['solve_trace'] if s['label']=='prepare_lift');contact=next(s for s in reversed(F['solve_trace']) if s['label'].startswith('contact_solve'));states=[('prepare',prepare),('contact',contact),('down-FAIL',fail)];cam=sc.camera;helper=bpy.data.objects['HLP-scene_camera_dummy'];rendered=[];errors=[]
for name,state in states:
 put(state['joint_x_radians'],state['key_world_hinge_radians'])
 for view,loc,target,scale,res in [('front',(0,-3,1.50),(0,-.13,.53),1.38,(1400,1400)),('left-hand',(.40,-.85,.83),(.08,-.28,.35),.32,(1200,1000))]:
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();helper.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();err=max(abs(helper.rotation_euler[i]-cam.matrix_world.to_euler()[i]) for i in range(3));assert err<1e-6;sc.render.filepath=str(O/(name+'-'+view+'.png'));bpy.ops.render.render(write_still=True);rendered.append(sc.render.filepath);errors.append({'state':name,'view':view,'error':err})
 if name in ['contact','down-FAIL']:
  cam.location=(0,-3,1.5);cam.rotation_euler=(Vector((0,-.13,.53))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.38;sc.render.resolution_x=1400;sc.render.resolution_y=1400;bpy.context.view_layer.update();helper.rotation_euler=cam.matrix_world.to_euler();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'-native36.blend')))
assert before==sha(S);r={'status':'FAIL_NEW_MOVING_KEY_CHASSIS_COLLISION_FROZEN','source_sha256_before':before,'source_sha256_after':sha(S),'renders':rendered,'camera_helper_errors':errors,'other_bone_control_bases_unchanged':True,'new_actions':0,'new_keyframes':0,'clip_created':False,'search_or_repair_after_stop':False,'ready_and_end':'approved source remains unchanged; no release/clip is claimed after down STOP','forensic':forensic}
(O/'failed-state-render-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('FROZEN_SINGLE_KEY_FAILURE_IMAGES',json.dumps({'renders':rendered,'chassis_pairs':len(pairs),'max_key_chassis_depth_m':forensic['maximum_key_vertex_chassis_depth_m']}))
