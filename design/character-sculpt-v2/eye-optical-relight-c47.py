"""C47 physical mirror-direction relight. Only existing optical area transforms change."""
import bpy, numpy as np, math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/character-eye-optical-c47';OLD=ROOT/'artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend';SRC=ROOT/'artifacts/character-eye-cap-c45/r2-layer-clearance/miao-c45-cap-curvature.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unit(v):return v/np.linalg.norm(v,axis=-1,keepdims=True)
def angle(a,b):return np.degrees(np.arccos(np.clip(np.sum(a*b,axis=-1),-1,1)))
def eye(ob):
 p=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',p);p=p.reshape(-1,3);m=np.asarray(ob.matrix_world);P=p@m[:3,:3].T+m[:3,3];normal=np.array([list(v.normal) for v in ob.data.vertices]);normal=unit(normal@np.linalg.inv(m[:3,:3]));return P,normal

def geometry():
 result={}
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH':
   p=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',p);ix=np.empty(len(ob.data.loops),np.int32);ob.data.loops.foreach_get('vertex_index',ix);result[ob.name]=hashlib.sha256(p.tobytes()+ix.tobytes()+np.asarray(ob.matrix_world,np.float32).tobytes()).hexdigest()
  elif ob.type=='CURVE':result[ob.name]=hashlib.sha256(repr([(list(p.co),list(p.handle_left),list(p.handle_right)) for s in ob.data.splines for p in s.bezier_points]+[list(p.co) for s in ob.data.splines for p in s.points]).encode()+np.asarray(ob.matrix_world,np.float32).tobytes()).hexdigest()
 return result

def lightdata(o):
 return {'energy':o.data.energy,'shape':o.data.shape,'size':o.data.size,'diffuse':o.data.diffuse_factor,'specular':o.data.specular_factor,'receiver':o.light_linking.receiver_collection.name if o.light_linking.receiver_collection else None,'receiver_objects':sorted(x.name for x in o.light_linking.receiver_collection.all_objects) if o.light_linking.receiver_collection else None}

def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'optical-diagnosis.json').exists(),'Preserve frozen result'
 diagnosis={};index=1+8*96+32 # j=9, k=32 -> (-.1875,+.32476) of actual source cap radii.
 for tag,path in [('C20',OLD),('C45r2',SRC)]:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.context.view_layer.update();view=np.asarray(s.camera.matrix_world.to_3x3()@Vector((0,0,1)));assert s.camera.data.type=='ORTHO';records=[]
  for side in ['L','R']:
   cap=bpy.data.objects['C7 / clear cornea '+side];P,N=eye(cap);light=bpy.data.objects['C7 / optical area '+side];n=(len(P)//2);indices=np.arange(1,1+21*96);L=unit(np.asarray(light.matrix_world.translation)[None,:]-P);V=np.tile(view,(len(P),1));H=unit(L+V);reflected=2*np.sum(N*V,axis=1)[:,None]*N-V;normal_error=angle(N,H);light_error=angle(unit(reflected),L);best=indices[np.argmin(light_error[indices])];distance=np.linalg.norm(np.asarray(light.matrix_world.translation)-P[index]);disk_radius=math.degrees(math.atan((light.data.size*.5)/distance));row={'side':side,'light':lightdata(light),'camera_type':'ORTHO','constant_to_camera_direction':view.tolist(),'target_front_vertex':index,'target_point_world':P[index].tolist(),'target_actual_smooth_normal':N[index].tolist(),'target_light_direction':L[index].tolist(),'target_half_vector':H[index].tolist(),'target_normal_vs_half_degrees':float(normal_error[index]),'target_specular_direction_vs_light_center_degrees':float(light_error[index]),'light_disk_angular_radius_degrees_at_target':disk_radius,'best_front_vertex':int(best),'best_front_normal_vs_half_degrees':float(normal_error[best]),'best_specular_direction_vs_light_center_degrees':float(light_error[best]),'interior_front_samples':len(indices),'interior_normal_vs_half_quantiles_degrees':np.quantile(normal_error[indices],[0,.1,.5,.9,1]).tolist(),'target_specular_mirror_direction':unit(reflected[index]).tolist()};records.append(row)
  diagnosis[tag]={'source_sha256':sha(path),'camera_matrix':list(map(list,s.camera.matrix_world)),'eyes':records}
 # A numerical diagnostic, not a claimed exhaustive visibility solver.
 diagnosis['limits']=['Uses actual smooth vertex normals and orthographic camera rays; full path-traced images remain the appearance evidence.','Finite area disk occlusion and full BRDF are not reduced to an angular threshold.','Both prior studies and their failures are retained.']
 (OUT/'optical-diagnosis.json').write_text(json.dumps(diagnosis,indent=2)+'\n')
 before=geometry();materials={o.name:[m.name for m in o.data.materials] for o in s.objects if hasattr(o.data,'materials')};alllights={o.name:{'data':lightdata(o),'matrix':list(map(list,o.matrix_world))} for o in s.objects if o.type=='LIGHT'};placements=[]
 for rec in diagnosis['C45r2']['eyes']:
  side=rec['side'];light=bpy.data.objects['C7 / optical area '+side];point=Vector(rec['target_point_world']);direction=Vector(rec['target_specular_mirror_direction']);distance=(light.matrix_world.translation-point).length;oldmatrix=list(map(list,light.matrix_world));light.location=point+direction*distance;light.rotation_euler=(point-light.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();assert lightdata(light)==alllights[light.name]['data'];placements.append({'light':light.name,'target_actual_vertex':index,'point':list(point),'actual_smooth_normal':rec['target_actual_smooth_normal'],'mirror_direction':list(direction),'preserved_source_to_target_distance':distance,'old_matrix':oldmatrix,'new_matrix':list(map(list,light.matrix_world))})
 bpy.context.view_layer.update();assert before==geometry();assert materials=={o.name:[m.name for m in o.data.materials] for o in s.objects if hasattr(o.data,'materials')}
 for o in s.objects:
  if o.type=='LIGHT' and not o.name.startswith('C7 / optical area '):assert alllights[o.name]=={'data':lightdata(o),'matrix':list(map(list,o.matrix_world))}
 s.cycles.samples=128;s.cycles.seed=17;s.cycles.use_animated_seed=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False;bpy.context.preferences.filepaths.save_version=0
 native=OUT/'miao-c47-physical-optical-relight.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);report={'scope':'C47 physical specular re-aim of existing two optical areas only; art review pending','source':str(SRC.relative_to(ROOT)),'source_sha256':sha(SRC),'native_sha256':sha(native),'script_sha256':sha(__file__),'all_mesh_curve_geometry_exact':True,'all_material_slots_exact':True,'all_light_nontransform_parameters_exact':True,'studio_receivers_unchanged_no_caps_added':True,'placements':placements,'renders':[],'art_gate_passed':False,'production_changed':False,'limits':diagnosis['limits']};(OUT/'receipt.partial.json').write_text(json.dumps(report,indent=2)+'\n')
 cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();scale=cam.data.ortho_scale
 for view in ['full','face']:
  if view=='face':cam.location=Vector((0,-6,3.05));cam.rotation_euler=(Vector((0,0,3.03))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.7
  else:cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=scale
  bpy.context.view_layer.update();file=OUT/('c47-'+view+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);report['renders'].append({'file':file.name,'sha256':sha(file),'camera_matrix':list(map(list,cam.matrix_world)),'ortho_scale':cam.data.ortho_scale})
 (OUT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps({'out':str(OUT),'renders':2,'only_existing_two_light_transforms_changed':True,'art_passed':False}),flush=True)
main()
