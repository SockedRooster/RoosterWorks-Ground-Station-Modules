from pathlib import Path
import sys,json,copy,math,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v19'
if (R/'Source/BaselineDev19').exists():OLD=R/'Source/BaselineDev19'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
from build_ring_options import components,circular,ranges,SURFACES
from build_adp250375 import collision_section
import build_hab250 as h
from build_v18 import node,box,cylinder,meshnode,add_door_light
GD=R/'GameData/RoosterWorksGroundModules';audit={}
def finish(model,p,root,report):
 ID=model.name;write(model,GD/f'Models/{ID}.mu');(GD/f'Parts/{ID}.cfg').write_text(dump(root),encoding='utf-8');report['triangles']=sum(len(s) for _,n in walk(model.root) if 'mesh' in n for s in n['mesh']['submeshes']);report['dev20_changes']=audit[ID];report['native_sha256']=hashlib.sha256((GD/f'Models/{ID}.mu').read_bytes()).hexdigest();(R/f'Reports/{ID}.json').write_text(json.dumps(report,indent=2)+'\n')
def read(role):
 ID='RW_GND_'+role;model=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu');root=parse((OLD/f'GameData/RoosterWorksGroundModules/Parts/{ID}.cfg').read_text(encoding='utf-8'));report=json.loads((OLD/f'Reports/{ID}.json').read_text());return model,root.children[0],root,report
def neck(model):
 spot=next(n for _,n in walk(model.root) if n['name']=='RW_DoorSpot');m=h.Mesh();box(m,(spot['position'][0],.89,1.51),(.26,.14,.18));meshnode(model,model.root,'RW_DoorLightNeck','rwm_graphite',m)
def light(role):
 model,p,root,report=read(role)
 if role=='LAB':
  add_door_light(model,p);entry=p.children[-1];template=parse((OLD/'GameData/RoosterWorksGroundModules/Parts/RW_GND_HAB.cfg').read_text(encoding='utf-8')).children[0];entry.values=copy.deepcopy(next(n for n in template.children if n.get('name')=='ModuleRWExteriorLight').values)
  spot=next(n for _,n in walk(model.root) if n['name']=='RW_DoorSpot');spot['light'].update(intensity=4,range=10,spotAngle=100)
 neck(model);audit[model.name]={'sealed_fixture_mount':True,'science_stair_light_added':role=='LAB'};finish(model,p,root,report)
def flex():
 model,p,root,report=read('FLEX')
 for sign,name in [(-1,'RW_TubeBase'),(1,'RW_TubeNose')]:
  parent=next(n for n in model.root['children'] if n['name']==name)
  boot=h.Mesh();metal=h.Mesh()
  for mesh,r in [(boot,1.225),(boot,1.10)]:
   temp=h.Mesh();h.cylinder_surface(temp,r,0,.24,96);temp.vertices=[(-sign*y,z,x) for x,y,z in temp.vertices];temp.normals=[(-sign*y,z,x) for x,y,z in temp.normals]
   if r==1.10:temp.normals=[tuple(-a for a in n) for n in temp.normals]
   offset=len(mesh.vertices);mesh.vertices+=temp.vertices;mesh.normals+=temp.normals;mesh.uvs+=temp.uvs;mesh.triangles += [tuple(i+offset for i in t) for t in temp.triangles]
  for depth in (0,.24):
   temp=h.Mesh();h.annulus(temp,1.10,1.225,depth,1 if depth==.24 else -1,96);temp.vertices=[(-sign*y,z,x) for x,y,z in temp.vertices];temp.normals=[(-sign*y,z,x) for x,y,z in temp.normals];off=len(boot.vertices);boot.vertices+=temp.vertices;boot.normals+=temp.normals;boot.uvs+=temp.uvs;boot.triangles +=[tuple(i+off for i in t) for t in temp.triangles]
  for depth in (.025,.205):cylinder(metal,(-sign*(depth-.007),0,0),(-sign*(depth+.007),0,0),1.232,1.232,False,64)
  meshnode(model,parent,'RW_FlexOverlapBoot_'+name,'rwm_graphite',boot);meshnode(model,parent,'RW_FlexBootBand_'+name,'rwm_steel',metal)
  c=next(n for n in parent['children'] if n['name']=='FlexEndCollision_'+name)['collider'];co=collision_section(-.24 if sign>0 else 0,0 if sign>0 else .24,1.21,1.21);c['mesh']=dict(vertices=[(y,z,x) for x,y,z in co.vertices],normals=[(y,z,x) for x,y,z in co.normals],uvs=co.uvs,submeshes=[co.triangles])
 p.set('description','Sealed 2.5 m legless telescoping crew passage, 1.2–4.0 m. Both ends dock. Extend/collapse can push or draw the assembly connected to the moving nose, in editor and flight. The rear is the fixed reference. Ground tethers release before motion. A closed connection loop must be opened first. Overlapping sleeves seal the bellows at both caps. No RCS or extra seats/storage.')
 for n in p.children:
  if n.get('name')=='ModuleRWCollapsibleTube':n.set('duration','8')
 audit[model.name]={'overlap_sleeve_depth':.24,'bellows_overlap_each_end':.09,'outer_radius':1.225,'connected_motion':True};finish(model,p,root,report)
def compact(mesh,keep):
 tris=[t for i,t in enumerate(mesh['submeshes'][0]) if i in keep];used=sorted({i for t in tris for i in t});mapping={i:j for j,i in enumerate(used)}
 for key in ('vertices','normals','uvs'):mesh[key]=[mesh[key][i] for i in used]
 mesh['submeshes']=[[tuple(mapping[i] for i in t) for t in tris]]
def command():
 model,p,root,report=read('CMD');rows=json.loads((R/'Reports/LAYOUT_INVENTORY.json').read_text())['CMD'];names=('Roof heat exchanger','Radiator fin','High gain dish rim','High gain parabolic reflector','Dish feed');bounds=[]
 for row in rows:
  if row['name'].startswith(names):
   lo=np.array(row['lo']);hi=np.array(row['hi']);bounds.append((np.array((lo[0],lo[2]-2.3,-hi[1]))-.0002,np.array((hi[0],hi[2]-2.3,-lo[1]))+.0002,row['name']))
 removed={};groups=[]
 for _,n in walk(model.root):
  if 'mesh' not in n or not n['name'].startswith('GND_'):continue
  mesh=n['mesh'];v=np.array(mesh['vertices']);tri=mesh['submeshes'][0];discard=set()
  for g in components(mesh):
   indices=sorted({i for t in g for i in tri[t]});a=v[indices]
   match=next((name for lo,hi,name in bounds if np.all(a.min(0)>=lo) and np.all(a.max(0)<=hi)),None)
   tex=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name'];center=(a.min(0)+a.max(0))/2
   if tex=='gnd_ivory' and abs(center[0]-.3)<.1 and 1.55<center[1]<2.3 and -.1<center[2]<.4:match='High gain parabolic reflector'
   if match:discard.update(g);removed[match]=removed.get(match,0)+len(g)
  if discard:compact(mesh,set(range(len(tri)))-discard)
 model.root['children']=[n for n in model.root['children'] if 'mesh' not in n or n['mesh']['vertices']]
 # Extend pressure shell axially; keep doors, stairs and lamp hardware rigid.
 special=set();leg_mounts={}
 for row in rows:
  if row['name'].startswith('Leg ') and row['name'].endswith('hull saddle'):
   number=int(row['name'].split()[1]);leg_mounts['RW_GroundLeg%02d'%number]=(row['lo'][0]+row['hi'][0])/2
 for child in model.root['children']:
  if child['name'].startswith(('RW_GroundLeg','RW_GroundStairs')):
   special.update(id(n) for _,n in walk(child))
   if child['name']=='RW_GroundStairs':shift=child['position'][0]*.25
   else:
    shift=leg_mounts[child['name']]*.25
   child['position']=(child['position'][0]+shift,*child['position'][1:])
   for binding in report.get('motion',[]):
    if binding['name']==child['name']:
     for key in ('position','retractPosition'):binding[key][0]+=shift
   for mod in p.children:
    if mod.get('name')=='ModuleRWGroundDeploy':
     for binding in mod.children:
      if binding.get('name')==child['name']:
       for key in ('deployPosition','retractPosition'):
        values=[float(a) for a in binding.get(key).split(',')];values[0]+=shift;binding.set(key,', '.join(format(a,'.9g') for a in values))
 for path,n in walk(model.root):
  if id(n) in special:continue
  n['position']=(n['position'][0]*1.25,*n['position'][1:])
  if 'mesh' in n:
   mesh=n['mesh'];v=np.array(mesh['vertices']);tex=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
   if n['name'].startswith('RW_DoorLight'):v[:,0]+=-.1*.25
   elif tex.startswith('gnd_') or 'label' in tex or 'crest' in tex:
    for group in components(mesh):
     idx=sorted({i for t in group for i in mesh['submeshes'][0][t]});a=v[idx];center=(a.min(0)+a.max(0))/2
     span=a.max(0)-a.min(0)
     if tex.startswith('gnd_') and span[0]>.8 and span[0]>2*max(span[1],span[2]):
      v[idx,0]*=1.25;normal=np.array(mesh['normals']);normal[idx,0]/=1.25;normal[idx]/=np.linalg.norm(normal[idx],axis=1)[:,None];mesh['normals']=normal.tolist();continue
     if center[1]<-.5 and .70<abs(center[2])<1.28:
      shift=min(leg_mounts.values(),key=lambda x:abs(x-center[0]))*.25
     elif center[2]>1.25:shift=-.025
     elif center[1]>1.5:shift=.3*.25
     else:shift=center[0]*.25
     v[idx,0]+=shift
   else:
    v[:,0]*=1.25;normal=np.array(mesh['normals']);normal[:,0]/=1.25;normal/=np.linalg.norm(normal,axis=1)[:,None];mesh['normals']=normal.tolist()
   mesh['vertices']=v.tolist()
  if 'collider' in n:
   c=n['collider']
   if c['type']=='mesh':
    c['mesh']['vertices']=[(x*1.25,y,z) for x,y,z in c['mesh']['vertices']];normal=np.array(c['mesh']['normals']);normal[:,0]/=1.25;normal/=np.linalg.norm(normal,axis=1)[:,None];c['mesh']['normals']=normal.tolist()
   else:
    c['center']=(c['center'][0]*1.25,*c['center'][1:])
 for key in ('node_stack_top','node_stack_bottom'):
  a=p.get(key).split(',');a[0]=format(float(a[0])*1.25,'.9g');p.set(key,','.join(a))
 p.set('CrewCapacity','3');p.set('mass','3.2');p.set('cost','17310');next(n for n in p.children if n.header=='INTERNAL').set('name','Mk1-3')
 p.set('description','Three-seat 2.5 m ground command station, 2.15 m long (25% longer). Stock three-seat Mk1-3 IVA; original command, data and electrical roles retained. Continuous dish reflector and reinforced mast connection, clear roof without heat exchangers. Deployable legs/stairs, warm cabin lights and ground-facing exterior spotlight. No RCS.')
 # One continuous, two-surface paraboloid, closed edge, rear hub and mast brace.
 c=np.array((.375,1.9,.12));axis=np.array((0,.55,.835));axis/=np.linalg.norm(axis);u=np.array((1,0,0));v=np.cross(axis,u);white=h.Mesh();back=h.Mesh();steel=h.Mesh();gold=h.Mesh()
 for side,mesh in [(1,white),(-1,back)]:
  for j in range(8):
   for i in range(64):
    corners=[(j/8,i/64),(j/8,(i+1)/64),((j+1)/8,(i+1)/64),((j+1)/8,i/64)];points=[];norms=[]
    for f,t in corners:
     r=f*.282;rad=u*math.cos(t*math.tau)+v*math.sin(t*math.tau);points.append(tuple(c+rad*r+axis*(.052*f*f-(.012 if side<0 else 0))));n=axis-rad*(2*.052*f/.282);n/=np.linalg.norm(n);norms.append(tuple(n*side))
    mesh.quad(points,norms)
 for i in range(64):
  a=i*math.tau/64;b=(i+1)*math.tau/64;pa=c+(u*math.cos(a)+v*math.sin(a))*.282+axis*.046;pb=c+(u*math.cos(b)+v*math.sin(b))*.282+axis*.046;h.tube(steel,pa,pb,.014,10)
 cylinder(steel,c-axis*.105,c-axis*.005,.065,.065,True,24);h.tube(steel,(.375,1.72,-.10),c-axis*.065,.045,16)
 cylinder(gold,c-axis*.006,c+axis*.255,.018,.018,True,16);cylinder(steel,c+axis*.25,c+axis*.277,.034,.034,True,16)
 for key,mesh in [('white',white),('steel',back),('steel',steel),('bronze',gold)]:meshnode(model,model.root,'RW_ContinuousDish_'+key+str(len(mesh.vertices)),'rwm_'+key,mesh)
 neck(model)
 # Mechanical report/airlock remains aligned with the translated door assembly.
 if 'airlock' in report:report['airlock'][0]*=1.25
 report['refinements']['removed_roof_objects']=[r['name'] for r in rows if r['name'].startswith(('Roof heat exchanger','Radiator fin'))]
 # Cabin volume increases with axial size, supplies with the third crew seat.
 compat=GD/'Compatibility/CommandKerbalism.cfg';cr=parse((OLD/'GameData/RoosterWorksGroundModules/Compatibility/CommandKerbalism.cfg').read_text())
 for rule in cr.children:
  for n in rule.children:
   if n.header.startswith('%RESOURCE'):
    for k in ('%amount','%maxAmount'):
     if n.get(k) is not None:n.set(k,format(float(n.get(k))*1.5,'.9g'))
   if n.header.startswith('%MODULE[Habitat]'):n.set('%volume','7.25');n.set('%surface','25')
 compat.write_text(dump(cr),encoding='utf-8')
 cp=GD/'Compatibility/ZZZCommandStorage075.cfg';s=(OLD/'GameData/RoosterWorksGroundModules/Compatibility/ZZZCommandStorage075.cfg').read_text().replace('with retained control, communications, IVA','with three seats, 25% longer hull, retained control, communications, three-seat IVA');cp.write_text(s,encoding='utf-8')
 audit[model.name]={'length_m':2.15,'old_length_m':1.72,'crew':3,'IVA':'Mk1-3','roof_removed':removed,'continuous_dish':True,'fixture_neck':True,'habitat_volume':7.25};finish(model,p,root,report)
 # Removing batched roof meshes changes triangle indices; regenerate only
 # CMD's exact ring selections, preserving every other model's map.
 baseline_map=OLD/'GameData/RoosterWorksGroundModules/Compatibility/GroundRingGeometry.cfg'
 if not baseline_map.exists():baseline_map=W/'ground-hotpatch-v19/GameData/RoosterWorksGroundModules/Compatibility/GroundRingGeometry.cfg'
 maps=parse(baseline_map.read_text());model=load(GD/'Models/RW_GND_CMD.mu');specs=[]
 for path,n in walk(model.root):
  if 'mesh' not in n:continue
  tex=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
  if tex not in SURFACES:continue
  selected=[j for group in components(n['mesh']) if circular(n['mesh'],group) for j in group]
  if selected:specs.append(Node('MESH',[('path',path),('texture',tex),('vertices',str(len(n['mesh']['vertices']))),('triangles',str(len(n['mesh']['submeshes'][0]))),('ranges',ranges(sorted(selected)))]))
 assert specs
 next(n for n in maps.children if n.get('model')=='RW_GND_CMD').children=specs
 (GD/'Compatibility/GroundRingGeometry.cfg').write_text(dump(maps),encoding='utf-8')
for role in ('HAB','AIR','LAB'):light(role)
flex();command()
vpath=GD/'RoosterWorksGroundModules.version';version=json.loads(vpath.read_text());version['VERSION']['BUILD']=20;vpath.write_text(json.dumps(version,indent=2)+'\n');(R/'Reports/DEV20_CHANGES.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
