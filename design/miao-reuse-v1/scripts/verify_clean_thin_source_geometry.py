"""Compare every delivered native vertex and topology to evaluated source under one rigid matrix."""
import bpy,numpy as np,json,hashlib,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
root=Path(args[0]).resolve() if args else Path(__file__).resolve().parents[3]/'artifacts/miao-reuse-v1/thin-electric-clean'
r=json.loads((root/'clean-prop-receipt.json').read_text());A=np.array(r['source_to_canonical_rigid_matrix']);src=Path(args[1]).resolve() if len(args)>1 else Path(r['source']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();expected={}
for item in r['source_mesh_fingerprints']:
 o=bpy.data.objects[item['source_object']];m=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',v)
 inds=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',inds);starts=np.empty(len(m.polygons),dtype=np.int32);m.polygons.foreach_get('loop_start',starts)
 expected[o.name]=(np.c_[v.reshape(-1,3),np.ones(len(m.vertices))]@(A@np.array(o.matrix_world)).T,hashlib.sha256(inds.tobytes()+starts.tobytes()).hexdigest())
bpy.ops.wm.open_mainfile(filepath=str(root/'thin-electric-clean.blend'),load_ui=False,use_scripts=False);rows=[]
for name,(e,top) in expected.items():
 m=bpy.data.objects[name].data;v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',v)
 inds=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',inds);starts=np.empty(len(m.polygons),dtype=np.int32);m.polygons.foreach_get('loop_start',starts)
 rows.append({'object':name,'vertices':len(m.vertices),'faces':len(m.polygons),'max_world_error_m':float(np.linalg.norm(e[:,:3]-v.reshape(-1,3),axis=1).max()),'topology_exact':top==hashlib.sha256(inds.tobytes()+starts.tobytes()).hexdigest()})
rot=A[:3,:3];summary={'source_sha256':sha(src),'source_sha256_unchanged':sha(src)==r['source_sha256_before'],'rigid_rotation_determinant':float(np.linalg.det(rot)),'rigid_rotation_orthogonality_error':float(np.max(np.abs(rot.T@rot-np.eye(3)))),'objects':rows,'max_vertex_world_error_m':max(x['max_world_error_m'] for x in rows),'all_topology_exact':all(x['topology_exact'] for x in rows),'body_thickness_m':bpy.data.objects['Body'].dimensions.y,'images':len(bpy.data.images),'nodegroups':len(bpy.data.node_groups),'texts':len(bpy.data.texts),'old_materials':[m.name for m in bpy.data.materials if not m.name.startswith('Miao_')]}
summary['pass']=summary['source_sha256_unchanged'] and summary['all_topology_exact'] and summary['max_vertex_world_error_m']<5e-7 and abs(summary['body_thickness_m']-.0413340983)<5e-7
(root/'source-preservation-audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='objects'}));assert summary['pass']
