"""Transport the accepted one-key source poses into the accepted complete GLB.

Blender 3.6.23, --factory-startup --disable-autoexec. No native saves, renders,
frame_set, embedded scripts, new pose search, rig reconstruction, or clips.
The only authored channel sampled is original FK-Index1.L local X. Contact/Down
are absolute shape targets against the received ready scene, never limb plates.
"""
import array
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from single_key_geometry import RenderMatchedProxy, geometry, bounds, overlaps

BASE = ROOT / 'artifacts/miao-reuse-keyboard-v1'
OUT = BASE / 'single-key-web-morph'
SOURCE = BASE / 'v2-keygroup-lift-color/keygroup-lift-color-native36.blend'
STATIC = BASE / 'v2-static-web-roundtrip/keyboard-static-test.glb'
NUMERIC = BASE / 'single-key-v2/single-key-numeric-receipt.json'
SOURCE_SHA = 'ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6'
STATIC_SHA = 'd8897cd917bf07ec3d140646e17b80ab7a87b4eb773fb5db939b9a66dcc849ea'
POSE_SHA = '6a034f30f3f848c4cd7833da9e86834d895a636bfed170d5cd5fbd16d7b5049b'
TARGET = 'Ivory piano key.014'
MATCH_TOLERANCE = 1e-6
REPORT = {'status': 'BUILDING', 'source': str(SOURCE.relative_to(ROOT)),
          'source_sha256': SOURCE_SHA, 'static_glb_sha256': STATIC_SHA,
          'new_actions': 0, 'new_keyframes': 0, 'native_saved': False,
          'renders': 0, 'web_verified': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def persist():
    (OUT / 'receipt.json').write_text(json.dumps(REPORT, indent=2) + '\n')


def mesh_record(obj):
    points, triangles, _ = geometry(obj)
    return {'name': obj.name, 'p': points, 't': triangles, 'bbox': bounds(points),
            'tree': BVHTree.FromPolygons(points, triangles, all_triangles=True)}


def pose_hash(rig):
    return hashlib.sha256(json.dumps([
        (bone.name, [list(row) for row in bone.matrix_basis])
        for bone in rig.pose.bones]).encode()).hexdigest()


def topology(mesh):
    return (len(mesh.vertices), tuple(tuple(poly.vertices) for poly in mesh.polygons))


def capture(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh(preserve_all_data_layers=True,
                             depsgraph=bpy.context.evaluated_depsgraph_get())
    result = {'p': [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices],
              'topology': topology(mesh)}
    if obj.name == 'GEO-hands':
        group = obj.vertex_groups['DEF-Index2.L'].index
        result['pad_ids'] = {vertex.index for vertex in mesh.vertices
                             if any(g.group == group and g.weight > .6
                                    for g in vertex.groups)}
    evaluated.to_mesh_clear()
    return result


def realize_authored_instances(scene):
    group = bpy.data.node_groups.new('WEB_MORPH_REALIZE_AUTHORED_INSTANCES', 'GeometryNodeTree')
    group.inputs.new('NodeSocketGeometry', 'Geometry')
    group.outputs.new('NodeSocketGeometry', 'Geometry')
    node_in = group.nodes.new('NodeGroupInput')
    node_out = group.nodes.new('NodeGroupOutput')
    realize = group.nodes.new('GeometryNodeRealizeInstances')
    group.links.new(node_in.outputs['Geometry'], realize.inputs['Geometry'])
    group.links.new(realize.outputs['Geometry'], node_out.inputs['Geometry'])
    for obj in scene.objects:
        if obj.type in {'MESH', 'CURVE'} and obj.visible_get() and not obj.hide_render and obj.name.startswith(('GEO-', 'CAT-')):
            modifier = obj.modifiers.new('WEB_MORPH_REALIZE_INSTANCES', 'NODES')
            modifier.node_group = group
    bpy.context.view_layer.update()


def map_vertices(obj, ready, targets):
    tree = KDTree(len(ready))
    for index, point in enumerate(ready):
        tree.insert(point, index)
    tree.balance()
    indices = []
    maximum = 0.0
    ambiguous = 0
    duplicate_matches = 0
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        near, index, distance = tree.find(world)
        if distance > MATCH_TOLERANCE:
            raise RuntimeError(f'{obj.name} vertex {vertex.index}: mapping distance {distance}')
        maximum = max(maximum, distance)
        # UV seams can duplicate source positions; they must have equivalent
        # target positions. A nearest-neighbor choice cannot hide ambiguity.
        coincident = [i for point, i, d in tree.find_range(near, 1e-8)]
        if len(coincident) > 1:
            duplicate_matches += 1
            for target in targets:
                if any((target[i] - target[index]).length > 1e-7 for i in coincident):
                    ambiguous += 1
                    raise RuntimeError(f'{obj.name} coincident ready vertex has divergent target')
        indices.append(index)
    return indices, {'source_vertices': len(ready), 'import_vertices': len(indices),
                     'maximum_world_mapping_error_m': maximum,
                     'coincident_source_matches': duplicate_matches,
                     'ambiguous_target_matches': ambiguous}


def read_glb(path):
    raw = path.read_bytes()
    assert raw[:4] == b'glTF'
    size, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4E4F534A
    return json.loads(raw[20:20 + size])


def morph_weights(q, q0, contact, down):
    if q <= contact:
        return (q - q0) / (contact - q0), 0.0
    t = (q - contact) / (down - contact)
    return 1.0 - t, t


def main():
    assert bpy.app.version == (3, 6, 23)
    assert sha(SOURCE) == SOURCE_SHA
    assert sha(STATIC) == STATIC_SHA
    numeric = json.loads(NUMERIC.read_text())
    assert numeric['source_sha_before'] == SOURCE_SHA
    assert numeric['source_pose_sha256'] == POSE_SHA
    OUT.mkdir(parents=True, exist_ok=True)
    persist()
    q0 = numeric['base_joint_x_radians']
    q_contact = numeric['contact_joint_x_radians']
    q_down = numeric['down_joint_x_radians']
    theta_full = numeric['key_down_radians']
    pivot = Vector(numeric['fixed_hinge_world'])
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    source_scene = bpy.context.scene
    rig = bpy.data.objects['RIG-Cat']
    assert pose_hash(rig) == POSE_SHA
    joint = rig.pose.bones['FK-Index1.L']
    assert abs(joint.rotation_euler.x - q0) < 1e-12
    other_bones = {b.name: b.matrix_basis.copy() for b in rig.pose.bones if b != joint}
    actions = set(a.name for a in bpy.data.actions)
    helper = bpy.data.objects['HLP-scene_camera_dummy']
    rotation_drivers = [f for f in helper.animation_data.drivers
                        if f.data_path == 'rotation_euler']
    assert len(rotation_drivers) == 3 and all(f.mute for f in rotation_drivers)
    helper.rotation_euler = source_scene.camera.matrix_world.to_euler()
    bpy.context.view_layer.update()
    assert max(abs(helper.rotation_euler[i] - source_scene.camera.matrix_world.to_euler()[i]) for i in range(3)) == 0
    cat_objects = [o for o in source_scene.objects
                   if o.type in {'MESH', 'CURVE'} and o.visible_get() and
                   not o.hide_render and o.name.startswith(('GEO-', 'CAT-'))]
    captures = {}
    with RenderMatchedProxy():
        realize_authored_instances(source_scene)
        for label, q in [('Ready', q0), ('Contact', q_contact), ('Down', q_down)]:
            joint.rotation_euler.x = q
            bpy.context.view_layer.update()
            captures[label] = {obj.name: capture(obj) for obj in cat_objects}
            for name, matrix in other_bones.items():
                assert rig.pose.bones[name].matrix_basis == matrix
            print('CAPTURED', label, len(captures[label]), flush=True)
        joint.rotation_euler.x = q0
        bpy.context.view_layer.update()
    assert pose_hash(rig) == POSE_SHA
    assert set(a.name for a in bpy.data.actions) == actions
    empty_parts = [name for name, value in captures['Ready'].items() if not value['p']]
    for label in captures:
        for name in empty_parts:
            assert not captures[label][name]['p'], ('Empty part became visible', name, label)
            del captures[label][name]
    REPORT['authored_empty_outputs_omitted'] = empty_parts
    source_parts = []
    changed = []
    for name, ready in captures['Ready'].items():
        row = {'source': name}
        for label in ['Contact', 'Down']:
            target = captures[label][name]
            assert target['topology'] == ready['topology'], (name, label, 'topology changed')
            row[label + '_maximum_delta_m'] = max((a - b).length for a, b in zip(ready['p'], target['p']))
        # Sub-micron changes in unrelated eye/head constraints are evaluation
        # rounding, below this transport's 1um spatial tolerance. Retain the
        # already accepted static bytes for those parts, never add a face morph.
        if max(row['Contact_maximum_delta_m'], row['Down_maximum_delta_m']) > MATCH_TOLERANCE:
            changed.append(name)
        source_parts.append(row)
    REPORT.update({'source_parts': source_parts, 'actual_deformed_parts': changed,
                   'source_pose_restored': True, 'source_pose_sha256': POSE_SHA,
                   'moving_part_threshold_m': MATCH_TOLERANCE,
                   'unchanged_parts_transport': 'retained accepted static GLB; sub-micron native evaluation jitter receives no morph'})
    persist()
    assert changed, 'No actual moving part'
    print('ACTUAL_CHANGED', changed, flush=True)
    # Discard source rig and embedded texts entirely before importing approved GLB.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(STATIC))
    imported = bpy.context.scene
    mapping_rows = []
    maps = {}
    for name, ready in captures['Ready'].items():
        obj = bpy.data.objects.get(name + '_WEB')
        assert obj is not None and obj.type == 'MESH', ('Missing complete source part', name)
        if name not in changed:
            continue
        targets = [captures[label][name]['p'] for label in ['Contact', 'Down']]
        indices, row = map_vertices(obj, ready['p'], targets)
        maps[name] = indices
        row['source'] = name
        mapping_rows.append(row)
        if name not in changed:
            continue
        obj.shape_key_add(name='Basis', from_mix=False)
        inverse = obj.matrix_world.inverted()
        for label, target in zip(['Contact', 'Down'], targets):
            shape = obj.shape_key_add(name=label, from_mix=False)
            for vertex, index in zip(shape.data, indices):
                vertex.co = inverse @ target[index]
            shape.value = 0
    assert len([o for o in imported.objects if o.name.startswith('GEO-hands_WEB')]) == 1
    key = bpy.data.objects[TARGET + '_WEB']
    assert not key.data.shape_keys
    key.name = 'MiaoKeyC4'
    key0 = key.matrix_world.copy()
    REPORT['mapping'] = mapping_rows
    REPORT['mapping_maximum_error_m'] = max(row['maximum_world_mapping_error_m'] for row in mapping_rows)
    persist()
    prop_names = {row['name'] + '_WEB' for row in json.loads((BASE / 'prop/prop-receipt.json').read_text())['objects']}
    prop_names.add('MiaoKeyC4')
    props = [obj for obj in imported.objects if obj.type == 'MESH' and
             (obj.name in prop_names or obj.name.startswith('SUPPORT-'))]
    assert len(props) >= 90, ('Missing prop components', len(props))
    fixed = [mesh_record(obj) for obj in props if obj != key]
    hands = bpy.data.objects['GEO-hands_WEB']
    arms = bpy.data.objects['GEO-arms_WEB']
    pad_source = captures['Ready']['GEO-hands']['pad_ids']
    pad_import = [i for i, source_index in enumerate(maps['GEO-hands']) if source_index in pad_source]
    assert pad_import
    unique_frames = {}
    for frame in numeric['frames']:
        ident = (frame['q_radians'], frame['key_theta_radians'])
        unique_frames.setdefault(ident, []).append(frame['frame'])
    # Include the exact Contact snapshot even if schedule rounding ever omitted it.
    unique_frames.setdefault((q_contact, 0.0), [])
    checks = []
    sleeves = mesh_record(arms)
    min_gap = math.inf
    maximum_source_error = 0.0
    for (q, theta), frames in sorted(unique_frames.items()):
        contact_weight, down_weight = morph_weights(q, q0, q_contact, q_down)
        for name in changed:
            obj = bpy.data.objects[name + '_WEB']
            obj.data.shape_keys.key_blocks['Contact'].value = contact_weight
            obj.data.shape_keys.key_blocks['Down'].value = down_weight
        key.matrix_world = Matrix.Translation(pivot) @ Matrix.Rotation(theta, 4, 'X') @ Matrix.Translation(-pivot) @ key0
        bpy.context.view_layer.update()
        moving = mesh_record(key)
        records = fixed + [moving]
        hand = mesh_record(hands)
        hand_hits = overlaps(hand['p'], hand['t'], records)
        sleeve_hits = overlaps(sleeves['p'], sleeves['t'], records)
        projected = []
        for index in pad_import:
            point = hand['p'][index]
            hit, normal, _, _ = moving['tree'].ray_cast(Vector((point.x, point.y, 2)), Vector((0, 0, -1)), 3)
            if hit is not None and normal.z > .9:
                projected.append(point.z - hit.z)
        assert projected, 'Empty target skin projection'
        gap = min(projected)
        min_gap = min(min_gap, gap)
        key_hits = overlaps(moving['p'], moving['t'], fixed)
        black_name = 'Raised black piano key.010_WEB'
        new_key_hits = {name: count for name, count in key_hits.items() if name != black_name}
        row = {'source_frames': frames, 'q': q, 'theta': theta,
               'weights': {'Contact': contact_weight, 'Down': down_weight},
               'whole_hands_external_triangle_intersections': hand_hits,
               'whole_sleeves_external_triangle_intersections': sleeve_hits,
               'target_pad_projected_samples': len(projected), 'target_min_gap_m': gap,
               'new_key_external_intersections': new_key_hits,
               'source_black010_intersections': key_hits.get(black_name, 0),
               'source_black010_local_region': 'unknown: not whole component exempt; original numeric receipt contains finite native intersection-region evidence, not re-proved for transported topology'}
        checks.append(row)
        REPORT['finite_state_checks'] = checks
        persist()
        print('MORPH_STATE', json.dumps({k: row[k] for k in ['source_frames', 'q', 'theta', 'target_min_gap_m', 'whole_hands_external_triangle_intersections', 'new_key_external_intersections']}), flush=True)
        assert not hand_hits and not sleeve_hits and not new_key_hits and gap >= 0, ('Interpolated external collision or negative gap', row)
    for name in changed:
        for label in ['Contact', 'Down']:
            bpy.data.objects[name + '_WEB'].data.shape_keys.key_blocks[label].value = 0
    key.matrix_world = key0
    bpy.context.view_layer.update()
    destination = OUT / 'miao-one-key.glb'
    bpy.ops.export_scene.gltf(filepath=str(destination), export_format='GLB',
                              use_active_scene=True, export_animations=False,
                              export_morph=True, export_morph_normal=True,
                              export_morph_tangent=False, export_colors=False,
                              export_cameras=True, export_lights=False, export_extras=False)
    gltf = read_glb(destination)
    assert not gltf.get('animations') and not gltf.get('skins')
    assert sum(node.get('name') == 'MiaoKeyC4' for node in gltf['nodes']) == 1
    morph_meshes = []
    for mesh in gltf['meshes']:
        if any('targets' in primitive for primitive in mesh['primitives']):
            assert mesh['extras']['targetNames'] == ['Contact', 'Down']
            assert all(len(primitive['targets']) == 2 for primitive in mesh['primitives'])
            morph_meshes.append(mesh['name'])
        assert all('COLOR_0' not in primitive['attributes'] for primitive in mesh['primitives'])
    assert len(morph_meshes) == len(changed)
    assert all('uri' not in image for image in gltf.get('images', []))
    assert all('uri' not in buffer for buffer in gltf.get('buffers', []))
    assert sha(SOURCE) == SOURCE_SHA and sha(STATIC) == STATIC_SHA
    # Release and down arithmetic produce one repeated q with theta differing
    # only by 8e-19 rad. Collapse equivalent q entries; never round distinct q.
    lookup = {}
    for q, theta in sorted(unique_frames):
        if q in lookup:
            assert abs(lookup[q] - theta) < 1e-12, ('Ambiguous q/theta lookup', q)
        else:
            lookup[q] = theta
    trajectory = [{'q': q, 'theta': theta} for q, theta in sorted(lookup.items())]
    assert trajectory[0]['q'] == q0 and trajectory[-1]['q'] == q_down
    assert all(trajectory[i]['theta'] >= trajectory[i+1]['theta'] for i in range(len(trajectory)-1))
    metadata = {'version': 1, 'modelFile': 'miao-one-key.glb', 'keyNode': 'MiaoKeyC4',
                'morphNames': {'contact': 'Contact', 'down': 'Down'},
                'q0': q0, 'qContact': q_contact, 'qDown': q_down,
                'contactFraction': (q_contact-q0)/(q_down-q0),
                'keyMaxRadians': theta_full, 'pivotThree': [pivot.x, pivot.z, -pivot.y],
                'trajectory': trajectory,
                'morphBlend': 'q<=qContact: Contact=(q-q0)/(qContact-q0),Down=0; else Contact=1-t,Down=t,t=(q-qContact)/(qDown-qContact). Relative-to-Basis glTF targets; do not sum two full weights.',
                'modelSha256': sha(destination), 'modelBytes': destination.stat().st_size,
                'morphNodes': [name + '_WEB' for name in changed],
                'coordinateSystem': 'glTF/Three right-handed Y-up; Blender world[x,y,z] -> [x,z,-y]; key hinge world X angle unchanged',
                'source': {'native': str(SOURCE.relative_to(ROOT)), 'sha256': SOURCE_SHA,
                           'poseSha256': POSE_SHA, 'staticGlbSha256': STATIC_SHA,
                           'numericReceipt': str(NUMERIC.relative_to(ROOT)), 'numericReceiptSha256': sha(NUMERIC)},
                'licenses': [
                    {'asset': 'Cat Rig', 'author': 'Blender Foundation / Blender Studio',
                     'sourceUrl': 'https://studio.blender.org/characters/cat/v1/',
                     'license': 'CC-BY-4.0', 'licenseUrl': 'https://creativecommons.org/licenses/by/4.0/',
                     'modifications': 'Existing approved seated scene and sampled original rig deformation transported as complete scene with Contact/Down morph targets; original topology retained.'},
                    {'asset': 'Key Forty - MIDI Keyboard', 'author': 'Innerscene Corp',
                     'sourceUrl': 'https://www.innerscene.com/tools/library/3d-parts/key-forty-midi-keyboard-0d9952a4',
                     'license': 'CC0-1.0', 'licenseUrl': 'https://creativecommons.org/publicdomain/zero/1.0/',
                     'modifications': 'Approved spatial placement/key-group clearance; one C4 key rigid rear-hinge rotation.'},
                    {'asset': 'COMMON280 communal work table', 'author': 'Innerscene Corp',
                     'sourceUrl': 'https://www.innerscene.com/tools/library/3d-parts/common-280-communal-work-table-0e45ba93',
                     'license': 'CC0-1.0', 'licenseUrl': 'https://creativecommons.org/publicdomain/zero/1.0/',
                     'modifications': 'Existing approved scaled support placement.'}],
                'attribution': 'Cat Rig (CC-BY) Blender Foundation | studio.blender.org; KeyForty Innerscene CC0; COMMON280 CC0. Existing rig deformation sampled, no replacement hand geometry.',
                'validation': {'status': 'FINITE_HAND_SLEEVE_CLEAR_KEY_LOCAL_UNKNOWN_WEB_PENDING',
                               'wholeScene': True, 'sourceCharacterParts': len(source_parts),
                               'actualDeformedParts': changed,
                               'maximumMappingErrorM': REPORT['mapping_maximum_error_m'],
                               'ambiguousTargetMatches': 0,
                               'sampledMorphStates': len(checks), 'originalFrameCount': 49,
                               'minimumTargetGapM': min_gap,
                               'sourceBlack010LocalRegion': 'unknown; no whole-component exemption',
                               'continuousIntervalCollisionProof': False,
                               'browserAudioInputVerified': False},
                'scope': 'Only A/C4 controlled real web experiment; no other key, hand, head, body action. Not final performance/product approval.'}
    (OUT / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    REPORT.update({'status': 'FINITE_HAND_SLEEVE_CLEAR_KEY_LOCAL_UNKNOWN_WEB_PENDING',
                   'source_file_unchanged': True, 'source_static_glb_unchanged': True,
                   'model': str(destination.relative_to(ROOT)), 'model_sha256': sha(destination),
                   'model_bytes': destination.stat().st_size, 'morph_meshes': morph_meshes,
                   'minimum_target_gap_m': min_gap, 'exported_animations': 0,
                   'exported_skins': 0, 'all_images_buffers_embedded': True,
                   'source_black010_local_region': 'unknown retained; no whole component exemption',
                   'continuous_collision_proof': False, 'source_capture_method': 'render-matched VIEWPORT proxy at render subdivision; authored GN instances realized on unsaved temporary source evaluation'})
    persist()
    print('SINGLE_KEY_WEB_MORPH_READY', json.dumps({'model': str(destination), 'sha256': sha(destination), 'bytes': destination.stat().st_size, 'changed': changed, 'minimum_gap': min_gap}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        OUT.mkdir(parents=True, exist_ok=True)
        REPORT['status'] = 'STOP_TRANSPORT_OR_INTERPOLATION_FAILURE'
        REPORT['error'] = repr(exc)
        persist()
        raise
