"""Read-only native artist-control and material audit. No pose application/render/save."""
from pathlib import Path
import bpy
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color/keygroup-lift-color-native36.blend'
OUT=ROOT/'artifacts/identity-adaptation-2026-10-30'
EXPECTED='ca5f9095d31badc8c4e0266ba969ec127bf3e2f4a90b7f7e7c532d8bf4f5abb6'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def simple(v):
    if v is None or isinstance(v,(str,bool,int,float)):return v
    if isinstance(v,dict) or hasattr(v,'to_dict'):
        return {str(k):simple(value) for k,value in (v.to_dict() if hasattr(v,'to_dict') else v).items()}
    if hasattr(v,'to_list'):return v.to_list()
    try:return [simple(i) for i in v]
    except TypeError:return repr(v)

def props(owner):
    out={}
    for key in owner.keys():
        if key=='_RNA_UI':continue
        try:ui=owner.id_properties_ui(key).as_dict()
        except Exception:ui={}
        out[key]={'value':simple(owner[key]),'ui':simple(ui)}
    return out

def drivers(owner):
    a=getattr(owner,'animation_data',None)
    if not a:return []
    return [{'path':f.data_path,'index':f.array_index,'mute':f.mute,'valid':f.driver.is_valid,'expression':f.driver.expression,
      'variables':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'path':t.data_path,'bone':t.bone_target} for t in v.targets]} for v in f.driver.variables]} for f in a.drivers]

def tree(tree,depth=0):
    if not tree:return None
    rows=[]
    for n in tree.nodes:
        row={'name':n.name,'type':n.bl_idname,'label':n.label,'mute':n.mute,'inputs':[]}
        for sock in n.inputs:
            item={'name':sock.name,'identifier':sock.identifier,'linked':sock.is_linked}
            if hasattr(sock,'default_value'):item['default']=simple(sock.default_value)
            row['inputs'].append(item)
        if getattr(n,'image',None):row['image']=n.image.name
        if n.bl_idname=='ShaderNodeValToRGB':row['ramp']=[{'position':e.position,'color':list(e.color)} for e in n.color_ramp.elements]
        if n.bl_idname=='ShaderNodeGroup' and n.node_tree:
            row['group']=n.node_tree.name
            if depth<2:row['subtree']=tree_report(n.node_tree,depth+1)
        rows.append(row)
    return {'name':tree.name,'nodes':rows,'links':[{'from':[l.from_node.name,l.from_socket.name],'to':[l.to_node.name,l.to_socket.name],'valid':l.is_valid} for l in tree.links],'drivers':drivers(tree)}

tree_report=tree

def components(mesh):
    neighbors=[[] for _ in mesh.vertices]
    for edge in mesh.edges:
        a,b=edge.vertices;neighbors[a].append(b);neighbors[b].append(a)
    seen=set();rows=[]
    for start in range(len(neighbors)):
        if start in seen:continue
        stack=[start];seen.add(start);indices=[]
        while stack:
            i=stack.pop();indices.append(i)
            for j in neighbors[i]:
                if j not in seen:seen.add(j);stack.append(j)
        mins=[min(mesh.vertices[i].co[a] for i in indices) for a in range(3)]
        maxs=[max(mesh.vertices[i].co[a] for i in indices) for a in range(3)]
        rows.append({'vertices':len(indices),'boundsLocal':[mins,maxs]})
    return sorted(rows,key=lambda x:x['vertices'],reverse=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert sha(SOURCE)==EXPECTED
    bpy.context.preferences.filepaths.use_scripts_auto_execute=False
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    assert bpy.app.version[:2]==(3,6),bpy.app.version_string
    rig=bpy.data.objects['RIG-Cat'];frame=bpy.context.scene.frame_current
    pose=lambda:hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest()
    pose_before=pose();actions=len(bpy.data.actions)
    meshrows=[]
    for o in bpy.data.objects:
        if o.type not in {'MESH','CURVE'}:continue
        if o.name.startswith(('Ivory','Raised','Controller','Top ','SUPPORT','ENV-')):continue
        row={'name':o.name,'type':o.type,'inActiveScene':o.name in bpy.context.scene.objects,'hideRender':o.hide_render,'hideViewport':o.hide_viewport,'parent':o.parent.name if o.parent else None,'parentType':o.parent_type,'parentBone':o.parent_bone,'hideGet':o.hide_get(),'collections':[c.name for c in o.users_collection],'materialSlots':[m.name if m else None for m in o.data.materials],'drivers':drivers(o),'dataDrivers':drivers(o.data),'props':props(o),'modifiers':[]}
        for m in o.modifiers:
            mo={'name':m.name,'type':m.type,'showRender':m.show_render,'showViewport':m.show_viewport}
            if m.type=='MASK':mo.update(vertexGroup=m.vertex_group,invert=m.invert_vertex_group)
            if m.type=='ARMATURE':mo.update(object=m.object.name if m.object else None)
            if m.type=='NODES':mo.update(group=m.node_group.name if m.node_group else None,props=props(m))
            row['modifiers'].append(mo)
        if o.type=='MESH':
            counts={str(i):0 for i in range(len(o.data.materials))}
            for f in o.data.polygons:counts[str(f.material_index)]=counts.get(str(f.material_index),0)+1
            row.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),materialFaces=counts,vertexGroups=[g.name for g in o.vertex_groups],shapeKeys=[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [])
            if o.name in {'GEO-body','GEO-arms','GEO-legs','GEO-shoes','GEO-hands','GEO-head','GEO-tail'}:row['baseConnectedComponents']=components(o.data)
        meshrows.append(row)
    bones=[]
    tokens=('Eye','Pupil','Head','Goggle','Hat','Hair','Sealed','Mouth','Nose','Properties_','PRP-','Fur','Smile','Jacket','Cloth')
    for b in rig.pose.bones:
        if not (any(t.lower() in b.name.lower() for t in tokens) or b.keys()):continue
        bones.append({'name':b.name,'parent':b.parent.name if b.parent else None,'props':props(b),'location':list(b.location),'scale':list(b.scale),'rotationMode':b.rotation_mode,'rotationEuler':list(b.rotation_euler),'lockLocation':list(b.lock_location),'lockRotation':list(b.lock_rotation),'lockScale':list(b.lock_scale),'constraints':[{'name':c.name,'type':c.type,'mute':c.mute,'influence':c.influence,'target':c.target.name if hasattr(c,'target') and c.target else None,'subtarget':getattr(c,'subtarget',None)} for c in b.constraints]})
    material_names=sorted({m.name for o in bpy.data.objects if o.name in {r['name'] for r in meshrows} for m in getattr(o.data,'materials',[]) if m})
    report={'status':'READ_ONLY_NATIVE_IDENTITY_PROBE','blender':bpy.app.version_string,'source':str(SOURCE.relative_to(ROOT)),'sourceSha256Before':EXPECTED,'poseSha256Before':pose_before,'frame':frame,'rigProps':props(rig),'objects':meshrows,'bones':bones,'rigDrivers':drivers(rig),'materials':[{'name':name,'diffuseColor':list(bpy.data.materials[name].diffuse_color),'nodes':tree_report(bpy.data.materials[name].node_tree)} for name in material_names],'images':[{'name':im.name,'size':list(im.size),'filepath':im.filepath,'source':im.source,'packed':bool(im.packed_file),'colorSpace':im.colorspace_settings.name} for im in bpy.data.images],'actions':[{'name':a.name,'channels':len(a.fcurves),'range':list(a.frame_range)} for a in bpy.data.actions],'texts':[{'name':t.name,'useModule':t.use_module,'bytes':len(t.as_string())} for t in bpy.data.texts],'sourceSha256After':sha(SOURCE),'poseSha256After':pose(),'actionCountBefore':actions,'actionCountAfter':len(bpy.data.actions),'renders':0,'posesApplied':0,'frameSetCalls':0,'nativeSaves':0,'embeddedPythonExecuted':False}
    assert report['sourceSha256After']==EXPECTED and pose_before==report['poseSha256After']
    assert bpy.context.scene.frame_current==frame and actions==len(bpy.data.actions)
    (OUT/'native-identity-readonly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('RESULT '+json.dumps({'status':report['status'],'objects':len(meshrows),'materials':len(material_names),'bones':len(bones),'sourceUnchanged':True,'poseUnchanged':True,'renders':0,'saves':0}),flush=True)

main()
