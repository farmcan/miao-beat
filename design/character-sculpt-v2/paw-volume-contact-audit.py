"""Read-only C11 grip diagnostic: actual six Bezier strings + evaluated skin/board.
No nearest fallback. A miss or front-face first-hit is not a valid back-surface gap.
"""
import bpy,sys,json,hashlib,argparse,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier
p=argparse.ArgumentParser();p.add_argument('--dir',default='artifacts/character-paw-c11');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[2];out=root/a.dir;src=out/'miao-c11-paw-volume.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();input_sha=sha(src)
origin=Vector((-.1950536246756659,-.85,1.5567366254980208));gu=Vector((1.0169595357706245,0,.40048756408789304));gv=Vector((-.40048756408789304,0,1.0169595357706245))
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
    hw=body.matrix_world@hit;nw=(body.matrix_world.to_3x3()@n).normalized();entry.update({'actual_skin_world':list(hw),'actual_skin_normal_world':list(nw),'surface_back_facing':nw.y>0,'centerline_minus_skin_y':point.y-hw.y,'valid_back_surface_gap':nw.y>0})
    if nw.y>0:entry['string_near_surface_clearance_y']=point.y-radius-hw.y
    else:entry['invalid_reason']='First hit front-facing; origin may be inside skin. No back-surface clearance claimed.'
   bh,bn,bface,bd=board_bvh.ray_cast(board_iv@Vector((point.x,-2,point.z)),board_dir,5)
   entry['board_hit']=bh is not None
   if bh is not None:
    bw=board.matrix_world@bh;entry['actual_board_front_world']=list(bw)
    if hit is not None and nw.y>0:entry['board_front_minus_skin_back_y']=bw.y-hw.y
   table.append(entry)
 valid=[r for r in table if r.get('valid_back_surface_gap')];values=[r['string_near_surface_clearance_y'] for r in valid]
 result={'stage':'read-only-static-grip-diagnostic-not-contact-pass','native_scene_sha256':input_sha,'source_scene_unchanged':sha(src)==input_sha,'script_sha256':sha(__file__),'method':'Actual saved six string Bezier controls/handles and matrices, 512 samples/segment; compare256. Skin rays startY=-.88 in front of torso and target toward viewer, explicithit/miss only. Only +Y backface normals permit a gap. Evaluated fingerboard separately raycast.','legacy_receipt_contacts_status':'Do not use earlier receipt.contacts for grip: old calculation extrapolated bridge segment slope to neck and rays began behind torso. Historical raw table retained, superseded by this explicit audit.','sampling':{'total':len(table),'valid_backface_samples':len(valid),'misses':sum(not r['skin_hit'] for r in table),'invalid_frontface_hits':sum(r['skin_hit'] and not r.get('valid_back_surface_gap',False) for r in table),'minimum_valid_near_surface_clearance_y':min(values) if values else None,'maximum_valid_near_surface_clearance_y':max(values) if values else None},'records':table,'limits':['Finite samples, not full collision or dynamics proof.','Some rays may hit palm/forearm skin within the restricted paw region; individual toe identity is not certified.','Positive clearance indicates a gap; it must not be called pressing a string. Negative means potential plush/string overlap at that sample.','No actual playing or per-note fingering has been built or passed.']}
 (out/'contact-audit.json').write_text(json.dumps(result,indent=2)+'\n');receipt=out/'receipt.json';d=json.loads(receipt.read_text());d['contact_status']='Read-only actual Bezier/backface audit complete, not a contact pass';d['replacement_contact_audit']='contact-audit.json';receipt.write_text(json.dumps(d,indent=2)+'\n');print('RESULT '+json.dumps(result['sampling']))
main()
