"""C39 one continuous right-arm anatomical candidate; known-failed C37 frozen.
Actual faired-Q ambient flow + exterior-accessible underarm clearance topology.
No separate limb/shell, animation, color or public asset. All new point source IDs 0.
"""
import bpy,bmesh,numpy as np,json,hashlib,sys,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/character-strum-paw-c39';OUT.mkdir(exist_ok=True);SRC=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
helper=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';hs=helper.read_text();exec(compile(hs[hs.index('def smooth'):hs.index('def main():')],str(helper)+'#read-only-reused-helpers','exec'),globals())
def compact(r):
 q=np.clip(r,0,1);return (1-q)**4*(4*q+1)
def volume(me):
 bm=bmesh.new();bm.from_mesh(me);r={'signed_volume':bm.calc_volume(signed=True),'euler':len(bm.verts)-len(bm.edges)+len(bm.faces)};bm.free();return r

def clipped(poly,axis,bound,less):
 result=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=p[axis]<=bound if less else p[axis]>=bound;c=q[axis]<=bound if less else q[axis]>=bound
  if a:result.append(p)
  if a!=c:result.append(p+(q-p)*((bound-p[axis])/(q[axis]-p[axis])))
 return result

def main():
 started=time.time();srcsha=sha(SRC);bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;P=arr(me).copy();original_topo=topo(me);original_vol=volume(me);original_faces=[tuple(f.vertices) for f in me.polygons];canonical=me.attributes.get('Miao_C35_vertex_id') or me.attributes.new('Miao_C35_vertex_id','INT','POINT');canonical.data.foreach_set('value',np.arange(1,len(P)+1,dtype=np.int32));original_attrs={a.name:np.array([x.value for x in a.data]) for a in me.attributes if a.domain=='POINT' and a.data_type in {'INT','BOOLEAN'}};protected={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};Q=np.load(OUT/'fair-only-coordinates.npz')['fair'].copy();assert np.array_equal(np.load(OUT/'fair-only-coordinates.npz')['original'].astype(np.float32),P)
 C=np.array([-.58,-1.19,1.8]);D=np.array([.78,0,-.625]);D/=np.linalg.norm(D);T=np.array([.625,0,.78]);T/=np.linalg.norm(T);V=np.array([-.40048756408789304,0,1.0169595357706245]);V/=np.linalg.norm(V)
 # One fixed 128-step Euler integration of a smooth ambient vector field,
 # evaluated on current Q every step. Each map is near identity, not a stale-P
 # displacement superimposed after fairing. The compact support locks outside.
 max_step=0.;initial_s=(Q-C)@D;initial_t=(Q-C)@T;initial_r=np.sqrt(((initial_s-.16)/.46)**2+(initial_t/.31)**2+((Q[:,1]+1.22)/.45)**2);flow_ids=np.flatnonzero(initial_r<1);F=Q[flow_ids].copy()
 for iteration in range(128):
  ss=(F-C)@D;tt=(F-C)@T;yy=F[:,1]+1.22;rr=np.sqrt(((ss-.16)/.46)**2+(tt/.31)**2+(yy/.45)**2);m=compact(rr);dist=smooth((ss+.025)/.20);web=np.exp(-((tt+.063)/.043)**2)+np.exp(-((tt-.064)/.043)**2);velocity=(-.019*m*dist*web)[:,None]*D-(.041*m*dist)[:,None]*V;velocity[:,1]+=.026*m*dist*smooth((-yy-.005)/.10);step=velocity/128;max_step=max(max_step,float(np.linalg.norm(step,axis=1).max()));F+=step
 Q[flow_ids]=F;print('STAGE actual-Q-flow-done '+str(len(flow_ids)),flush=True)
 # Broad shoulder-surface fairing. This mask ends below head z2.43 and above
 # pear deformation z1.4, and is restricted to anatomical right x<0.
 w=compact(np.sqrt(((P[:,0]+.83)/.49)**2+((P[:,1]+.28)/.58)**2+((P[:,2]-2.19)/.24)**2));w*=smooth((2.425-P[:,2])/.04);w[P[:,0]>=-.35]=0;ids=np.flatnonzero(w>0);mp=np.full(len(P),-1,np.int32);mp[ids]=np.arange(len(ids));edges=np.array([tuple(e.vertices) for e in me.edges]);edges=edges[(w[edges]>0).any(1)];ii=np.r_[edges[:,0],edges[:,1]];jj=np.r_[edges[:,1],edges[:,0]];keep=w[ii]>0;ii=ii[keep];jj=jj[keep];count=np.bincount(mp[ii],minlength=len(ids));prior=Q.copy()
 for it in range(50):
  sums=np.stack([np.bincount(mp[ii],weights=Q[jj,k],minlength=len(ids)) for k in range(3)],axis=1);Q[ids]+=.3*w[ids,None]*(sums/count[:,None]-Q[ids])
 shoulder_delta=Q-prior;me.vertices.foreach_set('co',Q.astype(np.float32).ravel());me.update();Q=arr(me).copy();bpy.context.view_layer.update();before_cut=volume(me);print('STAGE shoulder-fair-done',flush=True)
 # Build one clearance volume from the real guitar outline, expanded .065u
 # radially and clipped to the authorized right underarm/forearm window. Its
 # front is a rounded arm-back cross-section, not a flat guitar-plane slot.
 ob=bpy.data.objects['Guitar / rosewood body'];n=len(ob.data.vertices)//2;raw=np.array([tuple(ob.matrix_world@v.co) for v in list(ob.data.vertices)[:n]]);poly=[q[[0,2]] for q in raw];center=np.mean(poly,0);poly=[p+(p-center)/np.linalg.norm(p-center)*.065 for p in poly];poly=clipped(poly,0,-.18,True);poly=clipped(poly,1,1.475,False);poly=clipped(poly,1,2.30,True);n=len(poly);front=-1.105;back=-.620;verts=[(p[0],y,p[1]) for y in [front,back] for p in poly];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];cm=bpy.data.meshes.new('C39 exterior-accessible clearance volume');cm.from_pydata(verts,[],faces);cm.update();bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces[:])
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);bmesh.ops.subdivide_edges(bm,edges=bm.edges[:],cuts=2,use_grid_fill=True)
 for v in bm.verts:
  t=(v.co.y-front)/(back-front);dx=v.co.x+.77;dz=v.co.z-1.85;lateral=(dx*T[0]+dz*T[2]);rounded_front=-1.095-.080*min(1,(lateral/.30)**2);v.co.y=(1-t)*rounded_front+t*back
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(cm);bm.free();cm.update();cut=bpy.data.objects.new('C39 temporary actual-wood clearance',cm);s.collection.objects.link(cut);cut.hide_render=True;cut.hide_set(True);cut_topo=topo(cm);cut_vol=volume(cm)
 # Exterior accessibility is tested against the complete original skin, with
 # cutter boundary samples proven outside, in addition to final component/Euler.
 original_tree=BVHTree.FromPolygons(Q,original_faces);outside=[]
 def parity(tree,p,dr):
  pos=Vector(p);count=0
  for j in range(128):
   h,n,f,d=tree.ray_cast(pos,dr,8)
   if h is None:return count%2
   count+=1;pos=h+dr*1e-5
  return None
 dr=Vector((.371,.613,.697)).normalized()
 for i,v in enumerate(cm.vertices):
  if i%17==0 and parity(original_tree,v.co,dr)==0:outside.append(i)
 pre={'scope':'One fixed actual-wood clearance preflight, not an art variant','cutter_topology':cut_topo,'cutter_volume':cut_vol,'cutter_boundary_samples_outside_original_skin':len(outside),'outside_sample_ids':outside[:40],'front_definition':'rounded arm-back Y=-1.095-.080*min(1,(lateral/.30)^2); true tube global front min -1.0588 gives >=.0362u front clearance at plane center','back_y':back,'actual_guitar_outline_radial_padding':.065,'clip_window':{'x_max':-.18,'z_min':1.475,'z_max':2.30},'cannot_be_closed_internal_shell':bool(outside)};(OUT/'clearance-preflight.json').write_text(json.dumps(pre,indent=2)+'\n');print('STAGE clearance-preflight '+json.dumps(pre),flush=True);assert cut_topo['components']==1 and not cut_topo['nonmanifold_edges'] and outside
 # Apply one manifold difference. New faces truly share edges in body mesh.
 bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('C39 underarm exterior channel','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='MANIFOLD';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);me=body.data;me.update();bpy.context.view_layer.update();actual=arr(me);print('STAGE boolean-done '+str(len(actual)),flush=True);index_by_co={p.tobytes():i for i,p in enumerate(Q)};oldmap=np.array([index_by_co.get(p.tobytes(),-1) for p in actual],np.int32);retained=oldmap>=0;new=~retained;present=np.zeros(len(P),bool);present[oldmap[retained]]=True;removed=np.flatnonzero(~present);mapping_attr=me.attributes.get('C39 original point id') or me.attributes.new('C39 original point id','INT','POINT');mapping_attr.data.foreach_set('value',(oldmap+1).astype(np.int32));
 for name,values in original_attrs.items():
  a=me.attributes.get(name) or me.attributes.new(name,'INT','POINT');v=np.zeros(len(actual),np.int32);v[retained]=values[oldmap[retained]];a.data.foreach_set('value',v)
 for f in me.polygons:f.use_smooth=True
 topo_after=topo(me);vol_after=volume(me);me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);face=np.array([t.polygon_index for t in me.loop_triangles]);pcenter=actual[tri].mean(1);region=(pcenter[:,0]<-.17)&(pcenter[:,1]<.055)&(pcenter[:,2]>1.46)&(pcenter[:,2]<2.431);rt=tri[region];rfi=face[region];right_ids=sorted(set(rt.ravel().tolist()));local_faces=sorted(set(rfi.tolist()));local=local_stats(body,actual,local_faces);ht=BVHTree.FromPolygons(actual,rt.tolist(),all_triangles=True);whole=BVHTree.FromPolygons(actual,tri.tolist(),all_triangles=True);selfpairs=[];rti=np.flatnonzero(region)
 for i,j in ht.overlap(whole):
  a=int(rti[i])
  if a==j or set(tri[a])&set(tri[j]) or (region[j] and a>j):continue
  selfpairs.append([a,j,int(face[a]),int(face[j])])
 obstacles={name:actual_tree(bpy.data.objects[name]) for name in protected if bpy.data.objects[name].type in {'MESH','CURVE'} and not bpy.data.objects[name].hide_render};cross={name:len(ht.overlap(tree)) for name,(tree,nt) in obstacles.items()};solid=[]
 for name in ['Guitar / spruce soundboard','Guitar / rosewood body','Guitar / neck','Guitar / ebony fretboard']:
  tree,nt=obstacles[name];inside=[];amb=[];dirs=[Vector((.371,.613,.697)).normalized(),Vector((.739,.223,.635)).normalized()]
  for i in right_ids:
   votes=[parity(tree,actual[i],dr) for dr in dirs]
   if votes==[1,1]:inside.append(i)
   elif votes[0]!=votes[1] or None in votes:amb.append(i)
  solid.append({'object':name,'tested_right_skin_points':len(right_ids),'inside':len(inside),'ambiguous':len(amb),'inside_sample':inside[:20]})
 tube_gaps=[];tipids=[i for i in right_ids if actual[i,0]>-.70 and actual[i,1]<-1.0 and actual[i,2]<1.82]
 for k in range(6):
  tree,nt=obstacles['Guitar / string '+str(k+1)];best=min((tree.find_nearest(Vector(actual[i]))[3],i) for i in tipids);tube_gaps.append({'string':k+1,'minimum_skin_vertex_to_actual_tube_distance':float(best[0]),'skin_vertex':best[1],'skin':actual[best[1]].tolist()})
 closest=min(q['minimum_skin_vertex_to_actual_tube_distance'] for q in tube_gaps);idle_gap=.02<=closest<=.04
 protected_unchanged=protected=={n:fingerprint(bpy.data.objects[n]) for n in protected};allowed=(P[:,0]<-.17)&(P[:,1]<.055)&(P[:,2]>1.46)&(P[:,2]<2.431);d0=np.linalg.norm(Q-P,axis=1);locked=~allowed;locks_exact=bool(np.all(present[locked]) and np.array_equal(Q[locked],P[locked]));left=P[:,0]>.5;left_exact=bool(np.all(present[left]) and np.array_equal(Q[left],P[left]));head=P[:,2]>=2.43;head_exact=bool(np.all(present[head]) and np.array_equal(Q[head],P[head]));removed_outside=removed[~allowed[removed]];newsource0=all(all(a.data[i].value==0 for i in np.flatnonzero(new)) for a in me.attributes if a.domain=='POINT' and a.data_type=='INT' and a.name in original_attrs);woodpass=not any(cross.values()) and all(q['inside']==0 and q['ambiguous']==0 for q in solid);volume_pass=vol_after['signed_volume']>0 and vol_after['euler']==original_vol['euler'] and vol_after['signed_volume']<before_cut['signed_volume'];passed=not selfpairs and local['flipped_faces']==0 and topo_after['components']==1 and not topo_after['boundary_edges'] and not topo_after['nonmanifold_edges'] and protected_unchanged and locks_exact and left_exact and head_exact and not len(removed_outside) and newsource0 and woodpass and volume_pass and idle_gap
 np.savez_compressed(OUT/'source-map-and-authored-delta.npz',output_to_original_index=oldmap,original_to_present=present,removed_original_ids=removed,original=P,authored_before_boolean=Q,output=actual,source_ids=np.array([x.value for x in me.attributes['C23 source vertex id'].data]));receipt={'stage':'C39-one-actual-Q-flow-and-exterior-underarm-topology-candidate','source_native_sha256':srcsha,'script_sha256':sha(__file__),'C37_helper_sha256':sha(helper),'fair_only_diagnostic_is_not_art_pass':True,'direction':'anatomical right arm = screen left; anatomical left C35 = screen right','design':{'single_candidate':True,'actual_Q_flow_steps':128,'maximum_flow_step':max_step,'shoulder_fairing_steps':50,'max_shoulder_fair_delta':float(np.linalg.norm(shoulder_delta,axis=1).max()),'right_repair_allowance':'x<-.17,y<.055,z1.46..2.431; actual sources explicitly mapped; all head z>=2.43 exact','clearance_preflight':pre},'before_topology':original_topo,'after_topology':topo_after,'before_volume':original_vol,'before_clearance_volume':before_cut,'after_volume':vol_after,'new_points':int(new.sum()),'retained_original_points':int(retained.sum()),'removed_original_points':len(removed),'removed_original_points_outside_allowance':removed_outside.tolist(),'canonical_point_identity':'Miao_C35_vertex_id = frozen C35 original index+1; every retained original identity reconstructed by bit-exact pre-Boolean Q coordinate; every generated point0, including no interpolation inheritance','canonical_nonzero_retained_ids_unique':bool(len(np.unique(oldmap[retained]))==int(retained.sum())),'new_original_source_ids_zero':newsource0,'protected_original_points_exact_and_present':locks_exact,'left_C35_points_exact_and_present':left_exact,'head_points_exact_and_present':head_exact,'guitar_exact':protected_unchanged,'maximum_preboolean_old_point_displacement':float(d0.max()),'local_audit':local,'actual_right_vs_whole_non_neighbour_triangle_self_pairs':len(selfpairs),'self_pair_sample':selfpairs[:30],'actual_evaluated_guitar_triangle_intersections':cross,'wood_skin_parity':solid,'all_actual_wood_and_tube_clearance_pass':woodpass,'actual_closest_six_tube_vertex_probes':tube_gaps,'idle_closest_any_string_vertex_gap_02_04_pass':idle_gap,'idle_gap_limit':'closest actual sampled skin vertex to any six actual string tube, not six pressed contacts and not a motion path','positive_volume_same_euler_single_surface_pass':volume_pass,'engineering_gate_passed':passed,'limits':['Independent identity/craft/motion static reviews pending. No full-character approval.','Vertex nearest gap is finite sampling; triangle intersections and wood parity independently audited.','Topology new back surface may look unnatural: actual diagnostic images must decide.','No groom/UV/rig/animation/color/public/export/deploy or paid service.'],'seconds_before_render':time.time()-started};bpy.context.preferences.filepaths.save_version=0;native=OUT/('miao-c39-right-arm.blend' if passed else 'diagnostic-c39-geometry-failed.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({'passed':passed,'self':len(selfpairs),'wood_tubes':{k:v for k,v in cross.items() if v},'parity':solid,'closest_gap':closest,'topo':topo_after,'volume':vol_after,'locks':locks_exact,'left':left_exact,'head':head_exact,'new':int(new.sum()),'removed':len(removed),'native':receipt['native_sha256']}),flush=True)
 # Parent explicitly allows internal diagnostic gray of failed actual geometry.
 s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;receipt['renders']=[]
 for view in ['front','right-paw','right-side']:
  if view=='right-paw':cam.location=(-.65,-12,2.7);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
  if view=='right-side':cam.location=(-4,-6,3.1);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
  file=OUT/(('gray-' if passed else 'diagnostic-failed-gray-')+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);receipt['renders'].append({'file':file.name,'sha256':sha(file),'diagnostic_known_geometry_fail':not passed});(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 assert sha(SRC)==srcsha
main()
