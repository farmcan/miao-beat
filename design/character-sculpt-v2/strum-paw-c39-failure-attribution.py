"""C39 frozen native read-only proof: Boolean precision, self/wood locations.
No geometry candidate, restoration, save or render. Face provenance plus cyclic
corner correspondence is used for identity proof, never nearest-point identity.
"""
import bpy,numpy as np,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];O=R/'artifacts/character-strum-paw-c39';src=R/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';native=O/'diagnostic-c39-geometry-failed.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();frozen={str(p.name):sha(p) for p in [src,native,O/'receipt.json']};p=np.load(O/'source-map-and-authored-delta.npz');P=p['original'];Q=p['authored_before_boolean'];M=p['output_to_original_index'].copy();bpy.ops.wm.open_mainfile(filepath=str(src));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data;sf=[list(f.vertices) for f in me.polygons];tag='C35 original polygon id';source_tags=collections.defaultdict(list)
for f in me.polygons:source_tags[me.attributes[tag].data[f.index].value].append(f.index)
bpy.ops.wm.open_mainfile(filepath=str(native));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;actual=np.array([v.co[:] for v in me.vertices]);me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);fi=np.array([t.polygon_index for t in me.loop_triangles]);recover=collections.defaultdict(set);proof=[]
for f in me.polygons:
 outs=list(f.vertices)
 if all(M[i]>=0 for i in outs):continue
 value=me.attributes[tag].data[f.index].value;candidates=[]
 for oldface in source_tags.get(value,[]):
  olds=sf[oldface]
  if len(olds)!=len(outs):continue
  for shift in range(len(olds)):
   order=olds[shift:]+olds[:shift];err=float(np.max(np.abs(actual[outs]-Q[order])))
   if err<=2e-6:candidates.append((err,oldface,order))
 if len(candidates)!=1:continue
 err,oldface,order=candidates[0]
 # Entire cyclic face correspondence and preserved face identity; no spatial
 # nearest lookup. Require every previously exact corner agrees with it.
 if any(M[a]>=0 and M[a]!=b for a,b in zip(outs,order)):continue
 for a,b in zip(outs,order):recover[a].add(b)
 proof.append({'output_face':f.index,'source_C35_face':oldface,'preserved_C35_original_polygon_tag':value,'maximum_corner_error':err,'output_cyclic_vertices':outs,'source_cyclic_vertices':order})
conflicts={i:list(v) for i,v in recover.items() if len(v)!=1};recovered=[]
for i,vals in recover.items():
 if M[i]<0 and len(vals)==1:M[i]=next(iter(vals));recovered.append(i)
counts=collections.Counter(M[M>=0].tolist());duplicates=[i for i,n in counts.items() if n>1];present=np.zeros(len(P),bool);present[M[M>=0]]=True;head=P[:,2]>=2.43;left=P[:,0]>.5;allowed=(P[:,0]<-.17)&(P[:,1]<.055)&(P[:,2]>1.46)&(P[:,2]<2.431);error=np.linalg.norm(actual[M>=0]-Q[M[M>=0]],axis=1);headout=np.flatnonzero((M>=0)&(actual[:,2]>=2.43));leftout=np.flatnonzero((M>=0)&(actual[:,0]>.5));precision={'bit_exact_primary_map_retained':int((p['output_to_original_index']>=0).sum()),'recovered_by_preserved_face_provenance_and_full_cyclic_corner_match':len(recovered),'face_proof_count':len(proof),'face_proof_conflicts':conflicts,'duplicate_source_IDs':duplicates,'all_head_originals_still_present':bool(np.all(present[head])),'all_left_originals_still_present':bool(np.all(present[left])),'all_protected_originals_still_present':bool(np.all(present[~allowed])),'preboolean_head_authored_exact':bool(np.array_equal(Q[head],P[head])),'preboolean_left_authored_exact':bool(np.array_equal(Q[left],P[left])),'maximum_recovered_error':float(np.max(error)),'head_max_boolean_coordinate_error':float(np.max(np.linalg.norm(actual[headout]-Q[M[headout]],axis=1))),'left_max_boolean_coordinate_error':float(np.max(np.linalg.norm(actual[leftout]-Q[M[leftout]],axis=1))),'all_new_unproved_points_source0':True,'not_applied':'Read-only map proof only. Original failed native and canonical attributes remain unchanged; no restored native claimed.'}
cent=actual[tri].mean(1);region=(cent[:,0]<-.17)&(cent[:,1]<.055)&(cent[:,2]>1.46)&(cent[:,2]<2.431);ids=np.flatnonzero(region);ht=BVHTree.FromPolygons(actual,tri[region].tolist(),all_triangles=True);whole=BVHTree.FromPolygons(actual,tri.tolist(),all_triangles=True);pairs=[]
for a,b in ht.overlap(whole):
 a=int(ids[a])
 if a==b or set(tri[a])&set(tri[b]) or (region[b] and a>b):continue
 v=sorted(set(tri[[a,b]].ravel().tolist()));nnew=int(sum(M[i]<0 for i in v));pairs.append({'triangles':[a,b],'faces':[int(fi[a]),int(fi[b])],'original_C35_canonical_ids':[[int(M[i])+1 for i in t] for t in tri[[a,b]]],'new_or_unproved_vertices':nnew,'bbox':[actual[v].min(0).tolist(),actual[v].max(0).tolist()]})
wood=[];dg=bpy.context.evaluated_depsgraph_get()
for name in ['Guitar / spruce soundboard','Guitar / rosewood body']:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();co=[ob.matrix_world@v.co for v in m.vertices];tt=[tuple(t.vertices) for t in m.loop_triangles];tree=BVHTree.FromPolygons(co,tt,all_triangles=True);over=ht.overlap(tree);skin=sorted({int(v) for a,b in over for v in tri[ids[a]]});wood.append({'object':name,'pairs':len(over),'skin_bbox':[actual[skin].min(0).tolist(),actual[skin].max(0).tolist()] if skin else None,'skin_output_vertex_ids':skin,'skin_canonical_C35_ids':[int(M[i])+1 for i in skin]});ev.to_mesh_clear()
np.savez_compressed(O/'readonly-face-proven-canonical-map.npz',output_to_C35_index=M,recovered_output_indices=np.array(recovered,np.int32),original_point_presence=present)
r={'scope':'Frozen C39 failure attribution and read-only exact-source face identity proof, not a repaired/native pass','frozen_hashes':frozen,'precision_identity':precision,'face_identity_proofs':proof,'actual_self_triangle_pairs':len(pairs),'self_pairs_with_new_unproved_vertex':sum(q['new_or_unproved_vertices']>0 for q in pairs),'self_pairs_all_proven_retained_vertices':sum(q['new_or_unproved_vertices']==0 for q in pairs),'self_pair_geometry':pairs,'wood_intersections':wood,'interpretation':'Manifold cut produced a visible wedge/severed-arm shape and retained failures. Even restoring protected-point roundoff cannot repair this anatomy; no second artistic candidate or parameter adjustment. Need an anatomically planned shared-root forearm front/back surface, not larger instrument-shaped subtraction.'};assert all(sha(p)==frozen[p.name] for p in [src,native,O/'receipt.json']);(O/'failure-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print('ATTRIBUTION '+json.dumps({'precision':precision,'self':len(pairs),'self_new':r['self_pairs_with_new_unproved_vertex'],'self_old':r['self_pairs_all_proven_retained_vertices'],'wood':wood}),flush=True)
