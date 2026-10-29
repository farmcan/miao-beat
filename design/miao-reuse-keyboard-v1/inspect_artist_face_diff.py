"""Read source pose snapshots without applying actions or evaluating a frame."""
import bpy
import hashlib
import json
import pathlib
import re
import sys

args = sys.argv[sys.argv.index('--')+1:]
source = pathlib.Path(args[0]).resolve()
out = pathlib.Path(args[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
sha = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
rig = bpy.data.objects['RIG-Cat']


def snapshot(action):
    result = {}
    for curve in action.fcurves:
        keys = curve.keyframe_points
        assert len(keys)==1,(action.name,curve.data_path,len(keys))
        result[(curve.data_path,curve.array_index)] = {'value':float(keys[0].co.y),'frame':float(keys[0].co.x)}
    assert len(result)==len(action.fcurves)
    return result


base = snapshot(bpy.data.actions['default'])
smile = snapshot(bpy.data.actions['smile close'])
keys = set(base)|set(smile)
diffs = []
for path,index in sorted(keys):
    first = base.get((path,index))
    second = smile.get((path,index))
    if first==second:
        continue
    # Frame coordinates differ by definition; compare channel values only.
    if first is not None and second is not None and first['value']==second['value']:
        continue
    match = re.search(r'pose\.bones\["([^\"]+)"\]',path)
    name = match.group(1) if match else None
    bone = rig.pose.bones.get(name) if name else None
    ancestors = []
    parent = bone
    while parent:
        ancestors.append(parent.name)
        parent = parent.parent
    value_delta = None if first is None or second is None else second['value']-first['value']
    diffs.append({'data_path':path,'array_index':index,'default':first,'smile_close':second,
                  'value_delta':value_delta,'bone':name,'ancestor_chain':ancestors,
                  'constraints':[{'name':c.name,'type':c.type} for c in bone.constraints] if bone else [],
                  'resolved_current_value':repr(rig.path_resolve(path)) if path else None})
report = {'source':str(source),'source_sha256_before':sha,'source_sha256_after':hashlib.sha256(source.read_bytes()).hexdigest(),
          'blender':bpy.app.version_string,'source_current_frame_unchanged':bpy.context.scene.frame_current,
          'actions': [{'name':a.name,'fcurves':len(a.fcurves),'frame_range':list(a.frame_range)} for a in bpy.data.actions],
          'default_channels':len(base),'smile_close_channels':len(smile),
          'missing_from_default':[{'path':p,'index':i} for p,i in set(smile)-set(base)],
          'missing_from_smile':[{'path':p,'index':i} for p,i in set(base)-set(smile)],
          'prp_head_context': [{'data_path':path,'array_index':index,'default':base.get((path,index)),'smile_close':smile.get((path,index)),'current':repr(rig.path_resolve(path))} for path,index in sorted(keys) if path.startswith('pose.bones["PRP-Head"]')],
          'exact_value_differences':diffs,'frame_set_calls':0,'action_applications':0,'new_actions':0,'new_keyframes':0,'renders':0,'native_saves':0,
          'upstream_scripts_executed':[]}
assert report['source_sha256_before']==report['source_sha256_after']
(out/'default-to-smile-close-diff.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'status':'READ_ONLY_DIFF_COMPLETE','difference_channels':len(diffs),'bones':sorted({d['bone'] or '<non-bone>' for d in diffs}),'changed_head_flags':[d for d in diffs if d['bone']=='PRP-Head']}),flush=True)
