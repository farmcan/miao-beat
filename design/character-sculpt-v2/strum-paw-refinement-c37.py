"""C37: one reference-driven same-topology right strumming-paw cap study.

Anatomical right = screen left over soundhole. C35 left neck-gripping paw,
guitar, head/ears/pear and all vertices outside compact distal mask stay exact.
No primitive, remesh, separate limb, animation, paid service or public output.
"""
import bpy, bmesh, numpy as np, json, hashlib, sys, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/character-strum-paw-c37'; OUT.mkdir(exist_ok=True)
SRC=ROOT/'artifacts/character-paw-grip-c35/miao-c35-fixed-vertex-tessellation.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'))
import bx_audit as A

def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)

def arr(me):
    a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);return a.reshape(-1,3)

def topo(me):
    bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();seen=set();nc=0
    for v in bm.verts:
        if v.index in seen:continue
        nc+=1;stack=[v];seen.add(v.index)
        while stack:
            p=stack.pop()
            for e in p.link_edges:
                q=e.other_vert(p)
                if q.index not in seen:seen.add(q.index);stack.append(q)
    r=dict(vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),components=nc,boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges))
    bm.free();return r

def fingerprint(ob):
    r={'type':ob.type,'matrix':list(map(list,ob.matrix_world)),'hide_render':ob.hide_render}
    dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg)
    if ob.type in {'MESH','CURVE','CURVES'}:
        me=ev.to_mesh();me.calc_loop_triangles();r.update(evaluated_vertices=len(me.vertices),co_sha256=hashlib.sha256(arr(me).tobytes()).hexdigest(),tri_sha256=hashlib.sha256(np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32).tobytes()).hexdigest());ev.to_mesh_clear()
    return r

def actual_tree(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();co=[ob.matrix_world@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(co,tri,all_triangles=True);ev.to_mesh_clear();return tree,len(tri)

def local_stats(body,co,face_ids):
    me=body.data;used=sorted({i for fi in face_ids for i in me.polygons[fi].vertices});mp={i:j for j,i in enumerate(used)};lm=bpy.data.meshes.new('C37 temporary audit');lm.from_pydata(co[used],[],[[mp[i] for i in me.polygons[f].vertices] for f in face_ids]);lm.update();lo=bpy.data.objects.new('C37 temporary audit',lm);bpy.context.collection.objects.link(lo);r=A.audit(lo);bpy.data.objects.remove(lo,do_unlink=True);bpy.data.meshes.remove(lm);return r

def main():
    started=time.time();srcsha=sha(SRC);bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.view_layer.update();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];me=body.data;s=bpy.context.scene;original=arr(me).copy();beforetopo=topo(me)
    assert not body.modifiers and not me.shape_keys
    protected={o.name:fingerprint(o) for o in bpy.data.objects if o.name.startswith('Guitar /')}
    attrs={a.name:np.array([x.value for x in a.data]) for a in me.attributes if a.domain=='POINT' and a.data_type in {'INT','BOOLEAN'}}
    C=np.array([-.58,-1.19,1.80]);D=np.array([.78,0,-.625]);D/=np.linalg.norm(D);T=np.array([.625,0,.78]);T/=np.linalg.norm(T);P=original.astype(np.float64);ss=(P-C)@D;tt=(P-C)@T
    mask=smooth((P[:,0]+.98)/.13)*(1-smooth((P[:,0]+.25)/.06))*smooth((-.88-P[:,1])/.10)*smooth((P[:,2]-1.42)/.10)*(1-smooth((P[:,2]-2.04)/.08))*smooth((ss+.12)/.15)
    # This is an explicit finite authored mask, not nearest matching to another mesh.
    edit=mask>0;assert not np.any(edit&(P[:,0]>0));ids=np.flatnonzero(edit);mapping=np.full(len(P),-1,np.int32);mapping[ids]=np.arange(len(ids));edges=np.array([tuple(e.vertices) for e in me.edges],np.int32);edges=edges[edit[edges].any(1)];ii=np.r_[edges[:,0],edges[:,1]];jj=np.r_[edges[:,1],edges[:,0]];keep=edit[ii];ii=ii[keep];jj=jj[keep];count=np.bincount(mapping[ii],minlength=len(ids));Q=P.copy()
    # Fair the square boolean recesses before making broad toe structure. The
    # zero-value smooth boundary is fixed; no smoothing over the wrist/arm root.
    fairweight=mask*smooth((ss+.02)/.16)
    for k in range(80):
        sums=np.stack([np.bincount(mapping[ii],weights=Q[jj,d],minlength=len(ids)) for d in range(3)],axis=1);mean=sums/count[:,None];Q[ids]+=.35*fairweight[ids,None]*(mean-Q[ids])
    fair=Q-P
    # Soft shape of a short 3-toe cap. Two broad web setbacks change the outside
    # cap contour, instead of boolean grooves or detached finger spheres.
    distal=smooth((ss-.035)/.21);web=np.exp(-((tt+.063)/.029)**2)+np.exp(-((tt-.064)/.029)**2)
    ds=mask*distal*(-.014-.034*web-.014*smooth((np.abs(tt)-.10)/.08))
    dt=-.055*tt*mask*distal
    dy=-.16*(P[:,1]+1.22)*mask*smooth((ss+.015)/.25)
    Q+=ds[:,None]*D+dt[:,None]*T;Q[:,1]+=dy
    delta=Q-P;maximum=float(np.linalg.norm(delta,axis=1).max());assert maximum<.075,maximum;Q[~edit]=P[~edit]
    np.savez_compressed(OUT/'authored-delta-and-locks.npz',original=original,delta=delta.astype(np.float32),edit_ids=ids,edit_weight=mask[ids].astype(np.float32),source_vertex_ids=attrs['C23 source vertex id'][ids],palm_axis=D,lateral_axis=T,origin=C)
    me.calc_loop_triangles();tris=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32);tf=np.array([t.polygon_index for t in me.loop_triangles]);affected=np.any(edit[tris],axis=1);face_ids=sorted(set(tf[affected]));collar_ids={f.index for f in me.polygons if any(edit[i] for i in f.vertices)};used={i for f in collar_ids for i in me.polygons[f].vertices};collar_ids=sorted({f.index for f in me.polygons if any(i in used for i in f.vertices)})
    obstacles={name:actual_tree(bpy.data.objects[name]) for name in protected if bpy.data.objects[name].type in {'MESH','CURVE'} and not bpy.data.objects[name].hide_render}
    def crosses(co):
        tree=BVHTree.FromPolygons(co,[tuple(x) for x in tris[affected]],all_triangles=True);return {name:{'actual_evaluated_obstacle_triangles':n,'actual_intersection_pairs':len(tree.overlap(gt))} for name,(gt,n) in obstacles.items()}
    beforecross=crosses(P);baseline=local_stats(body,P,collar_ids);me.vertices.foreach_set('co',Q.astype(np.float32).ravel());me.update();bpy.context.view_layer.update();actual=arr(me);aftertopo=topo(me);aftercross=crosses(actual);afterlocal=local_stats(body,actual,collar_ids)
    a0=P[tris[affected]];a1=actual[tris[affected]];n0=np.cross(a0[:,1]-a0[:,0],a0[:,2]-a0[:,0]);n1=np.cross(a1[:,1]-a1[:,0],a1[:,2]-a1[:,0]);area0=np.linalg.norm(n0,axis=1);area1=np.linalg.norm(n1,axis=1);valid=area0>1e-12;dots=(n0[valid]*n1[valid]).sum(1)/(area0[valid]*area1[valid]);flips=int((dots<=0).sum());attrs_exact=all(np.array_equal(v,np.array([x.value for x in me.attributes[k].data])) for k,v in attrs.items());outside_exact=bool(np.array_equal(actual[~edit],original[~edit]));left=original[:,0]>.5;left_exact=bool(np.array_equal(actual[left],original[left]));guitar_exact=protected=={name:fingerprint(bpy.data.objects[name]) for name in protected};no_new_guitar=all(aftercross[k]['actual_intersection_pairs']<=beforecross[k]['actual_intersection_pairs'] for k in beforecross)
    # Actual affected triangles against the complete body, excluding topological
    # neighbours. This catches crossings with retained arm/body, not just cap self.
    whole=BVHTree.FromPolygons(actual,[tuple(t) for t in tris],all_triangles=True);sub=BVHTree.FromPolygons(actual,[tuple(t) for t in tris[affected]],all_triangles=True);affected_indices=np.flatnonzero(affected);selfpairs=[]
    for i,j in sub.overlap(whole):
        ti=int(affected_indices[i])
        if ti==j or set(tris[ti])&set(tris[j]):continue
        if affected[j] and ti>j:continue
        selfpairs.append([ti,j,int(tf[ti]),int(tf[j])])
    passed=outside_exact and left_exact and guitar_exact and attrs_exact and beforetopo==aftertopo and aftertopo['components']==1 and aftertopo['boundary_edges']==0 and aftertopo['nonmanifold_edges']==0 and afterlocal['self_intersections']==0 and afterlocal['flipped_faces']==0 and not selfpairs and flips==0 and no_new_guitar
    receipt={'stage':'C37-one-same-topology-right-strum-paw-static-gray','source_native':str(SRC),'source_native_sha256':srcsha,'script_sha256':sha(__file__),'reference_sha256':sha(ROOT/'public/character/instrument-scenes-v1/guitar/idle.jpg'),'direction':'Anatomical right strumming paw is screen-left over soundhole; C35 neck-gripping anatomical left is screen-right.','design':{'edit_region':'compact smooth mask: x[-.98,-.19], y<-.88, z[1.42,2.12], palm-axis s>-.12; plateau/influence all written in script and NPZ','protected':'All mask-zero original vertices, head/ears/pear, shoulder/upper arm, all left C35, all guitar data/transforms exact.','method':'80 fixed .35 weighted local Laplace steps on old square recesses; 2 broad palm-axis web setbacks .034u, cap setback .014u, lateral taper5.5%, distal depth compression16%. No topology change.','palm_axis':D.tolist(),'lateral_axis':T.tolist(),'origin':C.tolist(),'one_candidate':True},'changed_vertices':int(np.count_nonzero(np.linalg.norm(actual-original,axis=1)>0)),'editable_vertices':len(ids),'maximum_displacement':maximum,'maximum_fairing_displacement':float(np.linalg.norm(fair,axis=1).max()),'before_topology':beforetopo,'after_topology':aftertopo,'outside_edit_region_bit_exact':outside_exact,'left_C35_all_vertices_bit_exact':left_exact,'guitar_all_geometry_transform_visibility_bit_exact':guitar_exact,'source_and_all_integer_vertex_attributes_exact':attrs_exact,'baseline_local_audit':baseline,'after_local_audit':afterlocal,'affected_triangle_normal_reversals':flips,'minimum_affected_normal_dot':float(dots.min()),'affected_vs_whole_body_non_neighbour_triangle_crossings':len(selfpairs),'self_pair_sample':selfpairs[:20],'baseline_actual_guitar_intersections':beforecross,'after_actual_guitar_intersections':aftercross,'no_increased_actual_guitar_intersections':no_new_guitar,'render_gate_passed':passed,'limits':['Static shape study; no new strum contact target/path or natural motion acceptance.','Existing right-paw guitar intersections, if any, are explicitly reported and do not become a contact pass.','Same dense topology is not deformation-ready retopology, UV/groom or rig proof.','Builder inspection and independent three-role review still required.','C35 whole-character head/ears/pear issues are outside this candidate.'],'seconds_before_render':time.time()-started}
    native=OUT/('miao-c37-strum-paw.blend' if passed else 'diagnostic-c37-gate-failed.blend');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);receipt['native_sha256']=sha(native);(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESULT '+json.dumps({k:receipt[k] for k in ['render_gate_passed','changed_vertices','maximum_displacement','affected_triangle_normal_reversals','affected_vs_whole_body_non_neighbour_triangle_crossings','no_increased_actual_guitar_intersections','native_sha256']}),flush=True)
    if not passed:return
    cam=s.camera;cl=cam.location.copy();cr=cam.rotation_euler.copy();cs=cam.data.ortho_scale;s.cycles.samples=16;s.cycles.seed=17;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;receipt['renders']=[]
    for view in ['front','right-paw','right-side']:
        if view=='right-paw':cam.location=(-.65,-12,2.7);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
        if view=='right-side':cam.location=(-4,-6,3.1);cam.rotation_euler=(Vector((-.65,-1.05,1.97))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.4
        file=OUT/('gray-'+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);receipt['renders'].append({'file':file.name,'sha256':sha(file),'camera':list(map(list,cam.matrix_world)),'ortho_scale':cam.data.ortho_scale});(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    cam.location=cl;cam.rotation_euler=cr;cam.data.ortho_scale=cs;assert sha(SRC)==srcsha

main()
