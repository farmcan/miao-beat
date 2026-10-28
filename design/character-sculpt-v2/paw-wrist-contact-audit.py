"""Read-only C13 grip diagnostic: actual six Bezier strings + evaluated skin/board.
No nearest fallback. A miss or front-face first-hit is not a valid back-surface gap.
"""
import bpy,sys,json,hashlib,argparse,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier
p=argparse.ArgumentParser();p.add_argument('--dir',default='artifacts/character-paw-c13/r2');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.dir;src=out/'miao-c13-paw-wrist.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();input_sha=sha(src)
origin=Vector((-.1950536246756659,-.85,1.5567366254980208));gu=Vector((1.0169595357706245,0,.40048756408789304));gv=Vector((-.40048756408789304,0,1.0169595357706245))
V=gv.normalized()
def logical_v(p):return (p-origin).dot(gv)/gv.length_squared
def g(u,v,y):return origin+gu*u+gv*v+Vector((0,y-origin.y,0))
SOURCE_IDS={0:'source body',1:'authored palm',2:'authored toes',3:'authored basal wrist',4:'retained C8 near-wrist ROI, includes torso; not a semantic arm segmentation'}
def skin_source(body,face):
 idx=body.data.polygons[face].material_index
 return {'provenance_material_id':idx,'surface_source':SOURCE_IDS.get(idx,'unknown')}
def logical_u(p):return (p-origin).dot(gu)/gu.length_squared

def sample_string(obj,n):
 assert obj.type=='CURVE';spl=obj.data.splines[0];assert spl.type=='BEZIER';points=[];bp=spl.bezier_points
 for i in range(len(bp)-1):
  segment=interpolate_bezier(bp[i].co,bp[i].handle_right,bp[i+1].handle_left,bp[i+1].co,n)
  points.extend([obj.matrix_world@q for q in (segment[:-1] if i<len(bp)-2 else segment)])
 us=np.array([logical_u(q) for q in points]);assert np.all(np.diff(us)>-1e-6),'String U must be monotonic'
 return us,points

def at_u(data,u):
 us,pts=data;k=int(np.searchsorted(us,u));assert 0<k<len(us);f=(u-us[k-1])/(us[k]-us[k-1]);return pts[k-1].lerp(pts[k],float(f))

def main():
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Miao / continuous pear and rounded-square face'];board=bpy.data.objects['Guitar / ebony fretboard'];skin_bvh=BVHTree.FromObject(body,dg);skin_iv=body.matrix_world.inverted();skin_dir=(skin_iv.to_3x3()@Vector((0,-1,0))).normalized();board_bvh=BVHTree.FromObject(board,dg);board_iv=board.matrix_world.inverted();board_dir=(board_iv.to_3x3()@Vector((0,1,0))).normalized();table=[]
 for k in range(6):
  ob=bpy.data.objects['Guitar / string '+str(k+1)];d256=sample_string(ob,256);d512=sample_string(ob,512)
  for u in [1.22,1.25,1.33,1.36,1.44,1.47]:
   point=at_u(d512,u);approx=at_u(d256,u);radius=float(ob.data.bevel_depth);start=Vector((point.x,-.88,point.z));hit,n,face,distance=skin_bvh.ray_cast(skin_iv@start,skin_dir,1.5)
   entry={'string':k+1,'actual_object':ob.name,'u':u,'actual_bezier_centerline_world':list(point),'bevel_radius_scene_units':radius,'centerline_sampling_256_vs_512_error':(point-approx).length,'ray_origin_world':list(start),'ray_world_direction':[0,-1,0],'ray_maximum_distance':1.5,'skin_hit':hit is not None,'fallback_used':False}
   if hit is not None:
    entry.update(skin_source(body,face));hw=body.matrix_world@hit;nw=(body.matrix_world.to_3x3()@n).normalized();entry.update({'actual_skin_world':list(hw),'actual_skin_normal_world':list(nw),'surface_back_facing':nw.y>0,'centerline_minus_skin_y':point.y-hw.y,'valid_back_surface_gap':nw.y>0})
    if nw.y>0:entry['string_near_surface_clearance_y']=point.y-radius-hw.y
    else:entry['invalid_reason']='First hit front-facing; origin may be inside skin. No back-surface clearance claimed.'
   bh,bn,bface,bd=board_bvh.ray_cast(board_iv@Vector((point.x,-2,point.z)),board_dir,5)
   entry['board_hit']=bh is not None
   if bh is not None:
    bw=board.matrix_world@bh;entry['actual_board_front_world']=list(bw)
    if hit is not None and nw.y>0:entry['board_front_minus_skin_back_y']=bw.y-hw.y
   table.append(entry)
 # Designated intent declared by the authored C11 toe-root map, not chosen
 # from whichever of 36 samples happens to have the smallest absolute gap.
 targets=[]
 for digit,u in enumerate([1.2456666666666667,1.355,1.4643333333333335]):
  ob=bpy.data.objects['Guitar / string 3'];point=at_u(sample_string(ob,512),u);start=Vector((point.x,-.88,point.z));hit,n,face,d=skin_bvh.ray_cast(skin_iv@start,skin_dir,1.5)
  row={'intent':'relaxed short toe pad near string 3; not all-string fingering','digit':digit+1,'u':u,'expected_source':'authored toes','expected_source_id':2,'target_string':3,'target_world':list(point),'hit':hit is not None,'fallback_used':False}
  if hit is not None:
   hw=body.matrix_world@hit;nw=(body.matrix_world.to_3x3()@n).normalized();row.update(skin_source(body,face));row.update({'hit_world':list(hw),'normal_world':list(nw),'valid_back_surface':nw.y>0,'source_matches_declared_intent':body.data.polygons[face].material_index==2})
   if nw.y>0:row['signed_near_string_y_gap']=point.y-float(ob.data.bevel_depth)-hw.y
  targets.append(row)
 # Candidate hold support sites on the real lower edge of the fingerboard.
 # Negative gap means overlap; source identity and both ray misses remain explicit.
 supports=[]
 for u in [1.28,1.40]:
  # Establish a real board interior depth from explicit front AND back rays.
  front_origin=g(u,0,-2);back_origin=g(u,0,-.20);fh,fn,ff,fd=board_bvh.ray_cast(board_iv@front_origin,board_dir,5);back_dir=(board_iv.to_3x3()@Vector((0,-1,0))).normalized();rh,rn,rf,rd=board_bvh.ray_cast(board_iv@back_origin,back_dir,5)
  if fh is None or rh is None:
   supports.append({'u':u,'intent':'declared lower fingerboard support site','depth_calibration_failed':True,'front_hit':fh is not None,'back_hit':rh is not None,'fallback_used':False});continue
  front_world=board.matrix_world@fh;back_world=board.matrix_world@rh;y=(front_world.y+back_world.y)/2;start=g(u,-.30,y);bdirection=(board_iv.to_3x3()@V).normalized();bh,bn,bf,dist=board_bvh.ray_cast(board_iv@start,bdirection,.5)
  row={'intent':'palm interior under lower fingerboard edge supports relaxed hold','u':u,'calibrated_world_y':y,'board_depth_front_world':list(front_world),'board_depth_back_world':list(back_world),'depth_rule':'midpoint of explicit front/back board ray hits at logical V=0; no nearest fallback','expected_skin_source':'authored palm','expected_source_id':1,'board_ray_origin_world':list(start),'board_ray_direction_world':list(V),'board_hit':bh is not None,'fallback_used':False}
  skin_start=g(u,-.110,y);skin_direction=(skin_iv.to_3x3()@(-V)).normalized();h,n,face,d=skin_bvh.ray_cast(skin_iv@skin_start,skin_direction,.7);row['skin_ray_origin_world']=list(skin_start);row['skin_ray_direction_world']=list(-V);row['skin_hit']=h is not None
  if bh is not None:row['board_lower_edge_world']=list(board.matrix_world@bh)
  if h is not None:
   hw=body.matrix_world@h;nw=(body.matrix_world.to_3x3()@n).normalized();row.update(skin_source(body,face));row.update({'skin_world':list(hw),'skin_normal_world':list(nw),'valid_upward_facing_support_surface':nw.dot(V)>0,'source_matches_declared_intent':body.data.polygons[face].material_index==1})
   if bh is not None and nw.dot(V)>0:row['signed_lower_edge_gap_along_v']=(board.matrix_world@bh-hw).dot(V)
  supports.append(row)
 valid=[r for r in table if r.get('valid_back_surface_gap')];values=[r['string_near_surface_clearance_y'] for r in valid]
 result={'stage':'read-only-static-grip-diagnostic-not-contact-pass','native_scene_sha256':input_sha,'source_scene_unchanged':sha(src)==input_sha,'script_sha256':sha(__file__),'method':'Actual saved six string Bezier controls/handles and matrices, 512 samples/segment; compare256. Skin rays startY=-.88 in front of torso and target toward viewer, explicithit/miss only. Only +Y backface normals permit a gap. Evaluated fingerboard separately raycast.','legacy_receipt_contacts_status':'C10 old extrapolated table remains INVALID. This C13 audit uses saved actual Bezier controls and explicit BVH rays only.','sampling':{'total':len(table),'valid_backface_samples':len(valid),'misses':sum(not r['skin_hit'] for r in table),'invalid_frontface_hits':sum(r['skin_hit'] and not r.get('valid_back_surface_gap',False) for r in table),'minimum_valid_near_surface_clearance_y':min(values) if values else None,'maximum_valid_near_surface_clearance_y':max(values) if values else None,'strictly_negative_gap_count':sum(q<0 for q in values),'negative_below_minus_005_count':sum(q<-.005 for q in values),'positive_gap_count':sum(q>0 for q in values)},'records':table,'declared_toe_pad_targets':targets,'declared_hold_support_targets':supports,'hold_intent':'relaxed static support; all-six-string pressing is not required; declared source IDs must match actual hits; no animation/contact pass inferred','limits':['Finite samples, not full collision or dynamics proof.','Provenance materials identify authored palm/toes/wrist versus source forearm; digit number is assigned by intended U strip, not a dynamic skin-weight or full collision certification.','Positive clearance indicates a gap; it must not be called pressing a string. Negative means potential plush/string overlap at that sample.','No actual playing or per-note fingering has been built or passed.']}
 (out/'contact-audit.json').write_text(json.dumps(result,indent=2)+'\n');receipt=out/'receipt.json';d=json.loads(receipt.read_text());d['contact_status']='Read-only actual Bezier/backface audit complete, not a contact pass';d['replacement_contact_audit']='contact-audit.json';receipt.write_text(json.dumps(d,indent=2)+'\n');print('RESULT '+json.dumps(result['sampling']))
main()
