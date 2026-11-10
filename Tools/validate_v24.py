from pathlib import Path
import sys,json,hashlib,math
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;sys.path[:0]=[str(W/'rw-v075dev5/Source'),str(W/'rw-v075dev5/Tools'),str(R/'Tools')]
from native_model import load,walk
from config_nodes import parse
from industry_geometry import matrices
GD=R/'GameData/RoosterWorksGroundModules';BG=W/'ground-hotpatch-v23/GameData/RoosterWorksGroundModules';ID='RW_GND_HPT';checks=0
def check(v,message):
 global checks
 checks+=1
 assert v,message
for old in BG.rglob('*'):
 if not old.is_file():continue
 rel=old.relative_to(BG);check((GD/rel).exists(),'Removed old file '+str(rel))
 if rel.as_posix()!='RoosterWorksGroundModules.version':check((GD/rel).read_bytes()==old.read_bytes(),'Changed old file '+str(rel))
added={p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file() and not (BG/p.relative_to(GD)).exists()}
check(added=={f'Models/{ID}.mu',f'Parts/{ID}.cfg','Models/rwm_hptlabel.png','Compatibility/CompactHardpoint.cfg'},'Unexpected new files '+str(added))
check(len(list((GD/'Models').glob('*.mu')))==17 and len(list((GD/'Parts').glob('*.cfg')))==17,'Part/model count')
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==24,'Version')
p=parse((GD/f'Parts/{ID}.cfg').read_text()).children[0];modules=[n for n in p.children if n.header=='MODULE'];byname={n.get('name'):n for n in modules}
check(p.get('CrewCapacity')=='0' and p.get('mass')=='1.0','Crew/mass')
check(p.get('attachRules')=='1,0,1,1,0','Hull surface attachment')
check(p.get('fuelCrossFeed')=='true' and p.get('breakingForce')==p.get('breakingTorque')=='2000','Crossfeed/structural thresholds')
check(set(byname)=={'ModuleRWStationFinish','ModuleRWRingColor','ModuleRWEditorMenu','ModuleRWGroundDocking','ModuleDockingNode','ModuleColorChanger'},'Unexpected gameplay/leg/RCS module')
check(not any(n.header in ('RESOURCE','INTERNAL') for n in p.children),'Unexpected tank/IVA')
check(byname['ModuleRWRingColor'].get('ringModel')==ID,'Ring model ID')
ports=[n for n in modules if n.get('name')=='ModuleDockingNode'];check(len(ports)==2,'Exactly two inline docking ports')
for m in ports:
 check(m.get('referenceAttachNode') in ('top','bottom') and m.get('nodeType')=='size2','Side mounting surfaces became docking ports')
 check(m.get('crossfeed')=='true' and m.get('stagingEnabled')==m.get('stagingToggleEnabledEditor')==m.get('stagingToggleEnabledFlight')=='false','Dock crossfeed/staging')
model=load(GD/f'Models/{ID}.mu');nodes=dict(walk(model.root));named={n['name']:n for _,n in walk(model.root)};world=matrices(model.root)
expected={'top':(.6,0,0,1,0,0,2),'bottom':(-.6,0,0,-1,0,0,2),'port':(0,0,1.25,0,0,1,1),'starboard':(0,0,-1.25,0,0,-1,1)}
for name,values in expected.items():check(np.allclose([float(v) for v in p.get('node_stack_'+name).split(',')],values),'Node geometry '+name)
for port in ports:
 n=named[port.get('nodeTransformName')];mt=world[id(n)];target=expected[port.get('referenceAttachNode')];check(np.allclose(mt[:3,3],target[:3]) and np.allclose(mt[:3,2],target[3:6],atol=1e-6),'Dock transform alignment')
for sign,side in ((1,'Port'),(-1,'Starboard')):
 c=named['RW_HPT_'+side+'_FaceCollision']['collider'];check(np.allclose(c['center'],(0,0,sign*1.245)) and np.allclose(c['size'],(.70,.88,.01)),'Planar receiving collider')
 face=c['center'][2]+sign*c['size'][2]/2;check(abs(face-sign*1.25)<1e-6,'Flat node/collider face mismatch')
 n=named['RW_HPT_'+side+'_rwm_white'];mesh=n['mesh'];v=np.array(mesh['vertices']);norm=np.array(mesh['normals']);face_vertices=v[(norm[:,2]*sign)>.999]
 check(np.allclose(face_vertices[:,2],sign*1.25,atol=1e-6),'Visual face is not flat/flushed')
 # Rays used by the editor must hit this receiving face before any hull box.
 hits=[]
 for _,candidate in walk(model.root):
  collider=candidate.get('collider',{})
  if collider.get('type')!='box' or collider['trigger']:continue
  center=np.array(collider['center']);size=np.array(collider['size'])
  if abs(center[0])<=size[0]/2 and abs(center[1])<=size[1]/2:
   surface=center[2]+sign*size[2]/2;distance=3-sign*surface
   if distance>=0:hits.append((distance,candidate['name']))
 check(min(hits)[1]=='RW_HPT_'+side+'_FaceCollision','VAB ray misses flat receiving face')
 # Side bevel normals must face out, also on the mirrored saddle.
 n=named['RW_HPT_'+side+'_rwm_steel'];v=np.array(n['mesh']['vertices']);norm=np.array(n['mesh']['normals']);check(np.all((v[:,:2]*norm[:,:2]).sum(1)>=-1e-6),'Mirrored bevel normals face inward')
 # Our existing external equipment anchor is exactly at its rear mount plane.
 drill=parse((GD/'Parts/RW_GND_DRILL.cfg').read_text()).children[0];vt=parse((GD/'Parts/RW_GND_VT.cfg').read_text()).children[0]
 check(drill.get('node_stack_mount')=='0, 0, 0, 0, 0, -1, 1' and vt.get('node_attach')=='0, 0, 0, 0, 0, -1, 1','Equipment mounting convention changed')

all_vertices=[];triangles=0;colliders=0
for path,n in walk(model.root):
 check(not any(token in n['name'] for token in ('GroundLeg','GroundStairs','RCS')),'Unexpected moving/propulsion hardware')
 if 'mesh' in n:
  m=n['mesh'];v=np.array(m['vertices']);normal=np.array(m['normals']);all_vertices.append(v)
  check(len(v)==len(normal)==len(m['uvs']) and len(v)<65535,'Mesh cardinality')
  check(np.isfinite(v).all() and np.isfinite(m['uvs']).all() and np.isfinite(normal).all(),'Non-finite vertex/UV/normal')
  check(np.allclose(np.linalg.norm(normal,axis=1),1,atol=.001),'Unit normals')
  for sub in m['submeshes']:
   tri=np.array(sub);triangles+=len(tri);check(tri.min()>=0 and tri.max()<len(v),'Triangle index')
   cross=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]);dot=(cross*normal[tri].mean(1)).sum(1);check(dot.min(initial=0)>-1e-7,'Native winding '+path)
 if 'collider' in n:
  colliders+=1;c=n['collider'];check(c['trigger']==0,'Physical collider is a trigger')
  if c['type']=='box':check(all(s>0 for s in c['size']),'Positive collider dimensions')
  else:check(c['convex']==1 and sum(map(len,c['mesh']['submeshes']))<=255,'Convex PhysX limit')
v=np.concatenate(all_vertices);check(np.all(v[:,2]<=1.25001) and np.all(v[:,2]>=-1.25001),'Flat saddles exceed 2.5 m width')
check(v[:,0].min()>=-.60001 and v[:,0].max()<=.60001,'Compact length exceeds 1.2 m')
report=json.loads((R/'Reports/DEV24_HARDPOINT.json').read_text());check(len(report['end_face_refinement']['ends'])==2,'Side equipment faces received fake endcaps')
black=np.array(named['RW_HPT_graphite']['mesh']['vertices']);cladding=np.concatenate([np.array(named['RW_HPT_'+k]['mesh']['vertices']) for k in ('cladding','cladding_white')])
check(np.any(np.isclose(abs(black[:,2]),1.030,atol=1e-6)) and np.any(np.isclose(abs(cladding[:,2]),1.035,atol=1e-6)),'Flattened body backing separation')
for t in model.textures:check((GD/'Models'/(t['name']+'.png')).exists(),'Texture '+t['name'])
rule,cleanup=parse((GD/'Compatibility/CompactHardpoint.cfg').read_text()).children;check(rule.get('model')==ID and len(rule.children)==3,'Independent ring maps')
for e in rule.children:
 check('/RW_HPT_Port_' not in e.get('path') and '/RW_HPT_Starboard_' not in e.get('path'),'Side plates accidentally ring-colored')
 m=nodes[e.get('path')]['mesh'];check(int(e.get('vertices'))==len(m['vertices']) and int(e.get('triangles'))==len(m['submeshes'][0]),'Ring map native counts')
 for item in e.get('ranges').split(','):
  start,count=map(int,item.split(':'));check(start>=0 and count>0 and start+count<=len(m['submeshes'][0]),'Triangle range grammar/bounds')
check(cleanup.header=='@PART[RW_GND_HPT]:NEEDS[Kerbalism]:FINAL','Scoped utility habitat cleanup')
changer=byname['ModuleColorChanger'];check(changer.get('includedRenderer')=='RW_EndWindows','End window light target')
check(next(n for n in changer.children if n.header=='alphaCurve').values==[('key','0 1'),('key','1 1')],'Emission alpha')
check('PASS 3728 actual-map color assertions' in (R/'Reports/hardpoint-color-tests.log').read_text(),'Actual runtime color regression')
for path,digest in json.loads((R/'Reports/DEV24_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected baseline '+path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
for f in (GD/'Compatibility').glob('*.cfg'):parse(f.read_text())
(R/'Reports/DEV24_BOUNDS.json').write_text(json.dumps({'minimum':v.min(0).tolist(),'maximum':v.max(0).tolist(),'triangles':triangles,'colliders':colliders,'checks':checks},indent=2)+'\n')
print(f'PASS dev.24: {checks} native/configuration/preservation checks; compact 1.2 m collar; 2.5 m side envelope; opposed planar pads, outward bevel normals and receiving colliders; matching docking/structural nodes; no legs; separate body backing; accepted ground/station assets and plugins unchanged')
