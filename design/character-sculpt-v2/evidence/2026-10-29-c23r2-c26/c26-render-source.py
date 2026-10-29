"""One render buffer, noisy and denoised crop. No groom or shader changes.

Diagnostic only: raw sampling noise must not be relabelled as fine fur detail.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time
import bpy
import numpy as np
from mathutils import Matrix

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'public/sampled-audio.js').is_file())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='artifacts/character-plush-denoise-diagnostic')
    p.add_argument('--samples', type=int, default=32)
    p.add_argument('--coverage', action='store_true')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    if list(out.glob('*.png')) or (out / 'receipt.json').exists():
        raise RuntimeError('Use a fresh diagnostic directory')
    (out / 'executed-script.py').write_text(Path(__file__).read_text())
    helper = ROOT / 'design/character-sculpt-v2/eye-optics-diagnostic.py'
    sp = importlib.util.spec_from_file_location('miao_snapshots', helper)
    h = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(h)
    src = ROOT / 'artifacts/character-plush-coverage-c26/controlled-native-run/miao-c26-forehead-coverage-patch.blend'
    before = h.sha(src)
    bpy.ops.wm.open_mainfile(filepath=str(src))
    s = bpy.context.scene
    geom, lights, materials = h.geometry_hash(), h.light_snapshot(), h.material_snapshot()
    packet = json.loads((ROOT / 'artifacts/character-head-c14-color/receipt.json').read_text())
    head = next(x for x in packet['renders'] if x['name'] == 'color-head-front')
    s.camera.matrix_world = Matrix(head['camera_matrix'])
    s.camera.data.type, s.camera.data.lens = head['type'], head['lens']
    s.render.resolution_x = s.render.resolution_y = 1024
    s.render.resolution_percentage = 100
    s.render.use_border = s.render.use_crop_to_border = True
    s.render.border_min_x, s.render.border_max_x = .25, .75
    s.render.border_min_y, s.render.border_max_y = .30, .70
    s.cycles.samples = a.samples
    s.cycles.seed = 17
    s.cycles.use_animated_seed = False
    s.cycles.use_denoising = False
    bpy.context.view_layer.cycles.denoising_store_passes = True
    aov_node = None
    if a.coverage:
        aov = bpy.context.view_layer.aovs.add()
        aov.name, aov.type = 'FiberCoverage', 'COLOR'
        hairmat = bpy.data.objects['Miao / native short plush'].data.materials[0]
        aov_node = hairmat.node_tree.nodes.new('ShaderNodeOutputAOV')
        aov_node.aov_name = aov.name
        aov_node.inputs['Color'].default_value = (1, 1, 1, 1)
    group = bpy.data.node_groups.new('Plush diagnostic / one buffer two outputs', 'CompositorNodeTree')
    group.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    s.compositing_node_group = group
    n, l = group.nodes, group.links
    layers = n.new('CompositorNodeRLayers')
    denoise = n.new('CompositorNodeDenoise')
    l.new(layers.outputs['Image'], denoise.inputs['Image'])
    l.new(layers.outputs['Denoising Normal'], denoise.inputs['Normal'])
    l.new(layers.outputs['Denoising Albedo'], denoise.inputs['Albedo'])
    output = n.new('CompositorNodeOutputFile')
    output.directory = str(out)
    output.file_name = 'same-buffer'
    output.format.media_type = 'IMAGE'
    output.format.file_format = 'PNG'
    output.format.color_mode = 'RGBA'
    output.format.color_depth = '8'
    output.save_as_render = True
    for label, socket in [('noisy', layers.outputs['Image']), ('denoised', denoise.outputs['Image'])]:
        item = output.file_output_items.new('RGBA', label)
        alpha = n.new('CompositorNodeAlphaOver')
        alpha.inputs['Background'].default_value = (.94, .92, .86, 1)
        alpha.inputs['Factor'].default_value = 1
        l.new(socket, alpha.inputs['Foreground'])
        l.new(alpha.outputs['Image'], output.inputs[label])
        if label == 'denoised':
            end = n.new('NodeGroupOutput')
            l.new(alpha.outputs['Image'], end.inputs['Image'])
    if a.coverage:
        data = n.new('CompositorNodeOutputFile')
        data.directory, data.file_name = str(out), 'linear-'
        data.format.media_type = 'IMAGE'
        data.format.file_format, data.format.color_depth = 'OPEN_EXR', '32'
        data.save_as_render = False
        data.file_output_items.new('RGBA', 'fiber-coverage')
        l.new(layers.outputs['FiberCoverage'], data.inputs['fiber-coverage'])
    assert all(link.is_valid for link in l)
    t = time.monotonic()
    bpy.ops.render.render()
    files = sorted(out.glob('*.png'))
    assert len(files) == 2, [str(p) for p in out.rglob('*')]
    assert h.geometry_hash() == geom and h.light_snapshot() == lights
    snapshot = h.material_snapshot()
    if aov_node:
        snapshot[hairmat.name].pop(aov_node.name)
    assert snapshot == materials and h.sha(src) == before
    result = dict(scope='One-buffer noisy/denoised diagnostic, no art correction',
                  blender=bpy.app.version_string, source_sha256=h.sha(__file__),
                  input_sha256=before, render_calls=1, samples=a.samples, seed=17,
                  border=[.25, .75, .30, .70], seconds=time.monotonic()-t,
                  outputs=[dict(path=p.name, sha256=h.sha(p)) for p in files],
                  geometry_beauty_shaders_lights_and_source_unchanged=True,
                  limits=['No new groom/shader candidate or quality pass.',
                          'Raw sampling noise is not proof of fine hair geometry.',
                          'One fixed diagnostic crop; no full character/motion validation.'])
    if a.coverage:
        coverage_path = out / 'linear-fiber-coverage.exr'
        im = bpy.data.images.load(str(coverage_path), check_existing=False)
        values = np.empty(len(im.pixels), np.float32)
        im.pixels.foreach_get(values)
        rgb = np.flipud(values.reshape(im.size[1], im.size[0], 4)[:, :, :3]).copy()
        height, width = rgb.shape[:2]
        # Predeclared central forehead rectangle, top-origin relative crop coords.
        region = rgb[int(.14*height):int(.28*height), int(.25*width):int(.75*width), 0]
        result['fiber_aov'] = dict(file=coverage_path.name, sha256=h.sha(coverage_path),
                                  definition='Hair shader writes white AOV; skin/material/background default black. Antialiased coverage estimate, not fur beauty quality.',
                                  png_size=[width, height],
                                  forehead_roi_top_origin=[.25, .75, .14, .28],
                                  whole_crop_mean=float(rgb[:, :, 0].mean()),
                                  forehead_mean=float(region.mean()),
                                  forehead_fraction_over_half=float((region > .5).mean()),
                                  forehead_percentiles=np.quantile(region, [0, .5, .9, .99, 1]).tolist())
    (out / 'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print('RESULT ' + json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
