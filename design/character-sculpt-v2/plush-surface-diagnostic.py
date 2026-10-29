"""Read-only C14C no-groom contrast: isolate fibers from skin/bump artifacts.

This is a diagnostic control, not a proposed smooth/plastic replacement coat.
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='artifacts/character-plush-surface-diagnostic')
    p.add_argument('--mode', choices=['hide', 'shorten'], default='hide')
    a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'receipt.json').exists():
        raise RuntimeError('Preserve existing evidence; use a fresh directory')
    helper = ROOT / 'design/character-sculpt-v2/eye-optics-diagnostic.py'
    spec = importlib.util.spec_from_file_location('miao_optic_helpers', helper)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    src = ROOT / 'artifacts/character-head-c14-color/miao-c14c-head-color.blend'
    before = h.sha(src)
    bpy.ops.wm.open_mainfile(filepath=str(src))
    s = bpy.context.scene
    geom, lights, mats = h.geometry_hash(), h.light_snapshot(), h.material_snapshot()
    hair = bpy.data.objects['Miao / native short plush']
    assert not hair.hide_render and len(hair.data.curves) == 180000
    def points(evaluated=False):
        ob = hair.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else hair
        v = np.empty(len(ob.data.position_data) * 3, np.float32)
        ob.data.position_data.foreach_get('vector', v)
        return v.reshape(-1, 4, 3)
    raw = points().copy()
    roots_before = points(True)[:, 0].copy()
    old_radius = np.empty(len(hair.data.position_data), np.float32)
    hair.data.attributes['radius'].data.foreach_get('value', old_radius)
    if a.mode == 'hide':
        hair.hide_render = True
    else:
        # One deliberately selected groom candidate, not a parameter sweep.
        shorter = raw[:, :1] + (raw - raw[:, :1]) * np.float32(.4)
        hair.data.position_data.foreach_set('vector', shorter.ravel())
        hair.data.attributes['radius'].data.foreach_set('value', old_radius * .4)
        hair.data.update_tag()
        bpy.context.view_layer.update()
        assert np.array_equal(points()[:, 0], raw[:, 0])
        assert np.max(np.abs(points(True)[:, 0] - roots_before)) < 1e-6
    original_camera = s.camera
    packet = json.loads((ROOT / 'artifacts/character-head-c14-color/receipt.json').read_text())
    head = next(x for x in packet['renders'] if x['name'] == 'color-head-front')
    cam = original_camera.copy()
    cam.data = original_camera.data.copy()
    cam.name = 'Plush diagnostic / owned head camera'
    s.collection.objects.link(cam)
    cam.matrix_world = Matrix(head['camera_matrix'])
    cam.data.type, cam.data.lens = head['type'], head['lens']
    cam.data.ortho_scale = head['ortho_scale']
    s.render.resolution_x = s.render.resolution_y = 1024
    s.render.resolution_percentage = 100
    s.render.use_border = False
    s.render.use_crop_to_border = False
    s.cycles.samples = 32
    s.cycles.seed = 17
    s.cycles.use_animated_seed = False
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGBA'
    s.render.image_settings.color_depth = '8'
    receipt = dict(scope='No-groom control or one short-fiber candidate; no quality pass',
                   blender=bpy.app.version_string, input_sha256=before,
                   helper_sha256=h.sha(helper), source_sha256=h.sha(__file__),
                   mode=a.mode, changes=('native short plush hide_render=True' if a.mode == 'hide'
                                         else 'same 180k roots; fiber offsets and radii scaled to 0.4'),
                   original_tip_lengths=[float(x) for x in np.quantile(np.linalg.norm(raw[:, -1] - raw[:, 0], axis=1), [0, .5, 1])],
                   renders=[])
    if a.mode == 'shorten':
        receipt['evaluated_root_displacement_max'] = float(np.max(np.linalg.norm(points(True)[:, 0] - roots_before, axis=1)))
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'miao-short-fiber-candidate.blend'), compress=True)
        receipt['native_sha256'] = h.sha(out / 'miao-short-fiber-candidate.blend')
    for label, camera in [('whole', original_camera), ('head', cam)]:
        s.camera = camera
        s.render.filepath = str(out / (a.mode + '-' + label + '.png'))
        start = time.monotonic()
        bpy.ops.render.render(write_still=True)
        receipt['renders'].append(dict(view=label, seconds=time.monotonic() - start,
                                       sha256=h.sha(s.render.filepath)))
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert h.geometry_hash() == geom and h.light_snapshot() == lights
    assert h.material_snapshot() == mats and h.sha(src) == before
    receipt.update(source_unchanged=True, geometry_lights_materials_unchanged=True,
                   status='rendered-awaiting-actual-inspection',
                   limits=['Removing fibers is a diagnostic, not a production asset.',
                           'Shorter/thinner groom is one unreviewed material study, not a passed coat.',
                           'Skin material, including bump and pigment, is unchanged.',
                           'No motion, coat/character quality, or production acceptance.'])
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('RESULT ' + json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
