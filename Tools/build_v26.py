"""Three owned nuclear industry models. All dev.25 assets are read-only inputs."""
from pathlib import Path
import sys,copy,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v25'
sys.path[:0]=[str(W/'rw-v075dev5/Source'),str(W/'rw-v075dev5/Tools'),str(R/'Tools')]
from native_model import load
from native_derivatives import write
from config_nodes import Node,parse,dump
from appearance_textures import label
import build_hab250 as h
from build_v18 import node,box,cylinder,meshnode
GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models'
SPECS=[('NST','Nuclear Materials Vault',4.8,24000,{'ElectricCharge':500,'Uraninite':1000,'RW_NuclearFeedstock':500,'EnrichedUranium':200,'DepletedFuel':200}),
       ('NSM','Nuclear Smelter',5.5,36000,{'ElectricCharge':1000,'Uraninite':250,'RW_NuclearFeedstock':250}),
       ('CEN','Fuel Centrifuge',6.0,68000,{'ElectricCharge':1500,'RW_NuclearFeedstock':250,'EnrichedUranium':40,'DepletedFuel':200})]
RECIPES={'NSM':{'inputs':{'Uraninite':.02,'ElectricCharge':60},'outputs':{'RW_NuclearFeedstock':.01},'heat':54},
         'CEN':{'inputs':{'RW_NuclearFeedstock':.01,'ElectricCharge':120},'outputs':{'EnrichedUranium':.0001,'DepletedFuel':.0067},'heat':108}}

def converter(role):
 d=RECIPES[role];title='Nuclear Smelting' if role=='NSM' else 'Fuel Separation'
 c=Node('MODULE',[('name','ModuleSystemHeatConverter'),('ConverterName',title),('StartActionName','Start '+title),('StopActionName','Stop '+title),('AutoShutdown','true'),('GeneratesHeat','false'),('UseSpecialistBonus','false'),('EfficiencyBonus','1'),('moduleID','rw_'+role.lower()),('systemHeatModuleID','rw_nuclear'),('shutdownTemperature','850'),('systemOutletTemperature','700'),('systemPower',str(d['heat']))],
        [Node('systemEfficiency',[('key','0 0'),('key','700 1'),('key','850 0')])])
 for field,header in [('inputs','INPUT_RESOURCE'),('outputs','OUTPUT_RESOURCE')]:
  for name,rate in d[field].items():
   values=[('ResourceName',name),('Ratio',format(rate,'.8g'))]
   if name in ('EnrichedUranium','DepletedFuel'):values.append(('FlowMode','NO_FLOW'))
   if field=='outputs':values.append(('DumpExcess','false'))
   c.children.append(Node(header,values))
 return c

def main():
 protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev10') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV26_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
 base=parse((B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_PWR.cfg').read_text()).children[0]
 ringbase=next(n for n in parse((GD/'Compatibility/GroundRingGeometry.cfg').read_text()).children if n.get('model')=='RW_GND_PWR')
 rules=[];audit=[]
 for role,title,mass,cost,tanks in SPECS:
  ID='RW_GND_'+role;m=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu');m.name=ID;m.root['name']=ID
  tex='rwm_'+role.lower()+'label'
  for t in m.textures:
   if t['name']=='rwm_pwrlabel':t['name']=tex
  label(role+'-250',title.upper()).save(OUT/(tex+'.png'))
  # One working flank, one clear equipment flank. Retain the exact accepted
  # docking faces, supported roof rails, continuous pipes and telescoping legs.
  m.root['children']=[n for n in m.root['children'] if not n['name'].startswith('RW_HullMount_equipment_starboard')]
  group=node('RW_'+role+'_Industry',(0,.45,0));m.root['children'].append(group)
  meshes={key:h.Mesh() for key in ('rwm_graphite','rwm_steel','rwm_white','rwm_bronze')}
  dark,steel,white,gold=[meshes[k] for k in meshes]
  box(dark,(0,.03,-1.25),(1.85,1.14,.18))
  if role=='NST':
   for x in (-.61,0,.61):
    cylinder(white,(x,-.43,-1.49),(x,.49,-1.49),.235,.235,sides=32)
    for y in (-.49,.49):cylinder(steel,(x,y,-1.49),(x,y+.06,-1.49),.253,.253,sides=32)
    for y in (-.3,-.2,.21,.31):cylinder(gold,(x,y,-1.49),(x,y+.025,-1.49),.241,.241,False,32)
    box(dark,(x,.02,-1.73),(.22,.24,.026))
   box(steel,(0,-.55,-1.47),(1.90,.12,.54))
  elif role=='NSM':
   box(white,(0,.03,-1.50),(1.62,.95,.44))
   for x in (-.56,.56):
    box(dark,(x,.03,-1.74),(.38,.67,.055))
    for y in (-.22,-.10,.02,.14,.26):box(gold,(x,y,-1.78),(.30,.035,.03))
   cylinder(steel,(0,-.38,-1.79),(0,.41,-1.79),.22,.22,sides=32)
   for y in (-.26,.28):cylinder(gold,(0,y,-1.79),(0,y+.04,-1.79),.23,.23,sides=32)
   cylinder(steel,(-.80,.60,-1.40),(.80,.60,-1.40),.055,.055,sides=16)
  else:
   for x in (-.60,0,.60):
    cylinder(steel,(x,-.40,-1.50),(x,.40,-1.50),.215,.215,sides=32)
    cylinder(white,(x,.40,-1.50),(x,.54,-1.50),.215,.11,sides=32)
    cylinder(white,(x,-.54,-1.50),(x,-.40,-1.50),.11,.215,sides=32)
    for y in (-.31,.26):cylinder(gold,(x,y,-1.50),(x,y+.05,-1.50),.225,.225,sides=32)
    box(dark,(x,0,-1.72),(.12,.36,.025))
   for y in (-.59,.59):h.tube(gold,(-.83,y,-1.50),(.83,y,-1.50),.028,12)
  for key,mesh in meshes.items():meshnode(m,group,'RW_'+role+'_Process_'+key,key,mesh)
  co=node('RW_'+role+'_ProcessCollision');co['collider']=dict(type='box',trigger=0,size=(1.92,1.25,.87 if role=='NSM' else .60),center=(0,.02,-1.54));group['children'].append(co)
  write(m,OUT/(ID+'.mu'))
  p=copy.deepcopy(base);p.header='PART:NEEDS[RoosterWorksStationModules,CommunityResourcePack,SystemHeat]'
  for k,v in [('name',ID),('title','RoosterWorks Ground '+role+' — '+title),('TechRequired','nuclearPower'),('category','Utility'),('mass',str(mass)),('cost',str(cost)),('entryCost',str(cost*2)),('breakingForce','2000'),('breakingTorque','2000'),('tags','roosterworks ground nuclear uranium processing storage centrifuge smelter industry')]:p.set(k,v)
  purpose={'NST':'Dedicated materials vault: 1000 Uraninite, 500 RW nuclear feedstock, 200 EnrichedUranium and 200 DepletedFuel. All cargo starts empty. This is storage, not a reactor.',
           'NSM':'Smelts 0.02 Uraninite/s into 0.01 RW nuclear feedstock/s using 60 EC/s; 54 kW process heat. Abstract game recipe. Attach active SystemHeat radiators; requires the Uraninite drill and a separate centrifuge.',
           'CEN':'Processes 0.01 RW nuclear feedstock/s into 0.0001 EnrichedUranium/s and 0.0067 DepletedFuel/s using 120 EC/s; 108 kW process heat. Abstract game recipe. Both output tanks must have room; attach active SystemHeat radiators.'}[role]
  p.set('description',purpose+' Crewless 2.5 m inline utility module with four retractable legs, two strong end docking ports, permanent crossfeed, end lights and independent finish/ring colors. No habitat or shielding resource. Nuclear fuel does not crossfeed: use the installed SystemHeat fuel-transfer controls with a level-3 Engineer to move fuel between compatible vessels/containers. No staging.')
  p.values=[(k,v) for k,v in p.values if not k.startswith('node_stack_equipment_starboard')]
  p.children=[n for n in p.children if n.header!='RESOURCE']
  for n in p.children:
   if n.header=='MODEL':n.set('model','RoosterWorksGroundModules/Models/'+ID)
   if n.get('name')=='ModuleRWRingColor':n.set('ringModel',ID)
   if n.get('moduleID')=='RW_GND_PWR_EndLights':n.set('moduleID',ID+'_EndLights')
   if n.header.startswith('VABORGANIZER'):n.set('organizerSubcategory','resources')
  for name,cap in tanks.items():p.children.append(Node('RESOURCE',[('name',name),('amount',str(cap if name=='ElectricCharge' else 0)),('maxAmount',str(cap))]))
  if role in RECIPES:
   p.children += [Node('MODULE',[('name','ModuleSystemHeat'),('volume',str(mass)),('moduleID','rw_nuclear'),('iconName','Icon_Gears')]),converter(role)]
  if role in ('NST','CEN'):
   p.children.append(Node('MODULE',[('name','ModuleSystemHeatFissionFuelContainer'),('EngineerLevelForTransfer','3'),('ResourceNames','EnrichedUranium, DepletedFuel')]))
  (GD/f'Parts/{ID}.cfg').write_text(dump(Node('ROOT',children=[p])))
  rule=copy.deepcopy(ringbase);rule.set('model',ID)
  for n in rule.children:n.set('path',n.get('path').replace('/RW_GND_PWR/','/'+ID+'/'))
  rules.append(rule)
  report=json.loads((R/'Reports/RW_GND_PWR.json').read_text());(R/f'Reports/{ID}.json').write_text(json.dumps(report,indent=2)+'\n')
  audit.append(dict(id=ID,role=role,title=title,dry_mass_t=mass,cost=cost,capacities=tanks,recipe=RECIPES.get(role),motion_source='RW_GND_PWR'))
 ids=','.join(s['id'] for s in audit)
 rules.append(Node('@PART['+ids+']:NEEDS[Kerbalism]:FINAL',children=[Node('!MODULE[Habitat],*')]+[Node('!RESOURCE['+name+'],*') for name in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')]))
 (GD/'Compatibility/NuclearIndustry.cfg').write_text('// Ground-only ring maps and crewless utility cleanup. No global fuel or distribution edits.\n'+dump(Node('ROOT',children=rules)))
 (GD/'Resources').mkdir(exist_ok=True)
 feed=Node('RESOURCE_DEFINITION:NEEDS[CommunityResourcePack]',[('name','RW_NuclearFeedstock'),('displayName','RW Nuclear Feedstock'),('abbreviation','RW-NF'),('density','0.0075'),('unitCost','0.8'),('hsp','2010'),('flowMode','ALL_VESSEL'),('transfer','PUMP'),('isTweakable','true'),('volume','1')])
 (GD/'Resources/NuclearFeedstock.cfg').write_text('// Fictional intermediate for the RoosterWorks gameplay chain; not a planetary resource.\n'+dump(Node('ROOT',children=[feed])))
 (R/'Reports/DEV26_NUCLEAR.json').write_text(json.dumps(audit,indent=2)+'\n')
 path=GD/'RoosterWorksGroundModules.version';v=json.loads(path.read_text());v['VERSION']['BUILD']=26;path.write_text(json.dumps(v,indent=2)+'\n')
 for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
 print('PASS built NST / NSM / CEN, native models and complete gameplay chain; all prior parts/plugins preserved')

if __name__=='__main__':main()
