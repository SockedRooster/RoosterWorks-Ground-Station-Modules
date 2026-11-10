"""Independent native geometry/config checks, preserved baseline and equipment clearance."""
from pathlib import Path
import sys,json,math,hashlib,copy
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v17';GD=R/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import rotation,world_nodes
assert len(list((GD/'Parts').glob('*.cfg')))==13
assert len(list((GD/'Models').glob('*.mu')))==13
ports=jets=spots=0;new_vertices=0
for path in sorted((GD/'Parts').glob('*.cfg')):
 p=parse(path.read_text(encoding='utf-8')).children[0];ID=p.get('name');model=load(GD/f'Models/{ID}.mu');nodes=list(walk(model.root));lookup={n['name']:n for _,n in nodes}
 assert len(model.materials)==1+max(i for _,n in nodes for i in n.get('materials',[]))
 for _,n in nodes:
  if 'mesh' in n:
   m=n['mesh'];v=np.array(m['vertices']);normal=np.array(m['normals']);tri=np.array(m['submeshes'][0]);assert 0<len(v)<65535 and len(v)==len(normal)==len(m['uvs']) and np.isfinite(v).all()
   assert np.allclose(np.linalg.norm(normal,axis=1),1,atol=2e-5)
   dots=np.sum(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])*normal[tri].mean(1),axis=1);assert (dots>=-1e-6).all(),(ID,n['name'],'backwards faces')
   if n['name'].startswith(('RW_RCS_','RW_DoorLight','RW_VT_')):new_vertices+=len(v)
  if 'light' in n:assert n['light']['range']>0 and n['light']['intensity']>0
  for i in n.get('materials',[]):
   mat=model.materials[i]
   for value in mat['properties'].values():
    if isinstance(value,dict):
     tex=model.textures[value['index']]['name'];assert (GD/f'Models/{tex}.png').exists() or (CORE/f'GameData/RoosterWorksStationModules/Models/{tex}.png').exists(),tex
 for n in p.children:
  if n.get('name')=='ModuleDockingNode':
   ports+=1;assert n.get('acquireForce')=='40';assert n.get('nodeTransformName') in lookup
 if ID!='RW_GND_VT':
  oldm=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu');oldp=parse((OLD/'GameData/RoosterWorksGroundModules/Parts'/path.name).read_text(encoding='utf-8')).children[0]
  # Strip only new nodes; compare every original triangle, UV, collider, light,
  # transform and hierarchy, including nested moving FLEX and deployment rigs.
  stripped=copy.deepcopy(model)
  def strip(n):
   n['children']=[c for c in n['children'] if not c['name'].startswith(('RW_RCSCluster_','RW_DoorLight','RW_DoorSpot'))]
   for c in n['children']:strip(c)
  strip(stripped.root);assert stripped.root==oldm.root,(ID,'original geometry changed')
  assert model.materials==oldm.materials and model.textures==oldm.textures
  restored=copy.deepcopy(p);restored.children=[n for n in restored.children if n.get('name') not in ('ModuleRCSFX','ModuleRWExteriorLight') and n.header!='EFFECTS']
  restored.set('mass',oldp.get('mass'));restored.set('cost',oldp.get('cost'));restored.set('description',oldp.get('description'));assert dump(restored)==dump(oldp),(ID,'unrequested config change')
  assert math.isclose(float(p.get('mass'))-float(oldp.get('mass')),.04,abs_tol=1e-6)
  rcs=next(n for n in p.children if n.get('name')=='ModuleRCSFX');assert rcs.get('resourceName')=='MonoPropellant' and rcs.get('thrusterPower')=='.6'
  frames=[n for _,n in nodes if n['name']=='RW_GroundRCS'];assert len(frames)==16;jets+=len(frames)
  directions=np.array([rotation(n['rotation'])@np.array((0,1,0)) for n in frames])
  # Every cardinal thrust direction is available; jets point out from solid mounts.
  for axis in range(3):
   for sign in (-1,1):assert np.max(sign*directions[:,axis])>.99999
  if ID=='RW_GND_FLEX':
   base=next(n for n in model.root['children'] if n['name']=='RW_TubeBase');assert len([n for n in base['children'] if n['name'].startswith('RW_RCSCluster_')])==4
   assert all(not any(n['name']=='RW_GroundRCS' for _,n in walk(parent)) for parent in model.root['children'] if parent['name']!='RW_TubeBase')
  if ID in ('RW_GND_HAB','RW_GND_CMD','RW_GND_AIR'):
   spots+=1;spot=lookup['RW_DoorSpot'];light=spot['light'];direction=rotation(spot['rotation'])@np.array((0,0,1));origin=np.array(spot['position'])
   assert light['type']==0 and light['spotAngle']==90 and light['range']==9 and direction[1]<-.8 and direction[2]>.49
   ext=next(n for n in p.children if n.get('name')=='ModuleRWExteriorLight');assert ext.get('lightMeshRendererName')=='RW_DoorLightLens' and ext.get('resourceAmount')=='.03' and ext.get('isOn')=='false'
   # Landing and each physical stair tread fall inside actual spot cone/range.
   covered_treads=0
   stair_nodes={id(n) for _,n in walk(lookup['RW_GroundStairs'])}
   for n,m in world_nodes(model,1):
    if 'collider' not in n or n['collider'].get('trigger'):continue
    c=n['collider']
    if id(n) not in stair_nodes or c['type']!='box' or c['size'][0]<1:continue
    if c['type']=='box':center=np.array(c['center'])
    else:center=np.mean(c['mesh']['vertices'],axis=0)
    target=m[:3,:3]@center+m[:3,3];delta=target-origin;distance=np.linalg.norm(delta);assert distance<light['range'] and np.dot(delta/distance,direction)>math.cos(math.radians(45)),(ID,n['name'],'outside beam',target)
    covered_treads+=1
   assert covered_treads>=8,(ID,'stair coverage checks did not inspect all treads',covered_treads)
   # Fixture remains outside the moving stair/rail surfaces in five poses.
   for t in (0,.25,.5,.75,1):
    for n,m in world_nodes(model,t):
     if n['name'].startswith('GND_') and 'mesh' in n and any(n is c for _,c in walk(lookup['RW_GroundStairs'])):
      v=np.array(n['mesh']['vertices'])@m[:3,:3].T+m[:3,3]
      assert not ((np.abs(v[:,0]-origin[0])<.24)&(np.abs(v[:,1]-origin[1])<.10)&(np.abs(v[:,2]-origin[2])<.09)).any(),(ID,'stairs clip light',t)
 else:
  names=[n.get('name') for n in p.children];assert 'ModuleDockingNode' not in names and 'ModuleCommand' not in names and 'ModuleRWGroundDocking' not in names
  assert p.get('attachRules')=='1,1,0,1,0' and p.get('node_attach')=='0, 0, 0, 0, 0, -1, 1'
  assert not any(n.get('tag') in ('Airlock','Ladder') for _,n in nodes)
  engine=next(n for n in p.children if n.get('name')=='ModuleEnginesFX');assert engine.get('maxThrust')=='60'
  thrust=lookup[engine.get('thrustVectorTransformName')];gimbal=lookup['RW_VT_Gimbal'];assert np.allclose(rotation(gimbal['rotation'])@rotation(thrust['rotation'])@np.array((0,0,1)),(0,-1,0),atol=1e-6)
  assert next(n for n in p.children if n.get('name')=='ModuleGimbal').get('gimbalRange')=='3'
  resources={n.get('name'):float(n.get('maxAmount')) for n in p.children if n.header=='RESOURCE'};assert resources=={'LiquidFuel':90,'Oxidizer':110,'MonoPropellant':60}
  assert math.isclose(float(p.get('mass'))+(90+110)*.005+60*.004,1.84)
  assert 120/(9.80665*(3.86+.04+2*1.84))>1.5,'Balanced pair cannot lift loaded HAB at Kerbin gravity'
 print('PASS',ID,'preserved geometry/roles + equipment checks',flush=True)
assert ports==25 and jets==192 and spots==3
for filename in ('GroundDeploy.cs','GroundDocking.cs','GroundTether.cs','CollapsibleTube.cs','EndWindowLink.cs'):
 assert (R/'Source'/filename).read_bytes()==(OLD/'Source'/filename).read_bytes()
for path in (OLD/'GameData/RoosterWorksGroundModules/Compatibility').glob('*.cfg'):
 assert (GD/'Compatibility'/path.name).read_bytes()==path.read_bytes(),'Existing compatibility changed'
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,('Read-only baseline changed',path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==18
print(f'PASS dev.18: 13 models, {ports} preserved docking ports, {jets} directional RCS jets, {spots} real door spotlights; original geometry/colliders/gameplay preserved; stock engine and fuel/axis checks; {new_vertices} new equipment vertices; all read-only inputs unchanged')
