"""Confirm raw preSmooth witnesses from frozen NPZ/receipt; no remesh or save."""
import numpy as np,json,itertools,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
R=Path(__file__).resolve().parents[3];O=R/'artifacts/character-body-voxel-c57';p=O/'same-fixed-remesh-before-smooth.npz';rh=O/'smooth-cause-receipt.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={p.name:sha(p),rh.name:sha(rh)};co=np.load(p)['co'];rows=json.load(open(rh))['beforeSmooth_pair_geometry'];out=[]
for row in rows:
 pp=[Vector(co[i]) for i in row['vertices'][0]];qq=[Vector(co[i]) for i in row['vertices'][1]];points=[]
 for edges,t in [(pp,qq),(qq,pp)]:
  for a,b in zip(edges,edges[1:]+edges[:1]):
   length=(b-a).length
   if length<1e-12:continue
   d=(b-a)/length;h=intersect_ray_tri(*t,d,a,True)
   if h is not None and -1e-7<=(h-a).dot(d)<=length+1e-7 and not any((h-q).length<1e-7 for q in points):points.append(h)
 span=max(((a-b).length for a,b in itertools.combinations(points,2)),default=0);out.append({'triangles':row['triangles'],'bbox':row['bbox'],'span':span,'actual_segment_gt_1e_minus6':span>1e-6})
r={'scope':'C57 raw beforeSmooth110 witness edge-triangle line confirmation only','original_files_sha256':hashes,'beforeSmooth_BVH_pairs':len(out),'confirmed_segments_gt_1e_minus6':sum(q['actual_segment_gt_1e_minus6'] for q in out),'unconfirmed_or_tangency_count':sum(not q['actual_segment_gt_1e_minus6'] for q in out),'max_span':max(q['span'] for q in out),'pairs':out,'no_geometry_change':True};assert all(sha(p)==hashes[p.name] for p in [p,rh]);(O/'pre-smooth-line-confirmation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='pairs'}),flush=True)
