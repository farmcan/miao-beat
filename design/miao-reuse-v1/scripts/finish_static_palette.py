"""Observe the fixed single hold and recolor only received material colors."""
import hashlib
import json
import pathlib
import sys

import bpy
from mathutils import Vector

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
scene = bpy.context.scene
camera = scene.camera
rig = bpy.data.objects['RIG-Cat']


def pose_hash():
    digest = hashlib.sha256()
    for bone in rig.pose.bones:
        digest.update(bone.name.encode())
        digest.update(repr([list(row) for row in bone.matrix_basis]).encode())
    return digest.hexdigest()


def srgb_to_linear(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def render_view(name, target, direction, ortho_scale, resolution=1200):
    center = Vector(target)
    camera.location = center + Vector(direction).normalized() * 4.0
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = ortho_scale
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    scene.render.filepath = str(output / f'{name}.png')
    bpy.ops.render.render(write_still=True)


views = [
    ('front', (0.0, -0.01, 0.56), (0.0, -4.0, 0.18), 1.42),
    ('three-quarter', (0.0, -0.01, 0.56), (1.4, -4.0, 0.65), 1.42),
    ('left-hand', (0.082, -0.24, 0.385), (0.9, -4.0, 1.0), 0.285),
    ('right-hand', (-0.10, -0.26, 0.28), (-0.8, -4.0, 1.3), 0.285),
    ('face', (0.0, -0.045, 0.77), (0.5, -4.0, 0.25), 0.71),
]
pose_before = pose_hash()
for name, target, direction, scale in views[2:]:
    render_view(f'original-{name}-fix1', target, direction, scale)

palette = {
    'cat.fur_dark': (0.88, 0.42, 0.12),
    'cat.fur_bright': (1.0, 0.88, 0.65),
    'cat.fur_spikes_bright': (1.0, 0.88, 0.65),
    'cat.suit_blue': (0.16, 0.20, 0.23),
    'cat.suit_red': (0.28, 0.14, 0.08),
    'cat.blue_dark': (0.06, 0.075, 0.085),
}
material_changes = []
for name, srgb_color in palette.items():
    material = bpy.data.materials.get(name)
    if not material:
        continue
    shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    base = shader.inputs['Base Color']
    source_color = tuple(base.default_value)
    target_color = tuple(srgb_to_linear(channel) for channel in srgb_color)
    item = {'material': name, 'source_default': list(source_color), 'target_srgb': list(srgb_color), 'target_linear': list(target_color)}
    if base.is_linked:
        old_link = base.links[0]
        source_socket = old_link.from_socket
        material.node_tree.links.remove(old_link)
        tint = material.node_tree.nodes.new('ShaderNodeMixRGB')
        tint.name = 'MIAO-STATIC-PALETTE-TINT'
        tint.label = 'Static palette tint; original texture retained'
        tint.blend_type = 'MULTIPLY'
        tint.inputs[0].default_value = 1.0
        tint.use_clamp = False
        ratios = tuple(target_color[index] / max(source_color[index], 0.0001) for index in range(3))
        tint.inputs[2].default_value = (*ratios, 1.0)
        material.node_tree.links.new(source_socket, tint.inputs[1])
        material.node_tree.links.new(tint.outputs[0], base)
        item['method'] = 'multiply original texture by per-channel color ratio'
        item['ratios'] = list(ratios)
    else:
        base.default_value = (*target_color, 1.0)
        item['method'] = 'base color only'
    material.diffuse_color = (*target_color, 1.0)
    material_changes.append(item)

for name, target, direction, scale in views:
    render_view(f'warm-{name}-fix1', target, direction, scale)
pose_after = pose_hash()
assert pose_before == pose_after, 'Palette changed the hold pose'
for text in bpy.data.texts:
    text.use_module = False
working_copy = output / 'static-hold-warm-v1-fix1.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(working_copy), copy=True)
receipt = {
    'source': str(source),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'working_copy': str(working_copy),
    'working_sha256': hashlib.sha256(working_copy.read_bytes()).hexdigest(),
    'blender_version': bpy.app.version_string,
    'upstream_scripts_executed': [],
    'auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'pose_sha_before': pose_before,
    'pose_sha_after': pose_after,
    'material_changes': material_changes,
    'pose_changes': [],
    'geometry_changes': [],
    'known_gaps': ['left eye white triangle survives pupil reset', 'sealed mouth lacks a clear mouth line', 'hand contact requires independent review', 'upstream guitar brand/side material remains research-only'],
    'status': 'same-pose palette trial; not delivered art; pending three-role static gate',
}
(output / 'static-hold-warm-v1-fix1-receipt.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps({'working_copy': str(working_copy), 'pose_unchanged': pose_before == pose_after, 'material_changes': len(material_changes)}))
