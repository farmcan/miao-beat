"""Bounded static glTF transport test; immutable native source, no animation.

This uses the documented render-matched VIEWPORT proxy, not a captured RENDER
depsgraph. Exported pixels must pass a separate visual review before web use.
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'artifacts/miao-reuse-keyboard-v1'
SOURCE = BASE / 'default-color/keyboard-default-color-native36.blend'
OUT = BASE / 'static-web-roundtrip'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert bpy.app.version[:2] == (3, 6)
    OUT.mkdir(parents=True, exist_ok=True)
    source_sha = sha(SOURCE)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    native = bpy.context.scene
    rig = bpy.data.objects['RIG-Cat']
    pose = lambda: hashlib.sha256(json.dumps([(b.name, [list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest()
    pose_before = pose()
    assert pose_before == '4fb6d4c171f6aa36efa9f0e550048d037e91057225bd9856edf7670b8b1913be'
    for obj in native.objects:
        for curve in obj.animation_data.drivers if obj.animation_data else []:
            if 'modifiers[' in curve.data_path and curve.data_path.endswith('].levels'):
                curve.mute = True
        for modifier in obj.modifiers:
            modifier.show_viewport = modifier.show_render
            if modifier.type == 'SUBSURF':
                modifier.levels = modifier.render_levels
    for group in bpy.data.node_groups:
        for node in list(group.nodes):
            if node.bl_idname != 'GeometryNodeIsViewport':
                continue
            destinations = [link.to_socket for link in group.links if link.from_node == node]
            replacement = group.nodes.new('FunctionNodeInputBool')
            replacement.boolean = False
            for socket in destinations:
                group.links.new(replacement.outputs[0], socket)
    bpy.context.view_layer.update()
    # Native eyes contain GN instances; to_mesh alone drops that component.
    # Realize the authored output on the temporary evaluated copy, not the file.
    realize = bpy.data.node_groups.new('WEB_TEST_REALIZE_AUTHORED_INSTANCES', 'GeometryNodeTree')
    realize.inputs.new('NodeSocketGeometry', 'Geometry')
    realize.outputs.new('NodeSocketGeometry', 'Geometry')
    node_in = realize.nodes.new('NodeGroupInput')
    node_out = realize.nodes.new('NodeGroupOutput')
    node_realize = realize.nodes.new('GeometryNodeRealizeInstances')
    realize.links.new(node_in.outputs['Geometry'], node_realize.inputs['Geometry'])
    realize.links.new(node_realize.outputs['Geometry'], node_out.inputs['Geometry'])
    for obj in list(native.objects):
        if obj.type in {'MESH', 'CURVE'} and obj.name.startswith(('GEO-', 'CAT-')) and obj.visible_get() and not obj.hide_render:
            modifier = obj.modifiers.new('WEB_TEST_REALIZE_INSTANCES', 'NODES')
            modifier.node_group = realize
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    propnames = {row['name'] for row in json.loads((BASE / 'prop/prop-receipt.json').read_text())['objects']}
    snapshot = bpy.data.scenes.new('WEB_STATIC_TRANSPORT_TEST')
    snapshot.world = native.world.copy() if native.world else None
    rows = []
    for obj in list(native.objects):
        if obj.type not in {'MESH', 'CURVE'} or obj.hide_render or not obj.visible_get():
            continue
        if not (obj.name.startswith(('GEO-', 'CAT-', 'SUPPORT-', 'ENV-')) or obj.name in propnames):
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
        mesh.calc_loop_triangles()
        if not mesh.polygons:
            continue
        copy = bpy.data.objects.new(obj.name + '_WEB', mesh)
        snapshot.collection.objects.link(copy)
        copy.matrix_world = obj.matrix_world.copy()
        rows.append({'source': obj.name, 'vertices': len(mesh.vertices), 'triangles': len(mesh.loop_triangles), 'materials': [m.name if m else None for m in mesh.materials]})
    for obj in native.objects:
        if obj.type not in {'CAMERA', 'LIGHT'} or (obj.type == 'CAMERA' and obj != native.camera):
            continue
        copy = obj.copy()
        copy.data = obj.data.copy()
        snapshot.collection.objects.link(copy)
        copy.matrix_world = obj.matrix_world.copy()
        if obj == native.camera:
            snapshot.camera = copy
    assert any(row['source'] == 'GEO-head' for row in rows)
    assert any(row['source'] == 'GEO-hands' for row in rows)
    assert len([row for row in rows if row['source'] in propnames]) == len(propnames)
    assert pose() == pose_before
    bpy.context.window.scene = snapshot
    snapshot.render.engine = 'BLENDER_EEVEE'
    snapshot.eevee.taa_render_samples = 64
    snapshot.eevee.use_gtao = native.eevee.use_gtao
    snapshot.eevee.gtao_distance = native.eevee.gtao_distance
    snapshot.eevee.use_soft_shadows = native.eevee.use_soft_shadows
    snapshot.render.resolution_x = snapshot.render.resolution_y = 900
    snapshot.render.resolution_percentage = 100
    snapshot.view_settings.view_transform = native.view_settings.view_transform
    snapshot.view_settings.look = native.view_settings.look
    snapshot.view_settings.exposure = native.view_settings.exposure
    snapshot.view_settings.gamma = native.view_settings.gamma
    snapshot.render.filepath = str(OUT / 'evaluated-snapshot.png')
    bpy.ops.render.render(write_still=True)
    glb = OUT / 'keyboard-static-test.glb'
    # glTF does not support AREA lights. Keep geometry/material transport distinct
    # from the display environment, which is reinstated for this controlled test.
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_active_scene=True, export_animations=False, export_cameras=True, export_lights=False, export_extras=False)
    imported = bpy.data.scenes.new('WEB_GLTF_REIMPORT_TEST')
    imported.world = snapshot.world.copy() if snapshot.world else None
    bpy.context.window.scene = imported
    bpy.ops.import_scene.gltf(filepath=str(glb))
    for light in (o for o in snapshot.objects if o.type == 'LIGHT'):
        copy = light.copy()
        copy.data = light.data.copy()
        imported.collection.objects.link(copy)
    imported.camera = next(o for o in imported.objects if o.type == 'CAMERA')
    imported.render.engine = 'BLENDER_EEVEE'
    imported.eevee.taa_render_samples = 64
    imported.eevee.use_gtao = snapshot.eevee.use_gtao
    imported.eevee.gtao_distance = snapshot.eevee.gtao_distance
    imported.eevee.use_soft_shadows = snapshot.eevee.use_soft_shadows
    imported.render.resolution_x = imported.render.resolution_y = 900
    imported.render.resolution_percentage = 100
    imported.view_settings.view_transform = snapshot.view_settings.view_transform
    imported.view_settings.look = snapshot.view_settings.look
    imported.view_settings.exposure = snapshot.view_settings.exposure
    imported.view_settings.gamma = snapshot.view_settings.gamma
    imported.render.filepath = str(OUT / 'gltf-reimport.png')
    bpy.ops.render.render(write_still=True)
    assert sha(SOURCE) == source_sha
    result = {'status': 'STATIC_TRANSPORT_TEST_PENDING_VISUAL_REVIEW', 'source_sha256': source_sha, 'source_file_unchanged': True, 'original_pose_unchanged': True, 'method': 'render-matched VIEWPORT evaluated mesh snapshot; not direct RENDER depsgraph', 'objects': rows, 'triangles': sum(r['triangles'] for r in rows), 'glb_bytes': glb.stat().st_size, 'glb_sha256': sha(glb), 'new_animation': False, 'web_browser_verified': False}
    (OUT / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print('RESULT', json.dumps({k: v for k, v in result.items() if k != 'objects'}))


if __name__ == '__main__':
    main()
