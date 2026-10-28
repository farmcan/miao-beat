"""D0.3 bounded real 3D lid-shape study; no eye scaling, hiding or image overlays."""
import argparse,bpy,hashlib,json,math,sys,time,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--clip',action='store_true');p.add_argument('--output',default='artifacts/character-sculpt-d0-blink');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.output;out.mkdir(parents=True,exist_ok=True);src=root/'artifacts/character-sculpt-d0-groom/baseline-attached.blend';master=root/'design/character-sculpt-v2/miao-plush-static-study.blend'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(np.asarray(v).tobytes()).hexdigest()
def pos(o,e=False):
 o=o.evaluated_get(bpy.context.evaluated_depsgraph_get()) if e else o;c=o.data.vertices if o.type=='MESH' else o.data.position_data;v=np.empty(len(c)*3,np.float32);c.foreach_get('co' if o.type=='MESH' else 'vector',v);return v.reshape(-1,3)
def rest(o,e=False):
 o=o.evaluated_get(bpy.context.evaluated_depsgraph_get()) if e else o;v=np.empty(len(o.data.attributes['miao_rest_position'].data)*3,np.float32);o.data.attributes['miao_rest_position'].data.foreach_get('vector',v);return digest(v)
receipt={'stage':'D0.3 actual 3D upper-lid shape study','input_sha256':sha(src),'C5_master_sha256':sha(master),'source_sha256':sha(__file__),'started_unix':time.time(),'renders':[],'blender':bpy.app.version_string}
def save(): (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def stage(s):receipt['status']=s;save();print('D0_BLINK_STAGE',s,flush=True)
def main():
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];lids=sorted([o for o in bpy.data.objects if o.name.startswith('Face / integrated upper eyelid')],key=lambda o:float(pos(o)[:,0].mean()));eyes=sorted([o for o in bpy.data.objects if o.name.startswith('Face / ivory eye')],key=lambda o:o.location.x);irises=sorted([o for o in bpy.data.objects if o.name.startswith('Face / sideward iris')],key=lambda o:o.location.x)
 initial={o.name:{'positions':digest(pos(o)), 'rest':rest(o) if o.data.attributes.get('miao_rest_position') else None} for o in [body,hair]+lids};receipt['before']=initial
 stable={o.name:digest(pos(o)) for o in bpy.data.objects if o.type in {'MESH','CURVES'} and o not in lids}
 with bpy.data.libraries.load(str(master),link=False) as (data,to):to.objects=[n for n in data.objects if n.startswith('Face / integrated upper eyelid')]
 cages=sorted(to.objects,key=lambda o:float(pos(o)[:,0].mean()));receipt['lids']=[];control=bpy.data.objects.new('D0 / Blink control',None);s.collection.objects.link(control);control['Blink']=0.;control.id_properties_ui('Blink').update(min=0.,max=1.,description='Both real upper eyelids: 0 open, 1 closed. Narrow D0 study only.')
 for lid,cage,eye,iris in zip(lids,cages,eyes,irises):
  s.collection.objects.link(cage);assert len(cage.data.vertices)==245
  for name,values in [('d0_lid_r',np.repeat(np.arange(5)/4,49)),('d0_lid_angle',np.tile(np.linspace(.04*np.pi,.96*np.pi,49),5))]:
   at=cage.data.attributes.new(name,'FLOAT','POINT');at.data.foreach_set('value',values.astype(np.float32))
  bpy.context.view_layer.update();ev=cage.evaluated_get(bpy.context.evaluated_depsgraph_get());open_points=pos(lid).copy();cage_points=pos(cage,True);assert cage_points.shape==open_points.shape;difference=float(np.max(np.abs(cage_points-open_points)));assert difference<1e-6
  r=np.empty(len(open_points),np.float32);an=r.copy();ev.data.attributes['d0_lid_r'].data.foreach_get('value',r);ev.data.attributes['d0_lid_angle'].data.foreach_get('value',an);bpy.data.objects.remove(cage,do_unlink=True)
  # Frozen open mesh stays byte-identical. Parameters originate from evaluated C5 cage.
  ex,ey,ez=eye.location;ix,iy,iz=iris.location;face=BVHTree.FromObject(body,dg);base=lid.shape_key_add(name='Basis');record={'name':lid.name,'open_cage_max_coordinate_error':difference,'vertices':len(open_points),'samples':[]}
  for j in range(1,9):
   blink=j/8.;pts=open_points.copy();innerx=ex+(.117*(1-blink)+.126*blink)*np.cos(an);innerz=ez+(.099*(1-blink)-.015*blink)*np.sin(an)-.005*blink
   # Outer rim stays exactly at its C5 face junction; intermediate skin expands down.
   outerx=ex+.142*np.cos(an);outerz=ez+.121*np.sin(an)
   # Param reconstruction only supplies displacement, preserving actual Catmull-Clark open.
   oldx=ex+(.117+.025*r)*np.cos(an);oldz=ez+(.099+.022*r)*np.sin(an)
   pts[:,0]+=(1-r)*(innerx-(ex+.117*np.cos(an)));pts[:,2]+=(1-r)*(innerz-(ez+.099*np.sin(an)))
   for k,(x,y,z) in enumerate(pts):
    hit=face.ray_cast(Vector((float(x),-3,float(z))),Vector((0,1,0)),6)[0];fy=hit.y if hit else float(y)
    front=fy-.001
    # Actual analytic eye ellipsoids, inflated by .003 for a rounded skin clearance.
    for cx,cy,cz,rx,ry,rz in [(ex,ey,ez,.123,.056,.108),(ix,iy,iz,.063,.024,.069)]:
     q=((x-cx)/rx)**2+((z-cz)/rz)**2
     if q<1:front=min(front,float(cy-ry*math.sqrt(1-q)-.0045))
    # The fixed outside edge is the existing face junction. Across the lid interior
    # follow the complete front envelope (including the proud iris), never the globe center.
    blend=min(1.,blink*8)*min(1.,(1-float(r[k]))*100)
    pts[k,1]=float(y)*(1-blend)+front*blend
   key=lid.shape_key_add(name='Blink %03d'%round(blink*100));key.data.foreach_set('co',pts.ravel());key.slider_min=0;key.slider_max=1
   dr=key.driver_add('value').driver;dr.type='SCRIPTED';v=dr.variables.new();v.name='blink';v.targets[0].id=control;v.targets[0].data_path='["Blink"]';dr.expression='max(0, 1-abs(blink-%.3f)*8)'%blink
   record['samples'].append({'blink':blink,'sha256':digest(pts),'max_displacement':float(np.linalg.norm(pts-open_points,axis=1).max())})
  # Actual lower skin shell: at rest it is inside the existing face; at closure
  # it rises from below and meets the upper lid, avoiding one full orange globe cap.
  N=49;R=9;aa=np.tile(np.linspace(.04*np.pi,.96*np.pi,N),R);rr=np.repeat(np.linspace(0,1,R),N)
  xx=ex+(.126+.054*rr)*np.cos(aa);zz=ez-(.014*(1-rr)+.150*rr)*np.sin(aa)-.003*(1-rr)
  lowerbase=np.column_stack((xx,np.zeros(len(xx)),zz)).astype(np.float32)
  for k,(x,y,z) in enumerate(lowerbase):
   hit=face.ray_cast(Vector((float(x),-3,float(z))),Vector((0,1,0)),6)[0];lowerbase[k,1]=(hit.y if hit else ey)+.009
  fs=[]
  for row in range(R-1):
   for col in range(N-1):u=row*N+col;fs.append((u,u+N,u+N+1,u+1))
  me=bpy.data.meshes.new('D0 / lower lid skin');me.from_pydata(lowerbase.tolist(),[],fs);me.materials.append(lid.data.materials[0]);lower=bpy.data.objects.new('Face / D0 lower eyelid '+lid.name[-3:],me);s.collection.objects.link(lower)
  for poly in me.polygons:poly.use_smooth=True
  attr=me.attributes.new('miao_rest_position','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',lowerbase.ravel());lower.shape_key_add(name='Basis')
  for j in range(1,9):
   blink=j/8.;pts=lowerbase.copy()
   for k,(x,y,z) in enumerate(pts):
    hit=face.ray_cast(Vector((float(x),-3,float(z))),Vector((0,1,0)),6)[0];fy=hit.y if hit else float(y);front=fy-.001
    for cx,cy,cz,rx,ry,rz in [(ex,ey,ez,.123,.056,.108),(ix,iy,iz,.063,.024,.069)]:
     q=((x-cx)/rx)**2+((z-cz)/rz)**2
     if q<1:front=min(front,float(cy-ry*math.sqrt(1-q)-.0045))
    # Lower lid raises late, when the upper margin is approaching the iris.
    amount=max(0,min(1,(blink-.25)/.75));pts[k,1]=float(y)+(front-float(y))*amount*min(1,(1-rr[k])*40)
   key=lower.shape_key_add(name='Blink %03d'%round(blink*100));key.data.foreach_set('co',pts.ravel());dr=key.driver_add('value').driver;dr.type='SCRIPTED';v=dr.variables.new();v.name='blink';v.targets[0].id=control;v.targets[0].data_path='["Blink"]';dr.expression='max(0, 1-abs(blink-%.3f)*8)'%blink
  record['lower_skin']={'vertices':len(lowerbase),'rests_inside_face':True,'face_junction_unchanged':True}
  receipt['lids'].append(record)
 # Native UV validity checker copied from the actual D0.2 accepted technical source.
 source=(root/'design/character-sculpt-v2/d0-groom-binding.py').read_text();start=source.index('def native_uv_validity(');end=source.index('\ndef main():',start);scope={'bpy':bpy,'np':np};exec(source[start:end],scope);valid=scope['native_uv_validity'](body,hair);assert valid.all() and len(valid)==180000
 receipt['groom']={'curves':len(hair.data.curves),'points':len(hair.data.position_data),'native_uv_valid':int(valid.sum()),'native_uv_invalid':int((~valid).sum()),'rest_sha256':rest(hair,True),'rest_unchanged':rest(hair,True)==initial[hair.name]['rest']};assert receipt['groom']['rest_unchanged']
 for o in bpy.data.objects:
  if o.name in stable:assert digest(pos(o))==stable[o.name],o.name+' modified'
 receipt['body_hands_guitar_eyes_iris_geometry_unchanged']=True
 s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.cycles.seed=17;s.cycles.samples=32;s.cycles.use_animated_seed=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.fps=24
 stage('three-real-keyposes')
 for tag,value in [('open',0.),('half',.5),('closed',1.)]:
  control['Blink']=value;control.update_tag();bpy.context.view_layer.update();s.render.filepath=str(out/(tag+'.png'));t=time.time();bpy.ops.render.render(write_still=True);receipt['renders'].append({'tag':tag,'value':value,'seconds':time.time()-t,'sha256':sha(out/(tag+'.png'))});save()
 control['Blink']=0.;control.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-d0-blink-study.blend'),compress=True)
 receipt['limitations']=['True 3D upper-lid shape study only, not a full facial rig.','Open/half/closed images require independent visual review.','No natural strum, head, retopology, browser or export acceptance.','No body-eye-socket topology fusion; lid outside rim retains prior C5 junction.','Micro hair shader sampling still lacks a separate AOV proof.'];receipt['elapsed_seconds']=time.time()-receipt['started_unix'];receipt['input_unchanged']=sha(src)==receipt['input_sha256'];receipt['C5_master_unchanged']=sha(master)==receipt['C5_master_sha256'];stage('keyposes_complete_pending_visual_inspection')
def clip():
 global receipt
 receipt=json.loads((out/'receipt.json').read_text())
 if not receipt.get('keypose_gate_passed',False):raise RuntimeError('This bounded candidate failed keypose closure/appearance. Clip generation is blocked; see final-receipt.json and README.')
 receipt['clip_source_sha256']=sha(__file__);bpy.ops.wm.open_mainfile(filepath=str(out/'miao-d0-blink-study.blend'));s=bpy.context.scene;control=bpy.data.objects['D0 / Blink control'];frames=out/'frames';frames.mkdir(exist_ok=True);s.frame_start=1;s.frame_end=48;s.render.fps=24
 timing=[(1,0.),(14,0.),(15,.1),(16,.4),(17,.8),(18,1.),(19,1.),(20,.9),(21,.65),(22,.4),(23,.2),(24,.07),(25,0.),(48,0.)]
 for frame,value in timing:control['Blink']=value;control.keyframe_insert(data_path='["Blink"]',frame=frame)
 # Fully specify f-curve interpolation; no compositor animation or image-space eyes.
 action=control.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for kp in curve.keyframe_points:kp.interpolation='LINEAR'
 receipt['clip']={'frames':48,'fps':24,'seconds':2.,'timing':timing,'new_full_scene_renders':[],'held_frames':'Copy complete full-scene open/closed rendered frames; no body/eye compositing.'};stage('short-full-scene-clip-rendering')
 for frame,value in timing:
  if frame in [1,14,18,19,25,48]:continue
  s.frame_set(frame);s.render.filepath=str(frames/('%04d.png'%frame));t=time.time();bpy.ops.render.render(write_still=True);receipt['clip']['new_full_scene_renders'].append({'frame':frame,'blink':value,'seconds':time.time()-t,'sha256':sha(s.render.filepath)});save()
 import shutil
 for frame in range(1,49):
  target=frames/('%04d.png'%frame)
  if target.exists():continue
  source=out/('closed.png' if frame in [18,19] else 'open.png');shutil.copyfile(source,target)
 s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-d0-blink-study.blend'),compress=True);receipt['clip']['all_frame_hashes']={p.name:sha(p) for p in sorted(frames.glob('*.png'))};receipt['total_gpu_renders_including_failed_visual_attempts']=14+len(receipt['clip']['new_full_scene_renders']);stage('short-clip-full-scene-frames-complete-pending-encode-and-independent-review')
try:
 if a.clip:clip()
 else:main()
except Exception as e:receipt['error']=repr(e);receipt['traceback']=traceback.format_exc();stage('failed');print(receipt['traceback'],flush=True);raise
