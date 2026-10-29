"""Read-only CC0 support prop audit/render, then frozen cat subdivision/floor audit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];S=R/'artifacts/licensed-keyboard-support-2026-10-30/communal-work-table.glb';O=R/'artifacts/miao-reuse-keyboard-v1/support-prop';N=R/'artifacts/miao-reuse-keyboard-v1/gray-static/keyboard-gray-native36.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p) for p in [S,N]};assert bpy.app.version[:2]==(3,6)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(S));sc=bpy.context.scene;rows=[];allp=[]
def geom(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];result=(p,len(m.vertices),len(m.loop_triangles));ev.to_mesh_clear();return result
def bb(p):return {'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]}
for o in sc.objects:
 if o.type!='MESH':continue
 p,v,t=geom(o);allp+=p;rows.append({'name':o.name,'bbox':bb(p),'vertices':v,'tris':t,'materials':[m.name for m in o.data.materials]})
bounds=bb(allp);center=Vector([(bounds['min'][i]+bounds['max'][i])/2 for i in range(3)]);bounds['size']=[bounds['max'][i]-bounds['min'][i] for i in range(3)]
w=bpy.data.worlds.new('TABLE-INSPECT-WORLD');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.15,.18,.21,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;sc.world=w
for name,loc,pow,size in [('Key',(-2,-3,4),700,3),('Fill',(3,-1,2),400,3),('Rim',(0,2,3),600,2)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=pow;d.size=size;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('TABLE-INSPECT-CAMERA');c=bpy.data.objects.new(d.name,d);sc.collection.objects.link(c);sc.camera=c;c.location=(3,-4,2.8);c.rotation_euler=(center-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=3.45;sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=96;sc.eevee.use_gtao=True;sc.eevee.gtao_distance=.08;sc.eevee.gtao_factor=1.0;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(O/'table-author-materials.png');
if not (O/'table-author-materials.png').exists():bpy.ops.render.render(write_still=True)
table={'source':str(S),'sha256':before[str(S)],'blender':bpy.app.version_string,'bbox':bounds,'objects':rows,'meshes':len(rows),'triangles':sum(r['tris'] for r in rows),'materials':[{'name':m.name,'nodes':[n.bl_idname for n in m.node_tree.nodes]} for m in bpy.data.materials if m.users and m.use_nodes],'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.type=='IMAGE'],'geometry_modified':False,'materials_modified':False,'license':'Innerscene whole-file CC0 from embedded asset copyright; original4PBR/6images; no external URI'}
(O/'table-import-receipt.json').write_text(json.dumps(table,indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(N),load_ui=False,use_scripts=False);bpy.context.view_layer.update();rig=bpy.data.objects['RIG-Cat'];sc=bpy.context.scene;visible=[];subs=[]
for o in sc.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get() or o.name.startswith('WGT'):continue
 if not o.name.startswith(('GEO-','REUSE-')):continue
 p,v,t=geom(o)
 if not p:continue
 visible.append({'name':o.name,'bbox':bb(p),'vertices_viewport':v,'tris_viewport':t})
 for m in o.modifiers:
  if m.type=='SUBSURF':
   drivers=[]
   for f in o.animation_data.drivers if o.animation_data else []:
    if m.name in f.data_path:drivers.append({'path':f.data_path,'expression':f.driver.expression,'muted':f.mute,'variables':[{'name':v.name,'type':v.type,'paths':[t.data_path for t in v.targets]} for v in f.driver.variables]})
   subs.append({'object':o.name,'modifier':m.name,'levels':m.levels,'render_levels':m.render_levels,'show_viewport':m.show_viewport,'show_render':m.show_render,'drivers':drivers})
catmin=min(r['bbox']['min'][2] for r in visible);lowest=[r for r in visible if r['bbox']['min'][2]<catmin+.005];quality={k:repr(v) for k,v in rig.pose.bones['Properties_Character_Cat'].items()};pose=hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest()
audit={'source_native':str(N),'native_sha256':before[str(N)],'pose_sha256':pose,'quality_properties':quality,'visible_cat_meshes':visible,'floor_z_viewport_m':catmin,'lowest_objects':lowest,'subsurf':subs,'viewport_depsgraph_mode':bpy.context.evaluated_depsgraph_get().mode,'source_render_geometry_equivalence':'see levels/render_levels; explicit render-level evaluated read-only comparison next; do not assume VIEWPORT equals RENDER'}
(O/'frozen-cat-settings-audit.json').write_text(json.dumps(audit,indent=2)+'\n');assert before=={str(p):sha(p) for p in [S,N]};print('TABLE_PROP_AND_CAT_SETTINGS',json.dumps({'table_bbox':bounds,'table_tris':table['triangles'],'floor':catmin,'lowest':[x['name'] for x in lowest],'subsurf':subs,'quality':quality}))
