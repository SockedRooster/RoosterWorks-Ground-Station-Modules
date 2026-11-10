from pathlib import Path
import sys,json,hashlib,copy
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v31';GD=R/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev5/Source'),str(R/'Tools'),str(W/'work/python-deps')]
from config_nodes import parse,dump
import dnfile
checks=0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(v,msg):
 global checks
 checks+=1
 assert v,msg
baseline=json.loads((R/'Reports/DEV32_BASELINE.json').read_text());changed=set()
for name,digest in baseline.items():
 check(sha(B/name)==digest,'baseline changed '+name)
 if sha(R/name)!=digest:changed.add(name)
check(changed=={'GameData/RoosterWorksGroundModules/'+n for n in ('RoosterWorksGroundModules.version','Parts/RW_GND_CMD.cfg','Plugins/RoosterWorksGroundDeploy.dll')},'unexpected changes '+str(changed))
added={p.relative_to(R).as_posix() for p in (R/'GameData').rglob('*') if p.is_file()}-set(baseline)
check(added=={'GameData/RoosterWorksGroundModules/Compatibility/ZZZZZZDrillSystemHeat.cfg'},'unexpected additions')
cmd=parse((GD/'Parts/RW_GND_CMD.cfg').read_text()).children[0];level=[n for n in cmd.children if n.get('name')=='ModuleRWGroundLevel'];check(len(level)==1,'one command leveling controller');cmd.children.remove(level[0])
check(dump(cmd)==dump(parse((B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_CMD.cfg').read_text()).children[0]),'command otherwise preserved')
for name in ('GroundTether.cs','GroundDocking.cs','EndWindowLink.cs','ExteriorLight.cs','PodRelease.cs','GroundLogisticsContents.cs'):
 check(sha(R/'Source'/name)==sha(B/'Source'/name),'unrelated source '+name)
game=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program')
assemblies={}
for file,wanted in [(game/'GameData/SystemHeat/Plugin/SystemHeat.dll',{'ModuleSystemHeat','ModuleSystemHeatHarvester'}),(game/'GameData/zKerbalismSystemHeat/Plugins/zKerbalismSystemHeat.dll',{'SystemHeatHarvesterKerbalism'})]:
 pe=dnfile.dnPE(str(file));types={str(t.TypeName):t for t in pe.net.mdtables.TypeDef};check(wanted<=types.keys(),'installed thermal types')
 assemblies[file.name]={'sha256':sha(file),'assembly_name':str(pe.net.mdtables.Assembly.rows[0].Name),'types':sorted(wanted)}
patch=parse((GD/'Compatibility/ZZZZZZDrillSystemHeat.cfg').read_text()).children
base=patch[0];bridge=patch[1]
check(base.header=='@PART[RW_GND_DRILL,RW_GND_DRILL_*]:NEEDS[SystemHeat]:FINAL','heat scope/guard/order')
heat=next(n for n in base.children if n.header=='MODULE');edit=next(n for n in base.children if n.header.startswith('@MODULE[*]'))
check(heat.get('name')=='ModuleSystemHeat' and heat.get('moduleID')=='RW_DrillHeat','heat loop module')
check(edit.get('%systemHeatModuleID')==heat.get('moduleID'),'heat linkage')
check(edit.get('@name')=='ModuleSystemHeatHarvester','thermal harvester')
check(any(n.header=='!MODULE[ModuleSystemHeat],*' for n in base.children),'removes generic duplicate loop')
for module in ('ModuleCoreHeat','ModuleOverheatDisplay'):
 check(any(n.header=='!MODULE['+module+'],*' for n in base.children),'no parallel stock heating '+module)
check(edit.get('%GeneratesHeat')=='false','stock heating off')
check({n.header for n in edit.children}>={'!TemperatureModifier','!ThermalEfficiency','!systemEfficiency'},'stock thermal curve cleanup')
curve=next(n for n in edit.children if n.header=='systemEfficiency');keys=[tuple(map(float,v.split())) for k,v in curve.values if k=='key'];check(keys==[(0,1),(400,1),(650,0)],'cold/warm/hot thermal behavior')
check(float(edit.get('%shutdownTemperature'))==650 and float(edit.get('%systemOutletTemperature'))==350,'shutdown/outlet')
check(':NEEDS[SystemHeat,zKerbalismSystemHeat,Kerbalism]:FINAL' in bridge.header,'bridge requirements')
check(next(n for n in bridge.children if n.header.startswith('@MODULE[ModuleSystemHeatHarvester]')).get('@name')=='SystemHeatHarvesterKerbalism','background bridge')
drills=[]
for f in sorted((GD/'Parts').glob('RW_GND_DRILL*.cfg')):
 p=parse(f.read_text()).children[0];h=next(n for n in p.children if n.get('name')=='ModuleResourceHarvester');power=float(next(n for n in h.children if n.header=='INPUT_RESOURCE' and n.get('ResourceName')=='ElectricCharge').get('Ratio'))
 check(power==float(edit.get('%systemPower'))==7.5,'all rigs equal heat per EC '+f.name)
 check(h.get('HarvesterType')=='0','crustal harvester selector matches '+f.name)
 check(h.get('ResourceName') not in ('ElectricCharge',''),'valid feedstock')
 drills.append({'id':p.get('name'),'resource':h.get('ResourceName'),'power_ec_s':power,'heat_kw':7.5,'coolant_volume_m3':float(heat.get('volume')),'shutdown_k':650})
check(len(drills)==10 and any(d['resource']=='Water' for d in drills),'all ten rigs including Water')
for file,phrase in [('v32-tube-tests.log','PASS 1833'),('v32-level-tests.log','PASS 4837'),('v32-compile.log','PASS compiled')]:check(phrase in (R/'Reports'/file).read_text(),'required runtime gate '+file)
for p in sorted((R/'GameData').rglob('*')):
 if p.is_file():check(p.stat().st_size>0,'nonempty '+str(p))
(R/'Reports/DEV32_HEAT_AUDIT.json').write_text(json.dumps({'installed_assemblies':assemblies,'drills':drills,'power_conversion_kw_per_ec_s':1,'live_modmanager_and_game_acceptance_pending':True},indent=2)+'\n')
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
check(len(list((GD/'Parts').glob('*.cfg')))==29,'parts');check(len(list((GD/'Models').glob('*.mu')))==20,'models')
print(f'PASS dev.32: {checks} preservation/configuration/installed thermal API checks; 10 drills, SystemHeat loop selector, 7.5 kW each; live KSP/ModuleManager acceptance pending')
