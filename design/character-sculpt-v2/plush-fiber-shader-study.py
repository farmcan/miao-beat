"""One C21 revision: same shorter fibers, a native hair scattering shader.

Official node semantics: Blender manual hair_principled.html; local RNA checked.
No new coat color painting, density, light or geometry sweep.
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

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='artifacts/character-plush-short-fiber-c21-r2')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'receipt.json').exists():
        raise RuntimeError('Preserve previous evidence')
    helper = ROOT / 'design/character-sculpt-v2/eye-optics-diagnostic.py'
    sp = importlib.util.spec_from_file_location('miao_snapshot', helper)
    h = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(h)
    src = ROOT / 'artifacts/character-plush-short-fiber-c21/miao-short-fiber-candidate.blend'
    source_sha = h.sha(src)
    bpy.ops.wm.open_mainfile(filepath=str(src))
    s = bpy.context.scene
    original_camera = s.camera
    geom, lights, original_materials = h.geometry_hash(), h.light_snapshot(), h.material_snapshot()
    hair = bpy.data.objects['Miao / native short plush']
    raw = np.empty(len(hair.data.position_data)*3, np.float32)
    hair.data.position_data.foreach_get('vector', raw)
    original_shader = hair.data.materials[0]
    mat = original_shader.copy()
    mat.name = 'C21 / short fiber native hair scattering'
    n, l = mat.node_tree.nodes, mat.node_tree.links
    skin = n.get('Principled BSDF')
    base = next(link.from_socket for link in mat.node_tree.links if link.to_socket == skin.inputs['Base Color'])
    fiber = n.new('ShaderNodeBsdfHairPrincipled')
    fiber.model = 'CHIANG'
    fiber.parametrization = 'COLOR'
    fiber.inputs['Roughness'].default_value = .5
    fiber.inputs['Radial Roughness'].default_value = .5
    fiber.inputs['IOR'].default_value = 1.55
    fiber.inputs['Coat'].default_value = 0
    l.new(base, fiber.inputs['Color'])
    output = next(x for x in n if x.type == 'OUTPUT_MATERIAL' and x.is_active_output)
    for link in list(output.inputs['Surface'].links):
        l.remove(link)
    l.new(fiber.outputs[0], output.inputs['Surface'])
    hair.data.materials.clear()
    hair.data.materials.append(mat)
    assert all(link.is_valid for link in l)
    assert all(h.material_snapshot()[name] == value for name, value in original_materials.items())
    packet = json.loads((ROOT / 'artifacts/character-head-c14-color/receipt.json').read_text())
    head = next(x for x in packet['renders'] if x['name'] == 'color-head-front')
    camera = original_camera.copy()
    camera.data = original_camera.data.copy()
    camera.name = 'C21 r2 / owned head diagnostic'
    s.collection.objects.link(camera)
    camera.matrix_world = Matrix(head['camera_matrix'])
    camera.data.type, camera.data.lens = head['type'], head['lens']
    camera.data.ortho_scale = head['ortho_scale']
    s.render.resolution_x = s.render.resolution_y = 1024
    s.render.resolution_percentage = 100
    s.cycles.samples = 32
    s.cycles.seed = 17
    s.cycles.use_animated_seed = False
    bpy.context.preferences.filepaths.save_version = 0
    native = out / 'miao-fiber-scattering-candidate.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
    receipt = dict(scope='C21 one material revision; not reviewed or accepted',
                   input_sha256=source_sha, source_sha256=h.sha(__file__),
                   native_sha256=h.sha(native), blender=bpy.app.version_string,
                   reference='public/character/instrument-scenes-v1/guitar/idle.jpg',
                   change='Only hair material output changes to direct-color native Principled Hair Chiang',
                   shader=dict(model='CHIANG', parametrization='COLOR', roughness=.5,
                               radial_roughness=.5, ior=1.55, coat=0), renders=[])
    for label, cam in [('whole', original_camera), ('head', camera)]:
        s.camera = cam
        s.render.filepath = str(out / ('fiber-' + label + '.png'))
        t = time.monotonic()
        bpy.ops.render.render(write_still=True)
        receipt['renders'].append(dict(view=label, seconds=time.monotonic()-t,
                                      sha256=h.sha(s.render.filepath)))
    final = np.empty_like(raw)
    hair.data.position_data.foreach_get('vector', final)
    assert np.array_equal(raw, final) and h.geometry_hash() == geom
    assert h.light_snapshot() == lights and h.sha(src) == source_sha
    receipt.update(source_unchanged=True, mesh_hair_geometry_and_lights_unchanged=True,
                   limits=['Not an animation, material or whole-character pass.',
                           'Source uses old C14C eyes and unaccepted paws; independent coat comparison only.',
                           'No added fibers, light or texture. The shorter-fiber r1 geometry is reused.'])
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print('RESULT ' + json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
