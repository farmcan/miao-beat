"""C24: one 45-degree surface-flow forehead patch, unchanged short C21 fibers.

Uses the installed official Rotate Hair Curves asset and pinned MIT bx_hair
socket setters. No guide generation, density/length/radius/shader/light scan.
"""
import argparse,hashlib,importlib.util,json,math,sys,time
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SHA='edf1bc40172c5f9bbd459ccf4ba9314a9dd5ccb28b67617de49ace533dc4bb1f'
LIB=Path('/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/procedural_hair_node_assets.blend')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def stats(v):
    v=np.asarray(v);return dict(count=len(v),min=float(v.min()),mean=float(v.mean()),median=float(np.median(v)),p90=float(np.quantile(v,.9)),max=float(v.max()))

def hair_state(h):
    ev=h.evaluated_get(bpy.context.evaluated_depsgraph_get());cv=ev.data
    p=np.empty(len(cv.position_data)*3,np.float32);cv.position_data.foreach_get('vector',p)
    radius=np.empty(len(cv.attributes['radius'].data),np.float32);cv.attributes['radius'].data.foreach_get('value',radius)
    extra={}
    for name in ['curve_type','resolution','miao_rest_position','surface_uv_coordinate']:
        a=cv.attributes.get(name)
        if a is not None:
            field='vector' if a.data_type in {'FLOAT_VECTOR','FLOAT2'} else 'value'
            dim=3 if a.data_type=='FLOAT_VECTOR' else 2 if a.data_type=='FLOAT2' else 1
            x=np.empty(len(a.data)*dim,np.float32 if a.data_type!='INT8' else np.int8)
            a.data.foreach_get(field,x);extra[name]=hashlib.sha256(x.tobytes()).hexdigest()
        else:extra[name]=None
    return p.reshape(-1,4,3).astype(float),radius.copy(),extra,len(cv.curves)

def project(points,hair,cam):
    matrix=np.asarray(hair.matrix_world);world=points@matrix[:3,:3].T+matrix[:3,3]
    dg=bpy.context.evaluated_depsgraph_get();vp=np.asarray(cam.calc_matrix_camera(dg,x=1024,y=1024)@cam.matrix_world.inverted())
    clip=np.concatenate([world,np.ones((*world.shape[:2],1))],axis=2)@vp.T
    return world,(clip[:,:,:2]/clip[:,:,3:]+1)/2

def modifier_asset(hair,H):
    # The operator-based upstream add_asset returns before async Essentials loading
    # finishes in this headless 5.2.3 environment. Append the same native asset
    # synchronously, then use its verified interface through unmodified setters.
    with bpy.data.libraries.load(str(LIB),link=False) as (source,target):
        assert 'Rotate Hair Curves' in source.node_groups
        target.node_groups=['Rotate Hair Curves']
    md=hair.modifiers.new('C24 / masked surface-flow rotation','NODES');md.node_group=target.node_groups[0]
    assert list(hair.modifiers)[-1]==md
    H.set_inputs(md,{'Axis':'attr:c24_flow_axis','Angle':0.0,'Factor':1.0,
                     'Random Offset':0.0,'Lock Ends':False,'Seed':17})
    return md

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/character-plush-flow-c24')
    a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    if (out/'receipt.json').exists():raise RuntimeError('Use fresh directory; preserve previous candidate')
    (out/'executed-script.py').write_bytes(Path(__file__).read_bytes())
    helper_path=ROOT/'design/character-sculpt-v2/eye-optics-diagnostic.py'
    spec=importlib.util.spec_from_file_location('snapshots',helper_path);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_hair as H
    src=ROOT/'artifacts/character-plush-short-fiber-c21-r2/miao-fiber-scattering-candidate.blend';assert sha(src)==SHA
    bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;origcam=s.camera;original_matrix=origcam.matrix_world.copy()
    geom,lights,materials=h.geometry_hash(),h.light_snapshot(),h.material_snapshot()
    hair=bpy.data.objects['Miao / native short plush'];body=bpy.data.objects['Miao / continuous pear and rounded-square face']
    before,radius0,extra0,count0=hair_state(hair);assert count0==180000 and before.shape==(180000,4,3)
    original_raw=np.empty(len(hair.data.position_data)*3,np.float32);hair.data.position_data.foreach_get('vector',original_raw)
    packet=json.loads((ROOT/'artifacts/character-head-c14-color/receipt.json').read_text());head=next(q for q in packet['renders'] if q['name']=='color-head-front')
    cam=origcam.copy();cam.data=origcam.data.copy();cam.name='C24 / temporary matched head camera';s.collection.objects.link(cam)
    cam.matrix_world=Matrix(head['camera_matrix']);cam.data.type=head['type'];cam.data.lens=head['lens'];bpy.context.view_layer.update()
    world,uv=project(before,hair,cam);roots=uv[:,0];roi=[.375,.625,.588,.644]
    selected=np.flatnonzero((roots[:,0]>=roi[0])&(roots[:,0]<=roi[1])&(roots[:,1]>=roi[2])&(roots[:,1]<=roi[3]))
    dg=bpy.context.evaluated_depsgraph_get();bodytree=BVHTree.FromObject(body,dg);inv=body.matrix_world.inverted();eye=cam.matrix_world.translation.copy()
    visible=[];normals={};root_errors=[]
    normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
    for i in selected:
        point=Vector(world[i,0]);direction=(point-eye).normalized()
        hit,n,face,d=bodytree.ray_cast(inv@eye,inv.to_3x3()@direction,20)
        if hit is not None:
            error=(body.matrix_world@hit-point).length
            if error<1e-4:
                visible.append(i);normals[i]=np.asarray((normal_matrix@n).normalized());root_errors.append(error)
    assert len(visible)==549,'Predeclared baseline visible-root audit no longer matches'
    visible=np.asarray(visible,int)
    # Hypothesis: a small sideward forehead nap, not a reconstructed full-body flow.
    # Fade the angle itself; mixing positions would shorten strands at the boundary.
    axes=np.tile(np.array([0.,0.,1.]),(count0,1));angles=np.zeros(count0,np.float32)
    weights=np.zeros(count0,np.float64)
    for i in visible:
        x,y=roots[i];dx=min(x-roi[0],roi[1]-x)/.025;dy=min(y-roi[2],roi[3]-y)/.006
        fx=float(np.clip(dx,0,1));fy=float(np.clip(dy,0,1));fade=(fx*fx*(3-2*fx))*(fy*fy*(3-2*fy))
        N=normals[i];T=np.array([1.,0.,0.])-N[0]*N;T/=np.linalg.norm(T)
        axis=np.cross(N,T);axis/=np.linalg.norm(axis)
        axes[i]=np.asarray(hair.matrix_world.inverted().to_3x3()@Vector(axis)).astype(float)
        axes[i]/=np.linalg.norm(axes[i]);weights[i]=fade;angles[i]=math.pi/4*fade
    changed=np.flatnonzero(angles>0);assert len(changed)>0
    a_axis=hair.data.attributes.new('c24_flow_axis','FLOAT_VECTOR','CURVE');a_axis.data.foreach_set('vector',axes.astype(np.float32).ravel())
    a_angle=hair.data.attributes.new('c24_flow_angle','FLOAT','CURVE');a_angle.data.foreach_set('value',angles)
    md=modifier_asset(hair,H);bpy.context.view_layer.update()
    zero,radius_zero,extra_zero,count_zero=hair_state(hair)
    zero_error=np.linalg.norm(zero-before,axis=2) if zero.shape==before.shape else np.array([float('inf')])
    (out/'zero-angle-geometry-control.json').write_text(json.dumps(dict(count_before=count0,count_after=count_zero,shape_before=before.shape,shape_after=zero.shape,position_max_error=float(zero_error.max()),position_error=stats(zero_error.ravel()),radii_exact=bool(np.array_equal(radius_zero,radius0)),metadata_before=extra0,metadata_after=extra_zero),indent=2)+'\n')
    assert count_zero==count0 and zero.shape==before.shape and zero_error.max()<1e-8 and np.array_equal(radius_zero,radius0), 'Zero-angle asset changed actual geometry'
    assert {k:v for k,v in extra_zero.items() if k!='resolution'}=={k:v for k,v in extra0.items() if k!='resolution'}, 'Zero-angle asset changed type/rest/UV'
    evaluated=hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    resolution=evaluated.attributes.get('resolution')
    assert extra0['resolution'] is None and resolution is not None
    assert resolution.data_type=='INT' and resolution.domain=='CURVE' and len(resolution.data)==count0
    resolution_values=np.empty(count0,np.int32);resolution.data.foreach_get('value',resolution_values)
    assert np.all(resolution_values==12), 'Unexpected resolution metadata change'
    metadata_proof=dict(attribute='resolution',before='absent',after='INT CURVE, all 12',zero_angle_position_max_error=float(zero_error.max()),zero_angle_position_tolerance=1e-8,zero_angle_radii_bit_exact=True,zero_angle_type_rest_uv_exact=True)
    H.set_inputs(md,{'Angle':'attr:c24_flow_angle'});bpy.context.view_layer.update()
    after,radius1,extra1,count1=hair_state(hair)
    assert count1==count0 and after.shape==before.shape and np.array_equal(radius0,radius1)
    assert extra_zero==extra1,'Rotation changed metadata relative to zero-angle native asset; stop before render'
    raw1=np.empty_like(original_raw);hair.data.position_data.foreach_get('vector',raw1);assert np.array_equal(original_raw,raw1)
    root_delta=np.linalg.norm(after[:,0]-before[:,0],axis=1);assert root_delta.max()<1e-6
    beforelength=np.linalg.norm(np.diff(before,axis=1),axis=2).sum(axis=1);afterlength=np.linalg.norm(np.diff(after,axis=1),axis=2).sum(axis=1)
    length_error=np.abs(afterlength-beforelength)/beforelength;assert length_error.max()<5e-4
    outside=np.ones(count0,bool);outside[changed]=False
    outside_error=np.linalg.norm(after[outside]-before[outside],axis=2);assert outside_error.max()<1e-6
    offset=before[changed]-before[changed,0,None,:];axis=axes[changed,None,:];ang=angles[changed,None,None]
    expected=before[changed,0,None,:]+offset*np.cos(ang)+np.cross(axis,offset)*np.sin(ang)+axis*(axis*offset).sum(axis=2)[:,:,None]*(1-np.cos(ang))
    rigid_error=np.linalg.norm(expected-after[changed],axis=2);assert rigid_error.max()<1e-6,'Not the explicitly intended root-pivot rotation'
    world1,uv1=project(after,hair,cam)
    # Strict body clearance along every modified segment, not nearest fallback authoring.
    signed=[];eye_intersections=[]
    eye_objects=[o for o in s.objects if not o.hide_render and o.type=='MESH' and o.name.startswith(('C6 / sclera','C6 / iris','C7 / clear cornea'))]
    eye_trees=[(o,BVHTree.FromObject(o,dg),o.matrix_world.inverted()) for o in eye_objects]
    for i in changed:
        for j in range(3):
            A=Vector(world1[i,j]);B=Vector(world1[i,j+1])
            for t in [.25,.5,.75,1.]:
                P=A.lerp(B,t);near,n,face,d=bodytree.find_nearest(inv@P);assert near is not None
                gap=(P-body.matrix_world@near).dot((normal_matrix@n).normalized());signed.append(gap)
                if gap < -1e-5:raise RuntimeError('Rotated strand enters skin; stop')
            for ob,tree,iv in eye_trees:
                a0=iv@A;b0=iv@B;direction=b0-a0;length=direction.length
                if length>0:
                    hit=tree.ray_cast(a0,direction/length,length)[0]
                    if hit is not None:eye_intersections.append(dict(curve=int(i),segment=j,object=ob.name))
    assert not eye_intersections,'Hair intersects an eye surface; stop'
    def projection_metrics(points,screen):
        length=np.linalg.norm(np.diff(screen[visible]*1024,axis=1),axis=2).sum(axis=1)
        D=points[visible,-1]-points[visible,0];D/=np.linalg.norm(D,axis=1)[:,None]
        V=np.asarray(eye)-points[visible,0];V/=np.linalg.norm(V,axis=1)[:,None]
        angle=np.degrees(np.arccos(np.clip(np.abs((D*V).sum(axis=1)),0,1)))
        return dict(projected_polyline_pixels_at_1024=stats(length),strand_angle_to_view_degrees=stats(angle),fraction_under_one_pixel=float((length<1).mean()))
    assert h.geometry_hash()==geom and h.light_snapshot()==lights and h.material_snapshot()==materials and sha(src)==SHA
    s.camera=origcam;assert origcam.matrix_world==original_matrix
    bpy.data.objects.remove(cam,do_unlink=True)
    bpy.context.preferences.filepaths.save_version=0
    native=out/'miao-c24-forehead-flow-patch.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
    result=dict(stage='C24-one-native-direction-patch',status='geometry-valid-rendering-diagnostic',input_sha256=SHA,source_sha256=sha(__file__),
                native_sha256=sha(native),helper_sha256=sha(ROOT/'design/character-sculpt-v2/vendor/scenario-blender/bx_hair.py'),
                native_asset_path=str(LIB),native_asset_file_sha256=sha(LIB),asset_inputs=H.get_inputs(md),
                mask=dict(root_roi_normalized=roi,fade_x=.025,fade_y=.006,visible_body_ray_tolerance=1e-4,projected_roots=len(selected),visible_roots=len(visible),changed_curves=len(changed),fully_45_degree_curves=int((weights>.999999).sum()),tangent_design='world +X projected onto actual body-root tangent plane; single-patch artistic flow hypothesis, not proven full anatomy'),
                geometry_checks=dict(curves=count1,points=int(after.size/3),root_displacement=stats(root_delta),relative_polyline_length_error=stats(length_error),rigid_rotation_residual_max=float(rigid_error.max()),outside_patch_point_displacement_max=float(outside_error.max()),radii_exactly_unchanged=True,type_rest_and_uv_hashes_unchanged=True,metadata_hashes_after_zero_angle_control=extra1,native_asset_metadata_control=metadata_proof,skin_clearance_samples=len(signed),minimum_signed_skin_clearance=float(min(signed)),eye_segment_hits=eye_intersections),
                projection_before=projection_metrics(world,uv),projection_after=projection_metrics(world1,uv1),body_material_lights_unchanged=True,
                limits=['Only one forehead patch; counts/length/radius/shader/light fixed.','Same old C21 eye stack solely for fur control; independently passed C20 unchanged.','No whole-character/plush pass, motion, Web, Cloudflare, fees, commit or push.'])
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    # Reuse the exact C21 same-buffer renderer, changing only input-native path.
    renderer=ROOT/'design/character-sculpt-v2/plush-denoise-diagnostic.py';text=renderer.read_text()
    old='artifacts/character-plush-short-fiber-c21-r2/miao-fiber-scattering-candidate.blend'
    assert text.count(old)==1
    text=text.replace(old,str(native.relative_to(ROOT)))
    text=text.replace('ROOT = Path(__file__).resolve().parents[2]', "ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'public/sampled-audio.js').is_file())")
    render_script=out/'samebuffer-render.py';render_script.write_text(text)
    namespace={'__file__':str(render_script),'__name__':'c24_samebuffer_reuse'}
    exec(compile(text,str(render_script),'exec'),namespace)
    saved_args=sys.argv[:];sys.argv=[str(render_script),'--','--out',str(out/'render'),'--samples','128','--coverage']
    try:namespace['main']()
    finally:sys.argv=saved_args
    assert sha(src)==SHA and sha(native)==result['native_sha256']
    result.update(status='one-patch-rendered-awaiting-builder-inspection-and-independent-reviews',samebuffer_upstream_source_sha256=sha(renderer),samebuffer_executed_source_sha256=sha(render_script),render_receipt_sha256=sha(out/'render/receipt.json'))
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps(result),flush=True)

if __name__=='__main__':main()
