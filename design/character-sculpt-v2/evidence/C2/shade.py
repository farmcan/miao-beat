"""Stage C only. Load accepted gray-stage candidate, author pigment/short plush.
Never an image projection: pigment map contains only hand-authored flat colors.
"""
import bpy,math,sys,json,random,time
from pathlib import Path
from mathutils import Vector
import numpy as np
root=Path(__file__).resolve().parents[2];out=(root/'artifacts/character-sculpt-v2-color-2');out.mkdir(parents=True,exist_ok=True);s=bpy.context.scene
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.cycles.samples=64;s.render.resolution_x=s.render.resolution_y=1024
s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,.96,.88,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.22
# Camera sees a cream world independently of ambient illumination.
wn=s.world.node_tree.nodes;wl=s.world.node_tree.links;env=wn['Background'];camera_bg=wn.new('ShaderNodeBackground');camera_bg.inputs[0].default_value=(.96,.945,.90,1);camera_bg.inputs[1].default_value=1;lp=wn.new('ShaderNodeLightPath');ws=wn.new('ShaderNodeMixShader');wl.new(lp.outputs['Is Camera Ray'],ws.inputs[0]);wl.new(env.outputs[0],ws.inputs[1]);wl.new(camera_bg.outputs[0],ws.inputs[2]);wl.new(ws.outputs[0],wn.get('World Output').inputs[0])
for ob in bpy.data.objects:
 if ob.type=='LIGHT':
  ob.data.energy=650 if 'key' in ob.name else 110;ob.data.size=3.5 if 'key' in ob.name else 4
# Reuse the project's editable procedural wood material, not its rejected cat art.
import ast
src=(root/'design/blender-guitar-v1/scene.py').read_text();tree=ast.parse(src);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='material');exec(compile(ast.Module(body=[fn],type_ignores=[]),'project-wood-material','exec'))
body=bpy.data.objects['Miao / continuous pear and rounded-square face'];coat=material('Miao / warm short plush',(.9,.25,.025),.68,fur=True)
n=coat.node_tree.nodes;l=coat.node_tree.links;b=n.get('Principled BSDF');b.inputs['Subsurface Weight'].default_value=.025;b.inputs['Sheen Weight'].default_value=.22
pos=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(pos.outputs['Position'],sep.inputs[0]);combine=n.new('ShaderNodeCombineXYZ')
def remap(socket,scale,add):
 m=n.new('ShaderNodeMath');m.operation='MULTIPLY_ADD';m.inputs[1].default_value=scale;m.inputs[2].default_value=add;l.new(socket,m.inputs[0]);return m.outputs[0]
l.new(remap(sep.outputs['X'],1/4.3,2/4.3),combine.inputs['X']);l.new(remap(sep.outputs['Z'],1/3.6,0),combine.inputs['Y']);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(root/'design/character-sculpt-v2/coat-pigment.png'));tex.image.pack();tex.extension='EXTEND';l.new(combine.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],b.inputs['Base Color'])
# The back is a designed continuation, not recovered unseen geometry/pattern.
# Pigment is cut off on the rear so the face/muzzle is never painted on the back.
back=n.new('ShaderNodeMath');back.operation='GREATER_THAN';back.inputs[1].default_value=.1;l.new(sep.outputs['Y'],back.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.90,.19,.018,1);l.new(back.outputs[0],mix.inputs[0]);l.new(tex.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color'])

arm=n.new('ShaderNodeMath');arm.operation='LESS_THAN';arm.inputs[1].default_value=-.85;l.new(sep.outputs['Y'],arm.inputs[0]);low=n.new('ShaderNodeMath');low.operation='LESS_THAN';low.inputs[1].default_value=2.55;l.new(sep.outputs['Z'],low.inputs[0]);armmask=n.new('ShaderNodeMath');armmask.operation='MULTIPLY';l.new(arm.outputs[0],armmask.inputs[0]);l.new(low.outputs[0],armmask.inputs[1]);orange_arm=n.new('ShaderNodeMixRGB');orange_arm.inputs[2].default_value=(.92,.24,.022,1);l.new(armmask.outputs[0],orange_arm.inputs[0]);l.new(mix.outputs[0],orange_arm.inputs[1]);l.new(orange_arm.outputs[0],b.inputs['Base Color'])
for node in n:
 if node.bl_idname=='ShaderNodeBump':node.inputs['Distance'].default_value=.0006;node.inputs['Strength'].default_value=.12
 if node.bl_idname=='ShaderNodeTexNoise':node.inputs['Scale'].default_value=700

body.data.materials.clear();body.data.materials.append(coat)
ivory=material('Eye / warm ivory',(.82,.79,.68),.25);ink=material('Face / ink blue',(.008,.03,.045),.33);iris=material('Eye / midnight blue glass',(.004,.017,.028),.16);iris.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.35
spruce=material('Guitar / fine spruce',(.78,.45,.18),.44,wood=True);rose=material('Guitar / warm rosewood',(.21,.052,.014),.31,wood=True);ebony=material('Guitar / dark fingerboard',(.028,.009,.004),.40,wood=True);bind=material('Guitar / thin cream binding',(.74,.50,.26),.40);nylon=material('Guitar / nylon',(.72,.66,.48),.28,.25);nickel=material('Guitar / satin nickel',(.55,.56,.51),.24,.8);hole=material('Guitar / sound chamber',(.006,.003,.001),.94)

for wood in [spruce,rose,ebony]:
 for node in wood.node_tree.nodes:
  if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='MULTIPLY':node.inputs[1].default_value=(2,15,180)
  if node.bl_idname=='ShaderNodeValToRGB':
   base=wood.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value
   node.color_ramp.elements[0].color=tuple(c*.88 for c in base[:3])+(1,);node.color_ramp.elements[1].color=tuple(min(1,c*1.05) for c in base[:3])+(1,)
  if node.bl_idname=='ShaderNodeBump':node.inputs['Distance'].default_value=.0004

def assign(o,m):o.data.materials.clear();o.data.materials.append(m)
for o in list(bpy.data.objects):
 if o.name.startswith('Face / ivory eye'):assign(o,ivory)
 elif o.name.startswith('Face / sideward iris'):assign(o,iris)
 elif o.name.startswith('Face / integrated upper eyelid'):assign(o,coat)
 elif o.name.startswith('Face /'):assign(o,ink)
 elif o.name.startswith('Guitar /'):
  name=o.name
  m=spruce if 'spruce' in name else ebony if 'fretboard' in name else hole if 'soundhole' in name or 'dark slot' in name else bind if 'binding' in name or 'nut' in name or 'saddle' in name else ivory if 'tuning peg' in name else nickel if 'fret' in name or 'shaft' in name else nylon if 'string' in name else rose
  assign(o,m)
  if o.type=='CURVE' and ('binding' in name or 'rosette' in name):o.data.bevel_depth*=.38
# Real shallow ear pockets, with a thicker surrounding rim from the unified sculpt.
earfelt=material('Miao / ear velvet',(.45,.075,.018),.84)
for side in [-1,1]:
 x=.43*side;vs=[(x-.105,-.38,3.18),(x+.105,-.38,3.18),(x+side*.065,-.30,3.43),(x-.105,-.10,3.18),(x+.105,-.10,3.18),(x+side*.065,-.07,3.43)];fs=[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)];d=bpy.data.meshes.new('Ear pocket cutter');d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new('Authoring / ear pocket',d);s.collection.objects.link(o);o.data.materials.append(earfelt);be=o.modifiers.new('Soft pocket corners','BEVEL');be.width=.026;be.segments=4;mod=body.modifiers.new('Inset ear pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='MANIFOLD';mod.object=o;o.hide_render=True;o.hide_set(True)
# Reference has fine cream whiskers, not thick cords.
whisk=material('Miao / fine cream whisker',(.98,.81,.51),.53)
for side in [-1,1]:
 for k in range(2):
  c=bpy.data.curves.new('Whisker','CURVE');c.dimensions='3D';c.bevel_depth=.0018;c.bevel_resolution=3;c.resolution_u=20;sp=c.splines.new('BEZIER');sp.bezier_points.add(2)
  for p,co in zip(sp.bezier_points,[(.075+side*.30,-.43,2.80-k*.095),(.075+side*.55,-.48,2.85-k*.10),(.075+side*.78,-.40,2.85-k*.12)]):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
  ob=bpy.data.objects.new('Miao / fine whisker',c);s.collection.objects.link(ob);c.materials.append(whisk)
# Area-uniform, seeded native hair curves; all roots sampled from the actual mesh.
bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);idx=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',idx);idx=idx.reshape(-1,3);tri=v[idx];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1);rng=np.random.default_rng(17);N=180000;pick=np.searchsorted(np.cumsum(area,dtype=np.float64),rng.random(N)*area.sum(dtype=np.float64));chosen=tri[pick];uv=rng.random((N,2));uv[:,0]=np.sqrt(uv[:,0]);weights=np.stack([1-uv[:,0],uv[:,0]*(1-uv[:,1]),uv[:,0]*uv[:,1]],axis=1);roots=(chosen*weights[:,:,None]).sum(axis=1);norm=cross[pick]/np.maximum(area[pick,None],1e-12);length=rng.uniform(.004,.009,N);bend=rng.normal(0,.0005,(N,3));positions=np.stack([roots+norm*(length*t)[:,None]+bend*t*t for t in [0,.33,.67,1]],axis=1).astype(np.float32)
hc=bpy.data.hair_curves.new('Miao / short plush groom');hc.add_curves([4]*N);hc.position_data.foreach_set('vector',positions.ravel());rad=hc.attributes.new('radius','FLOAT','POINT');rad.data.foreach_set('value',np.tile(np.array([.00065,.00051,.00028,.000025],np.float32),N));ho=bpy.data.objects.new('Miao / native short plush',hc);s.collection.objects.link(ho);ho.data.materials.append(coat);ev.to_mesh_clear()
# Cream seamless studio, same locked gray camera.
assign(bpy.data.objects['Studio / floor'],material('Studio / warm cream',(.91,.89,.83),.83));s.render.filepath=str(out/'color-front.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-plush-color-study.blend'));bpy.ops.render.render(write_still=True)
cam=s.camera;target=Vector((.18,0,1.72));cam.location=(6,-9,3.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'color-three-quarter.png');bpy.ops.render.render(write_still=True)
(out/'receipt.json').write_text(json.dumps({'stage':'C-shaded-candidate-unreviewed','groom':'180000 native 4-point hair curves, fixed seed17, .004-.009 scene units','texture':'flat hand-authored pigment only; no source image pixel projection','not_verified':['identity/materials independent C reviews','eye closure deformation','retopology/rig','strum contacts/animation','web/export']},indent=2)+'\n')
