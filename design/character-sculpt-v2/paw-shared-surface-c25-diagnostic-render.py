"""C25 numerical-exception diagnostic assembly/render; no geometry solve/retry.
Reads the frozen once-tested patch, preserves all patch/source vertex positions.
Strict receipt remains unchanged. Parent-authorized <.01px exception, not contact pass.
"""
import bpy,bmesh,json,hashlib,sys,math,time
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'artifacts/character-paw-shared-surface-c25';old=root/'artifacts/character-paw-plane-source-c23/r2';src=old/'miao-c23-plane-source.blend';frozen=out/'diagnostic-failed-local.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();strictsha=sha(out/'receipt.json');source_sha=sha(src);frozen_sha=sha(frozen);strict=json.loads((out/'receipt.json').read_text());d=json.loads((out/'local-band-data.json').read_text());sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit as A

def topo(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();seen=set();parts=[]
 for v in bm.verts:
  if v.index in seen:continue
  stack=[v];seen.add(v.index);n=0
  while stack:
   p=stack.pop();n+=1
   for e in p.link_edges:
    q=e.other_vert(p)
    if q.index not in seen:seen.add(q.index);stack.append(q)
  parts.append(n)
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'components':len(parts),'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free();return r

def mesh(name,co,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(co,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return ob

bpy.ops.wm.open_mainfile(filepath=str(frozen));s=bpy.context.scene;patch=bpy.data.objects['C25 authoring / shared quad surface band'];pco=[v.co.copy() for v in patch.data.vertices];pfs=[list(f.vertices) for f in patch.data.polygons];pmats=[f.material_index for f in patch.data.polygons];body=bpy.data.objects['Miao / continuous pear and rounded-square face'];cam=s.camera;frontscale=cam.data.ortho_scale;maxerr=max(q['r2_hit_displacement'] for q in strict['declared_toe_target_checks']);pixelbound=maxerr*768/min(frontscale,1.25);assert pixelbound<.01
# Verify locks from frozen stored float vertices against saved complete source.
uid=body.data.attributes['C23 actual upper local id'];native_upper={x.value-1:body.data.vertices[i].co.copy() for i,x in enumerate(uid.data) if x.value>0};upper_local={int(k):v for k,v in d['upper_local_ids'].items()};lockrows=[]
for row in strict['plan']['toe_locks']:
 ids=row['exact_old_hit_face_vertices'];exact=all(pco[i]==native_upper[upper_local[i]] for i in ids);assert exact;lockrows.append({'digit':row['digit'],'face_vertices_bit_exact_in_frozen_blend':exact,'face_order_preserved':True})
exception={'stage':'C25-engineering-numerical-exception-diagnostic-only','strict_receipt_sha256':strictsha,'strict_gate_retained':'Failed original 1e-6u ray-hit stability test; not waived as contact pass','source_native_sha256':source_sha,'once_tested_frozen_patch_scene_sha256':frozen_sha,'maximum_ray_hit_difference_scene_units':maxerr,'render_resolution_px':768,'front_ortho_scale':frontscale,'inside_ortho_scale':1.25,'conservative_world_error_to_pixel_bound':pixelbound,'difference_fraction_of_original_point05_gap':maxerr/.05,'locked_faces':lockrows,'cause':'All four face vertices and polygon cyclic order exact. Saved native evaluated BVH vs BVHTree.FromPolygons choose different triangulations of the same nonplanar quads; analytic two-diagonal ray results reproduce the difference. See locked-face-triangulation-diagnostic.json.','authorization':'Parent instruction permits diagnostic images only if locked faces exact, self0/flipped0 and projected error below .01px; received 2026-10-29.','geometry_changes':'No new candidate or fair solve. Identity-stitch the frozen patch to original source opening only; float vertex positions preserved.','contact_status':'Existing real hold failures remain P0. No color/animation/engine/deploy.'}
(out/'engineering-exception.json').write_text(json.dumps(exception,indent=2)+'\n')
# Identity stitch of the SAME frozen patch; no nearest weld, smoothing or fitting.
bm=bmesh.new();bm.from_mesh(body.data);sf=bm.faces.layers.int['C23 source face id'];rid=bm.verts.layers.int['C23 source opening local id'];ui=bm.verts.layers.int['C23 actual upper local id'];uf=bm.faces.layers.int['C23 C11 upper face local id'];rg=bm.faces.layers.int['C23 construction region'];sourceverts={v for f in bm.faces if f[sf]>0 for v in f.verts};sourcepos={v:tuple(v.co) for v in sourceverts};rmap={v[rid]-1:v for v in bm.verts if v[rid]>0};assert len(rmap)==198
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f[sf]==0],context='FACES_ONLY');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces and v not in sourceverts],context='VERTS');rootids=d['root_indices'];mapping={rootids[j]:rmap[j] for j in range(198)}
for i,p in enumerate(pco):
 if i not in mapping:mapping[i]=bm.verts.new(p)
 if i in upper_local:mapping[i][ui]=upper_local[i]+1
for i,f in enumerate(pfs):
 nf=bm.faces.new([mapping[j] for j in f]);nf.smooth=True;nf[rg]=pmats[i];nf[uf]=i+1 if pmats[i]==2 else 0
assert all(tuple(v.co)==p for v,p in sourcepos.items());assert all(mapping[i].co==p for i,p in enumerate(pco));bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(body.data);bm.free();body.data.update();bpy.data.objects.remove(patch,do_unlink=True);final=topo(body);assert final['components']==1 and final['boundary_edges']==0 and final['non_manifold_edges']==0
# Actual combined patch + retained collar audit; a check of assembly, not a new candidate.
select=[f for f in body.data.polygons if .75<f.center.x<1.62 and f.center.y<-.60 and 1.3<f.center.z<2.35];ids=sorted({i for f in select for i in f.vertices});idmap={v:i for i,v in enumerate(ids)};probe=mesh('C25 authoring / final frozen band plus source collar',[body.data.vertices[i].co[:] for i in ids],[[idmap[i] for i in f.vertices] for f in select]);collar=A.audit(probe);bpy.data.objects.remove(probe,do_unlink=True);passed=collar['self_intersections']==0 and collar['flipped_faces']==0;result={'stage':'C25-frozen-geometry-diagnostic-assembly','exception':'engineering-exception.json','strict_receipt_sha256':strictsha,'final_body':final,'frozen_patch_vertex_positions_bit_exact':True,'C8_retained_source_vertices_bit_exact':True,'final_local_collar_audit':collar,'diagnostic_render_gate_passed':passed,'not_contact_or_art_pass':True,'source_unchanged':sha(src)==source_sha,'original_strict_receipt_unchanged':sha(out/'receipt.json')==strictsha,'build_script_sha256':sha(__file__)}
s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.context.preferences.filepaths.save_version=0;body['C25 status']='Shared-band frozen engineering-exception diagnostic; strict contact numeric gate failed; art/hold unpassed';body['C25 binding']='Old UV/groom/shape bindings invalid';native=out/('miao-c25-shared-surface-diagnostic.blend' if passed else 'diagnostic-failed-collar.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);result['diagnostic_native_sha256']=sha(native);(out/'diagnostic-assembly-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('ASSEMBLY '+json.dumps({k:v for k,v in result.items() if k!='final_local_collar_audit'}))
if not passed:print('STOP: actual collar collision, no gray images');sys.exit(0)
frontloc=cam.location.copy();frontrot=cam.rotation_euler.copy()
for view in ['front','inside']:
 if view=='inside':cam.location=(4,-6,3);cam.rotation_euler=(Vector((1.17,-.95,1.96))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
 s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
cam.location=frontloc;cam.rotation_euler=frontrot;cam.data.ortho_scale=frontscale;assert sha(out/'receipt.json')==strictsha and sha(src)==source_sha and sha(frozen)==frozen_sha;print('RESULT diagnostic only, strict receipt/source/frozen patch unchanged')
