"""C8: reference-anchor camera/instrument fit and continuous-body hold sculpt.
Owned C7 native scene only. Keeps original mesh, UV, rest pigments and native groom.
Run gray first; color and motion are separate gates.
"""
import bpy,numpy as np,math,json,hashlib,argparse,sys,time
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-fidelity-c8');p.add_argument('--size',type=int,default=896);p.add_argument('--samples',type=int,default=32);p.add_argument('--gray',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.out;out.mkdir(parents=True,exist_ok=True);src=root/'artifacts/character-eye-cornea-v3/miao-eye-cornea-static.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];cam=s.camera
s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(o):
 v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);return v.reshape(-1,3)
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
local=arr(body);M=np.array(body.matrix_world);world=local@M[:3,:3].T+M[:3,3]
rot=cam.rotation_euler.to_matrix();right=np.array(rot@Vector((1,0,0)));up=np.array(rot@Vector((0,1,0)));oldcamera=list(cam.location);oldscale=cam.data.ortho_scale
# Match ear/foot framing using actual geometry, not the floor shadow.
height=world@up;h0,h1=float(height.min()),float(height.max());scale=(h1-h0)/((1112-77)/1254);cup=h0+(1112/1254-.5)*scale;cright=-scale*((597.5/1254)-.5);delta=right*(cright-np.dot(cam.location,right))+up*(cup-np.dot(cam.location,up));cam.location+=Vector(delta);cam.data.ortho_scale=scale
# Fit actual bridge/hole/nut projected centers in a single affine guitar frame.
origin=np.array([-.27,-.85,1.30]);theta=math.radians(23.3);U=np.array([math.cos(theta),0,math.sin(theta)]);V=np.array([-math.sin(theta),0,math.cos(theta)]);oldbasis=np.stack([U*1.19,np.array([0,1,0]),V*1.19],axis=1)
anchors=[('Guitar / bridge',-.49,(391,728)),('Guitar / soundhole chamber',.12,(575,652)),('Guitar / nut',1.698,(1055,467))];A=[];B=[]
for name,u,pixel in anchors:
 o=bpy.data.objects[name];old=np.array(o.matrix_world.translation);x=cright+(pixel[0]/1254-.5)*scale;z=(cup+(.5-pixel[1]/1254)*scale-up[1]*old[1])/up[2];A.append([1,u]);B.append([x,z])
fit=np.linalg.lstsq(np.array(A),np.array(B),rcond=None)[0];neworigin=np.array([fit[0,0],origin[1],fit[0,1]]);newU=np.array([fit[1,0],0,fit[1,1]]);newscale=np.linalg.norm(newU);newV=np.array([-newU[2],0,newU[0]]) # match longitudinal and transverse scale
T=np.eye(4);T[:3,:3]=np.stack([newU,np.array([0,1,0]),newV],axis=1)@np.linalg.inv(oldbasis);T[:3,3]=neworigin-T[:3,:3]@origin
for o in list(s.objects):
 if o.name.startswith('Guitar /') or o.name=='Authoring / guitar grain coordinates':o.matrix_world=Matrix(T)@o.matrix_world

def screen_to_world(pixel,y):
 x=cright+(pixel[0]/1254-.5)*scale;z=(cup+(.5-pixel[1]/1254)*scale-up[1]*y)/up[2];return np.array([x,y,z])
# Smooth bounded displacement along each continuous anatomical sweep. This is a
# static sculpt key, not separate limb meshes and not a claimed animation rig.
pick=np.array([[-.48,.05,2.20],[-.76,-.20,2.10],[-.99,-.39,1.95],[-1.12,-.54,1.83],[-1.05,-.72,1.75],[-.86,-1,1.70],[-.67,-1.16,1.55],[-.50,-1.19,1.43],[-.42,-1.18,1.36],[-.43,-1.15,1.32]])
ptarget=[(410,359),(357,419),(303,477),(267,536),(300,556),(360,580),(413,609),(459,638),(474,645),(474,651)]
fret=np.array([[.48,.05,2.20],[.77,-.16,2.06],[1.04,-.36,1.90],[1.16,-.58,1.71],[1.20,-.82,1.70],[1.22,-1.02,1.83],[1.20,-1.035,1.98],[1.16,-1.025,2.035]])
ftarget=[(782,356),(852,425),(913,490),(944,568),(951,602),(952,561),(949,517),(945,500)]
paths=[]
for name,centers,pixels in [('picking',pick,ptarget),('fretting',fret,ftarget)]:
 target=np.array([screen_to_world(px,float(c[1])) for c,px in zip(centers,pixels)]);target[:2]=centers[:2] # shoulder anchored, not whole-arm translation
 target[2]=centers[2]*.5+target[2]*.5
 paths.append((name,centers,target))

def deform(P):
 Q=P.copy();z=P[:,2];# widen cheek softly, narrow belly 2%, reduce high head sidewall
 xscale=1-.020*(1-smooth((z-2.20)/.40))+.045*np.exp(-((z-2.70)/.20)**2)-.035*np.exp(-((z-3.22)/.12)**2)
 Q[:,0]*=xscale
 # Round the crown with a continuous spatial field, retaining integrated ear tips.
 crown=np.exp(-((z-3.30)/.065)**2)*smooth((np.abs(P[:,0])-.10)/.32)*(1-smooth((np.abs(P[:,0])-.43)/.10))
 Q[:,2]-=.042*crown
 for name,C,D in paths:
  dist=np.full(len(P),1e6);tbest=np.zeros(len(P));segidx=np.zeros(len(P),int)
  for j in range(len(C)-1):
   axis=C[j+1]-C[j];t=np.clip((P-C[j])@axis/np.dot(axis,axis),0,1);closest=C[j]+t[:,None]*axis;d=np.linalg.norm(P-closest,axis=1);take=d<dist;dist[take]=d[take];tbest[take]=t[take];segidx[take]=j
  front=smooth((-.25-P[:,1])/.30);side=smooth(((-P[:,0] if name=='picking' else P[:,0])-.10)/.22);heightmask=smooth((P[:,2]-.9)/.22)*(1-smooth((P[:,2]-2.20)/.25));weight=(1-smooth((dist-.23)/.17))*front*side*heightmask
  d0=D-C;offset=d0[segidx]*(1-tbest[:,None])+d0[np.minimum(segidx+1,len(C)-1)]*tbest[:,None];Q+=offset*weight[:,None]
  # Palm taper, measured around local centreline, does not shrink shoulder.
  localt=(segidx+tbest)/(len(C)-1);palm=smooth((localt-.50)/.30)*weight
  center=C[segidx]*(1-tbest[:,None])+C[np.minimum(segidx+1,len(C)-1)]*tbest[:,None]
  Q[:,0]-=.10*(P[:,0]-center[:,0])*palm;Q[:,1]-=.08*(P[:,1]-center[:,1])*palm
 return Q
Q=deform(world);invM=np.linalg.inv(M);qlocal=(Q-invM[:3,3]*0-M[:3,3])@np.linalg.inv(M[:3,:3]).T
key=body.shape_key_add(name='C8 / reference hold sculpt');key.data.foreach_set('co',qlocal.astype(np.float32).ravel());key.value=1
# Attached lids and face markings follow the same local head field.
for o in s.objects:
 if o==body or o==hair:continue
 if o.name.startswith(('C6 /','C7 / clear','Face /','Miao / fine whisker')):
  if o.type=='MESH':
   v=arr(o);m=np.array(o.matrix_world);w=v@m[:3,:3].T+m[:3,3];v=(deform(w)-m[:3,3])@np.linalg.inv(m[:3,:3]).T;o.data.vertices.foreach_set('co',v.astype(np.float32).ravel())
  elif o.type=='CURVE':
   for spl in o.data.splines:
    for p in spl.bezier_points:
     for field in ['co','handle_left','handle_right']:
      val=o.matrix_world@getattr(p,field);nv=deform(np.array([val]))[0];setattr(p,field,o.matrix_world.inverted()@Vector(nv))
# Slightly softer studio contact shadow; actual lights, no painted shadow.
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('Studio /'):o.data.size=max(5.0,o.data.size)
s.view_settings.exposure=-.20
# Preserve colored asset; gray copy below is only gate evidence.
bpy.context.view_layer.update();s.render.filepath='//renders/c8.png';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c8-reference-hold.blend'),compress=True)
def projection(ob):
 v=world_to_camera_view(s,cam,ob.matrix_world.translation);return [v.x*1254,(1-v.y)*1254]
receipt={'stage':'C8-static-gray-unreviewed' if a.gray else 'C8-static-color-unreviewed','source_sha256':sha(__file__),'input_sha256':sha(src),'camera':{'before':oldcamera,'before_scale':oldscale,'after':list(cam.location),'after_scale':scale},'guitar':{'origin':neworigin.tolist(),'u_vector':newU.tolist(),'scale':float(newscale),'angle_degrees':math.degrees(math.atan2(newU[2],newU[0])),'anchors':[{'object':name,'target':px,'actual':projection(bpy.data.objects[name])} for name,u,px in anchors]},'body':{'vertices':len(local),'continuous_mesh':True,'new_shape_key':key.name,'maximum_displacement':float(np.linalg.norm(Q-world,axis=1).max()),'native_groom_preserved':True},'limits':['Static hold is a smooth sculpt, not an articulated motion rig.','Gray and colored independent three-role gates pending.','No animation or browser acceptance yet.']}
if a.gray:
 def gray(name,val):
  m=bpy.data.materials.new('C8 gray '+name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(val,val,val,1);b.inputs['Roughness'].default_value=.65;return m
 mats={k:gray(k,v) for k,v in [('body',.4),('white',.72),('dark',.045),('wood',.30),('metal',.6)]}
 for o in s.objects:
  if o.type not in {'MESH','CURVES','CURVE'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear')):continue
  k='white' if o.name.startswith('C6 / sclera') else 'dark' if o.name.startswith(('C6 / iris','Face /')) else 'wood' if o.name.startswith('Guitar /') else 'body';o.data.materials.clear();o.data.materials.append(mats[k])
for view in ['front','three-quarter']:
 if view!='front':
  target=Vector((float(cright),0,float(cup)));cam.location=(6,-9,3.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(out/(('gray' if a.gray else 'color')+'-'+view+'.png'));bpy.ops.render.render(write_still=True)
receipt['input_unchanged']=sha(src)==receipt['input_sha256'];(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
