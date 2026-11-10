"""Narrow native edits against accepted dev.14; model hierarchy stays intact."""
from pathlib import Path
import sys,math,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v14'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load,walk
from native_derivatives import write
from build_ring_options import components
GD=R/'GameData/RoosterWorksGroundModules';audit={}
for role in ('PWR','ELB'):
 ID='RW_GND_'+role;model=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu');changed=[]
 for path,n in walk(model.root):
  if 'mesh' not in n:continue
  mesh=n['mesh'];texture=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
  if role=='ELB' and texture=='rwm_crest':
   mesh['uvs']=[(v,1-u) for u,v in mesh['uvs']];changed.append({'path':path,'rotation_clockwise_degrees':270,'vertices':len(mesh['vertices'])})
  if role=='PWR' and texture in ('rwm_pwrlabel','rwm_bronze','rwm_graphite'):
   vertices=np.array(mesh['vertices']);triangles=mesh['submeshes'][0]
   for group in components(mesh):
    indices=sorted({i for t in group for i in triangles[t]});p=vertices[indices];lo=p.min(0);hi=p.max(0)
    if max(abs(lo[0]),abs(hi[0]))<.6 and max(abs(lo[1]),abs(hi[1]))<.25 and hi[2]<-1.22:
     angle=math.radians(-35);c=math.cos(angle);s=math.sin(angle);rotation=np.array(((1,0,0),(0,c,-s),(0,s,c)))
     for i in indices:
      mesh['vertices'][i]=tuple(rotation@np.array(mesh['vertices'][i]));mesh['normals'][i]=tuple(rotation@np.array(mesh['normals'][i]))
     changed.append({'path':path,'material':texture,'vertices':len(indices),'rotation_down_degrees':35})
 assert len(changed)==(3 if role=='PWR' else 1),changed
 write(model,GD/f'Models/{ID}.mu');audit[role]=changed
 report_path=R/f'Reports/{ID}.json';report=json.loads(report_path.read_text());report['badge_refinement']=changed;report['native_sha256']=hashlib.sha256((GD/f'Models/{ID}.mu').read_bytes()).hexdigest();report_path.write_text(json.dumps(report,indent=2)+'\n')
 print('PASS preserved original mesh topology/rig/collision and refined badges:',role,flush=True)
(R/'Reports/BADGE_REFINEMENTS.json').write_text(json.dumps(audit,indent=2)+'\n')
