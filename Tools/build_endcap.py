"""Original rounded 2.5 -> 1.25 m endcap, native MU and editable OBJ source.

All existing ground models and configurations remain read-only to this builder.
Canonical procedural geometry is Y-axial; a proper cyclic rotation maps it to
the ground family's X axis. Both mating planes remain clear of decoration.
"""
from pathlib import Path
import sys,math,copy,json,hashlib
import numpy as np
from PIL import ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
import build_hab250 as h
from station_endcaps import face_mesh,append
from surface_uv import finish
from appearance_textures import label,font
from build_adp250375 import collision_section
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
from build_ring_options import components,circular,ranges,SURFACES
GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models';ID='RW_GND_END_250_125'
HALF=.45
def profile(t):
 # Cubic shoulder: tangent to the large barrel and rounded into the nose.
 p=((-0.36,1.204),(.13,1.204),(.35,.90),(.35,.602));s=1-t
 y=sum(c*p[i][0] for i,c in enumerate((s**3,3*s*s*t,3*s*t*t,t**3)))
 r=sum(c*p[i][1] for i,c in enumerate((s**3,3*s*s*t,3*s*t*t,t**3)))
 dy=3*s*s*(p[1][0]-p[0][0])+6*s*t*(p[2][0]-p[1][0])+3*t*t*(p[3][0]-p[2][0])
 dr=3*s*s*(p[1][1]-p[0][1])+6*s*t*(p[2][1]-p[1][1])+3*t*t*(p[3][1]-p[2][1])
 return y,r,dy,dr
def point(t,a,lift=0):
 y,r,dy,dr=profile(t);return ((r+lift)*math.sin(a),y,(r+lift)*math.cos(a))
def normal(t,a):
 y,r,dy,dr=profile(t);n=np.array((dy*math.sin(a),-dr,dy*math.cos(a)));return tuple(n/np.linalg.norm(n))
def panel(mesh,t0,t1,a0,a1,lift=0,rows=8,cols=8,label_side=0):
 for i in range(rows):
  for j in range(cols):
   samples=((i/rows,j/cols),(i/rows,(j+1)/cols),((i+1)/rows,(j+1)/cols),((i+1)/rows,j/cols))
   ps=[];ns=[];uv=[]
   for u,v in samples:
    t=t0+(t1-t0)*u;a=a0+(a1-a0)*v;ps.append(point(t,a,lift));ns.append(normal(t,a))
    # finish() flips label U once for KSP. Supply its inverse here so the
    # final plate reads outward along the ground module's horizontal axis.
    uv.append((u,1-v) if label_side>0 else (1-u,v) if label_side<0 else (u,v))
   mesh.quad(ps,ns,uv)
def cap(meshes,sign,small=False):
 if small:
  small_cap(meshes)
  return
 for key,src in face_mesh().items():
  dst=h.Mesh()
  for (x,y,z),(nx,ny,nz) in zip(src.vertices,src.normals):
   r=math.hypot(x,z)
   if small:
    # Keep a full-size pressure hatch on the small face, with a narrow metal
    # perimeter instead of shrinking the old 2.5 m hatch to toy proportions.
    rr=r*.90 if r<=.615 else .5535+(r-.615)*(.6125-.5535)/(1.225-.615)
    slope=.90 if r<=.615 else (.6125-.5535)/(1.225-.615)
    scale=rr/r if r>1e-9 else .90
    if r>1e-9:
     radial=(nx*x+nz*z)/r;tangent=(-nx*z+nz*x)/r
     vx=radial/slope*x/r-tangent/scale*z/r;vz=radial/slope*z/r+tangent/scale*x/r
    else:vx,vz=nx/.9,nz/.9
   else:scale=1;vx,vz=nx,nz
   dst.vertices.append((x*scale,sign*(HALF+y-2),sign*z*scale))
   n=np.array((vx,sign*ny,sign*vz));dst.normals.append(tuple(n/np.linalg.norm(n)))
  dst.uvs=list(src.uvs);dst.triangles=list(src.triangles);append(meshes[key],dst)

def small_cap(meshes):
 # Original 1.25 m face: no compressed 2.5 m blanket atlas or folded labels.
 local={key:h.Mesh() for key in h.TEXTURES}
 for material,inner,outer,depth in (('steel',.54,.6125,-.006),('bronze',.525,.54,-.011),('black',.505,.525,-.018),('ceramic',.115,.505,-.026),('steel',.09,.115,-.017),('black',0,.09,-.024)):
  h.annulus(local[material],inner,outer,HALF+depth,1,96)
 wall=h.Mesh();h.cylinder_surface(wall,.505,HALF-.026,HALF-.007,96)
 wall.normals=[tuple(-a for a in n) for n in wall.normals];wall.triangles=[(a,c,b) for a,b,c in wall.triangles];append(local['black'],wall)
 h.cylinder_surface(local['steel'],.6125,HALF-.09,HALF-.006,96)
 for j in range(12):
  a=j*math.tau/12;p=h.point(.576,a,HALF-.010);q=h.point(.576,a,HALF-.002)
  h.tube(local['graphite'],p,q,.012,10)
 h.tube(local['steel'],(-.16,HALF-.025,-.24),(.16,HALF-.025,-.24),.016,12)
 # Planar UVs across each surface give continuous, uniform hatch texture.
 for material,mesh in local.items():
  mesh.uvs=[(.5+x/1.225,.5+z/1.225) for x,y,z in mesh.vertices]
  mesh.vertices=[(x,y,z) for x,y,z in mesh.vertices]
  append(meshes[material],mesh)
 crest=h.Mesh();crest.quad([(-.085,HALF-.019,.19),(.085,HALF-.019,.19),(.085,HALF-.019,.36),(-.085,HALF-.019,.36)],[(0,1,0)]*4)
 append(meshes['crest'],crest)
def geometry():
 m={key:h.Mesh() for key in (*h.TEXTURES,'gnd_endlabel')}
 panel(m['graphite'],0,1,0,math.tau,rows=32,cols=128)
 for col in range(20):
  for row in range(3):
   panel(m['cladding_white' if col%5==0 else 'cladding'],row/3+.004,(row+1)/3-.004,math.tau*col/20+.006,math.tau*(col+1)/20-.006,.003,8,6)
 for lo,hi,r in ((-.45,-.36,1.204),(.35,.45,.602)):
  h.cylinder_surface(m['white'],r,lo,hi,segments=128)
  for mat,offset,width,extra in (('steel',.022,.018,.012),('bronze',.046,.007,.018)):
   y=lo+offset if lo<0 else hi-offset
   h.cylinder_surface(m[mat],r+extra,y-width/2,y+width/2,segments=128)
 cap(m,-1);cap(m,1,True)
 for a in (0,math.pi/2,math.pi,3*math.pi/2):
  # Conforming paired routed lines and solid saddles across the shoulder.
  gap=.16 if a in (math.pi/2,3*math.pi/2) else .035
  for da,mat,rad in ((-gap,'steel',.009),(gap,'bronze',.006)):
   for i in range(24):h.tube(m[mat],point(.05+.85*i/24,a+da,.018),point(.05+.85*(i+1)/24,a+da,.018),r=rad,sides=8)
  for t in (.08,.72):
   h.tube(m['steel'],point(t,a-.055,.020),point(t,a+.055,.020),r=.018,sides=8)
 for a in (math.pi/4,5*math.pi/4):
  # Two stand-off grab rails following the rounded profile.
  for i in range(18):h.tube(m['rail'],point(.16+.52*i/18,a,.055),point(.16+.52*(i+1)/18,a,.055),r=.017,sides=10)
  for t in (.16,.68):h.tube(m['steel'],point(t,a,.008),point(t,a,.055),r=.024,sides=8)
 for a,side in ((math.pi/2,1),(3*math.pi/2,-1)):
  for key,t0,t1,w,lift in (('graphite',.14,.49,.23,.014),('bronze',.15,.48,.21,.019),('gnd_endlabel',.16,.47,.19,.023)):
   panel(m[key],t0,t1,a-w/2,a+w/2,lift,12,8,label_side=side)
 # Continue the ground family's paired underside lines across the reducer.
 # Large endpoints match the accepted +/-600 mm runs exactly; the small
 # endpoints use half spacing and height, ready for a 1.25 m continuation.
 for side in (-1,1):
  for height,rad in ((-1.03,.065),(-1.16,.045)):
   path=[(-.45,1.204),(-.36,1.204)]+[(profile(t)[0],profile(t)[1]) for t in np.linspace(0,1,25)[1:]]+[(.45,.602)]
   for (y0,r0),(y1,r1) in zip(path,path[1:]):
    a=(side*.6*r0/1.204,y0,height*r0/1.204);b=(side*.6*r1/1.204,y1,height*r1/1.204)
    h.tube(m['graphite'],a,b,r=rad*(r0+r1)/(2*1.204),sides=12)
 finish(m)
 # Nose uses an upright outward mapping; retain the correct rear-face mapping.
 m['crest'].uvs=[(1-u,v) if p[1]>0 else (u,v) for p,(u,v) in zip(m['crest'].vertices,m['crest'].uvs)]
 return m
def native(p):return (p[1],p[2],p[0])
def node(name):return dict(name=name,position=(0,0,0),rotation=(0,0,0,1),scale=(1,1,1),children=[],tag='Untagged',layer=0)
def build():
 m=geometry();donor=load(CORE/'GameData/RoosterWorksStationModules/Models/RW_ADP_250_375.mu');model=copy.deepcopy(donor);model.name=ID;model.root=node(ID);model.materials=[];model.textures=[]
 im=label('END-250/125','ENDCAP');draw=ImageDraw.Draw(im);draw.rectangle((47,47,976,86),fill=(48,64,70));draw.text((65,49),'GROUND SYSTEMS   /   2.5 M TO 1.25 M',font=font(23,True),fill=(229,232,221));im.save(OUT/'rwm_gnd_endlabel.png',optimize=True)
 for key,mesh in m.items():
  if not mesh.triangles:continue
  texture='rwm_'+key;sample='rwm_label' if key=='gnd_endlabel' else texture
  original=next(mat for mat in donor.materials if donor.textures[mat['properties']['_MainTex']['index']]['name']==sample)
  mat=copy.deepcopy(original);mat['name']='RW_GroundEndcap_'+key;index=len(model.materials)
  if key!='gnd_endlabel' and not (OUT/(texture+'.png')).exists():(OUT/(texture+'.png')).write_bytes((CORE/'GameData/RoosterWorksStationModules/Models'/(texture+'.png')).read_bytes())
  model.textures.append(dict(name=texture,type=0));mat['properties']['_MainTex']['index']=index;model.materials.append(mat)
  vertices=[native(v) for v in mesh.vertices];normals=[native(n) for n in mesh.normals];tris=[]
  for tri in mesh.triangles:
   p=np.array([vertices[i] for i in tri]);n=np.mean([normals[i] for i in tri],axis=0)
   tris.append(tuple(reversed(tri)) if np.dot(np.cross(p[1]-p[0],p[2]-p[0]),n)<0 else tuple(tri))
  n=node('RW_Endcap_'+key);n.update(mesh=dict(vertices=vertices,normals=normals,uvs=list(mesh.uvs),submeshes=[tris]),materials=[index],shadows=(1,1));model.root['children'].append(n)
 # Eight convex frustums approximate the rounded shoulder from inside. They
 # stay below PhysX's triangle limit and seal both ends of every segment.
 sections=[(-.45,1.204),(-.36,1.204)]+[(profile(t)[0],profile(t)[1]) for t in np.linspace(0,1,9)[1:]]+[(.45,.602)]
 for i,((y0,r0),(y1,r1)) in enumerate(zip(sections,sections[1:])):
  c=collision_section(y0,y1,r0,r1);n=node('EndcapHull_'+str(i));n['collider']=dict(type='mesh',trigger=0,convex=1,mesh=dict(vertices=[native(v) for v in c.vertices],normals=[native(v) for v in c.normals],uvs=c.uvs,submeshes=[c.triangles]));model.root['children'].append(n)
 ports=[]
 for end,sign,kind in (('top',1,'size1'),):
  name='RW_Dock_'+end;n=node(name);n['position']=(sign*HALF,0,0);n['rotation']=(0,sign*math.sin(math.pi/4),0,math.cos(math.pi/4));model.root['children'].append(n)
  ports.append(dict(attachNode=end,transform=name,nodeType=kind,position=list(n['position']),forward=[sign,0,0]))
 write(model,OUT/(ID+'.mu'))
 values=[('name',ID),('module','Part'),('author','SockedRooster'),('rescaleFactor','1'),('node_stack_top','.45, 0, 0, 1, 0, 0, 1'),('node_stack_bottom','-.45, 0, 0, -1, 0, 0, 2'),('attachRules','1,0,1,1,0'),('bulkheadProfiles','size1, size2'),('TechRequired','advConstruction'),('entryCost','5400'),('cost','1350'),('category','Structural'),('subcategory','0'),('title','RoosterWorks Ground END-250/125 — Rounded Docking Endcap'),('manufacturer','RoosterWorks'),('description','Short rounded 2.5 m to 1.25 m ground-base endcap. Segmented pressure shell, recessed hatch, grab rails and routed services. Integrated stock-compatible docking at both ends; crossfeed permanently on and staging disabled. No crew capacity or exterior EVA hatch. White/Grey finish and independent ring colors.'),('tags','roosterworks ground base endcap adapter reducer dome docking 2.5 1.25'),('mass','.35'),('vesselType','Base'),('CrewCapacity','0'),('dragModelType','default'),('maximum_drag','.2'),('minimum_drag','.2'),('angularDrag','2'),('crashTolerance','15'),('breakingForce','220'),('breakingTorque','220'),('maxTemp','2000'),('skinMaxTemp','2400'),('fuelCrossFeed','true')]
 children=[Node('MODEL',[('model','RoosterWorksGroundModules/Models/'+ID)]),Node('MODULE',[('name','ModuleRWStationFinish'),('finish','White')]),Node('MODULE',[('name','ModuleRWRingColor'),('ringModel',ID),('ringColor','Original')]),Node('MODULE',[('name','ModuleRWEditorMenu')]),Node('VABORGANIZER:NEEDS[VABOrganizer]',[('organizerSubcategory','crewAdapters')]),Node('MODULE:NEEDS[ConnectedLivingSpace]',[('name','ModuleConnectedLivingSpace'),('passable','true')])]
 for port in ports:children.append(Node('MODULE',[('name','ModuleDockingNode'),('nodeTransformName',port['transform']),('controlTransformName',port['transform']),('referenceAttachNode',port['attachNode']),('useReferenceAttachNode','true'),('nodeType',port['nodeType']),('crossfeed','true'),('stagingEnabled','false'),('stagingToggleEnabledEditor','false'),('stagingToggleEnabledFlight','false'),('canRotate','false')]))
 children.append(Node('MODULE',[('name','ModuleRWGroundDocking')]))
 (GD/'Parts'/(ID+'.cfg')).write_text(dump(Node('ROOT',children=[Node('PART:NEEDS[RoosterWorksStationModules]',values,children)])),encoding='utf-8')
 specs=[]
 for path,n in walk(model.root):
  if 'mesh' not in n:continue
  mat=model.materials[n['materials'][0]];texture=model.textures[mat['properties']['_MainTex']['index']]['name']
  if texture not in SURFACES:continue
  selected=[j for group in components(n['mesh']) if circular(n['mesh'],group) for j in group]
  if selected:specs.append(Node('MESH',[('path',path),('texture',texture),('vertices',str(len(n['mesh']['vertices']))),('triangles',str(len(n['mesh']['submeshes'][0]))),('ranges',ranges(sorted(selected)))]))
 assert specs
 (GD/'Compatibility/EndcapRingGeometry.cfg').write_text(dump(Node('ROOT',children=[Node('RW_RING_MAP',[('model',ID)],specs)])))
 (GD/'Compatibility/EndcapVABOrganizer.cfg').write_text(dump(Node('ROOT',children=[Node('@PART['+ID+']:NEEDS[VABOrganizer]:FINAL',children=[Node('!VABORGANIZER,*'),Node('VABORGANIZER',[('organizerSubcategory','crewAdapters')])])])))
 report=dict(role='END_250_125',triangles=sum(len(mesh.triangles) for mesh in m.values()),legs=0,stairs=0,motion=[],docking_ports=ports,nodes={'node_stack_top':[.45,0,0,1,0,0,1],'node_stack_bottom':[-.45,0,0,-1,0,0,2]},native_sha256=hashlib.sha256((OUT/(ID+'.mu')).read_bytes()).hexdigest(),length=.9,interfaces=[2.5,1.25],colliders=len(sections)-1)
 (R/'Reports'/(ID+'.json')).write_text(json.dumps(report,indent=2)+'\n')
 # OBJ uses Blender Z-up: (native X, -native Z, native Y).
 folder=R/'Source/Endcap';folder.mkdir(exist_ok=True);obj=folder/(ID+'.obj');mtl=folder/(ID+'.mtl');lines=['mtllib '+mtl.name];offset=1;materials=[]
 for _,n in walk(model.root):
  if 'mesh' not in n:continue
  mesh=n['mesh'];mat=model.materials[n['materials'][0]];texture=model.textures[mat['properties']['_MainTex']['index']]['name'];lines+=['o '+n['name'],'usemtl '+mat['name']]
  lines+=['v %.8f %.8f %.8f'%(x,-z,y) for x,y,z in mesh['vertices']];lines+=['vt %.8f %.8f'%uv for uv in mesh['uvs']];lines+=['vn %.8f %.8f %.8f'%(x,-z,y) for x,y,z in mesh['normals']]
  lines+=['f '+' '.join(f'{i+offset}/{i+offset}/{i+offset}' for i in tri) for tri in mesh['submeshes'][0]];offset+=len(mesh['vertices'])
  relative='../../GameData/RoosterWorksGroundModules/Models/'+texture+'.png';materials+=['newmtl '+mat['name'],'Kd 1 1 1','map_Kd '+relative,'']
 obj.write_text('\n'.join(lines)+'\n');mtl.write_text('\n'.join(materials)+'\n')
 files=sorted(p for p in (R/'GameData').rglob('*') if p.is_file());(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in files))
 print('Built',ID,report['triangles'],'triangles, .9 m length, size2 structural rear / size1 docking nose, no staging, finish and ring variants',flush=True)
if __name__=='__main__':build()
