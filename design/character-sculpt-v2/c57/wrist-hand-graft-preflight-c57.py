"""Read-only C57 same C23 Y=-.72 wrist plane body/old-good-hand loop preflight.
Local BMesh cuts only. No graft, forced merge, deformation or asset overwrite.
"""
import bpy,bmesh,numpy as np,json,hashlib,sys,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-body-voxel-c57';paths={'voxel_body':ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend','old_good_hand':ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend'};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();hashes={k:sha(p) for k,p in paths.items()};h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';s=h.read_text();exec(compile(s[s.index('def smooth'):s.index('def main():')],str(h)+'#pure-helpers','exec'),globals())
def loops(me):
 bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();edges=[e for e in bm.edges if e.is_boundary];adj={}
 for e in edges:a,b=e.verts;adj.setdefault(a.index,[]).append(b.index);adj.setdefault(b.index,[]).append(a.index)
 bad={i:len(v) for i,v in adj.items() if len(v)!=2};result=[];unused=set(adj)
 if not bad:
  while unused:
   start=min(unused);cur=start;prev=None;loop=[]
   for j in range(len(adj)+1):
    if cur==start and loop:break
    loop.append(cur);unused.discard(cur);a,b=adj[cur];nxt=a if a!=prev else b;prev,cur=cur,nxt
   result.append(loop)
 bm.free();return result,bad

def signed_area(p):return .5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
def crossings(p):
 out=[];n=len(p)
 for i in range(n):
  for j in range(i+2,n):
   if i==0 and j==n-1:continue
   a,b=p[i],p[(i+1)%n];c,d=p[j],p[(j+1)%n]
   def orient(a,b,c):q=b-a;r=c-a;return q[0]*r[1]-q[1]*r[0]
   if orient(a,b,c)*orient(a,b,d)<-1e-18 and orient(c,d,a)*orient(c,d,b)<-1e-18:out.append([i,j])
 return out

def selfpairs(me):
 me.calc_loop_triangles();co=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,tri,all_triangles=True);pairs=[]
 for a,b in tree.overlap(tree):
  if a>=b or set(tri[a])&set(tri[b]):continue
  p=np.array([co[i][:] for i in set(tri[a])|set(tri[b])]);pairs.append({'triangles':[a,b],'bbox':[p.min(0).tolist(),p.max(0).tolist()]})
 return pairs

records={};allgtr={};data={}
for tag,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;original=arr(me).copy();allgtr[tag]={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};original_faces=[list(f.vertices) for f in me.polygons];bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();provenance=bm.verts.layers.int.new('C57 original input vertex id');faceprovenance=bm.faces.layers.int.new('C57 original input face id')
 for v in bm.verts:v[provenance]=v.index+1
 for f in bm.faces:f[faceprovenance]=f.index+1
 originals=set(bm.verts);roi=[f for f in bm.faces if .75<f.calc_center_median().x<1.62 and 1.30<f.calc_center_median().z<2.35 and f.calc_center_median().y<-.55];edges={e for f in roi for e in f.edges};verts={v for f in roi for v in f.verts};bmesh.ops.bisect_plane(bm,geom=list(verts)+list(edges)+roi,dist=1e-8,plane_co=(0,-.72,0),plane_no=(0,1,0),clear_inner=False,clear_outer=False)
 for v in bm.verts:
  if v not in originals:
   for layer in bm.verts.layers.int.values():v[layer]=0
 distal=[f for f in bm.faces if .75<f.calc_center_median().x<1.62 and 1.3<f.calc_center_median().z<2.35 and f.calc_center_median().y<-.72-1e-7]
 distalset=set(distal);delete=distal if tag=='voxel_body' else [f for f in bm.faces if f not in distalset];bmesh.ops.delete(bm,geom=delete,context='FACES_ONLY');loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.to_mesh(me);bm.free();me.update();co=arr(me);orig=np.array([v.value for v in me.attributes['C57 original input vertex id'].data]);old=orig>0;exact=bool(np.array_equal(co[old],original[orig[old]-1]));ls,bad=loops(me);rows=[]
 for l in ls:
  p=co[l];xz=p[:,[0,2]]
  if signed_area(xz)<0:l=l[::-1];p=co[l];xz=p[:,[0,2]]
  k=min(range(len(l)),key=lambda j:(p[j,2],p[j,0]));l=l[k:]+l[:k];p=co[l];xz=p[:,[0,2]];rows.append({'count':len(l),'output_vertices':l,'original_input_vertex_ids':orig[l].tolist(),'coordinates':p.tolist(),'XZ_area':float(signed_area(xz)),'planeY_max_error':float(np.max(np.abs(p[:,1]+.72))),'XZ_strict_crossings':crossings(xz),'bbox':[p.min(0).tolist(),p.max(0).tolist()]})
 contacts=[]
 if tag=='old_good_hand':
  original_rows=json.load(open(ROOT/'artifacts/character-paw-grip-c35/receipt.json'))['after_actual_target_rays'];fmap={v.value-1:i for i,v in enumerate(me.attributes['C57 original input face id'].data) if v.value>0}
  for r in original_rows:
   oldface=r['face_index'];fid=fmap.get(oldface);okay=fid is not None and [orig[i]-1 for i in me.polygons[fid].vertices]==original_faces[oldface] if fid is not None else False;contacts.append({'kind':r['kind'],'u':r['u'],'original_C35_face_index':oldface,'contact_world_target':r['actual_target_world'],'face_present_same_cyclic_vertices_exact':bool(okay),'source_C35_gap':r['gap'],'not_new_contact_pass':True})
 sp=selfpairs(me);rec={'source_sha256':hashes[tag],'same_planeY':-.72,'ROI':'C23 actual wrist cut: x.75..1.62,z1.3..2.35,y<-.55; distal sideY<-.72','kept':'proxim/body' if tag=='voxel_body' else 'distal original good C35 contact hand','topology':topo(me),'boundary_loops':rows,'bad_boundary_degrees':bad,'all_original_retained_input_coordinates_exact':exact,'new_plane_points_provenance0':int((~old).sum()),'actual_self_pairs_after_cut':len(sp),'self_pair_geometry':sp,'old_good_contact_face_preservation':contacts};records[tag]=rec;data[tag]={'co':co,'faces':np.array([list(f.vertices) for f in me.polygons],dtype=object),'original_input_vertex_ids':orig};np.savez_compressed(OUT/(tag+'-same-plane-cut.npz'),co=co,original_input_vertex_ids=orig,faces_flat=np.array([i for f in me.polygons for i in f.vertices],np.int32),face_sizes=np.array([len(f.vertices) for f in me.polygons],np.int32));print('CUT '+json.dumps({'tag':tag,'loops':[r['count'] for r in rows],'branches':len(bad),'self':len(sp),'original_exact':exact,'contact_faces_exact':[r['face_present_same_cyclic_vertices_exact'] for r in contacts]}),flush=True)

eligible=all(len(r['boundary_loops'])==1 and not r['bad_boundary_degrees'] and not r['boundary_loops'][0]['XZ_strict_crossings'] and r['all_original_retained_input_coordinates_exact'] for r in records.values());comparison=None
if eligible:
 a=np.array(records['voxel_body']['boundary_loops'][0]['coordinates']);b=np.array(records['old_good_hand']['boundary_loops'][0]['coordinates'])
 def resample(p,n):
  length=np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1);cum=np.r_[0,np.cumsum(length)];t=np.arange(n)/n*cum[-1];k=np.minimum(np.searchsorted(cum,t,side='right')-1,len(p)-1);f=(t-cum[k])/length[k];return p[k]*(1-f[:,None])+p[(k+1)%len(p)]*f[:,None]
 A=resample(a,256);B=resample(b,256);cost=[np.mean(np.linalg.norm(A-np.roll(B,k,axis=0),axis=1)**2) for k in range(256)];phase=int(np.argmin(cost));B=np.roll(B,phase,axis=0);dist=np.linalg.norm(A-B,axis=1)
 def pointline(p,q):
  best=np.full(len(p),1e9)
  for x,y in zip(q,np.roll(q,-1,axis=0)):
   v=y-x;t=np.clip((p-x)@v/(v@v),0,1);best=np.minimum(best,np.linalg.norm(p-(x+t[:,None]*v),axis=1))
  return best
 ha=pointline(a,b);hb=pointline(b,a);comparison={'uniform_arclength_diagnostic_samples':256,'best_cyclic_phase_samples':phase,'cyclic_RMS_u':float(np.sqrt(np.mean(dist**2))),'cyclic_max_u':float(dist.max()),'symmetric_polyline_Hausdorff_u':float(max(ha.max(),hb.max())),'counts':[len(a),len(b)],'count_parity':[len(a)%2,len(b)%2],'area_ratio_voxel_over_old':records['voxel_body']['boundary_loops'][0]['XZ_area']/records['old_good_hand']['boundary_loops'][0]['XZ_area'],'no_nearest_source_ID_assignment':True,'join_not_built':'These loops are coplanar and may cross each other; do not bridge atzero axial width. If accepted, cut a finite wrist band around centralY-.72 (proposed bodyY-.70 and handY-.74), monotonic correspondence/zipper or explicit count-matched strip, fixed old contact region; actual self/contact reverified before retention.'}
 xz=np.r_[a[:,[0,2]],b[:,[0,2]]];lo=xz.min(0);hi=xz.max(0);scale=600/max(hi-lo);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"><rect width="800" height="800" fill="white"/>','<text x="30" y="30" font-family="sans-serif" font-size="20">C57 same wrist plane Y=-.72 actual loops</text>','<text x="30" y="58" font-family="sans-serif" font-size="17">Gray=C52 body; orange=original C35 good hand. Not yet joined.</text>']
 for p,color in [(a,'#444444'),(b,'#e36b22')]:
  pp=p[:,[0,2]];xy=np.c_[80+(pp[:,0]-lo[0])*scale,730-(pp[:,1]-lo[1])*scale];svg.append('<polygon points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in xy)+'" fill="none" stroke="'+color+'" stroke-width="2"/>')
 svg.append('</svg>');(OUT/'same-wrist-plane-loop-overlay.svg').write_text('\n'.join(svg))
report={'stage':'C57-two-source-same-wrist-plane-graft-feasibility-only','source_hashes':hashes,'source_native_files_unchanged':all(sha(paths[k])==v for k,v in hashes.items()),'records':records,'both_single_simple_loops':eligible,'comparison':comparison,'guitar_contact_frame_geometry_transform_exact_across_sources':allgtr['voxel_body']==allgtr['old_good_hand'],'actual_graft_mesh_built':False,'old_hand_provenance':'Every surviving original hand vertex has explicit C35 inputindex+1; all bisect-created points0. Contact faces retain original C35 cyclic vertex indices/coordinates; no nearest index recovery.','limits':['A simple same-plane section is only an input gate. No seam, final full self, current wood/tube/5ray contact or art pass.','C52 ear self is outside this wrist graft; ear C56 branch remains independent.','No new right-palm shape or global remesh parameters.']};(OUT/'wrist-graft-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT '+json.dumps({'eligible_single_simple_loops':eligible,'comparison':comparison,'guitar_frame_exact':report['guitar_contact_frame_geometry_transform_exact_across_sources']}),flush=True)
