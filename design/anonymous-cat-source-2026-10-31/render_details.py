"""Diagnostic crops of the unmodified source, never production frames."""
from pathlib import Path
import bpy
from mathutils import Vector
root = Path(__file__).resolve().parents[2]
out = root / 'artifacts/anonymous-cat-source-2026-10-31/cat-warrior-inspection'
bpy.ops.wm.open_mainfile(filepath=str(out / 'source-inspection.blend'), use_scripts=False)
sc = bpy.context.scene
cam = sc.camera
sc.render.resolution_x = sc.render.resolution_y = 512
for mode in ('color','gray'):
    sc.render.engine = 'BLENDER_EEVEE' if mode == 'color' else 'BLENDER_WORKBENCH'
    if mode == 'gray':
        sc.display.shading.light = 'STUDIO'
        sc.display.shading.color_type = 'SINGLE'
        sc.display.shading.single_color = (.65,.65,.65)
    for label, target, size in [('left-paw',(-.34,-.015,.34),.25), ('right-paw',(.34,-.015,.34),.28), ('face',(0,-.02,.77),.58)]:
        target = Vector(target)
        cam.location = target + Vector((0,-3,.15))
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale = size
        bpy.context.view_layer.update()
        sc.render.filepath = str(out / (label+'-'+mode+'.png'))
        bpy.ops.render.render(write_still=True)
print('DETAILS_COMPLETE')
