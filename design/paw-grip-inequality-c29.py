"""C29 one collision-aware static feasibility solve, no topology/target changes.
Actual BVH directional outside inequalities + five contacts + physical Laplace energy.
OSQP runs in isolated external Python to avoid Blender ABI/dependency changes.
"""
import bpy,bmesh,numpy as np,json,sys,math,time,hashlib,argparse,subprocess
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri,interpolate_bezier
P=argparse.ArgumentParser();P.add_argument('--solver-python',required=True);P.add_argument('--out',default='artifacts/character-paw-grip-c29');args=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[1];out=root/args.out;out.mkdir(parents=True,exist_ok=True);src=root/'artifacts/character-paw-shared-surface-c25/miao-c25-shared-surface-diagnostic.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source_sha=sha(src);sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
# Reuse tested actual-string, provenance, topology and collision helpers, not a model builder.
helper=root/'design/character-sculpt-v2/paw-grip-contact-c27.py';text=helper.read_text();exec(compile(text[text.index('O=Vector'):text.index('def main():')],str(helper)+'#read-only-helpers','exec'),globals());legacy_targets=targets

def actual_targets(body):
 rows=legacy_targets(body);tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
 for row in rows:
  if row['kind']!='support':continue
  target=Vector(row['actual_target_world']);origin=target+V*.08;h,n,fi,d=tree.ray_cast(origin,-V,.8);row.update(ray_origin=list(origin),ray_direction=list(-V),ray_origin_rule='actual board lower edge + .08u V; targets unchanged',hit=h is not None)
  if h is not None:row.update(face_index=fi,source=provenance(body,fi),skin=list(h),normal=list(n),normal_condition=n.dot(V),gap=(target-h).dot(V))
 return rows

def object_geometry(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();co=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,fs,all_triangles=True);ev.to_mesh_clear();return {'object':ob.name,'co':co,'triangles':fs,'tree':tree}

def main():
 started=time.time();bpy.ops.wm.open_mainfile(filepath=str(src));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;scene=bpy.context.scene;original=np.array([v.co[:] for v in me.vertices]);before_topo=topo(body);before=actual_targets(body);assert all(r['hit'] and r['source']==r['expected_source'] and r['normal_condition']>.2 for r in before)
 for row in before:row['actual_hit_triangle']=hit_triangle(body,row)
 source=np.array([x.value>0 for x in me.attributes['C23 source vertex id'].data]);upper=np.array([x.value>0 for x in me.attributes['C23 actual upper local id'].data]);hand_ids=np.flatnonzero(~source);vv=np.array([logical_v(Vector(p)) for p in original]);locked=source|(original[:,1]<=-1.17)|(vv<=-.30);free=np.flatnonzero(~locked);index={int(v):i for i,v in enumerate(free)};n=len(free);directions=np.tile(VN if 'VN' in globals() else np.array(V),(len(original),1));directions[upper]=[0,1,0];axis_by_kind={'toe':np.array([0.,1.,0.]),'support':np.array(V)};s=np.zeros(n);maxmove=.095;clearance=.0004
 # All fixed world obstacle geometry is retained, including exact evaluated tube meshes.
 names=['Guitar / ebony fretboard','Guitar / neck']+['Guitar / string '+str(i+1) for i in range(6)];obstacles=[object_geometry(bpy.data.objects[name]) for name in names]
 adjacency={int(i):set() for i in hand_ids}
 for e in me.edges:
  a,b=e.vertices
  if a in adjacency:adjacency[a].add(b)
  if b in adjacency:adjacency[b].add(a)
 # Physical Laplace displacement, including fixed neighbors; no SciPy in Blender.
 Lr=[];Lc=[];Ld=[];lrow=0
 relevant=set(int(i) for i in free)
 for i in free:relevant.update(adjacency.get(int(i),[]))
 for i in sorted(relevant):
  nb=adjacency.get(i,set())
  if not nb:continue
  weights=np.array([1/max(np.linalg.norm(original[j]-original[i]),1e-5) for j in nb]);weights/=weights.sum();neighbors=list(nb)
  for dim in range(3):
   if i in index:Lr.append(lrow);Lc.append(index[i]);Ld.append(float(directions[i,dim]))
   for j,w in zip(neighbors,weights):
    if j in index:Lr.append(lrow);Lc.append(index[j]);Ld.append(float(-w*directions[j,dim]))
   lrow+=1
 constraints=[];dedup=set();dense_count=0;vertex_count=0;unmovable=[]
 def add_constraint(ids,weights,axis,bound,origin_info):
  row={}
  for i,w in zip(ids,weights):
   if int(i) in index:
    j=index[int(i)];row[j]=row.get(j,0.)+float(w*np.dot(directions[int(i)],axis))
  row={j:v for j,v in row.items() if abs(v)>1e-12};key=(tuple((j,round(v,7)) for j,v in sorted(row.items())),round(float(bound),7))
  if key in dedup:return False
  dedup.add(key)
  if not row:
   if bound<-1e-7:unmovable.append({'bound':float(bound),'source':origin_info})
   return False
  constraints.append({'row':row,'upper':float(bound),'source':origin_info});return True
 def actual_outside_rows(ids,weights,kind,current_point,reason):
  axis=axis_by_kind[kind];p0=np.array(weights)@original[list(ids)];point=Vector(current_point);axisv=Vector(axis);added=0
  for ob in obstacles:
   h,norm,fi,d=ob['tree'].ray_cast(point-axisv*.30,axisv,.75)
   if h is None:continue
   bound=float((np.array(h)-p0)@axis-clearance)
   if bound>maxmove+.001:continue
   info={'reason':reason,'object':ob['object'],'surface_triangle':fi,'actual_ray_origin':list(point-axisv*.30),'ray_direction':axis.tolist(),'actual_entry_world':list(h),'actual_entry_normal':list(norm),'skin_triangle_vertices':[int(i) for i in ids],'barycentric':[float(x) for x in weights],'preferred_outside_direction':(-axis).tolist()};added+=add_constraint(ids,weights,axis,bound,info)
  return added
 # Entire editable-region vertex constraints, including inherited tube penetration.
 for i in hand_ids:
  kind='toe' if upper[i] else 'support';vertex_count+=actual_outside_rows([int(i)],[1.],kind,original[i],'all actual hand vertices')
 # Dense actual-surface constraints explicitly cover the C27 failure neighborhood.
 me.calc_loop_triangles();initialtris=[(tuple(t.vertices),t.polygon_index) for t in me.loop_triangles if provenance(body,t.polygon_index)>0]
 for ids,face in initialtris:
  pp=original[list(ids)];us=[logical_u(Vector(p)) for p in pp];vs=[logical_v(Vector(p)) for p in pp];sid=provenance(body,face);wrist_zone=sid==1 and max(us)>=1.30 and min(us)<=1.48 and max(vs)>=-.20 and min(vs)<=-.055;toe_zone=sid==2 and max(us)>=1.18 and min(us)<=1.52 and max(vs)>=-.075 and min(vs)<=.055
  if not(wrist_zone or toe_zone):continue
  for j in range(5):
   for k in range(5-j):
    weights=np.array([j/4,k/4,1-(j+k)/4]);point=weights@pp;dense_count+=actual_outside_rows(ids,weights,'toe' if sid==2 else 'support',point,'dense actual face coverage C27 wrist and upper contact zones')
 eq=[]
 for row in before:
  tri=row['actual_hit_triangle'];axis=axis_by_kind[row['kind']];rr={}
  for i,w in zip(tri['vertex_indices'],tri['barycentric']):
   if i in index:rr[index[i]]=float(w*np.dot(directions[i],axis))
  assert rr,{'locked_contact':row};eq.append({'row':rr,'value':row['gap']-.0008,'kind':row['kind'],'fixed_target_world':row['actual_target_world']})
 def update(x):
  candidate=original.copy();candidate[free]+=x[:,None]*directions[free];me.vertices.foreach_set('co',candidate.astype(np.float32).ravel());me.update();bpy.context.view_layer.update()
 def intersections():
  me.calc_loop_triangles();tris=[(tuple(t.vertices),t.polygon_index) for t in me.loop_triangles if .75<me.polygons[t.polygon_index].center.x<1.62 and me.polygons[t.polygon_index].center.y<-.60 and 1.3<me.polygons[t.polygon_index].center.z<2.35];ht=BVHTree.FromPolygons([v.co[:] for v in me.vertices],[q[0] for q in tris],all_triangles=True);pairs=[]
  for ob in obstacles:
   over=ht.overlap(ob['tree']);pairs.append({'object':ob['object'],'pairs':over,'obstacle':ob})
  return tris,pairs
 def collision_cuts(tris,pairs):
  added=0;unresolved=[]
  for item in pairs:
   ob=item['obstacle']
   for ti,oi in item['pairs']:
    ids,face=tris[ti];pp=[me.vertices[i].co.copy() for i in ids];qq=[ob['co'][i] for i in ob['triangles'][oi]];points=[]
    for start,end in list(zip(pp,pp[1:]+pp[:1])):
     length=(end-start).length
     if length<1e-10:continue
     dr=(end-start)/length;h=intersect_ray_tri(*qq,dr,start,True)
     if h is not None and -1e-7<=(h-start).dot(dr)<=length+1e-7:points.append(h)
    for start,end in list(zip(qq,qq[1:]+qq[:1])):
     length=(end-start).length
     if length<1e-10:continue
     dr=(end-start)/length;h=intersect_ray_tri(*pp,dr,start,True)
     if h is not None and -1e-7<=(h-start).dot(dr)<=length+1e-7:points.append(h)
    if not points:unresolved.append({'object':ob['object'],'hand_triangle':ti,'obstacle_triangle':oi,'reason':'BVH pair without noncoplanar edge intersection; tangency/epsilon unresolved, not called zero penetration'});continue
    matrix=np.column_stack([np.array(pp[1]-pp[0]),np.array(pp[2]-pp[0])])
    for point in points:
     uv=np.linalg.lstsq(matrix,np.array(point-pp[0]),rcond=None)[0];weights=np.array([1-uv.sum(),uv[0],uv[1]]);sid=provenance(body,face);added+=actual_outside_rows(ids,weights,'toe' if sid==2 else 'support',point,'exact active triangle intersection witness')
  return added,unresolved
 # Baseline intersection witnesses enter the SAME feasibility problem, not a later candidate.
 baseline_tris,baseline_pairs=intersections();baseline_counts={r['object']:len(r['pairs']) for r in baseline_pairs};baseline_added,unresolved=collision_cuts(baseline_tris,baseline_pairs);trace=[];solved=False;status='not-started';solver_info=None
 for outer in range(8):
  ar=[];ac=[];ad=[];lo=[];hi=[]
  for i in range(n):ar.append(len(lo));ac.append(i);ad.append(1.);lo.append(-maxmove);hi.append(maxmove)
  for r in eq:
   ri=len(lo)
   for j,v in r['row'].items():ar.append(ri);ac.append(j);ad.append(v)
   lo.append(r['value']);hi.append(r['value'])
  for r in constraints:
   ri=len(lo)
   for j,v in r['row'].items():ar.append(ri);ac.append(j);ad.append(v)
   lo.append(-np.inf);hi.append(r['upper'])
  inp=out/('qp-'+str(outer)+'.npz');res=out/('qp-'+str(outer)+'-result.npz');np.savez(inp,n=n,A_rows=ar,A_cols=ac,A_data=ad,lower=lo,upper=hi,L_rows=Lr,L_cols=Lc,L_data=Ld,L_nrows=lrow,warm=s);proc=subprocess.run([args.solver_python,str(root/'design/paw-grip-c29-solve.py'),str(inp),str(res)],capture_output=True,text=True,timeout=50);(out/('qp-'+str(outer)+'-solver.log')).write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr;solver_info=json.loads(res.with_suffix('.json').read_text());status=solver_info['status'];step={'active_set_iteration':outer,'constraints':len(constraints),'solver':solver_info}
  if status not in ['solved','solved inaccurate']:
   cert=np.load(res)['primal_infeasibility_certificate'];topcert=[]
   if len(cert)==len(lo):
    for ri in np.argsort(np.abs(cert))[-30:][::-1]:
     entry={'constraint_row':int(ri),'certificate_weight':float(cert[ri]),'lower':lo[ri] if np.isfinite(lo[ri]) else None,'upper':hi[ri] if np.isfinite(hi[ri]) else None}
     if ri<n:entry.update(type='vertex displacement bound',actual_vertex=int(free[ri]))
     elif ri<n+len(eq):entry.update(type='fixed original contact target',contact=eq[ri-n])
     else:entry.update(type='actual obstacle outside inequality',source=constraints[ri-n-len(eq)]['source'])
     topcert.append(entry)
   step['largest_primal_infeasibility_certificate_rows']=topcert;trace.append(step);break
  s=np.load(res)['x'];update(s);now=actual_targets(body);tris,pairs=intersections();counts={r['object']:len(r['pairs']) for r in pairs};step.update(actual_targets=[{'kind':r['kind'],'gap':r.get('gap'),'normal':r.get('normal_condition'),'source':r.get('source')} for r in now],actual_triangle_intersections=counts,actual_max_displacement=float(np.max(np.abs(s))));trace.append(step);print('ACTIVE '+json.dumps(step),flush=True)
  if not any(counts.values()):solved=True;break
  added,unresolved=collision_cuts(tris,pairs);step['new_actual_intersection_cuts']=added;step['unresolved_pairs']=unresolved
  if not added:break
 finaltargets=actual_targets(body);actual=np.array([v.co[:] for v in me.vertices]);fixedexact=bool(np.array_equal(actual[locked],original[locked]));sourceexact=bool(np.array_equal(actual[source],original[source]));targetsunmoved=all(np.array_equal(np.array(r['actual_target_world']),np.array(q['actual_target_world'])) for r,q in zip(before,finaltargets));contacts_pass=all(r['hit'] and r.get('source')==r['expected_source'] and r.get('normal_condition',-1)>.2 and 0<=r.get('gap',-1)<=.002 for r in finaltargets);localfaces=[f for f in me.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];audit=collision_audit(body,localfaces);parity=solid_probes(body,hand_ids.tolist());collision_pass=all(r.get('surface_intersection_pairs',1)==0 for r in audit['guitar_surface_intersections']) and all(r['inside_by_two_independent_parity_rays']==0 and r['ambiguous_ray_votes']==0 for r in parity);finaltopo=topo(body);local=audit['local_audit'];passed=solved and contacts_pass and targetsunmoved and fixedexact and sourceexact and not unmovable and collision_pass and local['self_intersections']==0 and local['flipped_faces']==0 and finaltopo==before_topo
 plan={'method':'One OSQP collision-aware feasibility/physical Laplace solve with actual-BVH active inequalities; active-set re-solves are one candidate, no parameter sweep.','unknowns':n,'locked_vertices':int(locked.sum()),'locked_C8_source_vertices':int(source.sum()),'lock_rules':['all original C8 source-ID vertices','visible hand front Y<=-1.17','arm-root/palm V<=-.30'],'preferred_directions':{'upper_scalar_positive':[0,1,0],'upper_escape':[0,-1,0],'wrist_scalar_positive':list(V),'wrist_escape':list(-V)},'max_allowed_displacement':maxmove,'desired_target_gap':.0008,'accepted_target_gaps':[0,.002],'generic_actual_obstacle_clearance':clearance,'vertex_actual_BVH_constraints':vertex_count,'dense_actual_face_constraints':dense_count,'initial_actual_intersection_cuts':baseline_added,'total_constraints':len(constraints),'physical_Laplace_rows':lrow,'initial_actual_intersections':baseline_counts,'fixed_targets':eq,'unmovable_inequalities':unmovable,'solver_python':args.solver_python,'local_solver_script_sha256':sha(root/'design/paw-grip-c29-solve.py'),'locks_bit_exact':fixedexact,'source_bit_exact':sourceexact}
 receipt={'stage':'C29-one-collision-aware-feasibility','source_C25_native_sha256':source_sha,'source_unchanged':sha(src)==source_sha,'script_sha256':sha(__file__),'helper_script_sha256':sha(helper),'plan':plan,'active_set_trace':trace,'solver_final_status':status,'before_actual_targets':before,'after_actual_targets':finaltargets,'contact_target_world_unchanged':targetsunmoved,'contact_numeric_gate_passed':contacts_pass,'final_topology':finaltopo,'topology_counts_unchanged':finaltopo==before_topo,'actual_geometry_audit':audit,'inside_solid_probes':parity,'actual_collision_gate_passed':collision_pass,'unresolved_tangency_pairs':unresolved,'render_gate_passed':passed,'seconds_before_render':time.time()-started,'limits':['Discrete inequality infeasibility is not proof the original artistic pose is globally impossible.','Actual mesh BVH intersections and parity probes are tested; no AABB-negative substitute is used.','No numerical feasibility or zero intersections alone constitutes independent art/contact approval.','No color/hair/rig/animation/GLB/engine/deployment; old bindings invalid.']};(out/'constraint-plan.json').write_text(json.dumps(plan,indent=2)+'\n');(out/'actual-ray-evidence.json').write_text(json.dumps({'before':before,'after':finaltargets},indent=2)+'\n');(out/'active-inequalities.json').write_text(json.dumps(constraints)+'\n');changed=np.flatnonzero(np.linalg.norm(actual-original,axis=1)>0);(out/'changed-vertices.json').write_text(json.dumps([{'vertex':int(i),'before':original[i].tolist(),'after':actual[i].tolist()} for i in changed])+'\n');bpy.context.preferences.filepaths.save_version=0;native=out/('miao-c29-feasible-contact.blend' if passed else 'diagnostic-c29-infeasible-or-collision.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({'status':status,'contacts':contacts_pass,'collision':collision_pass,'self':local['self_intersections'],'flipped':local['flipped_faces'],'passed':passed,'native':receipt['native_sha256']}),flush=True)
 if not passed:return
 scene.cycles.samples=16;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.use_border=False;scene.render.use_crop_to_border=False;cam=scene.camera;fl=cam.location.copy();fr=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['front','inside']:
  if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
  scene.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 cam.location=fl;cam.rotation_euler=fr;cam.data.ortho_scale=scale;assert sha(src)==source_sha
main()
