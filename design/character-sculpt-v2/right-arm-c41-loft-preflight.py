"""C41 same single source cut, actual shared torso/shoulder/arm section preflight.
Only proceed when separately audited chart has every boundary edge and positive3D
patch orientation. Complete connected grass model, not art/animation acceptance.
"""
import bpy,bmesh,numpy as np,json,sys,hashlib,time,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/character-right-arm-c41';SRC=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A
h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';t=h.read_text();exec(compile(t[t.index('def smooth'):t.index('def main():')],str(h)+'#pure-helpers','exec'),globals())
def main():
 chart=json.loads((OUT/'torso-chart-preflight.json').read_text());assert chart['Delaunay_safe_to_use_as_annulus'] and chart['actual_3d_patch_positive_orientation'],chart
 started=time.time();bpy.ops.wm.open_mainfile(filepath=str(OUT/'diagnostic-c41-open-source-boundary.blend'));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;oldP=np.load(OUT/'source-cut-map.npz')['original'];source=json.loads((OUT/'source-boundary-preflight.json').read_text());loop=source['boundary_loops'][0]['C35_original_indices'];d=np.load(OUT/'torso-chart-data.npz');co=d['co'];pt=d['pts'];tri=d['tri'];nb=len(loop);ni=64;bm=bmesh.new();bm.from_mesh(me);can=bm.verts.layers.int['Miao_C35_vertex_id'];region=bm.faces.layers.int.new('C41 construction region');vmap={v[can]-1:v for v in bm.verts};patch=[]
 for i,p in enumerate(co):
  if i<nb:v=vmap[loop[i]]
  else:
   v=bm.verts.new(p)
   for layer in bm.verts.layers.int.values():v[layer]=0
  patch.append(v)
 for face in tri:
  f=bm.faces.new([patch[int(i)] for i in face]);f[region]=1;f.smooth=True
 root=[patch[nb+i] for i in range(ni)];rootco=np.array([v.co[:] for v in root]);center=rootco.mean(0);centers=[center,np.array([-.98,-.65,2.17]),np.array([-1.10,-1.18,1.99]),np.array([-.99,-1.25,1.90]),np.array([-.77,-1.25,1.83]),np.array([-.57,-1.23,1.72]),np.array([-.46,-1.19,1.66])];rads=[(.17,.13),(.22,.14),(.23,.10),(.215,.10),(.20,.11),(.175,.115),(.16,.09)]
 def sample(seq,i,t):
  p0,p1,p2,p3=[np.array(seq[max(0,min(len(seq)-1,k))]) for k in [i-1,i,i+1,i+2]];return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
 samples=[]
 for j in range((len(centers)-1)*6+1):
  i=min(j//6,len(centers)-2);t=(j-i*6)/6;samples.append((sample(centers,i,t),sample(rads,i,t)))
 theta=np.arange(ni)*2*np.pi/ni;prior=root;oldtan=Vector(np.cross(rootco[1]-rootco[0],rootco[16]-rootco[0])).normalized();width=Vector(rootco[0]-rootco[32]).normalized();ring_records=[]
 def newvert(p):
  v=bm.verts.new(p)
  for layer in bm.verts.layers.int.values():v[layer]=0
  return v
 def bridge(a,b,reg):
  assert len(a)==len(b)
  for k in range(len(a)):
   f=bm.faces.new((a[k],a[(k+1)%len(a)],b[(k+1)%len(b)],b[k]));f[region]=reg;f.smooth=True
 for j,(c,rad) in enumerate(samples[1:-1],1):
  tangent=Vector(samples[min(j+1,len(samples)-1)][0]-samples[max(j-1,0)][0]).normalized();width=oldtan.rotation_difference(tangent)@width;width=(width-tangent*width.dot(tangent)).normalized();depth=tangent.cross(width).normalized();coords=np.array([c+np.array(width)*(rad[0]*math.cos(a))+np.array(depth)*(rad[1]*math.sin(a)) for a in theta]);blend=min(1,j/3);transport=rootco+(c-center);coords=transport*(1-blend)+coords*blend;ring=[newvert(p) for p in coords];bridge(prior,ring,2);prior=ring;oldtan=tangent;ring_records.append({'station':j,'center':c.tolist(),'width':float(rad[0]),'depth':float(rad[1]),'complete_section_vertices':len(ring)})
 # Shared 32-column front/back knuckle strip. Three digit loops share exact web
 # edges; there are no individual toe objects, spheres, duplicated limb skins.
 C=centers[-1];D=Vector(centers[-1]-centers[-2]).normalized();T=Vector((-D.z,0,D.x)).normalized();Y=Vector((0,1,0));F=[];B=[]
 for k,u in enumerate(np.linspace(-.16,.16,32)):
  dep=.09*(.55+.45*math.sqrt(max(0,1-(u/.16)**2)));F.append(newvert(C+np.array(T)*u-np.array(Y)*dep));B.append(newvert(C+np.array(T)*u+np.array(Y)*dep))
 ring=(F+B[::-1])[::-1];# counterclockwise viewed along D
 costs=[sum((prior[k].co-ring[(k+off)%64].co).length_squared for k in range(64)) for off in range(64)];off=int(np.argmin(costs));ring=ring[off:]+ring[:off];bridge(prior,ring,2);toe_records=[]
 for digit,(a,b) in enumerate([(0,10),(10,21),(21,31)]):
  rootloop=(F[a:b+1]+B[a:b+1][::-1])[::-1];rp=np.array([v.co[:] for v in rootloop]);rc=rp.mean(0);ru=float(np.max(np.abs((rp-rc)@np.array(T))));phase=np.arctan2((rp-rc)@np.array(Y)/.09,(rp-rc)@np.array(T)/ru);last=rootloop;path=[]
  for j,(length,depth,scale,curl) in enumerate([(.025,.083,1.00,.000),(.060,.075,.95,.012),(.090,.055,.82,.022),(.115,.030,.52,.025)]):
   c=rc+np.array(D)*length+np.array(Y)*curl;points=[c+np.array(T)*(ru*scale*math.cos(ph))+np.array(Y)*(depth*math.sin(ph)) for ph in phase];ring2=[newvert(p) for p in points];bridge(last,ring2,3);last=ring2;path.append(c.tolist())
  tip=newvert(rc+np.array(D)*.128+np.array(Y)*.022)
  for k in range(len(last)):
   f=bm.faces.new((last[k],last[(k+1)%len(last)],tip));f[region]=3;f.smooth=True
  toe_records.append({'digit':digit+1,'root_shared_front_columns':[a,b],'root_ring_count':len(rootloop),'curve_centers':path,'extension_u':.128,'width_radius':ru})
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);volume=bm.calc_volume(signed=True);bm.to_mesh(me);bm.free();me.update();bpy.context.view_layer.update();actual=arr(me);canids=np.array([x.value for x in me.attributes['Miao_C35_vertex_id'].data]);keep=canids>0;assert len(np.unique(canids[keep]))==keep.sum() and np.array_equal(actual[keep],oldP[canids[keep]-1]);present=np.zeros(len(oldP),bool);present[canids[keep]-1]=True;head=oldP[:,2]>=2.43;left=oldP[:,0]>0;assert np.all(present[head|left]);top=topo(me);newfaces=[f.index for f in me.polygons if me.attributes['C41 construction region'].data[f.index].value>0];loc=local_stats(body,actual,newfaces);me.calc_loop_triangles();tr=np.array([tuple(t.vertices) for t in me.loop_triangles]);fi=np.array([t.polygon_index for t in me.loop_triangles]);reg=np.array([me.attributes['C41 construction region'].data[int(i)].value for i in fi]);isnew=reg>0;indices=np.flatnonzero(isnew);ht=BVHTree.FromPolygons(actual,tr[isnew].tolist(),all_triangles=True);whole=BVHTree.FromPolygons(actual,tr.tolist(),all_triangles=True);selfpairs=[]
 for a,b in ht.overlap(whole):
  a=int(indices[a])
  if a==b or set(tr[a])&set(tr[b]) or(isnew[b] and a>b):continue
  selfpairs.append({'triangles':[a,b],'faces':[int(fi[a]),int(fi[b])],'regions':[int(reg[a]),int(reg[b])]})
 cross={};parity=[];deps=bpy.context.evaluated_depsgraph_get();skinids=np.flatnonzero(~keep);directions=[Vector((.371,.613,.697)).normalized(),Vector((.739,.223,.635)).normalized()]
 def vote(tree,p,dr):
  pos=Vector(p);count=0
  for k in range(64):
   h,n,f,d=tree.ray_cast(pos,dr,8)
   if h is None:return count%2
   count+=1;pos=h+dr*1e-5
  return None
 trees={}
 for name in ['Guitar / spruce soundboard','Guitar / rosewood body','Guitar / neck','Guitar / ebony fretboard']+['Guitar / string '+str(i+1) for i in range(6)]:
  tree,nt=actual_tree(bpy.data.objects[name]);trees[name]=tree;over=ht.overlap(tree);cross[name]={'pairs':len(over),'new_regions':{str(r):sum(reg[indices[a]]==r for a,b in over) for r in [1,2,3]}}
  if name in ['Guitar / spruce soundboard','Guitar / rosewood body','Guitar / neck','Guitar / ebony fretboard']:
   ins=[];amb=[]
   for i in skinids:
    v=[vote(tree,actual[i],d) for d in directions]
    if v==[1,1]:ins.append(int(i))
    elif v[0]!=v[1] or None in v:amb.append(int(i))
   parity.append({'object':name,'inside_new_skin_points':len(ins),'ambiguous':len(amb),'inside_sample':ins[:20]})
 toeids=sorted({int(v) for t in tr[reg==3] for v in t});gaps=[]
 for i in range(6):
  tree=trees['Guitar / string '+str(i+1)];val=min(tree.find_nearest(Vector(actual[j]))[3] for j in toeids);gaps.append(float(val))
 receipt={'stage':'C41-same-source-cut-connected-section-grass-model-preflight','input_C35_sha256':sha(SRC),'script_sha256':sha(__file__),'chart':chart,'actual_shared_source_boundary_vertices':nb,'shoulder_shared_patch_inner_ring_vertices':ni,'all_surviving_C35_points_exact':True,'canonical_old_nonzero_unique_new0':True,'head_xpositive_leftC35_exact_present':True,'original_retained':int(keep.sum()),'new_skin_points':int((~keep).sum()),'topology':top,'signed_volume':volume,'closed_body_skin_grass_model':top['components']==1 and not top['boundary_edges'] and not top['nonmanifold_edges'],'section_stations':ring_records,'toes':toe_records,'new_skin_local_audit':loc,'actual_new_skin_vs_whole_non_neighbour_self':len(selfpairs),'self_pair_samples':selfpairs[:40],'actual_wood_and_six_tube_intersections':cross,'actual_wood_parity':parity,'six_actual_toe_to_tube_vertex_gap_samples':gaps,'nearest_idle_gap_02_04_sample_pass':.02<=min(gaps)<=.04,'claim':'A single geometric feasibility preflight; no art/clearance/animation completion is implied by closed topology.','limits':['No clean production retopology/groom/UV/rig claim.','New source0 points preserve original retained identity for exact head/left-shoulder branch merge.','All self/wood/normal/visible cross-section failures remain blockers.']};native=OUT/'diagnostic-c41-shared-root-section-preflight.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);np.savez_compressed(OUT/'loft-source-output-map.npz',output_to_original_index=canids-1,canonical=canids,original_presence=present);(OUT/'loft-preflight-receipt.json').write_text(json.dumps(receipt,indent=2,default=lambda q:int(q))+'\n');print('LOFT '+json.dumps({'topology':top,'volume':volume,'self':len(selfpairs),'cross':cross,'parity':parity,'tube_gaps':gaps,'native':receipt['native_sha256']},default=lambda q:int(q)),flush=True)
 s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;cam=s.camera
 for view in ['front','three-quarter']:
  if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
  s.render.filepath=str(OUT/('diagnostic-shared-root-full-'+view+'.png'));bpy.ops.render.render(write_still=True)
main()
