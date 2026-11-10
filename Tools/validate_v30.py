from pathlib import Path
import sys,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;GD=R/'GameData/RoosterWorksGroundModules';BG=W/'ground-hotpatch-v29/GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev10/Tools'),str(W/'rw-v075dev10/Source'),str(R/'Tools')]
from native_model import load,walk
from config_nodes import parse
from build_v30 import selected
checks=0
def check(v,m):
 global checks
 checks+=1
 assert v,m
check({p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file()}=={p.relative_to(BG).as_posix() for p in BG.rglob('*') if p.is_file()},'Same GameData file set')
changed=set()
for old in BG.rglob('*'):
 if old.is_file():
  rel=old.relative_to(BG)
  if (GD/rel).read_bytes()!=old.read_bytes():changed.add(rel.as_posix())
  if rel.as_posix() not in ('Models/RW_GND_PWR.mu','RoosterWorksGroundModules.version'):check((GD/rel).read_bytes()==old.read_bytes(),'Preserved unrelated asset '+str(rel))
check(changed=={'Models/RW_GND_PWR.mu','RoosterWorksGroundModules.version'},'Scoped PWR model/version only')
model=load(GD/'Models/RW_GND_PWR.mu');base=load(BG/'Models/RW_GND_PWR.mu');named={n['name']:n for _,n in walk(model.root)};before={n['name']:n for _,n in walk(base.root)}
report=json.loads((R/'Reports/DEV30_PWR_EQUIPMENT.json').read_text());diff={s['node']:s for s in report['mesh_changes']}
check(model.materials==base.materials and model.textures==base.textures,'Materials / textures preserved')
for old in base.root['children']:
 name=old['name'];remove=diff.get(name,{}).get('removed_triangles',[])
 if remove:
  expected=selected(old['mesh'],set(range(len(old['mesh']['submeshes'][0])))-set(remove))
  if expected['vertices']:
   check(named[name]['mesh']==expected,'Only console triangles removed '+name)
  else:check(name not in named,'Empty batch removed cleanly')
 else:check(named[name]==old,'Unrelated hull/legs/pipes/rails/lighting/docks unchanged '+name)
mirror=named[report['mirror_root']];check(mirror['rotation']==(0,1,0,0),'Proper 180 degree opposite-side transform')
check(mirror['position']==(0,0,0) and mirror['scale']==(1,1,1),'No source scale/offset change')
for spec in report['mesh_changes']:
 if not spec['mirrored_triangles']:continue
 source=before[spec['node']]['mesh'];copy=named['RW_PWR_Mirrored_'+spec['texture']]['mesh']
 check(copy==selected(source,set(spec['mirrored_triangles'])),'Exact original bank copied '+spec['texture'])
 v=np.array(copy['vertices']);check(v[:,2].min()>1.12 and v[:,2].max()<1.46,'Only side accumulator geometry selected')
 check(abs(v[:,0]).max()<.82,'Clear of end mounting pads and docking planes')
 # Opposite bank ends at y=-.39; the back plaque starts below y=-.57.
 check(v[:,1].min()>-.40 and v[:,1].max()<.49,'Mirrored bank clears lower logo / service pipes')
for path,n in walk(model.root):
 if 'mesh' not in n or (n['name'] not in diff and not n['name'].startswith('RW_PWR_Mirrored_')):continue
 m=n['mesh'];v=np.array(m['vertices']);norm=np.array(m['normals'])
 check(len(v)==len(norm)==len(m['uvs']) and len(v)<65535,'Native cardinality')
 check(np.isfinite(v).all() and np.isfinite(norm).all() and np.isfinite(m['uvs']).all(),'Finite geometry')
 check(np.allclose(np.linalg.norm(norm,axis=1),1,atol=.001),'Unit normals')
 for sub in m['submeshes']:
  tri=np.array(sub);check(tri.min()>=0 and tri.max()<len(v),'Valid triangles')
  dot=(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])*norm[tri].mean(1)).sum(1);check(dot.min(initial=0)>-1e-7,'Native winding')
check(len([s for s in report['objects'] if s.startswith('External service accumulator')])==3,'Three accumulators per bank')
check(all(v>0 for v in report['objects'].values()),'All accumulator/console objects accounted for')
rule=next(n for n in parse((GD/'Compatibility/GroundRingGeometry.cfg').read_text()).children if n.get('model')=='RW_GND_PWR');nodes=dict(walk(model.root));fixture=[]
for e in rule.children:
 m=nodes[e.get('path')]['mesh'];check(int(e.get('vertices'))==len(m['vertices']) and int(e.get('triangles'))==len(m['submeshes'][0]),'Original ring geometry/map counts')
 fixture.append(dict(path=e.get('path'),texture=e.get('texture'),vertexCount=len(m['vertices']),triangles=[i for t in m['submeshes'][0] for i in t],ranges=e.get('ranges')))
(R/'Reports/POWER_SIDE_COLOR_FIXTURE.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==30,'Version')
for path,digest in json.loads((R/'Reports/DEV30_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected input '+path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
print(f'PASS dev.30: {checks} native/selection/preservation checks; exact three-unit bank mirrored; console and its screen/LEDs/lettering removed; PWR gameplay, rigs, ring maps and all unrelated assets unchanged')
