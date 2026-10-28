"""Read-only C12 anatomy diagnostics; no tolerance relaxation or scene edits."""
import bpy,bmesh,numpy as np,json,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'design/character-sculpt-v2/vendor/scenario-blender'));import bx_audit
p=argparse.ArgumentParser();p.add_argument('--input',default='artifacts/character-head-c12-r2/miao-c12-head-shell.blend');p.add_argument('--out',default='artifacts/character-head-c12-r2/geometry-audit.json');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 src=ROOT/a.input;before=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));body=bpy.data.objects['Miao / continuous pear and rounded-square face'];dg=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);ev.to_mesh_clear();bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if (body.matrix_world@v.co).z<2.5],context='VERTS');bm.verts.index_update();bm.faces.index_update();bm.faces.ensure_lookup_table();bm.normal_update();n=len(bm.faces);pairs=bx_audit._self_intersections(bm);head={'region':'body surface z>=2.5 only, open below cut','vertices':len(bm.verts),'faces':n,'self_intersections':pairs,'self_check_face_limit':200000,'check_skipped':pairs is None};bm.free()
 nose=bpy.data.objects['Face / rounded triangular nose'];bm=bmesh.new();bm.from_mesh(nose.data);bm.faces.ensure_lookup_table();bm.verts.index_update();bm.faces.index_update();nose_audit={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'self_intersections':bx_audit._self_intersections(bm)};bm.free()
 tree=BVHTree.FromObject(body,dg);iv=body.matrix_world.inverted();direction=(iv.to_3x3()@Vector((0,1,0))).normalized();curves=[]
 for o in bpy.context.scene.objects:
  if o.type!='CURVE' or not o.name.startswith(('Face / smile','Face / thick curved brow')):continue
  samples=[];miss=0
  for sp in o.data.splines:
   for b0,b1 in zip(sp.bezier_points[:-1],sp.bezier_points[1:]):
    A,B,C,D=[o.matrix_world@p for p in [b0.co,b0.handle_right,b1.handle_left,b1.co]]
    for t in np.linspace(0,1,65):
     P=A*(1-t)**3+B*3*(1-t)**2*t+C*3*(1-t)*t*t+D*t**3;loc,n,face,d=tree.ray_cast(iv@Vector((P.x,-3,P.z)),direction,8)
     if loc is None:miss+=1;continue
     skin=body.matrix_world@loc;gap=float(skin.y-P.y);radius=float(o.data.bevel_depth*((1-t)*b0.radius+t*b1.radius));samples.append({'t':float(t),'x':P.x,'z':P.z,'centerline_to_skin_gap':gap,'bevel_radius':radius,'center_more_than_radius_inside_skin':gap<-radius})
  gaps=[v['centerline_to_skin_gap'] for v in samples];curves.append({'name':o.name,'samples':len(samples),'ray_misses':miss,'gap_min':min(gaps) if gaps else None,'gap_max':max(gaps) if gaps else None,'center_more_than_radius_inside_skin':sum(v['center_more_than_radius_inside_skin'] for v in samples),'counterexamples':[v for v in samples if v['center_more_than_radius_inside_skin']][:8]})
 assert sha(src)==before
 r={'input_sha256':before,'input_unchanged':True,'body_head_subset':head,'nose':nose_audit,'actual_curve_skin_sampling':curves,'limits':['Head subset self-check excludes torso, eye/nose/body intersections and any animation.','Curve-centerline behind skin more than bevel radius is a strong occlusion diagnostic; not a ray-traced visibility proof from every camera.','Zero primitive self-intersections cannot override failed appearance or original-reference judgments.']};(ROOT/a.out).write_text(json.dumps(r,indent=2)+'\n');print('RESULT '+json.dumps(r))
main()
