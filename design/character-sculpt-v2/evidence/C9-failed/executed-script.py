"""C9 primary forms with pinned MIT bx_sculpt, not a finished art or animation claim.
A disposable evaluated copy receives local brushes; deltas become one additional key
on the complete connected source body. Existing C8 pose stays at 1, UV/groom preserved.
"""
import bpy,sys,json,hashlib,numpy as np,math,time,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/character-anatomy-c9');p.add_argument('--size',type=int,default=1024);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path.home()/'.codex/skills/scenario-blender-sculpting/scripts'));import bx_sculpt as S
src=root/'artifacts/character-fidelity-c8-r2-color/miao-c8-reference-hold.blend';out=root/a.out;out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();input_sha=sha(src)
def getco(o):
 v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);return v.reshape(-1,3)
def main():
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;body=bpy.data.objects['Miao / continuous pear and rounded-square face'];hair=bpy.data.objects['Miao / native short plush'];s.render.resolution_x=s.render.resolution_y=a.size;s.cycles.samples=32;s.cycles.seed=17;s.render.use_border=False;s.render.use_crop_to_border=False
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(body.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);work=bpy.data.objects.new('C9 / disposable sculpt work',me);s.collection.objects.link(work);work.matrix_world=body.matrix_world.copy();work.hide_render=True
 sc=S.Sculptor(work,symmetry_x=False,front_faces_only=True);baseline=sc.co.copy();ops=[]
 def point(x,z):return sc.on_surface(sc.to_local((x,-3,z)),(0,1,0))
 # This is a cartoon plush reference: no human head_guides/jaw recipe/symmetry.
 sc.mask[:]=np.clip((sc.co[:,2]-2.88)/.055,0,1)
 for x,z,r,h in [(-.060,2.775,.215,.029),(.220,2.775,.215,.029),(.075,2.655,.235,.021)]:
  pt=point(x,z);n=sc.dab('inflate',pt,r,strength=.25,height=h,front=True);ops.append({'part':'muzzle/cheek/chin mass','point':pt.tolist(),'radius':r,'height':h,'changed_vertices':n})
 # Complete fretting palm: lift the hanging lower pad, restore rounded palm-back.
 sc.clear_mask();sc.mask_by(lambda c:(c[:,0]<.78)|(c[:,1]>-.72)|(c[:,2]>2.36))
 pt=point(1.19,1.89);n=sc.move_feature(pt,.24,translate=(0,-.005,.055),scale=(.97,1, .96),front=True);ops.append({'part':'shorten lower palm pad','changed_vertices':n})
 pt=point(1.205,2.045);n=sc.dab('inflate',pt,.185,strength=.2,height=.024,front=True);ops.append({'part':'palm back soft volume','changed_vertices':n})
 # Fold down top protrusions; this is a bounded primary mass correction, not an
 # individually articulated finger rig or a completed reconstruction.
 for x,z in [(1.095,2.235),(1.225,2.245)]:
  pt=point(x,z);n=sc.move_feature(pt,.145,translate=(0,-.018,-.038),scale=(1,1,.94),front=True);ops.append({'part':'curled toe mass','point':pt.tolist(),'changed_vertices':n})
 # Soften the actual ear rim and primary bowl, not a separate ear image.
 sc.clear_mask();sc.mask_by(lambda c:c[:,2]<3.13)
 for side in [-1,1]:
  center=point(side*.43,3.285);sc.smooth(center,.205,strength=.18,iterations=3,preserve_volume=True);n=sc.dab('inflate',center,.12,strength=.15,height=.008,front=True);ops.append({'part':'ear primary shell/rim','changed_vertices':n})
 delta=sc.co-baseline;basis=np.empty(len(body.data.vertices)*3,np.float32);body.data.shape_keys.key_blocks['Basis'].data.foreach_get('co',basis);basis=basis.reshape(-1,3)
 key=S.write_shape_key(body,'C9 / primary mouth paw ear sculpt',basis+delta);assert body.data.shape_keys.key_blocks['C8 / reference hold sculpt'].value==1
 bpy.data.objects.remove(work,do_unlink=True);bpy.data.meshes.remove(me);bpy.context.view_layer.update()
 # Embed mouth curves in the new skin instead of leaving them floating on a plane.
 tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());iv=body.matrix_world.inverted();forward=(iv.to_3x3()@Vector((0,1,0))).normalized();mouth=[]
 for o in list(s.objects):
  if o.type=='CURVE' and o.name.startswith(('Face / smile','Face / smile stem')):
   oi=o.matrix_world.inverted()
   for spl in o.data.splines:
    for bp in spl.bezier_points:
     w=o.matrix_world@bp.co;hit,n,_,_=tree.ray_cast(iv@Vector((w.x,-3,w.z)),forward,8)
     if hit is not None:
      target=body.matrix_world@(hit+n*.0025);shift=oi@target-bp.co;bp.co+=shift;bp.handle_left+=shift;bp.handle_right+=shift;mouth.append(list(target))
 # Geometry/groom counts stay untouched; native roots follow the deformed skin.
 assert len(body.data.vertices)==609383 and len(hair.data.curves)==180000
 s.render.filepath='//renders/c9.png';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'miao-c9-primary-anatomy.blend'),compress=True)
 mats={}
 for name,v in [('body',.4),('white',.72),('dark',.045),('wood',.30)]:
  m=bpy.data.materials.new('C9 gray '+name);b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(v,v,v,1);b.inputs['Roughness'].default_value=.65;mats[name]=m
 for o in list(s.objects):
  if o.type not in {'MESH','CURVES','CURVE'} or o.hide_render or o.name.startswith(('Studio /','Authoring /','D0 /','C7 / clear')):continue
  k='white' if o.name.startswith('C6 / sclera') else 'dark' if o.name.startswith(('C6 / iris','Face /')) else 'wood' if o.name.startswith('Guitar /') else 'body';o.data.materials.clear();o.data.materials.append(mats[k])
 for view in ['front','three-quarter']:
  if view!='front':cam=s.camera;cam.location=(6,-9,3.9);cam.rotation_euler=(Vector((.09881,0,1.609))-cam.location).to_track_quat('-Z','Y').to_euler()
  s.render.filepath=str(out/('gray-'+view+'.png'));bpy.ops.render.render(write_still=True)
 result={'stage':'C9-primary-form-gray-unreviewed','upstream_commit':'d44410f058991f677ccf733a8e86ce95110857eb','sculpt_helper_sha256':sha(S.__file__),'input_sha256':input_sha,'input_unchanged':sha(src)==input_sha,'operations':ops,'maximum_delta':float(np.linalg.norm(delta,axis=1).max()),'body_vertices':len(body.data.vertices),'groom_curves':len(hair.data.curves),'new_shape_key':key.name,'mouth_curve_skin_targets':mouth,'limits':['Primary local forms with local numpy brushes, not live GUI surface polish.','No clean finger retopology, full eyelid closure, bone rig, Godot character or motion acceptance.','Three independent actual-image gray reviews required before colored gate/animation.','All delivered frames show the full connected cat and instrument; no separate arm image/geometry composition.']};(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT '+json.dumps(result))
main()
