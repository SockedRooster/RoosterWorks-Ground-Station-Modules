"""Mirror accepted PWR accumulators; remove only the overlapping console."""
from pathlib import Path
import sys,copy,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v29';GD=R/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev10/Tools'),str(W/'rw-v075dev10/Source'),str(R/'Tools')]
from native_model import load,walk
from native_derivatives import write
from build_ring_options import components
from build_v18 import node

def selected(mesh,indices):
 out=copy.deepcopy(mesh);tri=[t for i,t in enumerate(mesh['submeshes'][0]) if i in indices];used=sorted({i for t in tri for i in t});remap={v:i for i,v in enumerate(used)}
 for k in ('vertices','normals','uvs','uv2','colors','tangents'):
  if k in out:out[k]=[out[k][i] for i in used]
 out['submeshes']=[[tuple(remap[i] for i in t) for t in tri]];return out

def main():
 protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev11') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV30_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
 model=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu');rows=json.loads((R/'Reports/LAYOUT_INVENTORY.json').read_text())['PWR']
 textures={'Graphite':'gnd_graphite','Steel':'gnd_steel','Copper':'gnd_copper','Ivory':'gnd_ivory','Screen':'gnd_screen','Warm glass':'gnd_warm_glass'}
 boxes=[]
 for row in rows:
  name=row['name'];kind='accumulator' if name.startswith(('External service accumulator','Accumulator strap','Service valve')) else 'console' if name in ('Service console enclosure','Service console face','Console screen','GND / AUX') or name.startswith('Status LED') else None
  if kind is None:continue
  lo,hi=row['lo'],row['hi'];minimum=np.array((lo[0],lo[2]-2.3,-hi[1]))-.00015;maximum=np.array((hi[0],hi[2]-2.3,-lo[1]))+.00015
  boxes.append((name,kind,textures[row['materials'][0]],minimum,maximum))
 mirror=node('RW_PWR_AccumulatorBank_Starboard',rot=(0,1,0,0));audit=[];counts={name:0 for name,_,_,_,_ in boxes}
 for _,n in list(walk(model.root)):
  if 'mesh' not in n or not n['name'].startswith('GND_RW_GroundHardware_'):continue
  mesh=n['mesh'];v=np.array(mesh['vertices']);tri=mesh['submeshes'][0];texture=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
  remove=set();copy_indices=set()
  for g in components(mesh):
   idx=sorted({i for t in g for i in tri[t]});p=v[idx]
   match=next(((name,kind) for name,kind,t,lo,hi in boxes if texture==t and np.all(p.min(0)>=lo) and np.all(p.max(0)<=hi)),None)
   if match is None:continue
   name,kind=match;counts[name]+=len(g)
   (remove if kind=='console' else copy_indices).update(g)
  if copy_indices:
   copied=node('RW_PWR_Mirrored_'+texture);copied.update(mesh=selected(mesh,copy_indices),materials=copy.deepcopy(n['materials']),shadows=n['shadows']);mirror['children'].append(copied)
  if remove:n['mesh']=selected(mesh,set(range(len(tri)))-remove)
  if remove or copy_indices:audit.append({'node':n['name'],'texture':texture,'removed_triangles':sorted(remove),'mirrored_triangles':sorted(copy_indices)})
 assert all(v>0 for v in counts.values()),counts
 assert len([k for k in counts if k.startswith('External service accumulator')])==3
 model.root['children']=[n for n in model.root['children'] if 'mesh' not in n or n['mesh']['vertices']]
 model.root['children'].append(mirror);write(model,GD/'Models/RW_GND_PWR.mu')
 (R/'Reports/DEV30_PWR_EQUIPMENT.json').write_text(json.dumps({'objects':counts,'mesh_changes':audit,'mirror_root':mirror['name'],'three_units_each_side':True,'console_removed':True},indent=2)+'\n')
 p=GD/'RoosterWorksGroundModules.version';v=json.loads(p.read_text());v['VERSION']['BUILD']=30;p.write_text(json.dumps(v,indent=2)+'\n')
 for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
 print('PASS mirrored all three existing PWR accumulators / six straps / three valves; removed only overlapping console, screen, LEDs and console lettering')

if __name__=='__main__':main()
