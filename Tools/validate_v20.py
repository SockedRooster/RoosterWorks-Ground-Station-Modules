from pathlib import Path
import sys,math,json,hashlib,copy
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;OLD=W/'ground-hotpatch-v19';GD=R/'GameData/RoosterWorksGroundModules';CORE=W/'rw-v075dev5';sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import world_nodes,rotation
def frames(model,t=0):
 def rec(n,parent):
  pos=n['position'];scale=n['scale']
  if n['name']=='RW_TubeNose':pos=(.6+2.8*t,0,0)
  if n['name']=='RW_TubeBellows':scale=((.9+2.8*t)/.9,1,1)
  m=np.eye(4);m[:3,:3]=rotation(n['rotation'])@np.diag(scale);m[:3,3]=pos;m=parent@m;yield n,m
  for c in n['children']:yield from rec(c,m)
 return list(rec(model.root,np.eye(4)))
affected={'HAB','AIR','LAB','CMD','FLEX'};ports=0;lights=0
for path in sorted((GD/'Parts').glob('*.cfg')):
 ID=path.stem;role=ID.removeprefix('RW_GND_');model=load(GD/f'Models/{ID}.mu');p=parse(path.read_text(encoding='utf-8')).children[0];nodes={n['name']:n for _,n in walk(model.root)}
 assert not any(n.get('name')=='ModuleRCSFX' for n in p.children)
 assert not any(n['name'].startswith(('RW_RCSCluster_','RW_GroundRCS')) for _,n in walk(model.root))
 for _,n in walk(model.root):
  if 'mesh' in n:
   m=n['mesh'];v=np.array(m['vertices']);normal=np.array(m['normals']);tri=np.array(m['submeshes'][0]);assert 0<len(v)<65535 and len(v)==len(normal)==len(m['uvs']) and np.isfinite(v).all()
   assert np.allclose(np.linalg.norm(normal,axis=1),1,atol=2e-5),(ID,n['name'],'normal length')
   assert np.all(np.sum(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])*normal[tri].mean(1),axis=1)>=-1e-6),(ID,n['name'],'winding')
  if 'collider' in n and n['collider']['type']=='mesh':assert len(n['collider']['mesh']['submeshes'][0])<=255
 if role not in affected:
  assert (GD/f'Models/{ID}.mu').read_bytes()==(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu').read_bytes()
  assert path.read_bytes()==(OLD/'GameData/RoosterWorksGroundModules/Parts'/path.name).read_bytes()
 for port in [n for n in p.children if n.get('name')=='ModuleDockingNode']:
  ports+=1;assert port.get('acquireForce')=='40'
  frame=next(m for n,m in frames(model) if n['name']==port.get('nodeTransformName'));a=np.array([float(x) for x in p.get('node_stack_'+port.get('referenceAttachNode')).split(',')]);assert np.allclose(frame[:3,3],a[:3],atol=1e-6) and np.allclose(frame[:3,:3]@np.array((0,0,1)),a[3:6],atol=1e-6)
 if role in ('HAB','CMD','AIR','LAB'):
  lights+=1;assert 'RW_DoorLightNeck' in nodes and 'RW_DoorLightLens' in nodes
  light=next(n for n in p.children if n.get('name')=='ModuleRWExteriorLight');assert light.get('followCabinLights')=='true' and light.get('resourceAmount')=='.03'
  cabin=next(n for n in p.children if n.get('name')=='ModuleColorChanger' and 'CabinLights' in (n.get('moduleID') or ''));assert cabin
  spot=nodes['RW_DoorSpot'];f=rotation(spot['rotation'])@np.array((0,0,1));origin=np.array(spot['position']);stairset={id(n) for _,n in walk(nodes['RW_GroundStairs'])};treads=0
  for n,m in world_nodes(model,1):
   if id(n) not in stairset or 'collider' not in n:continue
   c=n['collider']
   if c['type']!='box' or c['trigger'] or c['size'][0]<1:continue
   pos=m[:3,:3]@c['center']+m[:3,3];delta=pos-origin;assert np.dot(delta/np.linalg.norm(delta),f)>math.cos(math.radians(50)) and np.linalg.norm(delta)<10;treads+=1
  assert treads==8,(ID,treads)
  neck=np.array(nodes['RW_DoorLightNeck']['mesh']['vertices']);bracket=np.array(nodes['RW_DoorLightBracket']['mesh']['vertices']);housing=np.array(nodes['RW_DoorLightHousing']['mesh']['vertices'])
  for other in (bracket,housing):assert np.all(np.minimum(neck.max(0),other.max(0))-np.maximum(neck.min(0),other.min(0))>0),'Light fixture has an air gap'
 if role=='FLEX':
  assert p.get('CrewCapacity')=='0' and not any(n.get('name')=='ModuleRWGroundDeploy' for n in p.children)
  for t in (0,.25,.5,.75,1):
   ff={n['name']:(n,m) for n,m in frames(model,t)};collar=[]
   for cap in ('RW_TubeBase','RW_TubeNose'):
    n,m=ff['RW_FlexOverlapBoot_'+cap];v=np.array(n['mesh']['vertices'])@m[:3,:3].T+m[:3,3];rad=np.linalg.norm(v[:,1:3],axis=1);assert abs(rad.min()-1.1)<1e-5 and abs(rad.max()-1.225)<1e-5;collar.append((v[:,0].min(),v[:,0].max()))
   n,m=ff['RW_FlexPressureBellows'];v=np.array(n['mesh']['vertices'])@m[:3,:3].T+m[:3,3];lo,hi=v[:,0].min(),v[:,0].max()
   assert collar[0][0]<lo<collar[0][1] and collar[1][0]<hi<collar[1][1]
   assert abs(collar[0][1]-lo-.09)<1e-5 and abs(hi-collar[1][0]-.09)<1e-5
   assert abs(ff['RW_Dock_top'][1][0,3]-ff['RW_Dock_bottom'][1][0,3]-(1.2+2.8*t))<1e-6
 if role=='CMD':
  assert p.get('CrewCapacity')=='3' and next(n for n in p.children if n.header=='INTERNAL').get('name')=='Mk1-3'
  x1=float(p.get('node_stack_top').split(',')[0]);x0=float(p.get('node_stack_bottom').split(',')[0]);assert abs(x1-x0-2.15)<1e-6
  r=json.loads((R/'Reports/RW_GND_CMD.json').read_text());removed=r['dev20_changes']['roof_removed'];assert len([name for name in removed if name.startswith(('Roof heat exchanger','Radiator fin'))])==20
  assert removed.get('High gain parabolic reflector',0)>0 and len([name for name in nodes if name.startswith('RW_ContinuousDish_')])==4
  oldp=parse((OLD/'GameData/RoosterWorksGroundModules/Parts'/path.name).read_text(encoding='utf-8')).children[0];assert [dump(n) for n in p.children if n.header=='RESOURCE']==[dump(n) for n in oldp.children if n.header=='RESOURCE']
  # Native movement roots use the same new values as their config and report.
  for mod in [n for n in p.children if n.get('name')=='ModuleRWGroundDeploy']:
   for spec in mod.children:
    a=np.array([float(v) for v in spec.get('deployPosition').split(',')]);b=next(b for b in r['motion'] if b['name']==spec.get('name'));assert np.allclose(a,b['position']) and np.allclose(a,nodes[spec.get('name')]['position'])
  iva=parse(Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/Squad/Spaces/Mk1-3/internal.cfg').read_text()).children[0];assert len([n for n in iva.children if n.get('name')=='InternalSeat'])==3
 print('PASS',ID,'native, roles, lights/interfaces/seals checks',flush=True)
assert ports==25 and lights==4
rules=parse((GD/'Compatibility/CommandKerbalism.cfg').read_text()).children
hab=next(n for rule in rules for n in rule.children if n.header.startswith('%MODULE[Habitat]'));assert hab.get('%volume')=='7.25' and hab.get('%surface')=='25'
for path in (OLD/'GameData/RoosterWorksGroundModules/Compatibility').glob('*.cfg'):
 if path.name not in ('CommandKerbalism.cfg','ZZZCommandStorage075.cfg','GroundRingGeometry.cfg'):assert path.read_bytes()==(GD/'Compatibility'/path.name).read_bytes()
oldmaps=parse((OLD/'GameData/RoosterWorksGroundModules/Compatibility/GroundRingGeometry.cfg').read_text()).children
newmaps=parse((GD/'Compatibility/GroundRingGeometry.cfg').read_text()).children
for a,b in zip(oldmaps,newmaps):
 if a.get('model')!='RW_GND_CMD':assert dump(a)==dump(b)
for name in ('GroundDeploy.cs','GroundDocking.cs','GroundTether.cs','ExteriorLight.cs','EndWindowLink.cs','PodRelease.cs'):assert (R/'Source'/name).read_bytes()==(OLD/'Source'/name).read_bytes()
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==20
print('PASS dev.20: 13 models / 25 docking ports / 4 stair lights / sealed overlap at both FLEX ends across five lengths / 2.15 m three-seat CMD / twenty roof pieces removed / solid dish + mast support / unchanged unrelated source and models')
