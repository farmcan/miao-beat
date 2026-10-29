"""Read-only source-format probe: import the fixed licensed guitar into Blender 3.6."""
import hashlib
import json
import pathlib
import sys

import bpy
from mathutils import Vector

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
expected_sha = '1e3da0406355be281e2442de80bd4093eba58cfda640a07a6acd53ab231b1e41'
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha == expected_sha
assert bpy.app.version[:2] == (3, 6)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
lower = [min(point[axis] for point in points) for axis in range(3)]
upper = [max(point[axis] for point in points) for axis in range(3)]
triangles = 0
for obj in meshes:
    obj.data.calc_loop_triangles()
    triangles += len(obj.data.loop_triangles)
receipt = {
    'source': str(source),
    'source_sha256': source_sha,
    'source_sha256_after': hashlib.sha256(source.read_bytes()).hexdigest(),
    'blender_version': bpy.app.version_string,
    'blender_build_hash': bpy.app.build_hash.decode(),
    'import_result': 'success',
    'mesh_count': len(meshes),
    'triangles': triangles,
    'bounds': {'min': lower, 'max': upper, 'size': [upper[axis] - lower[axis] for axis in range(3)]},
    'images': [{'name': image.name, 'size': list(image.size), 'packed': bool(image.packed_file)} for image in bpy.data.images],
    'materials': [material.name for material in bpy.data.materials],
    'texts': len(bpy.data.texts),
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'limitations': ['format import only; no cat pose/contact or branded-surface repair performed'],
}
output.write_text(json.dumps(receipt, indent=2))
assert receipt['source_sha256'] == receipt['source_sha256_after']
assert triangles == 141217
print(json.dumps(receipt))
