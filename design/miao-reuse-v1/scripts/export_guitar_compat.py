"""Export the reviewed unmodified source guitar to standard embedded glTF 2.0."""
import bpy, json, hashlib, sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
mesh_objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(mesh_objects)==1, 'Expected reviewed single joined source mesh'
bpy.ops.object.select_all(action='DESELECT')
for o in mesh_objects:o.select_set(True)
bpy.context.view_layer.objects.active=mesh_objects[0]
before={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'objects':[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'dimensions_m':list(o.dimensions),'scale':list(o.scale),'uv_layers':list(o.data.uv_layers.keys())} for o in mesh_objects],'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images]}
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_image_format='AUTO',export_animations=False,export_cameras=False,export_lights=False,export_extras=False,export_draco_mesh_compression_enable=False)
receipt={'blender':bpy.app.version_string,'source':str(src),'output':str(out),'before':before,'source_after_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_bytes':out.stat().st_size,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'asset_modification':'None: source geometry, material, UV and transform unchanged; export only; no .blend saved','blender36_compatibility':'pending downstream import validation','axes':'glTF Y-up metres; Blender importer restores Z-up'}
assert receipt['source_after_sha256']==before['source_sha256']
(out.parent/'export-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
