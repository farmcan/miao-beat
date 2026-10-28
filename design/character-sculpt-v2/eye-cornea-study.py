"""A bounded eye-optics candidate: real closed clear cornea and linked area lights.
Keeps B-reviewed white/iris coordinates. No emission dots or output-image edits.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'artifacts/character-eye-cornea-v2';out.mkdir(exist_ok=True);src=root/'artifacts/character-eye-inset-v4/miao-eye-inset-static.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();records=[]
glass=bpy.data.materials.new('C7 / clear thin cornea');glass.use_nodes=True;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(1,1,1,1);bs.inputs['Roughness'].default_value=.035;bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.38
iris_material=bpy.data.materials['C6 / attached navy iris'];ib=iris_material.node_tree.nodes.get('Principled BSDF');ib.inputs['Coat Weight'].default_value=0;ib.inputs['Roughness'].default_value=.30;ib.inputs['Specular IOR Level'].default_value=0
for side in ['L','R']:
 ir=bpy.data.objects['C6 / iris '+side];white=bpy.data.objects['C6 / sclera '+side];iv=ir.matrix_world.inverted();direction=(iv.to_3x3()@Vector((0,1,0))).normalized();bvh=BVHTree.FromObject(ir,dg);center=ir.data.vertices[0].co;ex,ez=center.x,center.z;rx=.055 if side=='L' else .048;rz=.066;rx*=.99;rz*=.99;cache={}
 def base(x,z):
  k=(round(float(x),8),round(float(z),8))
  if k not in cache:
   hit=bvh.ray_cast(iv@Vector((float(x),-3,float(z))),direction,20)[0]
   if hit is None:raise RuntimeError('Cornea outside actual iris '+str(k))
   cache[k]=float((ir.matrix_world@hit).y)
  return cache[k]
 def front(x,z):
  q=((x-ex)/rx)**2+((z-ez)/rz)**2
  return base(x,z)-.00025-.010*max(0,1-q)**.65
 N=96;R=24;vs=[];fs=[]
 for back in [False,True]:
  vs.append((ex,base(ex,ez)-.00010 if back else front(ex,ez),ez))
  for j in range(1,R+1):
   r=j/R
   for k in range(N):
    t=2*math.pi*k/N;x=ex+rx*r*math.cos(t);z=ez+rz*r*math.sin(t);vs.append((x,base(x,z)-.00010 if back else front(x,z),z))
 layer=1+N*R
 for back in [False,True]:
  off=layer if back else 0
  for k in range(N):
   f=(off,off+1+k,off+1+(k+1)%N);fs.append(f[::-1] if back else f)
  for j in range(R-1):
   for k in range(N):
    u=off+1+j*N+k;v=off+1+j*N+(k+1)%N;f=(u,u+N,v+N,v);fs.append(f[::-1] if back else f)
 for k in range(N):u=1+(R-1)*N+k;v=1+(R-1)*N+(k+1)%N;fs.append((u,u+layer,v+layer,v))
 me=bpy.data.meshes.new('Cornea '+side);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('C7 / clear cornea '+side,me);s.collection.objects.link(ob);me.materials.append(glass);ob.visible_shadow=False
 for p in me.polygons:p.use_smooth=True
 bm=bmesh.new();bm.from_mesh(me);volume=bm.calc_volume(signed=True);boundary=sum(e.is_boundary for e in bm.edges);bm.free();assert volume>0 and boundary==0;assert max(p.normal.y for p in me.polygons[:2304])<0
 # Real reflection geometry: aim a small area source along the reflected camera
 # vector of the actual corneal sample, restricted to this optical surface pair.
 tx=ex-.18*rx;tz=ez+.32*rz;ty=front(tx,tz);eps=.00002;dx=(front(tx+eps,tz)-front(tx-eps,tz))/(2*eps);dz=(front(tx,tz+eps)-front(tx,tz-eps))/(2*eps);normal=Vector((dx,-1,dz)).normalized();pt=Vector((tx,ty,tz));view=(s.camera.location-pt).normalized();light_dir=(2*normal.dot(view)*normal-view).normalized()
 bpy.ops.object.light_add(type='AREA',location=pt+light_dir*3);light=bpy.context.object;light.name='C7 / optical area '+side;light.data.energy=25;light.data.shape='DISK';light.data.size=.28;light.data.diffuse_factor=0;light.data.specular_factor=1;light.rotation_euler=(pt-light.location).to_track_quat('-Z','Y').to_euler();receivers=bpy.data.collections.new('C7 optical receivers '+side);s.collection.children.link(receivers);receivers.objects.link(ob);receivers.objects.link(ir);light.light_linking.receiver_collection=receivers
 # Keep the iris colored; its blue ring is physical mesh color, not a photograph.
 colors=ir.data.color_attributes['C6IrisTone'].data;arr=np.empty(len(colors)*4,np.float32);colors.foreach_get('color',arr);arr=arr.reshape(-1,4);arr[:,:3]*=np.array([1.2,1.35,1.45],np.float32);colors.foreach_set('color',arr.ravel())
 records.append({'side':side,'cornea_max_added_depth':.01025,'IOR':1.38,'closed_signed_volume':volume,'boundary_edges':boundary,'linked_area_energy':25,'linked_area_size':.28,'linked_to':[ob.name,ir.name],'no_eye_emission':True,'cornea_shadow_ray_approximation':True,'iris_diffuse_tissue_specular_level':0,'source_position':list(light.location),'target':list(pt)})
# Separate the diffuse iris from the clear specular layer. Broad studio lights
# keep lighting the character/iris, while two real linked optical cards reflect
# in the clear caps. Shadow visibility off approximates the thin clear interface,
# avoiding a caustic-only dark iris; camera and glossy visibility stay enabled.
receivers=bpy.data.collections.new('C7 original studio receivers');s.collection.children.link(receivers)
for o in list(s.objects):
 if o.type in {'MESH','CURVE','CURVES'} and not o.hide_render and not o.name.startswith('C7 / clear cornea'):receivers.objects.link(o)
for o in s.objects:
 if o.type=='LIGHT' and not o.name.startswith('C7 / optical area'):o.light_linking.receiver_collection=receivers

s.render.resolution_x=s.render.resolution_y=1024;s.cycles.samples=64;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.cycles.transparent_max_bounces=12;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-eye-cornea-static.blend'),compress=True)
# An authoring crop tests optics cheaply. It is not whole-frame delivery evidence.
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.35;s.render.border_max_x=.63;s.render.border_min_y=.70;s.render.border_max_y=.90;s.render.filepath=str(out/'optics-authoring-crop.png');bpy.ops.render.render(write_still=True);s.render.use_border=False;s.render.use_crop_to_border=False
# Neutral whole-frame geometry packet; preserve the uncolored transparent cornea.
def gray(name,value):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(value,value,value,1);b.inputs['Roughness'].default_value=.65;return m
mats={k:gray('C7 gray '+k,v) for k,v in [('body',.4),('white',.72),('dark',.045),('wood',.30),('metal',.6)]}
for ob in s.objects:
 if ob.type not in {'MESH','CURVE','CURVES'} or ob.hide_render or ob.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear cornea')):continue
 key='white' if ob.name.startswith('C6 / sclera') else 'dark' if ob.name.startswith('C6 / iris') or ob.name.startswith('Face /') else 'wood' if ob.name.startswith('Guitar /') else 'body';ob.data.materials.clear();ob.data.materials.append(mats[key])
s.cycles.samples=32;s.render.filepath=str(out/'gray-front.png');bpy.ops.render.render(write_still=True);camera=s.camera;camera.location=(6,-9,3.9);camera.rotation_euler=(Vector((.18,0,1.72))-camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'gray-three-quarter.png');bpy.ops.render.render(write_still=True)
(out/'receipt.json').write_text(json.dumps({'stage':'C7-cornea-optics-gray-unreviewed','input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'optics':records,'limits':['Authoring crop is not final full-frame art acceptance.','Both gray and color independent reviews remain required.','New corneal envelope requires new physical eyelid closure tests.','No animation, web or delivery acceptance.']},indent=2)+'\n')
