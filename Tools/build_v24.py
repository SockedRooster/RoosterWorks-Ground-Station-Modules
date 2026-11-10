"""Compact 2.5 m ground equipment collar with integrated opposed flat hardpoints.

No existing part is changed. The flat saddle is part of the shell geometry,
not a floating box on top of a cylinder. Core/ground baselines are read-only.
"""
from pathlib import Path
import sys,copy,json,math,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v23';CORE=W/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
from station_endcaps import add_endcap
from surface_uv import finish
from appearance_textures import label
from build_adp250375 import collision_section
from build_ring_options import components,circular,ranges,SURFACES
import build_hab250 as h
from build_v18 import node,box,cylinder,meshnode,quat,module
from end_face_refinements import repair
GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models';ID='RW_GND_HPT';HALF=.6;RADIUS=1.204

def limit(axial):
 t=min(1,max(0,(abs(axial)-.40)/.16));return 1.035+(RADIUS-1.035)*t*t*(3-2*t)
def slope(axial):
 t=min(1,max(0,(abs(axial)-.40)/.16));return (RADIUS-1.035)*(6*t-6*t*t)/.16*(1 if axial>=0 else -1)
def point(axial,a,r=RADIUS):
 flat=limit(axial)+(r-RADIUS)
 return (float(np.clip(r*math.sin(a),-flat,flat)),axial,r*math.cos(a))
def normal(axial,a,r=RADIUS):
 x=r*math.sin(a)
 if abs(x)>limit(axial)+(r-RADIUS)+1e-9:
  sign=1 if x>0 else -1;n=np.array((sign,-slope(axial),0),float)
 else:n=np.array((math.sin(a),0,math.cos(a)),float)
 return tuple(n/np.linalg.norm(n))
def patch(mesh,x0,x1,a0,a1,r=RADIUS,rows=4,cols=6):
 for i in range(rows):
  for j in range(cols):
   samples=((i/rows,j/cols),(i/rows,(j+1)/cols),((i+1)/rows,(j+1)/cols),((i+1)/rows,j/cols));ps=[];ns=[];uv=[]
   for u,v in samples:
    x=x0+(x1-x0)*u;a=a0+(a1-a0)*v;ps.append(point(x,a,r));ns.append(normal(x,a,r));uv.append((v,u))
   mesh.quad(ps,ns,uv)
def native(mesh):
 mesh.vertices=[(y,z,x) for x,y,z in mesh.vertices];mesh.normals=[(y,z,x) for x,y,z in mesh.normals];return mesh
def chamfer(w,h,c):return [(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]
def bevel(mesh,sign,w0,h0,z0,w1,h1,z1):
 loops=[[(x,y,sign*z) for x,y in chamfer(w,ht,.07)] for w,ht,z in ((w0,h0,z0),(w1,h1,z1))]
 for i in range(8):
  j=(i+1)%8;ps=np.array((loops[0][i],loops[0][j],loops[1][j],loops[1][i]));n=np.cross(ps[1]-ps[0],ps[2]-ps[0]);n=sign*n/np.linalg.norm(n);mesh.quad([tuple(p) for p in ps],[tuple(n)]*4)
 for i in range(8):mesh.triangle([(0,0,sign*z1),loops[1][i],loops[1][(i+1)%8]],[(0,0,sign)]*3,[(.5,.5),(0,0),(1,0)])

def main():
 protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for root in (B,W/'rw-v075dev10') for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV24_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
 model=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu');model.name=ID;model.root=node(ID)
 meshes={key:h.Mesh() for key in h.TEXTURES}
 patch(meshes['graphite'],-.58,.58,0,math.tau,RADIUS-.005,rows=16,cols=192)
 for axial in range(3):
  lo=-.52+1.04*axial/3;hi=-.52+1.04*(axial+1)/3
  for col in range(24):patch(meshes['cladding_white' if col%6==0 else 'cladding'],lo+.003,hi-.003,math.tau*col/24+.003,math.tau*(col+1)/24-.003)
 # Circular end collars restore the unchanged 2.5 m mating interface.
 for sign in (-1,1):
  for key,r,a,b in [('white',1.204,.50,.60),('steel',1.218,.53,.56),('bronze',1.223,.565,.579)]:
   h.cylinder_surface(meshes[key],r,sign*a,sign*b,96)
  add_endcap(meshes,sign,HALF)
 finish(meshes)
 for key,mesh in meshes.items():
  if mesh.triangles:meshnode(model,model.root,'RW_HPT_'+key,'rwm_'+key,native(mesh))
 # Real, solid stepped saddles fill the cut-in shell on both flanks. The
 # exposed front planes and bolt heads stay inside Z=+/-1.25 m.
 for sign,side in ((1,'Port'),(-1,'Starboard')):
  dark=h.Mesh();metal=h.Mesh();white=h.Mesh();gold=h.Mesh()
  bevel(dark,sign,.92,1.18,1.025,.88,1.14,1.18)
  bevel(metal,sign,.88,1.14,1.165,.76,1.02,1.24)
  box(white,(0,0,sign*1.245),(.70,.88,.010))
  for x in (-.315,.315):
   for y in (-.39,.39):cylinder(gold,(x,y,sign*1.247),(x,y,sign*1.250),.020,.020,sides=12)
  # Alignment/index marks are recessed; the central mounting area is planar.
  for y in (-.485,.485):box(dark,(0,y,sign*1.241),(.24,.018,.002))
  for key,mesh in [('rwm_graphite',dark),('rwm_steel',metal),('rwm_white',white),('rwm_bronze',gold)]:meshnode(model,model.root,'RW_HPT_'+side+'_'+key,key,mesh)
  for name,c,size in [('Saddle',(0,0,sign*1.135),(.86,1.10,.210)),('Face',(0,0,sign*1.245),(.70,.88,.010))]:
   n=node('RW_HPT_'+side+'_'+name+'Collision');n['collider']=dict(type='box',trigger=0,size=size,center=c);model.root['children'].append(n)
 # Continuous underside service lines meet existing ground modules at X=+/-0.6.
 pipes=h.Mesh();rails=h.Mesh();sockets=h.Mesh()
 for side in (-1,1):
  for y,r in ((-1.03,.065),(-1.16,.045)):h.tube(pipes,(-HALF,y,side*.6),(HALF,y,side*.6),r,16)
  z=side*.60;foot=math.sqrt(RADIUS**2-z*z)
  h.tube(rails,(-.44,1.36,z),(.44,1.36,z),.022,12)
  for x in (-.44,.44):
   h.tube(sockets,(x,foot-.025,z),(x,foot+.06,z),.043,12)
   h.tube(rails,(x,foot+.035,z),(x,1.36,z),.021,12)
 meshnode(model,model.root,'RW_HPT_ServicePipes','rwm_graphite',pipes);meshnode(model,model.root,'RW_HPT_RoofRails','gnd_copper',rails);meshnode(model,model.root,'RW_HPT_RailSockets','gnd_graphite',sockets)
 # New compact label bridges the roof, away from both usable side faces.
 source=copy.deepcopy(next(m for m in model.materials if model.textures[m['properties']['_MainTex']['index']]['name']=='rwm_pwrlabel'))
 source['name']='RW_HPT_Label';source['properties']['_MainTex']['index']=len(model.textures);model.textures.append(dict(name='rwm_hptlabel',type=0));model.materials.append(source)
 label('HPT-250','EQUIPMENT COLLAR').save(OUT/'rwm_hptlabel.png')
 frame=h.Mesh();box(frame,(0,1.194,0),(.76,.034,.40));meshnode(model,model.root,'RW_HPT_LabelFrame','gnd_graphite',frame)
 plaque=h.Mesh();plaque.quad([(-.36,1.213,-.18),(.36,1.213,-.18),(.36,1.213,.18),(-.36,1.213,.18)],[(0,1,0)]*4,[(1,1),(0,1),(0,0),(1,0)])
 meshnode(model,model.root,'RW_HPT_RoofLabel','rwm_hptlabel',plaque)
 # Convex sections follow the flattened barrel rather than occupying space
 # outside the skin; two separate flat-face colliders receive surface attach.
 sections=[-.60,-.52,-.40,0,.40,.52,.60]
 for i,(a,b) in enumerate(zip(sections,sections[1:])):
  mesh=collision_section(a,b,1.195,1.195)
  mesh.vertices=[(float(np.clip(x,-limit(y),limit(y))),y,z) for x,y,z in mesh.vertices];native(mesh)
  n=node('RW_HPT_HullCollision'+str(i));n['collider']=dict(type='mesh',trigger=0,convex=1,mesh=dict(vertices=mesh.vertices,normals=mesh.normals,uvs=mesh.uvs,submeshes=[mesh.triangles]));model.root['children'].append(n)
 p=copy.deepcopy(parse((B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_PWR.cfg').read_text()).children[0]);p.set('name',ID);p.set('title','RoosterWorks Ground HPT-250 — Compact Equipment Collar');p.set('category','Structural');p.set('TechRequired','advConstruction');p.set('entryCost','4800');p.set('cost','2400');p.set('mass','1.0');p.set('breakingForce','2000');p.set('breakingTorque','2000')
 p.set('description','Compact 1.2 m-long, nominal 2.5 m ground-base equipment collar. Two integrated flat, reinforced side saddles accept surface-mounted equipment or central size1 structural snap connections. Flat faces stay within the 2.5 m hull width. Both inline ends dock at size2 with permanent crossfeed and no staging. No side docking ports, resources, RCS or crew. Legless: fit between supported base modules. Keep external equipment clear of neighboring doors/legs and use balanced loads. White/Grey finish, ring colors, roof handrails, end-window lights and continuous underside services match the ground set.')
 p.set('tags','roosterworks ground base compact equipment collar hardpoint flat hull side mount structural docking connector')
 p.set('bulkheadProfiles','size2, size1, srf')
 p.values=[(k,v) for k,v in p.values if not k.startswith('node_stack_')]
 for name,value in [('top','.6, 0, 0, 1, 0, 0, 2'),('bottom','-.6, 0, 0, -1, 0, 0, 2'),('port','0, 0, 1.25, 0, 0, 1, 1'),('starboard','0, 0, -1.25, 0, 0, -1, 1')]:p.set('node_stack_'+name,value)
 p.children=[n for n in p.children if n.header!='RESOURCE' and n.get('name') not in ('ModuleRWGroundDeploy','ModuleColorChanger')]
 for n in p.children:
  if n.header=='MODEL':n.set('model','RoosterWorksGroundModules/Models/'+ID)
  if n.get('name')=='ModuleRWRingColor':n.set('ringModel',ID)
  if n.get('name')=='ModuleDockingNode':
   end=n.get('referenceAttachNode');sign=1 if end=='top' else -1
   model.root['children'].append(node(n.get('nodeTransformName'),(sign*HALF,0,0),quat((0,1,0),sign*90)))
 p.children.append(Node('VABORGANIZER:NEEDS[VABOrganizer]',[('organizerSubcategory','crewTubes')]))
 p.children.append(Node('MODULE:NEEDS[ConnectedLivingSpace]',[('name','ModuleConnectedLivingSpace'),('passable','true')]))
 # Side hardpoints are equipment surfaces, not pressure hatches. Refine only
 # the two axial faces; the shared helper otherwise sees every stack node.
 values=p.values;p.values=[(k,v) for k,v in values if k not in ('node_stack_port','node_stack_starboard')]
 end_report=repair(model,p);p.values=values
 write(model,OUT/(ID+'.mu'));(GD/f'Parts/{ID}.cfg').write_text(dump(Node('ROOT',children=[p])))
 # Select only two deliberately separate interface bands. Side plates, bolt
 # heads and white flat faces never change with Ring color.
 specs=[]
 for path,n in walk(model.root):
  if n['name'] not in ('RW_HPT_white','RW_HPT_steel','RW_HPT_bronze'):continue
  mesh=n['mesh'];selected=[]
  for group in components(mesh):
   if circular(mesh,group,minimum=1.18,maximum=1.24):selected.extend(group)
  if selected:
   texture=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
   specs.append(Node('MESH',[('path',path),('texture',texture),('vertices',str(len(mesh['vertices']))),('triangles',str(len(mesh['submeshes'][0]))),('ranges',ranges(sorted(selected)))]))
 assert len(specs)==3,len(specs)
 rule=Node('RW_RING_MAP',[('model',ID)],specs)
 cleanup=Node('@PART['+ID+']:NEEDS[Kerbalism]:FINAL',children=[Node('!MODULE[Habitat],*')]+[Node('!RESOURCE['+s+'],*') for s in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')])
 (GD/'Compatibility/CompactHardpoint.cfg').write_text(dump(Node('ROOT',children=[rule,cleanup])))
 nodes=dict(walk(model.root));fixture=[dict(path=e.get('path'),texture=e.get('texture'),vertexCount=int(e.get('vertices')),triangles=[i for t in nodes[e.get('path')]['mesh']['submeshes'][0] for i in t],ranges=e.get('ranges')) for e in specs]
 (R/'Reports/HARDPOINT_COLOR_FIXTURE.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
 report={'id':ID,'length_m':1.2,'nominal_diameter_m':2.5,'flat_mounts':{'port':[0,0,1.25],'starboard':[0,0,-1.25]},'flat_face_size_m':[.70,.88],'legs':0,'crew':0,'docking_ports':2,'side_ports_structural_only':True,'mass_t':1.0,'breaking_force_torque':2000,'end_face_refinement':end_report}
 (R/'Reports/DEV24_HARDPOINT.json').write_text(json.dumps(report,indent=2)+'\n')
 path=GD/'RoosterWorksGroundModules.version';version=json.loads(path.read_text());version['VERSION']['BUILD']=24;path.write_text(json.dumps(version,indent=2)+'\n')
 for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
 print('PASS built HPT-250: 1.2 m compact collar, two integrated flat saddles at +/-1.25 m, structural side nodes, size2 docking ends and no legs; accepted assets preserved')

if __name__=='__main__':main()
