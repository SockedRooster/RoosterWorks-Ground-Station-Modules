"""Dev.19: remove RCS, runtime lighting/tube repairs, end-for-end cap and VT-90."""
from pathlib import Path
import sys,json,copy,math,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v18'
if (R/'Source/BaselineDev18').exists():OLD=R/'Source/BaselineDev18'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import parse,dump,Node
GD=R/'GameData/RoosterWorksGroundModules';M=np.diag([-1.,1.,-1.]);audit={}
def qmul(a,b):
 ax,ay,az,aw=a;bx,by,bz,bw=b
 return (aw*bx+ax*bw+ay*bz-az*by,aw*by-ax*bz+ay*bw+az*bx,aw*bz+ax*by-ay*bx+az*bw,aw*bw-ax*bx-ay*by-az*bz)
def turn(mesh):
 for key in ('vertices','normals'):mesh[key]=[tuple(M@np.array(v)) for v in mesh[key]]
def vector(text):
 values=[float(v.strip()) for v in text.split(',')];values[:3]=M@np.array(values[:3])
 if len(values)>=6:values[3:6]=M@np.array(values[3:6])
 return ', '.join(format(v,'.9g') for v in values)
for path in sorted((OLD/'GameData/RoosterWorksGroundModules/Parts').glob('*.cfg')):
 root=parse(path.read_text(encoding='utf-8'));p=root.children[0];ID=p.get('name');model=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu')
 removed=[]
 def strip(n):
  for c in list(n['children']):
   if c['name'].startswith('RW_RCSCluster_'):removed.append(c['name']);n['children'].remove(c)
   else:strip(c)
 strip(model.root)
 p.children=[n for n in p.children if n.get('name')!='ModuleRCSFX']
 for effects in p.children:
  if effects.header=='EFFECTS':effects.children=[n for n in effects.children if n.header!='rcs']
 p.children=[n for n in p.children if n.header!='EFFECTS' or n.children]
 report=json.loads((OLD/f'Reports/{ID}.json').read_text());info=dict(removed_rcs_clusters=len(removed))
 if ID!='RW_GND_VT':
  p.set('mass',format(float(p.get('mass'))-.04,'.6g'));p.set('cost',str(int(p.get('cost'))-480))
  desc=p.get('description').split(' Integrated upper/lower RCS clusters')[0];p.set('description',desc)
 if ID=='RW_GND_HAB':
  count=0
  for _,n in walk(model.root):
   if 'mesh' in n and not n['name'].startswith('RW_EndFaceBadges') and any(model.textures[model.materials[i]['properties']['_MainTex']['index']]['name']=='rwm_crest' for i in n.get('materials',[])):
    n['mesh']['uvs']=[(1-u,1-v) for u,v in n['mesh']['uvs']];count+=len(n['mesh']['uvs'])
  info['hab_badge_vertices_turned_180']=count
 if ID in ('RW_GND_HAB','RW_GND_CMD','RW_GND_AIR'):
  spot=next(n for _,n in walk(model.root) if n['name']=='RW_DoorSpot');spot['light'].update(intensity=4,range=10,spotAngle=100)
  light=next(n for n in p.children if n.get('name')=='ModuleRWExteriorLight')
  light.values=[('name','ModuleRWExteriorLight'),('lightName','RW_DoorSpot'),('lightMeshRendererName','RW_DoorLightLens'),('resourceAmount','.03'),('isOn','false'),('followCabinLights','true')]
  info['light']='explicit ForcePixel spot / cabin linked by default / 0.03 EC/s'
 if ID=='RW_GND_END_250_125':
  Q=(0,1,0,0);I=(0,-1,0,0)
  for _,n in walk(model.root):
   n['position']=tuple(M@np.array(n['position']));n['rotation']=qmul(qmul(Q,n['rotation']),I)
   if 'mesh' in n:turn(n['mesh'])
   if 'collider' in n:
    c=n['collider']
    if c['type']=='mesh':turn(c['mesh'])
    else:c['center']=tuple(M@np.array(c['center']))
   if n['name'].startswith('RW_Dock_'):n['rotation']=qmul(n['rotation'],Q)
  for k,v in list(p.values):
   if k.startswith('node_stack_'):p.set(k,vector(v[:]))
  for mod in p.children:
   if mod.get('name')=='ModuleRWGroundDeploy':
    for binding in mod.children:
     for key in ('position','retractPosition','retractEuler'):
      if binding.get(key):binding.set(key,vector(binding.get(key)))
  for binding in report.get('motion',[]):
   for key in ('position','retractPosition','retractEuler'):
    if key in binding:binding[key]=(M@np.array(binding[key])).tolist()
  info['endcap_rotation']='180 degrees about upright Y; large structural rear and small docking nose turn together'
 if ID=='RW_GND_VT':
  p.set('title','RoosterWorks VT-90 — Detachable Vertical Thrust Pod')
  p.set('description','Detachable surface-mounted 90 kN vertical lift pod. 180 LiquidFuel / 220 Oxidizer, no monopropellant. 0.60 t dry / 2.60 t fueled; 320 s vacuum / 260 s sea-level Isp. Fit balanced pairs, nozzles down and clear of stairs/legs. Decouple Thrust Pod shuts its engine down and releases the complete pod and mounting bracket; no hardware is left on the base. Surface attach only. Release ground tether before flight. No docking ports or command module.')
  p.set('attachRules','0,1,0,1,0');p.values=[(k,v) for k,v in p.values if k!='node_stack_mount']
  p.children=[n for n in p.children if not(n.header=='RESOURCE' and n.get('name')=='MonoPropellant')]
  for n in p.children:
   if n.get('name')=='ModuleEnginesFX':n.set('maxThrust','90')
   if n.header=='RESOURCE':
    for key in ('amount','maxAmount'):n.set(key,str(int(n.get(key))*2))
  p.children.append(Node('MODULE',[('name','ModuleDecouple'),('explosiveNodeID','srf'),('ejectionForce','4'),('isOmniDecoupler','false'),('automaticDir','false'),('explosiveDir','0, 0, 1'),('stagingEnabled','false'),('stagingToggleEnabledEditor','false'),('stagingToggleEnabledFlight','false')]))
  p.children.append(Node('MODULE',[('name','ModuleRWPodRelease')]))
  # New model labeling, same part/model IDs for compatibility.
  from appearance_textures import label
  label('VT-90','VERTICAL THRUST').save(GD/'Models/rwm_vtlabel.png')
  info.update(thrust_kn=90,dry_mass_t=.6,wet_mass_t=2.6,fuel=180,oxidizer=220,monopropellant=0,decoupler='whole pod / surface node / outward impulse / engine shutdown')
 write(model,GD/f'Models/{ID}.mu');(GD/'Parts'/path.name).write_text(dump(root),encoding='utf-8')
 report['dev19_changes']=info;report['triangles']=sum(len(s) for _,n in walk(model.root) if 'mesh' in n for s in n['mesh']['submeshes']);report['native_sha256']=hashlib.sha256((GD/f'Models/{ID}.mu').read_bytes()).hexdigest();(R/f'Reports/{ID}.json').write_text(json.dumps(report,indent=2)+'\n');audit[ID]=info
 print('Built',ID,info,flush=True)
version=GD/'RoosterWorksGroundModules.version';v=json.loads(version.read_text());v['VERSION']['BUILD']=19;version.write_text(json.dumps(v,indent=2)+'\n')
(R/'Reports/DEV19_CHANGES.json').write_text(json.dumps(audit,indent=2)+'\n')
