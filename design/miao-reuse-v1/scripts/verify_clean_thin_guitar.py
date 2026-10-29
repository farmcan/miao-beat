"""Actual factory-startup GLB import audit, works on Blender 3.6 and 5.2."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);mode=args[1]
receipt=json.loads((root/'clean-prop-receipt.json').read_text());source=Path(receipt['source']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
if mode=='native':bpy.ops.wm.open_mainfile(filepath=str(root/'thin-electric-clean.blend'),load_ui=False,use_scripts=False)
else:
 # Remove unused factory-startup Material / grease-pencil data and render buffers BEFORE import.
 for collection in (bpy.data.materials,bpy.data.images):
  for item in list(collection):collection.remove(item,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(root/'thin-electric-clean.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];dg=bpy.context.evaluated_depsgraph_get();triangles=0;points=[];objects=[]
for o in meshes:
 m=o.evaluated_get(dg).to_mesh();m.calc_loop_triangles();triangles+=len(m.loop_triangles)
 points.extend(o.matrix_world@Vector(c) for c in o.bound_box)
 objects.append({'name':o.name,'vertices':len(m.vertices),'faces':len(m.polygons),'triangles':len(m.loop_triangles)})
lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
strings=[o for o in objects if o['name'] in receipt['strings']]
# Use the exact 24 names from measured original geometry classification.
measure=receipt['frets_source_measurement']
def findfrets(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if 'fret' in k.lower() and isinstance(v,list):
    names=[i if isinstance(i,str) else i.get('object',i.get('name')) for i in v]
    if len(names)==24:return names
   found=findfrets(v)
   if found:return found
 if isinstance(x,list):
  for v in x:
   found=findfrets(v)
   if found:return found
 return None
fret_names=findfrets(measure);assert fret_names, 'Missing exact 24-fret reference'
frets=[o for o in objects if o['name'] in fret_names]
summary={'blender':bpy.app.version_string,'mode':mode,'mesh_objects':len(meshes),'triangles':triangles,'world_bbox':{'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]},'strings':strings,'frets':frets,'images':[i.name for i in bpy.data.images],'materials':[m.name for m in bpy.data.materials],'node_groups':[g.name for g in bpy.data.node_groups],'texts':[t.name for t in bpy.data.texts],'textures':[t.name for t in bpy.data.textures],'font_objects':[o.name for o in bpy.data.objects if o.type=='FONT'],'source_sha256':sha(source),'glb_sha256':sha(root/'thin-electric-clean.glb')}
summary['pass']=len(strings)==6 and len(frets)==24 and all(o['triangles']>0 for o in strings+frets) and triangles==receipt['triangles'] and not summary['images'] and not summary['node_groups'] and not summary['texts'] and not summary['textures'] and all(m.startswith('Miao_') for m in summary['materials']) and summary['source_sha256']==receipt['source_sha256_before'] and 'Stand' not in bpy.data.objects and 'Killer' not in bpy.data.objects
(root/('verify-'+mode+'-'+bpy.app.version_string.split()[0]+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['blender','mode','mesh_objects','triangles','world_bbox','pass']}));assert summary['pass']
