from pathlib import Path
import sys,json,copy,hashlib,math
from collections import Counter
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v16';GD=R/'GameData/RoosterWorksGroundModules';OGD=OLD/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import rotation
def world(model,t=0):
 def rec(n,parent):
  pos=n['position'];scale=n['scale']
  if model.name=='RW_GND_FLEX':
   if n['name']=='RW_TubeNose':pos=(.6+2.8*t,0,0)
   if n['name']=='RW_TubeBellows':scale=((.9+2.8*t)/.9,1,1)
  m=np.eye(4);m[:3,:3]=rotation(n['rotation'])@np.diag(scale);m[:3,3]=pos;m=parent@m
  yield n,m
  for c in n['children']:yield from rec(c,m)
 return list(rec(model.root,np.eye(4)))
def collisionmap(model):return {path:{k:v for k,v in n.items() if k!='children'} for path,n in walk(model.root) if 'collider' in n or n['name'].startswith(('RW_Dock_','RW_GroundLeg','RW_GroundStairs'))}
assert len(list((GD/'Models').glob('*.mu')))==12 and len(list((GD/'Parts').glob('*.cfg')))==12
ports=0;faces=0
for path in sorted((GD/'Parts').glob('*.cfg')):
 p=parse(path.read_text(encoding='utf-8')).children[0];ID=p.get('name');model=load(GD/f'Models/{ID}.mu');nodes=dict(walk(model.root));frames=world(model)
 for _,n in nodes.items():
  if 'mesh' in n:
   m=n['mesh'];v=np.array(m['vertices']);norm=np.array(m['normals']);tris=np.array(m['submeshes'][0]);assert 0<len(v)<65535 and np.isfinite(v).all() and np.isfinite(norm).all()
   assert np.allclose(np.linalg.norm(norm,axis=1),1,atol=2e-5)
   d=np.sum(np.cross(v[tris[:,1]]-v[tris[:,0]],v[tris[:,2]]-v[tris[:,0]])*norm[tris].mean(1),axis=1);assert np.all(d>=-1e-6),(ID,n['name'],d.min())
  if 'collider' in n and n['collider']['type']=='mesh':
   c=n['collider'];assert sum(len(s) for s in c['mesh']['submeshes'])<=255
   if ID=='RW_GND_FLEX':
    counts=Counter()
    for tri in c['mesh']['submeshes'][0]:
     pts=[tuple(round(x,5) for x in c['mesh']['vertices'][i]) for i in tri]
     for a,b in zip(pts,pts[1:]+pts[:1]):counts[tuple(sorted((a,b)))]+=1
    assert set(counts.values())=={2},'New FLEX hull must be closed'
 for port in [n for n in p.children if n.get('name')=='ModuleDockingNode']:
  ports+=1;assert port.get('acquireForce')=='40' and port.get('acquireRange')=='2.5' and port.get('acquireMinFwdDot')=='.258819'
  n,m=next((n,m) for n,m in frames if n['name']==port.get('nodeTransformName'));values=np.array([float(v) for v in p.get('node_stack_'+port.get('referenceAttachNode')).split(',')]);assert np.allclose(m[:3,3],values[:3],atol=1e-6)
  assert np.allclose(m[:3,:3]@np.array((0,0,1)),values[3:6],atol=1e-6)
 if ID!='RW_GND_FLEX':
  oldp=parse((OGD/'Parts'/path.name).read_text(encoding='utf-8')).children[0];oldm=load(OGD/f'Models/{ID}.mu');assert collisionmap(model)==collisionmap(oldm),(ID,'existing collision/rig changed')
  restored=copy.deepcopy(p)
  restored.children=[n for n in restored.children if n.get('name')!='ModuleRWEndWindowLink' and not (n.get('name')=='ModuleColorChanger' and (n.get('moduleID') or '').endswith('_EndLights'))]
  for n in restored.children:
   if n.get('name')=='ModuleColorChanger':n.values=[(k,v) for k,v in n.values if not (k=='includedRenderer' and v=='RW_EndWindows')]
   if n.get('name')=='ModuleDockingNode':n.set('acquireForce','20')
  assert dump(restored)==dump(oldp),(ID,'unrequested gameplay/config change')
  assert model.textures[:-2]==oldm.textures
  # Body crests alone rotate; the new planar end crests are independently mapped.
  if ID in ('RW_GND_HAB','RW_GND_AIR','RW_GND_CMD'):
   report=json.loads((R/f'Reports/{ID}.json').read_text());assert report['end_face_refinement']['body_badge_vertices_turned_90']>0
 # Validate every repaired badge's world-up position and outward-readable UV.
 ends=[(k,np.array([float(a) for a in v.split(',')])[:3],np.array([float(a) for a in v.split(',')])[3:6]) for k,v in p.values if k.startswith('node_stack_')]
 badges=[];windows=[]
 for n,m in frames:
  if n['name'].startswith(('RW_EndFaceBadges','RW_EndWindows')) and 'mesh' in n:
   mesh=n['mesh'];vertices=np.array(mesh['vertices'])@m[:3,:3].T+m[:3,3]
   (badges if n['name'].startswith('RW_EndFaceBadges') else windows).append((vertices,np.array(mesh['uvs'])))
 for key,center,outward in ends:
  right=-np.cross((0,1,0),outward);up=np.array((0,1,0));expected=center-outward*.023+up*.27
  candidates=[]
  for v,uv in badges:
   on=np.linalg.norm(v-expected,axis=1)<.13
   if on.any():candidates.append((v[on],uv[on]))
  assert len(candidates)==1,(ID,key,'end badge missing')
  v,uv=candidates[0];q=v-expected;assert len(v)==4 and np.allclose(uv[:,0],.5+(q@right)/.17,atol=1e-5) and np.allclose(uv[:,1],.5+(q@up)/.17,atol=1e-5),(ID,key,'badge orientation')
  assert sum(np.count_nonzero(np.linalg.norm(v-(center-outward*.022),axis=1)<.106) for v,uv in windows)>0
  faces+=1
 print('PASS',ID,'upright end badges, luminous windows, stock frames and preserved interfaces',flush=True)
assert faces==26 and ports==25
model=load(GD/'Models/RW_GND_FLEX.mu');part=parse((GD/'Parts/RW_GND_FLEX.cfg').read_text()).children[0]
assert part.get('CrewCapacity')=='0' and not any(n.get('name')=='ModuleRWGroundDeploy' for n in part.children)
assert not any(n['name'].startswith(('RW_GroundLeg','RW_GroundStairs')) for _,n in walk(model.root))
for t in (0,.25,.5,.75,1):
 nodes={n['name']:(n,m) for n,m in world(model,t)};base=nodes['RW_Dock_bottom'][1][:3,3];nose=nodes['RW_Dock_top'][1][:3,3]
 assert np.allclose(base,(-.6,0,0)) and np.allclose(nose,(.6+2.8*t,0,0));assert abs(np.linalg.norm(nose-base)-(1.2+2.8*t))<1e-6
 n,m=nodes['FlexPressureCollision'];v=np.array(n['collider']['mesh']['vertices'])@m[:3,:3].T+m[:3,3]
 assert abs(v[:,0].min()+.45)<1e-6 and abs(v[:,0].max()-(.45+2.8*t))<1e-6,'No pressure-hull gap through extension'
maps=parse((GD/'Compatibility/FlexRingGeometry.cfg').read_text()).children[0];assert maps.children
for spec in maps.children:assert len(dict(walk(model.root))[spec.get('path')]['mesh']['vertices'])==int(spec.get('vertices'))
for source in ('GroundDeploy.cs','GroundTether.cs'):assert (R/'Source'/source).read_bytes()==(OLD/'Source'/source).read_bytes()
assert (R/'Source/GroundDocking.cs').read_text()==(OLD/'Source/GroundDocking.cs').read_text().replace('port.acquireForce = 20f','port.acquireForce = 40f')
for path in OGD.rglob('*.png'):assert path.read_bytes()==(GD/path.relative_to(OGD)).read_bytes(),path
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert 'PASS 4959 docking/menu assertions' in (R/'Reports/docking-tests.log').read_text();assert 'PASS 161 collapsible-tube/light assertions' in (R/'Reports/flex-tests.log').read_text()
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==17
print('PASS 26 upright badges/windows, 25 stronger ports, 12 models, five FLEX poses and pressure hull continuity; 5120 controller assertions; existing inputs/resources/rigs and manifest retained')
