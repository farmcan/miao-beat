"""C17: bounded three-case optical-layer diagnosis, never a delivery asset.

Reopens the frozen C14C native for each case.  Only the named cornea IOR or
render visibility changes. No image editing, geometry fix, animation or network.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Matrix


ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry_hash():
    """Raw scene geometry; the input native and all generated settings are frozen."""
    h = hashlib.sha256()
    for ob in sorted(bpy.context.scene.objects, key=lambda x: x.name):
        if ob.type == 'MESH':
            a = np.empty(len(ob.data.vertices) * 3, np.float32)
            ob.data.vertices.foreach_get('co', a)
            h.update(ob.name.encode()); h.update(a.tobytes())
            h.update(np.asarray(ob.matrix_world, dtype=np.float64).tobytes())
    return h.hexdigest()


def light_snapshot():
    return [dict(name=o.name, matrix=[list(r) for r in o.matrix_world],
                 energy=o.data.energy, color=list(o.data.color),
                 type=o.data.type, size=getattr(o.data, 'size', None),
                 hide_render=o.hide_render,
                 receivers=(o.light_linking.receiver_collection.name
                            if o.light_linking.receiver_collection else None))
            for o in sorted(bpy.context.scene.objects, key=lambda x: x.name)
            if o.type == 'LIGHT']


def material_snapshot():
    result = {}
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        nodes = {}
        for n in m.node_tree.nodes:
            sockets = {}
            for inp in n.inputs:
                if hasattr(inp, 'default_value'):
                    value = inp.default_value
                    if isinstance(value, (int, float, bool, str)):
                        sockets[inp.name] = value
                    else:
                        try: sockets[inp.name] = list(value)
                        except TypeError: pass
            nodes[n.name] = sockets
        result[m.name] = nodes
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='artifacts/character-head-c14-color/miao-c14c-head-color.blend')
    p.add_argument('--out', default='artifacts/character-eye-optics-c17')
    p.add_argument('--size', type=int, default=1024)
    p.add_argument('--samples', type=int, default=32)
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    src = (ROOT / a.input).resolve(); out = (ROOT / a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'receipt.json').exists():
        raise RuntimeError('Use a fresh output directory; preserve prior diagnosis')
    before = sha(src)
    reference = ROOT / 'public/character/instrument-scenes-v1/guitar/idle.jpg'
    ref_sha = sha(reference)
    packet = json.loads((ROOT / 'artifacts/character-head-c14-color/receipt.json').read_text())
    head_camera = next(x for x in packet['renders'] if x['name'] == 'color-head-front')
    receipt = dict(stage='C17-single-variable-eye-layer-diagnosis',
                   input=str(src.relative_to(ROOT)), input_sha256=before,
                   reference_sha256=ref_sha, source_sha256=sha(__file__),
                   blender=bpy.app.version_string, cases=[], status='rendering',
                   limits=['Diagnostic only; cornea hiding is not a proposed production fix.',
                           'IOR change affects reflection and transmission together.',
                           'No normal/light/iris edits; remaining causes cannot be uniquely separated.',
                           'No animation, web, Cloudflare, paid service, commit or push.'])
    baseline_geometry = baseline_lights = baseline_materials = None
    for case, ior, hidden in [('A-original', 1.38, False),
                              ('B-ior-one', 1.0, False),
                              ('C-cornea-hidden', 1.38, True)]:
        bpy.ops.wm.open_mainfile(filepath=str(src))
        s = bpy.context.scene
        original_camera = s.camera
        corneas = [bpy.data.objects['C7 / clear cornea '+side] for side in ['L', 'R']]
        mat = bpy.data.materials['C7 / clear thin cornea']
        bs = mat.node_tree.nodes['Principled BSDF']
        assert abs(bs.inputs['IOR'].default_value-1.38) < 1e-5
        assert all(not o.hide_render for o in corneas)
        geom = geometry_hash(); lights = light_snapshot(); materials = material_snapshot()
        if baseline_geometry is None:
            baseline_geometry, baseline_lights, baseline_materials = geom, lights, materials
        assert geom == baseline_geometry and lights == baseline_lights and materials == baseline_materials
        bs.inputs['IOR'].default_value = ior
        for ob in corneas: ob.hide_render = hidden
        after_mat = material_snapshot()
        expected = json.loads(json.dumps(baseline_materials))
        expected[mat.name]['Principled BSDF']['IOR'] = bs.inputs['IOR'].default_value
        assert after_mat == expected, 'Unexpected material edit'
        assert geometry_hash() == baseline_geometry and light_snapshot() == baseline_lights
        s.render.resolution_x = s.render.resolution_y = a.size
        s.render.resolution_percentage = 100
        s.render.use_border = False; s.render.use_crop_to_border = False
        s.render.image_settings.file_format = 'PNG'
        s.render.image_settings.color_mode = 'RGBA'
        s.render.image_settings.color_depth = '8'
        s.cycles.samples = a.samples; s.cycles.seed = 17; s.cycles.use_animated_seed = False
        camera = original_camera.copy(); camera.data = original_camera.data.copy()
        camera.name = 'C17 / owned matched head camera'; s.collection.objects.link(camera)
        camera.matrix_world = Matrix(head_camera['camera_matrix'])
        camera.data.type = head_camera['type']; camera.data.lens = head_camera['lens']
        camera.data.ortho_scale = head_camera['ortho_scale']
        item = dict(case=case, cornea_ior=bs.inputs['IOR'].default_value,
                    cornea_hide_render=hidden, geometry_sha256=geom,
                    only_expected_material_change=True, lights_unchanged=True, renders=[])
        for view, cam in [('whole', original_camera), ('head', camera)]:
            s.camera = cam
            s.render.filepath = str(out / (case+'-'+view+'.png'))
            start = time.time(); bpy.ops.render.render(write_still=True)
            item['renders'].append(dict(view=view, filename=Path(s.render.filepath).name,
                                        sha256=sha(s.render.filepath), seconds=time.time()-start,
                                        camera_matrix=[list(row) for row in cam.matrix_world],
                                        camera_type=cam.data.type, lens=cam.data.lens,
                                        ortho_scale=cam.data.ortho_scale))
        receipt['cases'].append(item)
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    assert sha(src) == before and sha(reference) == ref_sha
    receipt.update(status='rendered-awaiting-builder-inspection', source_native_unchanged=True,
                   geometry_and_lights_identical_between_cases=True)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print('RESULT '+json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
