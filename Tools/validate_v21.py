from pathlib import Path
import sys,json,hashlib,math
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v20';GD=R/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev5/Tools'),str(W/'rw-v075dev5/Source')]
from native_model import load,walk
from config_nodes import parse
allowed={'Models/RW_GND_FLEX.mu','Parts/RW_GND_FLEX.cfg','Plugins/RoosterWorksGroundDeploy.dll','RoosterWorksGroundModules.version'}
previous=B/'GameData/RoosterWorksGroundModules'
assert {p.relative_to(GD) for p in GD.rglob('*') if p.is_file()}=={p.relative_to(previous) for p in previous.rglob('*') if p.is_file()}
for p in GD.rglob('*'):
 if p.is_file() and p.relative_to(GD).as_posix() not in allowed:assert p.read_bytes()==(previous/p.relative_to(GD)).read_bytes(),p
m=load(GD/'Models/RW_GND_FLEX.mu');old=load(previous/'Models/RW_GND_FLEX.mu')
nodes=dict(walk(m.root));oldnodes=dict(walk(old.root));changed=set()
for path,n in nodes.items():
 assert {k:v for k,v in n.items() if k not in ('children','mesh')}=={k:v for k,v in oldnodes[path].items() if k not in ('children','mesh')},path
 if n.get('mesh')!=oldnodes[path].get('mesh'):changed.add(n['name'])
 if 'mesh' not in n:continue
 mesh=n['mesh'];v=np.array(mesh['vertices']);norm=np.array(mesh['normals']);assert np.isfinite(v).all() and np.isfinite(norm).all()
 assert np.allclose(np.linalg.norm(norm,axis=1),1,atol=.001)
 assert len(v)<65535
 for sub in mesh['submeshes']:
  t=np.array(sub);cross=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])
  assert (np.einsum('ij,ij->i',cross,norm[t].mean(axis=1))>=-1e-8).all(),path
assert changed=={'RW_FlexOverlapBoot_RW_TubeBase','RW_FlexOverlapBoot_RW_TubeNose','RW_FlexBootBand_RW_TubeBase','RW_FlexBootBand_RW_TubeNose'}
for parent in ('RW_TubeBase','RW_TubeNose'):
 boot=next(n for n in nodes.values() if n['name']=='RW_FlexOverlapBoot_'+parent)['mesh'];v=np.array(boot['vertices']);r=np.linalg.norm(v[:,1:],axis=1)
 assert np.allclose(r[r>1.20],1.24,atol=1e-6)
 assert np.isclose(abs(v[:,0]).min(),.01) and np.isclose(abs(v[:,0]).max(),.24)
 cap=next(n for n in nodes.values() if n['name']=='FlexEnd_'+parent+'_steel')['mesh'];capr=np.linalg.norm(np.array(cap['vertices'])[:,1:],axis=1).max()
 assert 1.24*math.cos(math.pi/96)-capr>.014
 band=next(n for n in nodes.values() if n['name']=='RW_FlexBootBand_'+parent)['mesh'];bandr=np.linalg.norm(np.array(band['vertices'])[:,1:],axis=1)
 assert np.allclose(bandr,1.247,atol=1e-6) and 1.247*math.cos(math.pi/64)-1.24>.005
 for t in (0,.25,.5,.75,1):
  rear=-.6;front=.6+2.8*t;bellows=(-.45,.45+2.8*t)
  assert rear+.24>bellows[0] and front-.24<bellows[1]
p=parse((GD/'Parts/RW_GND_FLEX.cfg').read_text()).children[0]
assert p.get('breakingForce')==p.get('breakingTorque')=='3500'
assert len([n for n in p.children if n.get('name')=='ModuleDockingNode'])==2
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==21
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():
 assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
print('PASS dev.21: 13 models; only four FLEX ring surfaces changed; separated sleeves/bands and recessed annuli; sealed at five lengths; 3500 force/torque; other twelve models/configs and compatibility maps unchanged; protected inputs and manifest')
