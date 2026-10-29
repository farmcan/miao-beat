"""Compute one proposed transform and contact targets; do not transform or save scene objects."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve();cat=json.loads(Path(args[2]).read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src),merge_vertices=True)
o=next(o for o in bpy.context.scene.objects if o.type=='MESH');mesh=o.data;pts=[o.matrix_world@v.co for v in mesh.vertices]
s=.5;theta=math.radians(65);loc=Vector((-.235,-.241,.235));M=Matrix.Translation(loc)@Matrix.Rotation(theta,4,'Y')@Matrix.Diagonal((s,s,s,1))
def bbox(ps):
 mi=[min(p[k] for p in ps) for k in range(3)];ma=[max(p[k] for p in ps) for k in range(3)];return {'min':mi,'max':ma,'dimensions':[ma[k]-mi[k] for k in range(3)]}
adj=[[] for _ in mesh.vertices]
for e in mesh.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();strings=[]
for vi in range(len(mesh.vertices)):
 if vi in seen:continue
 todo=[vi];seen.add(vi);inds=[]
 while todo:
  u=todo.pop();inds.append(u)
  for n in adj[u]:
   if n not in seen:seen.add(n);todo.append(n)
 bb=bbox([pts[i] for i in inds]);ds=bb['dimensions']
 if ds[2]>.8 and ds[0]<.02:strings.append(set(inds))
def string_center_at(z):
 contacts=[]
 for ids in strings:
  xs=[]
  for e in mesh.edges:
   a,b=e.vertices
   if a not in ids or b not in ids:continue
   p,q=pts[a],pts[b]
   if (p.z-z)*(q.z-z)<=0 and abs(p.z-q.z)>1e-9:
    t=(z-p.z)/(q.z-p.z);xs.append(p+(q-p)*t)
  assert xs
  contacts.append(sum(xs,Vector())/len(xs))
 return sum(contacts,Vector())/len(contacts),contacts
right,rs=string_center_at(.30);left,ls=string_center_at(.70);right.y-=.006
rw=M@right;lw=M@left
shoulders={side:Vector(cat['bones'][f'ORG-UpperArm.{side}']['head']) for side in ['L','R']}
reach={side:sum(cat['bones'][f'{n}.{side}']['length'] for n in ['ORG-UpperArm','ORG-Forearm','ORG-Hand']) for side in ['L','R']}
contacts={}
for side,target in [('L',lw),('R',rw)]:
 d=(target-shoulders[side]).length;wrist=target+(shoulders[side]-target).normalized()*.05
 contacts[side]={'role':'neck contact' if side=='L' else 'hover over soundhole strings','target_world':list(target),'shoulder_world':list(shoulders[side]),'shoulder_to_contact_m':d,'arm_plus_hand_length_m':reach[side],'reach_fraction':d/reach[side],'suggested_wrist_world':list(wrist),'shoulder_to_suggested_wrist_m':(wrist-shoulders[side]).length,'arm_only_length_m':reach[side]-cat['bones'][f'ORG-Hand.{side}']['length']}
report={'blender':bpy.app.version_string,'instrument':str(src),'object':o.name,'material':[m.name for m in o.data.materials],'transform':{'scale_xyz':[s,s,s],'euler_xyz_degrees':[0,65,0],'location_m':list(loc),'matrix_world':[list(row) for row in M]},'original_bbox':bbox(pts),'proposed_bbox':bbox([M@p for p in pts]),'proposed_body_bbox':bbox([M@p for p in pts if p.z<.535]),'cat_measurements':str(Path(args[2]).resolve()),'contacts':contacts,'local_landmarks':{'neck_string_centroid_z_070':list(left),'right_hover_z_030':list(right),'six_string_intersections_z_070':[list(p) for p in ls],'six_string_intersections_z_030':[list(p) for p in rs]},'cat_objects_bbox':{k:v['evaluated_bbox'] for k,v in cat['objects'].items()},'limits':['No cat pose, mesh, rig, or source transform was edited.','Targets are a static proposal, not demonstrated contact.','Reach sum is a necessary kinematic check; joint limits, hand roll and silhouette require one actual posed render.','Cat body is curved; global bounding-plane clearance is not body contact evidence.']}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'output':str(out),'proposed_bbox':report['proposed_bbox'],'contacts':contacts}))
