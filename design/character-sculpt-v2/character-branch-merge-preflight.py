"""Read-only lineage check for merging accepted head and rebuilt hand branches.
No nearest-surface substitution, geometry editing, save, or art acceptance.
"""
import bpy, numpy as np, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/character-branch-merge-preflight';OUT.mkdir(parents=True,exist_ok=True)
FILES={'c8':'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend','c20':'artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend','c25':'artifacts/character-paw-shared-surface-c25/miao-c25-shared-surface-diagnostic.blend'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NAME='Miao / continuous pear and rounded-square face'
co={};snap={};source_ids=None
for tag,file in FILES.items():
 p=ROOT/file;before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));ob=bpy.data.objects[NAME];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
 ar=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',ar);co[tag]=ar.reshape(-1,3).copy()
 indices=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',indices)
 counts=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_total',counts)
 ids=me.attributes.get('C23 source vertex id')
 if ids:
  source_ids=np.empty(len(ids.data),np.int32);ids.data.foreach_get('value',source_ids)
 snap[tag]={'source':file,'source_sha256':before,'vertices':len(me.vertices),'faces':len(me.polygons),'ordered_topology_sha256':hashlib.sha256(indices.tobytes()+counts.tobytes()).hexdigest(),'attributes':[(a.name,a.data_type,a.domain) for a in me.attributes],'uv_layers':[u.name for u in me.uv_layers],'materials':[m.name if m else None for m in me.materials],'shape_keys':[k.name for k in ob.data.shape_keys.key_blocks] if ob.data.shape_keys else [],'source_identity_attribute':bool(ids)}
 features={}
 for x in bpy.context.scene.objects:
  if x.name.startswith(('Face /','C6 /','C7 /')):
   a=np.empty(len(x.data.vertices)*3,np.float32) if x.type=='MESH' else None
   if a is not None:x.data.vertices.foreach_get('co',a)
   features[x.name]={'type':x.type,'geometry_sha256':hashlib.sha256(a.tobytes()).hexdigest() if a is not None else None,'matrix_world':list(map(list,x.matrix_world)),'hide_render':x.hide_render,'materials':[m.name if m else None for m in getattr(x.data,'materials',[])]}
 snap[tag]['face_features']=features
 ev.to_mesh_clear();assert sha(p)==before
result={'scope':'read-only branch correspondence feasibility; no merged candidate created','snapshots':snap}
if co['c8'].shape==co['c20'].shape and snap['c8']['ordered_topology_sha256']==snap['c20']['ordered_topology_sha256']:
 delta=co['c20']-co['c8'];changed=np.linalg.norm(delta,axis=1)>1e-7
 retain=source_ids>0;assert source_ids[retain].max()<=len(delta)
 missing=np.ones(len(delta),bool);missing[source_ids[retain]-1]=False
 olderr=np.linalg.norm(co['c25'][retain]-co['c8'][source_ids[retain]-1],axis=1)
 result['correspondence']={'ordered_head_body_topology_matches':True,'changed_vertices':int(changed.sum()),'changed_bbox_min':co['c8'][changed].min(axis=0).tolist() if changed.any() else None,'changed_bbox_max':co['c8'][changed].max(axis=0).tolist() if changed.any() else None,'c25_retained_source_vertices':int(retain.sum()),'c25_retained_source_error_max':float(olderr.max()),'c20_changed_vertices_missing_from_c25':int((changed&missing).sum()),'maximum_missing_delta':float(np.linalg.norm(delta[missing],axis=1).max()) if missing.any() else 0.,'method_if_valid':'transfer evaluated C20-C8 delta only through exact C23 source vertex identity; preserve all new C25 hand vertices'}
else:result['correspondence']={'ordered_head_body_topology_matches':False,'reason':'Index transfer unproven; do not use approximate nearest matching as accepted lineage'}
(OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps(result),flush=True)
