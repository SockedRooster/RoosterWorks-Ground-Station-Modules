import re
from mathutils import Vector

def remove_middle_legs(asset,convert):
 # Remove complete assemblies on exported copies, including all fixed mounts,
 # hydraulic detail and pad hardware. Shared underfloor service pipes remain.
 saddles=[o for o in asset.objects if re.match(r'Leg \d+ \| hull saddle$',o.name)]
 assert len(saddles)==6
 def midpoint(obj):
  points=[Vector(convert(obj.matrix_world@Vector(p))) for p in obj.bound_box]
  return sum(points,Vector())/len(points)
 centers={int(re.search(r'Leg (\d+)',o.name)[1]):midpoint(o) for o in saddles}
 middle={number for number,p in centers.items() if abs(p.x)<.1};assert middle=={2,3}
 prefixes=('Pivot keeper','Seal collar','Copper compression ring','Anti rotation guide','Torque-link clevis','Hydraulic hose','Foot swivel','Wide load-spreading pad','Replaceable pad plate','Foot bronze perimeter','Captive hex fastener','Pad radial traction lug')
 removed=[]
 for obj in list(asset.objects):
  explicit=re.match(r'Leg (\d+) \| ',obj.name)
  if explicit:owner=int(explicit[1])
  elif obj.name.startswith(prefixes):
   p=midpoint(obj);owner=min(centers,key=lambda n:(p-centers[n]).length_squared)
  else:continue
  if owner in middle:
   assert all(abs(convert(obj.matrix_world@Vector(p))[0])<.5 for p in obj.bound_box),('End-leg hardware selected',obj.name)
   removed.append(obj.name)
 assert len(removed)==60,('Incomplete middle-leg assembly removal',len(removed))
 import bpy
 for name in removed:bpy.data.objects.remove(asset.objects[name],do_unlink=True)
 assert len([o for o in asset.objects if 'Replaceable pad plate' in o.name])==4
 return removed

def build(asset,convert):
 def center(o):return sum((Vector(convert(o.matrix_world@Vector(p))) for p in o.bound_box),Vector())/8
 feet=sorted([o for o in asset.objects if 'Replaceable pad plate' in o.name],key=lambda o:o.name)
 rams=sorted([o for o in asset.objects if 'polished ram' in o.name],key=lambda o:o.name)
 assignments={};bindings=[]
 for ram in rams:
  number=int(re.search(r'Leg (\d+)',ram.name)[1]);prefix=f'Leg {number:02d} | '
  sleeve=asset.objects[prefix+'upper pressure sleeve'];foot=min(feet,key=lambda o:(center(o)-center(ram)).length)
  direction=(center(sleeve)-center(foot)).normalized();name=f'RW_GroundLeg{number:02d}'
  bindings.append(dict(name=name,position=(0,0,0),retractPosition=tuple(direction*.72),retractEuler=(0,0,0),mechanism='Legs',foot=foot.name))
  assignments[ram.name]=name
 for o in asset.objects:
  if o.type!='MESH':continue
  if any(o.name.startswith(p) for p in ('Foot ','Wide load','Replaceable pad','Captive hex','Pad radial','Anti rotation','Torque-link','Hydraulic hose')):
   b=min(bindings,key=lambda b:(center(o)-center(asset.objects[b['foot']])).length);assignments[o.name]=b['name']
 stairs=any(o.name.startswith('Stair tread') for o in asset.objects)
 if stairs:
  landing=asset.objects['Access landing'];p=center(landing);p.z=max(convert(landing.matrix_world@Vector(v))[2] for v in landing.bound_box);p.y-=.04
  bindings.append(dict(name='RW_GroundStairs',position=tuple(p),retractPosition=tuple(p),retractEuler=(-130,0,0),mechanism='Stairs'))
  for o in asset.objects:
   if o.name.startswith(('Stair ','Tread anti','High visibility','Handrail stanchion','Continuous copper handrail')):assignments[o.name]='RW_GroundStairs'
 return assignments,bindings

def widen_stairs(asset):
 # Keep rail/stringer tube thickness while adding 18 cm of space per side.
 if 'Access landing' not in asset.objects:return {}
 landing=asset.objects['Access landing'];cx=landing.matrix_world.translation.x;changed=[]
 for obj in asset.objects:
  if obj.type!='MESH':continue
  stretch=obj.name.startswith(('Stair tread','Tread anti slip','High visibility nosing'))
  side=obj.name.startswith(('Handrail stanchion','Continuous copper handrail','Stair stringer','Stair ground shoe'))
  if not (stretch or side or obj==landing):continue
  obj.data=obj.data.copy();world=obj.matrix_world;inverse=world.inverted()
  if side:
   points=[world@Vector(p) for p in obj.bound_box];x=sum(p.x for p in points)/8;offset=.18 if x>cx else -.18
  for v in obj.data.vertices:
   p=world@v.co
   if side:p.x+=offset
   else:p.x=cx+(p.x-cx)*((1.27/.91) if obj==landing else (1.21/.85))
   v.co=inverse@p
  obj.data.update();changed.append(obj.name)
 import bpy
 bpy.context.view_layer.update()
 return dict(width=1.21,rail_center_half_width=.64,changed_objects=changed)
