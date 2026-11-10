"""Validate the requested art, docking and preservation changes precisely."""
from pathlib import Path
import sys,json,copy,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v14';GD=R/'GameData/RoosterWorksGroundModules';OGD=OLD/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from config_nodes import parse,dump
from poses import rotation
changed=set()
for path in OGD.rglob('*'):
 if path.is_file() and path.read_bytes()!=(GD/path.relative_to(OGD)).read_bytes():changed.add(path.relative_to(OGD).as_posix())
allowed={f'Parts/{p.name}' for p in (GD/'Parts').glob('*.cfg')}|{'RoosterWorksGroundModules.version','Plugins/RoosterWorksGroundDeploy.dll','Models/RW_GND_END_250_125.mu','Models/RW_GND_PWR.mu','Models/RW_GND_ELB.mu','Compatibility/EndcapRingGeometry.cfg'}
assert changed<=allowed,changed-allowed
newfiles={p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file()}-{p.relative_to(OGD).as_posix() for p in OGD.rglob('*') if p.is_file()}
assert newfiles=={'Compatibility/SkycraneEndcapCarrier.cfg'},newfiles
for source in ('GroundDeploy.cs','GroundTether.cs'):assert (R/'Source'/source).read_bytes()==(OLD/'Source'/source).read_bytes()
policy={'acquireRange':'2.5','acquireForce':'20','acquireTorque':'12','acquireForceTweak':'100','acquireMinFwdDot':'.98','captureRange':'.08','captureMinFwdDot':'.998','captureMaxRvel':'.3','minDistanceToReEngage':'3'}
ports=0
for path in (GD/'Parts').glob('*.cfg'):
 root=parse(path.read_text(encoding='utf-8'));p=root.children[0];old=parse((OGD/'Parts'/path.name).read_text(encoding='utf-8')).children[0]
 for port in [n for n in p.children if n.get('name')=='ModuleDockingNode']:
  ports+=1
  for key,value in policy.items():assert port.get(key)==value,(path.name,key)
  port.values=[(k,v) for k,v in port.values if k not in policy]
 for port in [n for n in old.children if n.get('name')=='ModuleDockingNode']:
  port.values=[(k,v) for k,v in port.values if k not in policy]
 if path.stem=='RW_GND_END_250_125':
  old.children=[n for n in old.children if not (n.get('name')=='ModuleDockingNode' and n.get('referenceAttachNode')=='bottom')]
  p.set('description',old.get('description'))
 assert dump(p)==dump(old),('Gameplay changes beyond requested port settings',path.name)
assert ports==23
for role in ('PWR','ELB'):
 ID='RW_GND_'+role;a=load(GD/f'Models/{ID}.mu');b=load(OGD/f'Models/{ID}.mu');oldnodes=dict(walk(b.root));restored=copy.deepcopy(a);edited=0
 assert a.materials==b.materials and a.textures==b.textures
 for path,n in walk(restored.root):
  if 'mesh' not in n:continue
  baseline=oldnodes[path]['mesh'];mesh=n['mesh']
  if mesh!=baseline:
   edited+=1
   if role=='ELB':
    assert mesh['vertices']==baseline['vertices'] and mesh['normals']==baseline['normals'] and mesh['submeshes']==baseline['submeshes']
    assert np.allclose(np.array(mesh['uvs']),np.array([(v,1-u) for u,v in baseline['uvs']]),atol=1e-6)
    mesh['uvs']=baseline['uvs']
   else:
    assert mesh['uvs']==baseline['uvs'] and mesh['submeshes']==baseline['submeshes']
    va=np.array(mesh['vertices']);vb=np.array(baseline['vertices']);moved=np.any(abs(va-vb)>1e-6,axis=1)
    assert moved.any() and va[moved,1].max()<-.4
    assert np.allclose(np.linalg.norm(va[moved,1:],axis=1),np.linalg.norm(vb[moved,1:],axis=1),atol=1e-6)
    mesh['vertices']=baseline['vertices'];mesh['normals']=baseline['normals']
 assert edited==(1 if role=='ELB' else 3) and restored.root==b.root,(role,edited)
 print('PASS',role,'only requested badge geometry/UVs changed; full rig, collision and roof mounts preserved',flush=True)
ID='RW_GND_END_250_125';m=load(GD/f'Models/{ID}.mu');old=load(OGD/f'Models/{ID}.mu')
assert {p:n['collider'] for p,n in walk(m.root) if 'collider' in n}=={p:n['collider'] for p,n in walk(old.root) if 'collider' in n}
frames=[n for _,n in walk(m.root) if n['name'].startswith('RW_Dock_')];assert len(frames)==1 and frames[0]['name']=='RW_Dock_top'
p=parse((GD/f'Parts/{ID}.cfg').read_text(encoding='utf-8')).children[0];port=[n for n in p.children if n.get('name')=='ModuleDockingNode'];assert len(port)==1 and port[0].get('nodeType')=='size1'
assert p.get('node_stack_bottom')==parse((OGD/f'Parts/{ID}.cfg').read_text()).children[0].get('node_stack_bottom')
for _,n in walk(m.root):
 if 'mesh' not in n:continue
 mesh=n['mesh'];v=np.array(mesh['vertices']);normal=np.array(mesh['normals']);t=np.array(mesh['submeshes'][0]);assert len(v)<65535 and np.isfinite(v).all() and np.isfinite(normal).all()
 assert np.allclose(np.linalg.norm(normal,axis=1),1,atol=2e-5)
 assert v[:,0].min()>=-.45001 and v[:,0].max()<=.45001,(n['name'],v[:,0].max())
 dots=np.sum(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])*normal[t].mean(1),axis=1);assert np.all(dots>=-1e-6),(n['name'],dots.min())
 texture=m.textures[m.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
 if texture=='rwm_hubblanket':assert v[:,0].max()<0,'No compressed blanket geometry on small face'
 if texture=='rwm_ceramic':
  nose=v[:,0]>.40;uv=np.array(mesh['uvs'])[nose];vv=v[nose]
  assert np.allclose(uv,np.column_stack((.5+vv[:,2]/1.225,.5+vv[:,1]/1.225)),atol=1e-6),'Planar nose UV continuity'
 if texture=='rwm_crest':
  nose=v[:,0]>.4;uv=np.array(mesh['uvs'])[nose];vv=v[nose]
  assert np.allclose(uv[:,0],(vv[:,2]+.085)/.17,atol=1e-6)
  assert np.allclose(uv[:,1],(vv[:,1]-.19)/.17,atol=1e-6),'Nose rooster upright and outward-readable'
for texture in m.textures:Image.open(GD/'Models'/(texture['name']+'.png')).verify()
maps=parse((GD/'Compatibility/EndcapRingGeometry.cfg').read_text()).children[0];lookup=dict(walk(m.root))
for spec in maps.children:assert len(lookup[spec.get('path')]['mesh']['vertices'])==int(spec.get('vertices'))
assert 'PASS 4904 docking/menu assertions' in (R/'Reports/docking-tests.log').read_text()
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==15
roadmap=(R/'ROADMAP.md').read_text().lower();assert all(s in roadmap for s in ('top and bottom rcs','exterior module lighting','dedicated thruster modules'))
print('PASS single size1 endcap port, retained rear stack node, planar nose UVs, 23 strongly aligned ports, 4904 menu checks, exact scope, source preservation, roadmap and checksums')
