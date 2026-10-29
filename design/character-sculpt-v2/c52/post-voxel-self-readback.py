"""One bounded read-only actual-body-self check after C52 actual-image inspection.
Not an18-category deliverable audit or inherited contact/art gate.
"""
import bpy,bmesh,numpy as np,json,hashlib,sys,time
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-body-voxel-c52';native=O/'miao-c52-whole-body-voxel-authoring-study.blend';source=R/'artifacts/character-local-merge-c49/miao-c49-local-merge.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nh=sha(native);sh=sha(source);start=time.time();bpy.ops.wm.open_mainfile(filepath=str(native));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;me.calc_loop_triangles();co=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,tri,all_triangles=True);over=tree.overlap(tree);count=0;sample=[]
for a,b in over:
 if a>=b or set(tri[a])&set(tri[b]):continue
 count+=1
 if len(sample)<32:sample.append({'triangles':[a,b],'vertices':[list(tri[a]),list(tri[b])]})
print('ACTUAL_GLOBAL_BODY_SELF '+str(count),flush=True);bm=bmesh.new();bm.from_mesh(me);bad=0
for edge in bm.edges:
 if len(edge.link_faces)==2:
  f1,f2=edge.link_faces;l1=next(l for l in edge.link_loops if l.face==f1);l2=next(l for l in edge.link_loops if l.face==f2)
  if l1.vert==l2.vert:bad+=1
bm.free();r={'scope':'One actual complete-body triangle-BVH self check, after actual before/after shape inspection. Independent objects and contact intentionally not audited here.','native_sha256_before_after':nh,'source_C49_sha256_before_after':sh,'actual_body_vertices':len(co),'actual_body_triangles':len(tri),'actual_non_neighbour_body_triangle_self_pairs':count,'self_pair_sample':sample,'inconsistent_winding_edges':bad,'retained_legacy_rest_vector_attributes':[a.name for a in me.attributes if a.domain=='POINT' and a.data_type=='FLOAT_VECTOR' and a.name in ['miao_rest_position','rest_position']],'all_int_point_ids0':all(all(x.value==0 for x in a.data) for a in me.attributes if a.domain=='POINT' and a.data_type in {'INT','BOOLEAN'}),'same_source_no_sculpt_field':True,'seconds':time.time()-start,'limits':['Self0 here concerns only the new body surface, not wood/string penetration or independent eyelid/eye intersections.','This is authoring topology; no UV/groom/rig/contact or character art approval.']};assert sha(native)==nh and sha(source)==sh;(O/'post-voxel-self-readback.json').write_text(json.dumps(r,indent=2)+'\n');print('READBACK '+json.dumps(r),flush=True)
