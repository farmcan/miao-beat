"""C18 D: one bounded cornea closure contrast, not a production eye fix.

Same native, geometry, IOR, roughness, normals and light setup as C17 A.
Pure GGX refraction removes the reflected lobe but also changes Fresnel energy
partition and multiscatter compensation: this is not an exact isolated-lobe ablation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='artifacts/character-eye-optics-c18-reflection')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out = ROOT / a.out; out.mkdir(parents=True, exist_ok=True)
    if (out / 'receipt.json').exists():
        raise RuntimeError('Use a new output directory to preserve the diagnostic')
    helper_path = ROOT / 'design/character-sculpt-v2/eye-optics-diagnostic.py'
    helper_spec = importlib.util.spec_from_file_location('c17_helpers', helper_path)
    helper = importlib.util.module_from_spec(helper_spec); helper_spec.loader.exec_module(helper)
    c17dir = ROOT / 'artifacts/character-eye-optics-c17'
    prior = json.loads((c17dir / 'receipt.json').read_text())
    baseline = next(c for c in prior['cases'] if c['case'] == 'A-original')
    for x in baseline['renders']:
        assert sha(c17dir / x['filename']) == x['sha256']
    src = ROOT / prior['input']; assert sha(src) == prior['input_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(src))
    s = bpy.context.scene; cam0 = s.camera
    geom0 = helper.geometry_hash(); lights0 = helper.light_snapshot()
    assert geom0 == baseline['geometry_sha256']
    materials0 = helper.material_snapshot()
    mat = bpy.data.materials['C7 / clear thin cornea']
    nt = mat.node_tree; bs = nt.nodes['Principled BSDF']
    output = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
    incoming = list(output.inputs['Surface'].links)
    assert len(incoming) == 1 and incoming[0].from_node == bs
    assert not bs.inputs['Normal'].is_linked
    params = {k: bs.inputs[k].default_value for k in
              ['IOR', 'Roughness', 'Transmission Weight', 'Metallic', 'Coat Weight',
               'Sheen Weight', 'Emission Strength', 'Alpha']}
    params['distribution'] = bs.distribution
    params['Base Color'] = list(bs.inputs['Base Color'].default_value)
    params['Normal_unlinked'] = True
    assert abs(params['IOR']-1.38) < 1e-5
    assert abs(params['Roughness']-.035) < 1e-5
    assert params['Transmission Weight'] == 1.0 and params['Metallic'] == 0.0
    assert params['Coat Weight'] == params['Sheen Weight'] == params['Emission Strength'] == 0.0
    assert params['Alpha'] == 1.0 and params['Base Color'] == [1.0, 1.0, 1.0, 1.0]
    refr = nt.nodes.new('ShaderNodeBsdfRefraction'); refr.name = 'C18 / diagnostic refraction only'
    refr.distribution = 'GGX'
    refr.inputs['Color'].default_value = params['Base Color']
    refr.inputs['IOR'].default_value = params['IOR']
    refr.inputs['Roughness'].default_value = params['Roughness']
    nt.links.remove(incoming[0]); nt.links.new(refr.outputs['BSDF'], output.inputs['Surface'])
    materials1 = helper.material_snapshot()
    for name in materials0:
        if name != mat.name: assert materials0[name] == materials1[name]
    assert helper.geometry_hash() == geom0 and helper.light_snapshot() == lights0
    for side in ['L', 'R']:
        assert not bpy.data.objects['C7 / clear cornea '+side].hide_render
    r = dict(stage='C18-D-refraction-only-closure-contrast', status='rendering',
             input=prior['input'], input_sha256=prior['input_sha256'],
             source_sha256=sha(__file__), helper_source_sha256=sha(helper_path),
             reused_baseline_receipt_sha256=sha(c17dir / 'receipt.json'),
             baseline_renders=baseline['renders'], blender=bpy.app.version_string,
             build_hash=bpy.app.build_hash.decode(), original_principled=params,
             changed_cornea_surface=dict(node='ShaderNodeBsdfRefraction', distribution='GGX',
                                         IOR=params['IOR'], roughness=params['Roughness'],
                                         color=params['Base Color'], normal_unlinked=True),
             geometry_sha256=geom0, all_non_cornea_materials_unchanged=True,
             geometry_lights_and_visibility_unchanged=True, renders=[],
             couplings=['Removes the reflected closure and the Principled glass Fresnel energy split.',
                        'Uses single-scatter GGX refraction instead of Principled multi-GGX glass.',
                        'Nominal IOR, roughness, white transmission, default normal and two interfaces retained.',
                        'Therefore not a mathematically exact isolated-reflection ablation.'],
             limits=['One new closure setting only; no parameter sweep.',
                     'Baseline A is reused and its output SHA checked; C17 files untouched.',
                     'Diagnostic only, not an accepted eye/material or motion.',
                     'No animation, web, Cloudflare, paid API, commit or push.'])
    s.render.resolution_x = s.render.resolution_y = 1024
    s.render.resolution_percentage = 100; s.render.use_border = False; s.render.use_crop_to_border = False
    s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
    s.render.image_settings.color_depth = '8'
    s.cycles.samples = 32; s.cycles.seed = 17; s.cycles.use_animated_seed = False
    hc = next(x for x in baseline['renders'] if x['view'] == 'head')
    head = cam0.copy(); head.data = cam0.data.copy(); head.name = 'C18 / diagnostic matched head camera'
    s.collection.objects.link(head); head.matrix_world = Matrix(hc['camera_matrix'])
    head.data.type = hc['camera_type']; head.data.lens = hc['lens']; head.data.ortho_scale = hc['ortho_scale']
    for view, camera in [('whole', cam0), ('head', head)]:
        s.camera = camera; s.render.filepath = str(out / ('D-refraction-only-'+view+'.png'))
        start = time.time(); bpy.ops.render.render(write_still=True)
        r['renders'].append(dict(view=view, filename=Path(s.render.filepath).name,
                                 sha256=sha(s.render.filepath), seconds=time.time()-start,
                                 camera_matrix=[list(row) for row in camera.matrix_world],
                                 camera_type=camera.data.type, lens=camera.data.lens,
                                 ortho_scale=camera.data.ortho_scale))
        (out / 'receipt.json').write_text(json.dumps(r, indent=2)+'\n')
    assert sha(src) == prior['input_sha256']
    assert sha(c17dir / 'receipt.json') == r['reused_baseline_receipt_sha256']
    assert helper.geometry_hash() == geom0 and helper.light_snapshot() == lights0
    r.update(status='rendered-awaiting-builder-inspection', source_native_unchanged=True,
             C17_receipt_and_baseline_images_unchanged=True)
    (out / 'receipt.json').write_text(json.dumps(r, indent=2)+'\n')
    print('RESULT '+json.dumps(r), flush=True)


if __name__ == '__main__':
    main()
