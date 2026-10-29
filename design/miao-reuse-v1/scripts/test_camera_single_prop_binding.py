"""Bounded Blender 3.6 camera-helper diagnostic; never save the input blend.

Run with --factory-startup --disable-autoexec --python-exit-code 1 -P this.py
-- SOURCE.blend OUTPUT_DIRECTORY. No frame changes, rendering or embedded scripts.
The reusable patch is deliberately restricted to an unparented XYZ camera/helper.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import time

import bpy


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pose_hash(rig):
    """Hash authored bone transforms, not camera-dependent evaluated deformation."""
    payload = [(bone.name, [list(row) for row in bone.matrix_basis])
               for bone in sorted(rig.pose.bones, key=lambda item: item.name)]
    return hashlib.sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()


def animation_inventory():
    return {
        'action_names': sorted(action.name for action in bpy.data.actions),
        'keyframe_points': sum(len(curve.keyframe_points)
                               for action in bpy.data.actions for curve in action.fcurves),
    }


def bind_camera_single_prop(scene, helper):
    """Patch only the three existing helper rotation drivers; caller must validate.

    SINGLE_PROP reads the actual scene.camera RNA property, unlike a TRANSFORMS
    variable's decomposed transform semantics. This function does not enable
    autoexec, execute embedded text, change the camera, or create animation.
    """
    camera = scene.camera
    assert camera is not None
    for obj in (camera, helper):
        assert obj.rotation_mode == 'XYZ', (obj.name, 'requires XYZ')
        assert obj.parent is None, (obj.name, 'requires no parent')
        assert not obj.constraints, (obj.name, 'constraints not covered')
        assert max(abs(value) for value in obj.delta_rotation_euler) == 0.0
    curves = sorted((curve for curve in helper.animation_data.drivers
                     if curve.data_path == 'rotation_euler'), key=lambda curve: curve.array_index)
    assert [curve.array_index for curve in curves] == [0, 1, 2]
    for curve in curves:
        curve.mute = True
        driver = curve.driver
        driver.type = 'SCRIPTED'
        while driver.variables:
            driver.variables.remove(driver.variables[0])
        variable = driver.variables.new()
        variable.name = 'var'
        variable.type = 'SINGLE_PROP'
        target = variable.targets[0]
        target.id_type = 'SCENE'
        target.id = scene
        target.data_path = 'camera.rotation_euler[%d]' % curve.array_index
        driver.expression = 'var'
        curve.mute = False
    helper.update_tag(refresh={'OBJECT'})
    scene.update_tag()
    bpy.context.view_layer.update()
    return curves


def main():
    arguments = sys.argv[sys.argv.index('--') + 1:]
    source, output = Path(arguments[0]).resolve(), Path(arguments[1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output / 'receipt.json'
    snapshot = output / 'input-snapshot.blend'
    working = output / 'camera-singleprop-working36.blend'
    assert source != snapshot and source != working
    source_sha = sha256(source)
    report = {'passed': False, 'source': str(source), 'source_sha256_before': source_sha,
              'snapshot': str(snapshot), 'rendered': False, 'frame_set_called': False,
              'embedded_source_scripts_executed': False,
              'scope': 'three existing camera-helper rotation drivers only'}
    started = time.monotonic()
    try:
        bpy.context.preferences.filepaths.use_scripts_auto_execute = False
        shutil.copy2(source, snapshot)
        report['snapshot_sha256'] = sha256(snapshot)
        assert report['snapshot_sha256'] == source_sha
        bpy.ops.wm.open_mainfile(filepath=str(snapshot), load_ui=False, use_scripts=False)
        assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
        assert bpy.app.version[:2] == (3, 6), bpy.app.version_string
        scene = bpy.context.scene
        camera = scene.camera
        helper = bpy.data.objects['HLP-scene_camera_dummy']
        rig = bpy.data.objects['RIG-Cat']
        original_rotation = camera.rotation_euler.copy()
        frame_before = scene.frame_current
        animation_before = animation_inventory()
        pose_before = pose_hash(rig)
        report.update(blender_version=bpy.app.version_string, scene_name=scene.name,
                      camera_name=camera.name, helper_name=helper.name,
                      camera_rotation_mode=camera.rotation_mode, helper_rotation_mode=helper.rotation_mode,
                      camera_parent=camera.parent.name if camera.parent else None,
                      helper_parent=helper.parent.name if helper.parent else None,
                      auto_execute_before=False, frame_before=frame_before,
                      pose_sha256_before=pose_before, animation_before=animation_before)
        original_curves = [curve for curve in helper.animation_data.drivers
                           if curve.data_path == 'rotation_euler']
        report['original_rotation_drivers_muted'] = [bool(curve.mute) for curve in original_curves]
        assert len(original_curves) == 3 and all(curve.mute for curve in original_curves)
        curves = bind_camera_single_prop(scene, helper)
        offsets = [('current', (0.0, 0.0, 0.0)),
                   ('offset_A', tuple(math.radians(value) for value in (8.0, -5.0, 11.0))),
                   ('offset_B', tuple(math.radians(value) for value in (-12.0, 7.0, -9.0)))]
        report['cases'] = []
        for name, offset in offsets:
            camera.rotation_euler = tuple(original_rotation[axis] + offset[axis] for axis in range(3))
            camera.update_tag(refresh={'OBJECT'})
            scene.update_tag()
            bpy.context.view_layer.update()
            expected = list(camera.matrix_world.to_euler('XYZ'))
            actual = list(helper.rotation_euler)
            evaluated = helper.evaluated_get(bpy.context.evaluated_depsgraph_get())
            evaluated_actual = list(evaluated.rotation_euler)
            errors = [abs(actual[axis] - expected[axis]) for axis in range(3)]
            evaluated_errors = [abs(evaluated_actual[axis] - expected[axis]) for axis in range(3)]
            case = {'name': name, 'assigned_camera_euler': list(camera.rotation_euler),
                    'camera_world_euler': expected, 'helper_euler': actual,
                    'evaluated_helper_euler': evaluated_actual, 'axis_errors_radians': errors,
                    'evaluated_axis_errors_radians': evaluated_errors,
                    'drivers_valid': [bool(curve.driver.is_valid) for curve in curves],
                    'drivers_simple': [bool(curve.driver.is_simple_expression) for curve in curves],
                    'auto_execute': bool(bpy.context.preferences.filepaths.use_scripts_auto_execute),
                    'rig_pose_unchanged': pose_hash(rig) == pose_before}
            report['cases'].append(case)
            case['numeric_pass'] = max(errors + evaluated_errors) < 1e-6
        camera.rotation_euler = original_rotation
        camera.update_tag(refresh={'OBJECT'})
        scene.update_tag()
        bpy.context.view_layer.update()
        report['restored_axis_errors_radians'] = [abs(helper.rotation_euler[i] - camera.matrix_world.to_euler('XYZ')[i]) for i in range(3)]
        report['driver_bindings'] = [
            {'axis': curve.array_index, 'expression': curve.driver.expression,
             'variable_type': curve.driver.variables[0].type,
             'id_type': curve.driver.variables[0].targets[0].id_type,
             'scene_id_is_actual': curve.driver.variables[0].targets[0].id == scene,
             'data_path': curve.driver.variables[0].targets[0].data_path}
            for curve in curves]
        report['pose_sha256_after'] = pose_hash(rig)
        report['animation_after'] = animation_inventory()
        report['frame_after'] = scene.frame_current
        report['auto_execute_after'] = bool(bpy.context.preferences.filepaths.use_scripts_auto_execute)
        assert report['pose_sha256_after'] == pose_before
        assert report['animation_after'] == animation_before
        assert scene.frame_current == frame_before
        assert max(report['restored_axis_errors_radians']) < 1e-6
        assert not report['auto_execute_after']
        report['numeric_binding_pass'] = all(case['numeric_pass'] for case in report['cases'])
        report['driver_flags_pass'] = all(all(case['drivers_valid']) and all(case['drivers_simple'])
                                          and not case['auto_execute'] for case in report['cases'])
        report['rig_pose_unchanged_all_cases'] = all(case['rig_pose_unchanged'] for case in report['cases'])
        assert report['numeric_binding_pass'], 'SINGLE_PROP did not follow changed camera properties; retain manual world-Euler bake'
        assert report['driver_flags_pass'] and report['rig_pose_unchanged_all_cases']
        bpy.ops.wm.save_as_mainfile(filepath=str(working), copy=True)
        report['working_copy'] = str(working)
        report['working_copy_sha256'] = sha256(working)
        report['passed'] = True
    except Exception as error:
        report['error'] = repr(error)
        raise
    finally:
        report['source_sha256_after'] = sha256(source)
        report['source_unchanged'] = report['source_sha256_after'] == source_sha
        report['elapsed_seconds'] = time.monotonic() - started
        receipt_path.write_text(json.dumps(report, indent=2) + '\n')
        print('RESULT ' + json.dumps(report, separators=(',', ':')))
        assert report['source_unchanged']


if __name__ == '__main__':
    main()
