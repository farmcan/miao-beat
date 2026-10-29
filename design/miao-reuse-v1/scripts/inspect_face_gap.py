"""Read only known face drivers and camera binding; no new pose/render experiment."""
import json
import pathlib
import sys

import bpy

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['RIG-Cat']
bpy.context.view_layer.update()
report = {
    'source': str(source),
    'mouth_flag': bool(rig.pose.bones['PRP-Head']['Sealed Mouth']),
    'head_basis': [list(row) for row in rig.pose.bones['FK-Head'].matrix_basis],
    'pupil_basis': {side: [list(row) for row in rig.pose.bones[f'Eye_Pupil.{side}'].matrix_basis] for side in ['L', 'R']},
    'mouth_related_drivers': [],
    'face_objects': [],
    'camera_diagnostic': {},
}
containers = list(bpy.data.objects) + list(bpy.data.meshes) + list(bpy.data.shape_keys) + list(bpy.data.node_groups) + list(bpy.data.materials)
for container in containers:
    animation = container.animation_data
    if not animation:
        continue
    for curve in animation.drivers:
        driver = curve.driver
        variables = []
        is_related = False
        for variable in driver.variables:
            for target in variable.targets:
                if 'Sealed Mouth' in target.data_path:
                    is_related = True
                variables.append({'variable': variable.name, 'id': target.id.name if target.id else None, 'path': target.data_path})
        if is_related:
            report['mouth_related_drivers'].append({'owner': container.name, 'path': curve.data_path, 'expression': driver.expression, 'valid': driver.is_valid, 'simple': driver.is_simple_expression, 'variables': variables})
for name in ['GEO-head', 'GEO-eye_boolean.L', 'GEO-eye_boolean.R', 'CAT-eye_white.L', 'CAT-eye_white.R', 'CAT-eyes_highlight.L', 'CAT-eyes_highlight2.L', 'CAT-eyes_highlight3.L']:
    obj = bpy.data.objects[name]
    report['face_objects'].append({'name': name, 'parent': obj.parent.name if obj.parent else None, 'parent_bone': obj.parent_bone, 'hide_render': obj.hide_render, 'visible': obj.visible_get(), 'modifiers': [{'name': modifier.name, 'type': modifier.type, 'show_render': modifier.show_render, 'show_viewport': modifier.show_viewport, 'object': modifier.object.name if hasattr(modifier, 'object') and modifier.object else None} for modifier in obj.modifiers]})
helper = bpy.data.objects['HLP-scene_camera_dummy']
report['camera_diagnostic'] = {
    'helper_rotation_mode': helper.rotation_mode,
    'helper_euler': list(helper.rotation_euler),
    'camera_euler': list(scene.camera.rotation_euler),
    'helper_parent': helper.parent.name if helper.parent else None,
    'world_quaternion_difference_angle': helper.matrix_world.to_quaternion().rotation_difference(scene.camera.matrix_world.to_quaternion()).angle,
    'drivers': [{'path': curve.data_path, 'index': curve.array_index, 'expression': curve.driver.expression, 'valid': curve.driver.is_valid, 'simple': curve.driver.is_simple_expression} for curve in helper.animation_data.drivers],
}
output.write_text(json.dumps(report, indent=2))
print(json.dumps({'mouth_flag': report['mouth_flag'], 'mouth_related_drivers': report['mouth_related_drivers'], 'camera': report['camera_diagnostic']}))
