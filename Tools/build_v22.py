"""Ground-only logistics capacity and non-habitable utility balance."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent
sys.path.insert(0,str(W/'rw-v075dev5/Source'))
from config_nodes import Node,parse,dump
GD=R/'GameData/RoosterWorksGroundModules';C=GD/'Compatibility'
capacities={'Food':1800,'Water':1700,'Oxygen':350000,'Nitrogen':200000,'Ammonia':40000,'CarbonDioxide':75000,'Hydrogen':750000}
fractions={name:(.2 if name in ('Food','Water','Oxygen') else .1) for name in capacities}
mixed={name:int(capacities[name]*fractions[name]) for name in capacities}
def resource(name,amount,maximum):return Node('RESOURCE',[('name',name),('amount',str(amount)),('maxAmount',str(maximum))])
loadouts=[Node('LOADOUT',[('name','Mixed supplies')],[resource(n,v,v) for n,v in mixed.items()])]
for name,maximum in capacities.items():loadouts.append(Node('LOADOUT',[('name','Carbon Dioxide' if name=='CarbonDioxide' else name)],[resource(name,maximum,maximum)]))
for name in ('Waste','WasteWater'):loadouts.append(Node('LOADOUT',[('name',name)],[resource(name,0,520)]))
patch=Node('@PART[RW_GND_LOG]:NEEDS[Kerbalism,ProfileDefault,CommunityResourcePack]:HAS[!MODULE[ModuleRWGroundLogisticsContents]]:FOR[RoosterWorksGroundModules]',children=[Node('MODULE',[('name','ModuleRWGroundLogisticsContents'),('profileSet','RW_GND_LOG'),('contents','Mixed supplies')])])
profiles=Node('RW_LOG_LOADOUTS',[('name','RW_GND_LOG')],loadouts)
(C/'LogisticsLoadouts.cfg').write_text('// Ground-only capacity profiles; orbital profiles remain unchanged.\n'+dump(Node('ROOT',children=[patch,profiles])),encoding='utf-8')
# Fallback default matches the selector; no habitat is created for LOG.
fallback=[]
for name,value in mixed.items():fallback.append(Node('%RESOURCE['+name+']',[('%name',name),('%amount',str(value)),('%maxAmount',str(value))]))
for name in ('Waste','WasteWater'):fallback.append(Node('!RESOURCE['+name+'],*'))
(C/'LogisticsKerbalism.cfg').write_text(dump(Node('ROOT',children=[Node('@PART[RW_GND_LOG]:NEEDS[Kerbalism,ProfileDefault]:AFTER[zzzKerbalismDefault]',children=fallback)])),encoding='utf-8')
cleanup=[Node('@PART['+part+']:NEEDS[Kerbalism]:FINAL',children=[Node('!MODULE[Habitat],*')]+[Node('!RESOURCE['+n+'],*') for n in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')]+[Node('!MODULE[Sensor]:HAS[#type[habitat_radiation]]')]) for part in ('RW_GND_LOG','RW_GND_PWR')]
remove_old=Node('@PART[RW_GND_LOG]:FINAL',children=[Node('!MODULE[ModuleRWLogisticsContents],*')])
(C/'ZZZZGroundUtilityNoHabitat.cfg').write_text('// Crewless utilities: no pressurized habitat or shielding; cargo gases and reactor unchanged.\n'+dump(Node('ROOT',children=cleanup+[remove_old])),encoding='utf-8')
src=(W/'rw-v075dev5/Source/LogisticsContents.cs').read_text(encoding='utf-8').replace('ModuleRWLogisticsContents','ModuleRWGroundLogisticsContents').replace('"RW_LOG_250"','"RW_GND_LOG"')
src=src.replace('"Ammonia", "Waste"','"Ammonia", "Carbon Dioxide", "Hydrogen", "Waste"',1)
src=src.replace('"Ammonia", "Waste"','"Ammonia", "CarbonDioxide", "Hydrogen", "Waste"',1)
src=src.replace('Ammonia, Waste or WasteWater','Ammonia, Carbon Dioxide, Hydrogen, Waste or WasteWater').replace('Fixed payload volume','Mixed loadout reserves 60% of capacity for food, water and oxygen. Dedicated capacities are calibrated by resource;')
(R/'Source/GroundLogisticsContents.cs').write_text(src,encoding='utf-8')
p=R/'Tools/build-runtime.ps1';s=p.read_text();line="$argsList += Join-Path $kit 'Source/GroundLogisticsContents.cs'"
if line not in s:s=s.replace('& dotnet @argsList',line+'\n& dotnet @argsList');p.write_text(s)
p=GD/'RoosterWorksGroundModules.version';v=json.loads(p.read_text());v['VERSION']['BUILD']=22;p.write_text(json.dumps(v,indent=2)+'\n')
(R/'Reports/LOG_CAPACITIES.json').write_text(json.dumps({'dedicated':capacities,'fractions':fractions,'mixed':mixed,'loadouts':{n.get('name'):[dict(r.values) for r in n.children] for n in loadouts}},indent=2)+'\n')
print('PASS built ground-only profiles, seven requested capacities, priority mixed supplies and utility habitat cleanup')
