"""One isolated eight-white/five-black key layout; no animation or mesh creation.

Inspect first. The one proposed adaptation retains original source components,
widening only one octave and fitting original native wrists to its end keys.
This is a static numerical/design study, never an acceptance signature.
"""
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from single_key_geometry import RenderMatchedProxy, bounds, geometry, overlaps, record

SOURCE = ROOT / 'artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/keygroup-lift-color-native36.blend'
OUT = ROOT / 'artifacts/miao-eight-key-prop-probe-2026-10-30'
EXPECTED = 'ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(matrix):
    return [list(row) for row in matrix]


def pose_hash(rig):
    return hashlib.sha256(json.dumps([(p.name, rows(p.matrix_basis)) for p in rig.pose.bones]).encode()).hexdigest()


def item(obj):
    points, tris, _ = geometry(obj)
    lo, hi = bounds(points)
    return {'name': obj.name, 'world': rows(obj.matrix_world), 'bbox': [lo, hi],
            'center': [(a+b)/2 for a,b in zip(lo,hi)],
            'dimensions': [b-a for a,b in zip(lo,hi)], 'triangles': len(tris)}


def source_mesh_hash():
    sha=hashlib.sha256()
    for mesh in sorted(bpy.data.meshes,key=lambda m:m.name):
        sha.update(mesh.name.encode())
        sha.update(array.array('f',[x for v in mesh.vertices for x in v.co]).tobytes())
        sha.update(str([tuple(p.vertices) for p in mesh.polygons]).encode())
        sha.update(str([m.name if m else None for m in mesh.materials]).encode())
    return sha.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['inspect', 'probe', 'verify'], default='inspect')
    opts = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    assert bpy.app.version[:2] == (3,6)
    before = digest(SOURCE)
    assert before == EXPECTED
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    rig = bpy.data.objects['RIG-Cat']
    actions = len(bpy.data.actions)
    pose0 = pose_hash(rig)
    if opts.mode=='verify':
        native=OUT/'eight-key-isolated-static-native36.blend'
        receipt=json.loads((OUT/'candidate-probe.json').read_text())
        assert digest(native)==receipt['diagnostic_native_sha256']
        base_meshes=source_mesh_hash()
        bases={b.name:rows(b.matrix_basis) for b in rig.pose.bones}
        counts={'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'materials':len(bpy.data.materials),'actions':len(bpy.data.actions)}
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        rig=bpy.data.objects['RIG-Cat']
        candidate_counts={'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'materials':len(bpy.data.materials),'actions':len(bpy.data.actions)}
        altered=[b.name for b in rig.pose.bones if bases[b.name]!=rows(b.matrix_basis)]
        result={'status':'NATIVE_REOPEN_STATIC_INVARIANTS_PASS', 'source_sha256':before,
                'native_sha256':digest(native),'original_base_meshes_material_slots_sha256':base_meshes,
                'reopened_base_meshes_material_slots_sha256':source_mesh_hash(),
                'source_counts':counts,'candidate_counts':candidate_counts,
                'changed_pose_bones':altered,'reopened_pose_sha256':pose_hash(rig),
                'not_an_art_or_motion_approval':True}
        assert counts==candidate_counts
        assert base_meshes==result['reopened_base_meshes_material_slots_sha256']
        assert set(altered)=={'IK-MSTR-Hand.L','IK-MSTR-Hand.R'}
        assert result['reopened_pose_sha256']==receipt['native_pose_sha256']
        assert digest(SOURCE)==before
        (OUT/'native-reopen-verification.json').write_text(json.dumps(result,indent=2)+'\n')
        print('RESULT '+json.dumps(result))
        return
    props = [o for o in scene.objects if o.type=='MESH' and o.name.startswith(('Ivory piano key', 'Raised black piano key', 'Controller chassis', 'Top rotary control', 'Top control index'))]
    source_matrices = {o.name: o.matrix_world.copy() for o in props}
    report = {'status': 'READ_ONLY_LAYOUT_INSPECTION', 'source': str(SOURCE.relative_to(ROOT)),
              'source_sha256': before, 'source_pose': pose0, 'blender': bpy.app.version_string,
              'embedded_scripts_executed': [], 'new_actions': 0, 'proposed_motion': False}
    with RenderMatchedProxy():
        report['source_props'] = [item(o) for o in props]
        report['native_arms'] = {}
        for side in ['L','R']:
            shoulder = rig.matrix_world @ rig.pose.bones['ORG-UpperArm.'+side].head
            wrist = rig.matrix_world @ rig.pose.bones['ORG-Hand.'+side].head
            length = sum(rig.pose.bones[n+side].bone.length for n in ['ORG-UpperArm.','ORG-Forearm.'])
            report['native_arms'][side] = {'shoulder': list(shoulder), 'wrist': list(wrist), 'length': length, 'reach_ratio': (wrist-shoulder).length/length,
                                          'control': rows(rig.matrix_world @ rig.pose.bones['IK-MSTR-Hand.'+side].matrix)}
        hand = bpy.data.objects['GEO-hands']
        points, tris, weights = geometry(hand)
        report['source_pads'] = {}
        for side in ['L','R']:
            gi = hand.vertex_groups['DEF-Index2.'+side].index
            ids = [i for i,w in enumerate(weights) if w.get(gi,0)>.6]
            low = min(ids, key=lambda i: points[i].z)
            report['source_pads'][side] = {'bbox': bounds([points[i] for i in ids]), 'lowest': list(points[low]), 'lowest_vertex': low}
    (OUT/'source-inspection.json').write_text(json.dumps(report, indent=2)+'\n')
    assert digest(SOURCE)==before and pose_hash(rig)==pose0 and len(bpy.data.actions)==actions
    if opts.mode=='inspect':
        print('RESULT '+json.dumps({'status':report['status'], 'props':len(props), 'source_unchanged':True}))
        return
    # One fixed adaptation derived from source dimensions, not a pose/scale sweep.
    # The existing whole scene remains intact; unused CC0 prop components are
    # hidden only in this isolated diagnostic derivative.
    selected_whites = ['Ivory piano key.'+str(i).zfill(3) for i in range(14,22)]
    selected_blacks = ['Raised black piano key.'+str(i).zfill(3) for i in range(10,15)]
    retained_controls = ['Top rotary control', 'Top rotary control.007',
                         'Top control index', 'Top control index.007']
    retained = set(selected_whites+selected_blacks+retained_controls+['Controller chassis'])
    hidden = []
    for obj in props:
        if obj.name not in retained:
            obj.hide_render = True
            obj.hide_viewport = True
            hidden.append(obj.name)
    sx = Matrix.Diagonal((3.4,1,1,1))
    for name in selected_whites+selected_blacks:
        bpy.data.objects[name].matrix_world = sx @ source_matrices[name]
    case = bpy.data.objects['Controller chassis']
    case_center = next(o['center'][0] for o in report['source_props'] if o['name']==case.name)
    case_fit = Matrix.Translation((-0.7*case_center,0,0)) @ Matrix.Diagonal((0.7,1,1,1))
    case.matrix_world = case_fit @ source_matrices[case.name]
    for stem in ['Top rotary control','Top control index']:
        for suffix,x in [('',.20),('.007',-.20)]:
            obj = bpy.data.objects[stem+suffix]
            mat = source_matrices[obj.name].copy()
            mat.translation.x = x
            obj.matrix_world = mat
    bpy.context.view_layer.update()
    changed_bones = ['IK-MSTR-Hand.L','IK-MSTR-Hand.R']
    original_bases = {b.name:rows(b.matrix_basis) for b in rig.pose.bones}
    shifts = {}
    # Maintain original orientations, finger controls, Y/Z pad clearance, elbow
    # pole and source nonstretch IK. Move only the original wrist in world X.
    for side,name in [('L',selected_whites[0]),('R',selected_whites[-1])]:
        desired = (bounds(geometry(bpy.data.objects[name])[0]))
        x = (desired[0][0]+desired[1][0])/2
        dx = x-report['source_pads'][side]['lowest'][0]
        control = rig.pose.bones['IK-MSTR-Hand.'+side]
        mat = rig.matrix_world @ control.matrix
        mat.translation.x += dx
        control.matrix = rig.matrix_world.inverted() @ mat
        bpy.context.view_layer.update()
        shifts[side] = {'target_key':name,'target_key_center_x':x,'wrist_world_dx_m':dx}
    assert all(rows(b.matrix_basis)==original_bases[b.name] for b in rig.pose.bones if b.name not in changed_bones)
    visible_props = [o for o in props if o.name in retained]
    with RenderMatchedProxy():
        records = [record(o) for o in visible_props]
        report['candidate_props'] = [item(o) for o in visible_props]
        report['candidate_arms'] = {}
        for side in ['L','R']:
            shoulder = rig.matrix_world @ rig.pose.bones['ORG-UpperArm.'+side].head
            wrist = rig.matrix_world @ rig.pose.bones['ORG-Hand.'+side].head
            length = report['native_arms'][side]['length']
            report['candidate_arms'][side] = {'shoulder':list(shoulder),'wrist':list(wrist),
                                             'reach_ratio':(wrist-shoulder).length/length,
                                             'original_length_m':length,
                                             'evaluated_segment_lengths_m':[rig.pose.bones[n+side].length for n in ['ORG-UpperArm.','ORG-Forearm.']]}
        report['candidate_cat_vs_instrument'] = {}
        for name in ['GEO-hands','GEO-arms','GEO-body','GEO-head','GEO-legs','GEO-feet']:
            obj = bpy.data.objects.get(name)
            if obj is None or obj.type!='MESH':continue
            p,t,_ = geometry(obj)
            report['candidate_cat_vs_instrument'][name] = overlaps(p,t,records)
        p,t,weights = geometry(hand)
        report['candidate_pads'] = {}
        for side in ['L','R']:
            gi = hand.vertex_groups['DEF-Index2.'+side].index
            ids = [i for i,w in enumerate(weights) if w.get(gi,0)>.6]
            low = min(ids,key=lambda i:p[i].z)
            name = shifts[side]['target_key']
            rec = next(r for r in records if r['name']==name)
            projected = []
            for i in ids:
                hit,n,_,_ = rec['tree'].ray_cast(Vector((p[i].x,p[i].y,2)),Vector((0,0,-1)),3)
                if hit is not None and n.z>.9: projected.append(p[i].z-hit.z)
            report['candidate_pads'][side] = {'lowest':list(p[low]),'bbox':bounds([p[i] for i in ids]),
                                             'target_key':name,'projected_pad_points':len(projected),
                                             'minimum_target_top_gap_m':min(projected) if projected else None,
                                             'nearest_target_distance_m':min(rec['tree'].find_nearest(p[i])[3] for i in ids)}
        report['key_case_intersections'] = {}
        case_record = next(r for r in records if r['name']==case.name)
        for name in selected_whites+selected_blacks:
            p,t,_ = geometry(bpy.data.objects[name])
            hits = overlaps(p,t,[case_record])
            if hits:report['key_case_intersections'][name] = hits
    report.update(status='NUMERIC_STATIC_PROBE_ONLY', retained_whites=selected_whites,
                  retained_blacks=selected_blacks, retained_controls=retained_controls,
                  hidden_source_components=hidden, key_world_x_scale=3.4,
                  case_world_x_scale=0.7, wrist_shifts=shifts,
                  native_pose_sha256=pose_hash(rig), new_meshes=0,
                  source_base_meshes_modified=False, source_materials_modified=False,
                  source_restored_on_disk=True, animation_permitted=False,
                  geometry_method='RenderMatchedProxy, not direct render depsgraph',
                  continuous_collision_or_motion='unverified; none authored')
    report['stop_reasons'] = []
    if any(report['candidate_cat_vs_instrument'].values()): report['stop_reasons'].append('visible cat/instrument triangle intersections')
    if report['key_case_intersections']:report['stop_reasons'].append('key/case triangle intersections')
    if any(a['reach_ratio']>.95 for a in report['candidate_arms'].values()):report['stop_reasons'].append('wrist exceeds fixed 95 percent original reach')
    if any(a['minimum_target_top_gap_m'] is None or a['minimum_target_top_gap_m']<0 for a in report['candidate_pads'].values()):report['stop_reasons'].append('pad misses or penetrates target')
    report['source_sha256_after'] = digest(SOURCE)
    assert report['source_sha256_after']==before and len(bpy.data.actions)==actions
    if report['stop_reasons']:
        report['status'] = 'STOP_STATIC_NUMERIC_PROBE'
        (OUT/'candidate-probe.json').write_text(json.dumps(report,indent=2)+'\n')
        print('RESULT '+json.dumps({'status':report['status'],'stop_reasons':report['stop_reasons']}))
        return
    # A single complete colored static diagnostic only, not review-sheet approval.
    camera = scene.camera
    camera.location = (0,-3,1.5)
    target = Vector((0,-.13,.53))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'
    camera.data.ortho_scale=1.38
    helper=bpy.data.objects['HLP-scene_camera_dummy']
    for driver in helper.animation_data.drivers:
        if driver.data_path=='rotation_euler':driver.mute=True
    bpy.context.view_layer.update()
    helper.rotation_euler=camera.matrix_world.to_euler()
    bpy.context.view_layer.update()
    helper_error=max(abs(helper.rotation_euler[i]-camera.matrix_world.to_euler()[i]) for i in range(3))
    assert helper_error<1e-6
    scene.render.resolution_x=1100
    scene.render.resolution_y=1100
    scene.render.resolution_percentage=100
    scene.render.filepath=str(OUT/'eight-key-front-diagnostic.png')
    bpy.ops.render.render(write_still=True)
    native=OUT/'eight-key-isolated-static-native36.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    report.update(status='ONE_STATIC_DIAGNOSTIC_PENDING_ALL_GATES',
                  render=str(Path(scene.render.filepath).relative_to(ROOT)),
                  diagnostic_native=str(native.relative_to(ROOT)),
                  diagnostic_native_sha256=digest(native), camera_helper_error=helper_error)
    assert digest(SOURCE)==before and len(bpy.data.actions)==actions
    (OUT/'candidate-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RESULT '+json.dumps({'status':report['status'],'source_unchanged':True,'new_actions':0,'native':str(native.relative_to(ROOT))}))


if __name__=='__main__':
    main()
