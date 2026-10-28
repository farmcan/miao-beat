"""Free, local-only fixed upstream tools probe on a disposable evaluated C8 copy.
Tests API compatibility and visible-surface queries; never changes the original asset.
"""
import bpy,sys,json,hashlib,time,numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'artifacts/blender-skills-research';out.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'design/character-sculpt-v2/vendor/scenario-blender'))
import bx_sculpt as S,bx_retopo as R
src=root/'artifacts/character-fidelity-c8-r2/miao-c8-reference-hold.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src);start=time.time()
def main():
 bpy.ops.wm.open_mainfile(filepath=str(src));original=bpy.data.objects['Miao / continuous pear and rounded-square face'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(original.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);work=bpy.data.objects.new('Skill API probe / disposable C8 copy',mesh);bpy.context.scene.collection.objects.link(work);work.matrix_world=original.matrix_world.copy();work.hide_render=True
 reports={}
 for name,center,hu,hv in [('mouth',(.075,-.5,2.77),.23,.13),('picking_palm',(-.55,-1.1,1.70),.18,.14),('fretting_palm',(1.20,-1,1.94),.16,.22),('ear',(.43,-.2,3.28),.15,.16)]:
  pts,normals=S.surface_samples(work,(0,1,0),center,hu,hv,grid=7)
  assert len(pts)>8,(name,len(pts));radii=S.curvature_radius(work,pts,.06);reports[name]={'actual_ray_hits':len(pts),'front_facing_samples':int((normals[:,1]<0).sum()),'median_radius_scene_units':float(np.nanmedian(radii)),'note':'Local curvature and sampling diagnostic only; not a likeness, craftsmanship or motion pass.'}
 sc=S.Sculptor(work,symmetry_x=False,front_faces_only=True);base=sc.co.copy();point=sc.on_surface((.075,-2,2.77),(0,1,0));sc.mask_by(lambda co:co[:,2]>2.92);sc.grab(point,.20,(0,-.005,0),front=True);delta=np.linalg.norm(sc.co-base,axis=1);changed=int((delta>1e-9).sum());assert changed>0 and delta.max()<=.00501
 key=S.write_shape_key(work,'Disposable compatibility probe',sc.co);assert len(key.data)==len(base)
 stations=R.joint_stations(Vector((0,0,0)),Vector((0,0,1)),Vector((.4,0,1.7)),spacing=.1);assert len(stations)>=5
 assert sha(src)==before
 result={'blender':bpy.app.version_string,'upstream_commit':'d44410f058991f677ccf733a8e86ce95110857eb','upstream_repository':'https://github.com/scenario-labs/skills','source_blend_sha256':before,'source_unchanged':True,'sculpt_module_sha256':sha(S.__file__),'retopo_module_sha256':sha(R.__file__),'headless_local_api_test':{'surface_query':reports,'mask_and_grab_changed_vertices':changed,'maximum_grab_displacement':float(delta.max()),'shape_key_on_disposable_copy':True,'joint_stations_count':len(stations)},'seconds':time.time()-start,'limits':['No API key, remote model, MCP server or paid service used.','No original geometry or published art altered.','This is a compatibility probe, not polished sculpting, clean retopology, rigging or motion proof.','Human-head ratios and symmetrical defaults were not applied to this posed stylized cat.']}
 (out/'local-api-probe.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps(result))
main()
