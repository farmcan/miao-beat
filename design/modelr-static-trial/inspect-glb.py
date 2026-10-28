"""Inspect uncompressed triangle GLB connectivity; no visual acceptance claim."""
import json,struct,pathlib,argparse
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output');a=p.parse_args()
path=pathlib.Path(a.input);b=path.read_bytes();jl,jt=struct.unpack_from('<II',b,12)
assert jt==0x4e4f534a,'Expected JSON chunk'
j=json.loads(b[20:20+jl]);off=20+jl;bl,bt=struct.unpack_from('<II',b,off)
assert bt==0x004e4942,'Expected BIN chunk'
binary=memoryview(b)[off+8:off+8+bl];summary=[]
for prim in [p for m in j['meshes'] for p in m['primitives']]:
 assert prim.get('mode',4)==4,'Triangle primitives only'
 pos=j['accessors'][prim['attributes']['POSITION']];ind=j['accessors'][prim['indices']]
 view=j['bufferViews'][ind['bufferView']]
 assert 'byteStride' not in view,'Only unstrided indices supported'
 start=view.get('byteOffset',0)+ind.get('byteOffset',0);n=pos['count'];parent=list(range(n));counts=[1]*n
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(x,y):
  x=find(x);y=find(y)
  if x!=y:
   if counts[x]<counts[y]:x,y=y,x
   parent[y]=x;counts[x]+=counts[y]
 fmt={5125:'I',5123:'H',5121:'B'}[ind['componentType']];size=struct.calcsize('<'+fmt)
 for x,y,z in struct.iter_unpack('<'+fmt*3,binary[start:start+ind['count']*size]):union(x,y);union(x,z)
 comps=sorted([counts[i] for i in range(n) if parent[i]==i],reverse=True)
 summary.append({'vertices':n,'triangles':ind['count']//3,'components':len(comps),'largest_component_vertex_counts':comps[:30]})
result={'meshes':len(j['meshes']),'primitives':summary,'has_skin':bool(j.get('skins')),'has_animations':bool(j.get('animations')),'limits':['Connectivity alone does not identify cat vs guitar semantic regions, skin quality or art fidelity.']}
text=json.dumps(result,indent=2)+'\n'
if a.output:pathlib.Path(a.output).write_text(text)
print(text)
