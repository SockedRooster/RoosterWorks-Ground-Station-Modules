"""Ground industry and explicit exterior mount points. Dev.22 is read-only.

Stock recipe/thermal settings are saved in Source/Industry for reproducibility.
The drill uses the installed Squad moving mechanism by MODEL reference only;
no Squad model or texture is copied into the distribution.
"""
from pathlib import Path
import sys,copy,json,hashlib,math
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1]; W=R.parent; B=W/'ground-hotpatch-v22'
sys.path[:0]=[str(W/'rw-v075dev5/Source'),str(W/'rw-v075dev5/Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
from appearance_textures import label
import build_hab250 as h
from build_v18 import node,box,cylinder,meshnode,module
GD=R/'GameData/RoosterWorksGroundModules'; OUT=GD/'Models'; C=GD/'Compatibility'
SOURCE=R/'Source/Industry'; SOURCE.mkdir(exist_ok=True)
GAME=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program')
audit={}

def part(role,base=B):return parse((base/f'GameData/RoosterWorksGroundModules/Parts/RW_GND_{role}.cfg').read_text(encoding='utf-8')).children[0]
def save(p): (GD/f"Parts/{p.get('name')}.cfg").write_text(dump(Node('ROOT',children=[p])),encoding='utf-8')
def resource(n,a,m):return Node('RESOURCE',[('name',n),('amount',str(a)),('maxAmount',str(m))])
def replace_texture(model,old,new):
 for t in model.textures:
  if t['name']==old:t['name']=new
def add_label_material(model,name):
 src=copy.deepcopy(next(m for m in model.materials if model.textures[m['properties']['_MainTex']['index']]['name']=='rwm_pwrlabel'))
 src['name']=name;src['properties']['_MainTex']['index']=len(model.textures)
 model.textures.append(dict(name=name,type=0));model.materials.append(src)

def templates():
 dest=SOURCE/'StockModuleTemplates.cfg'
 if dest.exists():return parse(dest.read_text()).children
 out=[]
 for role,file in [('Refinery','ISRU/ISRU.cfg'),('Drill','RadialDrill/RadialDrill.cfg')]:
  p=parse((GAME/'GameData/Squad/Parts/Resources'/file).read_text()).children[0]
  names=('ModuleResourceConverter','ModuleCoreHeat','ModuleOverheatDisplay') if role=='Refinery' else ('ModuleResourceHarvester','ModuleAnimationGroup','ModuleCoreHeat','ModuleOverheatDisplay')
  out.append(Node(role,children=[copy.deepcopy(n) for n in p.children if n.get('name') in names]))
 dest.write_text('// KSP 1.12.5 stock resource/thermal module settings, Squad/RoverDude.\n// No stock mesh, animation or texture is redistributed.\n'+dump(Node('ROOT',children=out)))
 return out

def build_isru(template):
 ID='RW_GND_ISRU';m=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu');m.name=ID;m.root['name']=ID
 replace_texture(m,'rwm_pwrlabel','rwm_isrulabel');label('ISRU-250','ORE REFINERY').save(OUT/'rwm_isrulabel.png')
 # New purpose-built refinery skid sits on the rear flank, clear of end ports,
 # underfloor pipes, leg motion and the retained yellow roof handrails.
 group=node('RW_RefinerySkid');m.root['children'].append(group)
 dark=h.Mesh();metal=h.Mesh();white=h.Mesh();gold=h.Mesh()
 for x in (-.65,0,.65):
  box(dark,(x,0,-1.27),(.45,1.25,.17))
  cylinder(white,(x,-.46,-1.51),(x,.46,-1.51),.20,.20,sides=32)
  cylinder(metal,(x,.46,-1.51),(x,.57,-1.51),.20,.10,sides=32)
  cylinder(metal,(x,-.55,-1.51),(x,-.46,-1.51),.10,.20,sides=32)
  for y in (-.40,.36):cylinder(gold,(x,y,-1.51),(x,y+.025,-1.51),.211,.211,False,32)
  h.tube(metal,(x,.57,-1.51),(x,.79,-1.51),.035,12)
  h.tube(metal,(x,.79,-1.51),(x,.79,-.96),.035,12)
  h.tube(gold,(x,-.55,-1.51),(x,-.74,-1.51),.025,12)
 h.tube(metal,(-.85,.79,-1.51),(.85,.79,-1.51),.045,16)
 h.tube(gold,(-.85,-.74,-1.51),(.85,-.74,-1.51),.035,12)
 # Real heat removal comes from attached active radiators, not decorative fins.
 for key,mesh in [('rwm_graphite',dark),('rwm_steel',metal),('rwm_white',white),('rwm_bronze',gold)]:meshnode(m,group,'RW_ISRU_Process_'+key,key,mesh)
 co=node('RW_ISRU_SkidCollision');co['collider']=dict(type='box',trigger=0,size=(1.90,1.70,.44),center=(0,.02,-1.49));group['children'].append(co)
 p=part('PWR');p.set('name',ID);p.set('title','RoosterWorks Ground ISRU — Ore Refinery');p.set('TechRequired','advScienceTech');p.set('category','Utility');p.set('mass','5.25');p.set('cost','14000');p.set('entryCost','28000');p.set('breakingForce','1000');p.set('breakingTorque','1000')
 p.set('description','Crewless 2.5 m inline Ore refinery. Four stock conversion modes: LF+Ox, LiquidFuel, Oxidizer and Monopropellant. 300 Ore buffer, 1000 EC. Requires power, an engineer for best efficiency, separate fuel tanks and active radiators. Four retractable legs, seamless service pipes and strong docking at both ends. Exterior equipment mounts are rigid structural nodes, not docking ports. No habitat, shielding or nuclear reactor.')
 p.set('tags','roosterworks ground base isru refinery converter ore mining fuel industry')
 for n in p.children:
  if n.header=='MODEL':n.set('model','RoosterWorksGroundModules/Models/'+ID)
  if n.get('name')=='ModuleRWRingColor':n.set('ringModel',ID)
  if n.get('moduleID')=='RW_GND_PWR_EndLights':n.set('moduleID',ID+'_EndLights')
 p.children=[n for n in p.children if n.header!='RESOURCE']
 p.children += [resource('ElectricCharge',1000,1000),resource('Ore',0,300)]+copy.deepcopy(template.children)
 converter_names=[('LF + Oxidizer','LF+Ox'),('Monopropellant','Monopropellant'),('LiquidFuel','LiquidFuel'),('Oxidizer','Oxidizer')]
 for n,(display,short) in zip([n for n in p.children if n.get('name')=='ModuleResourceConverter'],converter_names):
  n.set('ConverterName',display);n.set('StartActionName','Start Refinery ['+short+']');n.set('StopActionName','Stop Refinery ['+short+']');n.set('resourceOutputName',short)
 write(m,OUT/(ID+'.mu'));save(p)
 # Preserve accepted band selection indices: original meshes are untouched.
 maps=parse((C/'GroundRingGeometry.cfg').read_text());rule=copy.deepcopy(next(n for n in maps.children if n.get('model')=='RW_GND_PWR'))
 rule.set('model',ID)
 for n in rule.children:n.set('path',n.get('path').replace('/RW_GND_PWR/','/'+ID+'/'))
 (C/'IndustryRingGeometry.cfg').write_text(dump(Node('ROOT',children=[rule])))
 audit[ID]={'converters':4,'ore_buffer':300,'electric_charge':1000,'dry_mass_t':5.25,'stock_conversion_rates':True,'external_active_radiators_required':True,'motion_source':'RW_GND_PWR','docking_ports':2}

def blank_model(ID):
 m=load(B/'GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu');m.name=ID;m.root=node(ID);return m

def equipment_part(ID,title,mass,cost,description):
 return Node('PART:NEEDS[RoosterWorksStationModules]',[('name',ID),('module','Part'),('author','SockedRooster'),('rescaleFactor','1'),('attachRules','1,1,1,1,0'),('node_attach','0, 0, 0, 0, 0, -1, 1'),('node_stack_mount','0, 0, 0, 0, 0, -1, 1'),('bulkheadProfiles','srf'),('TechRequired','advScienceTech'),('entryCost',str(cost*2)),('cost',str(cost)),('category','Utility'),('subcategory','0'),('title',title),('manufacturer','RoosterWorks'),('description',description),('tags','roosterworks ground base industry drill ore hull mount equipment'),('mass',str(mass)),('CrewCapacity','0'),('fuelCrossFeed','true'),('dragModelType','default'),('maximum_drag','.2'),('minimum_drag','.2'),('angularDrag','2'),('crashTolerance','15'),('breakingForce','1000'),('breakingTorque','1000'),('maxTemp','2000'),('skinMaxTemp','2400')],[Node('MODEL',[('model','RoosterWorksGroundModules/Models/'+ID)])])

def build_drill(template):
 ID='RW_GND_DRILL';m=blank_model(ID);dark=h.Mesh();steel=h.Mesh();white=h.Mesh();gold=h.Mesh()
 # The mounting face is Z=0; the complete moving stock mechanism sits outboard.
 box(dark,(0,0,.065),(.82,1.36,.13))
 for x in (-.34,.34):
  box(steel,(x,.01,.16),(.12,1.38,.18))
  h.tube(gold,(x,-.55,.27),(x,.58,.27),.018,12)
  for y in (-.53,.54):cylinder(gold,(x,y,.255),(x,y,.285),.04,.04,sides=12)
 box(white,(0,.62,.23),(.66,.20,.18))
 box(dark,(0,-.58,.23),(.64,.10,.18))
 for key,mesh in [('rwm_graphite',dark),('rwm_steel',steel),('rwm_white',white),('rwm_bronze',gold)]:meshnode(m,m.root,'RW_DrillFrame_'+key,key,mesh)
 co=node('RW_DrillFrameCollision');co['collider']=dict(type='box',trigger=0,size=(.82,1.36,.30),center=(0,0,.15));m.root['children'].append(co)
 add_label_material(m,'rwm_drilllabel');label('DRILL-250','SURFACE MINING').save(OUT/'rwm_drilllabel.png')
 badge=h.Mesh();badge.quad([(-.28,.55,.326),(.28,.55,.326),(.28,.69,.326),(-.28,.69,.326)],[(0,0,1)]*4,[(1,0),(0,0),(0,1),(1,1)])
 meshnode(m,m.root,'RW_DrillFrame_Label','rwm_drilllabel',badge)
 p=equipment_part(ID,'RoosterWorks Ground DRILL — Deployable Mining Rig',.65,4800,'Deployable Ore drill with a reinforced RoosterWorks mounting cradle. Snap its rear mount node to a hull equipment pad, or surface-attach it. Keep the mast upright, drill head downward and clear of stairs/legs. Uses the stock animated Drill-O-Matic mechanism at half scale to suit the ground hull height: deploy before starting extraction. Requires ground contact, local Ore, 7.5 EC/s and active radiators; engineer bonus applies. 50 Ore buffer and 150 EC. No docking, crew, habitat or shielding.')
 # Native stock mount: (+.1,0,0), inward normal +X. Rotate +90 Y so
 # inward is -Z; half scale and +.05 Z align both mounting faces at Z=0.
 p.children.append(Node('MODEL',[('model','Squad/Parts/Resources/RadialDrill/TriBitDrill'),('position','0, 0, .05'),('rotation','0, 90, 0'),('scale','.5, .5, .5')]))
 p.children += copy.deepcopy(template.children)+[resource('ElectricCharge',150,150),resource('Ore',0,50)]
 harvester=next(n for n in p.children if n.get('name')=='ModuleResourceHarvester')
 for key,value in [('ConverterName','Ore Extraction'),('StartActionName','Start Ore Drill'),('StopActionName','Stop Ore Drill'),('ToggleActionName','Toggle Ore Drill')]:harvester.set(key,value)
 harvester.set('ImpactRange','2.71');harvester.set('Efficiency','.75')
 next(c for c in harvester.children if c.header=='INPUT_RESOURCE' and c.get('ResourceName')=='ElectricCharge').set('Ratio','7.5')
 next(c for c in p.children if c.get('name')=='ModuleCoreHeat').set('MaxCoolant','50')
 anim=next(n for n in p.children if n.get('name')=='ModuleAnimationGroup')
 for key,value in [('moduleType','Mining Rig'),('deployActionName','Deploy Drill'),('retractActionName','Retract Drill'),('toggleActionName','Toggle Drill')]:anim.set(key,value)
 write(m,OUT/(ID+'.mu'));save(p)
 audit[ID]={'stock_model_reference':'Squad/Parts/Resources/RadialDrill/TriBitDrill','no_stock_asset_redistribution':True,'stock_deploy_animation':'Drill_Deploy','stock_run_animation':'Drill_Running','stock_model_rotation':[0,90,0],'stock_model_translation':[0,0,.05],'stock_model_scale':.5,'ore_buffer':50,'ec_per_second':7.5,'dry_mass_t':.65,'docking_ports':0}

def mount_geometry(m,parent,prefix,center=(0,0,0),sign=1):
 # Thin flanged shoe, two guide rails and four captive bolts. Local mounting
 # plane Z=0 is flush to the parent; exposed node is at Z=.10.
 dark=h.Mesh();steel=h.Mesh();gold=h.Mesh()
 box(dark,(0,0,.025),(.20,.40,.05));box(steel,(0,0,.067),(.17,.34,.034))
 for y in (-.14,.14):
  for x in (-.062,.062):cylinder(gold,(x,y,.084),(x,y,.103),.015,.015,sides=8)
 for x in (-.082,.082):box(dark,(x,0,.091),(.022,.28,.025))
 for key,mesh in [('rwm_graphite',dark),('rwm_steel',steel),('rwm_bronze',gold)]:
  mesh.vertices=[(center[0]+sign*x,center[1]+y,center[2]+sign*z) for x,y,z in mesh.vertices]
  mesh.normals=[(sign*x,y,sign*z) for x,y,z in mesh.normals]
  meshnode(m,parent,prefix+'_'+key,key,mesh)
 co=node(prefix+'_Collision',center);co['collider']=dict(type='box',trigger=0,size=(.20,.40,.11),center=(0,0,sign*.055));parent['children'].append(co)

def build_shoe():
 ID='RW_GND_MOUNT';m=blank_model(ID);mount_geometry(m,m.root,'RW_HullShoe')
 p=equipment_part(ID,'RoosterWorks Ground MOUNT — Hull Equipment Shoe',.025,150,'Universal reinforced hull equipment shoe. Surface-attach to a clear rigid hull panel, then use its outward snap node for equipment. Passes resources; no docking, staging, crew or habitat. Keep clear of windows, doors, folding stairs, moving legs and expandable tube sections.')
 p.set('TechRequired','generalConstruction');p.set('node_stack_equipment','0, 0, .11, 0, 0, 1, 1');p.set('attachRules','1,1,1,1,0')
 write(m,OUT/(ID+'.mu'));save(p);audit[ID]={'dry_mass_t':.025,'surface_attach':True,'equipment_plane':.11,'docking_ports':0}

def hull_mounts():
 mounted={}
 for role in ('HAB','LAB','CMD','LOG','GRN','AIR','PWR','TUB','ISRU'):
  ID='RW_GND_'+role;p=part(role, R if role=='ISRU' else B)
  m=load(OUT/(ID+'.mu') if role=='ISRU' else B/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu')
  half=abs(float(p.get('node_stack_top').split(',')[0]));entries=[]
  for end in (-1,1):
   for sign,side in ((1,'port'),(-1,'starboard')):
    # ISRU rear is occupied by its process skid. Leave that flank clear.
    if role=='ISRU' and sign==-1:continue
    x=end*(half-.115);z=sign*1.225;name=f"equipment_{side}_{'a' if end<0 else 'b'}"
    mount_geometry(m,m.root,'RW_HullMount_'+name,(x,0,z),sign)
    pos=(x,0,z+sign*.11)
    p.set('node_stack_'+name,', '.join(format(v,'.8g') for v in (*pos,0,0,sign,1)))
    entries.append(dict(name=name,position=pos,outward=(0,0,sign),size=1))
  write(m,OUT/(ID+'.mu'));save(p);mounted[ID]=entries
 # The established VT uses a surface-specific decoupler. Preserve that contract;
 # its existing surface mount can use a clear pad/shoe without changing release.
 save(part('VT'))
 audit['hull_mounts']=mounted
 audit['attachment_audit']={'accepts_surface_attachment':{p.stem:part(p.stem.removeprefix('RW_GND_'),R).get('attachRules') for p in (GD/'Parts').glob('*.cfg')},'fixed_snap_points':sum(map(len,mounted.values())),'excluded_from_fixed_pads':['HUB (junction skin)','ELB (curved junction)','FLEX (moving bellows)','END_250_125 (tapered shoulder)','VT (equipment)'],'universal_shoe_for_other_clear_rigid_surfaces':True,'existing_docking_nodes_unchanged':True,'existing_flight_parts_not_migrated':True}

def compatibility():
 ids='RW_GND_ISRU,RW_GND_DRILL,RW_GND_MOUNT'
 cleanup=Node('@PART['+ids+']:NEEDS[Kerbalism]:FINAL',children=[Node('!MODULE[Habitat],*')]+[Node('!RESOURCE['+n+'],*') for n in ('Shielding','Atmosphere','WasteAtmosphere','MoistAtmosphere')]+[Node('!MODULE[Sensor]:HAS[#type[habitat_radiation]],*')])
 # Deliberately retain stock Ore harvesting/conversion. Kerbalism's generic
 # stock-module planner/background handling sees these; chemical-plant profile
 # replacement patches target stock part IDs and do not target these IDs.
 organizer=Node('@PART['+ids+']:NEEDS[VABOrganizer]:FINAL',children=[Node('%VABORGANIZER',[('%organizerSubcategory','crewUtility')])])
 (C/'IndustryCompatibility.cfg').write_text('// Ground industry only; preserves stock Ore recipes with and without Kerbalism.\n'+dump(Node('ROOT',children=[cleanup,organizer])))

def main():
 # Check baselines before and after every build without touching synced sources.
 hashes={p.relative_to(W).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in (B,W/'rw-v075dev9') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 (R/'Reports/DEV23_PROTECTED_INPUTS.json').write_text(json.dumps(hashes,indent=2)+'\n')
 t=templates();build_isru(t[0]);build_drill(t[1]);build_shoe();hull_mounts();compatibility()
 v=GD/'RoosterWorksGroundModules.version';d=json.loads(v.read_text());d['VERSION']['BUILD']=23;v.write_text(json.dumps(d,indent=2)+'\n')
 (R/'Reports/DEV23_INDUSTRY.json').write_text(json.dumps(audit,indent=2)+'\n')
 for path,digest in hashes.items():assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,path
 print('PASS built ISRU, deployable mining-rig cradle, universal shoe and 34 fixed hull mounts; protected baselines unchanged')

if __name__=='__main__':main()
