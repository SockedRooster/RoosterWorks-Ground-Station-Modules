"""Actual native/configuration checks for the industry extension."""
from pathlib import Path
import sys,copy,json,hashlib,math
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v22';GD=R/'GameData/RoosterWorksGroundModules';BG=B/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev5/Tools'),str(W/'rw-v075dev5/Source'),str(R/'Tools')]
from native_model import load,walk
from config_nodes import parse
from stock_drill_reader import load_stock
from industry_geometry import stock_pose,points,matrices
checks=0
def check(value,message):
 global checks
 checks+=1
 assert value,message
def part(role,base=GD):return parse((base/f'Parts/RW_GND_{role}.cfg').read_text()).children[0]
def modules(p,name):return [n for n in p.children if n.header=='MODULE' and n.get('name')==name]
audit=json.loads((R/'Reports/DEV23_INDUSTRY.json').read_text());mounts=audit['hull_mounts'];changed=[]
old_files={p.relative_to(BG).as_posix():p for p in BG.rglob('*') if p.is_file()}
allowed={'RoosterWorksGroundModules.version'}|{f'{kind}/{ID}.{ext}' for ID in mounts if ID!='RW_GND_ISRU' for kind,ext in [('Parts','cfg'),('Models','mu')]}
for rel,p in old_files.items():
 check((GD/rel).exists(),'Removed baseline file '+rel)
 if (GD/rel).read_bytes()!=p.read_bytes():changed.append(rel);check(rel in allowed,'Unexpected modification '+rel)
check(set(changed)==allowed,'Expected exact existing-file delta')
for role in ('HAB','LAB','CMD','LOG','GRN','AIR','PWR','TUB'):
 ID='RW_GND_'+role;old=part(role,BG);new=part(role)
 new.values=[(k,v) for k,v in new.values if not k.startswith('node_stack_equipment_')]
 check(new==old,'Existing part behavior changed '+role)
 a=load(BG/f'Models/{ID}.mu');b=load(GD/f'Models/{ID}.mu')
 b.root['children']=[n for n in b.root['children'] if not n['name'].startswith('RW_HullMount_')]
 check(a.root==b.root and a.materials==b.materials and a.textures==b.textures,'Existing native geometry/materials changed '+role)
check(part('VT')==part('VT',BG),'VT clean surface release changed')
check(len(list((GD/'Parts').glob('*.cfg')))==16,'Part count')
check(len(list((GD/'Models').glob('*.mu')))==16,'Native model count')
check(sum(map(len,mounts.values()))==34,'Mount count')
for ID,entries in mounts.items():
 p=part(ID.removeprefix('RW_GND_'));m=load(GD/f'Models/{ID}.mu');nodes={n['name']:n for _,n in walk(m.root)}
 for entry in entries:
  values=[float(x) for x in p.get('node_stack_'+entry['name']).split(',')]
  check(np.allclose(values[:3],entry['position']),'Mount config/geometry position')
  check(np.allclose(values[3:6],entry['outward']),'Mount config normal')
  c=nodes['RW_HullMount_'+entry['name']+'_Collision'];sign=entry['outward'][2]
  face=np.array(c['position'])+np.array((0,0,sign*c['collider']['size'][2]))
  check(np.allclose(face,entry['position']),'Mount exposed face flush with node')
  check(abs(entry['position'][0])+.1 < abs(float(p.get('node_stack_top').split(',')[0])),'Pad crosses docking plane')
 check(p.get('attachRules').split(',')[3]=='1','Hull no longer accepts surface attachment')
 # New structural nodes must not become accidental docking interfaces.
 for port in modules(p,'ModuleDockingNode'):
  check(not port.get('referenceAttachNode','').startswith('equipment'),'Docking module bound to equipment mount')

isru=part('ISRU');converters=modules(isru,'ModuleResourceConverter');check(len(converters)==4,'Refinery conversion modes')
expected=[{'LiquidFuel':.45,'Oxidizer':.55},{'MonoPropellant':1},{'LiquidFuel':.9},{'Oxidizer':1.1}]
for c,outputs in zip(converters,expected):
 ins={n.get('ResourceName'):float(n.get('Ratio')) for n in c.children if n.header=='INPUT_RESOURCE'}
 outs={n.get('ResourceName'):float(n.get('Ratio')) for n in c.children if n.header=='OUTPUT_RESOURCE'}
 check(ins['ElectricCharge']==30 and ins['Ore'] in (.45,.5,.55),'Stock input rates')
 check(outs==outputs,'Stock recipe output')
 # Stock Ore is 0.01 t/unit, LF/Ox 0.005 and monoprop 0.004.
 density={'LiquidFuel':.005,'Oxidizer':.005,'MonoPropellant':.004}
 check(sum(v*density[k] for k,v in outs.items())<=ins['Ore']*.01+1e-12,'Recipe creates mass')
 check(all(n.get('DumpExcess')=='false' for n in c.children if n.header=='OUTPUT_RESOURCE'),'Unwanted resource dumping')
 check(c.get('UseSpecialistBonus')=='true' and c.get('AutoShutdown')=='true','Engineer/thermal safeguards')
check(len(modules(isru,'ModuleDockingNode'))==2,'Inline refinery ports')
check(len(modules(isru,'ModuleRWGroundDeploy'))==1,'Refinery leg controller')
check(len(modules(isru,'ModuleRWGroundDeploy')[0].children)==4,'Refinery four leg transforms')
check(modules(isru,'ModuleRWRingColor')[0].get('ringModel')=='RW_GND_ISRU','Refinery ring map model')
for role in ('ISRU','DRILL','MOUNT'):
 p=part(role);check(p.get('CrewCapacity')=='0','Crewless industry part')
 check(not any(n.get('name')=='Habitat' for n in p.children),'Habitat on industry part')
 check(not any(n.get('name') in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere') for n in p.children if n.header=='RESOURCE'),'Unwanted shielding/pressure')
 if role!='ISRU':check(not modules(p,'ModuleDockingNode'),'Equipment has docking ports')
 for n in p.children:
  if n.header=='RESOURCE':check(0<=float(n.get('amount'))<=float(n.get('maxAmount')),'Invalid tank amount')
check(part('DRILL').get('node_stack_mount')==part('MOUNT').get('node_stack_mount'),'Equipment anchors use different convention')
check(part('MOUNT').get('node_stack_equipment')=='0, 0, .11, 0, 0, 1, 1','Universal shoe exposed node')

stock_path=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/Squad/Parts/Resources/RadialDrill/TriBitDrill.mu')
stock=load_stock(stock_path);clips={c['name'] for _,n in walk(stock.root) for c in n.get('animation',{}).get('clips',[])}
drill=part('DRILL');animation=modules(drill,'ModuleAnimationGroup')[0];harvester=modules(drill,'ModuleResourceHarvester')[0]
check(animation.get('deployAnimationName') in clips and animation.get('activeAnimationName') in clips,'Missing actual stock animation')
check(harvester.get('ResourceName')=='Ore' and harvester.get('HarvesterType')=='0','Surface Ore drill configuration')
check(float(harvester.get('Efficiency'))==.75,'Half-scale drill efficiency')
check(float(next(n for n in harvester.children if n.header=='INPUT_RESOURCE').get('Ratio'))==7.5,'Drill electrical demand')
check(len([n for n in drill.children if n.header=='MODEL'])==2,'Missing bespoke frame or stock mechanism')
poses=[]
for t in (0,.25,.5,.75,1):
 m=stock_pose(stock,t);v=points(m);world=matrices(m.root)
 check(np.isfinite(v).all(),'Non-finite drilling pose')
 # No hull penetration beyond the original recessed mounting face; full drill
 # stroke reaches below the ground-family 2.32 m centerline clearance.
 check(v[:,2].min()>-.03,'Drill swings into hull')
 if t==1:check(-3.1<v[:,1].min()<-2.32,'Drill stroke does not reach ground')
 if t==0:check(v[:,1].min()>-.75,'Retracted mechanism below frame')
 impact=next(n for _,n in walk(m.root) if n['name']==harvester.get('ImpactTransform'))
 mt=world[id(impact)];direction=mt[:3,2]/np.linalg.norm(mt[:3,2]);origin=mt[:3,3];end=origin+direction*float(harvester.get('ImpactRange'))
 check(direction[1]<-.999 and end[1]<-2.32,'Ground-contact ray cannot reach terrain')
 poses.append({'fraction':t,'minimum':v.min(0).tolist(),'maximum':v.max(0).tolist(),'contact_ray_start':origin.tolist(),'contact_ray_end':end.tolist()})
(R/'Reports/DEV23_DRILL_POSES.json').write_text(json.dumps(poses,indent=2)+'\n')

for ID in ('RW_GND_ISRU','RW_GND_DRILL','RW_GND_MOUNT',*mounts.keys()):
 m=load(GD/f'Models/{ID}.mu')
 for path,n in walk(m.root):
  if 'mesh' in n:
   mesh=n['mesh'];v=np.array(mesh['vertices']);norm=np.array(mesh['normals']);check(np.isfinite(v).all() and np.isfinite(norm).all(),'Non-finite native mesh '+path)
   check(len(v)==len(norm)==len(mesh['uvs']) and len(v)<65535,'Mesh cardinality '+path)
   check(np.allclose(np.linalg.norm(norm,axis=1),1,atol=.001),'Non-unit normals '+path)
   for sub in mesh['submeshes']:
    tri=np.array(sub);cross=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]);dot=(cross*norm[tri].mean(1)).sum(1)
    check(dot.min(initial=0)>-1e-7,'Inverted winding '+path)
  if 'collider' in n:
   c=n['collider']
   if c['type']=='box':check(all(s>0 for s in c['size']),'Invalid collider '+path)
  for index in n.get('materials',[]):check(0<=index<len(m.materials),'Invalid material index')
 for tex in m.textures:check((GD/'Models'/(tex['name']+'.png')).exists(),'Missing native texture '+tex['name'])
for mapfile in ('GroundRingGeometry.cfg','IndustryRingGeometry.cfg'):
 for rule in parse((GD/'Compatibility'/mapfile).read_text()).children:
  model=load(GD/f"Models/{rule.get('model')}.mu");nodes=dict(walk(model.root))
  for entry in rule.children:
   mesh=nodes[entry.get('path')]['mesh'];check(int(entry.get('vertices'))==len(mesh['vertices']),'Ring map mesh size')
   for token in entry.get('ranges').split(','):
    start,count=map(int,token.split(':'));check(start>=0 and count>0 and start+count<=len(mesh['vertices']),'Ring map range grammar/bounds')
for file in (GD/'Compatibility').glob('*.cfg'):parse(file.read_text())
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==23,'Version')
for path,digest in json.loads((R/'Reports/DEV23_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected baseline changed '+path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
print(f'PASS dev.23: {checks} native/configuration/preservation checks; 16 parts; four refinery modes; actual stock drill animations and five finite poses; ground-reaching contact ray; 34 flush equipment nodes; old geometry/runtime preserved; ring maps and resource mass balance')
