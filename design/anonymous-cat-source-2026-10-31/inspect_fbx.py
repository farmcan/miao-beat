"""Audit original FBX rig data without playing or changing animation."""
from pathlib import Path
import bpy
import json
root = Path(__file__).resolve().parents[2]
base = root / 'artifacts/anonymous-cat-source-2026-10-31/cat-warrior-original'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(base / 'extracted/Cat_Warrior_Pack_v1.0/Models/FBX/Idle.fbx'))
r = {'blender': bpy.app.version_string, 'scope': 'original Idle FBX structure only; no motion played', 'armatures': []}
for o in bpy.context.scene.objects:
    if o.type == 'ARMATURE':
        r['armatures'].append({'name': o.name, 'bones': [{'name': b.name, 'parent': b.parent.name if b.parent else None} for b in o.data.bones]})
r['meshes'] = [{'name': o.name, 'vertices': len(o.data.vertices), 'polygons': len(o.data.polygons), 'vertex_groups': list(o.vertex_groups.keys()), 'shape_keys': list(o.data.shape_keys.key_blocks.keys()) if o.data.shape_keys else [], 'modifiers': [{'type': m.type, 'target': getattr(m, 'object', None).name if getattr(m, 'object', None) else None} for m in o.modifiers]} for o in bpy.context.scene.objects if o.type == 'MESH']
r['actions'] = [{'name': a.name, 'frame_range': list(a.frame_range)} for a in bpy.data.actions]
r['images'] = [{'name': i.name, 'size': list(i.size), 'packed': bool(i.packed_file)} for i in bpy.data.images if i.type != 'RENDER_RESULT']
(base / 'fbx-inspection.json').write_text(json.dumps(r, indent=2))
print('FBX_INSPECTION_COMPLETE', json.dumps(r))
