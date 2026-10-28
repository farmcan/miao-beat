"""Reference-driven continuous surface study, distinct from rejected primitive pilot.
Geometry stage only: editable closed loft, voxel-unified shoulder/ear/foot junctions.
Instrument construction reuses original project code; no third-party mesh assets.
Run Blender -b --python this.py -- --output artifacts/character-sculpt-v2 --size 800
"""
import bpy, math, sys, argparse, json, hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/character-sculpt-v2');p.add_argument('--size',type=int,default=800);p.add_argument('--samples',type=int,default=32);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=(root/a.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.seed=17
try:
 pr=bpy.context.preferences.addons['cycles'].preferences;pr.compute_device_type='METAL';pr.get_devices()
 for d in pr.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.79,.75,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
# Gray stage intentionally preserves material boundaries via neutral values, no fur/color.
def material(name,value):
 m=bpy.data.materials.new(name);m.diffuse_color=(value,value,value,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(value,value,value,1);b.inputs['Roughness'].default_value=.65;return m
gray=material('Clay / body',.40);light=material('Clay / eyes',.72);dark=material('Clay / pupil and nose',.055);woodgray=material('Clay / guitar',.29);ground=material('Clay / backdrop',.8)
def smooth(o,mat=None):
 if mat:o.data.materials.append(mat)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def mesh(name,vs,fs,mat=gray):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);s.collection.objects.link(o);return smooth(o,mat)
def sphere(name,pos,scale,mat=gray,segments=48,rings=32):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return smooth(o,mat)
def curve(name,points,radius,mat,parent=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.use_fill_caps=True;c.resolution_u=24;c.bevel_depth=radius;c.bevel_resolution=4;sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for b,co in zip(sp.bezier_points,points):b.co=co;b.handle_left_type=b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);s.collection.objects.link(o);c.materials.append(mat);return o
def box(name,pos,scale,mat,bevel=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:m=o.modifiers.new('Rounded edges','BEVEL');m.width=bevel;m.segments=4
 return o
# Measured front silhouette mapped with 300 reference pixels per scene unit.
# No separate spherical head: full ear-base-to-belly trunk is a single quad surface.
# z, half-width, half-depth; interpolation uses smooth Catmull-Rom, not stacked balls.
profile=[(.29,.00,.02),(.34,.72,.34),(.43,1.06,.54),(.58,1.25,.67),(.85,1.38,.74),(1.15,1.38,.74),(1.45,1.30,.70),(1.78,1.17,.63),(2.05,1.05,.53),(2.28,.89,.46),(2.50,.66,.43),(2.60,.60,.425),(2.86,.575,.42),(3.10,.55,.405),(3.24,.51,.38),(3.30,.43,.31),(3.33,.00,.01)]
def catmull_value(i,t):
 ps=[Vector(profile[max(0,min(len(profile)-1,j))]) for j in [i-1,i,i+1,i+2]];p0,p1,p2,p3=ps
 return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
vs=[];fs=[];cols=128
for j in range((len(profile)-1)*8+1):
 i=min(j//8,len(profile)-2);t=(j-i*8)/8;z,rx,ry=catmull_value(i,t);rx=max(.001,rx);ry=max(.001,ry);ex=2.4+.8*min(1,max(0,(z-2.32)/.28))
 for k in range(cols):
  an=2*math.pi*k/cols;cx=math.cos(an);sn=math.sin(an);x=rx*math.copysign(abs(cx)**(2/ex),cx);y=ry*math.copysign(abs(sn)**(2/ex),sn)
  vs.append((x,y+.03,z))
rows=len(vs)//cols
for j in range(rows-1):
 for k in range(cols):u=j*cols+k;v=j*cols+(k+1)%cols;fs.append((u,v,v+cols,u+cols))
fs.extend([tuple(range(cols-1,-1,-1)),tuple((rows-1)*cols+k for k in range(cols))]);body=mesh('Miao / continuous pear and rounded-square face',vs,fs);merge=[body]
# Closed sweep with variable cross sections forms flattened shoulder-to-paw surface.
def sweep(name,points,radii):
 # dense sampled centerline, tangent-oriented elliptical sections, capped ends.
 verts=[];faces=[];N=32
 dense=[];dr=[]
 for j in range((len(points)-1)*10+1):
  i=min(j//10,len(points)-2);q=(j-i*10)/10
  def interp(seq):
   v0,v1,v2,v3=[Vector(seq[max(0,min(len(seq)-1,k))]) for k in [i-1,i,i+1,i+2]]
   return .5*((2*v1)+(-v0+v2)*q+(2*v0-5*v1+4*v2-v3)*q*q+(-v0+3*v1-3*v2+v3)*q*q*q)
  dense.append(interp(points));dr.append(interp(radii))
 points=dense;radii=dr
 for i,p in enumerate(points):
  c=Vector(p);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);t.normalize();u=t.cross(Vector((0,1,0))).normalized();v=t.cross(u).normalized();ra,rb=radii[i]
  for k in range(N):q=2*math.pi*k/N;verts.append(c+u*math.cos(q)*ra+v*math.sin(q)*rb)
 for i in range(len(points)-1):
  for k in range(N):q=i*N+k;r=i*N+(k+1)%N;faces.append((q,r,r+N,q+N))
 faces.extend([tuple(range(N-1,-1,-1)),tuple((len(points)-1)*N+k for k in range(N))]);return mesh(name,verts,faces)
# Relaxed arm is curved from shoulder, with no upright pipe or separated elbow spheres.
merge.append(sweep('Miao / integrated picking arm',[(-.48,.05,2.20),(-.76,-.20,2.10),(-.99,-.39,1.95),(-1.12,-.54,1.83),(-1.05,-.72,1.75),(-.86,-1.00,1.70),(-.67,-1.16,1.55),(-.50,-1.19,1.43),(-.42,-1.18,1.36),(-.43,-1.15,1.32)],[(.19,.23),(.25,.26),(.28,.27),(.29,.26),(.26,.25),(.235,.23),(.22,.21),(.19,.16),(.13,.13),(.015,.02)]))
merge.append(sweep('Miao / integrated holding arm',[(.48,.05,2.20),(.77,-.16,2.06),(1.04,-.36,1.90),(1.16,-.58,1.71),(1.20,-.82,1.70),(1.22,-1.02,1.83),(1.20,-1.035,1.98),(1.16,-1.025,2.035)],[(.19,.21),(.24,.24),(.26,.26),(.25,.25),(.24,.23),(.23,.19),(.19,.16),(.115,.10)]))

# Sculpted toe lobes are fused with the same hand/body surface, not arm plates.
for i in range(3):
 x=1.11+i*.095;z=2.02+i*.038
 merge.append(sweep('Miao / curled fretting toe '+str(i),[(x+.08,-1.025,z-.03),(x+.025,-1.09,z+.03),(x-.045,-1.125,z+.035),(x-.075,-1.12,z-.018)],[(.074,.078),(.073,.076),(.062,.063),(.035,.035)]))
merge.append(sweep('Miao / low curved tail',[(-1.08,.30,.70),(-1.37,.28,.58),(-1.57,.18,.62),(-1.69,.08,.78),(-1.67,.035,.96),(-1.64,.04,1.02)],[(.14,.15),(.15,.16),(.14,.15),(.13,.14),(.115,.12),(.045,.05)]))

for side in [-1,1]:
 merge.append(sweep('Miao / short continuous leg',[(side*.58,.02,.57),(side*.57,-.005,.35),(side*.56,-.08,.21),(side*.56,-.16,.12)],[(.23,.26),(.20,.23),(.145,.18),(.12,.16)]))
 merge.append(sphere('Miao / small padded foot',(side*.57,-.18,.105),(.175,.245,.105)))
 # Rounded triangular ears, broad low root integrated into head.
 x=side*.43;vv=[(x-.18,-.18,3.16),(x+.18,-.18,3.16),(x+side*.075,-.13,3.50),(x-.18,.14,3.16),(x+.18,.14,3.16),(x+side*.075,.11,3.48)]
 ear=mesh('Miao / integrated ear',vv,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]);be=ear.modifiers.new('Soft ear edge','BEVEL');be.width=.055;be.segments=4;bpy.context.view_layer.objects.active=ear;bpy.ops.object.modifier_apply(modifier=be.name);merge.append(ear)
# Voxel-unify anatomical junctions into one continuous editable mesh; no detached limbs.
bpy.ops.object.select_all(action='DESELECT')
for o in merge:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join();rem=body.modifiers.new('Continuous anatomical fusion','REMESH');rem.mode='VOXEL';rem.voxel_size=.015;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Sculpt relaxation','SMOOTH');sm.factor=.5;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name);sub=body.modifiers.new('Smooth sculpt surface','SUBSURF');sub.levels=1;sub.render_levels=1;body.modifiers.remove(sub)
# Eye structure: inset spherical volumes with sideward pupils, thick arc brows.
for side in [-1,1]:
 x=side*.235+.075
 # Only an upper lid wraps the sclera. Lower and outer edges sit in the face,
 # avoiding the full raised circular goggle which independent review rejected.
 from mathutils.bvhtree import BVHTree
 bpy.context.view_layer.update();face_bvh=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
 def surface_y(px,pz):
  hit,normal,idx,dist=face_bvh.ray_cast(Vector((px,-3,pz)),Vector((0,1,0)),6)
  return hit.y if hit else -.38
 fy=surface_y(x,2.973);ey=fy-.002
 eye_vs=[];eye_fs=[];count=49
 for r in range(5):
  t=r/4;rx=.117+.025*t;rz=.099+.022*t
  for k in range(count):
   an=.04*math.pi+k/(count-1)*.92*math.pi;px=x+rx*math.cos(an);pz=2.973+rz*math.sin(an)
   rho=(.117*math.cos(an)/.120)**2+(.099*math.sin(an)/.105)**2
   inner_y=ey-.053*math.sqrt(max(0,1-rho))-.001
   outer_y=surface_y(px,pz)-.001
   eye_vs.append((px,(1-t)*inner_y+t*outer_y,pz))
 for r in range(4):
  for k in range(count-1):u=r*count+k;v=u+1;eye_fs.append((u,v,v+count,u+count))
 lid=mesh('Face / integrated upper eyelid',eye_vs,eye_fs);m=lid.modifiers.new('Soft upper lid','SUBSURF');m.levels=2
 sphere('Face / ivory eye',(x,ey,2.973),(.120,.053,.105),light)
 sphere('Face / sideward iris',(x+.050,ey-.051,2.965),(.060,.021,.066),dark)
 curve('Face / thick curved brow',[(x-.10,-.418,3.136),(x-.045,-.45,3.165),(x+.015,-.454,3.168),(x+.08,-.428,3.145)],.026,dark)
# Soft square muzzle, continuous rounded box rather than a round ball.
# Muzzle patch is a future surface-color region; no protruding rectangular block.
nose=mesh('Face / rounded triangular nose',[(.005,-.467,2.897),(.145,-.467,2.897),(.075,-.492,2.817),(.005,-.415,2.897),(.145,-.415,2.897),(.075,-.42,2.817)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],dark);m=nose.modifiers.new('Soft nose corners','BEVEL');m.width=.022;m.segments=4
curve('Face / smile stem',[(.075,-.435,2.85),(.075,-.436,2.76)],.008,dark)
curve('Face / smile',[(-.015,-.425,2.772),(.030,-.438,2.753),(.075,-.439,2.757),(.120,-.438,2.753),(.155,-.425,2.775)],.008,dark)
# Guitar only: reuse the original project instrument mesh construction, scaled/angled to reference.
orange=gray;cream=light;stripe=gray;earpink=gray;white=light;navy=dark;black=dark;whisker=light;topwood=woodgray;rosewood=woodgray;fingerwood=dark;binding=light;rosette=dark;holemat=dark;metal=light;stringmat=light;scene=s
src=(root/'design/blender-guitar-v1/scene.py').read_text();start=src.index('# Guitar uses a local');end=src.index('# Sculpted arms',start)
guit=src[start:end].replace('angle=math.radians(19);origin=Vector((-.31,-.82,1.48))','angle=math.radians(23.3);origin=Vector((-.27,-.85,1.30))').replace('return origin+Vector((u*math.cos(angle)-v*math.sin(angle),depth,u*math.sin(angle)+v*math.cos(angle)))','return origin+Vector((1.19*(u*math.cos(angle)-v*math.sin(angle)),depth,1.19*(u*math.sin(angle)+v*math.cos(angle))))')
exec(compile(guit,'project-instrument-reuse','exec'))
# Actual carved hold clearance: editable live boolean after the sculpt surface.
# Neck remains separate from cat; does not weld instrument to a paw.
cutter=gbox('Authoring / fretting clearance',1.15,0,.025,(1.28,.30,.275),gray,.025)
cut=body.modifiers.new('Palm clearance around neck','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='MANIFOLD';cut.object=cutter;cutter.hide_render=True;cutter.hide_set(True)
# Ground and same near-front camera. Raw geometry gate, no fake fur or beauty grading.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.01));bpy.context.object.name='Studio / floor';bpy.context.object.data.materials.append(ground)
def area(name,pos,power,size):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
area('Studio / broad key',(-3,-4.5,7),650,5);area('Studio / broad fill',(4,-2,4),300,4)
bpy.ops.object.camera_add(location=(.18,-12,2.7));cam=bpy.context.object;cam.name='Camera / reference front';target=Vector((.18,0,1.72));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.1;s.camera=cam

# Camera-guided micro-sculpting. The author chooses a drawn line in the locked
# 1024px composition; rays locate the actual connected paw/foot surface.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();bvh=BVHTree.FromObject(body,dg)
rot=cam.rotation_euler.to_matrix();right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));forward=rot@Vector((0,0,-1));guide_receipt=[]
guides=[('Picking toe crease 1',[(367,610),(373,625),(372,638)],.012),('Picking toe crease 2',[(337,608),(345,625),(347,640)],.012),('Holding toe crease 1',[(748,454),(756,462),(760,478)],.010),('Holding toe crease 2',[(775,438),(783,446),(790,460)],.010)]
for side in [-1,1]:
 for px in ([314,340] if side<0 else [602,626]):guides.append(('Foot toe crease',[(px,925),(px,933),(px,941)],.009))
for name,pts,r in guides:
 centers=[]
 for px,py in pts:
  ray=cam.location+right*((px/1024-.5)*cam.data.ortho_scale)+up*((.5-py/1024)*cam.data.ortho_scale)
  hit,normal,face,distance=bvh.ray_cast(ray,forward,30)
  if hit is None:continue
  centers.append(hit+normal*.0015)
 if len(centers)<2:continue
 o=sweep('Authoring / '+name,centers,[(r,r)]*len(centers));m=body.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=o;o.hide_render=True;o.hide_set(True)
 guide_receipt.append({'name':name,'pixels':pts,'world':[list(v) for v in centers],'radius':r})
sub=body.modifiers.new('Smooth final sculpt surface','SUBSURF');sub.levels=1;sub.render_levels=1
(out/'sculpt-guides.json').write_text(json.dumps(guide_receipt,indent=2)+'\n')

# Source reference visible only in authoring, hidden render; no image-projection impostor.
bpy.ops.object.empty_add(type='IMAGE',location=(0,.9,1.7),rotation=(math.pi/2,0,0));ref=bpy.context.object;ref.name='Reference / original guitar idle';ref.data=bpy.data.images.load(str(root/'public/character/instrument-scenes-v1/guitar/idle.jpg'));ref.empty_display_size=4.1;ref.data.pack();ref.hide_render=True;ref.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-reference-gray.blend'))
s.render.filepath=str(out/'gray-front.png');bpy.ops.render.render(write_still=True)
# 45 degree diagnostic only, never accepted as source-proven unseen geometry.
cam.location=(6,-9,3.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'gray-three-quarter.png');bpy.ops.render.render(write_still=True)
receipt={'stage':'B-gray-candidate-unreviewed','reference_sha256':hashlib.sha256((root/'public/character/instrument-scenes-v1/guitar/idle.jpg').read_bytes()).hexdigest(),'body_method':'custom reference silhouette loft + swept arms, voxel fused anatomy; no separate head or limb plates','body_vertices':len(body.data.vertices),'body_faces':len(body.data.polygons),'guitar_reuse':'project instrument construction from design/blender-guitar-v1/scene.py; no old character construction','camera':'orthographic 4.1, near-front, target (.18,0,1.72)','unverified':['art fidelity','topology suitable for deformation','hand string contacts','all animation','color/plush materials','web rendering']};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
