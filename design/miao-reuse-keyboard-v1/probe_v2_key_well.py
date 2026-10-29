"""One fixed v1 hinge, 1.5mm front stroke mechanical sweep. No Boolean/save/render/action."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent));from single_key_geometry import record,overlaps,bounds,RenderMatchedProxy,geometry
O=R/'artifacts/miao-reuse-keyboard-v1/v2-static-probe';S=R/'artifacts/miao-reuse-keyboard-v1/default-color/keyboard-default-color-native36.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(S);bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);key=bpy.data.objects['Ivory piano key.014'];source=record(key);case=record(bpy.data.objects['Controller chassis']);bb=source['bbox'];pivot=Vector(((bb[0][0]+bb[1][0])/2,bb[0][1],(bb[0][2]+bb[1][2])/2));lever=bb[1][1]-pivot.y;stroke=.0015;alpha=math.asin(stroke/lever);objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!=key.name and o.name.startswith(('Ivory piano key','Raised black piano key','Controller chassis','SUPPORT-','Top rotary control','Top control index'))];fixed=[record(o) for o in objects];black=next(r for r in fixed if r['name']=='Raised black piano key.010')
def segtri(p0,p1,a,b,c):
 d=p1-p0;e1=b-a;e2=c-a;h=d.cross(e2);det=e1.dot(h)
 if abs(det)<1e-15:return None
 inv=1/det;s=p0-a;u=s.dot(h)*inv
 if u< -1e-7 or u>1+1e-7:return None
 q=s.cross(e1);v=d.dot(q)*inv
 if v< -1e-7 or u+v>1+1e-7:return None
 t=e2.dot(q)*inv
 return p0+d*t if -1e-7<=t<=1+1e-7 else None
def crosspoints(a,b,pairs):
 pts=[]
 for ia,ib in pairs:
  va=[a['p'][i] for i in a['t'][ia]];vb=[b['p'][i] for i in b['t'][ib]]
  for tri,other in [(va,vb),(vb,va)]:
   for i in range(3):
    p=segtri(tri[i],tri[(i+1)%3],*other)
    if p is not None:pts.append(p)
 return pts
# Convex halfspace checks classify inherited allowed volume, never exempt entire black component.
import numpy as np
def planes(r):
 center=sum(r['p'],Vector())/len(r['p']);pp=[]
 for tri in r['t']:
  a,b,c=[r['p'][i] for i in tri];n=(b-a).cross(c-a)
  if n.length<1e-12:continue
  n.normalize()
  if n.dot((a+b+c)/3-center)<0:n=-n
  pp.append([n.x,n.y,n.z,-n.dot(a)])
 arr=np.array(pp);pts=np.array([list(p)+[1] for p in r['p']]);error=float((arr@pts.T).max());return arr,error
def violations(points,pl):
 if not points:return []
 return (pl@np.array([list(p)+[1] for p in points]).T).max(axis=0).tolist()
sourceplanes,source_convex=planes(source);blackplanes,black_convex=planes(black);basepairs=set(source['tree'].overlap(black['tree']));rows=[];sweeppts=[]
for f in [0,.25,.5,.75,1]:
 theta=-alpha*f;M=Matrix.Translation(pivot)@Matrix.Rotation(theta,4,'X')@Matrix.Translation(-pivot);p=[M@v for v in source['p']];t=source['t'];m={'name':key.name,'p':p,'t':t,'bbox':bounds(p),'tree':BVHTree.FromPolygons(p,t,all_triangles=True)};hits=overlaps(p,t,fixed);pairs=set(m['tree'].overlap(black['tree']));points=crosspoints(m,black,pairs);currplanes,currconvex=planes(m)
 for v in p:
  if max(violations([v],blackplanes))<=5e-7:points.append(v)
 for v in black['p']:
  if max(violations([v],currplanes))<=5e-7:points.append(v)
 outside=violations(points,sourceplanes);newoutside=[{'point':list(v),'outside_source_white_m':d} for v,d in zip(points,outside) if d>5e-7];cpairs=m['tree'].overlap(case['tree']);cpoints=crosspoints(m,case,cpairs)
 rows.append({'fraction':f,'hinge_angle_degrees':math.degrees(theta),'front_stroke_m':lever*math.sin(-theta),'component_triangle_pairs':hits,'black010_exact_pairs':[list(v) for v in sorted(pairs)],'black010_added_pair_ids':[list(v) for v in sorted(pairs-basepairs)],'black010_retired_pair_ids':[list(v) for v in sorted(basepairs-pairs)],'black010_overlap_vertex_samples':len(points),'black010_max_outside_original_white_m':max(outside,default=0),'unreliable_halfspace_outside_samples':newoutside,'black010_confirmed_new_overlap':None,'halfspace_region_check_status':'INVALID as proof if source convexity defect exceeds0.5um; follow finite membership supplement','black010_region_check':'current intersection vertices inside original white halfspaces within0.5um; original and moving white plus black convex checks recorded; not whole-object whitelist','new_noncase_components':[n for n in hits if n not in ['Controller chassis','Raised black piano key.010']],'case_exact_intersection_points':[list(v) for v in cpoints],'case_intersection_bbox':None if not cpoints else bounds(cpoints)})
 sweeppts+=p
# Exact coordinate extrema over continuous angular interval for each original vertex.
continuous=[]
for v in source['p']:
 yp=v.y-pivot.y;zp=v.z-pivot.z;angles=[0,alpha]
 for root in [math.atan2(zp,yp),math.atan2(-yp,zp)]:
  for k in [-1,0,1]:
   a=root+k*math.pi
   if 0<a<alpha:angles.append(a)
 for a in angles:continuous.append(Vector((v.x,pivot.y+yp*math.cos(a)+zp*math.sin(a),pivot.z-yp*math.sin(a)+zp*math.cos(a))))
sweep=bounds(continuous);clearance=.0001;well={'min':[sweep[0][0]-clearance,sweep[0][1]-clearance,sweep[0][2]-clearance],'max':[sweep[1][0]+clearance,sweep[1][1]+clearance,.3120000064+clearance],'clearance_m':clearance,'definition':'one conservative rectangular hidden well for white014 only; intersect cutter with original case; no Boolean performed'};cross=[]
for x in [(well['min'][0]+well['max'][0])/2,well['min'][0]+.0002,well['max'][0]-.0002]:
 for y in [well['min'][1]+.002,(well['min'][1]+well['max'][1])/2,well['max'][1]-.002]:
  top,_,_,_=case['tree'].ray_cast(Vector((x,y,2)),Vector((0,0,-1)),3);bottom,_,_,_=case['tree'].ray_cast(Vector((x,y,-1)),Vector((0,0,1)),3);cross.append({'xy':[x,y],'roof_z':None if top is None else top.z,'bottom_z':None if bottom is None else bottom.z,'required_well_depth_m':None if top is None else max(0,top.z-well['min'][2]),'remaining_bottom_thickness_m':None if bottom is None else well['min'][2]-bottom.z})
front=[]
for z in [well['min'][2],(well['min'][2]+.312)/2,.312-.00001]:
 hit,_,_,_=case['tree'].ray_cast(Vector((pivot.x,1,z)),Vector((0,-1,0)),3);front.append({'z':z,'original_case_outer_front_y':None if hit is None else hit.y,'AABB_well_front_lip_m':None if hit is None else hit.y-well['max'][1]})
result={'status':'B_FIXED_SWEEP_NUMERIC_ONLY_NO_BOOLEAN','source':str(S),'source_sha_before':before,'source_sha_after':sha(S),'fixed_hinge_world':list(pivot),'maximum_front_stroke_m':stroke,'maximum_hinge_degrees':math.degrees(-alpha),'sweep_samples':rows,'continuous_swept_bbox':sweep,'aabb_bound_not_approved_as_cut':well,'proposed_single_well':{'definition':'actual fixed key sweep offset0.1mm INTERSECT original case; not whole AABB subtraction','bounds':well,'front_bevel_preservation':'requires concrete derivative/approval, not verified'},'case_sections':cross,'minimum_remaining_bottom_m':min(v['remaining_bottom_thickness_m'] for v in cross if v['remaining_bottom_thickness_m'] is not None),'front_profile_sections':front,'source_white_convex_max_error_m':source_convex,'source_black_convex_max_error_m':black_convex,'source_white_black_baseline_pair_ids':[list(v) for v in sorted(basepairs)],'unknown':['no actual Boolean topology/normals/material/wall verification','well AABB may intersect original front top bevel; must disclose sections before approval','continuous angular bbox exact, collision pair snapshots only5 angles; no hand animation driven'],'new_actions':0,'native_saved':False,'geometry_modified':False};assert before==sha(S);(O/'B-fixed-sweep-and-well.json').write_text(json.dumps(result,indent=2)+'\n');print('B_SWEEP',json.dumps({k:result[k] for k in ['fixed_hinge_world','maximum_hinge_degrees','continuous_swept_bbox','aabb_bound_not_approved_as_cut','minimum_remaining_bottom_m','front_profile_sections']}))
