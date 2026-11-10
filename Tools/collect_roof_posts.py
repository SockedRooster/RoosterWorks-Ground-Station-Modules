"""Read true roof-post feet from protected artist meshes; never save inputs."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;result={}
for role in ('HAB','LAB','CMD','LOG','GRN','AIR','PWR','TUB'):
 path=W/f'ground-modules-art-v4/Models/RW_GND_{role}.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
 asset=next(c for c in bpy.data.collections if c.name.startswith('RW GROUND'));posts=[]
 for obj in asset.objects:
  if not obj.name.startswith('Roof maintenance rail'):continue
  points=[obj.matrix_world@v.co for v in obj.data.vertices]
  points=[(p.x,p.z-2.3,-p.y) for p in points];low=min(p[1] for p in points)
  feet=[p for p in points if abs(p[1]-low)<.001]
  for side in (-1,1):
   group=[p for p in feet if p[0]*side>0];assert group
   center=[(min(p[k] for p in group)+max(p[k] for p in group))/2 for k in range(3)]
   posts.append(dict(rail=obj.name,foot=center))
 assert len(posts)==4,(role,posts)
 result[role]=dict(posts=posts,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(R/'Reports/ROOF_POST_FEET.json').write_text(json.dumps(result,indent=2)+'\n')
print('Located all 32 roof posts from protected source geometry')
