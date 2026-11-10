"""Original accordion crew connector: native model, source and stock ports."""
from pathlib import Path
import sys,math,copy,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from station_endcaps import face_mesh,append
from build_adp250375 import collision_section
from build_ring_options import components,circular,ranges,SURFACES
from config_nodes import Node,parse,dump
from end_face_refinements import repair,native
import build_hab250 as h
GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models';ID='RW_GND_FLEX'
def node(name,pos=(0,0,0)):return dict(name=name,position=pos,rotation=(0,0,0,1),scale=(1,1,1),children=[],tag='Untagged',layer=0)
def main():
 donor=load(W/'ground-hotpatch-v16/GameData/RoosterWorksGroundModules/Models/RW_GND_TUB.mu');model=copy.deepcopy(donor);model.name=ID;model.root=node(ID)
 indices={model.textures[m['properties']['_MainTex']['index']]['name']:i for i,m in enumerate(model.materials)}
 def meshnode(parent,name,key,mesh):
  if not mesh.triangles:return
  v=np.array(mesh.vertices);norm=np.array(mesh.normals)
  mesh.triangles=[tuple(reversed(t)) if np.dot(np.cross(v[t[1]]-v[t[0]],v[t[2]]-v[t[0]]),norm[list(t)].mean(0))<0 else t for t in mesh.triangles]
  parent['children'].append(native(name,mesh,indices['rwm_'+key]))
 def collision(parent,name,lo,hi,r):
  c=collision_section(lo,hi,r,r);n=node(name);n['collider']=dict(type='mesh',trigger=0,convex=1,mesh=dict(vertices=[(y,z,x) for x,y,z in c.vertices],normals=[(y,z,x) for x,y,z in c.normals],uvs=c.uvs,submeshes=[c.triangles]));parent['children'].append(n)
 for sign,name,x in ((-1,'RW_TubeBase',-.6),(1,'RW_TubeNose',.6)):
  parent=node(name,(x,0,0));model.root['children'].append(parent)
  for key,mesh in face_mesh().items():
   if not mesh.triangles:continue
   mesh.vertices=[(sign*(y-2),z,sign*a) for a,y,z in mesh.vertices]
   mesh.normals=[(sign*ny,nz,sign*nx) for nx,ny,nz in mesh.normals]
   meshnode(parent,'FlexEnd_'+name+'_'+key,key,mesh)
  shell=h.Mesh();h.cylinder_surface(shell,1.204,-.15 if sign>0 else 0,0 if sign>0 else .15,96)
  shell.vertices=[(y,z,a) for a,y,z in shell.vertices];shell.normals=[(ny,nz,nx) for nx,ny,nz in shell.normals];meshnode(parent,'FlexCollar_'+name,'white',shell)
  collision(parent,'FlexEndCollision_'+name,-.15 if sign>0 else 0,0 if sign>0 else .15,1.19)
  port=node('RW_Dock_top' if sign>0 else 'RW_Dock_bottom');port['rotation']=(0,sign*math.sin(math.pi/4),0,math.cos(math.pi/4));parent['children'].append(port)
 bellows=node('RW_TubeBellows',(-.45,0,0));model.root['children'].append(bellows)
 mesh=h.Mesh();ribs=h.Mesh();steps=80;sides=64
 for i in range(steps):
  x0=.9*i/steps;x1=.9*(i+1)/steps;r0=1.13 if i%2==0 else 1.205;r1=1.205 if i%2==0 else 1.13;slope=(r1-r0)/(x1-x0)
  for j in range(sides):
   a=j*math.tau/sides;b=(j+1)*math.tau/sides
   def point(x,r,t):return (x,r*math.sin(t),r*math.cos(t))
   def normal(t):
    n=np.array((-slope,math.sin(t),math.cos(t)));return tuple(n/np.linalg.norm(n))
   mesh.quad([point(x0,r0,a),point(x0,r0,b),point(x1,r1,b),point(x1,r1,a)],[normal(a),normal(b),normal(b),normal(a)],[(i/steps,j/sides),(i/steps,(j+1)/sides),((i+1)/steps,(j+1)/sides),((i+1)/steps,j/sides)])
 meshnode(bellows,'RW_FlexPressureBellows','graphite',mesh)
 # Reinforcing hoops give the accordion a readable mechanical silhouette.
 for i in range(40):
  x=.9*(2*i+1)/80
  for j in range(32):
   a=j*math.tau/32;b=(j+1)*math.tau/32
   h.tube(ribs,(x,1.208*math.sin(a),1.208*math.cos(a)),(x,1.208*math.sin(b),1.208*math.cos(b)),.003,6)
 meshnode(bellows,'RW_FlexReinforcingHoops','steel',ribs);collision(bellows,'FlexPressureCollision',0,.9,1.12)
 p=Node('PART:NEEDS[RoosterWorksStationModules]',[('name',ID),('module','Part'),('author','SockedRooster'),('rescaleFactor','1'),('attachRules','1,0,1,1,0'),('node_stack_top','.6, 0, 0, 1, 0, 0, 2'),('node_stack_bottom','-.6, 0, 0, -1, 0, 0, 2'),('bulkheadProfiles','size2'),('TechRequired','advConstruction'),('entryCost','7200'),('cost','4600'),('category','Structural'),('subcategory','0'),('title','RoosterWorks Ground FLEX — Collapsible Crew Tube'),('manufacturer','RoosterWorks'),('description','Legless 2.5 m crew passage with an accordion pressure shell. Collapses to 1.2 m and extends to 4 m. Stock docking at both ends. Keep the rear end attached; disconnect the moving nose before resizing. Crewless passage, no extra life-support volume or storage. White/Grey finish, ring colors and warm end-window lights.'),('tags','roosterworks ground crew tube tunnel flexible collapsible accordion connector docking'),('mass','.65'),('CrewCapacity','0'),('vesselType','Base'),('dragModelType','default'),('maximum_drag','.2'),('minimum_drag','.2'),('angularDrag','2'),('crashTolerance','13'),('breakingForce','350'),('breakingTorque','350'),('maxTemp','2000'),('skinMaxTemp','2400'),('fuelCrossFeed','true')],[Node('MODEL',[('model','RoosterWorksGroundModules/Models/'+ID)]),Node('MODULE',[('name','ModuleRWCollapsibleTube'),('extension','0'),('targetExtension','0'),('duration','6')]),Node('MODULE',[('name','ModuleRWStationFinish'),('finish','White')]),Node('MODULE',[('name','ModuleRWRingColor'),('ringModel',ID),('ringColor','Original')]),Node('MODULE',[('name','ModuleRWEditorMenu')]),Node('VABORGANIZER:NEEDS[VABOrganizer]',[('organizerSubcategory','crewTubes')]),Node('MODULE:NEEDS[ConnectedLivingSpace]',[('name','ModuleConnectedLivingSpace'),('passable','true')])])
 for end,sign in (('top',1),('bottom',-1)):
  p.children.append(Node('MODULE',[('name','ModuleDockingNode'),('nodeTransformName','RW_Dock_'+end),('controlTransformName','RW_Dock_'+end),('referenceAttachNode',end),('useReferenceAttachNode','true'),('nodeType','size2'),('crossfeed','true'),('stagingEnabled','false'),('stagingToggleEnabledEditor','false'),('stagingToggleEnabledFlight','false'),('canRotate','false')]))
 p.children.append(Node('MODULE',[('name','ModuleRWGroundDocking')]))
 # Repair expects root-space source end geometry; flatten the two caps once,
 # then move the repaired face badges/windows back beneath their owning cap.
 def flatten_end(n,offset):
  for c in n['children']:
   if 'mesh' in c:c['mesh']['vertices']=[tuple(np.array(v)+offset) for v in c['mesh']['vertices']]
  n['position']=(0,0,0)
 for name,x in (('RW_TubeBase',-.6),('RW_TubeNose',.6)):flatten_end(next(n for n in model.root['children'] if n['name']==name),np.array((x,0,0)))
 audit=repair(model,p)
 # Restore local cap coordinates and repair-added faces to correct moving parents.
 for name,x in (('RW_TubeBase',-.6),('RW_TubeNose',.6)):
  n=next(n for n in model.root['children'] if n['name']==name);n['position']=(x,0,0)
  for c in n['children']:
   if 'mesh' in c:c['mesh']['vertices']=[(a-x,b,c0) for a,b,c0 in c['mesh']['vertices']]
 for name in ('RW_EndFaceBadges','RW_EndWindows'):
  source=next(n for n in model.root['children'] if n['name']==name);model.root['children'].remove(source)
  for sign,parentname,x in ((-1,'RW_TubeBase',-.6),(1,'RW_TubeNose',.6)):
   child=copy.deepcopy(source);m=child['mesh'];keep=[all(sign*m['vertices'][i][0]>0 for i in t) for t in m['submeshes'][0]]
   from end_face_refinements import compact
   compact(m,keep);m['vertices']=[(a-x,b,c0) for a,b,c0 in m['vertices']]
   next(n for n in model.root['children'] if n['name']==parentname)['children'].append(child)
 # Each moving/rear renderer has a distinct name, explicitly controlled together.
 for parent in model.root['children']:
  for child in parent['children']:
   if child['name']=='RW_EndWindows':child['name']+='_'+parent['name']
 changer=next(n for n in p.children if n.get('name')=='ModuleColorChanger');changer.values=[(k,v) for k,v in changer.values if k!='includedRenderer']+[('includedRenderer','RW_EndWindows_RW_TubeBase'),('includedRenderer','RW_EndWindows_RW_TubeNose')]
 write(model,OUT/(ID+'.mu'));(GD/'Parts'/(ID+'.cfg')).write_text(dump(Node('ROOT',children=[p])),encoding='utf-8')
 specs=[]
 for path,n in walk(model.root):
  if 'mesh' not in n:continue
  if n['name']=='RW_FlexReinforcingHoops':continue # Mating-ring colors leave pressure reinforcement metallic.
  tex=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
  if tex not in SURFACES:continue
  selected=[j for group in components(n['mesh']) if circular(n['mesh'],group) for j in group]
  if selected:specs.append(Node('MESH',[('path',path),('texture',tex),('vertices',str(len(n['mesh']['vertices']))),('triangles',str(len(n['mesh']['submeshes'][0]))),('ranges',ranges(sorted(selected)))]))
 (GD/'Compatibility/FlexRingGeometry.cfg').write_text(dump(Node('ROOT',children=[Node('RW_RING_MAP',[('model',ID)],specs)])))
 report=dict(role='FLEX',triangles=sum(len(s) for _,n in walk(model.root) if 'mesh' in n for s in n['mesh']['submeshes']),legs=0,stairs=0,motion=[],collapsed_length=1.2,extended_length=4,nodes={'node_stack_top':[.6,0,0,1,0,0,2],'node_stack_bottom':[-.6,0,0,-1,0,0,2]},end_face_refinement=audit)
 (R/f'Reports/{ID}.json').write_text(json.dumps(report,indent=2)+'\n');print('Built legless FLEX tube, 1.2-4.0 m, two docking ends (one moving), finish/ring controls and end lights')
if __name__=='__main__':main()
