"""Read-only source geometry inspection; no rigging, recoloring or adaptation."""
from pathlib import Path
import json
import sys
import argparse
import bpy
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=root / 'artifacts/anonymous-cat-source-2026-10-31/muru-original/stylised-cat.glb')
parser.add_argument('--out', type=Path, default=root / 'artifacts/anonymous-cat-source-2026-10-31/muru-inspection')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
print('BLENDER_VERSION', bpy.app.version_string)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(args.source.resolve()))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
bpy.context.view_layer.update()
points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
center = (lo + hi) / 2
extent = max(hi - lo)
receipt = {'version': bpy.app.version_string, 'scope': 'unaltered source geometry and imported materials; diagnostic cameras/lights only',
           'bbox': [list(lo), list(hi)], 'armatures': sum(o.type == 'ARMATURE' for o in bpy.context.scene.objects),
           'meshes': [{'name': o.name, 'vertices': len(o.data.vertices), 'polygons': len(o.data.polygons), 'shape_keys': bool(o.data.shape_keys), 'vertex_groups': len(o.vertex_groups)} for o in meshes]}
(out / 'native-inspection.json').write_text(json.dumps(receipt, indent=2))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.65, .65, .65, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
scene.view_settings.view_transform = 'Standard'
for name, direction, energy in [('Key', (-2,-3,4), 500), ('Fill', (3,-1,2), 220)]:
    data = bpy.data.lights.new(name, 'AREA')
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = center + Vector(direction) * extent
    light.rotation_euler = (center - light.location).to_track_quat('-Z','Y').to_euler()
    data.energy = energy * extent**2
    data.shape = 'DISK'
    data.size = extent * 3
data = bpy.data.cameras.new('Diagnostic camera')
camera = bpy.data.objects.new('Diagnostic camera', data)
scene.collection.objects.link(camera)
scene.camera = camera
data.type = 'ORTHO'
data.ortho_scale = extent * 1.25
for name, direction in [('front', (0,-1,.06)), ('back', (0,1,.06)), ('three-quarter', (-.6,-1,.18))]:
    camera.location = center + Vector(direction).normalized() * extent * 3
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = str(out / (name + '.png'))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'source-inspection.blend'))
sys.path.append('/Users/levi/.codex/skills/scenario-blender-expert/scripts')
import bx_review
sheet = bx_review.review(meshes, str(out / 'geometry'), views=('front','back','threequarter'), modes=('silhouette','matcap','wire'), res=360)
print('REVIEW_SHEET', sheet)
print('INSPECTION_COMPLETE', json.dumps(receipt))
