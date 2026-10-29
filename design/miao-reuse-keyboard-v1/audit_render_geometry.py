"""Capture exact render depsgraph where available; no source or pose modification."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];N=R/'artifacts/miao-reuse-keyboard-v1/gray-static/keyboard-gray-native36.blend';O=R/'artifacts/miao-reuse-keyboard-v1/support-prop';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(N);bpy.ops.wm.open_mainfile(filepath=str(N),load_ui=False,use_scripts=False);s=bpy.context.scene
r={'native_sha256':before,'scene_simplify':{'use_simplify':s.render.use_simplify,'simplify_subdivision':s.render.simplify_subdivision,'simplify_subdivision_render':s.render.simplify_subdivision_render},'depsgraph_events':[],'exact_render':None}
def readgraph(dg):
 hand=bpy.data.objects['GEO-hands'];e=hand.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();p=[e.matrix_world@v.co for v in m.vertices];w=[{g.group:g.weight for g in v.groups} for v in m.vertices];result={'mode':dg.mode,'hand_vertices':len(p),'hand_tris':len(m.loop_triangles),'pads':{}}
 for side in ['L','R']:
  gi=hand.vertex_groups['DEF-Index2.'+side].index;ids=[i for i,v in enumerate(w) if v.get(gi,0)>.6]
  if ids:
   low=min(ids,key=lambda i:p[i].z);result['pads'][side]={'weighted_skin_vertices':len(ids),'lowest':list(p[low]),'vertical_gap_above_white_top_m':p[low].z-.3280000107}
 e.to_mesh_clear();o=bpy.data.objects['GEO-shoes'];ev=o.evaluated_get(dg);mm=ev.to_mesh();result['shoes_floor_z_m']=min((ev.matrix_world@v.co).z for v in mm.vertices);ev.to_mesh_clear();return result
r['viewport']=readgraph(bpy.context.evaluated_depsgraph_get())
def post(scene,dg):
 if len(r['depsgraph_events'])<30:r['depsgraph_events'].append(dg.mode)
 if dg.mode=='RENDER' and r['exact_render'] is None:r['exact_render']=readgraph(dg)
bpy.app.handlers.depsgraph_update_post.append(post)
s.render.resolution_x=64;s.render.resolution_y=64;s.render.resolution_percentage=100;s.eevee.taa_render_samples=1;s.render.filepath=str(O/'render-geometry-audit-thumbnail.png');bpy.ops.render.render(write_still=True)
bpy.app.handlers.depsgraph_update_post.remove(post)
# The source Subsurf render setting may be overridden globally by simplify.
r['effective_render_subsurf']=[{'object':o.name,'modifier':m.name,'viewport':m.levels,'render_setting':m.render_levels,'effective_render':min(m.render_levels,s.render.simplify_subdivision_render) if s.render.use_simplify else m.render_levels} for o in s.objects if o.type=='MESH' and o.visible_get() and not o.hide_render for m in o.modifiers if m.type=='SUBSURF']
r['native_sha256_after']=sha(N);assert before==r['native_sha256_after'];(O/'render-geometry-equivalence-audit.json').write_text(json.dumps(r,indent=2)+'\n');print('RENDER_GEOMETRY_AUDIT',json.dumps(r))
