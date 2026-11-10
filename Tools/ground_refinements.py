"""Ground-only derivative geometry: roof clearance, crop shelves and service runs."""
import math,re,random
from mathutils import Vector
import build_hab250 as h
import build_grn250 as grn
import build_crew_tubes as tubes
from ground_layout import blank
from surface_uv import finish

def refine_hardware(asset,role,convert):
 def midpoint(o):return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
 result={'handrail_reduction':.12,'greenhouse_leg_shift':0,'extended_pipes':[]}
 result['removed_roof_objects']=[]
 if role in ('GRN','PWR'):
  import bpy
  for obj in list(asset.objects):
   if obj.name.startswith(('Roof heat exchanger','Radiator fin')):
    result['removed_roof_objects'].append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
 # Change vertices in world space; procedural helper objects often have an
 # origin at world zero, unrelated to the location of their visible hardware.
 def edit(obj,fn):
  obj.data=obj.data.copy();w=obj.matrix_world;inv=w.inverted()
  for vertex in obj.data.vertices:vertex.co=inv@fn(w@vertex.co)
  obj.data.update()
 for o in asset.objects:
  if o.type!='MESH':continue
  if o.name.startswith('Handrail stanchion'):
   base=min((o.matrix_world@Vector(v)).z for v in o.bound_box)
   def shorten(p):p.z=base+(p.z-base)*(.73/.85);return p
   edit(o,shorten)
  elif o.name.startswith('Continuous copper handrail'):
   def lower(p):p.z-=.12;return p
   edit(o,lower)
 if role=='GRN':
  saddles=[o for o in asset.objects if re.match(r'Leg \d+ \| hull saddle$',o.name)]
  centers={int(re.search(r'Leg (\d+)',o.name)[1]):midpoint(o) for o in saddles}
  prefixes=('Pivot keeper','Seal collar','Copper compression ring','Anti rotation guide','Torque-link clevis','Hydraulic hose','Foot swivel','Wide load-spreading pad','Replaceable pad plate','Foot bronze perimeter','Captive hex fastener','Pad radial traction lug')
  for o in asset.objects:
   explicit=re.match(r'Leg (\d+) \| ',o.name)
   if explicit:owner=int(explicit[1])
   elif o.name.startswith(prefixes):owner=min(centers,key=lambda n:(midpoint(o)-centers[n]).length_squared)
   else:continue
   dx=math.copysign(.26,centers[owner].x)
   def shift(p):p.x+=dx;return p
   edit(o,shift)
  result['greenhouse_leg_shift']=.26
 # The original four service tubes end 12 cm short of each stack plane.
 # Extend the full tubes to the exact interface without changing their radii,
 # lateral spacing, height or surface material.
 if role not in ('HUB','ELB'):
  for o in asset.objects:
   if not o.name.startswith('Protected underfloor service pipe'):continue
   points=[o.matrix_world@Vector(v) for v in o.bound_box];half=max(abs(p.x) for p in points);target=half+.12
   def stretch(p):p.x*=target/half;return p
   edit(o,stretch);result['extended_pipes'].append({'object':o.name,'half':target})
 import bpy
 bpy.context.view_layer.update()
 return result

def box(mesh,lo,hi):
 # Native coordinates: X horizontal axis, Y up, Z front.
 for axis in range(3):
  a=(axis+1)%3;b=(axis+2)%3
  for sign in (-1,1):
   pts=[];n=[0,0,0];n[axis]=sign
   for u,v in ((0,0),(1,0),(1,1),(0,1)):
    p=[0,0,0];p[axis]=lo[axis] if sign<0 else hi[axis];p[a]=(lo[a],hi[a])[u];p[b]=(lo[b],hi[b])[v];pts.append(p)
   mesh.quad(pts,[tuple(n)]*4,reverse=sign<0)

def greenhouse_shelves():
 rng=random.Random(806);additions=[]
 for level,y in enumerate((-.68,-.12,.44)):
  m=blank(tuple(k for k in grn.MAT if k not in h.TEXTURES))
  width=(.72,.89,.66)[level]
  box(m['steel'],(-1.10,y-.065,-width),(1.10,y,width))
  box(m['grnroot'],(-1.06,y,-width+.04),(1.06,y+.012,width-.04))
  for z in (-width, width):h.tube(m['steel'],(-1.11,y+.025,z),(1.11,y+.025,z),r=.019,sides=8)
  for x in (-.88,-.44,0,.44,.88):
   for z in (-width*.65,0,width*.65):
    base=(x,y+.017,z)
    h.tube(m['grnleaf'],base,(x,y+.08,z),r=.008,sides=5)
    for j in range(7):
     grn.leaf(m['grnleaflight' if (j+level)%3==0 else 'grnleaf'],(x,y+.048,z),math.tau*j/7,rng.uniform(.09,.14),rng.uniform(.045,.07),rng.uniform(.045,.10))
  # Lamps sit above each horizontal growing bed, inside the pressure glass.
  for z in (-width*.65,width*.65):
   box(m['black'],(-1.07,y+.335,z-.033),(1.07,y+.37,z+.033))
   box(m['grnlamp'],(-1.04,y+.333,z-.024),(1.04,y+.338,z+.024))
  finish(m)
  additions.extend((key,mesh,'CropShelf_'+str(level)) for key,mesh in m.items() if mesh.triangles)
 m=blank()
 for x in (-1.10,1.10):
  for z in (-.63,.63):h.tube(m['steel'],(x,-.76,z),(x,.84,z),r=.022,sides=8)
 finish(m)
 return additions+[(key,mesh,'HorizontalCropSupports') for key,mesh in m.items() if mesh.triangles]

def elbow_handrails():
 yellow=h.Mesh();feet=h.Mesh();half=tubes.ARCLENGTH/2+tubes.COLLAR
 paths=[]
 for side in (-1,1):
  path=[]
  for i in range(65):
   c,n,t,k=tubes.frame(-half+.16+(2*half-.32)*i/64,True)
   path.append((c[0]+side*.48*n[0],1.38,-(c[1]+side*.48*n[1])))
  paths.append(path)
  for a,b in zip(path,path[1:]):h.tube(yellow,a,b,r=.020,sides=10)
  for i in (0,16,32,48,64):
   x,y,z=path[i];h.tube(yellow,(x,1.10,z),(x,y,z),r=.018,sides=10)
   h.tube(feet,(x,1.095,z),(x,1.145,z),r=.034,sides=10)
 return [('safety_yellow',yellow,'ElbowRoofHandrails'),('graphite',feet,'ElbowHandrailFeet')],paths

def service_network(role):
 # Same two 130/90 mm lines and +/-600 mm side spacing as the straight
 # barrels. Tube ends lie exactly on each stack plane. No collision changes.
 if role not in ('HUB','ELB'):return [],[]
 m=h.Mesh();paths=[]
 for side in (-1,1):
  for y,r in ((-1.03,.065),(-1.16,.045)):
   if role=='ELB':
    half=tubes.ARCLENGTH/2+tubes.COLLAR;path=[]
    for i in range(65):
     c,n,t,k=tubes.frame(-half+2*half*i/64,True)
     path.append((c[0]+side*.6*n[0],y,-(c[1]+side*.6*n[1])))
    paths.append({'points':path,'radius':r})
   else:
    for axis in (0,2):
     path=[]
     for s in (-2,-1.65,-1.1,0,1.1,1.65,2):
      p=[side*.6,y,side*.6];p[axis]=s
      # Drop clear of the closed, rounded belly, then return to the common
      # height at every port. Crossing runs share a deliberate service manifold.
      p[1]=y-.48*max(0,1-abs(s)/1.65)
      path.append(tuple(p))
     paths.append({'points':path,'radius':r})
 for item in paths:
  # Continuous swept tubes: shared tangent rings avoid segmented elbow gaps.
  path=[Vector(p) for p in item['points']];radius=item['radius'];rings=[]
  for i,p in enumerate(path):
   t=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized()
   u=t.cross(Vector((0,1,0))).normalized();v=t.cross(u).normalized()
   rings.append([(tuple(p+radius*(u*math.cos(math.tau*j/16)+v*math.sin(math.tau*j/16))),tuple(u*math.cos(math.tau*j/16)+v*math.sin(math.tau*j/16))) for j in range(16)])
  for a,b in zip(rings,rings[1:]):
   for j in range(16):
    coords=(a[j],a[(j+1)%16],b[(j+1)%16],b[j]);m.quad([x[0] for x in coords],[x[1] for x in coords])
 return [('groundservice',m,'ContinuousUnderfloorNetwork')],paths
