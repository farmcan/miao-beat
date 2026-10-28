"""C6 eye anatomy study: face-conforming sclera, attached iris, soft lid margins.
Only static anatomy here. No hiding/scaling eyes and no animation expansion.
"""
import argparse,hashlib,json,math,sys,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/character-eye-inset-v4');p.add_argument('--size',type=int,default=1024);p.add_argument('--samples',type=int,default=32);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.output;out.mkdir(parents=True,exist_ok=True);src=root/'artifacts/character-sculpt-d0-groom/baseline-attached.blend'
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];coat=bpy.data.materials['Miao / warm short plush']
old_eyes=sorted([o for o in s.objects if o.name.startswith('Face / ivory eye')],key=lambda o:o.location.x);old_irises=sorted([o for o in s.objects if o.name.startswith('Face / sideward iris')],key=lambda o:o.location.x)
white=old_eyes[0].data.materials[0].copy();white.name='C6 / warm sclera';iris_mat=old_irises[0].data.materials[0].copy();iris_mat.name='C6 / attached navy iris'
face_bvh=BVHTree.FromObject(body,dg);inv=body.matrix_world.inverted();fw=(inv.to_3x3()@Vector((0,1,0))).normalized();cache={}
def fy(x,z):
 k=(round(float(x),7),round(float(z),7))
 if k not in cache:
  hit=face_bvh.ray_cast(inv@Vector((float(x),-3,float(z))),fw,20)[0]
  if hit is None:raise RuntimeError('No actual face surface under eye '+str(k))
  cache[k]=float((body.matrix_world@hit).y)
 return cache[k]
def coords(o):
 col=o.data.vertices if o.type=='MESH' else o.data.position_data;arr=np.empty(len(col)*3,np.float32);col.foreach_get('co' if o.type=='MESH' else 'vector',arr);return arr.reshape(-1,3)
def dh(v):return hashlib.sha256(np.asarray(v).tobytes()).hexdigest()
stable={o.name:dh(coords(o)) for o in s.objects if o.type in {'MESH','CURVES'} and not o.name.startswith(('Face / ivory eye','Face / sideward iris','Face / integrated upper eyelid'))}
body_hash=dh(coords(body));hair_before=coords(hair).copy();rest_before=np.empty(len(hair.data.attributes['miao_rest_position'].data)*3,np.float32);hair.data.attributes['miao_rest_position'].data.foreach_get('vector',rest_before);rest_hash=dh(rest_before);specs=[]
for eye_index,(eye,ir) in enumerate(zip(old_eyes,old_irises)):
 specs.append({'center_x':float(eye.location.x),'center_z':float(eye.location.z),'white_rx':(.120 if eye_index==0 else .1085),'white_rz':(.105 if eye_index==0 else .1085),'protrusion':.028,'iris_dx':float(ir.location.x-eye.location.x),'iris_dz':float(ir.location.z-eye.location.z),'iris_rx':(.055 if eye_index==0 else .048),'iris_rz':.066,'old_white_center_y':float(eye.location.y),'old_iris_center_y':float(ir.location.y),'old_white_y_radius':.053,'old_iris_y_radius':.021})
for o in list(s.objects):
 if o.name.startswith(('Face / ivory eye','Face / sideward iris','Face / integrated upper eyelid')):bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,vs,fs,mat,rest=False):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(mat)
 for face in me.polygons:face.use_smooth=True
 if rest:
  at=me.attributes.new('miao_rest_position','FLOAT_VECTOR','POINT');at.data.foreach_set('vector',np.asarray(vs,np.float32).ravel())
 return ob
def sclera_y(e,x,z):
 r2=((x-e['center_x'])/e['white_rx'])**2+((z-e['center_z'])/e['white_rz'])**2
 if r2>1.000001:return None
 return fy(x,z)+.002-(e['protrusion']+.002)*max(0,1-r2)**.65
new_objects=[];fronts=[]
for side,e in zip(['L','R'],specs):
 ex,ez=e['center_x'],e['center_z'];N=96;R=24
 # A closed curved white volume. Its perimeter tucks just under the actual skin.
 v=[];f=[]
 for back in [False,True]:
  v.append((ex,fy(ex,ez)+.020 if back else sclera_y(e,ex,ez),ez))
  for j in range(1,R+1):
   r=j/R
   for k in range(N):
    t=2*math.pi*k/N;x=ex+e['white_rx']*r*math.cos(t);z=ez+e['white_rz']*r*math.sin(t);v.append((x,fy(x,z)+.020 if back else sclera_y(e,x,z),z))
 layer=1+N*R
 for back in [False,True]:
  off=layer if back else 0
  for k in range(N):
   tri=(off,off+1+k,off+1+(k+1)%N);f.append(tri[::-1] if back else tri)
  for j in range(R-1):
   for k in range(N):
    u=off+1+j*N+k;w=off+1+j*N+(k+1)%N;q=(u,u+N,w+N,w);f.append(q[::-1] if back else q)
 for k in range(N):
  u=1+(R-1)*N+k;w=1+(R-1)*N+(k+1)%N;f.append((u,u+layer,w+layer,w))
 white_obj=mesh('C6 / sclera '+side,v,f,white);new_objects.append(white_obj)
 # Iris is a true shallow curved mesh attached to the same sclera, not another ball.
 ix,iz=ex+e['iris_dx'],ez+e['iris_dz'];v=[(ix,sclera_y(e,ix,iz)-.0015,iz)];f=[];tones=[(.002,.008,.012,1)];IR=24
 for j in range(1,IR+1):
  r=j/IR
  for k in range(N):
   t=2*math.pi*k/N;x=ix+e['iris_rx']*r*math.cos(t);z=iz+e['iris_rz']*r*math.sin(t);y=sclera_y(e,x,z)
   if y is None:raise RuntimeError('Iris exceeded sclera aperture')
   v.append((x,y-.0008-.0007*(1-r*r),z));blend=max(0,min(1,(r-.54)/.26));grain=1+.025*math.sin(t*31+r*4);tones.append(((.002+.006*blend)*grain,(.008+.026*blend)*grain,(.012+.038*blend)*grain,1))
 for k in range(N):f.append((0,1+k,1+(k+1)%N))
 for j in range(IR-1):
  for k in range(N):u=1+j*N+k;w=1+j*N+(k+1)%N;f.append((u,u+N,w+N,w))
 iris_obj=mesh('C6 / iris '+side,v,f,iris_mat);assert max(p.normal.y for p in iris_obj.data.polygons)<0,'Iris must have consistent camera-facing orientation';new_objects.append(iris_obj);at=iris_obj.data.color_attributes.new('C6IrisTone','FLOAT_COLOR','POINT');at.data.foreach_set('color',np.asarray(tones,np.float32).ravel())
 # Two soft skin surfaces share eye-corner coordinates. Outside rim is on the face.
 for upper in [True,False]:
  v=[];f=[];n=65;rows=9
  for j in range(rows):
   q=j/(rows-1);sm=q*q*(3-2*q)
   for k in range(n):
    t=math.pi*k/(n-1);sign=1 if upper else -1;inner_rx=e['white_rx']*.965;inner_rz=e['white_rz']*.935;x=ex+(inner_rx+.041*q)*math.cos(t);z=ez+sign*(inner_rz+.047*q)*math.sin(t)
    xi=ex+inner_rx*math.cos(t);zi=ez+sign*inner_rz*math.sin(t);inner=sclera_y(e,xi,zi)-.0010;outer=fy(x,z)-.0004;y=(1-sm)*inner+sm*outer;white_y=sclera_y(e,x,z)
    if white_y is not None:y=min(y,white_y-.0010)
    v.append((x,y,z))
  for j in range(rows-1):
   for k in range(n-1):u=j*n+k;w=u+1;quad=(u,w,w+n,u+n);f.append(quad[::-1] if upper else quad)
  lid=mesh('C6 / '+('upper' if upper else 'lower')+' lid '+side,v,f,coat,True);lid['side']=side;lid['role']='upper' if upper else 'lower';new_objects.append(lid)
 fronts.append({'eye':side,'face_y_at_eye_center':fy(ex,ez),'sclera_center_front_y':sclera_y(e,ex,ez),'sclera_protrusion':.028,'iris_attached_front_y':sclera_y(e,ix,iz)-.0015,'iris_added_protrusion':.0015})
# Shader colors on the iris are attributes of actual geometry, not an image overlay.
bs=iris_mat.node_tree.nodes.get('Principled BSDF');node=iris_mat.node_tree.nodes.new('ShaderNodeAttribute');node.attribute_name='C6IrisTone';iris_mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.20;bs.inputs['Coat Weight'].default_value=.20
# Trim only tips behind the ocular area. Keep every root, curve, rest attribute and UV.
pts=coords(hair).reshape(-1,4,3);roots=pts[:,0,:];factor=np.ones(len(roots),np.float32)
for e in specs:
 r=np.sqrt(((roots[:,0]-e['center_x'])/e['white_rx'])**2+((roots[:,2]-e['center_z'])/e['white_rz'])**2);candidate=np.flatnonzero(r<1.08)
 for i in candidate:
  if abs(float(roots[i,1])-fy(roots[i,0],roots[i,2]))<.035:
   t=np.clip((r[i]-.88)/.20,0,1);factor[i]=min(factor[i],.25+.75*t*t*(3-2*t))
pts[:]=roots[:,None,:]+(pts-roots[:,None,:])*factor[:,None,None];hair.data.position_data.foreach_set('vector',pts.astype(np.float32).ravel());assert np.array_equal(hair_before.reshape(-1,4,3)[:,0,:],pts[:,0,:]);assert dh(coords(body))==body_hash
for o in s.objects:
 if o.name in stable and o!=hair:assert dh(coords(o))==stable[o.name],o.name
# Check the actual retained root binding, not just hair counts.
source=(root/'design/character-sculpt-v2/d0-groom-binding.py').read_text();start=source.index('def native_uv_validity(');end=source.index('\ndef main():',start);scope={'bpy':bpy,'np':np};exec(source[start:end],scope);valid=scope['native_uv_validity'](body,hair);assert len(valid)==180000 and valid.all();rest_after=rest_before.copy();hair.data.attributes['miao_rest_position'].data.foreach_get('vector',rest_after);assert dh(rest_after)==rest_hash
s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100;s.cycles.samples=a.samples;s.cycles.seed=17;s.cycles.use_animated_seed=False
s.render.filepath='//renders/eye-inset.png';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-eye-inset-static.blend'),compress=True)
# Neutral gray preserves material boundaries for the actual B-stage reviewers.
def gray(name,value):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(value,value,value,1);b.inputs['Roughness'].default_value=.65;return m
neutral={k:gray('C6 gray '+k,x) for k,x in [('body',.40),('white',.72),('dark',.045),('wood',.30),('metal',.6)]}
for ob in s.objects:
 if ob.type not in {'MESH','CURVES','CURVE'} or ob.hide_render or ob.name.startswith(('Studio /','Authoring /','D0 /')):continue
 key='white' if ob.name.startswith('C6 / sclera') else 'dark' if ob.name.startswith('C6 / iris') or ob.name.startswith('Face /') and 'lid' not in ob.name else 'metal' if ob.name.startswith('Guitar / string') or 'silver fret' in ob.name else 'wood' if ob.name.startswith('Guitar /') else 'body'
 ob.data.materials.clear();ob.data.materials.append(neutral[key])
s.render.filepath=str(out/'gray-front.png');bpy.ops.render.render(write_still=True)
cam=s.camera;target=Vector((.18,0,1.72));cam.location=(6,-9,3.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'gray-three-quarter.png');bpy.ops.render.render(write_still=True)
receipt={'stage':'C6-eye-anatomy-gray-unreviewed','input_sha256':sha(src),'source_sha256':sha(__file__),'eye_specs':specs,'front_depths':fronts,'body_geometry_unchanged':dh(coords(body))==body_hash,'groom':{'curve_count':len(roots),'root_positions_unchanged':True,'native_uv_valid':int(valid.sum()),'native_uv_invalid':int((~valid).sum()),'miao_rest_sha256_unchanged':rest_hash,'ocular_curves_tip_trimmed':int((factor<1).sum()),'maximum_tip_displacement':float(np.linalg.norm(coords(hair)-hair_before,axis=1).max()),'no_curves_deleted':True},'limits':['New static eye anatomy only; no blink rig or animation in this candidate.','Gray-stage independent identity/craft/motion reviews pending.','Native groom UV root positions unchanged, but new ocular trimming requires local visual review.','No production assets or published source frame altered.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
