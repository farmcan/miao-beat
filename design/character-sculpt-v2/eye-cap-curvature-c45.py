"""C45 restore only original cap curvature above C38 embedded sclera. No art pass implied."""
import bpy,bmesh,numpy as np,hashlib,json,math,sys,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/character-eye-cap-c45');parser.add_argument('--contact-clearance',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);OUT=ROOT/args.out;SRC=ROOT/'artifacts/character-eye-lighting-c43/controlled-ab/A-original-routing.blend';OLD=ROOT/'artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def points(o):
 p=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',p);p=p.reshape(-1,3);m=np.asarray(o.matrix_world);return p@m[:3,:3].T+m[:3,3]
def sett(o,p):
 m=np.asarray(o.matrix_world);local=(p-m[:3,3])@np.linalg.inv(m[:3,:3]).T;o.data.vertices.foreach_set('co',local.astype(np.float32).ravel());o.data.update()
def tree(o):
 p=points(o);o.data.calc_loop_triangles();return BVHTree.FromPolygons([Vector(v) for v in p],[t.vertices[:] for t in o.data.loop_triangles],all_triangles=True)
def unyaw(p):
 q=p.copy();c=math.cos(math.radians(7.5));t=math.sin(math.radians(7.5));x=p[:,0]-.040;y=p[:,1]-.03;q[:,0]=c*x+t*y;q[:,1]=.03-t*x+c*y;return q

def yaw(p):
 q=p.copy();c=math.cos(math.radians(7.5));t=math.sin(math.radians(7.5));x=p[:,0];y=p[:,1]-.03;q[:,0]=c*x-t*y+.040;q[:,1]=.03+t*x+c*y;return q

def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'preflight.json').exists(),'Preserve frozen result'
 bpy.ops.wm.open_mainfile(filepath=str(OLD));old={side:points(bpy.data.objects['C7 / clear cornea '+side]) for side in ['L','R']}
 bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;allmesh={o.name:hashlib.sha256(points(o).tobytes()).hexdigest() for o in s.objects if o.type=='MESH'}
 r={'scope':'C45 only cap curvature restoration; current C38 white/lids/iris/head/lighting unchanged','source':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC)},'curvature_source':{'path':str(OLD.relative_to(ROOT)),'sha256':sha(OLD)},'eyes':[],'geometry_gate_passed':False,'art_gate_passed':False,'production_changed':False}
 forward=Vector((-math.sin(math.radians(7.5)),math.cos(math.radians(7.5)),0));failed=[]
 for side in ['L','R']:
  ob=bpy.data.objects['C7 / clear cornea '+side];P=old[side];Q=unyaw(points(ob));n=len(P)//2;N=96;R=24;assert n==1+N*R and np.max(abs(P[:,[0,2]]-Q[:,[0,2]]))<2e-6
  rim=np.arange(n+1+(R-1)*N,n+1+R*N);X=np.column_stack((P[:,0],P[:,2],np.ones(len(P))));sourceplane=np.linalg.lstsq(X[rim],P[rim,1],rcond=None)[0];targetplane=np.linalg.lstsq(X[rim],Q[rim,1],rcond=None)[0]
  candidate=P.copy();candidate[:,1]+=X@(targetplane-sourceplane);candidate=yaw(candidate);before=points(ob);clearance_lift=0.0
  if args.contact_clearance:
   gaps=[]
   for name in ['C6 / iris '+side,'C6 / sclera '+side]:
    layer_tree=tree(bpy.data.objects[name])
    for v in candidate:
     h=layer_tree.ray_cast(Vector(v)-forward*3,forward,6)[0];assert h is not None;gaps.append(float((h-Vector(v)).dot(forward)))
   clearance_lift=max(0.0,4e-5-min(gaps));assert clearance_lift<.002,'Excessive cap detach';candidate-=np.asarray(forward)*clearance_lift
  sett(ob,candidate);bpy.context.view_layer.update();actual=points(ob)
  bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update();vol=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);selfpairs=A._self_intersections(bm);bm.free()
  cap=tree(ob);checks=[]
  for name in ['C6 / iris '+side,'C6 / sclera '+side,'Miao / continuous pear and rounded-square face']:
   other=tree(bpy.data.objects[name]);hits=cap.overlap(other);gaps=[];miss=[]
   for index,v in enumerate(actual):
    origin=Vector(v)-forward*3;hit=other.ray_cast(origin,forward,6)[0]
    if hit is None:miss.append(index)
    else:gaps.append(float((hit-Vector(v)).dot(forward)))
   checks.append({'object':name,'triangle_overlap_pairs':len(hits),'ray_hit_count':len(gaps),'ray_misses':len(miss),'min_cap_in_front_distance':min(gaps) if gaps else None,'max_cap_in_front_distance':max(gaps) if gaps else None})
   if hits or miss or min(gaps)<=1e-6:failed.append({'side':side,'object':name,'reason':'intersection/missed-layer/or nonpositive front clearance'})
  rec={'side':side,'vertices':len(P),'cap_only_max_displacement_u':float(np.linalg.norm(actual-before,axis=1).max()),'source_cap_relative_rim_original_depth_restored':True,'source_to_candidate_affine_shear_determinant':1.0,'actual_layer_clearance_forward_translation_u':clearance_lift,'source_rim_plane':sourceplane.tolist(),'target_rim_plane':targetplane.tolist(),'volume':vol,'nonmanifold_edges':nonmanifold,'self_intersections':selfpairs,'actual_layer_checks':checks};r['eyes'].append(rec)
  if vol<=0 or nonmanifold or selfpairs:failed.append({'side':side,'reason':'cap geometry invalid'})
 current={o.name:hashlib.sha256(points(o).tobytes()).hexdigest() for o in s.objects if o.type=='MESH'};othernames=[k for k in allmesh if not k.startswith('C7 / clear cornea')];r['all_other_mesh_positions_exact']=all(current[k]==allmesh[k] for k in othernames);assert r['all_other_mesh_positions_exact'];r['failures']=failed;r['geometry_gate_passed']=not failed;r['script_sha256']=sha(__file__)
 (OUT/'preflight.json').write_text(json.dumps(r,indent=2)+'\n')
 if failed:print('RESULT '+json.dumps({'geometry_gate_passed':False,'failures':failed}),flush=True);return
 s.cycles.samples=128;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False;bpy.context.preferences.filepaths.save_version=0
 native=OUT/'miao-c45-cap-curvature.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native);cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale;r['renders']=[]
 for view in ['full','face']:
  if view=='face':cam.location=Vector((0,-6,3.05));cam.rotation_euler=(Vector((0,0,3.03))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.7
  else:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
  bpy.context.view_layer.update();file=OUT/('c45-'+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);r['renders'].append({'file':file.name,'sha256':sha(file),'camera_matrix':list(map(list,cam.matrix_world)),'ortho_scale':cam.data.ortho_scale})
 (OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps({'geometry_gate_passed':True,'renders':2}),flush=True)
main()
