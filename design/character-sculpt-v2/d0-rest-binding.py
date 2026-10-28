"""D0.1 only: freeze evaluated C5 surfaces and bind pigment to world rest positions.

Run with Blender -b --python this.py. Exactly two rest-pose renders; no animation.
The C5 editable master is read-only. Diagnostic AOVs do not feed Surface.
"""
import argparse, bpy, hashlib, json, sys, time
from pathlib import Path
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('--input', default='design/character-sculpt-v2/miao-plush-static-study.blend')
p.add_argument('--output', default='artifacts/character-sculpt-d0')
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
root = Path(__file__).resolve().parents[2]
source, out = (root / a.input).resolve(), (root / a.output).resolve()
out.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
started = time.time()
bpy.ops.wm.open_mainfile(filepath=str(source))
s = bpy.context.scene
coat = bpy.data.materials['Miao / warm short plush']
targets = [o for o in s.objects if o.type in {'MESH', 'CURVES'}
           and any(m == coat for m in o.data.materials)]
assert len(targets) == 4, [o.name for o in targets]
camera_matrix = [list(r) for r in s.camera.matrix_world]
light_state = {o.name: {'matrix': [list(r) for r in o.matrix_world],
                      'energy': o.data.energy, 'size': o.data.size}
               for o in s.objects if o.type == 'LIGHT'}
records = []
for o in targets:
    modifier_info = [(m.name, m.type) for m in o.modifiers]
    if o.type == 'MESH':
        for m in o.modifiers:
            assert m.show_viewport == m.show_render, (o.name, m.name)
            if m.type == 'SUBSURF':
                assert m.levels == m.render_levels, (o.name, m.name)
        dg = bpy.context.evaluated_depsgraph_get()
        evaluated = o.evaluated_get(dg)
        old = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
        old_co = np.empty(len(old.vertices) * 3, np.float32)
        old.vertices.foreach_get('co', old_co)
        frozen = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True,
                                               depsgraph=dg)
        new_co = np.empty(len(frozen.vertices) * 3, np.float32)
        frozen.vertices.foreach_get('co', new_co)
        assert np.array_equal(old_co, new_co), o.name
        evaluated.to_mesh_clear()
        o.modifiers.clear()
        o.data = frozen
        coords = new_co.reshape(-1, 3)
    else:
        assert not o.modifiers, 'Do not silently ignore evaluated curve modifiers'
        coords = np.empty(len(o.data.position_data) * 3, np.float32)
        o.data.position_data.foreach_get('vector', coords)
        coords = coords.reshape(-1, 3)
    matrix = np.array(o.matrix_world, np.float64)
    world = (coords.astype(np.float64) @ matrix[:3, :3].T + matrix[:3, 3]).astype(np.float32)
    attr = o.data.attributes.get('miao_rest_position')
    assert attr is None, 'Never overwrite a previous rest binding without inspection'
    attr = o.data.attributes.new('miao_rest_position', 'FLOAT_VECTOR', 'POINT')
    attr.data.foreach_set('vector', world.ravel())
    check = np.empty(world.size, np.float32)
    attr.data.foreach_get('vector', check)
    assert np.array_equal(check.reshape(-1, 3), world), o.name
    records.append({'name': o.name, 'type': o.type, 'points': len(world),
                    'frozen_modifiers': modifier_info,
                    'world_rest_sha256': hashlib.sha256(world.tobytes()).hexdigest(),
                    'rest_attribute_type': attr.data_type, 'rest_attribute_domain': attr.domain,
                    'rest_readback_max_error': float(np.max(np.abs(check - world.ravel()))),
                    'world_min': world.min(axis=0).tolist(),
                    'world_max': world.max(axis=0).tolist()})

n, links = coat.node_tree.nodes, coat.node_tree.links
position_links = [l for l in links if l.from_node.bl_idname == 'ShaderNodeNewGeometry'
                  and l.from_socket.name == 'Position']
assert len(position_links) == 1, [(l.from_node.name, l.to_node.name) for l in position_links]
geometry = position_links[0].from_node
destination = position_links[0].to_socket
rest = n.new('ShaderNodeAttribute')
rest.name = 'D0 / immutable world rest position'
rest.attribute_type = 'GEOMETRY'
rest.attribute_name = 'miao_rest_position'

# These AOVs are evaluated in the same two renders, without changing Surface.
aov_nodes, aov_error = {}, None
audit_shader_nodes, audit_comp_nodes, audit_aovs = [], [], []
try:
    layer = bpy.context.view_layer
    hair = n.new('ShaderNodeHairInfo'); audit_shader_nodes.append(hair)
    distance = n.new('ShaderNodeVectorMath'); audit_shader_nodes.append(distance)
    distance.operation = 'DISTANCE'
    links.new(rest.outputs['Vector'], distance.inputs[0])
    links.new(geometry.outputs['Position'], distance.inputs[1])
    magnitude = n.new('ShaderNodeVectorMath'); audit_shader_nodes.append(magnitude)
    magnitude.operation = 'LENGTH'
    links.new(rest.outputs['Vector'], magnitude.inputs[0])
    outputs = {'D0RestError': distance.outputs['Value'],
               'D0RestMagnitude': magnitude.outputs['Value'],
               'D0Hair': hair.outputs['Is Strand'], 'D0RestAlpha': rest.outputs['Alpha']}
    nt = s.compositing_node_group
    rl = next(node for node in nt.nodes if node.type == 'R_LAYERS')
    for name, socket in outputs.items():
        av = layer.aovs.add(); audit_aovs.append(av); av.name = name; av.type = 'VALUE'
        shader_out = n.new('ShaderNodeOutputAOV'); audit_shader_nodes.append(shader_out)
        shader_out.name = name
        shader_out.aov_name = name; links.new(socket, shader_out.inputs['Value'])
    layer.update_render_passes()
    for name in outputs:
        node = nt.nodes.new('CompositorNodeOutputFile')
        audit_comp_nodes.append(node)  # Track before any version-sensitive property assignment.
        node.name = 'D0 audit / ' + name
        node.file_name = name; node.save_as_render = False
        node.format.file_format = 'OPEN_EXR'; node.format.color_depth = '32'
        node.format.color_mode = 'RGB'; node.format.exr_codec = 'ZIP'
        node.file_output_items.new('FLOAT', 'Data')
        nt.links.new(rl.outputs[name], node.inputs['Data'])
        aov_nodes[name] = node
except Exception as e:
    aov_error = repr(e)
    # Do not let a diagnostic API issue block the two actual beauty renders.
    for node in audit_comp_nodes:
        s.compositing_node_group.nodes.remove(node)
    for node in audit_shader_nodes:
        n.remove(node)
    for av in audit_aovs:
        layer.aovs.remove(av)
    layer.update_render_passes()
    aov_nodes = {}

s.render.resolution_x = s.render.resolution_y = 512
s.render.resolution_percentage = 100
s.cycles.samples = 32; s.cycles.seed = 17; s.cycles.use_animated_seed = False
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '8'
render_records = []
for tag in ['baseline-position', 'named-rest-position']:
    if tag == 'named-rest-position':
        links.new(rest.outputs['Vector'], destination)
    for name, node in aov_nodes.items():
        directory = out / tag / 'aov'; directory.mkdir(parents=True, exist_ok=True)
        node.directory = str(directory)
    s.render.filepath = str(out / (tag + '.png'))
    filename = 'miao-d0-rest-bound.blend' if tag == 'named-rest-position' else 'miao-d0-position-baseline.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(out / filename), compress=True)
    t = time.time(); bpy.ops.render.render(write_still=True)
    render_records.append({'tag': tag, 'seconds': time.time() - t,
                           'beauty_sha256': hashlib.sha256((out / (tag + '.png')).read_bytes()).hexdigest()})

assert camera_matrix == [list(r) for r in s.camera.matrix_world]
assert light_state == {o.name: {'matrix': [list(r) for r in o.matrix_world],
                             'energy': o.data.energy, 'size': o.data.size}
                      for o in s.objects if o.type == 'LIGHT'}
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
receipt = {'stage': 'D0.1-rest-binding-unreviewed', 'source_sha256': source_hash,
           'source_unchanged': True, 'blender': bpy.app.version_string,
           'renders': render_records, 'seed': 17, 'samples': 32, 'size': 512,
           'targets': records, 'camera_lights_unchanged': True,
           'aov_setup_error': aov_error, 'aov_files': [str(p.relative_to(out)) for p in out.rglob('*.exr')],
           'elapsed_seconds': time.time() - started,
           'limits': ['Rest-pose shader binding only; no deformation or anti-swim motion test.',
                      'No rig, eyelid closure, string contact, browser or export verification.',
                      'Unconnected micro-noise Vector input remains as C5; not converted in this experiment.',
                      'Baseline and rest use the same frozen evaluated geometry; not a third C5 render.']}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('D0_REST_BINDING_COMPLETE', json.dumps(receipt))
