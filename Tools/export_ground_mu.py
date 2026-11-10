"""Read-only Blender-to-native export into a separate additive ground kit.

Visual vertices/UVs are preserved; handedness/winding, materials and runtime
colliders are adapted on exported copies. Original .blend files are never saved.
"""
import bpy,sys,math,json,copy,hashlib,re
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5'
sys.path[:0]=[str(R/'Tools'),str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import parse
from ground_layout import windows,plaque,key as geometry_key,label_removals,image_key
from ground_rig import build as build_rig,remove_middle_legs,widen_stairs
from ground_refinements import refine_hardware,greenhouse_shelves,service_network,elbow_handrails
GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models';OUT.mkdir(parents=True,exist_ok=True)
SHIFT=2.3;C=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
ROLES=('HAB','LAB','CMD','LOG','GRN','AIR','PWR','HUB','TUB','ELB')
def source_id(role):return 'RW_ADP_250_375' if role=='ADP' else f'RW_{role}_250'
def matrix(role):
 if role=='ELB':return Matrix.Identity(3),Vector((0,0,SHIFT))
 if role=='CUP':return Matrix(((1,0,0),(0,0,-1),(0,1,0))),Vector((0,0,1.52))
 a=math.pi/3 if role in ('HAB','LAB','LOG','GRN') else 0
 return Matrix(((0,1,0),(-math.sin(a),0,-math.cos(a)),(math.cos(a),0,-math.sin(a)))),Vector((0,0,SHIFT))
def convert(p):return tuple(C@Vector(p)-Vector((0,SHIFT,0)))
def normal(n):return tuple((C@Vector(n)).normalized())
def node(name):return dict(name=name,position=(0,0,0),rotation=(0,0,0,1),scale=(1,1,1),children=[],tag='Untagged',layer=0)
def srgb(v):return 12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
def source_world(n,parent):
 q=n['rotation'];m=parent@Matrix.LocRotScale(Vector(n['position']),Quaternion((q[3],q[0],q[1],q[2])),Vector(n['scale']))
 yield n,m
 for child in n['children']:yield from source_world(child,m)
def mesh_points(points,tris,normals=None):
 return dict(vertices=points,normals=normals or [(0,1,0)]*len(points),uvs=[(0,0)]*len(points),submeshes=[tris])
def box_collision(name,lo,hi,tag='Untagged',trigger=False):
 n=node(name);n['position']=tuple((a+b)/2 for a,b in zip(lo,hi));n['tag']=tag;n['layer']=21 if trigger else 0
 n['collider']=dict(type='box',trigger=int(trigger),size=tuple(b-a for a,b in zip(lo,hi)),center=(0,0,0));return n
def round_collision(name,rings,axis=1):
 # Closed convex profiles, 16 sides, below PhysX's 255-triangle limit.
 points=[];tris=[];sides=16
 for height,radius in rings:
  for j in range(sides):
   p=[radius*math.cos(j*2*math.pi/sides),height,radius*math.sin(j*2*math.pi/sides)]
   if axis!=1:p[axis],p[1]=p[1],p[axis]
   points.append(tuple(p))
 for k in range(len(rings)-1):
  for j in range(sides):
   a=k*sides+j;b=k*sides+(j+1)%sides;c=b+sides;d=a+sides;tris.extend(((a,b,c),(a,c,d)))
 for k,reverse in ((0,False),(len(rings)-1,True)):
  for j in range(1,sides-1):
   t=(k*sides,k*sides+j,k*sides+j+1);tris.append(tuple(reversed(t)) if reverse else t)
 # Normalize all face winding from a point inside the convex body.
 center=sum((Vector(v) for v in points),Vector())/len(points);normals=[Vector() for _ in points]
 for i,t in enumerate(tris):
  a,b,c=(Vector(points[x]) for x in t);n=(b-a).cross(c-a)
  if n.dot((a+b+c)/3-center)<0:t=tuple(reversed(t));tris[i]=t;n=-n
  for x in t:normals[x]+=n
 n=node(name);n['collider']=dict(type='mesh',trigger=0,convex=1,mesh=mesh_points(points,tris,[tuple(v.normalized()) for v in normals]));return n
def export(role):
 path=W/f'ground-modules-art-v4/Models/RW_GND_{role}.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
 asset=next(c for c in bpy.data.collections if c.name.startswith('RW GROUND'))
 removed_legs=remove_middle_legs(asset,convert) if role in ('HAB','LAB','LOG','GRN') else []
 stair_clearance=widen_stairs(asset)
 refinements=refine_hardware(asset,role,convert)
 part=f'RW_GND_{role}';model=load(CORE/f'GameData/RoosterWorksStationModules/Models/{source_id(role)}.mu')
 oldmodel=copy.deepcopy(model);model.name=part;model.root=node(part);model.materials=[];model.textures=[]
 texmap={};groups={};matmeta={};report=dict(role=role,source_blend_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),objects=0,triangles=0,inheritance_winding_corrected=role not in ('ELB','CUP'),emissive_renderers=[],mechanical_colliders=0,legs=0,stairs=0)
 A,translation=matrix(role)
 report['removed_middle_leg_objects']=removed_legs
 report['stair_clearance']=stair_clearance
 report['refinements']=refinements
 assignments,bindings=build_rig(asset,convert);roots={'':model.root}
 for b in bindings:
  n=node(b['name']);n['position']=b['position'];roots[b['name']]=n;model.root['children'].append(n)
 report['motion']=bindings
 report['rig_members']=assignments;report['hose_bounds']={};report['foot_bounds']={}
 for obj in asset.objects:
  if obj.name.startswith('Hydraulic hose') or obj.name.startswith('Replaceable pad plate'):
   points=[convert(obj.matrix_world@Vector(v)) for v in obj.bound_box];bounds=([min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)])
   if obj.name.startswith('Hydraulic hose'):report['hose_bounds'][obj.name]=bounds
   else:report['foot_bounds'][assignments[obj.name]]=bounds
 if stair_clearance:
  def bounds(obj):
   points=[convert(obj.matrix_world@Vector(v)) for v in obj.bound_box];return ([min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)])
  landing=bounds(asset.objects['Access landing']);cx=(landing[0][0]+landing[1][0])/2
  door=bounds(asset.objects['Ground access door | hull-integrated mounting block']);stair_clearance['door_mount_half_width']=max(abs(door[0][0]-cx),abs(door[1][0]-cx))
  stair_clearance['rail_inner_half_width']=min(abs(p[0]-cx) for obj in asset.objects if obj.name.startswith(('Handrail stanchion','Continuous copper handrail')) for p in [convert(obj.matrix_world@Vector(v)) for v in obj.bound_box])
  stair_clearance['landing_top']=landing[1][1]
 original={}
 for mat in oldmodel.materials:
  t=oldmodel.textures[mat['properties']['_MainTex']['index']]['name'].rsplit('/',1)[-1];original[t]=mat
 if role=='HUB':
  cup=load(CORE/'GameData/RoosterWorksStationModules/Models/RW_CUP_250.mu')
  for mat in cup.materials:
   m=copy.deepcopy(mat)
   for v in m['properties'].values():
    if isinstance(v,dict):
     oldmodel.textures.append(copy.deepcopy(cup.textures[v['index']]));v['index']=len(oldmodel.textures)-1
   t=oldmodel.textures[m['properties']['_MainTex']['index']]['name'].rsplit('/',1)[-1];original[t]=m
 def texture(name,image=None,color=None):
  key=name
  if key not in texmap:
   target=OUT/(name+'.png')
   if image:
    if image.packed_file:target.write_bytes(bytes(image.packed_file.data))
    else:
     target.write_bytes(Path(bpy.path.abspath(image.filepath)).read_bytes())
   else:
    im=bpy.data.images.new('runtime color '+name,width=4,height=4);im.pixels=list(color)*16;im.filepath_raw=str(target);im.file_format='PNG';im.save();bpy.data.images.remove(im)
   texmap[key]=len(model.textures);model.textures.append(dict(name=key,type=0))
  return dict(index=texmap[key],scale=(1,1),offset=(0,0))
 def material(mat):
  if mat.name in matmeta:return matmeta[mat.name]
  images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if mat.use_nodes else []
  im=images[0] if images else None;t=Path(im.name).stem if im else None
  if t in original:
   result=copy.deepcopy(original[t]);result['name']='RW_Ground_'+t.removeprefix('rwm_')
   for k,v in result['properties'].items():
    if not isinstance(v,dict):continue
    oldtex=oldmodel.textures[v['index']]['name'].rsplit('/',1)[-1]
    teximage=next((x for x in bpy.data.images if Path(x.name).stem==oldtex),None)
    if teximage is not None:result['properties'][k]=texture(oldtex,teximage)
    else:
     target=OUT/(oldtex+'.png');target.write_bytes((CORE/f'GameData/RoosterWorksStationModules/Models/{oldtex}.png').read_bytes())
     key=oldtex
     if key not in texmap:texmap[key]=len(model.textures);model.textures.append(dict(name=key,type=0))
     v['index']=texmap[key]
  else:
   label=re.sub(r'[^a-z0-9]+','_',mat.name.lower()).strip('_');p=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
   color=list(p.inputs['Base Color'].default_value if p else mat.diffuse_color);color[:3]=[srgb(max(0,min(1,v))) for v in color[:3]]
   emission=float(p.inputs['Emission Strength'].default_value) if p else 0
   main=texture('gnd_'+label,color=color)
   shader='KSP/Emissive/Diffuse' if emission>0 else 'KSP/Specular'
   props={'_Color':(1,1,1,1),'_MainTex':main}
   if emission>0:props.update({'_Emissive':copy.deepcopy(main),'_EmissiveColor':(0,0,0,1)})
   else:props.update({'_SpecColor':(.35,.35,.35,1),'_Shininess':.3})
   result=dict(name='RW_GroundHardware_'+label,shader=shader,properties=props)
  index=len(model.materials);model.materials.append(result);matmeta[mat.name]=(index,t);return index,t
 def group(index,root='',batch=''):
  label=(index,root,batch)
  if label not in groups:groups[label]=[dict(vertices=[],normals=[],uvs=[],submeshes=[[]])]
  m=groups[label][-1]
  if len(m['vertices'])+3>65000:m=dict(vertices=[],normals=[],uvs=[],submeshes=[[]]);groups[label].append(m)
  return m
 def append_tri(index,root,pts,norms,uvs,batch=''):
  m=group(index,root,batch);offset=Vector(roots[root]['position']);p=[Vector(v)-offset for v in pts];n=[Vector(v).normalized() for v in norms]
  if (p[1]-p[0]).cross(p[2]-p[0]).dot(sum(n,Vector()))<0:p.reverse();n.reverse();uvs=list(reversed(uvs))
  start=len(m['vertices']);m['vertices']+=list(map(tuple,p));m['normals']+=list(map(tuple,n));m['uvs']+=list(uvs);m['submeshes'][0].append((start,start+1,start+2));report['triangles']+=1
 deps=bpy.context.evaluated_depsgraph_get()
 removed_windows,additions=windows(role,A,C,translation,SHIFT);removed_labels=label_removals(asset,deps,convert)
 report['window_triangles_expected']=len(removed_windows);report['window_triangles_removed']=0;report['label_triangles_removed']=0;report['dish_backfaces']=0
 label_texture={'HAB':'label','LAB':'lablabel','CMD':'cmdlabel','LOG':'loglabel','GRN':'grnlabel','AIR':'airlabel','PWR':'pwrlabel','HUB':'hublabel','TUB':'tublabel','ELB':'elblabel'}[role]
 additions+=plaque(role,label_texture)
 pipe_additions,paths=service_network(role);additions+=pipe_additions;report['service_paths']=paths
 if role=='GRN':additions+=greenhouse_shelves()
 if role=='ELB':
  rails,paths=elbow_handrails();additions+=rails;report['roof_handrail_paths']=paths
  yellow=bpy.data.materials.new('RW Safety Yellow');yellow.use_nodes=True
  yellow.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.85,.58,.015,1)
 report['replaced_greenhouse_interior_triangles']=0
 for obj in asset.objects:
  if obj.type!='MESH':continue
  report['objects']+=1;ev=obj.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles();world=obj.matrix_world;norm=world.to_3x3().inverted().transposed()
  heritage=obj.name.startswith('Station heritage');reverse=heritage and role not in ('ELB','CUP')
  for tri in mesh.loop_triangles:
   fingerprint=geometry_key([convert(world@mesh.vertices[i].co) for i in tri.vertices])
   if role=='GRN' and heritage:
    points=[convert(world@mesh.vertices[i].co) for i in tri.vertices]
    # The upright orbital crop tiers became vertical walls after the barrel
    # was laid on its side. Replace only their internal geometry, preserving
    # all glazing, pressure frames, inspection strips and exterior equipment.
    if image_key(mesh.materials[tri.material_index]) in ('rwm_grnleaf','rwm_grnleaflight','rwm_grnroot','rwm_grnlamp') or all(abs(p[0])<1.20 and math.hypot(p[1],p[2])<1.145 for p in points):
     report['replaced_greenhouse_interior_triangles']+=1;continue
   if fingerprint in removed_windows:report['window_triangles_removed']+=1;continue
   if fingerprint in removed_labels:report['label_triangles_removed']+=1;continue
   mat=mesh.materials[tri.material_index] if mesh.materials else None
   if mat is None:raise RuntimeError('Missing material '+obj.name)
   if heritage and role in ('HAB','LAB','CMD') and image_key(mat)=='rwm_glass':continue
   index,t=material(mat);root=assignments.get(obj.name,'');loops=list(tri.loops)
   if reverse:loops.reverse()
   pts=[];norms=[];uvs=[]
   for l in loops:
    p=world@mesh.vertices[mesh.loops[l].vertex_index].co;n=norm@mesh.corner_normals[l].vector
    if reverse:n=-n
    pts.append(convert(p));norms.append(normal(n));uvs.append(tuple(mesh.uv_layers.active.data[l].uv) if mesh.uv_layers.active else (0,0))
   append_tri(index,root,pts,norms,uvs)
   if obj.name.startswith('High gain parabolic reflector'):
    append_tri(index,root,list(reversed(pts)),[tuple(-Vector(n)) for n in reversed(norms)],list(reversed(uvs)));report['dish_backfaces']+=1
  # Compact, conservative collision on the feet/support sleeves and stair treads.
  if any(k in obj.name for k in ('Replaceable pad plate','upper pressure sleeve','polished ram','Stair tread','Access landing','Stair ground shoe','hull saddle','mounting block','reinforcing cheek','solid hull bridge')):
   points=[convert(world@Vector(p)) for p in obj.bound_box];lo=tuple(min(p[i] for p in points) for i in range(3));hi=tuple(max(p[i] for p in points) for i in range(3))
   # Include the lower traction lugs in each foot's conservative contact box;
   # the replaceable plate alone sits 5 cm above those visible ground contacts.
   if 'Replaceable pad plate' in obj.name:lo=(lo[0],lo[1]-.05,lo[2])
   root=assignments.get(obj.name,'');offset=Vector(roots[root]['position']);lo=tuple(Vector(lo)-offset);hi=tuple(Vector(hi)-offset)
   roots[root]['children'].append(box_collision('GroundContact_'+str(report['mechanical_colliders']),lo,hi));report['mechanical_colliders']+=1
  if 'Replaceable pad plate' in obj.name:report['legs']+=1
  if 'Stair tread' in obj.name:report['stairs']+=1
  ev.to_mesh_clear()
 for material_key,mesh,label in additions:
  tex='rwm_'+material_key
  mat=bpy.data.materials.get('RW Safety Yellow') if material_key=='safety_yellow' else bpy.data.materials.get('Graphite') if material_key=='groundservice' else next((m for m in bpy.data.materials if image_key(m)==tex),None)
  assert mat is not None,('Missing source appearance',role,tex)
  index,_=material(mat)
  # Individual plant/soil/shelf renderers keep the closest per-tier lights
  # relevant even on KSP graphics settings with limited lights per renderer.
  batch=label if label.startswith('CropShelf_') and material_key in ('grnleaf','grnleaflight','grnroot','steel','graphite') else ''
  for tri in mesh.triangles:append_tri(index,'',[mesh.vertices[i] for i in tri],[mesh.normals[i] for i in tri],[mesh.uvs[i] for i in tri],batch)
 assert report['window_triangles_removed']>=len(removed_windows)*.97,('Old windows did not match source kit',role,report['window_triangles_removed'],len(removed_windows))
 for (index,root,batch),meshes in groups.items():
  mat=model.materials[index];t=next((v[1] for v in matmeta.values() if v[0]==index),None)
  for j,mesh in enumerate(meshes):
   name='GND_'+mat['name']+'_'+str(index)+'_'+str(j)+('_'+root if root else '')
   if batch:name+='_'+batch
   if role=='GRN' and t=='rwm_grnlamp':name='RW_GreenhouseLamps' if j==0 else name
   if role=='GRN' and t=='rwm_grninspection':name='RW_GreenhouseInspectionLamps' if j==0 else name
   n=node(name);n.update(mesh=mesh,materials=[index],shadows=(1,1));roots[root]['children'].append(n)
   if mat['shader']=='KSP/Emissive/Diffuse':report['emissive_renderers'].append(name)
 A,translation=matrix(role);B=C@A
 for src,world in source_world(oldmodel.root,Matrix.Identity(4)):
  if role=='HUB':continue
  if 'collider' not in src or src['collider']['trigger']:continue
  c=copy.deepcopy(src['collider']);n=node('Hull_'+src['name'])
  if c['type']=='mesh':
   m=c['mesh'];m['vertices']=[convert(A@(world@Vector(v))+translation) for v in m['vertices']]
   m['normals']=[tuple((B@(world.to_3x3().inverted().transposed()@Vector(v))).normalized()) for v in m['normals']]
   if B.determinant()<0:m['submeshes']=[[tuple(reversed(t)) for t in triangles] for triangles in m['submeshes']]
  else:
   center=convert(A@(world@Vector(c['center']))+translation);rot=B@world.to_3x3()
   # Collider boxes are symmetric, so an improper orthogonal basis can use its
   # negated third column with identical physical volume and proper quaternion.
   if rot.determinant()<0:rot.col[2]=-rot.col[2]
   q=rot.to_quaternion();n['position']=center;n['rotation']=(q.x,q.y,q.z,q.w);c['center']=(0,0,0)
  n['collider']=c;model.root['children'].append(n)
 if role=='HUB':
  model.root['children'].append(round_collision('GroundHubClosedHull',[(h,math.sqrt(1.8**2-h*h)) for h in (-1.36,-.7,0,.7,1.30)]))
  for axis in (0,2):
   for sign in (-1,1):
    model.root['children'].append(round_collision(f'GroundHubPort_{axis}_{sign}',sorted([(sign*1.20,1.24),(sign*2.0,1.24)]),axis))
  model.root['children'].append(round_collision('GroundHubObservationHull',[(1.26,1.25),(1.77,1.25),(2.64,.83)]))
 if role in ('HAB','LAB','CMD','AIR'):
  source=parse((CORE/f'GameData/RoosterWorksStationModules/Parts/{source_id(role)}.cfg').read_text()).children[0]
  half=abs(float(source.get('node_stack_top').split(',')[1]));x=half*.38 if role in ('HAB','LAB') else -.1
  # Exit transform retains the tested spawn location. Boarding is a separate
  # collider volume relative to that transform, overlapping a Kerbal at the
  # actual landing instead of requiring a climb onto the upper door.
  hatch=box_collision('Ground_EVA_Airlock',(x-.40,-1.15,1.43),(x+.40,.55,2.10),'Airlock',True)
  old_center=Vector(hatch['position']);hatch['position']=(x,-.16,1.55);hatch['collider']['center']=tuple(old_center-Vector(hatch['position']));model.root['children'].append(hatch)
  ladder=box_collision('Ground_EVA_Ladder',(x-.25,-2.18,1.5),(x+.25,-.4,1.75),'Ladder',True);ladder['rotation']=(0,1,0,0);offset=Vector(roots['RW_GroundStairs']['position']);ladder['position']=tuple(Vector(ladder['position'])-offset);roots['RW_GroundStairs']['children'].append(ladder)
  report['airlock']=(x,-.16,1.55)
  report['boarding_bounds']=((x-.40,-1.15,1.43),(x+.40,.55,2.10))
 if role=='GRN':
  for shelf in (-.68,-.12,.44):
   for x in (-.8,0,.8):
    n=node('RW_GreenhouseInspectionLight');n['position']=(x,shelf+.26,0);n['light']=dict(type=2,intensity=1.6,range=1.4,color=(1,.91,.76,1),cullingMask=0xffffffff,spotAngle=30);model.root['children'].append(n)
 write(model,OUT/(part+'.mu'));report['draw_calls']=sum(len(v) for v in groups.values());report['native_sha256']=hashlib.sha256((OUT/(part+'.mu')).read_bytes()).hexdigest()
 source=parse((CORE/f'GameData/RoosterWorksStationModules/Parts/{source_id(role)}.cfg').read_text()).children[0];nodes={}
 for key,value in source.values:
  if not key.startswith('node_stack_'):continue
  v=[float(x.strip()) for x in value.split(',')];pos=convert(A@Vector(v[:3])+translation);direction=B@Vector(v[3:6]);nodes[key]=list(pos)+list(direction)+[int(v[6])]
 if role=='HUB':
  nodes={}
  for suffix,guide in (('right','X+'),('left','X-'),('front','Y-'),('back','Y+')):
   p=convert(asset.objects['LATERAL CONNECTION '+guide].matrix_world.translation);p=(p[0],0,p[2]);d=Vector(p).normalized();nodes['node_stack_'+suffix]=list(p)+list(d)+[2]
 report['nodes']=nodes;(R/'Reports').mkdir(exist_ok=True);(R/f'Reports/{part}.json').write_text(json.dumps(report,indent=2)+'\n');print('EXPORTED',part,report['triangles'],'triangles',report['draw_calls'],'draw calls',flush=True)
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ROLES
assert selected and all(role in ROLES for role in selected)
for role in selected:export(role)
