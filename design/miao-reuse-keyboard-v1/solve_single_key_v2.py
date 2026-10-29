"""One approved1.5mm key stroke; measured render2 skin and one native FK axis.
Source immutable. Stops on confirmed new external collisions; no pose search.
"""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent));from single_key_geometry import RenderMatchedProxy,geometry,record,overlaps,bounds
A=R/'artifacts/miao-reuse-keyboard-v1';O=A/'single-key-v2';O.mkdir(exist_ok=True);S=A/'v2-keygroup-lift-color/keygroup-lift-color-native36.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);assert before=='ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6';bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];joint=rig.pose.bones['FK-Index1.L'];q0=joint.rotation_euler.x;key=bpy.data.objects['Ivory piano key.014'];K0=key.matrix_world.copy();other={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b.name!=joint.name};world={o.name:[list(v) for v in o.matrix_world] for o in sc.objects if o!=key};ph=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest();pose0=ph();assert pose0=='6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b';trace=[];frames=[];contact_q=None;status='SOLVING'
def put(q,theta):
 joint.rotation_euler.x=q;key.matrix_world=K0 if abs(theta)<1e-12 else Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot)@K0;bpy.context.view_layer.update();assert other=={b.name:[list(v) for v in b.matrix_basis] for b in rig.pose.bones if b.name!=joint.name}
def persist():
 (O/'numeric-progress.json').write_text(json.dumps({'status':status,'source':str(S),'source_sha256':before,'source_pose_sha256':pose0,'base_joint_x_radians':q0,'pivot':list(pivot),'K0':[list(v) for v in K0],'trace':trace,'frames':frames},indent=2)+'\n')
def stop(reason,row):
 global status
 status='STOP_CONFIRMED_COLLISION_OR_BOUND';persist();(O/'failure-receipt.json').write_text(json.dumps({'status':status,'reason':reason,'failed':row,'source_sha_before':before,'source_sha_after':sha(S),'new_actions':0,'frames_rendered':0},indent=2)+'\n');raise RuntimeError(reason)
def segtri(p0,p1,a,b,c):
 d=p1-p0;e1=b-a;e2=c-a;h=d.cross(e2);det=e1.dot(h)
 if abs(det)<1e-15:return None
 s=p0-a;u=s.dot(h)/det
 if not -1e-7<=u<=1+1e-7:return None
 q=s.cross(e1);v=d.dot(q)/det
 if v< -1e-7 or u+v>1+1e-7:return None
 f=e2.dot(q)/det
 return p0+d*f if -1e-7<=f<=1+1e-7 else None
def crosses(a,b,pairs):
 pts=[]
 for ia,ib in pairs:
  va=[a['p'][i] for i in a['t'][ia]];vb=[b['p'][i] for i in b['t'][ib]]
  for tri,ot in [(va,vb),(vb,va)]:
   for i in range(3):
    p=segtri(tri[i],tri[(i+1)%3],*ot)
    if p is not None:pts.append(p)
 return pts
dirs=[Vector(v).normalized() for v in [(1,.314159,.1729),(-.247,1,.413),(.271,-.381,1)]]
def member(r,p):
 _,_,_,distance=r['tree'].find_nearest(p)
 if distance is not None and distance<5e-7:return 'boundary',distance,[]
 votes=[]
 for d in dirs:
  origin=p+d*1e-8;count=0
  for k in range(30):
   hit,_,_,_=r['tree'].ray_cast(origin,d,3)
   if hit is None:break
   count+=1;origin=hit+d*1e-7
  votes.append(count%2)
 return ('inside' if all(votes) else 'outside' if not any(votes) else 'unknown'),distance,votes
with RenderMatchedProxy():
 props=[o for o in sc.objects if o.type=='MESH' and o.name.startswith(('Ivory piano key','Raised black piano key','Controller chassis','SUPPORT-','Top rotary control','Top control index'))];fixed=[record(o) for o in props if o!=key];initial=record(key);bb=initial['bbox'];pivot=Vector(((bb[0][0]+bb[1][0])/2,bb[0][1],(bb[0][2]+bb[1][2])/2));lever=bb[1][1]-pivot.y;theta_down=-math.asin(.0015/lever);black=next(r for r in fixed if r['name']=='Raised black piano key.010');basepairs=set(initial['tree'].overlap(black['tree']));assert len(basepairs)==59;assert not {n:v for n,v in overlaps(initial['p'],initial['t'],fixed).items() if n!=black['name']};hand=bpy.data.objects['GEO-hands'];gi=hand.vertex_groups['DEF-Index2.L'].index;sleeves=record(bpy.data.objects['GEO-arms']);assert not overlaps(sleeves['p'],sleeves['t'],fixed+[initial]);regioncache={};keycache={}
 def keydata(theta):
  ident=round(theta,12)
  if ident in keycache:return keycache[ident]
  moving=record(key);hits=overlaps(moving['p'],moving['t'],fixed);pairs=set(moving['tree'].overlap(black['tree']));new={n:v for n,v in hits.items() if n!=black['name']};pts=crosses(moving,black,pairs)
  for v in moving['p']:
   if member(black,v)[0]=='inside':pts.append(v)
  for v in black['p']:
   if member(moving,v)[0]=='inside':pts.append(v)
  unique={tuple(round(c,8) for c in p):p for p in pts};counts={'inside':0,'boundary':0,'outside':0,'unknown':0};unknown=[]
  for k,p in unique.items():
   if k not in regioncache:regioncache[k]=member(initial,p)
   state,dist,votes=regioncache[k];counts[state]+=1
   if state in ['outside','unknown']:unknown.append({'point':list(p),'membership':state,'distance_m':dist,'votes':votes})
  classification={'exact_pairs':[list(p) for p in sorted(pairs)],'added_pairs':[list(p) for p in sorted(pairs-basepairs)],'retired_pairs':[list(p) for p in sorted(basepairs-pairs)],'source_allowed_region_membership':counts,'outside_unknown_points':unknown,'scope':'actual finite current intersection samples in original white solid; no whole-component exemption; near-boundary/continuous volume unknown retained'}
  if new or counts['outside']:stop('NEW_KEY_EXTERNAL_OR_CONFIRMED_SOURCE_REGION_EXTENSION',{'key_hits':hits,'classification':classification})
  keycache[ident]=(moving,hits,classification);return keycache[ident]
 def evaluate(label,q,theta,keep=True):
  put(q,theta);moving,khits,classification=keydata(theta);p,t,w=geometry(hand);ids=[i for i,v in enumerate(w) if v.get(gi,0)>.6];samples=[];neighbors={};rr=fixed+[moving]
  for rec in rr:
   if not rec['name'].startswith(('Ivory piano key','Raised black piano key')):continue
   gg=[]
   for i in ids:
    hit,n,_,_=rec['tree'].ray_cast(Vector((p[i].x,p[i].y,2)),Vector((0,0,-1)),3)
    if hit is not None and n.z>.9:gg.append({'gap_m':p[i].z-hit.z,'skin_vertex':i,'skin_point':list(p[i]),'surface_point':list(hit),'normal':list(n)})
   if gg:
    val=min(gg,key=lambda v:v['gap_m'])
    if rec['name']==key.name:samples.append(val)
    else:neighbors[rec['name']]=val['gap_m']
  if not samples:stop('NO_FINITE_TARGET_PROJECTION',{'q':q,'theta':theta})
  pad=min(samples,key=lambda v:v['gap_m']);hh=overlaps(p,t,rr);ah=overlaps(sleeves['p'],sleeves['t'],rr);row={'label':label,'q_radians':q,'q_degrees':math.degrees(q),'joint_delta_degrees':math.degrees(q-q0),'key_theta_radians':theta,'key_front_travel_m':lever*math.sin(-theta),'target_pad':pad,'neighbor_min_projected_gap_m':min(neighbors.values()) if neighbors else None,'neighbor_gaps':neighbors,'whole_hands_external_triangle_intersections':hh,'sleeves_external_triangle_intersections':ah,'key_component_triangle_intersections':khits,'inherited_black010_region':classification,'skin_vertex_count':len(p),'skin_triangles':len(t),'pad_count':len(ids)}
  if hh or ah or pad['gap_m']<0:stop('NEW_HAND_OR_SLEEVE_EXTERNAL_COLLISION',row)
  if keep:trace.append(row);persist()
  return row
 def solve(theta,start,label):
  q=start;last=None
  for i in range(16):
   row=evaluate(label+'-solve'+str(i),q,theta);gap=row['target_pad']['gap_m'];res=gap-.00005
   if abs(res)<=.000015:return q,row
   derivative=-.04
   if last and abs(q-last[0])>1e-8:derivative=(gap-last[1])/(q-last[0])
   if derivative>=-.001:stop('NON_MONOTONIC_NATIVE_FK',row)
   step=max(-math.radians(1.25),min(math.radians(1.25),-.85*res/derivative));last=(q,gap);q+=step
   if not q0<=q<=q0+math.radians(9):stop('NATIVE_FK_BOUND',row)
  stop('PAD_TOUCH_UNSOLVED',row)
 ready=evaluate('ready',q0,0);contact_q,contact=solve(0,q0,'contact');down_q,down=solve(theta_down,contact_q,'down');print('KEY_STATES',json.dumps({'contact_deg':math.degrees(contact_q),'down_deg':math.degrees(down_q),'contact_gap':contact['target_pad']['gap_m'],'down_gap':down['target_pad']['gap_m'],'down_neighbor_gap':down['neighbor_min_projected_gap_m'],'pivot':list(pivot)}),flush=True)
 def smooth(v):return v*v*(3-2*v)
 cache={(round(0.,12),round(q0,12)):ready}
 for f in range(49):
  theta=0.;q=q0;needsolve=False
  if 12<f<14:q=q0+(contact_q-q0)*smooth((f-12)/2)
  elif 14<=f<=17:theta=theta_down*smooth((f-14)/3);needsolve=True
  elif 17<f<=19:theta=theta_down;needsolve=True
  elif 19<f<=25:theta=theta_down*(1-smooth((f-19)/6));needsolve=True
  elif 25<f<30:q=contact_q+(q0-contact_q)*smooth((f-25)/5)
  if needsolve:
   if abs(theta)<1e-12:q=contact_q
   elif abs(theta-theta_down)<1e-12:q=down_q
   else:q,_=solve(theta,contact_q,'frame'+str(f))
  ident=(round(theta,12),round(q,12))
  if ident in cache:row=cache[ident]
  else:row=evaluate('frame'+str(f),q,theta);cache[ident]=row
  frames.append({'frame':f,'time_seconds':f/60,'q_radians':q,'key_theta_radians':theta,'metrics':row});persist()
 put(q0,0);assert ph()==pose0;assert [list(v) for v in key.matrix_world]==[list(v) for v in K0];status='SAFE_ALL49_FINITE_FRAMES_PENDING_VISUAL';persist()
assert world=={o.name:[list(v) for v in o.matrix_world] for o in sc.objects if o!=key};assert before==sha(S);receipt={'status':status,'source':str(S),'source_sha_before':before,'source_sha_after':sha(S),'source_pose_sha256':pose0,'base_joint_x_radians':q0,'contact_joint_x_radians':contact_q,'down_joint_x_radians':down_q,'key_source_world_matrix':[list(v) for v in K0],'fixed_hinge_world':list(pivot),'key_front_lever_m':lever,'front_maximum_m':.0015,'key_down_radians':theta_down,'fps':60,'duration_seconds':.8,'frames':frames,'critical_frames':{'ready':0,'contact':14,'down':17,'release':25,'end':30},'schedule':'0-.2s ready; .2-.2333 approach; .2333-.2833 1.5mm down; hold to.3167; key release to.4167; finger return to.5; still to.8','all_other_bones_and_world_matrices_unchanged':True,'return_pose_hash_exact':pose0,'render_proxy':'independent matching show_render/render_levels2/IsViewportFalse; direct RENDER depsgraph unavailable','original_white_black_overlap':'specific exact pairs and finite source-region membership per frame, unknown retained, not full mechanical model','continuous_collision_scope':'all49 actual production states plus numerical solve states tested; not interval continuous solid proof','native_or_render_started':False,'new_actions':0};(O/'single-key-numeric-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SINGLE_KEY_V2_NUMERIC_READY',json.dumps({k:receipt[k] for k in ['status','contact_joint_x_radians','down_joint_x_radians','front_maximum_m','return_pose_hash_exact']}),flush=True)
