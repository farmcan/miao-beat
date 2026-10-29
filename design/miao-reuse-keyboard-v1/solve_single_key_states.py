"""One bounded FK-X touch solve and one clearance-limited rear-hinge stroke.
No wrist/other finger/rig scale/mesh change. Stops immediately on new collision.
"""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'design/miao-reuse-keyboard-v1'));from single_key_geometry import RenderMatchedProxy,record,measure_hand,overlaps,bounds
A=R/'artifacts/miao-reuse-keyboard-v1';O=A/'single-key-v1';S=A/'default-color/keyboard-default-color-native36.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);rig=bpy.data.objects['RIG-Cat'];joint=rig.pose.bones['FK-Index1.L'];q0=joint.rotation_euler.x;key=bpy.data.objects['Ivory piano key.014'];K0=key.matrix_world.copy();controlled='FK-Index1.L';base_other={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b.name!=controlled};base_lengths={b.name:b.length for b in rig.pose.bones if b.name.startswith(('ORG-UpperArm','ORG-Forearm','DEF-Index'))};propobjects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Ivory piano key','Raised black piano key','Controller chassis','SUPPORT-','Top rotary control','Top control index'))];trace=[];states=[];status='NUMERICAL_BUILDING'
def unchanged():
 assert base_other=={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b.name!=controlled},'Other control basis changed'
 assert max(abs(rig.pose.bones[n].length-v) for n,v in base_lengths.items())<1e-6,'Bone length changed'
def put(q,theta):
 joint.rotation_euler.x=q
 if abs(theta)<1e-12:key.matrix_world=K0
 else:key.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot)@K0
 bpy.context.view_layer.update();unchanged()
def overlap_depth(a,b,box):
 # Finite vertical occupancy of the two original closed solids, sampled fixed XY.
 total=0.;maximum=0.;hits=0;dx=(box[1][0]-box[0][0])/20;dy=(box[1][1]-box[0][1])/24
 for ix in range(20):
  for iy in range(24):
   x=box[0][0]+(ix+.5)*dx;y=box[0][1]+(iy+.5)*dy;intervals=[]
   for r in [a,b]:
    top,_,_,_=r['tree'].ray_cast(Vector((x,y,2)),Vector((0,0,-1)),3);bot,_,_,_=r['tree'].ray_cast(Vector((x,y,-1)),Vector((0,0,1)),3)
    intervals.append(None if top is None or bot is None else (bot.z,top.z))
   if all(v is not None for v in intervals):
    depth=max(0.,min(v[1] for v in intervals)-max(v[0] for v in intervals));total+=depth*dx*dy;maximum=max(maximum,depth);hits+=depth>1e-8
 return {'sample_grid':[20,24],'overlap_volume_estimate_m3':total,'maximum_vertical_overlap_m':maximum,'nonzero_samples':hits}
with RenderMatchedProxy():
 records=[record(o) for o in propobjects];fixed=[r for r in records if r['name']!=key.name];initial_key=record(key);black=next(r for r in fixed if r['name']=='Raised black piano key.010');bb=initial_key['bbox'];pivot=Vector(((bb[0][0]+bb[1][0])/2,bb[0][1],(bb[0][2]+bb[1][2])/2));frontlever=bb[1][1]-pivot.y;inherited=set(overlaps(initial_key['p'],initial_key['t'],fixed));box=([max(initial_key['bbox'][0][i],black['bbox'][0][i]) for i in range(2)],[min(initial_key['bbox'][1][i],black['bbox'][1][i]) for i in range(2)]);baseline_overlap=overlap_depth(initial_key,black,box)
 def evaluate(label,q,theta,full=True):
  put(q,theta);moving=record(key);rr=fixed+[moving];m=measure_hand(rr,full=full);khits=overlaps(moving['p'],moving['t'],fixed);newhits={n:v for n,v in khits.items() if n not in inherited};hidden=overlap_depth(moving,black,box)
  safe=not m.get('whole_hands_component_triangle_intersections',{}) and not newhits and hidden['overlap_volume_estimate_m3']<=baseline_overlap['overlap_volume_estimate_m3']+1e-11
  row={'label':label,'joint_x_radians':q,'joint_delta_degrees':math.degrees(q-q0),'key_world_hinge_radians':theta,'key_front_travel_m':frontlever*math.sin(-theta),'hand':m,'target_key_component_intersections':khits,'inherited_source_overlap_names':sorted(inherited),'new_key_component_intersections':newhits,'hidden_source_key_overlap':hidden,'safe_no_new_intersections':safe};trace.append(row)
  (O/'single-key-progress.json').write_text(json.dumps({'source':str(S),'source_sha256':before,'base_q':q0,'pivot':list(pivot),'K0':[list(v) for v in K0],'trace':trace},indent=2)+'\n')
  print('STATE',json.dumps({'label':label,'qdeg':math.degrees(q),'theta':theta,'target_gap':m.get('target'),'hand_hits':m.get('whole_hands_component_triangle_intersections'),'new_key_hits':newhits,'inherited_overlap':hidden}),flush=True)
  if not safe:
   failure={'status':'STOP_NO_FURTHER_POSE_SEARCH','source':str(S),'source_sha256_before':before,'source_sha256_after':sha(S),'failed_state':row,'base_joint_x_radians':q0,'hinge_world_pivot':list(pivot),'key_source_world_matrix':[list(v) for v in K0],'solve_trace':trace,'inherited_key_overlap_baseline':baseline_overlap,'inherited_overlap_names':sorted(inherited),'new_actions':0,'clip':False,'source_geometry_modified':False}
   (O/'single-key-failure-receipt.json').write_text(json.dumps(failure,indent=2)+'\n')
   raise RuntimeError('STOP_NEW_FINITE_COLLISION_'+label)
  return row
 ready=evaluate('ready',q0,0);prep=evaluate('prepare_lift',q0-math.radians(3),0)
 def solve(label,theta,qstart):
  q=qstart;last=None
  for it in range(10):
   row=evaluate(label+'_solve_'+str(it),q,theta);gap=row['hand']['target']['gap_m'];res=gap-.00005
   if abs(res)<.000015:return q,row
   derivative=-.040 # metres / rad initial real calibration ~-.040; updated secant below
   if last is not None and abs(q-last[0])>1e-7:derivative=(gap-last[1])/(q-last[0])
   if derivative>=-.001:raise RuntimeError('STOP_WRONG_LOCAL_DIRECTION')
   step=max(-math.radians(1.25),min(math.radians(1.25),-res/derivative));last=(q,gap);q+=step
   if not q0-math.radians(4)<=q<=q0+math.radians(8):raise RuntimeError('STOP_JOINT_BOUND')
  raise RuntimeError('STOP_UNSOLVED_SKIN_TOUCH')
 contact_q,contact=solve('contact',0,q0+math.radians(3.9));neighbor=contact['hand']['other_key_minimum_projected_gap_m'];fingerlever=contact['hand']['target']['skin_point'][1]-pivot.y
 # Preserve at least half measured neighbor clearance; never force 1–2mm.
 travel=min(.0004,neighbor*.5*frontlever/max(.01,fingerlever));theta=-math.asin(travel/frontlever);down_q,down=solve('down',theta,contact_q+math.radians(.45))
 release=evaluate('release_contact',contact_q,0);end=evaluate('end_return',q0,0);states=[ready,prep,contact,down,release,end];put(q0,0);status='SAFE_FINITE_STATES_NOT_MOTION_ACCEPTED'
report={'status':status,'source':str(S),'source_sha_before':before,'source_sha_after':sha(S),'source_pose_sha256':'4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be','method':'render matched independent proxy; show_render/render_levels2/IsViewportFalse; direct RENDER depsgraph unavailable','controlled_bone':'FK-Index1.L','other_bones_wrist_right_head_body_unchanged':True,'base_joint_x_radians':q0,'base_joint_x_degrees':math.degrees(q0),'prepare_joint_x_radians':q0-math.radians(3),'contact_joint_x_radians':contact_q,'down_joint_x_radians':down_q,'hinge_world_pivot':list(pivot),'key_source_world_matrix':[list(v) for v in K0],'key_front_lever_m':frontlever,'down_hinge_radians':theta,'down_front_travel_m':travel,'approved_requested_limit_m':.0004,'state_sequence':states,'solve_trace':trace,'inherited_key_overlap_baseline':baseline_overlap,'inherited_key_overlap_names':sorted(inherited),'baseline_mechanical_limitation':'Original rectangular white014 overlaps black010 rear region. Existing hidden overlap separately recorded; down must reduce it, no new external intersection permitted. Source is not complete mechanical piano.','new_actions_created':0,'native_saved':False,'clip_created':False,'visual_motion_gate':'not yet rendered or accepted'}
assert before==sha(S);(O/'single-key-states-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('SINGLE_KEY_FINITE_STATES',json.dumps({k:report[k] for k in ['status','base_joint_x_degrees','contact_joint_x_radians','down_joint_x_radians','hinge_world_pivot','down_front_travel_m','inherited_key_overlap_baseline']}))
