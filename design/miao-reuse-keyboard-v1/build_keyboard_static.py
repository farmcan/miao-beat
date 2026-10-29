"""One native-joint static keyboard candidate. probe is unsaved numerical inspection.
No source mesh edits, bone scaling, actions, animation, or broad parameter search.
"""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];O=R/'artifacts/miao-reuse-keyboard-v1';S=R/'artifacts/miao-reuse-v1/source-rest-baseline/source-rest-native36.blend';P=R/'artifacts/licensed-keyboard-alternative-2026-10-30/innerscene-key-forty/piano-midi-keyboard.glb'
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'probe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={str(p):sha(p) for p in [S,P]};assert bpy.app.version[:2]==(3,6)
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['RIG-Cat'];hand=bpy.data.objects['GEO-hands'];actions_before=len(bpy.data.actions)
def update():bpy.context.view_layer.update()
def geometry(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];t=[tuple(t.vertices) for t in m.loop_triangles];w=[{g.group:g.weight for g in v.groups} for v in m.vertices];ev.to_mesh_clear();return p,t,w
def bbox(points):return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
def frame(y,palm):
 y=y.normalized();x=(palm-y*palm.dot(y)).normalized();z=x.cross(y).normalized();x=y.cross(z).normalized();return Matrix((x,y,z)).transposed()
update();sourceH={s:(rig.matrix_world@rig.pose.bones['ORG-Hand.'+s].matrix).copy() for s in ['L','R']};sourceC={s:(rig.matrix_world@rig.pose.bones['IK-MSTR-Hand.'+s].matrix).copy() for s in ['L','R']}
sourcepalm={s:(rig.matrix_world@rig.pose.bones['FK-Middle2.'+s].matrix).to_3x3().col[2].normalized() for s in ['L','R']}
for side,word in [('L','left'),('R','right')]:
 prop=rig.pose.bones['PRP-UpperArm.'+side];prop['ik_'+word+'_upperarm']=1.;prop['ik_stretch_'+word+'_upperarm']=0.;prop['auto_rubber_hose_'+word+'_upperarm']=0.
 # Index alone curls around its own native +X. Other long fingers remain source-relaxed.
 for stem,angle in [('FK-Index1.',18),('FK-Index2.',27)]:
  bone=rig.pose.bones[stem+side];bone.rotation_mode='XYZ';bone.rotation_euler.x=math.radians(angle)
update();old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P));props=[o for o in bpy.data.objects if o not in old and o.type=='MESH'];canon={o.name:o.matrix_world.copy() for o in props}
G=Matrix.Rotation(math.pi,4,'Z');G.translation=Vector((-.03325,-.405,.270))
for o in props:o.matrix_world=G@canon[o.name]
update()
frames={};targets={};wrists={}
def put_hand(side,F):
 control=F@sourceH[side].inverted()@sourceC[side];rig.pose.bones['IK-MSTR-Hand.'+side].matrix=rig.matrix_world.inverted()@control;update()
 shoulder=rig.matrix_world@rig.pose.bones['ORG-UpperArm.'+side].head;d=(F.translation-shoulder);distance=d.length;direction=d.normalized();a=rig.pose.bones['ORG-UpperArm.'+side].bone.length;b=rig.pose.bones['ORG-Forearm.'+side].bone.length
 along=(a*a-b*b+min(distance,a+b-.0001)**2)/(2*min(distance,a+b-.0001));hint=Vector((1 if side=='L' else -1,.12,-.75));hint=(hint-direction*hint.dot(direction)).normalized();elbow=shoulder+direction*along+hint*math.sqrt(max(0,a*a-along*along));pb=rig.pose.bones['IK-POLE-UpperArm.'+side];pm=rig.matrix_world@pb.matrix;pm.translation=elbow+hint*.16;pb.matrix=rig.matrix_world.inverted()@pm;update()
def pad(side):
 p,t,w=geometry(hand);gi=hand.vertex_groups['DEF-Index2.'+side].index;ids=[i for i,v in enumerate(w) if v.get(gi,0)>.6];assert ids;lowest=min(ids,key=lambda i:p[i].z);return p,t,w,ids,lowest
for side,sign in [('L',1),('R',-1)]:
 # Native palmar direction is calibrated from source, rather than assuming Hand+Z.
 rotation=frame(Vector((0,-1,0)),Vector((0,0,-1)))@frame(sourceH[side].to_3x3().col[1],sourcepalm[side]).inverted()@sourceH[side].to_3x3()
 F=rotation.to_4x4();F.translation=Vector((sign*.105,-.205,.370));put_hand(side,F)
 name='Ivory piano key.014' if side=='L' else 'Ivory piano key.021';key=next(o for o in props if o.name==name);kp,kt,kw=geometry(key);bb=bbox(kp)
 target=Vector(((bb['min'][0]+bb['max'][0])/2,-.320,bb['max'][2]+.002));targets[side]={'key':name,'skin_target':list(target)}
 p,t,w,ids,i=pad(side);F.translation+=target-p[i];put_hand(side,F);frames[side]=F.copy();wrists[side]=list(F.translation)
# Exact finite triangle BVHs; no same infinite plane mask.
records=[]
for o in props:
 p,t,_=geometry(o);records.append({'name':o.name,'p':p,'t':t,'bbox':bbox(p),'tree':BVHTree.FromPolygons(p,t,all_triangles=True)})
def overlap_bbox(a,b):return all(a['max'][i]>=b['min'][i] and b['max'][i]>=a['min'][i] for i in range(3))
def intersections(p,t):
 bb=bbox(p);tree=BVHTree.FromPolygons(p,t,all_triangles=True);pairs={}
 for r in records:
  if overlap_bbox(bb,r['bbox']):
   hit=tree.overlap(r['tree'])
   if hit:pairs[r['name']]=len(hit)
 return pairs
report={'status':'NUMERICAL_PROBE_ONLY' if mode=='probe' else 'GRAY_PENDING_REVIEW','inputs':inputs,'blender':bpy.app.version_string,'one_candidate':'source KeyForty scale=1; rotate Z180 so white front faces cat; centre original14-21; fixed G','keyboard_matrix':[list(v) for v in G],'keyboard_white_pitch_m':.016375,'skin_targets':targets,'wrists':wrists,'hands':{},'cat_collisions':{},'actions_before':actions_before,'new_actions':len(bpy.data.actions)-actions_before,'upstream_geometry_modified':False,'source_scripts_executed':[]}
p,t,w=geometry(hand)
for side in ['L','R']:
 sidegroups={g.index for g in hand.vertex_groups if g.name.endswith('.'+side)};ids={i for i,v in enumerate(w) if sum(ww for g,ww in v.items() if g in sidegroups)>.5};tri=[tr for tr in t if all(i in ids for i in tr)];_,_,_,padids,low=pad(side)
 nearest=[]
 for rec in records:
  near=min(rec['tree'].find_nearest(p[i])[3] for i in padids);nearest.append({'object':rec['name'],'distance_m':near})
 nearest.sort(key=lambda v:v['distance_m']);shoulder=rig.matrix_world@rig.pose.bones['ORG-UpperArm.'+side].head;wrist=rig.matrix_world@rig.pose.bones['ORG-Hand.'+side].head;a=rig.pose.bones['ORG-UpperArm.'+side].bone.length;b=rig.pose.bones['ORG-Forearm.'+side].bone.length
 # Ray each actual pad vertex onto finite component tops. No projected global half-space.
 clear={}
 for rec in records:
  if not rec['name'].startswith(('Ivory piano key','Raised black piano key')):continue
  samples=[]
  for i in padids:
   hit,_,_,_=rec['tree'].ray_cast(Vector((p[i].x,p[i].y,2)),Vector((0,0,-1)),3)
   if hit is not None:samples.append(p[i].z-hit.z)
  if samples:clear[rec['name']]={'projected_pad_vertices':len(samples),'minimum_vertical_gap_m':min(samples)}
 report['hands'][side]={'actual_wrist':list(wrist),'wrist_target_error_m':(wrist-frames[side].translation).length,'shoulder':list(shoulder),'arm_original_length_sum_m':a+b,'wrist_reach_ratio':(wrist-shoulder).length/(a+b),'upperarm_evaluated_length_m':rig.pose.bones['ORG-UpperArm.'+side].length,'forearm_evaluated_length_m':rig.pose.bones['ORG-Forearm.'+side].length,'pad_skin_vertex_count':len(padids),'pad_lowest_vertex':low,'pad_lowest_world':list(p[low]),'pad_nearest_finite_surfaces':nearest[:5],'pad_projected_key_clearances':clear,'actual_hand_triangle_collision_pairs':intersections(p,tri)}
for name in ['GEO-body','GEO-head','GEO-feet','GEO-arms','GEO-legs']:
 obj=bpy.data.objects.get(name)
 if obj and obj.type=='MESH':
  cp,ct,_=geometry(obj);report['cat_collisions'][name]=intersections(cp,ct)
report['source_hashes_after']={str(p):sha(p) for p in [S,P]};assert report['source_hashes_after']==inputs;assert report['new_actions']==0
(O/('probe-receipt.json' if mode=='probe' else 'gray-static-receipt.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
if mode=='probe':raise SystemExit(0)
# Rendering intentionally added only after independent prop craft approval.
# Gray gate = native material rendering desaturated by native 3.6 compositor.
# Underlying mature materials/eye graphs remain intact for the later same-pose default-color gate.
sc.use_nodes=True;nt=sc.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');gray=nt.nodes.new('CompositorNodeRGBToBW');composite=nt.nodes.new('CompositorNodeComposite');nt.links.new(rl.outputs['Image'],gray.inputs['Image']);nt.links.new(gray.outputs[0],composite.inputs['Image'])
sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=96;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
cam=sc.camera;cam.data.type='ORTHO';helper=bpy.data.objects['HLP-scene_camera_dummy']
for driver in helper.animation_data.drivers:
 if driver.data_path=='rotation_euler':driver.mute=True
helper.rotation_mode='XYZ'
def posehash():return hashlib.sha256(json.dumps([(b.name,[list(v) for v in b.matrix_basis]) for b in rig.pose.bones]).encode()).hexdigest()
pose=posehash();dest=O/'gray-static';dest.mkdir(parents=True,exist_ok=True);renders=[]
views=[('front',(0,-3,1.50),(0,-.13,.53),1.38,(1400,1400)),('three-quarter',(.95,-2.5,1.3),(0,-.13,.53),1.38,(1400,1400)),('face',(.30,-2.0,1.13),(0,-.08,.79),.74,(1100,1100)),('left-hand',(.40,-.85,.83),(.08,-.28,.35),.32,(1200,1000)),('right-hand',(-.40,-.85,.83),(-.08,-.28,.35),.32,(1200,1000)),('hands-top',(0,-.35,1.25),(0,-.30,.33),.48,(1400,1000))]
for name,location,target,scale,res in views:
 cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;sc.render.resolution_x,sc.render.resolution_y=res;update();expected=cam.matrix_world.to_euler();helper.rotation_euler=expected;helper.update_tag(refresh={'OBJECT'});update();assert max(abs(helper.rotation_euler[i]-expected[i]) for i in range(3))<1e-6
 sc.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True);assert posehash()==pose;renders.append(sc.render.filepath)
sc.render.filepath=str(dest/'front.png');sc.camera.location=views[0][1];sc.camera.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera.data.ortho_scale=views[0][3];update();helper.rotation_euler=cam.matrix_world.to_euler();update()
for image in bpy.data.images:
 if image.type=='IMAGE' and not image.packed_file:
  try:image.pack()
  except RuntimeError:pass
bpy.ops.wm.save_as_mainfile(filepath=str(dest/'keyboard-gray-native36.blend'))
report['renders']=renders;report['pose_sha256']=pose;report['gray_method']='Native compositor RGBToBW; source material graphs retained, later default-color gate bypasses grayscale only';report['native']=str(dest/'keyboard-gray-native36.blend');report['native_sha256']=sha(dest/'keyboard-gray-native36.blend');report['new_actions']=len(bpy.data.actions)-actions_before;assert report['new_actions']==0
(O/'gray-static-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('GRAY_GATE_READY',json.dumps({'native':report['native'],'renders':renders,'pose':pose,'new_actions':report['new_actions']}))
