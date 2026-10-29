"""Read-only geometry/import audit of the released pure-CC0 prop in current Blender."""
import argparse
import sys
import bpy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/miao-eight-key-prop-probe-2026-10-30/prop-export'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model',type=Path,default=OUT/'eight-key-cc0-prop.glb')
parser.add_argument('--reference',type=Path,default=OUT/'reimport-verification.json')
parser.add_argument('--out',type=Path,default=OUT/'current-blender-import-verification.json')
options=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
GLB=options.model.resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6'
assert sha(GLB)==expected
reference=json.loads(options.reference.read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))
bpy.context.view_layer.update()
objects=list(bpy.context.scene.objects)
assert len(objects)==18 and all(o.type=='MESH' for o in objects)
assert not any([len(bpy.data.armatures),len(bpy.data.actions),len(bpy.data.texts),len(bpy.data.cameras),len(bpy.data.lights)])
tris=0;max_bound_error=0.0
for row in reference['objects']:
    obj=bpy.data.objects[row['export_name']]
    obj.data.calc_loop_triangles();tris+=len(obj.data.loop_triangles)
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    bounds=[[min(p[axis] for p in points) for axis in range(3)],[max(p[axis] for p in points) for axis in range(3)]]
    max_bound_error=max(max_bound_error,max(abs(bounds[i][j]-row['source']['world_bbox'][i][j]) for i in range(2) for j in range(3)))
assert tris==5560 and max_bound_error<1e-6
materials={slot.material for o in objects for slot in o.material_slots if slot.material}
images=[im for im in bpy.data.images if im.type=='IMAGE']
assert len(materials)==3 and len(images)==4 and all(im.packed_file for im in images)
assert all(any(node.type=='BSDF_PRINCIPLED' for node in material.node_tree.nodes) for material in materials)
assert sha(GLB)==expected
receipt={'status':'CURRENT_BLENDER_READONLY_IMPORT_PASS','blender':bpy.app.version_string,'source_glb_sha256':expected,'mesh_count':len(objects),'triangles':tris,'materials':len(materials),'packed_images':len(images),'world_bounds_max_abs_error_m':max_bound_error,'source_unchanged':True,'scripts_executed_from_asset':False,'new_renders':0,'scope':'Import/data compatibility only; does not extend the static craft gate or approve character, motion or mechanical safety.'}
options.out.parent.mkdir(parents=True,exist_ok=True)
options.out.write_text(json.dumps(receipt,indent=2)+'\n')
print('RESULT '+json.dumps(receipt))
