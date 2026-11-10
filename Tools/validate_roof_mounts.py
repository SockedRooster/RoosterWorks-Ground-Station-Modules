from pathlib import Path
import sys,json,hashlib,numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;OLD=W/'ground-hotpatch-v12';CORE=W/'rw-v075dev5'
sys.path.insert(0,str(CORE/'Tools'))
from native_model import load,walk
gd=R/'GameData/RoosterWorksGroundModules';old=OLD/'GameData/RoosterWorksGroundModules'
posts=json.loads((R/'Reports/ROOF_POST_FEET.json').read_text());count=0
for role,info in posts.items():
 path=gd/f'Models/RW_GND_{role}.mu';m=load(path);baseline=load(old/'Models'/path.name)
 mounts=[n for n in m.root['children'] if n['name']=='RW_RoofRailMounts'];assert len(mounts)==1;mount=mounts[0]
 m.root['children'].remove(mount);assert m.root==baseline.root and m.materials==baseline.materials and m.textures==baseline.textures,role
 material=m.materials[mount['materials'][0]];assert m.textures[material['properties']['_MainTex']['index']]['name']=='rwm_graphite'
 v=np.array(mount['mesh']['vertices']);n=np.array(mount['mesh']['normals']);t=np.array(mount['mesh']['submeshes'][0]);assert np.isfinite(v).all() and np.allclose(np.linalg.norm(n,axis=1),1,atol=2e-5)
 assert np.all((np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])*n[t].mean(1)).sum(1)>-1e-6)
 report=json.loads((R/f'Reports/RW_GND_{role}.json').read_text());assert len(report['roof_rail_sockets'])==len(info['posts'])==4
 for post,socket in zip(info['posts'],report['roof_rail_sockets']):
  x,y,z=post['foot'];assert np.allclose(socket['center'],(x,z))
  assert socket['bottom']<socket['hull']-.02 and socket['top']>y+.03
  vertices=v[(abs(v[:,0]-x)<.05)&(abs(v[:,2]-z)<.05)];assert len(vertices)>0
  assert vertices[:,1].min()<socket['hull']-.02 and vertices[:,1].max()>y+.03
  # The wider shoe penetrates the hull even at its outside transverse edge.
  surface_at_edge=np.sqrt(1.204**2-(abs(z)+.045)**2);assert socket['bottom']<surface_at_edge
  count+=1
 assert info['source_sha256']==hashlib.sha256((W/f'ground-modules-art-v4/Models/RW_GND_{role}.blend').read_bytes()).hexdigest()
 print('PASS',role,'four black sockets overlap the real source post feet and curved hull; original model nodes/materials unchanged',flush=True)
assert count==32
for p in old.rglob('*'):
 if not p.is_file():continue
 name=p.relative_to(old).as_posix()
 if name in {'Models/RW_GND_'+role+'.mu' for role in posts}|{'RoosterWorksGroundModules.version'}:continue
 assert p.read_bytes()==(gd/name).read_bytes(),name
assert json.loads((gd/'RoosterWorksGroundModules.version').read_text())['VERSION']['BUILD']==13
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
print('PASS all 32 post connections; all part configs, runtime, docking, lighting, elbow, hub, endcap, palettes and input kits preserved')
