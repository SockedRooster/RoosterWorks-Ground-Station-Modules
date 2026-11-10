from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v21';GD=R/'GameData/RoosterWorksGroundModules';BG=B/'GameData/RoosterWorksGroundModules'
sys.path.insert(0,str(W/'rw-v075dev5/Source'))
from config_nodes import parse
allowed={'Compatibility/LogisticsLoadouts.cfg','Compatibility/LogisticsKerbalism.cfg','Compatibility/ZZZZGroundUtilityNoHabitat.cfg','Plugins/RoosterWorksGroundDeploy.dll','RoosterWorksGroundModules.version'}
changed=[]
for f in GD.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(GD).as_posix();old=BG/rel
 if not old.exists() or f.read_bytes()!=old.read_bytes():changed.append(rel);assert rel in allowed,rel
assert set(changed)==allowed
assert {f.relative_to(BG) for f in BG.rglob('*') if f.is_file()} <= {f.relative_to(GD) for f in GD.rglob('*') if f.is_file()}
for name in ('GroundDeploy','GroundDocking','GroundTether','EndWindowLink','CollapsibleTube','ExteriorLight','PodRelease'):
 assert (R/f'Source/{name}.cs').read_bytes()==(B/f'Source/{name}.cs').read_bytes()
root=parse((GD/'Compatibility/LogisticsLoadouts.cfg').read_text());patch,profiles=root.children
assert 'RW_GND_LOG' in patch.header and patch.children[0].get('name')=='ModuleRWGroundLogisticsContents'
assert profiles.get('name')=='RW_GND_LOG'
choices={n.get('name'):n for n in profiles.children};assert len(choices)==10
expected={'Food':1800,'Water':1700,'Oxygen':350000,'Nitrogen':200000,'Ammonia':40000,'CarbonDioxide':75000,'Hydrogen':750000}
for n,cap in expected.items():
 c=choices['Carbon Dioxide' if n=='CarbonDioxide' else n];assert len(c.children)==1
 r=c.children[0];assert r.get('name')==n and float(r.get('amount'))==float(r.get('maxAmount'))==cap
mixed={r.get('name'):float(r.get('maxAmount')) for r in choices['Mixed supplies'].children}
assert set(mixed)==set(expected)
assert abs(sum(mixed[n]/expected[n] for n in expected)-1)<1e-8
assert abs(sum(mixed[n]/expected[n] for n in ('Food','Water','Oxygen'))-.6)<1e-8
for n in ('Waste','WasteWater'):assert choices[n].children[0].get('amount')=='0' and choices[n].children[0].get('maxAmount')=='520'
report=json.loads((R/'Reports/LOG_CAPACITIES.json').read_text())
assert report['loadouts']=={c.get('name'):[dict(n.values) for n in c.children] for c in profiles.children}
fallback=parse((GD/'Compatibility/LogisticsKerbalism.cfg').read_text());assert len(fallback.children)==1
for n in fallback.children[0].children:
 if n.header.startswith('%RESOURCE'):
  assert float(n.get('%amount'))==float(n.get('%maxAmount'))==mixed[n.get('%name')]
cleanup=parse((GD/'Compatibility/ZZZZGroundUtilityNoHabitat.cfg').read_text())
for part in ('RW_GND_LOG','RW_GND_PWR'):
 rule=next(n for n in cleanup.children if n.header=='@PART['+part+']:NEEDS[Kerbalism]:FINAL')
 headers={n.header for n in rule.children}
 assert headers=={'!MODULE[Habitat],*','!MODULE[Sensor]:HAS[#type[habitat_radiation]]'}|{'!RESOURCE['+n+'],*' for n in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')}
assert len(list((GD/'Models').glob('*.mu')))==13
assert json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==22
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
print('PASS dev.22: seven exact dedicated capacities; 60% priority mixed allocation; ten selectable loadouts including CO2/H2; fallback consistent; scoped LOG/PWR habitat/shielding deletion; all thirteen models and seven prior controllers unchanged; protected inputs and manifest')
