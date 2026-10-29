"""Read-only original torso/shoulder/head/arm control-chain diagnostic.

Opens two native files with scripts disabled. Never edits a pose, saves a blend,
executes embedded code, or renders. Exports actual constraint and frame evidence.
"""
import hashlib
import json
import pathlib
import sys

import bpy

args = sys.argv[sys.argv.index('--') + 1:]
output = pathlib.Path(args[0]).resolve()
output.mkdir(parents=True, exist_ok=True)
paths = [pathlib.Path(value).resolve() for value in args[1:]]
bpy.context.preferences.filepaths.use_scripts_auto_execute = False


def clean(value):
    if hasattr(value, 'to_dict'):
        return clean(value.to_dict())
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    try:
        return [clean(item) for item in value]
    except TypeError:
        return repr(value)


def constraint_record(constraint):
    result = {'name': constraint.name, 'type': constraint.type}
    fields = ['influence', 'target', 'subtarget', 'owner_space', 'target_space',
              'pole_target', 'pole_subtarget', 'pole_angle', 'chain_count',
              'use_stretch', 'mix_mode', 'use_x', 'use_y', 'use_z']
    for field in fields:
        if not hasattr(constraint, field):
            continue
        value = getattr(constraint, field)
        if isinstance(value, bpy.types.ID):
            value = value.name
        result[field] = value
    if constraint.type == 'ARMATURE':
        result['targets'] = [
            {'object': target.target.name if target.target else None,
             'bone': target.subtarget, 'weight': target.weight}
            for target in constraint.targets
        ]
    return result


report = {'scope': 'read-only chain diagnostic; no pose edits/render/native save',
          'blender': bpy.app.version_string, 'files': []}
for path in paths:
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    bpy.context.view_layer.update()
    rig = bpy.data.objects['RIG-Cat']
    selected = set()
    for bone in rig.pose.bones:
        token_match = any(token in bone.name for token in
                          ['Spine', 'Torso', 'Chest', 'Shoulder', 'Clavicle', 'Pelvis', 'Hips'])
        arm_match = any(token in bone.name for token in
                        ['UpperArm.', 'Forearm.', 'Hand.'])
        head_match = bone.name in ['FK-Head', 'FK-Head_Hinge', 'ORG-Head_Hinge',
                                  'ROOT-Head', 'PRP-Head', 'PRP-Properties', 'root']
        if (token_match or arm_match or head_match) and not bone.name.startswith('CTR-'):
            selected.add(bone.name)
            parent = bone.parent
            while parent:
                selected.add(parent.name)
                parent = parent.parent
    bones = []
    for name in sorted(selected):
        bone = rig.pose.bones[name]
        matrix = rig.matrix_world @ bone.matrix
        bones.append({
            'name': name, 'parent': bone.parent.name if bone.parent else None,
            'head_world': list(rig.matrix_world @ bone.head),
            'tail_world': list(rig.matrix_world @ bone.tail),
            'world_axes_xyz': [list(matrix.to_3x3().col[index].normalized())
                               for index in range(3)],
            'rest_length_m': bone.bone.length, 'pose_length_m': bone.length,
            'matrix_basis': [list(row) for row in bone.matrix_basis],
            'rotation_mode': bone.rotation_mode,
            'rotation_euler_deg': [value * 180.0 / 3.141592653589793
                                   for value in bone.rotation_euler],
            'location': list(bone.location),
            'lock_location': list(bone.lock_location),
            'lock_rotation': list(bone.lock_rotation),
            'lock_scale': list(bone.lock_scale),
            'ik_limits': {
                axis: {'locked': getattr(bone, 'lock_ik_' + axis),
                       'enabled': getattr(bone, 'use_ik_limit_' + axis),
                       'min': getattr(bone, 'ik_min_' + axis),
                       'max': getattr(bone, 'ik_max_' + axis)}
                for axis in ['x', 'y', 'z']},
            'custom_shape': bone.custom_shape.name if bone.custom_shape else None,
            'properties': {key: clean(bone[key]) for key in bone.keys()
                           if key not in ['rigify_parameters']},
            'constraints': [constraint_record(item) for item in bone.constraints],
        })
    drivers = []
    if rig.animation_data:
        for fcurve in rig.animation_data.drivers:
            if any('pose.bones["' + name + '"]' in fcurve.data_path for name in selected):
                drivers.append({'data_path': fcurve.data_path,
                                'expression': fcurve.driver.expression,
                                'muted': fcurve.mute,
                                'fcurve_valid': fcurve.is_valid,
                                'valid': fcurve.driver.is_valid,
                                'variables': [
                                    {'name': variable.name, 'type': variable.type,
                                     'targets': [{'id': target.id.name if target.id else None,
                                                  'path': target.data_path,
                                                  'bone': target.bone_target}
                                                 for target in variable.targets]}
                                    for variable in fcurve.driver.variables]})
    ui_data = clean(rig.data.get('ui_data', {}))
    report['files'].append({'path': str(path), 'sha256': before,
                            'sha256_after': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'bones': bones, 'drivers': drivers, 'ui_data': ui_data})
    assert report['files'][-1]['sha256_after'] == before
report['native_saves'] = 0
report['pose_edits'] = 0
report['renders'] = 0
(output / 'whole-rig-chain-readonly.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'status': 'READ_ONLY_COMPLETE', 'files': len(paths),
                  'bones': [len(item['bones']) for item in report['files']],
                  'pose_edits': 0, 'renders': 0, 'native_saves': 0}))
