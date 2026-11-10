"""Eight specialist drill parts, with native MODEL texture remaps.

The original Ore rig, ISRU, all meshes and every plugin remain untouched.
Only real installed crustal resources are selected; no distribution is added.
"""
from pathlib import Path
import sys,re,json,hashlib,copy
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v24';CORE=W/'rw-v075dev5'
sys.path.insert(0,str(CORE/'Source'))
from config_nodes import Node,parse,dump
from appearance_textures import label
GD=R/'GameData/RoosterWorksGroundModules';SOURCE=R/'Source/MiningVariants';SOURCE.mkdir(exist_ok=True)
GAME=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program')
SPECS=[
 ('MetalOre','Metal Ore','MET',[96,127,154],'ExtraplanetaryLaunchpads|SimpleConstruction'),
 ('MetallicOre','Metallic Ore','MTO',[161,77,48],'CommunityResourcePack'),
 ('Minerals','Minerals','MIN',[184,142,52],'CommunityResourcePack'),
 ('Substrate','Substrate','SUB',[118,132,72],'CommunityResourcePack'),
 ('Uraninite','Uraninite','URN',[156,173,45],'CommunityResourcePack'),
 ('Lithium','Lithium','LTH',[49,135,179],'CommunityResourcePack'),
 ('RareMetals','Rare Metals','RAR',[136,94,161],'CommunityResourcePack'),
 ('Rock','Rock','RCK',[124,127,124],'CommunityResourcePack'),
]

def blocks(text,headers):
 pattern=r'(?m)^\s*('+('|'.join(headers))+r')\s*\n\s*\{'
 for match in re.finditer(pattern,text):
  start=match.end();depth=1;end=start
  while depth:
   if text[end]=='{':depth+=1
   elif text[end]=='}':depth-=1
   end+=1
  yield match.group(1),text[start:end-1]
def fields(block):return dict(re.findall(r'(?m)^\s*([a-zA-Z_]+)\s*=\s*([^\r\n]+)',block))

def inventory():
 out=SOURCE/'InstalledResourceInventory.json'
 if out.exists():return json.loads(out.read_text())
 file=GAME/'GameData/ModuleManager.ConfigCache';text=file.read_text(encoding='utf-8-sig')
 wanted={s[0] for s in SPECS}|{'Ore'};definitions={};distribution={n:[] for n in wanted}
 for _,block in blocks(text,['RESOURCE_DEFINITION']):
  f=fields(block)
  if f.get('name') in wanted:
   name=f['name'];entry={k:f.get(k) for k in ('density','volume','flowMode')}
   if name in definitions:assert definitions[name]==entry,('Conflicting definition',name)
   definitions[name]=entry
 for kind,block in blocks(text,['GLOBAL_RESOURCE','PLANETARY_RESOURCE','BIOME_RESOURCE']):
  f=fields(block);name=f.get('ResourceName')
  if name in wanted and f.get('ResourceType')=='0' and float(f.get('PresenceChance','0'))>0 and float(f.get('MaxAbundance','0'))>0:
   distribution[name].append({k:f.get(k) for k in ('PlanetName','BiomeName','PresenceChance','MinAbundance','MaxAbundance')}|{'kind':kind})
 for name in wanted:assert name in definitions and distribution[name],('No defined and mapped crustal resource',name)
 data={'source':'Installed ModuleManager.ConfigCache, KSP 1.12.5','source_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'definitions':definitions,'positive_crustal_distributions':distribution,'maps_are_reference_only':True,'not_guaranteed_local_abundance':True}
 out.write_text(json.dumps(data,indent=2)+'\n');return data

def main():
 protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev10') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV25_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
 inv=inventory();original=parse((B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_DRILL.cfg').read_text()).children[0]
 ore_volume=float(inv['definitions']['Ore']['volume']);buffer_liters=50*ore_volume
 paint=Image.open(GD/'Models/rwm_white.png').convert('RGB');audit=[]
 for resource,display,code,color,dependency in SPECS:
  ID='RW_GND_DRILL_'+resource;slug=resource.lower();p=copy.deepcopy(original)
  volume=float(inv['definitions'][resource]['volume']);capacity=buffer_liters/volume;efficiency=.75*ore_volume/volume
  assert capacity%10==0
  p.header='PART:NEEDS[RoosterWorksStationModules,'+dependency+']';p.set('name',ID)
  p.set('title','RoosterWorks Ground DRILL-'+code+' — '+display+' Rig')
  p.set('description',f'Specialist {display} surface mining rig in the RoosterWorks drill family. Same half-scale deployable mechanism, mounting frame and 2.71 m contact reach as the Ore rig. Requires a scanned site with nonzero crustal {display}, power, ground contact and active radiators; engineer/thermal bonuses apply. 7.5 EC/s; 150 EC and {capacity:g} {display} capacity ({buffer_liters:g} L), initially empty. {display} is raw feedstock: external storage and compatible processing are separate. No automatic conversion or planet-wide deposit additions. Color-coded {code} frame/label; fixed specialist part, not an in-flight resource selector.')
  p.set('tags','roosterworks ground drill mining extractor resource '+display.lower()+' '+resource.lower()+' '+code.lower())
  frame=next(n for n in p.children if n.header=='MODEL' and n.get('model')=='RoosterWorksGroundModules/Models/RW_GND_DRILL')
  for old,new in [('rwm_drilllabel','rwm_drilllabel_'+slug),('rwm_white','rwm_drillpaint_'+slug)]:frame.values.append(('texture',old+', RoosterWorksGroundModules/Models/'+new))
  harvester=next(n for n in p.children if n.get('name')=='ModuleResourceHarvester')
  for key,value in [('ResourceName',resource),('ConverterName',display+' Extraction'),('StartActionName','Start '+display+' Drill'),('StopActionName','Stop '+display+' Drill'),('ToggleActionName','Toggle '+display+' Drill'),('Efficiency',format(efficiency,'.8g')),('HarvestThreshold','0')]:harvester.set(key,value)
  for n in p.children:
   if n.header=='RESOURCE' and n.get('name')=='Ore':n.set('name',resource);n.set('amount','0');n.set('maxAmount',format(capacity,'.8g'))
  p.children.append(Node('VABORGANIZER:NEEDS[VABOrganizer]',[('organizerSubcategory','resources')]))
  (GD/f'Parts/{ID}.cfg').write_text(dump(Node('ROOT',children=[p])))
  im=label('DRILL-'+code,display.upper()+' MINING');draw=ImageDraw.Draw(im);draw.rectangle((47,47,976,80),fill=tuple(color));im.save(GD/f'Models/rwm_drilllabel_{slug}.png',optimize=True)
  tinted=Image.blend(paint,Image.new('RGB',paint.size,tuple(color)),.70);tinted.save(GD/f'Models/rwm_drillpaint_{slug}.png',optimize=True)
  audit.append({'id':ID,'resource':resource,'display':display,'code':code,'color':color,'dependency':dependency,'capacity_units':capacity,'buffer_liters':buffer_liters,'unit_volume_liters':volume,'dry_mass_t':.65,'full_resource_mass_t':capacity*float(inv['definitions'][resource]['density']),'efficiency':efficiency,'ec_per_second':7.5,'frame_model':'RW_GND_DRILL','stock_mechanism_unchanged':True,'known_positive_map_records':len(inv['positive_crustal_distributions'][resource])})
 (R/'Reports/DEV25_MINERAL_DRILLS.json').write_text(json.dumps(audit,indent=2)+'\n')
 ids=','.join(s['id'] for s in audit)
 cleanup=Node('@PART['+ids+']:NEEDS[Kerbalism]:FINAL',children=[Node('!MODULE[Habitat],*')]+[Node('!RESOURCE['+s+'],*') for s in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')])
 (GD/'Compatibility/MineralDrills.cfg').write_text('// Specialist stock harvesters use installed resource maps; no distributions or conversion recipes added.\n'+dump(Node('ROOT',children=[cleanup])))
 path=GD/'RoosterWorksGroundModules.version';v=json.loads(path.read_text());v['VERSION']['BUILD']=25;path.write_text(json.dumps(v,indent=2)+'\n')
 for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
 print('PASS built eight mineral drill specialists; active crustal resource maps verified; 250 L empty buffers; distinct labels/paint; all existing assets and plugins preserved')

if __name__=='__main__':main()
