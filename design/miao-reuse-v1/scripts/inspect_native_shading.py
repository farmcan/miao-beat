import bpy
import hashlib
import json
import pathlib
import sys

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
report = {'materials': [], 'node_groups': [], 'lighting_objects': [], 'character_properties': []}
for material in bpy.data.materials:
    entry = {'name': material.name, 'diffuse_color': list(material.diffuse_color), 'nodes': []}
    if material.node_tree:
        for node in material.node_tree.nodes:
            item = {'name': node.name, 'type': node.bl_idname}
            if node.type == 'GROUP':
                item['group'] = node.node_tree.name if node.node_tree else None
            entry['nodes'].append(item)
    report['materials'].append(entry)
for group in bpy.data.node_groups:
    entry = {'name': group.name, 'drivers': [], 'inputs': [], 'node_types': []}
    if hasattr(group, 'inputs'):
        sockets = group.inputs
    else:
        sockets = [item for item in group.interface.items_tree if item.item_type == 'SOCKET' and item.in_out == 'INPUT']
    for socket in sockets:
        item = {'name': socket.name, 'identifier': socket.identifier}
        if hasattr(socket, 'default_value'):
            value = socket.default_value
            item['default_value'] = list(value) if hasattr(value, '__iter__') and not isinstance(value, str) else value
        entry['inputs'].append(item)
    entry['node_types'] = sorted({node.bl_idname for node in group.nodes})
    if group.animation_data:
        for curve in group.animation_data.drivers:
            driver = curve.driver
            item = {'path': curve.data_path, 'index': curve.array_index, 'expression': driver.expression, 'variables': []}
            for variable in driver.variables:
                item['variables'].append({'name': variable.name, 'type': variable.type, 'targets': [{'id': target.id.name if target.id else None, 'data_path': target.data_path} for target in variable.targets]})
            entry['drivers'].append(item)
    report['node_groups'].append(entry)
for obj in bpy.data.objects:
    if obj.name.startswith('LGT'):
        report['lighting_objects'].append({'name': obj.name, 'properties': {key: repr(obj[key]) for key in obj.keys()}})
    if obj.name == 'RIG-Cat':
        for bone in obj.pose.bones:
            if 'Properties' in bone.name:
                report['character_properties'].append({'bone': bone.name, 'properties': {key: repr(bone[key]) for key in bone.keys()}})
output.write_text(json.dumps(report, indent=2))
print(json.dumps({'saved': str(output), 'materials': len(report['materials']), 'groups': len(report['node_groups'])}))
