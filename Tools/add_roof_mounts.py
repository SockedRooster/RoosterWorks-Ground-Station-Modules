"""Append elbow-style black sockets beneath the 32 straight roof posts."""
from pathlib import Path
import sys,json,hashlib,math
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load
from native_derivatives import write
import build_hab250 as h
gd=R/'GameData/RoosterWorksGroundModules';data=json.loads((R/'Reports/ROOF_POST_FEET.json').read_text())
for role,info in data.items():
 path=gd/f'Models/RW_GND_{role}.mu';model=load(path)
 assert not any(n['name']=='RW_RoofRailMounts' for n in model.root['children']),'Use a clean pre-mount model when rebuilding'
 material=next(i for i,m in enumerate(model.materials) if model.textures[m['properties']['_MainTex']['index']]['name']=='rwm_graphite')
 mesh=h.Mesh();sockets=[]
 for post in info['posts']:
  x,foot,z=post['foot'];hull=math.sqrt(1.204**2-z*z);bottom=hull-.030;top=foot+.040
  assert top>hull+.02
  h.tube(mesh,(x,bottom,z),(x,hull+.025,z),r=.045,sides=16)
  h.tube(mesh,(x,hull-.005,z),(x,top,z),r=.034,sides=16)
  sockets.append(dict(center=[x,z],bottom=bottom,top=top,rail_foot=foot,hull=hull))
 node=dict(name='RW_RoofRailMounts',position=(0,0,0),rotation=(0,0,0,1),scale=(1,1,1),tag='Untagged',layer=0,children=[],mesh=dict(vertices=mesh.vertices,normals=mesh.normals,uvs=mesh.uvs,submeshes=[mesh.triangles]),materials=[material],shadows=(1,1))
 model.root['children'].append(node);write(model,path)
 report_path=R/f'Reports/RW_GND_{role}.json';report=json.loads(report_path.read_text());report['triangles']+=len(mesh.triangles);report['draw_calls']+=1;report['roof_rail_sockets']=sockets;report['native_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();report_path.write_text(json.dumps(report,indent=2)+'\n')
 print('Mounted four roof posts:',role,flush=True)
version=gd/'RoosterWorksGroundModules.version';v=json.loads(version.read_text());v['VERSION']['BUILD']=13;version.write_text(json.dumps(v,indent=2)+'\n')
files=sorted(p for p in (R/'GameData').rglob('*') if p.is_file());(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in files))
