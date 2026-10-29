"""Read-only sequential reopen of immutable gray and derived color native."""
import bpy,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'artifacts/miao-reuse-keyboard-v1/v2-keygroup-lift-color';r=json.loads((O/'default-color-receipt.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);bpy.context.view_layer.update();sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];h=hashlib.sha256()
 for o in sorted((o for o in sc.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());h.update(array.array('f',[c for v in o.data.vertices for c in v.co]).tobytes());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([m.name if m else None for m in o.data.materials]).encode())
 materials=[]
 for m in sorted(bpy.data.materials,key=lambda m:m.name):
  if m.use_nodes:
   ns=[]
   for n in m.node_tree.nodes:
    values=[]
    for s in n.inputs:
     if hasattr(s,'default_value'):
      v=s.default_value
      if not isinstance(v,(str,bool,int,float)):
       try:v=list(v)
       except TypeError:v=getattr(v,'name',None)
      values.append((s.identifier,v))
    ns.append((n.name,n.bl_idname,values))
   materials.append((m.name,ns,[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]))
 world={o.name:[list(v) for v in o.matrix_world] for o in sc.objects if o.name not in {sc.camera.name,'HLP-scene_camera_dummy'}}
 return {'pose_sha256':hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest(),'mesh_material_slots_hash':h.hexdigest(),'material_graph_and_input_values_hash':hashlib.sha256(json.dumps(materials).encode()).hexdigest(),'world_matrices_sha256':hashlib.sha256(json.dumps(world,sort_keys=True).encode()).hexdigest(),'Quality':rig.pose.bones['Properties_Character_Cat']['Quality'],'render_use_simplify':sc.render.use_simplify,'subsurf':[(o.name,m.name,m.levels,m.render_levels,m.show_render) for o in sorted(sc.objects,key=lambda o:o.name) for m in o.modifiers if m.type=='SUBSURF'],'actions_total':len(bpy.data.actions),'keys_count':len([o for o in sc.objects if o.type=='MESH' and o.name.startswith(('Ivory piano key','Raised black piano key'))])}
source=snapshot(r['source']);derived=snapshot(r['native']);links=[(l.from_node.bl_idname,l.to_node.bl_idname) for l in bpy.context.scene.node_tree.links];checks={'all_snapshot_invariants_equal':source==derived,'pose_fixed':derived['pose_sha256']==r['pose_sha256'],'mesh_fixed':derived['mesh_material_slots_hash']==r['all_mesh_material_slot_hash_before'],'native_sha_matches_receipt':sha(r['native'])==r['native_sha256'],'source_gray_sha_unchanged':sha(r['source'])==r['source_sha256_before'],'original_material_color_connected':('CompositorNodeRLayers','CompositorNodeComposite') in links,'actions27_keys68_quality1_render2':derived['actions_total']==27 and derived['keys_count']==68 and derived['Quality']==1 and not derived['render_use_simplify']};result={'status':'PASS' if all(checks.values()) else 'FAIL','blender':bpy.app.version_string,'checks':checks,'source':source,'derived':derived,'compositor_links':links,'native_sha256':sha(r['native']),'source_sha256_after':sha(r['source']),'new_actions':0};(O/'native-reopen-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('COLOR_NATIVE_REOPEN',json.dumps(result));assert all(checks.values())
