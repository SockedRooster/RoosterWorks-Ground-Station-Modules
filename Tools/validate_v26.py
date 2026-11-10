from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent
sys.path[:0]=[str(W/'rw-v075dev5/Source'),str(W/'rw-v075dev5/Tools'),str(R/'Tools')]
from native_model import load,walk
from config_nodes import parse
from industry_geometry import matrices
from poses import world_nodes
GD=R/'GameData/RoosterWorksGroundModules';BG=W/'ground-hotpatch-v25/GameData/RoosterWorksGroundModules';checks=0
def check(v,message):
 global checks
 checks+=1
 assert v,message

specs=json.loads((R/'Reports/DEV26_NUCLEAR.json').read_text());check({s['role'] for s in specs}=={'NST','NSM','CEN'},'Three nuclear parts')
added={'Compatibility/NuclearIndustry.cfg','Resources/NuclearFeedstock.cfg'}
for s in specs:added|={f"Parts/{s['id']}.cfg",f"Models/{s['id']}.mu",'Models/rwm_'+s['role'].lower()+'label.png'}
check({p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file() and not (BG/p.relative_to(GD)).exists()}==added,'Addition scope')
for old in BG.rglob('*'):
 if not old.is_file():continue
 rel=old.relative_to(BG);check((GD/rel).exists(),'Removed old file')
 if rel.as_posix()!='RoosterWorksGroundModules.version':check((GD/rel).read_bytes()==old.read_bytes(),'Changed old file '+str(rel))
check(len(list((GD/'Parts').glob('*.cfg')))==28,'28 parts')
check(len(list((GD/'Models').glob('*.mu')))==20,'20 native models')
base=parse((BG/'Parts/RW_GND_PWR.cfg').read_text()).children[0];bm=load(BG/'Models/RW_GND_PWR.mu')
rules=parse((GD/'Compatibility/NuclearIndustry.cfg').read_text()).children
densities={'Uraninite':.0075,'RW_NuclearFeedstock':.0075,'EnrichedUranium':.01097,'DepletedFuel':.01097}
fixture={};bounds={}
for s in specs:
 ID=s['id'];role=s['role'];p=parse((GD/f'Parts/{ID}.cfg').read_text()).children[0]
 check(p.header=='PART:NEEDS[RoosterWorksStationModules,CommunityResourcePack,SystemHeat]','Required installed providers')
 check(p.get('CrewCapacity')=='0' and p.get('mass')==str(s['dry_mass_t']),'Mass/crew')
 check(p.get('breakingForce')==p.get('breakingTorque')=='2000' and p.get('fuelCrossFeed')=='true','Strong crossfeed connections')
 check(not any(n.get('name') in ('Habitat','Shielding','ModuleRCS','ModuleRCSFX','ModuleCommand') for n in p.children),'Utility scope')
 tanks={n.get('name'):n for n in p.children if n.header=='RESOURCE'};check(set(tanks)==set(s['capacities']),'Cargo set')
 for name,tank in tanks.items():
  check(float(tank.get('maxAmount'))==s['capacities'][name] and s['capacities'][name]%10==0,'Round capacities')
  check(float(tank.get('amount'))==(s['capacities'][name] if name=='ElectricCharge' else 0),'Initial tank contents')
 model=load(GD/f'Models/{ID}.mu');nodes=dict(walk(model.root));named={n['name']:n for _,n in walk(model.root)};world=matrices(model.root)
 check(model.root['name']==ID,'Native root')
 # Every retained base child has exactly the same geometry and transform.
 for old in bm.root['children']:
  if old['name'].startswith('RW_HullMount_equipment_starboard'):continue
  check(named[old['name']]==old,'Accepted hull geometry changed '+old['name'])
  check('RW_HullMount_equipment_starboard' not in old['name'],'Occupied flank mount')
 allv=[]
 for path,n in walk(model.root):
  if 'mesh' in n:
   m=n['mesh'];v=np.array(m['vertices']);norm=np.array(m['normals']);allv.append(v@world[id(n)][:3,:3].T+world[id(n)][:3,3])
   check(len(v)==len(norm)==len(m['uvs']) and len(v)<65535,'Native mesh cardinality')
   check(np.isfinite(v).all() and np.isfinite(norm).all() and np.isfinite(m['uvs']).all(),'Finite data')
   check(np.allclose(np.linalg.norm(norm,axis=1),1,atol=.001),'Unit normals')
   for sub in m['submeshes']:
    tri=np.array(sub);check(tri.min()>=0 and tri.max()<len(v),'Triangle bounds')
    cross=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
    check(((cross*norm[tri].mean(1)).sum(1)).min(initial=0)>-1e-7,'Winding '+path)
  if 'collider' in n:
   c=n['collider']
   if c['type']=='box':check(all(x>0 for x in c['size']),'Positive collider')
   else:check(c['convex']==1 and sum(map(len,c['mesh']['submeshes']))<=255,'PhysX convex limit')
 for tex in model.textures:check((GD/'Models'/(tex['name']+'.png')).exists(),'Texture reference '+tex['name'])
 ports=[n for n in p.children if n.get('name')=='ModuleDockingNode'];check(len(ports)==2,'Two end docks')
 for dock in ports:
  key=dock.get('referenceAttachNode');target=np.array([float(x) for x in p.get('node_stack_'+key).split(',')]);mt=world[id(named[dock.get('nodeTransformName')])]
  check(np.allclose(mt[:3,3],target[:3]) and np.allclose(mt[:3,2],target[3:6],atol=1e-6),'Dock alignment')
  check(dock.get('stagingEnabled')=='false' and dock.get('crossfeed')=='true' and dock.get('acquireForce')=='40','Accepted dock settings')
 deploy=next(n for n in p.children if n.get('name')=='ModuleRWGroundDeploy')
 check(deploy==next(n for n in base.children if n.get('name')=='ModuleRWGroundDeploy'),'Accepted leg controls')
 for bind in deploy.children:check(bind.get('name') in named,'Leg binding exists')
 # Process housing occupies only the middle flank and stays clear of moving
 # leg mesh bounds throughout the accepted retraction curve.
 process=next(n for n in model.root['children'] if n['name']=='RW_'+role+'_Industry')
 pv=np.concatenate([np.array(n['mesh']['vertices'])@world[id(n)][:3,:3].T+world[id(n)][:3,3] for _,n in walk(process) if 'mesh' in n]);pmin=pv.min(0);pmax=pv.max(0)
 check(pmin[0]>-1.20 and pmax[0]<1.20,'Clear docking planes')
 for progress in np.linspace(0,1,21):
  moving=[]
  for n,mt in world_nodes(model,float(progress)):
   if 'mesh' in n and ('Leg' in n['name'] or 'Ram' in n['name']):
    v=np.array(n['mesh']['vertices'])@mt[:3,:3].T+mt[:3,3];moving.append(v)
  check(bool(moving),'Leg mesh census')
  for v in moving:
   overlap=np.minimum(v.max(0),pmax)-np.maximum(v.min(0),pmin)
   check(not np.all(overlap>1e-5),'Process housing/leg bounding overlap at '+str(progress))
 rule=next(n for n in rules if n.get('model')==ID);check(len(rule.children)==3,'Three ring meshes')
 fixture[ID]=[]
 for e in rule.children:
  m=nodes[e.get('path')]['mesh'];check(int(e.get('vertices'))==len(m['vertices']) and int(e.get('triangles'))==len(m['submeshes'][0]),'Exact native map counts')
  for item in e.get('ranges').split(','):
   start,count=map(int,item.split(':'));check(start>=0 and count>0 and start+count<=len(m['submeshes'][0]),'Valid colon-count map')
  fixture[ID].append(dict(path=e.get('path'),texture=e.get('texture'),vertexCount=len(m['vertices']),triangles=[i for t in m['submeshes'][0] for i in t],ranges=e.get('ranges')))
 check(next(n for n in p.children if n.get('name')=='ModuleRWRingColor').get('ringModel')==ID,'Ring ID')
 check(next(n for n in p.children if n.get('name')=='ModuleColorChanger').get('includedRenderer')=='RW_EndWindows','End lights')
 converters=[n for n in p.children if n.get('name')=='ModuleSystemHeatConverter']
 if s['recipe']:
  check(len(converters)==1,'Single converter');c=converters[0];d=s['recipe']
  check(c.get('UseSpecialistBonus')=='false' and c.get('AutoShutdown')=='true' and c.get('shutdownTemperature')=='850','Explicit safety/efficiency settings')
  for key,header in [('inputs','INPUT_RESOURCE'),('outputs','OUTPUT_RESOURCE')]:
   actual={n.get('ResourceName'):float(n.get('Ratio')) for n in c.children if n.header==header};check(actual==d[key],'Recipe '+key)
  im=sum(densities[n]*rate for n,rate in d['inputs'].items() if n!='ElectricCharge');om=sum(densities[n]*rate for n,rate in d['outputs'].items())
  check(0<om<=im,'No resource mass creation')
  check(d['inputs']['ElectricCharge']>0 and float(c.get('systemPower'))==d['heat'],'Power/cooling')
  heat=next(n for n in p.children if n.get('name')=='ModuleSystemHeat');check(heat.get('moduleID')==c.get('systemHeatModuleID'),'Thermal link')
  for n in c.children:
   if n.header=='OUTPUT_RESOURCE':
    check(n.get('DumpExcess')=='false','No silent nuclear dumping')
    if n.get('ResourceName') in ('EnrichedUranium','DepletedFuel'):check(n.get('FlowMode')=='NO_FLOW' and n.get('ResourceName') in tanks,'Local nuclear output tanks')
 else:check(not converters,'Vault must not generate fuel/power')
 transfer=[n for n in p.children if n.get('name')=='ModuleSystemHeatFissionFuelContainer']
 check(bool(transfer)==(role in ('NST','CEN')),'Fuel transfer availability')
 if transfer:check(transfer[0].get('EngineerLevelForTransfer')=='3' and transfer[0].get('ResourceNames')=='EnrichedUranium, DepletedFuel','Provider fuel-transfer settings')
 v=np.concatenate(allv);bounds[ID]={'min':v.min(0).tolist(),'max':v.max(0).tolist()}
 check(v[:,0].min()>=-1.50 and v[:,0].max()<=1.50,'Physical hardware end envelope')
feed=parse((GD/'Resources/NuclearFeedstock.cfg').read_text()).children[0]
check(feed.get('name')=='RW_NuclearFeedstock' and feed.get('flowMode')=='ALL_VESSEL' and feed.get('transfer')=='PUMP','Fictional pumpable intermediate')
check(float(feed.get('density'))==densities['RW_NuclearFeedstock'],'Intermediate density')
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==26,'Version')
for f in GD.rglob('*.cfg'):parse(f.read_text())
for path,digest in json.loads((R/'Reports/DEV26_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected baseline '+path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
(R/'Reports/NUCLEAR_COLOR_FIXTURE.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
(R/'Reports/DEV26_BOUNDS.json').write_text(json.dumps(bounds,indent=2)+'\n')
print(f'PASS dev.26: {checks} native/configuration/preservation checks; three nuclear industry parts; exact end docks/leg bindings, 21-pose hardware clearance, ring maps, complete mass-bounded recipes, cooling, local fuel output/transfer, empty cargo and all dev.25 assets preserved')
