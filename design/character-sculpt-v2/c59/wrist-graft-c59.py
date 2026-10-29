"""C59 one finite wrist zipper graft: C56 repaired-ear body + exact C35 good hand.
Body Y=-.70, old hand original Y=-.72 preserves all5359 points; no Manifold,
nearest identity, right-palm shape or inherited contact pass. Images precede audit.
"""
import bpy,bmesh,numpy as np,json,sys,time,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/character-wrist-graft-c59';SRCBODY=ROOT/'artifacts/character-ear-sculpt-c56/gray-material-consistency/miao-c56-gray-skin-consistent.blend';SRCHAND=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend';C52=ROOT/'artifacts/character-body-voxel-c52/miao-c52-whole-body-voxel-authoring-study.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();h=ROOT/'design/character-sculpt-v2/strum-paw-refinement-c37.py';s=h.read_text();exec(compile(s[s.index('def smooth'):s.index('def main():')],str(h)+'#pure-helpers','exec'),globals());h57=ROOT/'design/character-sculpt-v2/c57/wrist-hand-graft-preflight-c57.py';s=h57.read_text();exec(compile(s[s.index('def loops'):s.index('records={}')],str(h57)+'#pure-helpers','exec'),globals())
C52ID='C59 C52 source vertex id';C35ID='C59 C35 source vertex id';C52F='C59 C52 source face id';C35F='C59 C35 source face id';REG='C59 construction region'
def topohash(me):
 a=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',a);b=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_total',b);return hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()

def cut(body,level,distal,pointname,facename):
 me=body.data;P=arr(me).copy();bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table();pid=bm.verts.layers.int.get(pointname) or bm.verts.layers.int.new(pointname);fid=bm.faces.layers.int.get(facename) or bm.faces.layers.int.new(facename)
 for v in bm.verts:v[pid]=v.index+1
 for f in bm.faces:f[fid]=f.index+1
 original=set(bm.verts);roi=[f for f in bm.faces if .75<f.calc_center_median().x<1.62 and 1.3<f.calc_center_median().z<2.35 and f.calc_center_median().y<-.55];edges={e for f in roi for e in f.edges};verts={v for f in roi for v in f.verts};plane=float(Vector((0,level,0)).y);crossedges=[]
 for e in edges:
  a,b=e.verts
  if(a.co.y-plane)*(b.co.y-plane)<0:
   t=(plane-a.co.y)/(b.co.y-a.co.y);crossedges.append({'edge_ref':e,'input_edge_index':e.index,'input_vertex_indices':[a[pid]-1,b[pid]-1],'parameter':t,'predicted_world':list(a.co.lerp(b.co,t))})
 bmesh.ops.bisect_plane(bm,geom=list(verts)+list(edges)+roi,dist=1e-8,plane_co=(0,level,0),plane_no=(0,1,0),clear_inner=False,clear_outer=False);new=[v for v in bm.verts if v not in original];provenance=[]
 for v in new:
  for layer in bm.verts.layers.int.values():v[layer]=0
  candidates=[r for r in crossedges if r['edge_ref'].is_valid and v in r['edge_ref'].verts];method='actual original split-edge identity'
  if len(candidates)!=1:
   candidates=[r for r in crossedges if (v.co-Vector(r['predicted_world'])).length<2e-6];method='unique declared source-edge/plane interpolation witness; not original vertex identity'
  assert len(candidates)==1,{'cut_edge_provenance_candidates':len(candidates)};r=candidates[0];provenance.append({'vertex_ref':v,'input_edge_index':r['input_edge_index'],'input_vertex_indices':r['input_vertex_indices'],'edge_parameter':r['parameter'],'cut_world':list(v.co),'witness_method':method,'old_source_id':0})
 df=[f for f in bm.faces if .75<f.calc_center_median().x<1.62 and 1.3<f.calc_center_median().z<2.35 and f.calc_center_median().y<level-1e-7];dfset=set(df);delete=[f for f in bm.faces if f not in dfset] if distal else df;bmesh.ops.delete(bm,geom=delete,context='FACES_ONLY');loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.verts.index_update();rows=[]
 for r in provenance:
  v=r['vertex_ref']
  if v.is_valid:rows.append({**{k:v for k,v in r.items() if k!='vertex_ref'},'cut_output_vertex_index':v.index})
 bm.to_mesh(me);bm.free();me.update();co=arr(me);ids=np.array([v.value for v in me.attributes[pointname].data]);old=ids>0;assert np.array_equal(co[old],P[ids[old]-1]);ls,bad=loops(me);assert len(ls)==1 and not bad;loop=ls[0];xz=co[loop][:,[0,2]]
 if signed_area(xz)<0:loop=loop[::-1]
 k=min(range(len(loop)),key=lambda i:(co[loop[i],2],co[loop[i],0]));loop=loop[k:]+loop[:k];assert not crossings(co[loop][:,[0,2]])
 return {'original':P,'co':co,'faces':[list(f.vertices) for f in me.polygons],'loop':loop,'point_attributes':{a.name:np.array([v.value for v in a.data],np.int32) for a in me.attributes if a.domain=='POINT' and a.data_type=='INT'},'face_attributes':{a.name:np.array([v.value for v in a.data],np.int32) for a in me.attributes if a.domain=='FACE' and a.data_type=='INT' and a.name!='material_index'},'cut_edge_provenance':rows,'new_cut_points':int((~old).sum()),'topology':topo(me),'plane':level}

def resample(p,n=256):
 d=np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1);t=np.r_[0,np.cumsum(d)];q=np.arange(n)/n*t[-1];k=np.minimum(np.searchsorted(t,q,side='right')-1,len(p)-1);a=(q-t[k])/d[k];return p[k]*(1-a[:,None])+p[(k+1)%len(p)]*a[:,None]

def main():
 assert not (OUT/'receipt.json').exists(),'C59 frozen';start=time.time();hashes={'body':sha(SRCBODY),'hand':sha(SRCHAND),'C52':sha(C52)};assert hashes['body']=='2af4802f996c61badb0883385d6be2048ec3f63494648042e11b0594ac9f463a';bpy.ops.wm.open_mainfile(filepath=str(C52));base=bpy.data.objects['Miao / continuous pear and rounded-square face'];c52topo=topohash(base.data);c52count=len(base.data.vertices);bpy.ops.wm.open_mainfile(filepath=str(SRCHAND));handob=bpy.data.objects['Miao / continuous pear and rounded-square face'];gtrhand={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};contactsource=json.load(open(ROOT/'artifacts/character-paw-grip-c35/receipt.json'))['after_actual_target_rays'];old_contact_vertices={r['face_index']:list(handob.data.polygons[r['face_index']].vertices) for r in contactsource};hand=cut(handob,-.72,True,C35ID,C35F);assert len(hand['co'])==5359 and hand['new_cut_points']==0
 # All5359 are retained original C35 vertices, not just a nearest-position copy.
 handids=hand['point_attributes'][C35ID];assert np.all(handids>0) and len(np.unique(handids))==5359;fids=hand['face_attributes'][C35F];contactpres=[]
 for row in contactsource:
  f=int(np.flatnonzero(fids==row['face_index']+1)[0]);ids=(handids[hand['faces'][f]]-1).tolist();assert ids==old_contact_vertices[row['face_index']];contactpres.append({'kind':row['kind'],'original_C35_face':row['face_index'],'cyclic_original_vertex_indices':ids,'actual_target_world':row['actual_target_world'],'source_gap_not_new_pass':row['gap']})
 bpy.ops.wm.open_mainfile(filepath=str(SRCBODY));scene=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];assert len(body.data.vertices)==c52count and topohash(body.data)==c52topo;assert np.allclose(np.array(body.matrix_world),np.eye(4));others={o.name:{**fingerprint(o),'materials':[m.name if m else None for m in o.data.materials]} for o in bpy.data.objects if o!=body and o.type in {'MESH','CURVE','CURVES'} and not(o.type=='CURVES' and o.hide_render)};gtrbody={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')};assert gtrbody==gtrhand;prox=cut(body,-.70,False,C52ID,C52F);bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();region=bm.faces.layers.int.get(REG) or bm.faces.layers.int.new(REG)
 for f in bm.faces:f[region]=1
 for name in hand['point_attributes']:
  if bm.verts.layers.int.get(name) is None:bm.verts.layers.int.new(name)
 if bm.verts.layers.int.get(C35ID) is None:bm.verts.layers.int.new(C35ID)
 for name in hand['face_attributes']:
  if bm.faces.layers.int.get(name) is None:bm.faces.layers.int.new(name)
 oldbodyverts=list(bm.verts);hv=[]
 for i,p in enumerate(hand['co']):
  v=bm.verts.new(p)
  for layer in bm.verts.layers.int.values():v[layer]=0
  for name,values in hand['point_attributes'].items():v[bm.verts.layers.int[name]]=int(values[i])
  hv.append(v)
 for i,vs in enumerate(hand['faces']):
  f=bm.faces.new([hv[j] for j in vs]);f.material_index=0;f.smooth=True
  for name,values in hand['face_attributes'].items():f[bm.faces.layers.int[name]]=int(values[i])
  f[region]=2
 A=[oldbodyverts[i] for i in prox['loop']];B=[hv[i] for i in hand['loop']];Ap=np.array([v.co[:] for v in A]);cost=[]
 for off in range(len(B)):
  bp=np.array([B[(i+off)%len(B)].co[:] for i in range(len(B))]);cost.append(float(np.mean(np.linalg.norm(resample(Ap)[:,[0,2]]-resample(bp)[:,[0,2]],axis=1)**2)))
 offset=int(np.argmin(cost));B=B[offset:]+B[:offset]
 def fractions(v):p=np.array([q.co[:] for q in v]);d=np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1);return np.r_[0,np.cumsum(d)]/sum(d)
 af=fractions(A);bf=fractions(B);i=j=0;band=[]
 while i<len(A) or j<len(B):
  if i<len(A) and (j==len(B) or af[i+1]<=bf[j+1]):vs=(A[i%len(A)],A[(i+1)%len(A)],B[j%len(B)]);i+=1
  else:vs=(A[i%len(A)],B[(j+1)%len(B)],B[j%len(B)]);j+=1
  f=bm.faces.new(vs)
  for layer in bm.faces.layers.int.values():f[layer]=0
  f[region]=3;f.material_index=0;f.smooth=True;band.append(f)
 # No fairing needed/applied in this single candidate: original hand5359 and
 # every surviving body point remain exact; the straight narrow strip alone joins.
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);volume=bm.calc_volume(signed=True);bm.verts.index_update();band_triangles=[[v.index for v in f.verts] for f in band];body.data.name='C59 / ear-repaired voxel body with exact C35 hand';bm.to_mesh(body.data);bm.free();me=body.data;me.update();bpy.context.view_layer.update();co=arr(me);bid=np.array([v.value for v in me.attributes[C52ID].data]);hid=np.array([v.value for v in me.attributes[C35ID].data]);bodykeep=bid>0;handkeep=hid>0;assert np.array_equal(co[bodykeep],prox['original'][bid[bodykeep]-1]);assert handkeep.sum()==5359 and np.array_equal(co[handkeep],hand['original'][hid[handkeep]-1]);assert not np.any(bodykeep&handkeep);top=topo(me);top['euler']=top['vertices']-top['edges']+top['faces'];assert top['components']==1 and not top['boundary_edges'] and not top['nonmanifold_edges'] and top['euler']==2;independent=all(before=={**fingerprint(bpy.data.objects[name]),'materials':[m.name if m else None for m in bpy.data.objects[name].data.materials]} for name,before in others.items());assert independent;r={'stage':'C59-one-real-finite-wrist-zipper-graft-appearance-gate','sources_sha256':hashes,'script_sha256':sha(__file__),'source_body_has_C52_ordered_topology_exact':True,'body_planeY':-.70,'old_hand_planeY':-.72,'plane_change_reason':'Root authorized prioritize all5359 old hand vertices. Proposed-.74 would remove251 including198 root points; use original-.72 with positive.02u band.','actual_loops':{'body_count':len(A),'hand_count':len(B),'old_hand_cyclic_offset':offset,'zipper_triangle_count':len(band_triangles),'monotonic_arclength_order':True},'fairing':'none; no retained body or old hand vertices moved','body_cut_edge_provenance':prox['cut_edge_provenance'],'old_hand_new_cut_points':hand['new_cut_points'],'all_5359_old_hand_coordinates_bit_exact':True,'all_retained_C56_body_coordinates_bit_exact':True,'independent_C56_objects_geometry_transform_material_visibility_exact':independent,'excluded_hidden_unbound_curves':[o.name for o in bpy.data.objects if o.type=='CURVES' and o.hide_render],'guitar_contact_geometry_world_frame_exact_across_C35_C56':True,'provenance_layers':{'body':C52ID,'hand':C35ID,'body_faces':C52F,'hand_faces':C35F,'new_cut_band_source_ids':0},'old_contact_faces':contactpres,'topology':top,'signed_volume':volume,'new_zero_source_cut_points':int(((bid==0)&(hid==0)).sum()),'original_C52_source_points_retained':int(bodykeep.sum()),'contact_art_status':'Original contact triangles/points protected, but no inherited pass. Full actual self/wood/tube/5rays audit only after actual images.','limits':['No new right-palm shape; C58 contribution is separate and may use explicit retained C52 indices.','No UV/groom/rig/animation/GLB/public/deploy/service cost.']};np.savez_compressed(OUT/'two-source-output-map.npz',C52_source_vertex_id=bid,C35_source_vertex_id=hid,band_triangles=np.array(band_triangles,np.int32));native=OUT/'miao-c59-c56-body-exact-c35-hand.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);r['native_sha256']=sha(native);r['seconds_before_render']=time.time()-start;(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('BUILT '+json.dumps({'topology':top,'loops':r['actual_loops'],'oldhand':int(handkeep.sum()),'body':int(bodykeep.sum()),'native':r['native_sha256']}),flush=True)
 scene.cycles.samples=16;scene.cycles.seed=17;scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.use_border=False;scene.render.use_crop_to_border=False;cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale;r['renders']=[]
 for view in ['front','three-quarter','wrist']:
  if view=='three-quarter':cam.location=(-6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
  elif view=='wrist':cam.location=(4,-1.8,2.5);cam.rotation_euler=(Vector((1.20,-.71,1.83))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.85
  file=OUT/('gray-'+view+'.png');scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);r['renders'].append({'file':file.name,'sha256':sha(file)});(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 assert all(sha(p)==hashes[k] for k,p in [('body',SRCBODY),('hand',SRCHAND),('C52',C52)])
main()
