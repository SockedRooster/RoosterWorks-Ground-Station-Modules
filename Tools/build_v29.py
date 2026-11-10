"""Add seated roof fittings without changing any accepted CMD mesh/triangle map."""
from pathlib import Path
import sys,math,json,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v28';GD=R/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev10/Source'),str(W/'rw-v075dev10/Tools'),str(R/'Tools')]
from native_model import load,walk
from native_derivatives import write
from build_ring_options import components
from build_v18 import node,meshnode,cylinder
import build_hab250 as h
RADIUS=1.206

def round_seat(mesh,cx,cz,radius,top):
 def bottom(z):return math.sqrt(RADIUS*RADIUS-z*z)-.012
 def normal(z):
  v=np.array((0,-math.sqrt(RADIUS*RADIUS-z*z),-z));return tuple(v/np.linalg.norm(v))
 for i in range(64):
  a=i*math.tau/64;b=(i+1)*math.tau/64
  x0=cx+radius*math.cos(a);z0=cz+radius*math.sin(a);x1=cx+radius*math.cos(b);z1=cz+radius*math.sin(b)
  low0=(x0,bottom(z0),z0);low1=(x1,bottom(z1),z1);up0=(x0,top,z0);up1=(x1,top,z1)
  mesh.quad((low0,low1,up1,up0),((math.cos(a),0,math.sin(a)),(math.cos(b),0,math.sin(b)),(math.cos(b),0,math.sin(b)),(math.cos(a),0,math.sin(a))))
  mesh.triangle(((cx,top,cz),up0,up1),((0,1,0),)*3,((.5,.5),(0,0),(1,0)))
  mesh.triangle(((cx,bottom(cz),cz),low1,low0),(normal(cz),normal(z1),normal(z0)),((.5,.5),(1,0),(0,0)))

def prism(mesh,x0,x1,z0,z1,y0,y1,t0,t1):
 points=np.array([(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1),(x0,t0,z0),(x1,t0,z0),(x1,t1,z1),(x0,t1,z1)])
 for face in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)):
  v=points[list(face)];n=np.cross(v[1]-v[0],v[2]-v[0]);n/=np.linalg.norm(n)
  if np.dot(n,v.mean(0)-points.mean(0))<0:v=v[::-1];n=-n
  mesh.quad(v.tolist(),[n.tolist()]*4)

def main():
 protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev11') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV29_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
 model=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_CMD.mu');group=node('RW_CommandRoofSeats');model.root['children'].append(group)
 dark=h.Mesh();steel=h.Mesh();bolts=h.Mesh();infill=h.Mesh();audit=[]
 # Original roof cutouts reveal the recessed graphite backing where the
 # removed roof equipment used to sit. A closed curved underlay restores
 # the outer pressure skin, 6 mm below existing cladding to avoid z-fighting.
 angles=np.linspace(-math.asin(.5/1.2),math.asin(.5/1.2),49)
 def point(x,r,a):return (x,r*math.cos(a),r*math.sin(a))
 for a,b in zip(angles,angles[1:]):
  na=(0,math.cos(a),math.sin(a));nb=(0,math.cos(b),math.sin(b))
  infill.quad((point(-.89,1.2,a),point(.89,1.2,a),point(.89,1.2,b),point(-.89,1.2,b)),(na,na,nb,nb))
  infill.quad((point(-.89,1.15,a),point(-.89,1.15,b),point(.89,1.15,b),point(.89,1.15,a)),(tuple(-v for v in na),tuple(-v for v in nb),tuple(-v for v in nb),tuple(-v for v in na)))
  for x,sign in ((-.89,-1),(.89,1)):
   infill.quad((point(x,1.15,a),point(x,1.2,a),point(x,1.2,b),point(x,1.15,b)),((sign,0,0),)*4)
 for a,sign in ((angles[0],-1),(angles[-1],1)):
  n=(0,-sign*math.sin(a),sign*math.cos(a))
  infill.quad((point(-.89,1.15,a),point(.89,1.15,a),point(.89,1.2,a),point(-.89,1.2,a)),(n,)*4)
 # Existing cone spans x=-.7125..-.4125 and starts at y=1.26. The new
 # curved-bottom socket embeds in the hull and overlaps that flat bottom.
 round_seat(dark,-.5625,0,.166,1.272)
 cylinder(steel,(-.5625,1.248,0),(-.5625,1.267,0),.185,.185,sides=64)
 for dx in (-.12,.12):
  for z in (-.12,.12):cylinder(bolts,(-.5625+dx,1.265,z),(-.5625+dx,1.283,z),.013,.013,sides=8)
 audit.append({'name':'telemetry radome','center':[-.5625,0],'radius':.166,'top':1.272,'existing_base':1.26})
 # The mast already enters the hull, but a seated collar closes its foot
 # and gives the roof hardware a consistent bolted mounting treatment.
 round_seat(dark,.375,-.10,.067,1.225)
 cylinder(steel,(.375,1.215,-.10),(.375,1.233,-.10),.072,.072,sides=32)
 audit.append({'name':'communications mast','center':[.375,-.10],'radius':.067,'top':1.225,'existing_base':1.15})
 # Two tangent-mounted instrument panels need curved underside gaskets.
 # Fit their actual lower planes rather than lifting/moving accepted panels.
 for _,n in walk(model.root):
  if n['name'] not in ('GND_RW_Ground_graphite_8_0','GND_RW_Ground_black_0_0'):continue
  m=n['mesh'];v=np.array(m['vertices']);normal=np.array(m['normals']);tri=m['submeshes'][0]
  for g in components(m):
   idx=sorted({i for t in g for i in tri[t]});p=v[idx]
   if p[:,1].min()<1.12 or p[:,0].max()-p[:,0].min()<.4:continue
   ns=normal[idx];slopes=[-q[2]/q[1] for q in ns if abs(q[1])>.9]
   if not slopes:continue
   slope=float(np.median(slopes));offset=float((p[:,1]-slope*p[:,2]).min())+.0015
   lo=p.min(0);hi=p.max(0);zs=np.linspace(lo[2],hi[2],25)
   for z0,z1 in zip(zs,zs[1:]):
    t0=offset+slope*z0;t1=offset+slope*z1
    y0=min(math.sqrt(RADIUS**2-z0*z0)-.012,t0-.004);y1=min(math.sqrt(RADIUS**2-z1*z1)-.012,t1-.004)
    prism(dark,float(lo[0]),float(hi[0]),float(z0),float(z1),y0,y1,t0,t1)
   audit.append({'name':'roof panel gasket','source':n['name'],'x_range':[float(lo[0]),float(hi[0])],'z_range':[float(lo[2]),float(hi[2])],'slope':slope,'top_offset':offset})
 assert len([a for a in audit if a['name']=='roof panel gasket'])==2,audit
 audit.append({'name':'roof skin infill','outer_radius':1.2,'inner_radius':1.15,'x_range':[-.89,.89],'z_range':[-.5,.5],'cladding_radius':1.206})
 for texture,mesh in [('rwm_graphite',dark),('rwm_steel',steel),('rwm_bronze',bolts),('rwm_white',infill)]:meshnode(model,group,'RW_CommandRoofSeat_'+texture,texture,mesh)
 write(model,GD/'Models/RW_GND_CMD.mu')
 p=GD/'RoosterWorksGroundModules.version';version=json.loads(p.read_text());version['VERSION']['BUILD']=29;p.write_text(json.dumps(version,indent=2)+'\n')
 (R/'Reports/DEV29_ROOF_SEATS.json').write_text(json.dumps(audit,indent=2)+'\n')
 for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
 print('PASS built radome socket/flange/bolts, mast collar and two hull-conforming roof panel gaskets; existing geometry and ring maps preserved')

if __name__=='__main__':main()
