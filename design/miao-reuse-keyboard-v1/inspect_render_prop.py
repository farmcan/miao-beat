"""Author-supported 3.6 import of immutable CC0 KeyForty, audit and native prop inspection."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];S=R/'artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/piano-midi-keyboard.glb';O=R/'artifacts/miao-reuse-keyboard-v1/prop';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S)
assert bpy.app.version[:2]==(3,6)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(S));sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[];allpoints=[]
for o in sc.objects:
 if o.type!='MESH':continue
 e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();p=[o.matrix_world@v.co for v in m.vertices];allpoints+=p
 lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 rows.append({'name':o.name,'bbox':{'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]},'matrix':[list(v) for v in o.matrix_world],'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'materials':[x.name for x in m.materials],'negative_scale':o.matrix_world.determinant()<0});e.to_mesh_clear()
lo=Vector([min(v[i] for v in allpoints) for i in range(3)]);hi=Vector([max(v[i] for v in allpoints) for i in range(3)]);center=(lo+hi)/2
w=bpy.data.worlds.new('KEYFORTY-INSPECTION-WORLD');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.23,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;sc.world=w
for name,loc,power,size in [('Key',(-.6,-.7,1.1),95,1),('Fill',(.7,-.1,.6),65,1),('Rim',(0,.8,.8),110,.7)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;d.shape='DISK';o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('KEYFORTY-INSPECTION-CAMERA');c=bpy.data.objects.new(d.name,d);sc.collection.objects.link(c);sc.camera=c;d.type='ORTHO';sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=96;sc.eevee.use_gtao=True;sc.eevee.gtao_distance=.04;sc.eevee.gtao_factor=1.1;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Filmic';sc.view_settings.look='Medium High Contrast'
for name,loc,target,scale,res in [('prop-three-quarter',(.55,-.65,.65),center,.84,(1500,900)),('prop-keys',(0,-.35,.55),Vector((0,-.02,.025)),.32,(1400,1000))]:
 c.location=loc;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'keyforty-import-native36.blend'))
receipt={'source':str(S),'source_sha256_before':before,'source_sha256_after':sha(S),'blender':bpy.app.version_string,'axes':'Blender Z-up import; X keyboard width; Y depth; determine key front from geometry below','bbox':{'min':list(lo),'max':list(hi),'size':list(hi-lo)},'objects':rows,'white_keys':sum(x['name'].startswith('Ivory piano key') for x in rows),'black_keys':sum(x['name'].startswith('Raised black piano key') for x in rows),'triangles':sum(x['triangles'] for x in rows),'materials':[m.name for m in bpy.data.materials if m.users],'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.type=='IMAGE'],'animations':len(bpy.data.actions),'geometry_modified':False,'materials_modified':False,'source_geometry_material_license':'Innerscene complete asset CC0-1.0; archived LICENSE-EVIDENCE.txt','new_code_light_camera_license':'project MIT','craft_gate':'pending independent judgment','assembly':'not attempted'}
assert before==receipt['source_sha256_after'];assert receipt['white_keys']==40 and receipt['black_keys']==28 and receipt['animations']==0
(O/'prop-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['bbox','white_keys','black_keys','triangles','animations']}))
