"""C39 read-only source decomposition saved as explicitly unpassed diagnostic."""
import bpy,numpy as np,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];O=R/'artifacts/character-strum-paw-c39';O.mkdir(exist_ok=True);src=R/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();srcsha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;b=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=b.data;P=np.array([v.co[:] for v in me.vertices]);p=np.load(R/'artifacts/character-strum-paw-c37/authored-delta-and-locks.npz');ids=p['edit_ids'];mask=np.zeros(len(P));mask[ids]=p['edit_weight'];edit=mask>0;mapping=np.full(len(P),-1,np.int32);mapping[ids]=np.arange(len(ids));edges=np.array([tuple(e.vertices) for e in me.edges]);edges=edges[edit[edges].any(1)];ii=np.r_[edges[:,0],edges[:,1]];jj=np.r_[edges[:,1],edges[:,0]];keep=edit[ii];ii=ii[keep];jj=jj[keep];count=np.bincount(mapping[ii],minlength=len(ids));ss=(P-p['origin'])@p['palm_axis']
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
Q=P.copy();fw=mask*smooth((ss+.02)/.16)
for k in range(80):
 sums=np.stack([np.bincount(mapping[ii],weights=Q[jj,d],minlength=len(ids)) for d in range(3)],axis=1);Q[ids]+=.35*fw[ids,None]*(sums/count[:,None]-Q[ids])
me.vertices.foreach_set('co',Q.astype(np.float32).ravel());me.update();bpy.context.view_layer.update();me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);fi=np.array([t.polygon_index for t in me.loop_triangles]);right=(P[:,0]<-.20)&(P[:,1]<-.55)&(P[:,2]>1.4)&(P[:,2]<2.25);righttri=np.all(right[tri],1);tr=tri[righttri];tf=fi[righttri];tree=BVHTree.FromPolygons(Q,tr.tolist(),all_triangles=True);collision=[];height=[]
for name in ['Guitar / spruce soundboard','Guitar / rosewood body']+['Guitar / string '+str(i+1) for i in range(6)]:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();co=[ob.matrix_world@v.co for v in m.vertices];gt=[tuple(t.vertices) for t in m.loop_triangles];bt=BVHTree.FromPolygons(co,gt,all_triangles=True);pairs=tree.overlap(bt);v=sorted({int(j) for a,c in pairs for j in tr[a]});collision.append({'object':name,'actual_triangle_pairs':len(pairs),'right_skin_vertex_bbox':[Q[v].min(0).tolist(),Q[v].max(0).tolist()] if v else None,'skin_faces':sorted({int(tf[a]) for a,c in pairs}),'skin_vertex_ids':v});ev.to_mesh_clear()
 if name.endswith('soundboard') or name.endswith('body'):
  for i in np.flatnonzero(right):
   h,n,f,d=bt.ray_cast(Vector((Q[i,0],-3,Q[i,2])),Vector((0,1,0)),5)
   if h is not None and Q[i,1]>h.y-.03:height.append({'object':name,'vertex':int(i),'co':Q[i].tolist(),'actual_front_y':h.y,'required_forward_delta_for_03':float(Q[i,1]-h.y+.03)})
np.savez_compressed(O/'fair-only-coordinates.npz',original=P,fair=Q,right_mask=right,source_ids=np.array([x.value for x in me.attributes['C23 source vertex id'].data]));(O/'fair-only-preinspection.json').write_text(json.dumps({'scope':'Known-unpassed fair-only internal diagnostic; original right forearm wood contact unresolved. Not art or contact pass.','input_sha256':srcsha,'right_region_definition':'x<-.20 y<-.55 z1.4..2.25; diagnostic broad forearm scope, includes retained collar','collisions':collision,'actual_front_surface_ray_violations':height,'max_required_forward_delta_for_03':max((q['required_forward_delta_for_03'] for q in height),default=0)},indent=2)+'\n');bpy.context.preferences.filepaths.save_version=0;native=O/'diagnostic-c39-fair-only-unpassed.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);print('PREFLIGHT '+json.dumps({'collisions':[{k:c[k] for k in ['object','actual_triangle_pairs','right_skin_vertex_bbox']} for c in collision],'max_required_lift':max((q['required_forward_delta_for_03'] for q in height),default=0),'native_sha256':sha(native)}),flush=True)
s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera
for view in ['front','right-paw','right-side']:
 if view=='right-paw':cam.location=(-.65,-12,2.7);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
 if view=='right-side':cam.location=(-4,-6,3.1);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
 s.render.filepath=str(O/('diagnostic-fair-only-gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
assert sha(src)==srcsha
