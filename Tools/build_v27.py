"""Seat the three nuclear equipment racks on closed, hull-conforming saddles."""
from pathlib import Path
import sys,math,json,hashlib,copy
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;B=W/'ground-hotpatch-v26';GD=R/'GameData/RoosterWorksGroundModules'
sys.path[:0]=[str(W/'rw-v075dev5/Source'),str(W/'rw-v075dev5/Tools'),str(R/'Tools')]
from native_model import load
from native_derivatives import write
from config_nodes import parse,dump,Node
import build_hab250 as h
from build_v18 import node,box,cylinder,meshnode

def prism(mesh,x0,x1,y0,y1,z0,z1,front):
 points=np.array([(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1),(x0,y0,front),(x1,y0,front),(x1,y1,front),(x0,y1,front)])
 center=points.mean(0)
 for face in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)):
  v=points[list(face)];normal=np.cross(v[1]-v[0],v[2]-v[0]);normal/=np.linalg.norm(normal)
  if np.dot(normal,v.mean(0)-center)<0:v=v[::-1];normal=-normal
  mesh.quad(v.tolist(),[normal.tolist()]*4)

def main():
 unit_cost={'ElectricCharge':0,'Uraninite':.7,'RW_NuclearFeedstock':.8,'EnrichedUranium':865,'DepletedFuel':0}
 prices={}
 protected={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev10') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV27_PROTECTED_INPUTS.json').write_text(json.dumps(protected,indent=2)+'\n')
 for role in ('NST','NSM','CEN'):
  ID='RW_GND_'+role;m=load(B/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu')
  group=node('RW_'+role+'_HullSaddle');m.root['children'].append(group)
  saddle=h.Mesh();steel=h.Mesh();gold=h.Mesh()
  # Inner surface penetrates the accepted radius-1.204 hull by 35 mm.
  # The outer face overlaps the rack backplate by 80 mm. This closes the
  # growing wedge-shaped air gap above the hull equator, rather than adding
  # struts whose top ends would still float above the curved shell.
  ys=np.linspace(-.15,1.08,25)
  for a,b in zip(ys,ys[1:]):
   za=-math.sqrt(1.204**2-a*a)+.035;zb=-math.sqrt(1.204**2-b*b)+.035
   prism(saddle,-.95,.95,float(a),float(b),za,zb,-1.24)
  for x in (-.86,.86):
   # Solid side cheek brackets and visible captive bolts join the saddle
   # to the existing equipment frame. Lowest point stays above leg travel.
   box(steel,(x,.46,-1.285),(.10,1.18,.13))
   for y in (-.05,.48,.99):cylinder(gold,(x,y,-1.36),(x,y,-1.385),.028,.028,sides=12)
  for texture,mesh in [('rwm_graphite',saddle),('rwm_steel',steel),('rwm_bronze',gold)]:meshnode(m,group,'RW_'+role+'_Mount_'+texture,texture,mesh)
  # The opposite flank gets an identical assembly, turned 180 degrees about
  # the vertical axis. This preserves outward normals, caps and handedness.
  # It is one part with the same resource capacities, not a second processor.
  m.root['children']=[n for n in m.root['children'] if not n['name'].startswith('RW_HullMount_equipment_port')]
  for original in [next(n for n in m.root['children'] if n['name']=='RW_'+role+'_Industry'),group]:
   mirror=copy.deepcopy(original);mirror['name']+='_Port';mirror['rotation']=(0,1,0,0)
   def unique(n):
    for child in n['children']:child['name']+='_Port';unique(child)
   unique(mirror);m.root['children'].append(mirror)
  cfg=GD/f'Parts/{ID}.cfg';p=parse((B/f'GameData/RoosterWorksGroundModules/Parts/{ID}.cfg').read_text()).children[0]
  p.values=[(k,v) for k,v in p.values if not k.startswith('node_stack_equipment_port')]
  # KSP subtracts missing resource value from the configured full-tank price.
  # Baseline configs incorrectly used the dry price for empty nuclear tanks.
  dry=float(p.get('cost'));capacity_cost=sum(float(n.get('maxAmount'))*unit_cost[n.get('name')] for n in p.children if n.header=='RESOURCE')
  p.set('cost',format(dry+capacity_cost,'.10g'))
  for organizer in p.children:
   if organizer.header.startswith('VABORGANIZER'):organizer.set('organizerSubcategory','crewUtility')
  prices[ID]={'unit_costs':unit_cost,'dry_price':dry,'configured_full_price':dry+capacity_cost,'initial_price':dry,'empty_fuel_tanks':True}
  cfg.write_text(dump(Node('ROOT',children=[p])))
  # Hull and existing process colliders already bound this occupied space;
  # no broad new collider is added across the folding-leg envelope.
  write(m,GD/f'Models/{ID}.mu')
 path=GD/'RoosterWorksGroundModules.version';v=json.loads(path.read_text());v['VERSION']['BUILD']=27;path.write_text(json.dumps(v,indent=2)+'\n')
 catalogue=[]
 for ids,subcategory in [('RW_GND_DRILL,RW_GND_DRILL_*','resources'),('RW_GND_NST,RW_GND_CEN,RW_GND_NSM','crewUtility')]:
  catalogue.append(Node('@PART['+ids+']:NEEDS[VABOrganizer]:FINAL',[('%category','Utility')],[Node('!VABORGANIZER,*'),Node('VABORGANIZER',[('organizerSubcategory',subcategory)])]))
 (GD/'Compatibility/ZZZZZGroundIndustryCategories.cfg').write_text('// Final user placement: all ground drills in Harvesting; nuclear modules in Station Utility.\n'+dump(Node('ROOT',children=catalogue)))
 (R/'Reports/DEV27_COSTS.json').write_text(json.dumps(prices,indent=2)+'\n')
 for path,digest in protected.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 (R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted((R/'GameData').rglob('*')) if p.is_file()))
 print('PASS built matching equipment on both flanks, closed curved saddles, cheek brackets and bolts; capacities, recipes, hulls and plugins preserved')

if __name__=='__main__':main()
