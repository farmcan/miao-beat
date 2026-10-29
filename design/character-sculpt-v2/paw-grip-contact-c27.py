"""C27 one bounded no-topology RBF grip candidate on frozen C25.
True saved skin triangles + fixed actual string/board rays; no target relocation.
"""
import bpy,bmesh,json,math,hashlib,sys,time,argparse,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier,intersect_ray_tri
P=argparse.ArgumentParser();P.add_argument('--out',default='artifacts/character-paw-grip-c27');a=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.out;out.mkdir(parents=True,exist_ok=True);src=root/'artifacts/character-paw-shared-surface-c25/miao-c25-shared-surface-diagnostic.blend';prior=root/'artifacts/character-paw-shared-surface-c25/contact-audit.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source_sha=sha(src);sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
O=Vector((-.1950536246756659,-.85,1.5567366254980208));GU=Vector((1.0169595357706245,0,.40048756408789304));GV=Vector((-.40048756408789304,0,1.0169595357706245));V=GV.normalized();VN=np.array(V)
def logical_u(p):return (p-O).dot(GU)/GU.length_squared
def logical_v(p):return (p-O).dot(GV)/GV.length_squared
def g(u,v,y):return O+GU*u+GV*v+Vector((0,y-O.y,0))
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def compact(t):t=np.clip(t,0,1);return (1-t)**4*(4*t+1)
def mesh(name,co,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(co,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return ob

def topo(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();seen=set();components=0
 for v in bm.verts:
  if v.index in seen:continue
  components+=1;stack=[v];seen.add(v.index)
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q.index not in seen:seen.add(q.index);stack.append(q)
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free();return r

def provenance(body,fi):
 return 2 if body.data.attributes['C23 C11 upper face local id'].data[fi].value>0 else 0 if body.data.attributes['C23 source face id'].data[fi].value>0 else 1

def bezier(ob,n=512):
 pts=[];bp=ob.data.splines[0].bezier_points
 for i in range(len(bp)-1):
  pp=interpolate_bezier(bp[i].co,bp[i].handle_right,bp[i+1].handle_left,bp[i+1].co,n);pts.extend([ob.matrix_world@q for q in (pp[:-1] if i<len(bp)-2 else pp)])
 return np.array([logical_u(q) for q in pts]),pts

def at_u(data,u):
 us,pts=data;k=int(np.searchsorted(us,u));assert 0<k<len(us);return pts[k-1].lerp(pts[k],float((u-us[k-1])/(us[k]-us[k-1])))

def worldtree(ob):
 dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();co=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,fs,all_triangles=True);ev.to_mesh_clear();return tree,len(co),len(fs)

def targets(body):
 bpy.context.view_layer.update();tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());board=bpy.data.objects['Guitar / ebony fretboard'];bt=BVHTree.FromObject(board,bpy.context.evaluated_depsgraph_get());biv=board.matrix_world.inverted();rows=[]
 def boardcast(origin,direction,distance):
  h,n,fi,d=bt.ray_cast(biv@origin,(biv.to_3x3()@direction).normalized(),distance)
  return (board.matrix_world@h if h is not None else None),n,fi,d
 for digit,u in enumerate([1.2456666666666667,1.355,1.4643333333333335]):
  st=bpy.data.objects['Guitar / string 3'];pt=at_u(bezier(st),u);origin=Vector((pt.x,-.88,pt.z));h,n,fi,dist=tree.ray_cast(origin,Vector((0,-1,0)),1.5);r={'kind':'toe','digit':digit+1,'u':u,'actual_target_world':list(pt),'radius':float(st.data.bevel_depth),'ray_origin':list(origin),'ray_direction':[0,-1,0],'hit':h is not None,'expected_source':2,'fallback_used':False}
  if h is not None:r.update(face_index=fi,source=provenance(body,fi),skin=list(h),normal=list(n),normal_condition=float(n.y),gap=float(pt.y-st.data.bevel_depth-h.y))
  rows.append(r)
 for u in [1.28,1.4]:
  fh,fn,ff,fd=boardcast(g(u,0,-2),Vector((0,1,0)),5);bh,bn,bf,bd=boardcast(g(u,0,-.2),Vector((0,-1,0)),5);assert fh is not None and bh is not None;y=(fh.y+bh.y)/2;boardorigin=g(u,-.3,y);edge,en,efi,ed=boardcast(boardorigin,V,.5);origin=g(u,-.110,y);h,n,fi,dist=tree.ray_cast(origin,-V,.7);r={'kind':'support','u':u,'actual_target_world':list(edge) if edge is not None else None,'calibrated_depth_y':y,'board_front_hit':list(fh),'board_back_hit':list(bh),'board_ray_origin':list(boardorigin),'board_ray_direction':list(V),'ray_origin':list(origin),'ray_direction':list(-V),'hit':h is not None,'expected_source':1,'fallback_used':False}
  if h is not None:r.update(face_index=fi,source=provenance(body,fi),skin=list(h),normal=list(n),normal_condition=float(n.dot(V)),gap=float((edge-h).dot(V)) if edge is not None else None)
  rows.append(r)
 return rows

def hit_triangle(body,row):
 me=body.data;me.calc_loop_triangles();origin=Vector(row['ray_origin']);direction=Vector(row['ray_direction']);choices=[]
 for tri in me.loop_triangles:
  if tri.polygon_index!=row['face_index']:continue
  pp=[me.vertices[i].co.copy() for i in tri.vertices];h=intersect_ray_tri(*pp,direction,origin,True)
  if h is None:continue
  err=(h-Vector(row['skin'])).length;mat=np.column_stack([np.array(pp[1]-pp[0]),np.array(pp[2]-pp[0])]);uv=np.linalg.lstsq(mat,np.array(h-pp[0]),rcond=None)[0];weights=np.array([1-uv.sum(),uv[0],uv[1]]);choices.append((err,list(tri.vertices),weights.tolist(),list(h)))
 assert choices,{'missing_triangle':row};result=min(choices,key=lambda x:x[0]);assert result[0]<5e-7,result;return {'vertex_indices':result[1],'barycentric':result[2],'ray_match_error':result[0],'actual_triangle_hit':result[3]}

def collision_audit(body,localfaces):
 used=sorted({i for f in localfaces for i in f.vertices});mp={v:i for i,v in enumerate(used)};ob=mesh('C27 authoring / actual hand plus retained collar',[body.data.vertices[i].co[:] for i in used],[[mp[i] for i in f.vertices] for f in localfaces]);local=A.audit(ob);bpy.data.objects.remove(ob,do_unlink=True);body.data.calc_loop_triangles();local_face_ids={f.index for f in localfaces};tris=[t for t in body.data.loop_triangles if t.polygon_index in local_face_ids];ht=BVHTree.FromPolygons([v.co[:] for v in body.data.vertices],[tuple(t.vertices) for t in tris],all_triangles=True);pairs=[]
 for name in ['Guitar / ebony fretboard','Guitar / neck']+['Guitar / string '+str(i+1) for i in range(6)]:
  ob=bpy.data.objects.get(name)
  if ob is None:pairs.append({'object':name,'missing':True});continue
  tree,nv,nt=worldtree(ob);over=ht.overlap(tree);pairs.append({'object':name,'actual_evaluated_vertices':nv,'actual_evaluated_triangles':nt,'surface_intersection_pairs':len(over),'sample_pairs':[list(x) for x in over[:12]],'method':'Actual evaluated mesh triangle BVH overlap; no primitive radius guess or U/V extrapolation.'})
 return {'local_audit':local,'guitar_surface_intersections':pairs,'limits':['Surface-overlap count is a triangle intersection test, not a complete solid-containment proof.','All same-source hand+collar faces self-tested separately; additional explicit ray inside-solid probes supplied.']}

def solid_probes(body,changed_ids):
 rows=[];directions=[Vector((.371,.613,.697)).normalized(),Vector((.739,.223,.635)).normalized()]
 for name in ['Guitar / ebony fretboard','Guitar / neck']:
  ob=bpy.data.objects.get(name)
  if ob is None:continue
  tree,nv,nt=worldtree(ob);inside=[];ambiguous=0
  for i in changed_ids:
   p=body.data.vertices[i].co;votes=[]
   for dr in directions:
    pos=p.copy();count=0
    for k in range(16):
     h,n,fi,d=tree.ray_cast(pos,dr,3)
     if h is None:break
     count+=1;pos=h+dr*1e-5
    votes.append(count%2)
   if votes==[1,1]:inside.append(i)
   elif votes[0]!=votes[1]:ambiguous+=1
  rows.append({'object':name,'changed_vertices_tested':len(changed_ids),'inside_by_two_independent_parity_rays':len(inside),'inside_vertex_sample':inside[:30],'ambiguous_ray_votes':ambiguous,'directions':[list(x) for x in directions],'limits':'Finite vertex probes, not continuous volume proof; combined with actual triangle intersection audit.'})
 return rows

def main():
 started=time.time();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;original=np.array([v.co[:] for v in me.vertices]);print('GUITAR_MESHES '+json.dumps([o.name for o in bpy.data.objects if o.name.startswith('Guitar /') and o.type=='MESH']));before_topo=topo(body);before=targets(body);assert all(r['hit'] and r['source']==r['expected_source'] and r['normal_condition']>.2 for r in before);prior_data=json.loads(prior.read_text());expected=[r['signed_near_string_y_gap'] for r in prior_data['declared_toe_pad_targets']]+[r['signed_lower_edge_gap_along_v'] for r in prior_data['declared_hold_support_targets']];assert max(abs(r['gap']-e) for r,e in zip(before,expected))<5e-7
 for r in before:r['actual_hit_triangle']=hit_triangle(body,r)
 # Original C8 source region remains exact. Fields are compact, zero with zero
 # first derivative at their boundaries and at the protected visible palm face.
 upper=np.array([q.value>0 for q in me.attributes['C23 actual upper local id'].data]);source=np.array([q.value>0 for q in me.attributes['C23 source vertex id'].data]);vv=np.array([logical_v(Vector(p)) for p in original]);front=smooth((original[:,1]+1.235)/.115);toe_mask=upper*front*smooth((vv+.072)/.045);wrist=(~upper)&(~source);support_mask=wrist*front*smooth((vv+.30)/.14)*smooth((-.07-vv)/.04);toe_mask[source]=0;support_mask[source]=0;desired=.0008;fields=[];delta=np.zeros_like(original)
 for group,mask,radius,direction in [('toe',toe_mask,.155,np.array([0,1,0.])),('support',support_mask,.22,VN)]:
  rr=[r for r in before if r['kind']==group];centers=np.array([r['skin'] for r in rr]);K=compact(np.linalg.norm(original[:,None,:]-centers[None,:,:],axis=2)/radius)*mask[:,None];matrix=[]
  for r in rr:
   tr=r['actual_hit_triangle'];matrix.append(np.array(tr['barycentric'])@K[tr['vertex_indices']])
  matrix=np.array(matrix);rhs=np.array([r['gap']-desired for r in rr]);coeff=np.linalg.solve(matrix,rhs);scalar=K@coeff;delta+=scalar[:,None]*direction;fields.append({'kind':group,'kernel':'compact Wendland C2 (1-r)^4(4r+1)','radius':radius,'centers_actual_skin':centers.tolist(),'constraint_matrix':matrix.tolist(),'rhs_gap_minus_target':rhs.tolist(),'coefficients':coeff.tolist(),'max_scalar_displacement':float(np.max(np.abs(scalar))),'collocation_residual':float(np.max(np.abs(matrix@coeff-rhs)))})
 displacement=np.linalg.norm(delta,axis=1);maxmove=float(displacement.max());changed=np.flatnonzero(displacement>1e-10);assert maxmove<=.085,{'STOP_displacement_bound':maxmove};candidate=original+delta;me.vertices.foreach_set('co',candidate.astype(np.float32).ravel());me.update();bpy.context.view_layer.update();actual=np.array([v.co[:] for v in me.vertices]);source_exact=bool(np.array_equal(actual[source],original[source]));assert source_exact
 # Predetermined, falsifiable gates. No correction iteration follows the result.
 after=targets(body);targets_unchanged=all(np.array_equal(np.array(r['actual_target_world']),np.array(p['actual_target_world'])) for r,p in zip(before,after));contacts_pass=all(r['hit'] and r.get('source')==r['expected_source'] and r.get('normal_condition',-1)>.2 and r.get('gap',-1)>=0 and r.get('gap',1)<=.002 for r in after)
 localfaces=[f for f in me.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];audits=collision_audit(body,localfaces);probes=solid_probes(body,changed.tolist());solid_pass=all(r.get('surface_intersection_pairs',1)==0 for r in audits['guitar_surface_intersections']) and all(r['inside_by_two_independent_parity_rays']==0 and r['ambiguous_ray_votes']==0 for r in probes);local=audits['local_audit'];final=topo(body);topology_same=final==before_topo;passed=contacts_pass and targets_unchanged and source_exact and topology_same and local['self_intersections']==0 and local['flipped_faces']==0 and solid_pass
 # Lock accounting verifies the former horizontal lip's visible front surface.
 front_locked=(original[:,1]<=-1.235)|source;plan={'intent_assessment':'Reference shows short rounded curls over neck and relaxed palm support. These fixed three third-string and two lower-edge sites are reasonable static design intents, not directly measurable facts of the single original image. All target objects/U values/world points remain fixed; six-string pressing is not required.','editable_regions':'Actual C25 upper-derived vertices for toe-Y field, actual new wrist vertices for support-V field, selected by saved source IDs. Original C8/non-hand is fixed.','lock_mask':'All original C8 source-ID points; visible front Y<=-1.235; compact kernels and smooth zero support masks preserve boundary continuity. No topology changes.','toe_V_mask':[-.072,-.027],'support_V_fades':{'lower':[-.30,-.16],'upper':[-.11,-.07]},'front_Y_fade':[-1.235,-1.12],'maximum_allowed_displacement':.085,'actual_maximum_displacement':maxmove,'changed_vertices':len(changed),'C8_source_locked_vertices':int(source.sum()),'C8_source_bit_exact':source_exact,'front_locked_count':int(front_locked.sum()),'front_locked_bit_exact':bool(np.array_equal(actual[front_locked],original[front_locked])),'fields':fields,'desired_gap_u':desired,'accepted_actual_gap_interval':[0,.002],'normal_dot_minimum':.2,'candidate_count':1,'no_iteration_or_parameter_sweep':True}
 receipt={'stage':'C27-one-bounded-static-contact-candidate','source_C25_native_sha256':source_sha,'source_C25_unchanged':sha(src)==source_sha,'script_sha256':sha(__file__),'plan':plan,'before_actual_targets':before,'after_actual_targets':after,'targets_world_unchanged':targets_unchanged,'contacts_numeric_gate_passed':contacts_pass,'before_topology':before_topo,'final_topology':final,'topology_bit_counts_unchanged':topology_same,'audits':audits,'inside_solid_vertex_probes':probes,'guitar_penetration_gate_passed':solid_pass,'render_gate_passed':passed,'seconds_before_render':time.time()-started,'limits':['Contact numerical pass is not art or animated grip approval.','Finite target rays, surface triangle intersections and finite inside probes do not prove all continuous collisions.','UV/groom/shape binding invalid; no color/rig/animation/GLB/engine/deploy.','The single reference does not establish exact fingerboard pressure, six-string pressing or hidden thumb anatomy.']};(out/'lock-and-displacement-plan.json').write_text(json.dumps(plan,indent=2)+'\n');(out/'ray-target-evidence.json').write_text(json.dumps({'before':before,'after':after,'actual_world_targets_unchanged':targets_unchanged},indent=2)+'\n');(out/'changed-vertices.json').write_text(json.dumps([{'vertex':int(i),'before':original[i].tolist(),'after':actual[i].tolist(),'displacement':(actual[i]-original[i]).tolist()} for i in changed])+'\n');bpy.context.preferences.filepaths.save_version=0;body['C27 status']='One bounded no-topology static contact study; art gate pending';native=out/('miao-c27-static-contact.blend' if passed else 'diagnostic-failed-contact-or-collision.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('GATE '+json.dumps({'targets':[r.get('gap') for r in after],'normal':[r.get('normal_condition') for r in after],'maxmove':maxmove,'self':local['self_intersections'],'flipped':local['flipped_faces'],'collisions':audits['guitar_surface_intersections'],'solidprobes':probes,'passed':passed}))
 if not passed:print('STOP one C27 candidate failed; no gray renders or geometry retry');return
 s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera;fl=cam.location.copy();fr=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['front','inside']:
  if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
  s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 cam.location=fl;cam.rotation_euler=fr;cam.data.ortho_scale=scale;assert sha(src)==source_sha;print('RESULT C27 two gray diagnostic views, independent art/contact review required')
main()
