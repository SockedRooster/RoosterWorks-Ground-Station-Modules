import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];W=R.parent
p=W/'ground-modules-art-v4/Models/RW_GND_HUB.blend'
bpy.ops.wm.open_mainfile(filepath=str(p));c=next(c for c in bpy.data.collections if c.name.startswith('RW GROUND'))
out=[]
for o in c.objects:
 d={'name':o.name,'type':o.type,'position':list(o.location)}
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];d['bounds']=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
  d['materials']=[m.name for m in o.data.materials if m]
 out.append(d)
(R/'Reports/HUB_INVENTORY.json').write_text(json.dumps(out,indent=2))
