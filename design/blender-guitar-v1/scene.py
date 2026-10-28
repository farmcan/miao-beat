"""Original complete-scene Blender guitar study. No external models/textures.
Run: blender -b --python scene.py -- --output artifacts/blender-v1 --size 640 --samples 32 --still
Every exported frame contains the complete cat, connected arms/paws, guitar and floor.
"""
import argparse, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/blender-guitar-v1');p.add_argument('--size',type=int,default=640);p.add_argument('--samples',type=int,default=32);p.add_argument('--frame',type=int);p.add_argument('--still',action='store_true');p.add_argument('--no-render',action='store_true');p.add_argument('--device',choices=['AUTO','CPU','METAL'],default='AUTO');p.add_argument('--all',action='store_true');p.add_argument('--engine',choices=['CYCLES','BLENDER_EEVEE_NEXT'],default='CYCLES');args=p.parse_args(argv)
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine=args.engine
scene.render.resolution_x=args.size;scene.render.resolution_y=args.size;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.fps=60;scene.frame_start=0;scene.frame_end=23
if args.engine=='CYCLES':
 scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.cycles.seed=17;scene.cycles.use_animated_seed=False
 scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
 try:
  if args.device=='CPU':raise RuntimeError('CPU requested')
  prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
  gpus=[d for d in prefs.devices if d.type=='METAL']
  if gpus:
   for d in prefs.devices:d.use=(d.type=='METAL')
   scene.cycles.device='GPU'
 except Exception:pass
try:scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=-.4
except Exception:pass
scene.world.color=(0.65,0.65,0.65)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.85,0.85,0.82,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.60

# Materials remain editable and procedural in the .blend.
def material(name,color,rough=.5,metal=0,fur=False,wood=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if fur:
  if 'Sheen Weight' in b.inputs:b.inputs['Sheen Weight'].default_value=.25
  if 'Subsurface Weight' in b.inputs:b.inputs['Subsurface Weight'].default_value=.035
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=155;tex.inputs['Detail'].default_value=2.4;tex.inputs['Roughness'].default_value=.75
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.013;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],b.inputs['Normal'])
 if wood:
  coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,40,1.2);l.new(coord.outputs['Generated'],mapping.inputs[0]);tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=3;l.new(mapping.outputs[0],tex.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.16;ramp.color_ramp.elements[0].color=(*[x*.60 for x in color],1);ramp.color_ramp.elements[1].position=.84;ramp.color_ramp.elements[1].color=(*[min(x*1.18,1) for x in color],1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],b.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.11;bump.inputs['Distance'].default_value=.006;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
 return m
orange=material('Miao / warm tangerine plush',(0.64,.105,.012),.61,fur=True)
cream=material('Miao / buttercream plush',(.98,.77,.43),.7,fur=True)
stripe=material('Miao / cinnamon stripes',(.40,.070,.010),.68,fur=True)
earpink=material('Miao / warm ear felt',(.70,.24,.16),.68,fur=True)
white=material('Eyes / ivory',(.99,.96,.83),.23)
navy=material('Eyes / midnight teal',(.014,.061,.075),.20)
black=material('Nose and mouth',(.013,.025,.030),.4)
whisker=material('Whiskers / warm ivory',(.91,.73,.43),.59)
topwood=material('Guitar / spruce soundboard',(.80,.48,.19),.38,wood=True)
rosewood=material('Guitar / rosewood ribs',(.20,.057,.018),.3,wood=True)
fingerwood=material('Guitar / ebony fretboard',(.045,.018,.009),.35,wood=True)
binding=material('Guitar / ivory binding',(.93,.76,.43),.35)
rosette=material('Guitar / rosette inlay',(.26,.087,.018),.4)
holemat=material('Guitar / dark sound chamber',(.008,.005,.003),.93)
metal=material('Guitar / nickel silver',(.68,.70,.66),.24,.82)
stringmat=material('Guitar / nylon and wound strings',(.79,.73,.54),.30,.5)
floor=material('Studio / warm parchment',(.80,.79,.75),.78)

def smooth(obj,mat=None):
 if mat:obj.data.materials.append(mat)
 if obj.type=='MESH':
  for f in obj.data.polygons:f.use_smooth=True
 return obj

def sphere(name,pos,scale,mat,segments=48,rings=32):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;return smooth(o,mat)

def curve(name,points,radius,mat,parent=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=radius;c.bevel_resolution=4;s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for b,co in zip(s.bezier_points,points):b.co=co;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);c.materials.append(mat)
 if parent:o.parent=parent
 return o

def box(name,pos,scale,mat,bevel=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  m=o.modifiers.new('Soft handcrafted edges','BEVEL');m.width=bevel;m.segments=4;m=o.modifiers.new('Weighted corners','WEIGHTED_NORMAL')
 return o

def mesh(name,verts,faces,mat):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);return smooth(o,mat)

# The pear body is one continuous revolved surface, not stacked spheres.
rings=44;cols=80;verts=[];faces=[]
for j in range(rings+1):
 t=j/rings;z=.35+2.34*t;r=math.sin(math.pi*t)**.58*(1.14-.37*t)
 for i in range(cols):
  a=i/cols*2*math.pi;verts.append((r*math.cos(a),r*.72*math.sin(a),z))
for j in range(rings):
 for i in range(cols):a=j*cols+i;b=j*cols+(i+1)%cols;faces.append((a,b,b+cols,a+cols))
body=mesh('Miao / continuous pear body',verts,faces,orange)
sphere('Miao / cream belly',(0,-.525,1.42),(.78,.205,.99),cream)
# Short legs and rounded paws.
for side in [-1,1]:
 sphere('Miao / haunch',(.54*side,.04,.47),(.35,.40,.43),orange)
 sphere('Miao / foot',(.54*side,-.15,.22),(.34,.48,.22),orange)
 for dx in [-.105,.105]:curve('Miao / toe seam',[(.54*side+dx,-.597,.19),(.54*side+dx,-.59,.255),(.54*side+dx,-.54,.30)],.007,stripe)
# Tail sweeps out to the left; still connected behind the haunch.
curve('Miao / curled tail',[(-.75,.29,.67),(-1.15,.27,.55),(-1.42,.19,.71),(-1.46,.05,1.02)],.135,orange)
for i in range(3):
 t=i/3;curve('Miao / tail band',[(-1.08-.32*t,.13,.59+.30*t),(-1.12-.31*t,.33,.62+.30*t)],.054,stripe)
# Squared-round cat head, modest cheeks and compact muzzle.
head=sphere('Miao / rounded head',(0,-.015,2.96),(.90,.64,.77),orange,64,40)
for side in [-1,1]:
 sphere('Miao / cheek',(.48*side,-.28,2.74),(.39,.39,.35),orange)
# Sculpted softly beveled pointed ears.
for side in [-1,1]:
 x=.59*side
 vs=[(x-.28,-.10,3.36),(x+.25,-.10,3.37),(x+.10*side,-.03,4.00),(x-.28,.20,3.36),(x+.25,.20,3.37),(x+.10*side,.16,3.94)]
 ear=mesh('Miao / soft pointed ear',vs,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],orange);be=ear.modifiers.new('Rounded ear rim','BEVEL');be.width=.095;be.segments=5;ear.modifiers.new('Soft ear normals','WEIGHTED_NORMAL')
 vs=[(x-.15,-.164,3.49),(x+.15,-.164,3.49),(x+.065*side,-.14,3.84)]
 inner=mesh('Miao / inner ear felt',vs,[(0,1,2)],earpink);sol=inner.modifiers.new('Ear felt thickness','SOLIDIFY');sol.thickness=.013;be=inner.modifiers.new('Felt edge','BEVEL');be.width=.04;be.segments=4
# Cream muzzle is one shallow rounded shape.
sphere('Miao / cream muzzle',(0,-.566,2.72),(.49,.15,.30),cream)
for side in [-1,1]:
 x=.305*side
 sphere('Miao / eye white',(x,-.600,3.065),(.222,.085,.245),white)
 sphere('Miao / iris',(x+.045,-.674,3.023),(.117,.043,.151),navy)
 sphere('Miao / eye pupil',(x+.057,-.708,3.019),(.061,.018,.095),black)
 # Gentle raised brow rather than surprised eyebrows.
 curve('Miao / eyebrow',[(x-.17,-.561,3.405),(x,-.632,3.452),(x+.15,-.573,3.419)],.026,navy)
# Little rounded triangular nose and deliberate smile.
nose=mesh('Miao / nose',[(-.105,-.737,2.856),(.105,-.737,2.856),(0,-.783,2.755),(-.082,-.698,2.86),(.082,-.698,2.86),(0,-.71,2.76)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],black);be=nose.modifiers.new('Rounded nose','BEVEL');be.width=.036;be.segments=4;nose.modifiers.new('Nose normals','WEIGHTED_NORMAL')
curve('Miao / smile stem',[(0,-.736,2.77),(0,-.736,2.68)],.014,black)
curve('Miao / smile',[(-.16,-.712,2.68),(-.09,-.738,2.642),(0,-.74,2.66),(.09,-.738,2.642),(.16,-.712,2.68)],.013,black)
for side in [-1,1]:
 for row in range(3):
  z=2.78-row*.085
  curve('Miao / whisker',[(.38*side,-.625,z),(.73*side,-.697,z+.045-row*.015),(1.03*side,-.59,z+.08-row*.02)],.0065,whisker)
# Tabby markings are thin surface-following inlays, never raised sausage tubes.
def head_patch(name,cx,cz,rx,rz):
 vs=[];count=40
 for j in range(6):
  r=j/5
  for k in range(count):
   a=k/count*math.pi*2;x=cx+rx*r*math.cos(a);z=cz+rz*r*math.sin(a);surface=max(.002,1-(x/.9)**2-((z-2.96)/.77)**2);y=-.015-.64*math.sqrt(surface)-.003;vs.append((x,y,z))
 fs=[]
 for j in range(5):
  for k in range(count):a=j*count+k;b=j*count+(k+1)%count;fs.append((a,b,b+count,a+count))
 return mesh(name,vs,fs,stripe)
head_patch('Miao / forehead middle inlay',0,3.53,.067,.18)
for side in [-1,1]:
 head_patch('Miao / forehead side inlay',.265*side,3.51,.055,.16)
 for z in [2.91,3.17]:head_patch('Miao / temple stripe inlay',.79*side,z,.055,.095)

# Guitar uses a local u/v plane, front toward -Y, with 19-degree rising neck.
angle=math.radians(19);origin=Vector((-.31,-.82,1.48))
def g(u,v,depth=0):return origin+Vector((u*math.cos(angle)-v*math.sin(angle),depth,u*math.sin(angle)+v*math.cos(angle)))
# Closed outline sampled around a luthier-style classical body, longitudinal u.
outline=[(-.90,0),(-.85,.32),(-.67,.52),(-.42,.58),(-.18,.52),(.02,.38),(.22,.34),(.39,.43),(.59,.39),(.72,.20),(.73,0),(.72,-.20),(.59,-.39),(.39,-.43),(.22,-.34),(.02,-.38),(-.18,-.52),(-.42,-.58),(-.67,-.52),(-.85,-.32)]
# Catmull-Rom subdivision creates a flowing waist without polygonal corners.
def catmull(points,steps=5):
 r=[]
 for i in range(len(points)):
  p0=Vector(points[(i-1)%len(points)]);p1=Vector(points[i]);p2=Vector(points[(i+1)%len(points)]);p3=Vector(points[(i+2)%len(points)])
  for k in range(steps):
   t=k/steps;r.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 return r
outline=catmull(outline,7);N=len(outline)
def guitar_body(name,front,back,mat,shrink=1):
 vs=[g(v.x*shrink,v.y*shrink,d) for d in [front,back] for v in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];o=mesh(name,vs,fs,mat);be=o.modifiers.new('Instrument edge rounding','BEVEL');be.width=.018;be.segments=3;o.modifiers.new('Instrument normals','WEIGHTED_NORMAL');return o
guitar_body('Guitar / rosewood body',-.10,.20,rosewood)
guitar_body('Guitar / spruce soundboard',-.115,-.094,topwood,.993)
for d in [-.122,.18]:curve('Guitar / continuous binding',[g(v.x,v.y,d) for v in outline]+[g(outline[0].x,outline[0].y,d)],.012,binding)
# Shallow black soundhole and concentric rosette; no floating decal or backdrop.
def disc(name,u,v,r,d,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=.007,location=g(u,v,d),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=name;return smooth(o,mat)
def ring(name,u,v,r,thick,d,mat):
 return curve(name,[g(u+r*math.cos(i/96*2*math.pi),v+r*math.sin(i/96*2*math.pi),d) for i in range(97)],thick,mat)
disc('Guitar / soundhole chamber',.12,0,.221,-.132,holemat)
for r,w,mat in [(.237,.012,rosette),(.257,.008,binding),(.272,.009,rosette),(.287,.006,binding)]:ring('Guitar / rosette ring',.12,0,r,w,-.139,mat)
# Guitar-fitted boxes follow the instrument angle.
def gbox(name,u,v,d,scale,mat,bevel=.012):
 o=box(name,g(u,v,d),scale,mat,bevel);o.rotation_euler[1]=-angle;return o
gbox('Guitar / neck',1.19,0,.005,(1.10,.19,.19),rosewood,.035)
gbox('Guitar / ebony fretboard',1.13,0,-.133,(1.20,.06,.228),fingerwood,.012)
gbox('Guitar / bridge',-.49,0,-.153,(.12,.06,.42),rosewood,.015)
gbox('Guitar / bridge saddle',-.466,0,-.192,(.023,.025,.31),binding,.004)
gbox('Guitar / nut',1.698,0,-.172,(.024,.026,.228),binding,.004)
gbox('Guitar / headstock',1.94,0,-.025,(.43,.16,.29),rosewood,.045)
for row in [-1,1]:
 gbox('Guitar / headstock dark slot',1.95,row*.077,-.117,(.26,.009,.040),holemat,.018)
 for k in range(3):
  u=1.79+k*.126;v=row*.164
  sphere('Guitar / ivory tuning peg',g(u,v,-.015),(.041,.045,.041),binding,24,16)
  curve('Guitar / tuner shaft',[g(u,row*.10,-.03),g(u,row*.17,-.03)],.014,metal)
# Physical equal-tempered fret positions, six individually visible strings.
for fret in range(1,19):
 u=1.698-(1.698+.466)*(1-2**(-fret/12))
 if u<.52:continue
 curve('Guitar / silver fret',[g(u,-.111,-.170),g(u,.111,-.170)],.0065,metal)
for k in range(6):
 v=(k-2.5)*.037
 curve('Guitar / string %d'%(k+1),[g(-.49,v,-.206),g(.50,v,-.186),g(1.70,v,-.188),g(2.04,v*.66,-.137)],.0028 if k<3 else .0021,stringmat)
 sphere('Guitar / bridge tie',g(-.51,v,-.19),(.013,.013,.010),binding,16,12)
# Sculpted arms with continuous overlapping shoulder/forearm/paw volumes.
# Plucking-side pivot drives everything together; arm is not rendered separately.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0));pickroot=bpy.context.object;pickroot.name='Rig / plucking shoulder'
def parent_keep(o,parent):
 bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;return o
sphere('Miao / picking upper arm',(-.80,-.49,2.01),(.27,.25,.33),orange)
arm=curve('Miao / picking connected forearm',[(-.84,-.58,2.08),(-.69,-.88,1.93),(-.37,-1.234,1.90)],.20,orange)
paw=parent_keep(sphere('Miao / picking paw',(-.33,-1.234,1.88),(.255,.19,.22),orange),pickroot)
for dx in [-.07,.04]:parent_keep(curve('Miao / picking toe fold',[(dx-.32,-1.414,1.85),(dx-.29,-1.412,1.79)],.006,stripe),pickroot)
# Fretting-side hand wraps around neck; the palm remains stationary in v1.
sphere('Miao / fretting shoulder',(.73,-.37,2.06),(.26,.25,.33),orange)
curve('Miao / fretting connected arm',[(.78,-.47,2.16),(.89,-.64,1.99),(1.00,-.89,2.00)],.19,orange)
fretpaw=sphere('Miao / fretting paw',(1.00,-.925,2.025),(.17,.105,.225),orange);fretpaw.rotation_euler[1]=-.25
for i in range(3):
 sphere('Miao / fretting curled toe',(1.00+i*.065,-1.028,2.075+i*.022),(.043,.037,.073),orange,24,16)
# One forward downstroke, then retract from the strings before lifting.
# Shoulder is fixed; elbow/forearm control points follow the whole-paw target.
# With front toward -Y, the paw's back surface always stays in front of soundboard.
stroke_keys=[(0,-1.234,1.88),(1,-1.200,1.79),(2,-1.164,1.70),(3,-1.203,1.59),(4,-1.204,1.48),(6,-1.220,1.33),(8,-1.285,1.34),(12,-1.310,1.60),(18,-1.265,1.90),(23,-1.234,1.88)]
for frame,y,z in stroke_keys:
 delta=Vector((0,y+1.234,z-1.88));pickroot.location=delta;pickroot.keyframe_insert(data_path='location',frame=frame)
def clamp_action(obj):
 if obj.animation_data and obj.animation_data.action:
  action=obj.animation_data.action
  fcurves=list(action.fcurves) if hasattr(action,'fcurves') else [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
  for fc in fcurves:
   for k in fc.keyframe_points:
    k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
clamp_action(pickroot)
# Analytic two-bone IK. A stable outward pole selects the elbow; lengths never stretch.
shoulder=Vector((-.80,-.49,2.05));upper_length=.58;fore_length=.70;pole=Vector((-1,0,.15));joint_audit=[]
for frame in range(24):
 scene.frame_set(frame);bpy.context.view_layer.update();wrist=paw.matrix_world.translation.copy();direction=wrist-shoulder;distance=direction.length;direction.normalize()
 if not abs(upper_length-fore_length)<distance<upper_length+fore_length:raise RuntimeError('Unreachable paw target at frame '+str(frame))
 along=(upper_length**2-fore_length**2+distance**2)/(2*distance);height=math.sqrt(max(0,upper_length**2-along**2));bend=pole-direction*pole.dot(direction);bend.normalize();elbow=shoulder+direction*along+bend*height
 for bp,pos in zip(arm.data.splines[0].bezier_points,[shoulder,elbow,wrist]):bp.co=pos;bp.keyframe_insert(data_path='co',frame=frame)
 joint_audit.append({'frame':frame,'shoulder':list(shoulder),'elbow':list(elbow),'wrist':list(wrist),'upper_length':(elbow-shoulder).length,'fore_length':(wrist-elbow).length})
clamp_action(arm.data)
(out/'rig-audit.json').write_text(json.dumps({'method':'analytic two-bone IK, stable outward pole; connected thick curve follows joint centers','upper_length':upper_length,'fore_length':fore_length,'frames':joint_audit},indent=2)+'\n')
# Fixed portrait camera and studio, never keyframed.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.012));smooth(bpy.context.object,floor);bpy.context.object.name='Studio / seamless floor'
def area(name,pos,energy,size,color,target=(0,0,1.9)):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Studio / large soft key',(-3.5,-4.5,7.0),650,5.0,(1,.94,.86))
area('Studio / cool fill',(4,-3.3,4.4),350,4.0,(.78,.88,1))
area('Studio / edge light',(1.5,3.0,5.5),600,3.5,(1,.91,.79))
bpy.ops.object.camera_add(location=(3.0,-11.5,4.8));camera=bpy.context.object;camera.name='Camera / fixed complete scene';target=Vector((.20,0,2.0));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=4.95;camera.data.lens=52;scene.camera=camera
# Analytic surface audit: actual evaluated paw center against string center lines.
# Positive string_surface_gap = clearance; negative = string displaced into plush.
audit=[]
for frame in range(24):
 scene.frame_set(frame);bpy.context.view_layer.update();c=paw.matrix_world.translation;gaps=[]
 for k in range(6):
  v=(k-2.5)*.037;u=(c.x-origin.x+v*math.sin(angle))/math.cos(angle);point=g(u,v,-.206+(u+.49)/.99*.020);r=1-((point.x-c.x)/.255)**2-((point.z-c.z)/.22)**2
  gaps.append(None if r<0 else round(point.y-(c.y+.19*math.sqrt(r)),6))
 audit.append({'frame':frame,'paw_center':list(c),'soundboard_clearance':round((origin.y-.115)-(c.y+.19),6),'string_surface_gaps':gaps})
(out/'contact-audit.json').write_text(json.dumps({'units':'Blender scene units','paw_radii':[.255,.19,.22],'soundboard_front_y':origin.y-.115,'meaning':'positive clearance; small negative value = contact with compliant string; all soundboard_clearance must stay positive','frames':audit},indent=2)+'\n')
scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-guitar-v1.blend'))
meta={'generator':'scene.py','original_model':True,'external_assets':[],'complete_scene':True,'fps':60,'frames':24,'contact_frame':2,'frame_size':args.size,'engine':args.engine,'samples':args.samples,'note':'Short one-shot right-paw study; stationary fretting paw. Visual and input acceptance still required.'};(out/'scene-manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
frames=[] if args.no_render else range(24) if args.all else [args.frame if args.frame is not None else 0]
for frame in frames:
 scene.frame_set(frame);scene.render.filepath=str(out/f'frame-{frame:03d}.png');bpy.ops.render.render(write_still=True)
print('MIAO_BLENDER_RENDER_DONE',str(out))
