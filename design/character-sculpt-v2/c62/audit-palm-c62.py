"""Read-only C62 fixed r2 actual self + evaluated guitar intersection audit."""
import bpy,bmesh,numpy as np,json,hashlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-palm-sculpt-c62';SRC=ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend';NATIVE=OUT/'miao-c62-main-local-palm-study.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();start=time.time()
h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';text=h.read_text();exec(compile(text[text.index('def smooth'):text.index('def main():')],str(h)+'#helpers','exec'),globals())
def snapshot(o):
 r={'name':o.name,'type':o.type,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'data_name':o.data.name if o.data else None,'modifiers':[(m.name,m.type) for m in o.modifiers],'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}
 if o.type in {'MESH','CURVE'}:r['geometry']=fingerprint(o)
 elif o.type=='CURVES':
  r['raw_attributes']={}
  for a in o.data.attributes:
   k='vector' if a.data_type in {'FLOAT_VECTOR','FLOAT2'} else 'color' if a.data_type in {'FLOAT_COLOR','BYTE_COLOR'} else 'value';n=(2 if a.data_type=='FLOAT2' else 3) if k=='vector' else 4 if k=='color' else 1;v=np.empty(len(a.data)*n,np.float32 if a.data_type not in {'INT','BOOLEAN'} else np.int32);a.data.foreach_get(k,v);r['raw_attributes'][a.name]=hashlib.sha256(v.tobytes()).hexdigest()
 return r
bpy.ops.wm.open_mainfile(filepath=str(SRC));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];before=arr(body.data);source_normals=np.empty(len(before)*3,np.float32);body.data.vertices.foreach_get('normal',source_normals);source_normals=source_normals.reshape(-1,3);protected={o.name:snapshot(o) for o in bpy.data.objects if o!=body};source_count=len(bpy.data.objects)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;actual=arr(me);me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32);changed=np.any(actual!=before,1);affected=changed[tri].any(1);aid=np.flatnonzero(affected)
def tree(co,ids=None):return BVHTree.FromPolygons(co,[tuple(x) for x in (tri if ids is None else tri[ids])],all_triangles=True)
def selfpairs(co):
 t=tree(co);return {(a,b) for a,b in t.overlap(t) if a<b and not(set(tri[a])&set(tri[b]))}
oldpairs=selfpairs(before);newpairs=selfpairs(actual);introduced=newpairs-oldpairs;local=[p for p in newpairs if affected[p[0]] or affected[p[1]]]
local_before=tree(before,aid);local_after=tree(actual,aid);cross=[];dg=bpy.context.evaluated_depsgraph_get();parity=[]
def solid_parity(t,p):
 votes=[]
 for dr in [Vector((1,.173,.331)).normalized(),Vector((.281,1,.193)).normalized(),Vector((.217,.353,1)).normalized()]:
  q=Vector(p);count=0
  for step in range(32):
   hit,n,i,d=t.ray_cast(q,dr,20.)
   if hit is None:break
   count+=1;q=hit+dr*1e-6
  votes.append(count%2)
 return 1 if votes==[1,1,1] else 0 if votes==[0,0,0] else -1
C=np.array([-.58,-1.19,1.80]);D=np.array([.78,0,-.625]);D/=np.linalg.norm(D);T=np.array([.625,0,.78]);T/=np.linalg.norm(T)
def attribution(ids):
 if not len(ids):return {'n':0}
 p=before[ids];s=(p-C)@D;t=(p-C)@T;ny=source_normals[ids,1];disp=np.linalg.norm(actual[ids]-before[ids],axis=1)
 return {'n':len(ids),'source_C52_indices':ids.tolist(),'source_coordinate_bbox':[p.min(0).tolist(),p.max(0).tolist()],'source_palm_axis_quantiles_0_25_50_75_100':np.percentile(s,[0,25,50,75,100]).tolist(),'source_lateral_quantiles_0_25_50_75_100':np.percentile(t,[0,25,50,75,100]).tolist(),'source_normal_y_quantiles_0_25_50_75_100':np.percentile(ny,[0,25,50,75,100]).tolist(),'source_shell_direction_counts':{'front_normal_y_lt_minus025':int((ny<-.25).sum()),'back_normal_y_gt025':int((ny>.25).sum()),'side_or_shoulder_normal':int((abs(ny)<=.25).sum())},'geometric_axial_region_counts':{'proximal_s_lt_minus003':int((s<-.03).sum()),'central_s_minus003_to014':int(((s>=-.03)&(s<.14)).sum()),'distal_s_gt014':int((s>=.14).sum())},'displacement_quantiles_0_25_50_75_100':np.percentile(disp,[0,25,50,75,100]).tolist(),'displacement_gt001_count':int((disp>.001).sum()),'semantic_limit':'Axial region and surface normal are measured; source C52 has no retained anatomical face provenance. Do not automatically label every rear shell sample torso or tip.'}
for ob in bpy.data.objects:
 if not ob.name.startswith('Guitar /') or ob.hide_render or ob.type not in {'MESH','CURVE'}:continue
 ev=ob.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();gc=[ob.matrix_world@v.co for v in m.vertices];gt=[tuple(t.vertices) for t in m.loop_triangles];t=BVHTree.FromPolygons(gc,gt,all_triangles=True);old=set(local_before.overlap(t));new=set(local_after.overlap(t));row={'object':ob.name,'actual_evaluated_triangles':len(gt),'affected_triangle_pairs_before':len(old),'affected_triangle_pairs_after':len(new),'new_triangle_pair_ids':len(new-old),'removed_triangle_pair_ids':len(old-new)};cross.append(row)
 if ob.name in ['Guitar / spruce soundboard','Guitar / rosewood body','Guitar / bridge','Guitar / neck','Guitar / ebony fretboard']:
  bm=bmesh.new();bm.from_mesh(m);bad=sum(not e.is_manifold for e in bm.edges);bm.free();pr={'object':ob.name,'nonmanifold_edges':bad,'rule':'Three oblique parity rays per changed actual body vertex, unanimous odd=inside, mixed=unknown; no nearest fallback.'}
  if bad==0:
   ids=np.flatnonzero(changed);a=np.array([solid_parity(t,before[i]) for i in ids]);b=np.array([solid_parity(t,actual[i]) for i in ids]);pr.update(samples=len(ids),inside_before=int((a==1).sum()),inside_after=int((b==1).sum()),unknown_before=int((a<0).sum()),unknown_after=int((b<0).sum()),new_inside_count=int(((b==1)&(a!=1)).sum()),new_inside_source_C52_index_sample=ids[(b==1)&(a!=1)][:20].tolist());pr['source_inside_attribution']=attribution(ids[a==1]);pr['result_inside_attribution']=attribution(ids[b==1])
  else:pr['status']='Open/nonmanifold evaluated mesh; closed-solid parity deliberately not claimed.'
  parity.append(pr)
 ev.to_mesh_clear()
p0=before[tri[affected]];p1=actual[tri[affected]];n0=np.cross(p0[:,1]-p0[:,0],p0[:,2]-p0[:,0]);n1=np.cross(p1[:,1]-p1[:,0],p1[:,2]-p1[:,0]);norm0=np.linalg.norm(n0,axis=1);norm1=np.linalg.norm(n1,axis=1);dots=(n0*n1).sum(1)/(norm0*norm1);exact={n:protected[n]==snapshot(bpy.data.objects[n]) for n in protected};r={'scope':'Read-only C62-main actual source/result body self and affected palm triangle vs actual evaluated guitar; not a static contact or art pass.','source_sha256':sha(SRC),'native_sha256':sha(NATIVE),'source_all_object_count':source_count,'protected_all_object_count':len(protected),'all_protected_objects_exact':all(exact.values()),'non_exact_names':[n for n,v in exact.items() if not v],'source_body_self_pairs':len(oldpairs),'result_body_self_pairs':len(newpairs),'new_global_self_pairs':len(introduced),'right_palm_non_neighbour_self_pairs':len(local),'new_self_pairs_sample':list(introduced)[:20],'topology':topo(me),'changed_vertices':int(changed.sum()),'affected_triangles':int(affected.sum()),'triangle_normal_reversals':int((dots<=0).sum()),'minimum_normal_dot':float(dots.min()),'area_ratio_quantiles_0_1_50_99_100':np.percentile(norm1/norm0,[0,1,50,99,100]).tolist(),'actual_guitar_triangle_intersections':cross,'actual_wood_solid_parity':parity,'all_C52_indices_exact':np.array_equal(np.array([v.value for v in me.attributes['C62 source C52 vertex index plus1'].data]),np.arange(1,len(actual)+1)),'all_legacy_C35_integer_attributes_stay0':all(all(v.value==0 for v in a.data) for a in me.attributes if a.domain=='POINT' and a.data_type=='INT' and a.name!='C62 source C52 vertex index plus1'),'elapsed_seconds':time.time()-start,'limits':['Actual triangle pairs count crossings, not penetration volume. No parity claim for open wood surfaces.','No continuous motion/string contact paths, per-note response, dynamics or natural playing pass.','Source75 self pairs in unchanged left-hand/right-ear regions remain external static blockers.','No UV/groom/rig/deformation approval.']};(OUT/'main-fresh-geometry-audit.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({k:r[k] for k in ['all_protected_objects_exact','protected_all_object_count','source_body_self_pairs','result_body_self_pairs','new_global_self_pairs','right_palm_non_neighbour_self_pairs','triangle_normal_reversals','actual_wood_solid_parity']}),flush=True)
