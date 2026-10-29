"""C38 reference-led coupled head/face candidate. Not a passed character.
One continuous mesh field plus all-feature yaw; no hidden eyes or replacement cat.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
NAME='Miao / continuous pear and rounded-square face';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sm(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def co(ob):
 a=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',a);return a.reshape(-1,3)
def world(ob,p):
 m=np.array(ob.matrix_world);return p@m[:3,:3].T+m[:3,3]
def local(ob,p):
 m=np.array(ob.matrix_world);return (p-m[:3,3])@np.linalg.inv(m[:3,:3]).T

def pre(P):
 P=np.asarray(P,float);Q=P.copy();x,y,z=P.T
 # A low-amplitude C2 shared lower-face return. No vertical lift, neck collar,
 # isolated lateral cheek pad or x-partitioned ear/forehead deformation.
 r2=(x/.65)**2+((z-2.61)/.22)**2;g=np.maximum(0,1-r2)**3;front=1-sm(-.12,.10,y)
 Q[:,1]+=.018*g*front
 # Only a shallow C2 cavity return, with no head-wide x/z compression. The
 # previously rejected fields caused forehead partitions/bands in actual renders.
 for side in [-1,1]:
  r2=((x-side*.435)/.12)**2+((z-3.255)/.13)**2;ear=np.maximum(0,1-r2)**3
  Q[:,1]-=0.0*ear # Ear cavity deformations failed geometry/visual gates; retained as a known unresolved P0.
 return Q
YAW=math.radians(7.5);LEAN=.040
# Fit: original nose offset relative cheek midpoint .0392H, source .0221H.
# At nose depth .445u, a 7.5deg yaw yields approximately .058u extra relative
# offset; .040u head lean separately fits cheek-midpoint/body-center offset.
def yaw(P):
 P=np.asarray(P,float);Q=P.copy();x,y,z=P.T;w=sm(2.43,2.68,z);ang=YAW*w;c=np.cos(ang);t=np.sin(ang);Q[:,0]=x*c-(y-.03)*t+LEAN*w;Q[:,1]=.03+x*t+(y-.03)*c;return Q

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-alignment-c38/head-expression-only');p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
 if (out/'receipt.json').exists():raise RuntimeError('Frozen candidate exists; preserve it')
 src=ROOT/'artifacts/character-alignment-c36/repaired/miao-c36-reference-alignment-gray.blend';source_sha=sha(src);assert source_sha=='d3bdc3d312fa5ef1f8832d2a4283ad2761bf2bf3bf9f4d622bfa8528d063fb5f'
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;b=bpy.data.objects[NAME];me=b.data;old=co(b);assert b.matrix_world==Matrix.Identity(4) and not b.modifiers and not me.shape_keys
 oldtree=BVHTree.FromObject(b,bpy.context.evaluated_depsgraph_get());ids=np.empty(len(old),np.int32);me.attributes['C23 source vertex id'].data.foreach_get('value',ids)
 x,y,z=old.T;lock=(ids==0)|((z<2.43)&(z>1.40)&(np.abs(x)>.64)&(y<-.20));base=pre(old);base[lock]=old[lock];ear_before=base.copy();edges=np.empty(len(me.edges)*2,np.int32);me.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2);ear_weight=sm(.25,.40,np.abs(x))*sm(3.10,3.22,z)
 for iteration in range(0):
  for factor in [.20,-.21]:
   sums=np.zeros_like(base);counts=np.zeros(len(base));np.add.at(sums,edges[:,0],base[edges[:,1]]);np.add.at(sums,edges[:,1],base[edges[:,0]]);np.add.at(counts,edges[:,0],1);np.add.at(counts,edges[:,1],1);base+=(sums/np.maximum(counts,1)[:,None]-base)*(factor*ear_weight)[:,None]
 ear_delta=base-ear_before;assert np.linalg.norm(ear_delta,axis=1).max()<.01;assert np.array_equal(base[lock],old[lock]);np.savez_compressed(out/'ear-softening-evidence.npz',source_ids=ids,changed_indices=np.flatnonzero(np.any(ear_delta!=0,axis=1)),delta=ear_delta[np.any(ear_delta!=0,axis=1)])
 me.vertices.foreach_set('co',base.astype(np.float32).ravel());me.update();bpy.context.view_layer.update();pretree=BVHTree.FromObject(b,bpy.context.evaluated_depsgraph_get())
 ray_misses=[]
 def skin(tree,x,z):
  h=tree.ray_cast(Vector((float(x),-3,float(z))),Vector((0,1,0)),8)[0]
  if h is None:ray_misses.append([float(x),float(z)]);raise RuntimeError('Actual skin ray missed')
  return float(h.y)
 eye_records=[];feature_records=[];owned=[]
 eye_names=[o.name for o in s.objects if o.type=='MESH' and o.name.startswith(('C6 /','C7 / clear cornea'))]
 nose_name='Face / rounded triangular nose'
 # Final, visible eye geometry is always retained, including lids/cornea. Compress
 # its depth relative to actual old/new skin, preserving XZ extent and ordering.
 for name in eye_names+[nose_name]:
  o=bpy.data.objects[name];assert not o.hide_render;P=world(o,co(o));Q=pre(P);delta=[]
  for i,(v,w) in enumerate(zip(P,Q)):
   oldskin=skin(oldtree,v[0],v[2]);newskin=skin(pretree,w[0],w[2]);scale=.55 if name==nose_name else .42;d=v[1]-oldskin;w[1]=newskin+scale*d
   if 'lid' in name:w[1]=min(w[1],newskin-.00025)
   delta.append([oldskin-v[1],newskin-w[1]])
  if name!=nose_name:eye_records.append({'name':name,'before_skin_gap_range':np.min(delta,axis=0).tolist(),'old_new_skin_gap_quantiles':np.quantile(np.array(delta),[0,.5,1],axis=0).tolist(),'XZ_preserved_before_yaw':bool(np.array_equal(P[:,[0,2]],Q[:,[0,2]])),'hidden':False,'vertex_count_unchanged':len(P)})
  o.data.vertices.foreach_set('co',local(o,Q).astype(np.float32).ravel());o.data.update();owned.append(name)
 bpy.context.view_layer.update()
 # Numerical front-surface checks BEFORE common rigid yaw, in which all ordering
 # is invariant. Back sclera volume is intentionally tucked under skin.
 ocular=[]
 for side in ['L','R']:
  white=bpy.data.objects['C6 / sclera '+side];W=world(white,co(white));n=len(W)//2;front=W[:n];c=front[0];rx=(W[:,0].max()-W[:,0].min())/2;rz=(W[:,2].max()-W[:,2].min())/2;rad=np.sqrt(((front[:,0]-c[0])/rx)**2+((front[:,2]-c[2])/rz)**2);gaps=np.array([skin(pretree,v[0],v[2])-v[1] for v in front]);interior=rad<.94;assert gaps[interior].min()>1e-4,'Visible white penetrates head'
  tree=BVHTree.FromObject(white,bpy.context.evaluated_depsgraph_get());rec={'side':side,'white_front_interior_samples':int(interior.sum()),'minimum_white_front_interior_skin_gap':float(gaps[interior].min()),'maximum_white_front_skin_protrusion':float(gaps.max()),'iris_caps':[]}
  for name in ['C6 / iris '+side,'C7 / clear cornea '+side]:
   o=bpy.data.objects[name];P=world(o,co(o));dist=[]
   for v in P:
    h=tree.ray_cast(Vector((float(v[0]),-3,float(v[2]))),Vector((0,1,0)),8)[0];assert h is not None;dist.append(float(h.y-v[1]))
   rec['iris_caps'].append({'name':name,'all_vertices':len(P),'minimum_distance_in_front_of_white':min(dist),'maximum':max(dist)});assert min(dist)>1e-5,'Iris/cap lies behind actual sclera'
  ocular.append(rec)
 # Curves: same lower-face deformation, then exact shared yaw. Preserve controls
 # and handles. Mouth stays inlaid relative actual new skin, brows taper softly.
 for o in list(s.objects):
  if o.type!='CURVE' or not o.name.startswith(('Face /','Miao / fine whisker')):continue
  owned.append(o.name);oldbevel=o.data.bevel_depth
  for sp in o.data.splines:
   for point in sp.points:
    w=o.matrix_world@Vector(point.co[:3]);P=np.array([w]);Q=pre(P)
    if o.name.startswith('Face /'):
     oldskin=skin(oldtree,w.x,w.z);ns=skin(pretree,Q[0,0],Q[0,2]);Q[0,1]=ns+(w.y-oldskin)*.70
    v=o.matrix_world.inverted()@Vector(yaw(Q)[0]);point.co=(*v,point.co.w)
   bp=list(sp.bezier_points)
   if bp:
    allx=[p.co.x for p in bp];lo,hi=min(allx),max(allx)
    for point in bp:
     original={k:o.matrix_world@getattr(point,k) for k in ['co','handle_left','handle_right']};P=np.array([original[k] for k in ['co','handle_left','handle_right']]);Q=pre(P)
     if o.name.startswith('Face /'):
      ns=skin(pretree,Q[0,0],Q[0,2]);os=skin(oldtree,P[0,0],P[0,2]);shift=ns+(P[0,1]-os)*.70-Q[0,1];Q[:,1]+=shift
     Q=yaw(Q)
     for k,q in zip(['co','handle_left','handle_right'],Q):setattr(point,k,o.matrix_world.inverted()@Vector(q))
     if o.name.startswith('Face / thick curved brow'):
      t=(original['co'].x-lo)/max(hi-lo,1e-8);point.radius*=.35+.65*max(0,math.sin(math.pi*t))**.5
  if o.name.startswith('Face / thick curved brow'):o.data.bevel_depth*=.85
  feature_records.append({'name':o.name,'type':'CURVE','all_controls_and_handles_transformed':True,'old_bevel_depth':oldbevel,'new_bevel_depth':o.data.bevel_depth,'hide_render':o.hide_render})
 # Every ocular and nose vertex uses exactly the same yaw as the head. No local
 # matrix that silently rotates an eye without its associated lid or iris.
 for name in eye_names+[nose_name]:
  o=bpy.data.objects[name];P=world(o,co(o));Q=yaw(P);o.data.vertices.foreach_set('co',local(o,Q).astype(np.float32).ravel());o.data.update();feature_records.append({'name':name,'type':'MESH','all_vertices_yawed':len(P),'hide_render':o.hide_render})
 for o in s.objects:
  if o.name.startswith('C7 / optical area'):
   o.location=Vector(yaw(np.array([o.location]))[0]);o.rotation_euler=(Matrix.Rotation(YAW,4,'Z')@o.rotation_euler.to_matrix().to_4x4()).to_euler();owned.append(o.name)
 final=yaw(base).astype(np.float32);final[lock]=old[lock];assert np.array_equal(final[lock],old[lock]);me.vertices.foreach_set('co',final.ravel());me.update();bpy.context.view_layer.update()
 changed=np.any(old!=final,axis=1);me.calc_loop_triangles();tris=np.array([t.vertices[:] for t in me.loop_triangles]);T=tris[changed[tris].any(1)];n0=np.cross(old[T[:,1]]-old[T[:,0]],old[T[:,2]]-old[T[:,0]]);n1=np.cross(final[T[:,1]]-final[T[:,0]],final[T[:,2]]-final[T[:,0]]);l0=np.linalg.norm(n0,axis=1);l1=np.linalg.norm(n1,axis=1);dot=np.einsum('ij,ij->i',n0,n1)/np.maximum(l0*l1,1e-24)
 # A smooth depth compression can legally rotate surface normals beyond 45deg.
 # Transport source normals with the actual field Jacobian; a positive Jacobian
 # plus agreement with actual triangle normals distinguishes rotation from a fold.
 C=old[T].mean(1).astype(float);eps=1e-5;J=np.empty((len(C),3,3))
 for axis in range(3):
  step=np.zeros(3);step[axis]=eps;J[:,:,axis]=(yaw(pre(C+step))-yaw(pre(C-step)))/(2*eps)
 det=np.linalg.det(J);expected=np.einsum('nij,nj->ni',np.linalg.inv(J).transpose(0,2,1),n0)*det[:,None];transport_dot=np.einsum('ij,ij->i',expected,n1)/np.maximum(np.linalg.norm(expected,axis=1)*l1,1e-24)
 regularization=[] # No custom normals and no extra vertex reflow in final candidate.
 pre_gate={'minimum_normal_dot':float(dot.min()),'minimum_area_ratio':float((l1/l0).min()),'negative_source_to_new_normal_dots':int((dot<=0).sum()),'minimum_field_jacobian_determinant':float(det.min()),'minimum_actual_vs_transported_normal_dot':float(transport_dot.min()),'minimum_transport_counterexample':{'dot':float(transport_dot.min()),'old_cross_area':float(l0[int(np.argmin(transport_dot))]),'source':old[T[int(np.argmin(transport_dot))]].tolist(),'new':final[T[int(np.argmin(transport_dot))]].tolist()},'new_flipped_triangles_against_transported_orientation':int((transport_dot<=0).sum()),'collapsed_triangles':int((l1<1e-13).sum()),'thin_ear_triangle_subpixel_reflow':regularization,'changed_vertices':int(changed.sum()),'max_displacement':float(np.linalg.norm(final-old,axis=1).max()),'counterexamples':[{'index':int(i),'normal_dot':float(dot[i]),'before':old[T[i]].tolist(),'after':final[T[i]].tolist()} for i in np.argsort(dot)[:6]]};(out/'pre-gate.json').write_text(json.dumps({'body':pre_gate,'eyes':ocular,'ray_misses':ray_misses},indent=2)+'\n');edge0=np.max(np.stack([np.linalg.norm(old[T[:,1]]-old[T[:,0]],axis=1),np.linalg.norm(old[T[:,2]]-old[T[:,0]],axis=1),np.linalg.norm(old[T[:,2]]-old[T[:,1]],axis=1)]),axis=0);condition=l0/np.maximum(edge0**2,1e-24);stable=condition>=.02;pre_gate['source_conditioning']={'source_cross_area_over_longest_edge_squared_threshold':.02,'stable_triangles':int(stable.sum()),'near_collinear_triangles':int((~stable).sum()),'minimum_stable_transported_normal_dot':float(transport_dot[stable].min()),'near_collinear_counterexamples':[{'condition':float(condition[i]),'old_cross_area':float(l0[i]),'trans_dot':float(transport_dot[i])} for i in np.argsort(transport_dot)[:12]]};pre_gate['actual_ear_softening_max_delta']=float(np.linalg.norm(ear_delta,axis=1).max());assert det.min()>.20 and transport_dot.min()>.70 and l1.min()>1e-13,'New stable-triangle fold or collapse';(out/'pre-gate.json').write_text(json.dumps({'body':pre_gate,'eyes':ocular,'ray_misses':ray_misses},indent=2)+'\n')
 bm=bmesh.new();bm.from_mesh(me);assert not any(not e.is_manifold for e in bm.edges);bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<2.28],context='VERTS');bm.verts.index_update();bm.faces.index_update();bm.faces.ensure_lookup_table();bm.normal_update();selfpairs=A._self_intersections(bm);bm.free();assert selfpairs==0,'New head self-crossing'
 np.savez_compressed(out/'body-deformation-evidence.npz',source_ids=ids,locked_indices=np.flatnonzero(lock),changed_indices=np.flatnonzero(changed),before=old[changed],after=final[changed])
 s.cycles.samples=24;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';bpy.context.preferences.filepaths.save_version=0;native=out/'miao-c38-coupled-head-gray.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 r={'stage':'C38 one coupled head/face gray candidate, art review pending','source':{'path':str(src.relative_to(ROOT)),'sha256':source_sha},'native_sha256':sha(native),'script_sha256':sha(__file__),'reference':'public/character/instrument-scenes-v1/guitar/idle.jpg','fitted_head_yaw_degrees':7.5,'separately_fitted_head_lean_u':LEAN,'body_gate':pre_gate,'head_self_pairs':selfpairs,'ocular_actual_geometry_checks':ocular,'all_head_parts_transformed':feature_records,'C35_new_points_and_broad_paw_lock_bit_exact':True,'locked_vertices':int(lock.sum()),'source_ids_and_body_topology_preserved':True,'no_eye_or_lid_hidden':True,'renders':[],'limits':['Gray candidate, not approved character; source C36 P0 is not erased by numerical gates.','Shoulders/body/feet and C37 right paw are outside this candidate; whole-character P0 may remain.','Static iris/white/head ordering checked before common yaw, not blink/rig/animation acceptance.','Mouth/whisker final all-angle attachment and ear craft require actual image review.','No groom rebind, materials redesign, production outputs or deployment.']};(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 if a.render:
  cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
  for name,pos,target,zoom in [('front',None,None,None),('face',Vector((0,-6,3.05)),Vector((0,0,3.03)),1.7),('three-quarter',Vector((6,-9,3.9)),Vector((.09881,0,1.609)),scale)]:
   if pos is None:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
   else:cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
   bpy.context.view_layer.update();f=out/('gray-'+name+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);r['renders'].append({'file':f.name,'sha256':sha(f),'camera_matrix':list(map(list,cam.matrix_world)),'ortho_scale':cam.data.ortho_scale})
 assert sha(src)==source_sha;(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({'native':r['native_sha256'],'gate':pre_gate,'head_self':selfpairs,'renders':r['renders']}),flush=True)
main()
