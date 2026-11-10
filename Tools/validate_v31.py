from pathlib import Path
import sys,json,hashlib,copy
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];B=R.parent/'ground-hotpatch-v30';GD=R/'GameData/RoosterWorksGroundModules'
sys.path.insert(0,str(R.parent/'rw-v075dev5/Source'))
from config_nodes import parse,dump
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=0
def check(v,msg):
 global checks
 assert v,msg
 checks+=1
baseline=json.loads((R/'Reports/DEV31_BASELINE.json').read_text())
version='GameData/RoosterWorksGroundModules/RoosterWorksGroundModules.version'
for name,digest in baseline.items():
 check(sha(B/name)==digest,'baseline changed '+name)
 if name!=version:check(sha(R/name)==digest,'existing payload changed '+name)
added={p.relative_to(R).as_posix() for p in (R/'GameData').rglob('*') if p.is_file()}-set(baseline)
check(added=={'GameData/RoosterWorksGroundModules/'+n for n in ('Parts/RW_GND_DRILL_Water.cfg','Models/rwm_drilllabel_water.png','Models/rwm_drillpaint_water.png','Compatibility/WaterDrill.cfg')},'unexpected additions')
p=parse((GD/'Parts/RW_GND_DRILL_Water.cfg').read_text()).children[0]
q=parse((GD/'Parts/RW_GND_DRILL_Minerals.cfg').read_text()).children[0]
check(p.header=='PART:NEEDS[RoosterWorksStationModules,CommunityResourcePack]','dependencies')
h=next(n for n in p.children if n.get('name')=='ModuleResourceHarvester')
check(h.get('ResourceName')=='Water' and h.get('HarvesterType')=='0','crustal water')
inv=json.loads((R/'Source/WaterDrill/InstalledWaterInventory.json').read_text());d=inv['definitions']['Water'];capacity=250/float(d['volume'])
check(bool(inv['positive_crustal_distributions']),'positive maps')
check(float(h.get('Efficiency'))*float(d['volume'])==.75*float(inv['definitions']['Ore']['volume']),'normalized volume output')
water=next(n for n in p.children if n.header=='RESOURCE' and n.get('name')=='Water')
check(float(water.get('maxAmount'))==capacity and water.get('amount')=='0','buffer')
check(abs(float(p.get('cost'))-capacity*float(d['unitCost'])-4800)<1e-8,'empty cost')
check(p.get('CrewCapacity')=='0','crewless')
check('organizerSubcategory = resources' in dump(p),'Harvesting category')
check('@PART[RW_GND_DRILL,RW_GND_DRILL_*]' in (GD/'Compatibility/ZZZZZGroundIndustryCategories.cfg').read_text(),'wildcard category policy')
# Compare unchanged mechanism, animation, heat and all other fields with the established rig.
for key in ('name','title','cost','description','tags'):p.set(key,q.get(key))
for n in p.children:
 if n.header=='MODEL':n.values=[(k,v.replace('_water','_minerals')) for k,v in n.values]
 if n.get('name')=='ModuleResourceHarvester':
  source=next(x for x in q.children if x.get('name')=='ModuleResourceHarvester')
  for key in ('ResourceName','ConverterName','StartActionName','StopActionName','ToggleActionName','Efficiency'):n.set(key,source.get(key))
 if n.header=='RESOURCE' and n.get('name')=='Water':n.set('name','Minerals')
check(dump(p)==dump(q),'unexpected mechanism or gameplay change')
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,name=line.split('  ',1);check(sha(R/name)==digest,'manifest '+name)
check(len(list((GD/'Parts').glob('*.cfg')))==29,'part count')
check(json.loads((R/version).read_text())['VERSION']['BUILD']==31,'version')
print(f'PASS dev.31 Water drill: {checks} preservation, configuration, resource-map and manifest checks; live KSP testing pending')
