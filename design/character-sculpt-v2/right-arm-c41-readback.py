"""Read-only C41 source/provenance/collision attribution; frozen native unchanged."""
import bpy,numpy as np,json,hashlib,sys,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/character-right-arm-c41';SRC=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';native=OUT/'diagnostic-c41-shared-root-section-preflight.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();frozen=sha(native);h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';t=h.read_text();exec(compile(t[t.index('def smooth'):t.index('def main():')],str(h)+'#pure-helpers','exec'),globals());bpy.ops.wm.open_mainfile(filepath=str(SRC));me=bpy.data.objects['Miao / continuous pear and rounded-square face'].data;P=arr(me);attrs={a.name:np.array([x.value for x in a.data]) for a in me.attributes if a.domain=='POINT' and a.data_type in {'INT','BOOLEAN'}};protected={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};bpy.ops.wm.open_mainfile(filepath=str(native));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;actual=arr(me);can=np.array([v.value for v in me.attributes['Miao_C35_vertex_id'].data]);old=can>0;new=~old;present=np.zeros(len(P),bool);present[can[old]-1]=True;head=P[:,2]>=2.43;left=P[:,0]>0;newlefthand=attrs['C23 source vertex id']==0;attrchecks={name:{'retained_exact':bool(np.array_equal(np.array([v.value for v in me.attributes[name].data])[old],values[can[old]-1])),'new0':bool(np.all(np.array([v.value for v in me.attributes[name].data])[new]==0))} for name,values in attrs.items()};gexact=protected=={n:fingerprint(bpy.data.objects[n]) for n in protected};me.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);fi=np.array([t.polygon_index for t in me.loop_triangles]);reg=np.array([me.attributes['C41 construction region'].data[int(i)].value for i in fi]);newtri=reg>0;idx=np.flatnonzero(newtri);ht=BVHTree.FromPolygons(actual,tri[newtri].tolist(),all_triangles=True);whole=BVHTree.FromPolygons(actual,tri.tolist(),all_triangles=True);pairrows=[];counts=collections.Counter()
for a,b in ht.overlap(whole):
 a=int(idx[a])
 if a==b or set(tri[a])&set(tri[b]) or(newtri[b] and a>b):continue
 v=sorted(set(tri[[a,b]].ravel().tolist()));kind='-'.join(map(str,sorted([int(reg[a]),int(reg[b])])));counts[kind]+=1;pairrows.append({'triangles':[a,b],'faces':[int(fi[a]),int(fi[b])],'regions':[int(reg[a]),int(reg[b])],'bbox':[actual[v].min(0).tolist(),actual[v].max(0).tolist()]})
wood=[]
for name in ['Guitar / spruce soundboard','Guitar / rosewood body']:
 tree,nt=actual_tree(bpy.data.objects[name]);pairs=ht.overlap(tree);v=sorted({int(i) for a,b in pairs for i in tri[idx[a]]});wood.append({'object':name,'pairs':len(pairs),'bbox':[actual[v].min(0).tolist(),actual[v].max(0).tolist()] if v else None,'regions':dict(collections.Counter(str(int(reg[idx[a]])) for a,b in pairs)),'skin_vertices':v})
layers=[]
for x,z in [(-1.05,1.85),(-.90,1.90),(-.75,1.82),(-.6,1.75),(-.45,1.65),(-.35,1.69),(-1.1,2.0),(-.9,1.6)]:
 pos=Vector((x,-3,z));hits=[]
 for j in range(16):
  q,n,f,d=whole.ray_cast(pos,Vector((0,1,0)),8)
  if q is None:break
  hits.append({'y':q.y,'normalY':n.y,'actual_triangle':f,'region':int(reg[f])});pos=q+Vector((0,1e-5,0))
 layers.append({'xz':[x,z],'hits':hits})
rows=[]
for kind,n in sorted(counts.items()):
 vals=[np.array(r['bbox']) for r in pairrows if '-'.join(map(str,sorted(r['regions'])))==kind];v=np.array(vals);rows.append({'regions':kind,'count':n,'bbox':[v[:,0].min(0).tolist(),v[:,1].max(0).tolist()]})
r={'scope':'Frozen C41 geometric feasibility readback, not art pass','native_sha256_before_after':frozen,'canonical_nonzero_unique':len(np.unique(can[old]))==int(old.sum()),'all_retained_old_coordinates_exact':bool(np.array_equal(actual[old],P[can[old]-1])),'all_head_present_exact':bool(np.all(present[head])),'all_xpositive_present_exact':bool(np.all(present[left])),'all_5359_new_C35_left_hand_present_exact':bool(np.all(present[newlefthand])),'point_int_attribute_checks':attrchecks,'all_guitar_geometry_transform_visibility_exact':gexact,'self_by_regions_0retained_1torso_2arm_3toe':rows,'actual_self_pairs':pairrows,'wood_intersections':wood,'actual_arm_vs_torso_Y_layers':layers,'euler':len(me.vertices)-len(me.edges)+len(me.polygons),'no_native_mutation':sha(native)==frozen};assert r['no_native_mutation'];(OUT/'readback-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print('READBACK '+json.dumps({k:r[k] for k in ['canonical_nonzero_unique','all_retained_old_coordinates_exact','all_head_present_exact','all_xpositive_present_exact','all_5359_new_C35_left_hand_present_exact','all_guitar_geometry_transform_visibility_exact','self_by_regions_0retained_1torso_2arm_3toe','wood_intersections','euler']}),flush=True)
