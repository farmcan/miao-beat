"""CC0 evaluated geometry only; original local PBR. Never save the upstream file."""
import bpy, json, hashlib, math, sys
import numpy as np
from pathlib import Path
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'artifacts/thin-guitar-alternative-2026-10-30/hh-guitar-with-stand-original.blend'
OUT=ROOT/'artifacts/miao-reuse-v1/thin-electric-clean';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(SRC)
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
dg=bpy.context.evaluated_depsgraph_get()
body=bpy.data.objects['Body']; r=body.matrix_world.to_3x3().normalized()
# Source body X=width,Y=neckwards,Z=front; target +X,+Z,-Y.
target=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
canonical=(target@r.transposed()).to_4x4()
rows=[]; keep=[]; exclusions=[]
for o in list(bpy.context.scene.objects):
 if o.type not in {'MESH','CURVE'} or o.name in {'Stand','Killer'}:
  exclusions.append({'object':o.name,'type':o.type,'reason':'stand assembly including separate padded neck yoke' if o.name in {'Stand','Killer'} else 'text/logo or non-render geometry'});continue
 ev=o.evaluated_get(dg); m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
 if not len(m.polygons):
  exclusions.append({'object':o.name,'type':o.type,'reason':'zero-face construction guide'});bpy.data.meshes.remove(m);continue
 raw=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',raw)
 loops=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',loops)
 starts=np.empty(len(m.polygons),dtype=np.int32);m.polygons.foreach_get('loop_start',starts)
 mats=[x.name if x else '' for x in o.data.materials]
 row={'source_object':o.name,'source_type':o.type,'source_vertex_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'source_topology_sha256':hashlib.sha256(loops.tobytes()+starts.tobytes()).hexdigest(),'vertices':len(m.vertices),'faces':len(m.polygons),'source_material_slots':mats,'uv_layers':list(m.uv_layers.keys()),'world_matrix': [list(v) for v in o.matrix_world]}
 mat_indices=[p.material_index for p in m.polygons]
 m.materials.clear();m.name='Geometry_'+o.name.replace('/','_')
 transform=canonical@o.matrix_world;m.transform(transform)
 transformed=np.empty_like(raw);m.vertices.foreach_get('co',transformed)
 # Local evaluated-geometry comparison after inverse world+canonical transform.
 inverse=np.array(transform.inverted(),dtype=np.float64)
 back=np.c_[transformed.reshape(-1,3),np.ones(len(m.vertices))]@inverse.T
 row['max_inverse_local_vertex_error']=float(np.linalg.norm(back[:,:3]-raw.reshape(-1,3),axis=1).max())
 row['canonical_vertex_sha256']=hashlib.sha256(transformed.tobytes()).hexdigest()
 row['canonical_topology_sha256']=row['source_topology_sha256']
 keep.append((o.name,m,mats,mat_indices));rows.append(row)
# Pure new scene content; source datablocks are removed rather than orphaned into delivery.
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
keep_mesh={x[1] for x in keep}
for m in list(bpy.data.meshes):
 if m not in keep_mesh:bpy.data.meshes.remove(m)
for collection in (bpy.data.materials,bpy.data.images,bpy.data.textures,bpy.data.curves,bpy.data.fonts,bpy.data.texts,bpy.data.node_groups,bpy.data.actions,bpy.data.armatures,bpy.data.worlds):
 for x in list(collection):
  if hasattr(x,'is_builtin') and x.is_builtin:continue
  try:collection.remove(x,do_unlink=True)
  except TypeError:collection.remove(x)
# Original project-authored constant PBR only. No image textures or upstream groups.
PAL={
 'Miao_Blue':((.038,.20,.43,1),.18,.27),
 'Miao_BlueGray':((.043,.072,.115,1),.10,.32),
 'Miao_Fretboard':((.014,.020,.029,1),.0,.36),
 'Miao_Silver':((.55,.61,.68,1),1.,.23),
 'Miao_Charcoal':((.018,.022,.028,1),.0,.4),
 'Miao_Ivory':((.69,.73,.70,1),.0,.28)}
newmats={}
for name,(color,metal,rough) in PAL.items():
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear()
 p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if name=='Miao_Blue':p.inputs['Coat Weight'].default_value=.25;p.inputs['Coat Roughness'].default_value=.2
 out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);m.diffuse_color=color
 newmats[name]=m
mapping={'Car paint':'Miao_Blue','Back':'Miao_BlueGray','RIm':'Miao_BlueGray','Black Painted Wood':'Miao_Fretboard','Holes':'Miao_Charcoal','Black Plastic':'Miao_Charcoal','Rubber':'Miao_Charcoal','Rubber Black':'Miao_Charcoal','Sea Pearl':'Miao_Ivory','Simple Crystal':'Miao_Ivory'}
collection=bpy.context.scene.collection
for name,m,slots,indices in keep:
 obj=bpy.data.objects.new(name,m);collection.objects.link(obj)
 obj['upstream_geometry_object']=name
 for s in slots:m.materials.append(newmats[mapping.get(s,'Miao_Silver')])
 if not slots:m.materials.append(newmats['Miao_Silver'])
 for p,i in zip(m.polygons,indices):p.material_index=min(i,len(m.materials)-1)
# Common rigid translation sets lowest instrument point at Z=0, X bbox centre=0.
pts=np.concatenate([np.array([v.co[:] for v in m.vertices]) for _,m,_,_ in keep])
lo=pts.min(0);hi=pts.max(0);shift=Vector((-(lo[0]+hi[0])/2,0,-lo[2]))
for _,m,_,_ in keep:m.transform(Matrix.Translation(shift))
canonical=Matrix.Translation(shift)@canonical
lo+=np.array(shift);hi+=np.array(shift)
for row,(_,m,_,_) in zip(rows,keep):
 vv=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',vv);row['canonical_vertex_sha256']=hashlib.sha256(vv.tobytes()).hexdigest()
 m.calc_loop_triangles();row['triangles']=len(m.loop_triangles)
frets=json.loads((ROOT/'artifacts/thin-guitar-alternative-2026-10-30/body-string-material-measurement.json').read_text())
# Select only instrument geometry for standard glTF.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['Body']
glb=OUT/'thin-electric-clean.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_animations=False,export_cameras=False,export_lights=False,export_extras=False,export_draco_mesh_compression_enable=False)
# Original simple lighting and camera, for native inspection views only.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Miao_Studio_World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.16,.20,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.view_settings.view_transform='AgX'
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(-1.2,-1.6,1.7),350,1.2),('Fill',(1.0,-.8,.8),220,1.),('Rim',(.4,.9,1.4),450,1.)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);collection.objects.link(o);o.location=loc;aim(o,(0,0,.55))
d=bpy.data.cameras.new('Miao_Inspection_Camera');camera=bpy.data.objects.new(d.name,d);collection.objects.link(camera);scene.camera=camera;d.type='ORTHO'
views=[('full',(1.0,-3,1.12),(0,-.1,.56),1.30,(1100,1500)),('side',(3,-.30,.8),(0,-.1,.56),1.30,(900,1500)),('bridge',(.34,-1.7,.59),(0,-.12,.24),.48,(1400,1400))]
for name,loc,targetpoint,scale,res in views:
 camera.location=loc;aim(camera,targetpoint);d.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=res;scene.render.resolution_percentage=100
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
name,loc,targetpoint,scale,res=views[0];camera.location=loc;aim(camera,targetpoint);d.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=res
scene.render.filepath=str(OUT/'full.png')
# Cycles creates a transient Render Result image. Strip it too before native save.
for i in list(bpy.data.images):bpy.data.images.remove(i,do_unlink=True)
assert len(bpy.data.images)==0 and len(bpy.data.texts)==0 and len(bpy.data.node_groups)==0
assert all(m.name.startswith('Miao_') for m in bpy.data.materials)
native=OUT/'thin-electric-clean.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
receipt={'source':str(SRC),'source_sha256_before':source_sha,'source_sha256_after':sha(SRC),'blender':bpy.app.version_string,'geometry_license':'CC0 upstream; model only','new_materials_code':'project original, no upstream materials/images/nodes/texts','excluded':exclusions,'source_to_canonical_rigid_matrix':[list(x) for x in canonical],'axes':'metres; +Z neck; front -Y; +X body width; no resize/nonuniform deformation','world_bbox':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist()},'mesh_objects':len(keep),'triangles':sum(x['triangles'] for x in rows),'strings':['Spiral'+('.%03d'%i if i else '') for i in range(6)],'frets_source_measurement':frets,'source_mesh_fingerprints':rows,'materials':PAL,'stripped':{'images':len(bpy.data.images),'old_materials':0,'node_groups':len(bpy.data.node_groups),'texts':len(bpy.data.texts),'textures':len(bpy.data.textures),'stand':bpy.data.objects.get('Stand') is not None,'font_objects':sum(o.type=='FONT' for o in bpy.data.objects)},'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [native,glb]},'blender36_import':'pending actual import','assembly':'not attempted; awaiting independent prop craft review'}
assert receipt['source_sha256_before']==receipt['source_sha256_after']
(OUT/'clean-prop-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('CLEAN_PROP_COMPLETE',json.dumps({k:receipt[k] for k in ['mesh_objects','triangles','world_bbox','stripped','outputs']}))
