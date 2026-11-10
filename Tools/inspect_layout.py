import bpy,json,sys
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];W=R.parent;out={}
for role in ('HAB','LAB','CMD','AIR','HUB','GRN','TUB','ELB','LOG','PWR'):
 bpy.ops.wm.open_mainfile(filepath=str(W/f'ground-modules-art-v4/Models/RW_GND_{role}.blend'))
 coll=next(c for c in bpy.data.collections if c.name.startswith('RW GROUND'));rows=[]
 for o in coll.objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append(dict(name=o.name,lo=[min(v[i] for v in pts) for i in range(3)],hi=[max(v[i] for v in pts) for i in range(3)],materials=[m.name for m in o.data.materials if m]))
 out[role]=rows
(R/'Reports/LAYOUT_INVENTORY.json').write_text(json.dumps(out,indent=2))
