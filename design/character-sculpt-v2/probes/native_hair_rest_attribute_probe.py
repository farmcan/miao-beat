import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
# Isolated diagnostic only: never loads or modifies the Miao asset.
out=Path(__file__).resolve().parents[3]/'artifacts/native-groom-binding-research'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
me=bpy.data.meshes.new('ProbeSurface');me.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)]);me.update();surface=bpy.data.objects.new('ProbeSurface',me);bpy.context.scene.collection.objects.link(surface)
uv=me.uv_layers.new(name='BindUV')
for d,p in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):d.uv=p
surface.add_rest_position_attribute=True
hc=bpy.data.hair_curves.new('ProbeHair');hc.add_curves([4,4]);roots=[(.25,.25,0),(.75,.75,0)];pos=[(x,y,.005+.03*i) for x,y,z in roots for i in range(4)];hc.position_data.foreach_set('vector',[a for p in pos for a in p]);hair=bpy.data.objects.new('ProbeHair',hc);bpy.context.scene.collection.objects.link(hair);hc.surface=surface;hc.surface_uv_map='BindUV'
rest_attr=hc.attributes.new('miao_rest_position','FLOAT_VECTOR','POINT');rest_attr.data.foreach_set('vector',[x for p in pos for x in p])
bpy.ops.object.select_all(action='DESELECT');hair.select_set(True);bpy.context.view_layer.objects.active=hair
snap_result=bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')
attr=hc.attributes.get('surface_uv_coordinate')
print('SNAP_DEBUG',snap_result,[(a.name,a.data_type,a.domain) for a in hc.attributes])
ng=bpy.data.node_groups.new('Probe Official Surface Deform','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');ni=ng.nodes.new('NodeGroupInput');no=ng.nodes.new('NodeGroupOutput');dn=ng.nodes.new('GeometryNodeDeformCurvesOnSurface');ng.links.new(ni.outputs['Geometry'],dn.inputs['Curves']);ng.links.new(dn.outputs['Curves'],no.inputs['Geometry']);mod=hair.modifiers.new('Official Deform','NODES');mod.node_group=ng
base=surface.shape_key_add(name='Basis');key=surface.shape_key_add(name='RigidProbe');R=Matrix.Rotation(math.radians(25),4,'Y');T=Vector((.13,-.07,.20))
for d,v in zip(key.data,me.vertices):d.co=R@v.co+T
key.value=1
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=hair.evaluated_get(dg);got=[Vector(d.vector) for d in ev.data.position_data];expected=[R@(Vector(p)-Vector((0,0,.005)))+T for p in pos];errors=[(a-b).length for a,b in zip(got,expected)]
rest_got=[Vector(d.vector) for d in ev.data.attributes['miao_rest_position'].data];rest_err=max((a-Vector(b)).length for a,b in zip(rest_got,pos))
report={'blender':bpy.app.version_string,'node':dn.bl_idname,'snap_operator_result':list(snap_result),'attachment_uvs':[list(d.vector) for d in attr.data],'hair_surface':hc.surface.name,'surface_uv_map':hc.surface_uv_map,'root_attribute':{'name':attr.name,'data_type':attr.data_type,'domain':attr.domain,'count':len(attr.data)},'add_rest_position_attribute':surface.add_rest_position_attribute,'evaluated_surface_attributes':[(a.name,a.data_type,a.domain) for a in surface.evaluated_get(dg).data.attributes],'input_points':pos,'evaluated_points':[list(p) for p in got],'expected_points':[list(p) for p in expected],'max_position_error':max(errors),'curve_count':len(ev.data.curves),'point_count':len(ev.data.points),'custom_rest_attribute_max_error':rest_err,'custom_rest_attribute_preserved':rest_err<1e-7,'pass':max(errors)<1e-5 and rest_err<1e-7,'operator_props':{}}
for name in ['surface_set','snap_curves_to_surface']:
 op=getattr(bpy.ops.curves,name).get_rna_type();report['operator_props'][name]=[{ 'id':p.identifier,'type':p.type,'description':p.description,'enums':[x.identifier for x in p.enum_items] if p.type=='ENUM' else None} for p in op.properties]
(out/'minimal-rest-attribute-result.json').write_text(json.dumps(report,indent=2));print('PROBE_RESULT',json.dumps({'pass':report['pass'],'max_error':max(errors),'custom_rest_error':rest_err,'attributes':report['evaluated_surface_attributes'],'operators':report['operator_props']}))
