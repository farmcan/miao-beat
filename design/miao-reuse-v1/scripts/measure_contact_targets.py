"""One read-only enlarged-guitar fit, exact body envelope, rig-frame wrist targets.
No object/pose assignments, no .blend saves, no render calls.
"""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve();base=Path('artifacts/miao-reuse-v1')
meas=json.loads((base/'contact-proposal/read-only-contact-measurements.json').read_text());diag=json.loads((base/'static-hold/static-hold-readonly-technical-diagnostic.json').read_text())
sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();g=bpy.data.objects['REUSE-CLASSIC-GUITAR'];rig=bpy.data.objects['RIG-Cat'];pts=[v.co.copy() for v in g.data.vertices];g.data.calc_loop_triangles();tris=[tuple(t.vertices) for t in g.data.loop_triangles]
def bb(ps):
 lo=[min(p[k] for p in ps) for k in range(3)];hi=[max(p[k] for p in ps) for k in range(3)];return {'min':lo,'max':hi,'dimensions':[hi[k]-lo[k] for k in range(3)]}
def scene_tree(names):
 vs=[];ts=[]
 for name in names:
  o=bpy.data.objects.get(name)
  if o is None:continue
  e=o.evaluated_get(dg);mesh=e.to_mesh();mesh.calc_loop_triangles();ofs=len(vs);vs += [e.matrix_world@v.co for v in mesh.vertices];ts += [tuple(i+ofs for i in t.vertices) for t in mesh.loop_triangles];e.to_mesh_clear()
 return BVHTree.FromPolygons(vs,ts,all_triangles=True)
body_names=['GEO-body','GEO-pockets','GEO-zipper_line','GEO-zipper_handle','GEO-collar'];body=scene_tree(body_names);head=scene_tree(['GEO-head'])
# Use actual source string islands. UV/normal splits create 24 narrow pieces, grouped by across-neck position into six tubes.
adj=[[] for _ in pts]
for ed in g.data.edges:a,b=ed.vertices;adj[a].append(b);adj[b].append(a)
seen=set();pieces=[]
for i in range(len(pts)):
 if i in seen:continue
 todo=[i];seen.add(i);ids=[]
 while todo:
  a=todo.pop();ids.append(a)
  for n in adj[a]:
   if n not in seen:seen.add(n);todo.append(n)
 dims=bb([pts[j] for j in ids])['dimensions']
 if dims[2]>.8 and dims[0]<.02:pieces.append(set(ids))
def cross(z):
 raw=[]
 for ids in pieces:
  hits=[]
  for ed in g.data.edges:
   a,b=ed.vertices
   if a not in ids or b not in ids:continue
   p,q=pts[a],pts[b]
   if (p.z-z)*(q.z-z)<=0 and abs(p.z-q.z)>1e-9:hits.append(p+(q-p)*((z-p.z)/(q.z-p.z)))
  if hits:raw.append(sum(hits,Vector())/len(hits))
 clusters=[]
 for p in sorted(raw,key=lambda v:v.x):
  if not clusters or p.x-sum(v.x for v in clusters[-1])/len(clusters[-1])>.002:clusters.append([p])
  else:clusters[-1].append(p)
 centers=[sum(c,Vector())/len(c) for c in clusters];assert len(centers)==6
 return centers,[len(c) for c in clusters]
s=.7;theta=math.radians(75);T=Vector((math.sin(theta),0,math.cos(theta)));C=Vector((math.cos(theta),0,-math.sin(theta)));N=Vector((0,-1,0));initialloc=Vector((-.7*math.sin(theta)*.5075,-.22,.205))
def mx(loc):return Matrix.Translation(loc)@Matrix.Rotation(theta,4,'Y')@Matrix.Diagonal((s,s,s,1))
def depth_probe(M,tree,local_z_max=None):
 deepest=0;worst=None;count=0;tested=0
 # Ray front/back envelope along Y; only mathematical transformed vertices, not changed objects.
 for p in pts:
  if local_z_max is not None and p.z>local_z_max:continue
  wp=M@p;front,_,_,_=tree.ray_cast(Vector((wp.x,-.8,wp.z)),Vector((0,1,0)),1.6)
  if front is None:continue
  back,_,_,_=tree.ray_cast(Vector((wp.x,.8,wp.z)),Vector((0,-1,0)),1.6)
  if back is None:continue
  tested+=1
  if front.y<wp.y<back.y:
   count+=1;dep=wp.y-front.y
   if dep>deepest:deepest=dep;worst={'guitar_vertex':list(wp),'garment_front':list(front),'garment_back':list(back),'source_local':list(p)}
 return {'vertices_tested_in_y_envelope':tested,'inside_sample_count':count,'maximum_y_penetration_m':deepest,'worst':worst,'limit':'vertex envelope test, not full triangle collision acceptance'}
M0=mx(initialloc);initial=depth_probe(M0,body,.535);loc=initialloc.copy();loc.y-=initial['maximum_y_penetration_m']+.002 if initial['inside_sample_count'] else 0
M=mx(loc);finalbody=depth_probe(M,body,.535);finalhead=depth_probe(M,head,None);world=[M@p for p in pts];gtree=BVHTree.FromPolygons(world,tris,all_triangles=True)
def surf(p,side):
 p=M@p;o=p+N*(.15 if side=='front' else -.15);h,n,idx,d=gtree.ray_cast(o,-N if side=='front' else N,.3);return {'point':list(h),'normal':list(n),'triangle':idx} if h is not None else None
zL=.696;zR=.38;ls,lc=cross(zL);rs,rc=cross(zR);left_hits=[surf(p,'front') for p in ls];right_hits=[surf(p,'front') for p in rs];backhit=surf(Vector((0,0,zL)),'back')
# Wrist from actual rig-relative distal phalanx frame, not guessed Euler angles.
def old_bone_matrix(name):
 d=diag['def_axes_and_points'][name];R=Matrix((d['local_x_in_world'],d['local_y_in_world'],d['local_z_in_world'])).transposed().to_4x4();R.translation=Vector(d['head_world']);return R
def frame(cols):return Matrix(cols).transposed()
def wrist_from_pad(side,bone,desired_R,q,skin_target):
 oldH=Matrix(meas['hand_bones'][side]['matrix_world']);oldB=old_bone_matrix(bone);relR=oldH.to_3x3().inverted()@oldB.to_3x3();H=desired_R@relR.inverted();qhand=oldH.inverted()@(oldB@q);w=skin_target-H@qhand;shoulder=rig.matrix_world@rig.pose.bones[f'ORG-UpperArm.{side}'].head;upper=rig.pose.bones[f'ORG-UpperArm.{side}'].bone.length;fore=rig.pose.bones[f'ORG-Forearm.{side}'].bone.length;d=(w-shoulder).length
 return {'wrist':list(w),'hand_basis_xyz_world':[list(H.col[k]) for k in range(3)],'shoulder':list(shoulder),'shoulder_to_wrist_m':d,'original_upper_plus_forearm_m':upper+fore,'reach_ratio':d/(upper+fore),'reachable_without_stretch':d<upper+fore,'pad_proxy_bone_local':list(q),'skin_target':list(skin_target),'rig_relative_mapping':'Hnew = desired_distal_frame @ inverse(Hold^-1 @ Bdistal_old); wrist = target_skin - Hnew @ (Hold^-1 @ Bdistal_old @ qpad)','angles_held_for_algebraic_frame':'existing fix1 FK values only; this does not solve or endorse other finger curls'}
# One left index pad on bass-side outer string, thumb reserved for actual neck back.
lskin=Vector(left_hits[0]['point'])+N*.0005
Lbone='DEF-Index2.L';lb=meas['skin_tip_proxies'][Lbone]['bone_local_bbox'];Llen=meas['skin_tip_proxies'][Lbone]['bone_length'];lq=Vector((0,.8*Llen,lb['max'][2]));L=wrist_from_pad('L',Lbone,frame((-T,-C,-N)),lq,lskin)
# Single right thumb preparation above upper string; distal thumb runs across the strings, compact fingers stay away.
rskin=Vector(right_hits[0]['point'])+N*.003
Rbone='DEF-Thumb2.R';rb=meas['skin_tip_proxies'][Rbone]['bone_local_bbox'];Rlen=meas['skin_tip_proxies'][Rbone]['bone_length'];rq=Vector((rb['max'][0],.8*Rlen,0));# Thumb preparation uses an actual rig-relative pad vector, aimed from an outside-edge wrist seed.
oldH=Matrix(meas['hand_bones']['R']['matrix_world']);oldB=old_bone_matrix(Rbone);relpad=oldH.inverted()@(oldB@rq);relpadnormal=(oldH.to_3x3().inverted()@oldB.to_3x3().col[0]).normalized()
wseed=M@Vector((-.15,.02,.40));direction=(rskin-wseed).normalized();Q=relpad.normalized().rotation_difference(direction);H=Q.to_matrix();a=H@relpadnormal;desired=-N
ap=(a-direction*a.dot(direction)).normalized();dp=(desired-direction*desired.dot(direction)).normalized();ang=math.atan2(direction.dot(ap.cross(dp)),ap.dot(dp));H=Matrix.Rotation(ang,3,direction)@H;w=rskin-H@relpad;shoulder=rig.matrix_world@rig.pose.bones['ORG-UpperArm.R'].head;arm=sum(rig.pose.bones[n].bone.length for n in ['ORG-UpperArm.R','ORG-Forearm.R']);d=(w-shoulder).length
R={'wrist':list(w),'wrist_seed_world':list(wseed),'hand_basis_xyz_world':[list(H.col[k]) for k in range(3)],'shoulder':list(shoulder),'shoulder_to_wrist_m':d,'original_upper_plus_forearm_m':arm,'reach_ratio':d/arm,'reachable_without_stretch':d<arm,'pad_proxy_bone_local':list(rq),'skin_target':list(rskin),'pad_proxy_outward_normal_world':list(H@relpadnormal),'pad_normal_dot_toward_guitar':(H@relpadnormal).dot(-N),'method':'rig-relative skin vector alignment + one analytically determined twist about that vector, wrist derived exactly; no Euler search or pose mutation','right_thumb_old_angles_deg':[10,25],'limits':['proxy skin point, not full hand collision proof','three non-playing fingers must use separate bounded curls into palm, not preserved dangling pose']}
for hand_result in [L,R]:
 wp=Vector(hand_result['wrist']);near,nn,ii,dd=gtree.find_nearest(wp);hand_result['wrist_center_nearest_guitar']={'point':list(near),'normal':list(nn),'unsigned_distance_m':dd,'normal_signed_distance_m':(wp-near).dot(nn),'warning':'point only; a positive distance still does not prove the wrist skin clears.'}
# Opposing thumb reach once the left hand rigid frame is set (remaining thumb joints to solve within finite bounds).
Hl=Matrix(L['hand_basis_xyz_world']).transposed();oldH=Matrix(meas['hand_bones']['L']['matrix_world']);oldthumb=old_bone_matrix('DEF-Thumb1.L');thumbbase=Vector(L['wrist'])+Hl@(oldH.inverted()@oldthumb.translation);backnormal=Vector(backhit['normal']).normalized();thumbskin=Vector(backhit['point'])+backnormal*.0005;thumbcenter=thumbskin+backnormal*.01636;tl=sum(rig.pose.bones[f'DEF-Thumb{k}.L'].bone.length for k in [1,2]);thumbdist=(thumbcenter-thumbbase).length
# Measure thumb-1 mid-pad geometry so it can support the neck without forcing the tip into a 146-degree fold.
hand=bpy.data.objects['GEO-hands'];eh=hand.evaluated_get(dg);hm=eh.to_mesh();pb=rig.pose.bones['DEF-Thumb1.L'];B=rig.matrix_world@pb.matrix;Bi=B.inverted();vg=hand.vertex_groups['DEF-Thumb1.L'];mid=[]
for vert in hm.vertices:
 weight=next((q.weight for q in vert.groups if q.group==vg.index),0)
 if weight>.35:
  lp=Bi@(eh.matrix_world@vert.co)
  if .3*pb.length<lp.y<.8*pb.length:mid.append(lp)
eh.to_mesh_clear();radii=sorted(math.sqrt(p.x*p.x+p.z*p.z) for p in mid);pr=radii[int(.9*(len(radii)-1))] if radii else .014;pc=thumbskin+backnormal*pr;pd=(pc-thumbbase).length
proximal={'skin_target':list(thumbskin),'surface_normal':list(backnormal),'estimated_pad_axis_center':list(pc),'measured_thumb1_midpad_radius90_m':pr,'sample_vertices':len(mid),'thumb1_base_virtual':list(thumbbase),'base_to_pad_center_m':pd,'original_thumb1_length_m':pb.length,'fraction_along_proximal_phalanx':pd/pb.length,'intent':'Use proximal thumb pad against neck back. Do not force distal thumb tip onto same point; distal thumb remains relaxed along back/edge.','normal_offset_limit':'cross-section radius is an initial proxy; evaluate actual skin signed distances before accepting.'}
result={'scope':'read-only algebraic proposal; no pose edits or renders','source':str(src),'source_sha256_before':sha,'string_grouping':{'raw_long_split_pieces':len(pieces),'neck_cluster_sizes':lc,'strum_cluster_sizes':rc,'string_count':6,'method':'sort source cross-neck X then cluster consecutive centers within 2mm; assert six groups'},'initial_candidate':{'scale':s,'neck_axis':list(T),'cross_axis':list(C),'front_normal':list(N),'location':list(initialloc),'garment_envelope':initial},'single_analytic_outward_correction_m':initial['maximum_y_penetration_m']+.002 if initial['inside_sample_count'] else 0,'final_candidate':{'scale':s,'location':list(loc),'matrix_world':[list(row) for row in M],'neck_axis':list(T),'cross_axis':list(C),'front_normal':list(N),'bbox':bb(world),'garment_envelope':finalbody,'head_envelope':finalhead},'left_index_pad':L,'right_thumb_prepare':R,'left_proximal_thumb_back_support':proximal,'rejected_distal_thumb_same_point_proxy':{'neck_back_surface':backhit,'skin_target':list(thumbskin),'bone_center_proxy':list(thumbcenter),'virtual_thumb1_base':list(thumbbase),'base_to_center_m':thumbdist,'original_two_thumb_bones_sum_m':tl,'reachable_two_link_proxy':thumbdist<=tl,'normal':list(backnormal)},'left_six_string_front_surfaces':left_hits,'right_six_string_front_surfaces':right_hits,'finger_ik_required':'Wrist/frame is proposal only; solve per-finger two-joint bounded FK X using actual evaluated skin signed gaps; no unified curl values. If multiple targets infeasible, stop rather than scale fingers or stretch arm.','source_sha256_after':hashlib.sha256(src.read_bytes()).hexdigest()};assert result['source_sha256_after']==sha;out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['string_grouping','single_analytic_outward_correction_m','final_candidate','left_index_pad','right_thumb_prepare','left_proximal_thumb_back_support']}))
