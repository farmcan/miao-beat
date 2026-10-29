import bpy
import json
import pathlib
import sys

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
rig = bpy.data.objects['RIG-Cat']
report = {'rig_matrix_world': [list(row) for row in rig.matrix_world], 'bones': []}
for bone in rig.pose.bones:
    is_control = not bone.name.startswith(('DEF-', 'ORG-', 'STR-', 'MCH-', 'P-IK-', 'IK-STR-'))
    is_relevant = any(token in bone.name for token in ('Arm', 'Hand', 'Elbow', 'Finger', 'Thumb', 'Index', 'Middle', 'Pinky', 'Eye', 'Head', 'Mouth', 'Lips', 'Shoulder', 'Properties', 'PRP-', 'Torso', 'Spine'))
    if not (is_control and is_relevant):
        continue
    report['bones'].append({
        'name': bone.name,
        'parent': bone.parent.name if bone.parent else None,
        'head_world': list(rig.matrix_world @ bone.head),
        'tail_world': list(rig.matrix_world @ bone.tail),
        'location': list(bone.location),
        'rotation_mode': bone.rotation_mode,
        'rotation_euler': list(bone.rotation_euler),
        'matrix': [list(row) for row in bone.matrix],
        'properties': {key: repr(bone[key]) for key in bone.keys()},
        'constraints': [{'name': con.name, 'type': con.type, 'target': con.target.name if hasattr(con, 'target') and con.target else None, 'subtarget': con.subtarget if hasattr(con, 'subtarget') else None, 'influence': con.influence} for con in bone.constraints],
    })
output.write_text(json.dumps(report, indent=2))
for bone in report['bones']:
    if bone['properties'] or bone['name'].startswith(('IK-MSTR-Hand', 'IK-Hand', 'FK-UpperArm', 'FK-Forearm', 'FK-Hand', 'FK-Thumb', 'FK-Index', 'FK-Middle', 'FK-Pinky', 'Eyes', 'Eye', 'Head', 'Lips')):
        print(json.dumps(bone))
