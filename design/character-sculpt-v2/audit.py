"""Inspect actual evaluated candidate geometry. No art-quality score is emitted."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True)
obj=bpy.data.objects.get('Miao / continuous pear and rounded-square face');dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);me=ev.to_mesh()
vs=[obj.matrix_world@v.co for v in me.vertices];polys=[tuple(p.vertices) for p in me.polygons];bvh=BVHTree.FromPolygons(vs,polys,all_triangles=False)
# Full-body connectivity is structural only, not proof of good shoulder edge flow.
parent=list(range(len(vs)))
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
for e in me.edges:
 a,b=e.vertices;ra,rb=find(a),find(b)
 if ra!=rb:parent[ra]=rb
components={}
for i in range(len(vs)):
 r=find(i);components[r]=components.get(r,0)+1
# Probe rays through the evaluated paw along Y at each string. Positive plane gap
# means the paw ends in front of a board/string plane; negative means intersection.
angle=math.radians(23.3);origin=Vector((-.27,-.85,1.30));probes=[]
for key in range(6):
 v=(key-2.5)*.037
 for x in [-.57,-.52,-.47,-.42,-.37]:
  u=((x-origin.x)/1.19+v*math.sin(angle))/math.cos(angle);z=origin.z+1.19*(u*math.sin(angle)+v*math.cos(angle));ys=origin.y-.206+(u+.49)/.99*.020;start=Vector((x,-3,z));hits=[]
  for n in range(12):
   loc,normal,idx,dist=bvh.ray_cast(start,Vector((0,1,0)),8)
   if loc is None:break
   hits.append(float(loc.y));start=loc+Vector((0,.0002,0))
  # Only an interval in front of the torso and near guitar counts as picking paw.
  paw=[(hits[i],hits[i+1]) for i in range(0,len(hits)-1,2) if hits[i]<-.95 and hits[i+1]<-.70]
  probes.append({'string':key+1,'x':x,'z':round(z,6),'string_y':round(ys,6),'ray_body_intersections_y':[round(y,6) for y in hits],'paw_intervals':paw,'string_inside_paw':any(lo<=ys<=hi for lo,hi in paw),'note':'ray-classified local volume, not physical cloth/string simulation'})
receipt={'stage':'static-geometry-audit','evaluated_vertices':len(vs),'evaluated_faces':len(polys),'connected_component_vertex_counts':sorted(components.values(),reverse=True),'picking_probes':probes,'limits':['Does not prove art fidelity, natural grasp, skin deformation, animation or web behavior.','Torso behind the instrument is excluded heuristically from paw intervals; inspect cuts visually.','Rendered beauty may reveal defects that these measurements cannot detect.']}
out.write_text(json.dumps(receipt,indent=2)+'\n');print('AUDIT',out,'vertices',len(vs),'components',len(components));ev.to_mesh_clear()
