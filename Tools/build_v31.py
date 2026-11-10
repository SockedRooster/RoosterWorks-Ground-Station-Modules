"""Water specialist built from the existing mineral rig; installed maps are reference only."""
from pathlib import Path
import sys,json,hashlib,copy
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v30'
sys.path.insert(0,str(R/'Tools'))
import build_v25 as helper
from config_nodes import Node,parse,dump
from appearance_textures import label
from PIL import Image,ImageDraw
GD=R/'GameData/RoosterWorksGroundModules'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 protected={p.relative_to(B).as_posix():sha(p) for p in (B/'GameData').rglob('*') if p.is_file()}
 (R/'Reports/DEV31_BASELINE.json').write_text(json.dumps(protected,indent=2)+'\n')
 cache=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/ModuleManager.ConfigCache');text=cache.read_text(encoding='utf-8-sig')
 definitions={helper.fields(body)['name']:helper.fields(body) for _,body in helper.blocks(text,['RESOURCE_DEFINITION']) if helper.fields(body).get('name') in ('Ore','Water')}
 maps=[{'kind':kind,**helper.fields(body)} for kind,body in helper.blocks(text,['GLOBAL_RESOURCE','PLANETARY_RESOURCE','BIOME_RESOURCE']) if helper.fields(body).get('ResourceName')=='Water' and helper.fields(body).get('ResourceType')=='0' and float(helper.fields(body).get('PresenceChance',0))>0 and float(helper.fields(body).get('MaxAbundance',0))>0]
 assert maps and set(definitions)=={'Ore','Water'}
 source=R/'Source/WaterDrill';source.mkdir(exist_ok=True)
 inv={'source_sha256':sha(cache),'definitions':definitions,'positive_crustal_distributions':maps,'reference_only':True}
 (source/'InstalledWaterInventory.json').write_text(json.dumps(inv,indent=2)+'\n')
 p=parse((GD/'Parts/RW_GND_DRILL_Minerals.cfg').read_text()).children[0]
 p.set('name','RW_GND_DRILL_Water');p.set('title','RoosterWorks Ground DRILL-H2O — Water Rig')
 volume=float(definitions['Water']['volume']);capacity=250/volume;efficiency=.75*float(definitions['Ore']['volume'])/volume
 p.set('cost',format(4800+capacity*float(definitions['Water']['unitCost']),'.10g'))
 p.set('description',f'Deployable RoosterWorks water drilling rig. Extracts mapped crustal Water at sites with nonzero abundance and ground contact. Same 2.71 m reach, thermal system and engineer bonuses as the other RoosterWorks drills. Requires 7.5 EC/s and radiator cooling; carries 150 EC and an initially empty {capacity:g}-unit ({250:g} L) Water buffer. Scan for Water before choosing a site. Connect to logistics storage for sustained extraction. This drill does not extract ocean or atmospheric water.')
 p.set('tags','roosterworks ground water ice drill mining harvesting h2o extractor')
 for n in p.children:
  if n.header=='MODEL':n.values=[(k,v.replace('rwm_drilllabel_minerals','rwm_drilllabel_water').replace('rwm_drillpaint_minerals','rwm_drillpaint_water')) for k,v in n.values]
  if n.get('name')=='ModuleResourceHarvester':
   for k,v in [('ResourceName','Water'),('ConverterName','Water Extraction'),('StartActionName','Start Water Drill'),('StopActionName','Stop Water Drill'),('ToggleActionName','Toggle Water Drill'),('Efficiency',format(efficiency,'.8g'))]:n.set(k,v)
  if n.header=='RESOURCE' and n.get('name')=='Minerals':n.set('name','Water');n.set('maxAmount',format(capacity,'.8g'))
 (GD/'Parts/RW_GND_DRILL_Water.cfg').write_text(dump(Node('ROOT',children=[p])),encoding='utf-8')
 color=(35,164,190);im=label('DRILL-H2O','WATER EXTRACTION');ImageDraw.Draw(im).rectangle((47,47,976,80),fill=color);im.save(GD/'Models/rwm_drilllabel_water.png',optimize=True)
 paint=Image.open(GD/'Models/rwm_white.png').convert('RGB');Image.blend(paint,Image.new('RGB',paint.size,color),.70).save(GD/'Models/rwm_drillpaint_water.png',optimize=True)
 cleanup=Node('@PART[RW_GND_DRILL_Water]:NEEDS[Kerbalism]:FINAL',children=[Node('!MODULE[Habitat],*')]+[Node('!RESOURCE['+s+'],*') for s in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')])
 (GD/'Compatibility/WaterDrill.cfg').write_text('// Crewless Water mining rig. Existing CRP maps only.\n'+dump(Node('ROOT',children=[cleanup])))
 spec={'id':'RW_GND_DRILL_Water','resource':'Water','code':'H2O','buffer_liters':250,'capacity_units':capacity,'efficiency':efficiency,'color':color,'map_records':len(maps)}
 (R/'Reports/DEV31_WATER_DRILL.json').write_text(json.dumps(spec,indent=2)+'\n')
 path=GD/'RoosterWorksGroundModules.version';v=json.loads(path.read_text());v['VERSION']['BUILD']=31;path.write_text(json.dumps(v,indent=2)+'\n')
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(sha(f)+'  '+f.relative_to(R).as_posix()+'\n' for f in sorted((R/'GameData').rglob('*')) if f.is_file()))
 print(f'PASS built Water drill; {len(maps)} positive crustal map records, {capacity:g} units, efficiency {efficiency:g}')
if __name__=='__main__':main()
