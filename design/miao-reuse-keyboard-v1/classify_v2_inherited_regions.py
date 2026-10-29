"""Exact same A/B inputs: classify original cuff seam and inherited white/black region.
No extra placement, mesh operation, render, native save or animation.
"""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent));from single_key_geometry import RenderMatchedProxy,geometry,record,bounds
O=R/'artifacts/miao-reuse-keyboard-v1/v2-static-probe';S=R/'artifacts/miao-reuse-keyboard-v1/default-color/keyboard-default-color-native36.blend';B=json.load(open(O/'B-fixed-sweep-and-well.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);rig=bpy.data.objects['RIG-Cat'];control=rig.pose.bones['IK-MSTR-Hand.L'];basis=control.matrix_basis.copy()
def segtri(p0,p1,a,b,c):
 d=p1-p0;e1=b-a;e2=c-a;h=d.cross(e2);det=e1.dot(h)
 if abs(det)<1e-15:return None
 inv=1/det;s=p0-a;u=s.dot(h)*inv
 if u< -1e-7 or u>1+1e-7:return None
 q=s.cross(e1);v=d.dot(q)*inv
 if v< -1e-7 or u+v>1+1e-7:return None
 t=e2.dot(q)*inv
 return p0+d*t if -1e-7<=t<=1+1e-7 else None
def crosses(a,b,pairs):
 pts=[]
 for ia,ib in pairs:
  va=[a['p'][i] for i in a['t'][ia]];vb=[b['p'][i] for i in b['t'][ib]]
  for tri,other in [(va,vb),(vb,va)]:
   for i in range(3):
    p=segtri(tri[i],tri[(i+1)%3],*other)
    if p is not None:pts.append(p)
 return pts
def localbbox(pts,M):return None if not pts else bounds([M@p for p in pts])
with RenderMatchedProxy():
 hand=bpy.data.objects['GEO-hands'];arms=bpy.data.objects['GEO-arms'];h0=record(hand);a0=record(arms);pairs0=set(h0['tree'].overlap(a0['tree']));inv0=(rig.matrix_world@rig.pose.bones['ORG-Hand.L'].matrix).inverted();left0=[pair for pair in pairs0 if sum(h0['p'][i].x for i in h0['t'][pair[0]])>0];basecross=crosses(h0,a0,left0);W=(rig.matrix_world@control.matrix).copy();W.translation.x-=.005962789;control.matrix=rig.matrix_world.inverted()@W;bpy.context.view_layer.update();h1=record(hand);a1=record(arms);pairs1=set(h1['tree'].overlap(a1['tree']));added=pairs1-pairs0;retired=pairs0-pairs1;inv1=(rig.matrix_world@rig.pose.bones['ORG-Hand.L'].matrix).inverted();newcross=crosses(h1,a1,added);p,t,weights=geometry(hand);groups={g.index:g.name for g in hand.vertex_groups};details=[]
 for ih,ia in sorted(added):
  w={}
  for vi in t[ih]:
   for gi,value in weights[vi].items():w[groups[gi]]=w.get(groups[gi],0)+value/3
  details.append({'hand_triangle':ih,'arm_triangle':ia,'hand_dominant_groups':sorted(w.items(),key=lambda v:v[1],reverse=True)[:3],'wrist_local_hand_triangle_center':list(inv1@((p[t[ih][0]]+p[t[ih][1]]+p[t[ih][2]])/3))})
 cuff={'baseline_pairs':len(pairs0),'after_pairs':len(pairs1),'added_pair_count':len(added),'retired_pair_count':len(retired),'baseline_left_seam_intersection_bbox_in_wrist_frame':localbbox(basecross,inv0),'added_intersection_bbox_in_wrist_frame':localbbox(newcross,inv1),'added_pairs':details,'new_hand_triangle_ids_outside_original_seam_pool':sorted({p[0] for p in pairs1}-{p[0] for p in pairs0}),'classification':'pair migration evaluated in native wrist frame; original embedded hand/cuff seam retained, no separation edits; static visual seam verdict pending new gate'};control.matrix_basis=basis;bpy.context.view_layer.update()
# Original mesh finite membership, not invalid convex halfspaces.
source=record(bpy.data.objects['Ivory piano key.014']);black=record(bpy.data.objects['Raised black piano key.010']);pivot=Vector(B['fixed_hinge_world']);cache={};dirs=[Vector(v).normalized() for v in [(1,.314159,.1729),(-.247,1,.413),(.271,-.381,1)]]
def membership(r,p):
 near,_,_,distance=r['tree'].find_nearest(p)
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
rows=[]
for row in B['sweep_samples']:
 theta=math.radians(row['hinge_angle_degrees']);M=Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot);p=[M@v for v in source['p']];cur={'p':p,'t':source['t'],'tree':BVHTree.FromPolygons(p,source['t'],all_triangles=True)};pairs=cur['tree'].overlap(black['tree']);pts=crosses(cur,black,pairs)
 for v in p:
  if membership(black,v)[0]=='inside':pts.append(v)
 for v in black['p']:
  if membership(cur,v)[0]=='inside':pts.append(v)
 unique={tuple(round(c,8) for c in v):v for v in pts};counts={'inside':0,'boundary':0,'outside':0,'unknown':0};out=[]
 for k,v in unique.items():
  if k not in cache:cache[k]=membership(source,v)
  state,dist,votes=cache[k];counts[state]+=1
  if state in ['outside','unknown']:out.append({'point':list(v),'state':state,'nearest_old_white_distance_m':dist,'ray_votes':votes})
 rows.append({'fraction':row['fraction'],'specific_added_pair_ids':row['black010_added_pair_ids'],'specific_retired_pair_ids':row['black010_retired_pair_ids'],'current_overlap_boundary_and_contained_vertex_samples':len(unique),'membership_in_original_white_mesh':counts,'outside_or_unknown_points':out,'scope':'actual finite current white/black intersection samples checked against original white solid; no whole-black exemption; continuous volume inclusion not certified'})
result={'source_sha_before':before,'source_sha_after':sha(S),'A_cuff_classification':cuff,'B_inherited_region_finite_membership':rows,'B_old_halfspace_attempt_invalid':{'source_key_max_support_plane_error_m':B['source_white_convex_max_error_m'],'reason':'source mesh not numerically convex to0.5um; even baseline gave false outside; do not classify those halfspace samples as confirmed new overlap'},'unknown':['no new static render has been made; cuff seam appearance unreviewed','finite intersection sampling is not complete continuous volume proof','full1.5mm angular path pair snapshots five states; continuous component intersection unknown between samples'],'no_boolean_no_native_save_no_render_no_actions':True};assert before==sha(S);(O/'inherited-region-classification.json').write_text(json.dumps(result,indent=2)+'\n');print('INHERITED_REGION_CLASSIFICATION',json.dumps({'cuff_counts':[len(pairs0),len(pairs1),len(added),len(retired)],'cuff_local_bbox':cuff['added_intersection_bbox_in_wrist_frame'],'black_membership':[{k:r[k] for k in ['fraction','membership_in_original_white_mesh','specific_added_pair_ids']} for r in rows]}))
