import ast
import hashlib
import json
import pathlib
import sys

import bpy

arguments = sys.argv[sys.argv.index('--') + 1:]
source = pathlib.Path(arguments[0]).resolve()
output = pathlib.Path(arguments[1]).resolve()
output.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
result = {
    'source': str(source),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'blender_version': bpy.app.version_string,
    'scripts_auto_execute': bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'texts': [],
    'non_simple_drivers': [],
}
for text in bpy.data.texts:
    content = text.as_string()
    destination = output / text.name
    destination.write_text(content)
    item = {
        'name': text.name,
        'sha256': hashlib.sha256(content.encode()).hexdigest(),
        'module': text.use_module,
        'lines': len(content.splitlines()),
    }
    if text.name.endswith('.py'):
        tree = ast.parse(content)
        item['imports'] = []
        item['calls'] = []
        item['functions'] = []
        item['classes'] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                item['imports'].append({'line': node.lineno, 'code': ast.get_source_segment(content, node)})
            elif isinstance(node, ast.Call):
                function = ast.get_source_segment(content, node.func)
                item['calls'].append({'line': node.lineno, 'function': function})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                item['functions'].append({'line': node.lineno, 'name': node.name})
            elif isinstance(node, ast.ClassDef):
                item['classes'].append({'line': node.lineno, 'name': node.name})
    result['texts'].append(item)
for container in list(bpy.data.objects) + list(bpy.data.node_groups) + list(bpy.data.materials) + list(bpy.data.shape_keys):
    animation = container.animation_data
    if not animation:
        continue
    for curve in animation.drivers:
        if curve.driver.type == 'SCRIPTED' and not curve.driver.is_simple_expression:
            result['non_simple_drivers'].append({
                'id': container.name,
                'path': curve.data_path,
                'expression': curve.driver.expression,
            })
(output / 'static-extraction.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'output': str(output), 'texts': len(result['texts']), 'non_simple_drivers': len(result['non_simple_drivers'])}))
