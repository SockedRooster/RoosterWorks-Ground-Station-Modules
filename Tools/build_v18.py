"""Additive dev.18 equipment; reads protected dev.17 as its sole geometry baseline."""
from pathlib import Path
import sys,math,copy,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=R/'Source/BaselineDev17'
if not OLD.exists():OLD=W/'ground-hotpatch-v17'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
from appearance_textures import label
import build_hab250 as h
GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models';audit={}

def node(name,pos=(0,0,0),rot=(0,0,0,1)):
 return dict(name=name,position=tuple(pos),rotation=tuple(rot),scale=(1,1,1),children=[],tag='Untagged',layer=0)
def quat(axis,angle):
 a=math.radians(angle)/2;return tuple(v*math.sin(a) for v in axis)+(math.cos(a),)
def module(name,values=(),children=()):return Node('MODULE',[('name',name)]+list(values),list(children))
def box(mesh,c,size):
 c=np.array(c,dtype=float);d=np.array(size)/2
 for axis in range(3):
  other=[i for i in range(3) if i!=axis]
  for sign in (-1,1):
   normal=np.zeros(3);normal[axis]=sign;ps=[]
   for a,b in ((-1,-1),(1,-1),(1,1),(-1,1)):
    p=c.copy();p[axis]+=sign*d[axis];p[other[0]]+=a*d[other[0]];p[other[1]]+=b*d[other[1]];ps.append(tuple(p))
   mesh.quad(ps,(tuple(normal),)*4)
def cylinder(mesh,a,b,r0,r1,cap=True,sides=16):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);axis=b-a;length=np.linalg.norm(axis);axis/=length
 u=np.cross(axis,(0,1,0) if abs(axis[1])<.9 else (1,0,0));u/=np.linalg.norm(u);v=np.cross(axis,u)
 slope=(r1-r0)/length
 for i in range(sides):
  t=i*math.tau/sides;s=(i+1)*math.tau/sides;r=math.cos(t)*u+math.sin(t)*v;q=math.cos(s)*u+math.sin(s)*v
  nr=r-axis*slope;nr/=np.linalg.norm(nr);nq=q-axis*slope;nq/=np.linalg.norm(nq)
  mesh.quad([tuple(a+r*r0),tuple(a+q*r0),tuple(b+q*r1),tuple(b+r*r1)],(tuple(nr),tuple(nq),tuple(nq),tuple(nr)))
  if cap:
   for center,radius,normal in ((a,r0,-axis),(b,r1,axis)):
    mesh.triangle((tuple(center),tuple(center+r*radius),tuple(center+q*radius)),(tuple(normal),)*3,((.5,.5),(0,0),(1,0)))
def material(model,key):
 return next(i for i,m in enumerate(model.materials) if model.textures[m['properties']['_MainTex']['index']]['name']==key)
def meshnode(model,parent,name,key,mesh):
 if not mesh.triangles:return None
 vertices=np.array(mesh.vertices);norm=np.array(mesh.normals)
 triangles=[tuple(reversed(t)) if np.dot(np.cross(vertices[t[1]]-vertices[t[0]],vertices[t[2]]-vertices[t[0]]),norm[list(t)].mean(0))<0 else t for t in mesh.triangles]
 n=node(name);n.update(mesh=dict(vertices=mesh.vertices,normals=mesh.normals,uvs=mesh.uvs,submeshes=[triangles]),materials=[material(model,key)],shadows=(1,1));parent['children'].append(n);return n
def rcs_effect():
 return Node('rcs',children=[Node('MODEL_MULTI_PARTICLE',[('modelName','Squad/FX/Monoprop_small'),('transformName','RW_GroundRCS'),('emission','0 0'),('emission','1 1'),('speed','0 .8'),('speed','1 1'),('localRotation','-90, 0, 0')])])
def rcs_module(power='.6'):
 return module('ModuleRCSFX',[('stagingEnabled','false'),('thrusterTransformName','RW_GroundRCS'),('thrusterPower',power),('resourceName','MonoPropellant'),('resourceFlowMode','STAGE_PRIORITY_FLOW'),('runningEffectName','rcs'),('enablePitch','true'),('enableYaw','true'),('enableRoll','true'),('enableX','true'),('enableY','true'),('enableZ','true')],[Node('atmosphereCurve',[('key','0 240'),('key','1 100'),('key','4 .001')])])
def rcs_cluster(model,parent,center,sy,sz,label,local_offset=(0,0,0)):
 """Four outward/tangential exhaust directions; no inward-facing jets into hull."""
 c=np.array(center,dtype=float);base=node('RW_RCSCluster_'+label,local_offset);parent['children'].append(base)
 dark=h.Mesh();metal=h.Mesh();gold=h.Mesh();radial=np.array((0,sy,sz),dtype=float);radial/=np.linalg.norm(radial)
 cylinder(dark,c-radial*.14,c,.10,.10);box(dark,c,(.15,.15,.15))
 for j,direction in enumerate(((1,0,0),(-1,0,0),(0,sy,0),(0,0,sz))):
  d=np.array(direction,dtype=float);tip=c+d*.18
  cylinder(metal,c+d*.04,tip,.035,.048,False)
  cylinder(dark,tip-d*.004,tip,.036,.036,True)
  cylinder(gold,tip-d*.022,tip-d*.011,.050,.050,False)
  if direction[0]:q=quat((0,0,1),-90*direction[0])
  elif direction[1]:q=quat((1,0,0),180) if sy<0 else (0,0,0,1)
  else:q=quat((1,0,0),90*sz)
  base['children'].append(node('RW_GroundRCS',tip+d*.006,q))
 for key,m in [('rwm_graphite',dark),('rwm_steel',metal),('rwm_bronze',gold)]:meshnode(model,base,'RW_RCS_'+label+'_'+key,key,m)
 return dict(root=base['name'],center=(c+np.array(local_offset)).tolist(),directions=[[1,0,0],[-1,0,0],[0,sy,0],[0,0,sz]])
def add_rcs(model,p):
 ID=model.name;parent=model.root;offset=(0,0,0)
 if ID=='RW_GND_FLEX':
  parent=next(n for n in model.root['children'] if n['name']=='RW_TubeBase');x=.075;r=1.204;origin=0;offset=parent['position']
 elif ID=='RW_GND_ELB':x=1.00;r=1.25;origin=-.90
 elif ID=='RW_GND_HUB':x=-1.80;r=1.25;origin=0
 elif ID=='RW_GND_END_250_125':x=-.35;r=1.21;origin=0
 else:
  x=float(p.get('node_stack_bottom').split(',')[0])+.18;r=1.25;origin=0
 result=[]
 for sy in (-1,1):
  for sz in (-1,1):
   c=(x,(r+.13)*sy/math.sqrt(2),origin+(r+.13)*sz/math.sqrt(2))
   result.append(rcs_cluster(model,parent,c,sy,sz,('Top' if sy>0 else 'Bottom')+('Front' if sz>0 else 'Rear'),offset))
 p.children.append(rcs_module());p.children.append(Node('EFFECTS',children=[rcs_effect()]))
 p.set('mass',format(float(p.get('mass'))+.04,'.6g'));p.set('cost',str(int(p.get('cost'))+480))
 p.set('description',p.get('description')+' Integrated upper/lower RCS clusters use vessel monopropellant; supply it from a thrust pod or external tank.')
 return result
def add_door_light(model,p):
 airlock=next(n for _,n in walk(model.root) if n.get('tag')=='Airlock');x=airlock['position'][0]
 support=h.Mesh();body=h.Mesh();lens=h.Mesh();trim=h.Mesh()
 # Seated hood over door roof. Bracket reaches back into pressure hull; no floating fixture.
 box(support,(x,.82,1.22),(.32,.075,.64))
 direction=np.array((0,-math.sqrt(3)/2,.5));center=np.array((x,.865,1.646));right=np.array((1,0,0));up=np.cross(direction,right)
 for mesh,c,size in [(body,(0,0,-.06),(.46,.14,.10)),(trim,(0,.064,-.06),(.44,.018,.11))]:
  box(mesh,c,size);basis=np.array((right,up,direction)).T
  mesh.vertices=[tuple(center+basis@np.array(v)) for v in mesh.vertices];mesh.normals=[tuple(basis@np.array(n)) for n in mesh.normals]
 points=[tuple(center+right*.19*a+up*.045*b) for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))]
 lens.quad(points,(tuple(direction),)*4)
 for name,key,m in [('RW_DoorLightBracket','rwm_graphite',support),('RW_DoorLightHousing','rwm_steel',body),('RW_DoorLightTrim','rwm_bronze',trim),('RW_DoorLightLens','rwm_endwindow',lens)]:meshnode(model,model.root,name,key,m)
 spot=node('RW_DoorSpot',center+direction*.035,quat((1,0,0),60));spot['light']=dict(type=0,intensity=3.0,range=9,color=(1,.91,.76,1),cullingMask=0xffffffff,spotAngle=90);model.root['children'].append(spot)
 p.children.append(module('ModuleRWExteriorLight',[('moduleID',model.name+'_Exterior'),('lightName','RW_DoorSpot'),('lightMeshRendererName','RW_DoorLightLens'),('useAnimationDim','false'),('useAutoDim','false'),('lightBrightenSpeed','3'),('lightDimSpeed','3'),('useResources','true'),('resourceName','ElectricCharge'),('resourceAmount','.03'),('disableColorPicker','true'),('lightR','1'),('lightG','.91'),('lightB','.76'),('canBlink','false'),('isOn','false')]))
 return dict(position=spot['position'],direction=direction.tolist(),range=9,cone_degrees=90,ec_per_second=.03)
def build_existing():
 for source in sorted((OLD/'GameData/RoosterWorksGroundModules/Parts').glob('*.cfg')):
  root=parse(source.read_text(encoding='utf-8'));p=root.children[0];ID=p.get('name');model=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu')
  item=dict(rcs=add_rcs(model,p))
  if ID in ('RW_GND_HAB','RW_GND_CMD','RW_GND_AIR'):item['exterior_light']=add_door_light(model,p)
  write(model,OUT/(ID+'.mu'));(GD/'Parts'/source.name).write_text(dump(root),encoding='utf-8')
  report=json.loads((OLD/f'Reports/{ID}.json').read_text());report['dev18_equipment']=item;report['triangles']=sum(len(s) for _,n in walk(model.root) if 'mesh' in n for s in n['mesh']['submeshes']);report['native_sha256']=hashlib.sha256((OUT/(ID+'.mu')).read_bytes()).hexdigest();(R/f'Reports/{ID}.json').write_text(json.dumps(report,indent=2)+'\n')
  audit[ID]=item;print('Built',ID,'top/bottom RCS'+(' + door spotlight' if 'exterior_light' in item else ''),flush=True)

def build_thruster():
 ID='RW_GND_VT';donor=load(OLD/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu');model=copy.deepcopy(donor);model.name=ID;model.root=node(ID)
 source_mat=copy.deepcopy(model.materials[material(model,'rwm_pwrlabel')]);source_mat['name']='RW_VT_Label';source_mat['properties']['_MainTex']['index']=len(model.textures);model.textures.append(dict(name='rwm_vtlabel',type=0));model.materials.append(source_mat)
 label('VT-60','VERTICAL THRUST').save(OUT/'rwm_vtlabel.png')
 meshes={k:h.Mesh() for k in ('graphite','steel','white','bronze','black','crest','vtlabel')}
 # Vertical side pod, inner mounting plane Z=0, engine safely outboard at Z=.95.
 box(meshes['graphite'],(0,.18,.12),(.54,1.22,.24));box(meshes['steel'],(0,.22,.29),(.64,.95,.16))
 for y in (-.20,.64):
  for x in (-.23,.23):
   cylinder(meshes['bronze'],(x,y,.37),(x,y,.40),.042,.042)
 cylinder(meshes['white'],(0,-.40,.84),(0,.96,.84),.40,.40,sides=48)
 cylinder(meshes['white'],(0,.96,.84),(0,1.14,.84),.40,.18,sides=48)
 cylinder(meshes['graphite'],(0,-.53,.84),(0,-.40,.84),.22,.40,sides=48)
 for y in (-.38,.28,.93):cylinder(meshes['steel'],(0,y,.84),(0,y+.035,.84),.414,.414,False,48)
 for y in (.12,.48):
  for sign in (-1,1):
   h.tube(meshes['graphite'],(sign*.18,y,.25),(sign*.30,y,.59),.045,12)
 for sign in (-1,1):
  h.tube(meshes['bronze'],(sign*.42,-.42,.84),(sign*.42,.87,.84),.016,10)
  box(meshes['graphite'],(sign*.404,.50,.84),(.035,.40,.33))
  for y in np.linspace(.35,.65,6):box(meshes['steel'],(sign*.427,y,.84),(.025,.018,.27))
 # Readable front service label and upright rooster; reuse accepted original textures.
 for key,c,width,height in [('vtlabel',(0,.28,1.249),.46,.23),('crest',(0,.73,1.249),.19,.19)]:
  a=np.array(c);meshes[key].quad([tuple(a+(dx*width/2,dy*height/2,0)) for dx,dy in ((1,-1),(-1,-1),(-1,1),(1,1))],((0,0,1),)*4)
 for key,m in meshes.items():meshnode(model,model.root,'RW_VT_'+key,'rwm_'+key,m)
 # Gimbal's own local +Z follows the engine axis, as stock ModuleGimbal expects.
 g=node('RW_VT_Gimbal',(0,-.53,.84),quat((1,0,0),90));model.root['children'].append(g);outer=h.Mesh();inner=h.Mesh();rim=h.Mesh()
 cylinder(outer,(0,-.38,0),(0,0,0),.27,.11,False,48)
 cylinder(inner,(0,-.38,0),(0,-.01,0),.232,.080,False,48)
 # Reverse inner normals and winding to show the inside of the bell.
 inner.normals=[tuple(-v for v in n) for n in inner.normals]
 cylinder(rim,(0,-.388,0),(0,-.365,0),.282,.282,False,48)
 for key,m in [('steel',outer),('black',inner),('bronze',rim)]:
  m.vertices=[(x,z,-y) for x,y,z in m.vertices];m.normals=[(x,z,-y) for x,y,z in m.normals];meshnode(model,g,'RW_VT_Bell_'+key,'rwm_'+key,m)
 g['children'].append(node('RW_VT_Thrust',(0,0,.40)))
 for name,c,size in [('Mount',(0,.18,.15),(.54,1.22,.30)),('Tank',(0,.29,.84),(.74,1.60,.74))]:
  n=node('RW_VT_Collision_'+name);n['collider']=dict(type='box',trigger=0,size=size,center=c);model.root['children'].append(n)
 n=node('RW_VT_BellCollision');n['collider']=dict(type='box',trigger=0,size=(.45,.45,.35),center=(0,0,.20));g['children'].append(n)
 # Two little attitude jets clear of tank shoulders; fuel is shared vessel-wide.
 # Use the four collar clusters on the payload for attitude control. This pod
 # supplies their propellant, without putting additional jets through its tank.
 clusters=[]
 # Pod RCS uses only outward/fore-aft directions; thrust frame points vertically down.
 p=Node('PART:NEEDS[RoosterWorksStationModules]',[('name',ID),('module','Part'),('author','SockedRooster'),('rescaleFactor','1'),('node_attach','0, 0, 0, 0, 0, -1, 1'),('node_stack_mount','0, 0, 0, 0, 0, -1, 1'),('attachRules','1,1,0,1,0'),('bulkheadProfiles','srf'),('TechRequired','precisionPropulsion'),('entryCost','9500'),('cost','4200'),('category','Engine'),('subcategory','0'),('title','RoosterWorks VT-60 — Vertical Thrust Pod'),('manufacturer','RoosterWorks'),('description','Surface-mounted 60 kN lift pod. Fit balanced pods on opposite sides with nozzle arrows down, clear of doors, stairs and legs. 90 LiquidFuel / 110 Oxidizer and 60 MonoPropellant; RCS fuel is shared with ground modules. 320 s vacuum / 260 s sea-level Isp. Three-degree gimbal. No docking or command module. Release the ground tether before takeoff. Designed for vertical handling and low-gravity surface hops; plan orbital delivery separately.'),('tags','roosterworks ground base surface lift vertical thrust engine rcs hopper'),('mass','.60'),('CrewCapacity','0'),('fuelCrossFeed','true'),('dragModelType','default'),('maximum_drag','.2'),('minimum_drag','.2'),('angularDrag','2'),('crashTolerance','12'),('breakingForce','350'),('breakingTorque','350'),('maxTemp','2000'),('skinMaxTemp','2300')],[Node('MODEL',[('model','RoosterWorksGroundModules/Models/'+ID)]),module('ModuleRWStationFinish',[('finish','White')])])
 p.children.append(module('ModuleEnginesFX',[('engineID','VerticalLift'),('thrustVectorTransformName','RW_VT_Thrust'),('runningEffectName','lift'),('engageEffectName','engage'),('disengageEffectName','disengage'),('exhaustDamage','true'),('exhaustDamageMaxRange','2'),('ignitionThreshold','.1'),('minThrust','0'),('maxThrust','60'),('heatProduction','55'),('EngineType','LiquidFuel')],[Node('PROPELLANT',[('name','LiquidFuel'),('ratio','.9'),('DrawGauge','true')]),Node('PROPELLANT',[('name','Oxidizer'),('ratio','1.1')]),Node('atmosphereCurve',[('key','0 320'),('key','1 260'),('key','4 .001')])]))
 p.children.append(module('ModuleGimbal',[('gimbalTransformName','RW_VT_Gimbal'),('gimbalRange','3'),('gimbalResponseSpeed','12'),('useGimbalResponseSpeed','true')]))
 effects=Node('EFFECTS',children=[Node('lift',children=[Node('AUDIO',[('channel','Ship'),('clip','sound_rocket_mini'),('volume','0 0'),('volume','1 .8'),('pitch','0 .7'),('pitch','1 1'),('loop','true')]),Node('PREFAB_PARTICLE',[('prefabName','fx_exhaustFlame_yellow_tiny_Z'),('transformName','RW_VT_Thrust'),('emission','0 0'),('emission','1 1'),('speed','0 .8'),('speed','1 1'),('localPosition','0, 0, .12')])]),rcs_effect()])
 for name,clip in [('engage','sound_vent_medium'),('disengage','sound_vent_soft')]:effects.children.append(Node(name,children=[Node('AUDIO',[('channel','Ship'),('clip',clip),('loop','false')])]))
 effects.children=[n for n in effects.children if n.header!='rcs']
 p.children+=[effects]
 for name,amount in [('LiquidFuel',90),('Oxidizer',110),('MonoPropellant',60)]:p.children.append(Node('RESOURCE',[('name',name),('amount',str(amount)),('maxAmount',str(amount))]))
 write(model,OUT/(ID+'.mu'));(GD/'Parts'/(ID+'.cfg')).write_text(dump(Node('ROOT',children=[p])),encoding='utf-8')
 audit[ID]=dict(thrust_kn=60,dry_mass_t=.6,wet_mass_t=1.84,rcs=clusters,ports=0)
 (R/'Reports'/f'{ID}.json').write_text(json.dumps(dict(role='VT',motion=[],dev18_equipment=audit[ID]),indent=2)+'\n')
 print('Built VT-60 lift pod / 60 kN / LFO + shared monopropellant / zero docking ports',flush=True)
def main():
 build_existing();build_thruster()
 v=json.loads((GD/'RoosterWorksGroundModules.version').read_text());v['VERSION']['BUILD']=18;(GD/'RoosterWorksGroundModules.version').write_text(json.dumps(v,indent=2)+'\n')
 (R/'Reports/DEV18_EQUIPMENT.json').write_text(json.dumps(audit,indent=2)+'\n')
if __name__=='__main__':main()
