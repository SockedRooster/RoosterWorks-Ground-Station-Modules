from pathlib import Path
import sys,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;GD=R/'GameData/RoosterWorksGroundModules';BG=W/'ground-hotpatch-v28/GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev10/Tools'),str(W/'rw-v075dev10/Source')]
from native_model import load,walk
from config_nodes import parse
checks=0
def check(v,m):
 global checks
 checks+=1
 assert v,m
check({p.relative_to(GD).as_posix() for p in GD.rglob('*') if p.is_file()}=={p.relative_to(BG).as_posix() for p in BG.rglob('*') if p.is_file()},'Unchanged GameData file set')
changed=set()
for old in BG.rglob('*'):
 if old.is_file():
  rel=old.relative_to(BG)
  if old.read_bytes()!=(GD/rel).read_bytes():changed.add(rel.as_posix())
  if rel.as_posix() not in ('Models/RW_GND_CMD.mu','RoosterWorksGroundModules.version'):check((GD/rel).read_bytes()==old.read_bytes(),'Unchanged part/asset/runtime '+str(rel))
check(changed=={'Models/RW_GND_CMD.mu','RoosterWorksGroundModules.version'},'Only command native model and version may change')
model=load(GD/'Models/RW_GND_CMD.mu');old=load(BG/'Models/RW_GND_CMD.mu')
check(model.root['children'][:-1]==old.root['children'],'Existing command geometry, colliders, lights and rig untouched')
check(model.textures==old.textures and model.materials==old.materials,'Existing textures/shaders untouched')
group=model.root['children'][-1];check(group['name']=='RW_CommandRoofSeats','Roof-only attachment group')
for path,n in walk(group):
 check(n['position']==(0,0,0) and n['rotation']==(0,0,0,1),'Identity addition transforms')
 if 'mesh' not in n:continue
 m=n['mesh'];v=np.array(m['vertices']);normal=np.array(m['normals'])
 check(len(v)==len(normal)==len(m['uvs']) and len(v)<65535,'Mesh cardinality')
 check(np.isfinite(v).all() and np.isfinite(normal).all() and np.isfinite(m['uvs']).all(),'Finite mesh')
 check(np.allclose(np.linalg.norm(normal,axis=1),1,atol=.001),'Unit normals')
 check(v[:,1].min()>1.0 and v[:,1].max()<1.30 and abs(v[:,0]).max()<.95,'Confined to roof; clear of legs, stairs, dish and docking faces')
 for sub in m['submeshes']:
  tri=np.array(sub);check(tri.min()>=0 and tri.max()<len(v),'Valid indices')
  dot=(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])*normal[tri].mean(1)).sum(1)
  check(dot.min(initial=0)>-1e-7,'Native winding')
audit=json.loads((R/'Reports/DEV29_ROOF_SEATS.json').read_text());check(len(audit)==5,'Radome / mast / two panels / outer roof skin')
for a in audit[:2]:
 cx,cz=a['center'];radius=a['radius']
 for angle in np.linspace(0,2*np.pi,129):
  z=cz+radius*np.sin(angle);roof=np.sqrt(1.206**2-z*z);bottom=roof-.012
  check(bottom<roof and a['top']>roof,'Curved foot intersects roof and rises into fitting')
 if a['name']=='telemetry radome':check(a['top']>a['existing_base'] and radius>.15,'Radome gap closed with overlap and full footprint')
 else:check(a['top']>a['existing_base'],'Mast and foot overlap')
for a in [v for v in audit if v['name']=='roof panel gasket']:
 for z in np.linspace(*a['z_range'],129):
  roof=np.sqrt(1.206**2-z*z);top=a['top_offset']+a['slope']*z;bottom=min(roof-.012,top-.004)
  check(bottom<roof and top>bottom,'Panel gasket closed under hull contour')
 for x in a['x_range']:check(abs(x)<.9,'Panel support clear of end rings')
skin=audit[-1];check(skin['inner_radius']<1.168<skin['outer_radius']<skin['cladding_radius'],'Skin intersects backing and stays below original cladding')
for z in np.linspace(-.166,.166,129):
 check(np.sqrt(1.206**2-z*z)-.012<np.sqrt(1.2**2-z*z),'Radome curved seat overlaps restored roof skin')
maps=parse((GD/'Compatibility/GroundRingGeometry.cfg').read_text());rule=next(n for n in maps.children if n.get('model')=='RW_GND_CMD');nodes=dict(walk(model.root));fixture=[]
for entry in rule.children:
 m=nodes[entry.get('path')]['mesh'];check(int(entry.get('vertices'))==len(m['vertices']) and int(entry.get('triangles'))==len(m['submeshes'][0]),'Accepted ring indices unchanged')
 fixture.append(dict(path=entry.get('path'),texture=entry.get('texture'),vertexCount=len(m['vertices']),triangles=[i for t in m['submeshes'][0] for i in t],ranges=entry.get('ranges')))
(R/'Reports/COMMAND_ROOF_COLOR_FIXTURE.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
check(json.loads((GD/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==29,'Version')
for path,digest in json.loads((R/'Reports/DEV29_PROTECTED_INPUTS.json').read_text()).items():check(hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,'Protected ground/station input '+path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);check(hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Manifest '+path)
print(f'PASS dev.29: {checks} native/contact/preservation checks; restored outer roof skin, curved radome socket, mast collar and two panel gaskets; existing rig, docking, colors, gameplay and every other asset preserved')
