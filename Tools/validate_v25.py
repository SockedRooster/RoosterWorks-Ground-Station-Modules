from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;sys.path.insert(0,str(W/'rw-v075dev5/Source'))
from config_nodes import parse,dump
GD=R/'GameData/RoosterWorksGroundModules';BG=W/'ground-hotpatch-v24/GameData/RoosterWorksGroundModules';checks=0
def check(v,message):
 global checks
 checks+=1
 assert v,message
specs=json.loads((R/'Reports/DEV25_MINERAL_DRILLS.json').read_text());inventory=json.loads((R/'Source/MiningVariants/InstalledResourceInventory.json').read_text())
expected={'MetalOre','MetallicOre','Minerals','Substrate','Uraninite','Lithium','RareMetals','Rock'};check({s['resource'] for s in specs}==expected and len(specs)==8,'Specialist set')
added=set()
for spec in specs:
 slug=spec['resource'].lower();added|={f"Parts/{spec['id']}.cfg",f'Models/rwm_drilllabel_{slug}.png',f'Models/rwm_drillpaint_{slug}.png'}
added.add('Compatibility/MineralDrills.cfg')
new={p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file() and not (BG/p.relative_to(GD)).exists()};check(new==added,'GameData addition scope')
for old in BG.rglob('*'):
 if old.is_file():
  rel=old.relative_to(BG);check((GD/rel).exists(),'Removed previous asset')
  if rel.as_posix()!='RoosterWorksGroundModules.version':check((GD/rel).read_bytes()==old.read_bytes(),'Changed previous file '+str(rel))
check(len(list((GD/'Parts').glob('*.cfg')))==25,'Part count')
check(len(list((GD/'Models').glob('*.mu')))==17,'Native models must be reused')
base=parse((BG/'Parts/RW_GND_DRILL.cfg').read_text()).children[0];base_stock=[n for n in base.children if n.header=='MODEL'][1]
native_textures={'rwm_drilllabel','rwm_white'};hashes=set()
for s in specs:
 resource=s['resource'];p=parse((GD/f"Parts/{s['id']}.cfg").read_text()).children[0]
 check(p.get('name')==s['id'] and s['display'] in p.get('title'),'Part identity')
 check(p.header=='PART:NEEDS[RoosterWorksStationModules,'+s['dependency']+']','Optional resource dependency')
 check(inventory['definitions'][resource]['volume'] is not None and inventory['positive_crustal_distributions'][resource],'Resource not defined or mapped in installed snapshot')
 for d in inventory['positive_crustal_distributions'][resource]:check(float(d['PresenceChance'])>0 and float(d['MaxAbundance'])>0,'Zero-abundance reference entry')
 models=[n for n in p.children if n.header=='MODEL'];check(len(models)==2 and models[1]==base_stock,'Stock mechanism/animation changed')
 check(models[0].get('model')=='RoosterWorksGroundModules/Models/RW_GND_DRILL','Native frame reuse')
 remaps={v.split(',')[0].strip():v.split(',')[1].strip() for k,v in models[0].values if k=='texture'};check(set(remaps)==native_textures,'MODEL texture remaps')
 for old,newpath in remaps.items():
  path=R/'GameData'/(newpath+'.png');check(path.exists(),'Missing specialist texture');im=Image.open(path);check(im.mode=='RGB' and im.width>=128 and im.height>=128,'Texture mode/size')
  if old=='rwm_drillpaint':raise AssertionError('Wrong target texture')
  hashes.add(hashlib.sha256(path.read_bytes()).hexdigest())
 modules=[n for n in p.children if n.header=='MODULE'];harvest=[n for n in modules if n.get('name')=='ModuleResourceHarvester'];check(len(harvest)==1,'Multiple harvesters on specialist')
 h=harvest[0];check(h.get('ResourceName')==resource and h.get('HarvesterType')=='0','Wrong resource or crustal type')
 check(h.get('HarvestThreshold')=='0','Trace deposits rejected')
 check(h.get('ImpactTransform')=='ImpactTransform' and h.get('ImpactRange')=='2.71','Ground reach altered')
 check(h.get('UseSpecialistBonus')==h.get('AutoShutdown')==h.get('GeneratesHeat')=='true','Stock thermal/engineer safeguards')
 power=next(n for n in h.children if n.header=='INPUT_RESOURCE');check(power.get('ResourceName')=='ElectricCharge' and float(power.get('Ratio'))==7.5,'Power balance')
 definition=inventory['definitions'][resource];volume=float(definition['volume']);check(abs(float(h.get('Efficiency'))*volume-.75*5)<1e-8,'Volumetric efficiency normalization')
 tanks={n.get('name'):n for n in p.children if n.header=='RESOURCE'};check(set(tanks)=={'ElectricCharge',resource},'Wrong buffer resources')
 check(tanks[resource].get('amount')=='0','Prefilled mineral cargo')
 capacity=float(tanks[resource].get('maxAmount'));check(capacity*volume==250 and capacity%10==0,'Buffer volume/rounding')
 check(tanks['ElectricCharge'].get('amount')==tanks['ElectricCharge'].get('maxAmount')=='150','Electrical buffer')
 check(float(p.get('mass'))==.65 and float(p.get('cost'))==4800,'Dry mass/cost')
 # Restore only intentional specialization fields, then compare the complete
 # part tree: attachment, animations, heat curves and all other modules match.
 q=copy.deepcopy(p);q.header=base.header
 for key in ('name','title','description','tags'):q.set(key,base.get(key))
 frame=next(n for n in q.children if n.header=='MODEL' and n.get('model').startswith('RoosterWorks'));frame.values=[(k,v) for k,v in frame.values if k!='texture']
 q.children=[n for n in q.children if not n.header.startswith('VABORGANIZER')]
 hq=next(n for n in q.children if n.get('name')=='ModuleResourceHarvester');hq.values=[(k,v) for k,v in hq.values if k!='HarvestThreshold']
 hb=next(n for n in base.children if n.get('name')=='ModuleResourceHarvester')
 for k in ('ResourceName','Efficiency','ConverterName','StartActionName','StopActionName','ToggleActionName'):hq.set(k,hb.get(k))
 tq=next(n for n in q.children if n.header=='RESOURCE' and n.get('name')==resource);tq.set('name','Ore');tq.set('maxAmount','50')
 check(q==base,'Unintended specialization change '+resource)
check(len(hashes)==16,'Specialist skins must be distinct')
cleanup=parse((GD/'Compatibility/MineralDrills.cfg').read_text()).children
check(len(cleanup)==1 and 'RW_GND_DRILL_MetalOre' in cleanup[0].header,'Scoped utility cleanup')
check(not any(n.header in ('GLOBAL_RESOURCE','PLANETARY_RESOURCE','BIOME_RESOURCE') for f in (GD/'Compatibility').glob('*.cfg') for n in parse(f.read_text()).children),'Unexpected distribution edit')
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==25,'Version')
for path,digest in json.loads((R/'Reports/DEV25_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected baseline '+path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
print(f'PASS dev.25: {checks} resource/configuration/preservation checks; eight mapped crustal specialists; exact resource identities; optional dependencies; 250 L empty buffers and volume-normalized efficiency; native geometry/stock mechanism/plugins and every prior part preserved; no distribution or ISRU changes')
