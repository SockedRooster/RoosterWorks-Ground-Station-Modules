"""Retain all nuclear/clearance checks, then verify additive seated mounts."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
source=(R/'Tools/validate_v26.py').read_text().replace("==26,'Version'","==27,'Version'").replace('DEV26_BOUNDS.json','DEV27_BOUNDS.json').replace('PASS dev.26:', 'PASS dev.27 baseline:')
source=source.replace("old['name'].startswith('RW_HullMount_equipment_starboard')", "old['name'].startswith('RW_HullMount_equipment_')")
source=source.replace("added={'Compatibility/NuclearIndustry.cfg','Resources/NuclearFeedstock.cfg'}", "added={'Compatibility/NuclearIndustry.cfg','Resources/NuclearFeedstock.cfg','Compatibility/ZZZZZGroundIndustryCategories.cfg'}")
exec(compile(source,str(R/'Tools/validate_v26.py'),'exec'))
before=checks
base=W/'ground-hotpatch-v26/GameData/RoosterWorksGroundModules'
allowed={'RoosterWorksGroundModules.version'}|{folder+'/RW_GND_'+role+ext for role in ('NST','NSM','CEN') for folder,ext in [('Models','.mu'),('Parts','.cfg')]}
for old in base.rglob('*'):
 if old.is_file():
  rel=old.relative_to(base)
  if rel.as_posix() not in allowed:check((GD/rel).read_bytes()==old.read_bytes(),'Dev.26 gameplay/asset changed '+str(rel))
for role in ('NST','NSM','CEN'):
 ID='RW_GND_'+role;m=load(GD/f'Models/{ID}.mu');old=load(base/f'Models/{ID}.mu')
 retained=[n for n in old.root['children'] if not n['name'].startswith('RW_HullMount_equipment_port')]
 check(m.root['children'][:len(retained)]==retained,'Existing native geometry changed')
 p=parse((GD/f'Parts/{ID}.cfg').read_text()).children[0];previous=parse((base/f'Parts/{ID}.cfg').read_text()).children[0]
 previous.values=[(k,v) for k,v in previous.values if not k.startswith('node_stack_equipment_port')]
 price=json.loads((R/'Reports/DEV27_COSTS.json').read_text())[ID]
 previous.set('cost',format(price['configured_full_price'],'.10g'))
 for organizer in previous.children:
  if organizer.header.startswith('VABORGANIZER'):organizer.set('organizerSubcategory','crewUtility')
 check(p==previous,'Only occupied equipment pad nodes and full-tank price may change')
 tanks=[n for n in p.children if n.header=='RESOURCE'];capacity_cost=sum(float(n.get('maxAmount'))*price['unit_costs'][n.get('name')] for n in tanks)
 actual_cost=sum(float(n.get('amount'))*price['unit_costs'][n.get('name')] for n in tanks)
 check(float(p.get('cost'))-capacity_cost+actual_cost==price['dry_price'],'Correct initial VAB price')
 for fraction in (0,.25,.5,.75,1):check(float(p.get('cost'))-capacity_cost+fraction*capacity_cost>=price['dry_price']>0,'Positive partially/full-loaded price')
 check(m.materials==old.materials and m.textures==old.textures,'Accepted materials/textures changed')
 groups={n['name']:n for n in m.root['children']};group=groups['RW_'+role+'_HullSaddle']
 for original in (groups['RW_'+role+'_Industry'],group):
  expected=copy.deepcopy(original);expected['name']+='_Port';expected['rotation']=(0.,1.,0.,0.)
  def suffix(n):
   for child in n['children']:child['name']+='_Port';suffix(child)
  suffix(expected);check(groups[original['name']+'_Port']==expected,'Exact opposite-side equipment/mount symmetry')
 mesh=group['children'][0]['mesh'];v=np.array(mesh['vertices'])
 # Every curved-hull contact slice embeds its rear edge in the hull; the
 # outboard face enters the existing rack backplate, so neither end floats.
 for y in np.unique(v[:,1]):
  section=v[np.isclose(v[:,1],y,atol=1e-7)];inner=section[:,2].max();outer=section[:,2].min()
  check(inner>-np.sqrt(1.204**2-y*y)+.025,'Curved saddle fails to contact hull')
  check(-1.34<outer<-1.16,'Saddle fails to overlap rack backing')
 for progress in np.linspace(0,1,21):
  for n,mt in world_nodes(m,float(progress)):
   if 'mesh' not in n or not ('Leg' in n['name'] or 'Ram' in n['name']):continue
   lv=np.array(n['mesh']['vertices'])@mt[:3,:3].T+mt[:3,3]
   worlds=matrices(m.root)
   mounts=[mount for g in (group,groups[group['name']+'_Port'],groups['RW_'+role+'_Industry'],groups['RW_'+role+'_Industry_Port']) for _,mount in walk(g)]
   for mount in mounts:
    if 'mesh' not in mount:continue
    transform=worlds[id(mount)];mv=np.array(mount['mesh']['vertices'])@transform[:3,:3].T+transform[:3,3]
    # Test each closed curved slice separately. A single bounding box for
    # the whole saddle includes empty space below its inward-curving top.
    sections=[mv[i:i+24] for i in range(0,len(mv),24)] if 'rwm_graphite' in mount['name'] else [mv]
    for section in sections:
     overlap=np.minimum(lv.max(0),section.max(0))-np.maximum(lv.min(0),section.min(0))
     check(not np.all(overlap>1e-5),'Mount clips retracting leg')
for path,digest in json.loads((R/'Reports/DEV27_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Dev.26/core preservation '+path)
catalogue=parse((GD/'Compatibility/ZZZZZGroundIndustryCategories.cfg').read_text()).children
check(len(catalogue)==2,'Only requested catalogue overrides')
for rule,ids,subcategory in zip(catalogue,('RW_GND_DRILL,RW_GND_DRILL_*','RW_GND_NST,RW_GND_CEN,RW_GND_NSM'),('resources','crewUtility')):
 check(rule.header=='@PART['+ids+']:NEEDS[VABOrganizer]:FINAL','Scoped final catalogue selection')
 check(rule.get('%category')=='Utility','Utility parent category')
 check(rule.children[0].header=='!VABORGANIZER,*' and rule.children[1].get('organizerSubcategory')==subcategory,'Single correct subcategory')
print(f'PASS dev.27 mounts: {checks-before} additional checks; matching equipment on both sides; curved saddles embedded in hull and rack backing; bolted cheeks; 21-pose bilateral leg clearance; corrected positive empty/full prices; scoped native models, pad nodes, prices and version changes')
