"""Create ten additive part definitions and scoped compatibility patches.

The accepted station kit and artist handoff are read-only inputs. Ground IDs
are distinct; no generated selector ever targets an existing station part.
"""
from pathlib import Path
import sys,json,copy,re,math,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from config_nodes import Node,parse,dump
from native_model import load,walk
from build_ring_options import components,circular,ranges,SURFACES
GD=R/'GameData/RoosterWorksGroundModules';(GD/'Parts').mkdir(exist_ok=True);(GD/'Compatibility').mkdir(exist_ok=True)
ROLES=('HAB','LAB','CMD','LOG','GRN','AIR','PWR','HUB','TUB','ELB')
SOURCE={('RW_ADP_250_375' if role=='ADP' else 'RW_'+role+'_250'):'RW_GND_'+role for role in ROLES}
SUB={'HAB':'crewHabitation','LAB':'labs','CMD':'station','LOG':'crewUtility','GRN':'greenhouses','CUP':'cupolas','AIR':'airlocks','PWR':'batteries','HUB':'crewHubs','TUB':'crewTubes','ELB':'crewTubes','ADP':'crewAdapters'}
reports={role:json.loads((R/f'Reports/RW_GND_{role}.json').read_text()) for role in ROLES}
def lighting(n,role):
    if n.header.split('[')[0] not in ('MODULE','%MODULE','@MODULE'):return
    name=n.get('name') or n.get('%name') or n.header.split('[',1)[-1].split(']')[0]
    if name=='ModuleColorChanger':
        n.values=[(k,v) for k,v in n.values if k.lstrip('@%')!='includedRenderer']
        for renderer in reports[role]['emissive_renderers']:
            if role=='GRN' and renderer=='RW_GreenhouseInspectionLamps':continue
            n.values.append(('includedRenderer',renderer))
for old,new in SOURCE.items():
    role=new.rsplit('_',1)[-1];report=reports[role]
    p=copy.deepcopy(parse((CORE/f'GameData/RoosterWorksStationModules/Parts/{old}.cfg').read_text()).children[0]);p.header='PART:NEEDS[RoosterWorksStationModules]'
    if role=='HUB':
        cup=parse((CORE/'GameData/RoosterWorksStationModules/Parts/RW_CUP_250.cfg').read_text()).children[0]
        p.set('CrewCapacity','1');p.set('mass',str(float(p.get('mass'))+float(cup.get('mass'))))
        p.set('cost',str(float(p.get('cost'))+float(cup.get('cost'))));p.set('entryCost',str(float(p.get('entryCost'))+float(cup.get('entryCost'))))
        p.children += [copy.deepcopy(n) for n in cup.children if n.header in ('INTERNAL','RESOURCE') or (n.header=='MODULE' and n.get('name')=='ModuleColorChanger')]
        for n in p.children:
            if n.get('name')=='ModuleColorChanger':n.set('moduleID','RW_GND_HUB_ObservationLights')
            if n.header=='INTERNAL':n.set('offset','0, 2, 0')
    p.set('name',new);p.set('title',f'RoosterWorks Ground {role} — '+{'HAB':'Habitation','LAB':'Science Laboratory','CMD':'Command Core','LOG':'Logistics Vault','GRN':'Greenhouse','CUP':'Cupola','AIR':'EVA Airlock','PWR':'Power and Service','HUB':'Junction Hub','TUB':'Crew Tube','ELB':'Level 90 Degree Elbow','ADP':'2.5–3.75 m Adapter'}[role])
    p.set('description',f'Ground adaptation of the accepted RoosterWorks {role} module. Fixed deployed support legs'+(' and ground access stairs.' if report['stairs'] else '.')+' Existing crew, science, supply and electrical role retained. Independent White/Grey finish and ring colors. Supports and stairs are static; no folding or adjustable deployment is supplied in this hot patch.')
    p.set('tags',(p.get('tags') or '')+' ground base surface legs roosterworks')
    if role=='HUB':
        p.set('title','RoosterWorks Ground HUB — Four-Way Observation Hub')
        p.set('description','Four horizontal 2.5 m connections with an integrated one-Kerbal observation cupola. Closed underside; no vertical attachment ports or exterior EVA hatch. Includes observation lighting and the temporary stock Cupola interior. Static reinforced support legs. Independent White/Grey finish and ring colors.')
        p.set('tags','roosterworks ground base hub four junction observation cupola kerbalism legs')
    p.values=[(k,v) for k,v in p.values if not k.startswith('node_stack_') and k!='node_attach']
    for key,v in report['nodes'].items():p.set(key,', '.join(format(float(x),'.9g') for x in v))
    p.set('attachRules','1,0,1,1,0');p.set('vesselType','Base');p.set('rescaleFactor','1')
    p.set('fuelCrossFeed','true')
    support_mass=report['legs']*.065+(.10 if report['stairs'] else 0)
    support_cost=report['legs']*450+(300 if report['stairs'] else 0)
    p.set('mass',format(float(p.get('mass'))+support_mass,'.9g'));p.set('cost',str(round((float(p.get('cost'))+support_cost)/10)*10));p.set('entryCost',str(round((float(p.get('entryCost'))+support_cost*1.5)/10)*10))
    p.children=[n for n in p.children if not (n.header=='MODULE' and n.get('name') in ('ModulePartVariants','ModuleRWStationHatch'))]
    for n in p.children:
        if n.header=='MODEL':n.set('model',f'RoosterWorksGroundModules/Models/{new}')
        lighting(n,role)
    if role=='CUP':p.set('CoMOffset','0, 0, 0')
    p.children += [Node('MODULE',[('name','ModuleRWStationFinish'),('finish','White')]),Node('MODULE',[('name','ModuleRWRingColor'),('ringModel',new),('ringColor','Original')]),Node('MODULE',[('name','ModuleRWEditorMenu')]),Node('VABORGANIZER:NEEDS[VABOrganizer]',[('organizerSubcategory',SUB[role])])]
    if role=='CMD':
        p.children.append(Node('MODULE',[('name','ModuleRWGroundTether'),('tetherEnabled','false'),('settleSeconds','1.5'),('engageSpeed','0.15'),('releaseSpeed','0.75')]))
    for mechanism in ('Legs','Stairs'):
        bindings=[b for b in report['motion'] if b['mechanism']==mechanism]
        if not bindings:continue
        module=Node('MODULE',[('name','ModuleRWGroundDeploy'),('deploymentID',mechanism),('duration','2.5'),('deployed','true'),('deployment','1')])
        for b in bindings:
            module.children.append(Node('TRANSFORM',[('name',b['name']),('deployPosition',', '.join(format(float(x),'.9g') for x in b['position'])),('retractPosition',', '.join(format(float(x),'.9g') for x in b['retractPosition'])),('retractEuler',', '.join(str(x) for x in b['retractEuler']))]))
        p.children.append(module)
    ports=report.get('docking_ports',[])
    assert len(ports)==len(report['nodes']),('Run add_docking_transforms.py first',new)
    for port in ports:
        p.children.append(Node('MODULE',[('name','ModuleDockingNode'),('nodeTransformName',port['transform']),('controlTransformName',port['transform']),('referenceAttachNode',port['attachNode']),('useReferenceAttachNode','true'),('nodeType','size2'),('crossfeed','true'),('stagingEnabled','false'),('stagingToggleEnabledEditor','false'),('stagingToggleEnabledFlight','false'),('canRotate','false'),('acquireRange','0.5'),('captureRange','0.06')]))
    p.children.append(Node('MODULE',[('name','ModuleRWGroundDocking')]))
    p.set('description',(p.get('description') or '')+' Integrated docking at every connection end. Crossfeed is permanently on; manual detach/undock only, with staging disabled.')
    p.set('description',(p.get('description') or '').replace('Fixed deployed','Deployable').replace('Static reinforced','Deployable reinforced').replace('Supports and stairs are static; no folding or adjustable deployment is supplied in this hot patch.','Animated telescoping supports and folding access stairs have independent editor and flight controls.'))
    (GD/f'Parts/{new}.cfg').write_text(dump(Node('ROOT',children=[p])),encoding='utf-8')
# Copy only exact, explicitly targeted station patches to their distinct ground
# counterparts. Generic RW_* finish/editor patches already match the new parts
# and are not duplicated. Global profile/process/resource definitions stay in core.
skip={'ExteriorFinish.cfg','EditorAppearance.cfg','RingColors.cfg','RingGeometry.cfg','Family500.cfg','LargeFamilyKerbalism.cfg','LargeFamilyVABOrganizer.cfg','ShortHabitats.cfg','LongCrewTubes.cfg','StationCatalogue.cfg','VABOrganizer.cfg','AirlockVABOrganizer.cfg','HubKerbalism.cfg'}
for path in sorted((CORE/'GameData/RoosterWorksStationModules/Compatibility').glob('*.cfg')):
    if path.name in skip:continue
    out=Node('ROOT')
    for src in parse(path.read_text()).children:
        match=re.match(r'^@PART\[([^\]]+)\](.*)$',src.header)
        if not match:continue
        aliases={**SOURCE,'RW_CUP_250':'RW_GND_HUB'}
        names=[aliases[n] for n in match[1].split(',') if n in aliases]
        if not names:continue
        patch=copy.deepcopy(src);patch.header='@PART['+','.join(names)+']'+match[2]
        patch.values=[(k,v.replace('orbital science laboratory','ground science laboratory').replace('station command core','ground command core')) for k,v in patch.values]
        # Declare this add-on only. Copying the core's FOR tag would falsely
        # satisfy the dependency even when Station Modules is not installed.
        patch.header=patch.header.replace(':FOR[RoosterWorksStationModules]',':FOR[RoosterWorksGroundModules]')
        role=names[0].rsplit('_',1)[-1]
        # Native glass and inspection lamp transforms are the only geometry-
        # specific bindings altered in the cloned compatible backend.
        for n in patch.children:lighting(n,role)
        if path.name=='CupolaKerbalism.cfg':
            for n in patch.children:
                if n.get('%name')=='Habitat':n.set('%volume','16.2');n.set('%surface','52')
        out.children.append(patch)
    if out.children:(GD/'Compatibility'/path.name).write_text('// Additive ground-only counterparts; existing station patches untouched.\n'+dump(out),encoding='utf-8')
# Keep native base EC and Kerbalism's automatic crewed battery handling intact.
# Only VAB placement needs a final override; science tiers use cloned late patches.
final=Node('ROOT')
for old,new in SOURCE.items():
    final.children.append(Node(f'@PART[{new}]:NEEDS[VABOrganizer]:FINAL',children=[Node('!VABORGANIZER,*'),Node('VABORGANIZER',[('organizerSubcategory',SUB[new.rsplit('_',1)[-1]])])]))
(GD/'Compatibility/ZZZGroundBalance.cfg').write_text(dump(final),encoding='utf-8')
maps=Node('ROOT');counts={}
for role in ROLES:
    name=f'RW_GND_{role}';model=load(GD/f'Models/{name}.mu');specs=[]
    for path,n in walk(model.root):
        if 'mesh' not in n or len(n.get('materials',[]))!=1:continue
        mat=model.materials[n['materials'][0]]
        if mat['shader']!='KSP/Diffuse':continue
        texture=model.textures[mat['properties']['_MainTex']['index']]['name'].rsplit('/',1)[-1]
        if texture not in SURFACES:continue
        mesh=n['mesh'];selected=[]
        for group in components(mesh):
            if circular(mesh,group):selected.extend(group)
        if selected:specs.append(Node('MESH',[('path',path),('texture',texture),('vertices',str(len(mesh['vertices']))),('triangles',str(len(mesh['submeshes'][0]))),('ranges',ranges(sorted(selected)))]))
    assert specs,('No complete rings found',name)
    counts[name]=len(specs);maps.children.append(Node('RW_RING_MAP',[('model',name)],specs))
(GD/'Compatibility/GroundRingGeometry.cfg').write_text('// Exact triangle selections from the ground exports only.\n'+dump(maps))
(R/'Reports/RING_MAP_COUNTS.json').write_text(json.dumps(counts,indent=2)+'\n')
(GD/'RoosterWorksGroundModules.version').write_text(json.dumps({'NAME':'RoosterWorks Ground Modules Hot Patch','VERSION':{'MAJOR':0,'MINOR':8,'PATCH':0,'BUILD':17},'KSP_VERSION':{'MAJOR':1,'MINOR':12,'PATCH':5}},indent=2)+'\n')
files=sorted(p for p in (R/'GameData').rglob('*') if p.is_file())
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in files))
print('Built ten additive ground parts, scoped compatibility, ring maps and checksum manifest')
