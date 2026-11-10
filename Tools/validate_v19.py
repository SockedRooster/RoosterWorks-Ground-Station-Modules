from pathlib import Path
import sys,json,copy,hashlib,math
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;OLD=W/'ground-hotpatch-v18';GD=R/'GameData/RoosterWorksGroundModules';CORE=W/'rw-v075dev5';sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import rotation,world_nodes
M=np.diag([-1.,1.,-1.]);ports=0;fixtures=0
def world(model):
 def rec(n,parent):
  matrix=np.eye(4);matrix[:3,:3]=rotation(n['rotation'])@np.diag(n['scale']);matrix[:3,3]=n['position'];matrix=parent@matrix;yield n,matrix
  for c in n['children']:yield from rec(c,matrix)
 return list(rec(model.root,np.eye(4)))
def strip(n):
 n['children']=[c for c in n['children'] if not c['name'].startswith('RW_RCSCluster_')]
 for c in n['children']:strip(c)
assert len(list((GD/'Models').glob('*.mu')))==len(list((GD/'Parts').glob('*.cfg')))==13
for path in sorted((GD/'Parts').glob('*.cfg')):
 ID=path.stem;p=parse(path.read_text(encoding='utf-8')).children[0];oldp=parse((OLD/'GameData/RoosterWorksGroundModules/Parts'/path.name).read_text(encoding='utf-8')).children[0];model=load(GD/f'Models/{ID}.mu');old=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu');strip(old.root)
 nodes={n['name']:n for _,n in walk(model.root)}
 assert not any(n['name'].startswith(('RW_RCSCluster_','RW_GroundRCS','RW_RCS_')) for _,n in walk(model.root))
 assert not any(n.get('name')=='ModuleRCSFX' for n in p.children)
 assert all('rcs' not in n.header.lower() for e in p.children if e.header=='EFFECTS' for n in e.children)
 assert not any(n.header=='RESOURCE' and n.get('name')=='MonoPropellant' for n in p.children)
 for _,n in walk(model.root):
  if 'mesh' in n:
   m=n['mesh'];v=np.array(m['vertices']);normal=np.array(m['normals']);tri=np.array(m['submeshes'][0]);assert 0<len(v)<65535 and np.isfinite(v).all() and np.allclose(np.linalg.norm(normal,axis=1),1,atol=2e-5)
   assert np.all(np.sum(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])*normal[tri].mean(1),axis=1)>=-1e-6)
 if ID!='RW_GND_END_250_125':
  for _,n in walk(old.root):
   if ID=='RW_GND_HAB' and 'mesh' in n and not n['name'].startswith('RW_EndFaceBadges') and any(old.textures[old.materials[i]['properties']['_MainTex']['index']]['name']=='rwm_crest' for i in n.get('materials',[])):n['mesh']['uvs']=[(1-u,1-v) for u,v in n['mesh']['uvs']]
   if n['name']=='RW_DoorSpot':n['light'].update(intensity=4,range=10,spotAngle=100)
  # Native serialization rounds transformed UVs; compare tolerance for those.
  if ID=='RW_GND_HAB':
   for _,n in walk(old.root):
    if 'mesh' in n:
     assert np.allclose(n['mesh']['uvs'],nodes[n['name']]['mesh']['uvs'],atol=1e-6);n['mesh']['uvs']=nodes[n['name']]['mesh']['uvs']
  assert model.root==old.root,(ID,'unrequested visual/collider/rig change')
 else:
  # All endcap geometry/colliders turn as a unit; no UVs or triangles are changed.
  oldworld={n['name']:(n,m) for n,m in world(old)}
  for n,m in world(model):
   on,om=oldworld[n['name']]
   if 'mesh' in n:
    v=np.array(n['mesh']['vertices'])@m[:3,:3].T+m[:3,3];ov=np.array(on['mesh']['vertices'])@om[:3,:3].T+om[:3,3];assert np.allclose(v,ov@M.T,atol=1e-6)
    assert n['mesh']['uvs']==on['mesh']['uvs'] and n['mesh']['submeshes']==on['mesh']['submeshes']
   if 'collider' in n:
    assert n['collider']['type']==on['collider']['type']
    if n['collider']['type']=='box':
     c=m[:3,:3]@n['collider']['center']+m[:3,3];oc=om[:3,:3]@on['collider']['center']+om[:3,3];assert np.allclose(c,M@oc,atol=1e-6) and n['collider']['size']==on['collider']['size']
    else:
     v=np.array(n['collider']['mesh']['vertices'])@m[:3,:3].T+m[:3,3];ov=np.array(on['collider']['mesh']['vertices'])@om[:3,:3].T+om[:3,3];assert np.allclose(v,ov@M.T,atol=1e-6)
  for k,v in p.values:
   if k.startswith('node_stack_'):
    a=np.array([float(x) for x in v.split(',')]);b=np.array([float(x) for x in oldp.get(k).split(',')]);assert np.allclose(a[:3],M@b[:3]) and np.allclose(a[3:6],M@b[3:6]) and a[6]==b[6]
 for port in [n for n in p.children if n.get('name')=='ModuleDockingNode']:
  ports+=1;assert port.get('acquireForce')=='40' and port.get('nodeType') in ('size1','size2')
  n,m=next((n,m) for n,m in world(model) if n['name']==port.get('nodeTransformName'));values=np.array([float(x) for x in p.get('node_stack_'+port.get('referenceAttachNode')).split(',')]);assert np.allclose(m[:3,3],values[:3],atol=1e-6) and np.allclose(m[:3,:3]@np.array((0,0,1)),values[3:6],atol=1e-6)
 if ID!='RW_GND_VT':
  assert math.isclose(float(p.get('mass')),float(oldp.get('mass'))-.04,abs_tol=1e-6)
  assert [dump(n) for n in p.children if n.header=='RESOURCE']==[dump(n) for n in oldp.children if n.header=='RESOURCE']
 else:
  res={n.get('name'):float(n.get('maxAmount')) for n in p.children if n.header=='RESOURCE'};assert res=={'LiquidFuel':180,'Oxidizer':220}
  engine=next(n for n in p.children if n.get('name')=='ModuleEnginesFX');assert engine.get('maxThrust')=='90' and float(p.get('mass'))==.6 and .6+(180+220)*.005==2.6
  assert p.get('attachRules')=='0,1,0,1,0' and p.get('node_stack_mount') is None
  names=[n.get('name') for n in p.children];assert names.count('ModuleDecouple')==names.count('ModuleRWPodRelease')==1 and 'ModuleAnchoredDecoupler' not in names and 'ModuleDockingNode' not in names
  dec=next(n for n in p.children if n.get('name')=='ModuleDecouple');assert dec.get('explosiveNodeID')=='srf' and dec.get('stagingEnabled')=='false' and dec.get('explosiveDir')=='0, 0, 1'
 if ID in ('RW_GND_HAB','RW_GND_CMD','RW_GND_AIR'):
  fixtures+=1;spot=nodes['RW_DoorSpot'];forward=rotation(spot['rotation'])@np.array((0,0,1));origin=np.array(spot['position']);assert forward[1]<-.8 and forward[2]>.49
  assert spot['light']['range']==10 and spot['light']['spotAngle']==100
  stage={id(n) for _,n in walk(nodes['RW_GroundStairs'])};covered=0
  for n,m in world_nodes(model,1):
   if id(n) in stage and 'collider' in n and n['collider']['type']=='box' and not n['collider']['trigger'] and n['collider']['size'][0]>1:
    c=m[:3,:3]@n['collider']['center']+m[:3,3];delta=c-origin;assert np.dot(delta/np.linalg.norm(delta),forward)>math.cos(math.radians(50)) and np.linalg.norm(delta)<10;covered+=1
  assert covered==8
  light=next(n for n in p.children if n.get('name')=='ModuleRWExteriorLight');assert light.get('followCabinLights')=='true' and light.get('resourceAmount')=='.03'
 print('PASS',ID,'RCS removed; requested changes and interface/geometry checks',flush=True)
assert ports==25 and fixtures==3
for filename in ('GroundDeploy.cs','GroundDocking.cs','GroundTether.cs','EndWindowLink.cs'):assert (R/'Source'/filename).read_bytes()==(OLD/'Source'/filename).read_bytes()
for path in (OLD/'GameData/RoosterWorksGroundModules/Compatibility').glob('*.cfg'):assert (GD/'Compatibility'/path.name).read_bytes()==path.read_bytes()
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==19
print('PASS dev.19: 13 parts; zero RCS; real door-spot coverage; HAB body UV180; endcap Y180 including port/node/collision; VT90 / 180LF / 220Ox / no mono / whole-part release; 25 retained dock ports; baseline and manifest protected')
